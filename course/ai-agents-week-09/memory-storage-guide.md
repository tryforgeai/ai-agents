# Choosing and Structuring Agent Memory Storage: Vector Stores, Relational Tables, Chunking, Embeddings and Metadata

2026-11-15 · Rosso Han · From Week 9 class Q&A · Chinese version: [memory-storage-guide.zh.md](memory-storage-guide.zh.md) · Runnable example: [learning/2026-11-15-memory-store-filters](../../learning/2026-11-15-memory-store-filters/README.md) · Companion note: [Permission-Aware Retrieval](permission-aware-retrieval.md)

> **In one line: pick the storage by the question you need to ask.** Keyed facts go in a relational table, fuzzy recall goes in a vector index, and the raw record goes in a log. Give every record proper metadata, or filtering, freshness, access control, auditing and deletion all become impossible.
> From the lesson plan: *Substrate follows query shape.* · *Storage is easy. The policy is the whole game.*

---

## 1. Three things that are easy to confuse

| Name | What it is | Where it lives | Who owns it |
| --- | --- | --- | --- |
| **KV cache** | Cached attention keys and values from tokens already processed, so the next token is cheaper. Provider prompt caching (Foyer G3) builds on it | Inside the serving stack, **within the context window** | Infrastructure; measured by throughput |
| **Vector store** | Text turned into vectors, searched by similarity of meaning | **Outside the window**, in the memory store | Your harness; measured by recall and behaviour |
| **Relational database** | Tables, columns and indexes, queried by exact conditions | Outside the window, in the memory store | Your harness |

The lesson plan's "two evictions, two altitudes": KV-cache eviction is a serving optimisation, while memory reclamation is a design decision. Mixing them sends you debugging the wrong layer. **RAG and agent memory use the last two, not the KV cache.**

## 2. What the course recommends: substrate follows query shape (Practice I)

| Substrate | Answers well | Answers poorly | Write cost |
| --- | --- | --- | --- |
| **Append-log** | What happened, in what order | Everything else | Near zero. **Always keep it**: it is the ground truth you rebuild other indexes from when extraction improves, and it is your eval corpus |
| **Relational table** | Typed, keyed facts: time zone, plan tier, supplier lead time | "Something like this" | Near zero |
| **Vector index** | Associative recall: "memories similar to this situation" | "What changed between Tuesday and Friday" | One embedding call per write, plus another stateful service to run |
| **Temporal graph** | Relationships and time: who relates to whom, and when it changed | — | One **LLM extraction** call per write (the most expensive) |

**Default path (worth memorising):** start with **the log and a relational table** → add a **vector index** when recall demands it → add a **graph** only when a relational or temporal query proves it needs edges.

**Build or adopt (Letta, Mem0, Zep):** adopt when the framework's default policy is better than what you would write this quarter; build your own when the policy is the core of your product.

## 3. When to use which

| Situation | Use | Example (Memory Palace / Harbor & Hearth) |
| --- | --- | --- |
| Look up a definite value by key | **Relational table** | "How many weeks does Kolkata take?" "What is Jaipur's minimum order?" |
| Need transactions, joins, or co-location with business data | **Relational table** | Orders, stock, invoice approvers |
| Facts change and you must answer "what was true then" | **Relational table** with `valid_from` / `valid_to`, or a temporal graph | Old warehouse address → new address |
| The user's wording differs from the stored wording | **Vector index** | Flood F1: "the thing that kept toppling over" ↔ "the floor lamp kept wobbling" |
| Find similar situations across many past episodes | **Vector index** | "How did we handle the last supplier delay?" |
| Both: narrow by conditions, then rank by meaning | **Vector search with filters** (Postgres + pgvector, or Qdrant + payload) | "The five most relevant memories that are Meera's, still valid, and about logistics" |
| Record what happened | **Log** | Every turn, tool call and result |

**Rule of thumb:** if you can write it as `WHERE key = value`, use a table. If you can only say "something like this", use vectors. If you need "as of then", add time fields.

## 4. What a record looks like: text + vector + metadata

