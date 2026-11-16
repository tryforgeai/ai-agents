# Permission-Aware Retrieval for Enterprise RAG

2026-11-15 · Rosso Han · Chinese version: [permission-aware-retrieval.zh](permission-aware-retrieval.zh.md) · Shared doc: https://claude.ai/artifact/Ced6Q82y5Dwfi4YDnQkgD1

## TL;DR

In enterprise RAG, authorization is a hard constraint on the search space, not a ranking signal and not a prompt instruction. Compute the set of chunks the user may see, then search only inside it.

- **Pre-filter, never post-filter.** Post-filtering a top-10 that loses 8 results silently becomes a top-2.
- **Attach a normalized security descriptor to every chunk** at ingestion, copied from the source system's ACLs.
- **Keep the entitlement pipeline in sync** with the content pipeline; permission changes must reach the index by event, not by TTL.
- **Treat six leakage surfaces**, not just retrieval: context, answer, citations/metadata, cache and logs.

This note is based on the bootcamp's Week 09 Module 5 (Enterprise Entitlement-RAG), Weeks 06 and 10, and Microsoft's Azure AI Search documentation.

## The problem: relevance does not imply authorization

Conventional RAG retrieves the most similar chunk across the whole corpus. That silently assumes every user may see every document.

```latex
d^* = \arg\max_{d \in D} \mathrm{sim}(q, d)
```

In a mixed enterprise corpus, a perfect retriever is an efficient leak. An employee asks "What are the plans for Project Phoenix?" and the best semantic match is an executive acquisition memo.

The fix is one subscript. The search space itself depends on who is asking:

```latex
D_u = \{\, d \in D : \mathrm{Authorized}(u, d) = 1 \,\}, \qquad d^* = \arg\max_{d \in D_u} \mathrm{sim}(q, d)
```

Two things the constraint is **not**: it is not a term added to the ranking score, so high relevance can never outweigh missing permission. It is not a system-prompt instruction, which a prompt injection can talk the model out of. `D_u` is recomputed per user, per request, from live entitlements.

## Prevention, not suppression

Authorization must happen during retrieval, before unauthorized text reaches the LLM.

| Pattern | What happens | Nature of the boundary |
| --- | --- | --- |
| **Prevention** | Unauthorized chunks never enter the context window | Deterministic infrastructure (a control) |
| **Suppression** | Confidential chunks enter context; the model is told to refuse | A request to a stochastic system, one prompt injection from the output |

A refusal generated after the model has seen confidential text is not the same as preventing exposure.

### Six leakage surfaces

Retrieval is only the first place confidential information escapes. The last three are the ones teams most often forget.

1. **Unauthorized retrieval** — the chunk enters the candidate set.
2. **Unauthorized context** — the chunk crosses into the prompt.
3. **Generated-answer leakage** — the fact appears in the answer.
4. **Citation / metadata leakage** — a title, filename or URL is exposed.
5. **Cache leakage** — one user's privileged answer is served to another.
6. **Logs / traces leakage** — the secret lands in observability tooling or the SIEM.

A refusal can also leak: "I found `Acquisition-of-Company-X.pdf` but you can't open it" discloses the acquisition. Tests must distinguish **content denial** (you can't read it) from **resource-discovery denial** (you can't learn it exists).

## Permission models and the normalized security descriptor

Production systems layer the four models rather than picking one, then flatten every decision into one descriptor per chunk.

| Model | Idea | Best for | Watch out for |
| --- | --- | --- | --- |
| ACL | The resource names who may see it | Source-system truth (SharePoint, Drive, Confluence); per-document exceptions | List size, drift |
| RBAC | The job implies the scope | Coarse gates; joiner/mover/leaver hygiene | Role explosion |
| ABAC | Attributes compute access | Classification, data residency, tenant, device posture | Metadata quality; fails open unless designed otherwise |
| ReBAC | A path in a graph grants access | Projects, folder inheritance, hierarchy, delegation | Graph traversal cost (OpenFGA, SpiceDB) |

The ingestion layer translates every source's dialect into one shape and stamps it on **every chunk**:

```json
{
  "document_id":    "DOC-731",
  "tenant":         "acme",
  "classification": "confidential",
  "allow_users":    ["u123"],
  "allow_groups":   ["finance", "executives"],
  "deny_users":     [],
  "regions":        ["US"],
  "projects":       ["phoenix"],
  "acl_version":    17
}
```

Design rules:

- **Absent fields deny, never allow.**
- **Deny beats allow.**
- **Version the descriptor** so any decision can be replayed later.
- **Propagate through chunking.** If a chunk is retrieved on its own, it must still say who may see it.