```json
{
  "id": "m_0412",
  "text": "Meera decided the Diya floor lamp will get a weighted brass base.",
  "embedding": [0.12, -0.33, "..."],

  "user_id": "meera",  "scope": "user",  "source": "s007#turn_4",  "ingested_at": "2026-11-06T14:01Z",
  "memory_type": "semantic",  "entities": ["Diya floor lamp", "brass base"],  "topic": "product",
  "importance": 7,  "event_time": "2026-11-06T14:00Z",  "slot": "diya_lamp_decision",
  "valid": true,  "valid_to": null,  "superseded_by": null
}
```

### Why metadata is required

With vectors alone you can only ask "which records are most similar". Everything below depends on metadata:

| What you need | Fields | Without it |
| --- | --- | --- |
| **Partitioning and access**: Alice's facts never reach Bob | `user_id` `scope` `tenant` `allow_groups` | The better the retriever, the more precisely it leaks |
| **Freshness**: only facts still in force | `valid` `valid_to` `superseded_by` | The zombie address (Flood F2): confidently wrong |
| **Time travel**: "what was true then" | `event_time` + `ingested_at` (the two clocks) | No way to audit why the agent booked the wrong office |
| **Re-ranking signals** | `importance` `event_time` (recency) | Ranking by similarity alone; recent and important items never surface |
| **Provenance and poisoning defence** | `source` `ingested_at` | No way to tell who wrote it or whether to trust it |
| **Deletion / right to be forgotten** | `user_id` `source` | Incomplete deletion, and no proof it happened |
| **Less noise in retrieval** | `entities` `topic` `memory_type` | Irrelevant items in the top-k (in the Flood, e47 reached rank 2 on recency alone) |

**Key property: changing metadata does not require re-embedding.** Marking a fact superseded, changing access or adjusting importance only touches the payload or columns. That is why access and freshness can move much faster than content.

## 5. The write path: chunking, embedding and filling metadata

```
A conversation turn or a document
  → ① Extract atomic facts; resolve pronouns now ("she said yes" is useless three sessions later)
  → ② Salience gate: will this matter three sessions from now? Trivia stays out of long-term memory (it is still in the log)
  → ③ Fill metadata: access and audit fields by code; semantic fields by the LLM
  → ④ Chunk long documents: every chunk inherits all of the parent's filter fields
  → ⑤ Embed: compute the vector from the text only
  → ⑥ Reconcile with existing memories: add / update / supersede / no-op (Mem0's ADD / UPDATE / DELETE / NOOP)
  → ⑦ Write: vector into the vector index, metadata into payload or columns; superseded records are marked, never deleted
```

### Who fills which field (worth memorising)

| Fields | Filled by | Why |
| --- | --- | --- |
| `user_id` `scope` `tenant` `source` `ingested_at`, access fields | **Code**, from the session context or the source system's ACLs | Access and audit; **never let the LLM guess these** |
| `text` `entities` `topic` `memory_type` `importance` `event_time` | **LLM extraction** (structured output) | Requires understanding the content |
| `valid` `valid_to` `superseded_by` | **Updated by later writes** | Superseding means closing the validity window |

### Chunking: memories differ from documents

| | Conversational memory | Long documents (RAG corpus) |
| --- | --- | --- |
| Unit | **One atomic fact per record**, not cut by length | Split by paragraph, heading or fixed length, with a little overlap |
| What matters | Resolve pronouns at write time so each record **stands on its own** | Every chunk **inherits the parent's metadata**; optionally prepend one line of context ("From contract X, section 3") |
| Why | Retrieval happens per record | Retrieval happens per chunk; a chunk retrieved alone must still say whose it is and when it held |

### Embedding notes

- Embed only the `text`. **Metadata does not go into the embedding**: it would no longer be filterable exactly and would distort similarity
- **Rewrite the query** before embedding: replace "that thing" or "it" with concrete nouns (Flood F1)
- Changing the embedding model means **re-embedding everything**, which is another reason to keep the log

## 6. Where it is stored: Qdrant vs Postgres + pgvector

| | Qdrant | Postgres + pgvector |
| --- | --- | --- |
| Metadata | **Payload** (a JSON object per point) | **Ordinary columns**, plus an optional `jsonb` |
| Filter indexes | `create_payload_index` (keyword / bool / datetime …); **must be created explicitly** | B-tree; GIN (arrays / JSONB); **partial indexes** such as `WHERE valid` |
| How filtering runs | Filters during HNSW traversal; switches to a full scan when the allowed set is small | By default HNSW first, then `WHERE`, which is post-filtering; from 0.8, `SET hnsw.iterative_scan = relaxed_order` mitigates it |
| Update / delete | `set_payload` / `delete(FilterSelector)` | `UPDATE` / `DELETE` |
| Good fit | Large data, varied filters, strict filters | Small to mid scale, need for transactions and joins, team already on Postgres |

Code: [qdrant_demo.py](../../learning/2026-11-15-memory-store-filters/qdrant_demo.py) (run and verified) and [pg_demo.py](../../learning/2026-11-15-memory-store-filters/pg_demo.py).

## 7. The read path

```python
q = rewrite_query(question)                        # 1. Rewrite: pronouns → concrete nouns
f = {"user_id": me, "scope": ["user", "app"],      # 2. Filter: mine + shared, still valid, no one else's session
     "valid": True}
cands = store.search(embed(q), filter=f, k=20)     # 3. Over-retrieve: 20 candidates inside the allowed set
top = rerank(cands, w_rel=3, w_rec=0.5, w_imp=1)[:5]   # 4. Re-rank: the Smallville score (weights from the Flood)
context = render(top)                              # 5. Into the window, after the history (Foyer G3: order is cost)
```

The lesson plan's retrieval config (Practice I): `candidate_k: 20 · final_k: 5 · rerank: cross_encoder · exclude_superseded: true · query_rewrite: true`.

## 8. How this relates to the permission-aware retrieval note

[permission-aware-retrieval.md](permission-aware-retrieval.md) already covers **who may see what**: filter before searching, a normalised security descriptor on every chunk, missing fields deny, deny beats allow, event-driven entitlement sync, bitmap evaluation and six leakage surfaces. **All of it applies to memory stores.**

Today's class adds what agent memory needs on top, which that note does not yet cover:

| Extra requirement for agent memory | Why | Course link |
| --- | --- | --- |
| **Freshness fields**: `valid`, `valid_to`, `superseded_by`; queries default to `valid = true` | A changed document gets re-indexed; a memory is **continually superseded by newer facts** | Experiments 6, 7, 9; `exclude_superseded` |
| **Two clocks**: `event_time` + `ingested_at` | You must be able to answer "what did the agent believe at the time?" | Act III |
| **The agent itself is the writer**, so code stamps the access fields at write time | RAG copies permissions from source-system ACLs; a memory the agent wrote has no source system to copy from | Scoped drawers, ADK state prefixes |
| **Session-scoped scratch must not be promoted** to a durable fact | A scratch assumption treated as fact poisons every later answer | The "20% discount" draft |
| **Writes pass a governor**: provenance, append-only deltas, behavioural evaluation | An agent that can edit its own memory is an attack surface | Act III governance; my [MemGPT × System 5](memgpt-as-system-5.md) note: agents may read it, never write it |
| **Forgetting must reach derivatives**: summaries, indexes, caches, extracted facts | Deleting the original is not deletion; keep a record of the deletion event, never the content | The right to be forgotten as a GC specification |

**Decision:** leave that note unchanged. It exists in the RAG project and in the shared online doc, so editing one copy would put them out of sync. This section carries the additions; an "Appendix: agent memory" can be added there later if they are merged.

## 9. Pre-launch checklist

- [ ] The raw log is kept, append-only, never edited
- [ ] Every record has `user_id` / `scope` / `source` / `ingested_at`, filled by code
- [ ] Every filtered field has an index
- [ ] After chunking, every chunk carries the parent's filter fields
- [ ] Superseding marks records, never deletes them; queries exclude superseded records by default
- [ ] Queries filter before searching; pgvector has iterative scan enabled or data is partitioned
- [ ] Queries are rewritten before embedding
- [ ] Deletion reaches summaries, caches and extracted facts, and leaves a deletion record
- [ ] An eval built from your own logs: plant → distract → probe, including "the fact was updated" and "the fact was never stated"

## 10. Sources

- Lesson plan notes [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md): §5.1 substrate follows query shape, §5.2 write policy, §5.3 retrieval config, §4.2 two clocks, §4.3 partitioning, §4.6 governance and the right to be forgotten, §3.5 two evictions
- Memory Palace results: [lab-log.zh.md](lab-log.zh.md) (Foyer G3, Flood F1 / F2 / Verify)
- Class Q&A: [notes.zh.md](notes.zh.md)