Enterprise RAG runs two ingestion pipelines: content (`parse → chunk → embed → index`) and entitlements (`ACLs / groups / relationships → normalize → sync`). Their consistency is the security property. A document indexed at 10:01 whose permissions change at 10:05 is a leak waiting for a query at 10:06.

## How the vector DB stores records and evaluates the filter

A filtered query is two indexes working together: a vector index answers "what is similar", and a metadata inverted index answers "what may this user see".

### Storage

Each chunk gets an internal integer id and is stored in three places:

```
internal_id = 42
├─ vector:   [0.12, -0.33, ...]          → vector index (HNSW graph / IVF lists)
├─ payload:  {tenant, allow_groups, deny_users, classification, regions, text, acl_version}
└─ inverted index, one table per indexed field:
     tenant         : "acme"         → bitmap{1, 2, ..., 42, ...}
     allow_groups   : "finance"      → bitmap{7, 42, 90}
                      "executives"   → bitmap{42, 91}
     classification : "confidential" → bitmap{42, 88}
     regions        : "US"           → bitmap{3, 42, ...}
```

- **Array fields are indexed per element**, so `allow_groups $in groups` is the union of each group's bitmap.
- **Bitmaps are compressed** (typically Roaring bitmaps), so intersection, union and difference are fast.
- **A permission change only updates payload and bitmaps.** No re-embedding, which is why the entitlement pipeline can move faster than content.

### Filter evaluation

The filter tree compiles to set algebra over bitmaps. The result is `D_u`:

```
allowed = B[tenant=acme]
        ∩ ( B[allow_users=u123] ∪ B[allow_groups=g1] ∪ … ∪ B[allow_groups=gn] )
        ∖ B[deny_users=u123]                    # $nin = set difference → deny beats allow
        ∩ ( B[classification=public] ∪ B[classification=internal] ∪ … )
        ∩ B[regions=US]
```

This gives fail-closed behaviour for free. A chunk with no `classification` field is in no classification bitmap, so the intersection drops it.

## Searching inside the allowed set

The query planner estimates **selectivity** (|allowed| / |all|) and picks a strategy. Post-filtering is the one that breaks recall.

| Selectivity | Strategy | How it works | Trade-off |
| --- | --- | --- | --- |
| Tiny allowed set (e.g. a few thousand) | Brute force | Score only the allowed vectors | Exact, and fast at that size |
| Large allowed set | Filtered HNSW traversal | Walk the graph normally; disallowed nodes are stepping stones but never enter results | Near-normal recall and speed |
| Low to mid (~1–10%) | Filter-aware graph or partitioning | Allowed nodes are sparse, so the graph disconnects; use extra edges (ACORN, Qdrant payload links) or physical tenant partitions | Hardest zone; benchmark it |
| Any (anti-pattern) | Post-filter | Search top-K, then drop disallowed hits | Top-10 silently becomes top-2 |

How common engines behave (check current docs before relying on details):

- **Qdrant** — estimates filter cardinality from payload indexes; small sets go to full scan, otherwise filterable HNSW.
- **Weaviate** — builds an allow-list from the inverted index; below `flatSearchCutoff` it does a flat search; recent versions offer ACORN.
- **Milvus** — builds a bitset from the filter and passes it into the index search.
- **pgvector** — HNSW first, then `WHERE`, i.e. effectively post-filtering; 0.8 added iterative index scans to mitigate it.

When evaluating a vendor, ask one question: does the engine search **with** the bitmap during traversal, or search first and delete afterwards?

## Reference implementation

The query side builds the user's filter from identity, then hands it to the vector DB as a pre-filter.

```python
def secure_search(q, user, k=10):
    groups = expand_groups(user)          # from the IdP / ReBAC engine
    f = {
      "tenant": {"$eq": user.tenant},
      "$or": [{"allow_users": {"$in": [user.id]}},
              {"allow_groups": {"$in": groups}}],
      "deny_users": {"$nin": [user.id]},
      "classification": {"$in": allowed_levels(user.clearance)},
      "regions": {"$in": [user.region]},
    }
    return vdb.query(embed(q), filter=f, top_k=k)  # pre-filter, never search-then-delete
```

A toy vector DB shows what `vdb.query` does underneath: inverted index → allowed set → similarity only inside it. It takes the exact brute-force path; swap in a traversal that checks `id in allowed` for the HNSW path.

```python
import numpy as np
from collections import defaultdict

class TinyVDB:
    def __init__(self, dim):
        self.vecs = np.empty((0, dim), dtype=np.float32)
        self.payload = []
        self.inv = defaultdict(lambda: defaultdict(set))   # field -> value -> {ids}

    def upsert(self, vec, meta):
        iid = len(self.payload)
        self.vecs = np.vstack([self.vecs, vec / np.linalg.norm(vec)])
        self.payload.append(meta)
        for field, v in meta.items():
            for x in (v if isinstance(v, list) else [v]):
                self.inv[field][x].add(iid)                 # array fields: one entry per element
        return iid

    def _eval(self, f):                                     # filter tree -> allowed id set
        ids = set(range(len(self.payload)))
        for field, cond in f.items():
            if field == "$or":
                s = set().union(*(self._eval(sub) for sub in cond))
            else:
                op, val = next(iter(cond.items()))
                vals = val if isinstance(val, list) else [val]
                hit = set().union(*(self.inv[field].get(x, set()) for x in vals))
                s = ids - hit if op == "$nin" else hit      # $eq/$in -> union; $nin -> difference
            ids &= s
        return ids

    def query(self, qvec, filter, top_k=10):
        allowed = np.fromiter(self._eval(filter), dtype=int)   # D_u first
        if allowed.size == 0:
            return []
        q = qvec / np.linalg.norm(qvec)
        scores = self.vecs[allowed] @ q                     # similarity only inside D_u
        top = allowed[np.argsort(-scores)[:top_k]]
        return [(int(i), self.payload[i]) for i in top]
```

Unauthorized vectors are never scored, so the result is exact and never shrinks the way a post-filter does.

## How Microsoft does it: Azure AI Search

Azure AI Search offers two routes to document-level trimming. Both apply the permission check at query time inside the search service, i.e. pre-filtering.

| Route | Ingestion | Query | Caveats |
| --- | --- | --- | --- |
| [Native document-level access control](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview) (preview) | Indexers carry ACL / RBAC metadata from ADLS Gen2, Blob and SharePoint into the index; Purview sensitivity labels can be extracted too | Pass the user's Entra token in `x-ms-query-source-authorization`; the service validates it and trims results, with no custom filter or nested-group expansion | Preview; SharePoint groups not yet supported; check the current API version |
| [Security filters](https://docs.azure.cn/en-us/search/search-security-trimming-for-azure-search) (manual) | Your pipeline writes principal strings into a field such as `group_ids` | An OData filter such as `group_ids/any(g: search.in(g, 'finance,executives'))` | The field is just a string; correctness and freshness are on you |

Sync lag still applies. A [Microsoft ISE post](https://devblogs.microsoft.com/ise/?p=16628) notes that after access is revoked in SharePoint, the user may still see the content in the index until the next ingestion run. That is the 10:01 / 10:05 / 10:06 window above.

## Production checklist

- [ ] Every filtered field has a payload / inverted index; unindexed fields fall back to slow per-record checks.
- [ ] Tenants are physically isolated (collection, namespace or partition), not only filtered.
- [ ] Group explosion is handled: flatten groups at ingestion or cache a per-user allowed bitmap, invalidated by events.
- [ ] Permission changes reach the index by event push, not TTL.
- [ ] Missing descriptor fields deny; deny lists override allow lists.
- [ ] Cache keys include a permission fingerprint, so answers are never reused across entitlement sets.
- [ ] Citations and source lists pass through the same filter as content.
- [ ] Logs and traces redact or permission-gate retrieved text.
- [ ] Recall is benchmarked at low selectivity (1–10%), not just on the unfiltered index.

### Tests

- [ ] Pick any chunk on its own: can the system say who may see it without looking up the parent document?
- [ ] Revoke a user, query immediately: is the document gone?
- [ ] Red-team refusal wording: does any denial confirm a document exists?

## References

Microsoft documentation (opened):

- [Document-level access control in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview)
- [Security filters for trimming results in Azure AI Search](https://docs.azure.cn/en-us/search/search-security-trimming-for-azure-search)
- [Azure AI Search document-level access announcement](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/-/4418584)
- [Microsoft ISE devblog on SharePoint permission sync, Apr 2026](https://devblogs.microsoft.com/ise/?p=16628)

Papers and standards (cited from memory, not re-checked):

- Pang et al., *Zanzibar: Google's Consistent, Global Authorization System*, USENIX ATC 2019
- Sandhu et al., *Role-Based Access Control Models*, IEEE Computer 1996
- Hu et al., *Guide to Attribute Based Access Control*, NIST SP 800-162, 2014
- Gollapudi et al., *Filtered-DiskANN*, WWW 2023
- Patel et al., *ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data*, SIGMOD 2024

Course material: LLM and Enterprise RAG Bootcamp, [Week 09 Module 5 (Enterprise Entitlement-RAG)](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_09/week-09.zh.md) (§十一), [Week 06 (Guardrails)](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_06/week-06.zh.md) and [Week 10 (Access control)](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_10/week-10.zh.md).
