# 企业 RAG 的权限感知检索（Permission-Aware Retrieval）

2026-11-15 · Rosso Han

## 摘要

在企业 RAG 里，授权是对**搜索空间的硬约束**，不是排序信号，也不是 prompt 里的一句指令。先算出用户能看的 chunk 集合，再只在这个集合里检索。

- **前置过滤（pre-filter），绝不后置过滤。** 一个 top-10 被后置过滤删掉 8 条，就静默变成了 top-2。
- **在摄取时给每个 chunk 挂上归一化安全描述符**，从源系统的 ACL 复制过来。
- **权限流水线要和内容流水线保持同步**：权限变更必须通过事件推送到索引，不能靠 TTL 过期。
- **要防六个泄漏面**，不只是检索：上下文、答案、引用/元数据、缓存、日志。

本文基于 Bootcamp 第 09 周 Module 5（Enterprise Entitlement-RAG）、第 06 周和第 10 周，以及微软 Azure AI Search 的官方文档。

## 问题：相关不等于被授权

常规 RAG 在整个语料库上找最相似的 chunk，这默认了每个用户都能看每一份文档。

```latex
d^* = \arg\max_{d \in D} \mathrm{sim}(q, d)
```

在混合的企业语料库里，一个完美的检索器就是一条高效的泄漏通道。员工问"Project Phoenix 有什么计划？"，最佳语义匹配可能是一份高管级的收购备忘录。

修复只需要一个下标——搜索空间本身取决于是谁在问：

```latex
D_u = \{\, d \in D : \mathrm{Authorized}(u, d) = 1 \,\}, \qquad d^* = \arg\max_{d \in D_u} \mathrm{sim}(q, d)
```

这个约束**不是**两样东西：它不是加到排序分数里的一项，所以再高的相关性也抵消不了缺失的权限；它也不是 system prompt 里的指令，那种指令可能被 prompt injection 说服放弃。`D_u` 要按每个用户、每次请求，用实时权限数据重新计算。

## 预防，而不是压制

授权必须发生在检索阶段，在未授权文本到达 LLM 之前。

| 模式 | 发生了什么 | 边界的性质 |
| --- | --- | --- |
| **Prevention（预防）** | 未授权 chunk 永远不进入上下文窗口 | 确定性基础设施（一个"控制"） |
| **Suppression（压制）** | 机密 chunk 进入上下文，再要求模型拒答 | 对随机系统的一个"请求"，离泄漏只差一次 prompt injection |

模型已经看到机密内容之后再生成的拒答，不等于防止了暴露。

### 六个泄漏面

检索只是机密信息泄漏的第一个地方。后三个是团队最常整个忘掉的。

1. **未授权检索**——chunk 进入候选集。
2. **未授权上下文**——chunk 进入 prompt。
3. **生成答案泄漏**——事实出现在回答里。
4. **引用 / 元数据泄漏**——标题、文件名或 URL 被暴露。
5. **缓存泄漏**——一个用户的特权答案被提供给另一个用户。
6. **日志 / trace 泄漏**——机密落进可观测性工具或 SIEM。

拒答本身也会泄漏："我找到了 `Acquisition-of-Company-X.pdf`，但你无权打开"就暴露了这次收购。测试必须区分**内容拒绝**（你不能读）和**资源发现拒绝**（你不能知道它存在）。

## 权限模型与归一化安全描述符

生产系统会把四种模型叠起来用，而不是只选一种，然后把所有判定压平成每个 chunk 上的一个描述符。

| 模型 | 核心理念 | 适用场景 | 要小心的坑 |
| --- | --- | --- | --- |
| ACL | 资源自己写明谁能看 | 源系统事实（SharePoint、Drive、Confluence）；逐文档例外 | 清单规模、漂移 |
| RBAC | 职位决定范围 | 粗粒度门禁；入职/转岗/离职的权限维护 | 角色爆炸 |
| ABAC | 由属性计算权限 | 密级、数据驻留、租户、设备安全态势 | 元数据质量；除非专门设计，否则会失败开放（fail open） |
| ReBAC | 图上的一条路径授予权限 | 项目、文件夹继承、组织层级、委托 | 图遍历代价（OpenFGA、SpiceDB） |

摄取层把各源系统的权限"方言"统一翻译成一种形状，并打在**每一个 chunk** 上：

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

设计规则：

- **缺失字段一律拒绝，绝不默认允许。**
- **拒绝优先于允许。**
- **描述符带版本号**，以便日后回放任何一次判定。
- **权限要穿过切片传下去。** 一个 chunk 被单独检索出来时，它自己必须能说清楚谁能看它。

企业 RAG 有两条摄取流水线：内容流水线（`parse → chunk → embed → index`）和权限流水线（`ACLs / groups / relationships → normalize → sync`）。两者的一致性本身就是安全属性。一份 10:01 建好索引的文档，权限在 10:05 变了，10:06 的一次查询就是一次正在等待发生的泄漏。

## 向量库如何存储记录、如何计算 filter

一次带过滤的查询是两套索引在配合：向量索引回答"什么相似"，元数据倒排索引回答"这个用户能看什么"。

### 存储

每个 chunk 分配一个内部整数 id，存在三个地方：

```
internal_id = 42
├─ 向量:     [0.12, -0.33, ...]          → 向量索引（HNSW 图 / IVF 桶）
├─ payload:  {tenant, allow_groups, deny_users, classification, regions, text, acl_version}
└─ 倒排索引，每个建了索引的字段一张表:
     tenant         : "acme"         → bitmap{1, 2, ..., 42, ...}
     allow_groups   : "finance"      → bitmap{7, 42, 90}
                      "executives"   → bitmap{42, 91}
     classification : "confidential" → bitmap{42, 88}
     regions        : "US"           → bitmap{3, 42, ...}
```

- **数组字段按元素分别建索引**，所以 `allow_groups $in groups` 就是各个组 bitmap 的并集。
- **bitmap 是压缩的**（通常是 Roaring Bitmap），求交、并、差都很快。
- **权限变更只需更新 payload 和 bitmap**，不用重新 embed——这就是权限流水线可以比内容流水线更新得更快的原因。

### Filter 计算

filter 表达式树被编译成 bitmap 上的集合运算，结果就是 `D_u`：

```
allowed = B[tenant=acme]
        ∩ ( B[allow_users=u123] ∪ B[allow_groups=g1] ∪ … ∪ B[allow_groups=gn] )
        ∖ B[deny_users=u123]                    # $nin = 差集 → 拒绝优先
        ∩ ( B[classification=public] ∪ B[classification=internal] ∪ … )
        ∩ B[regions=US]
```

这顺带免费得到了 fail-closed：一个没有 `classification` 字段的 chunk 不在任何 classification 的 bitmap 里，求交时自动被排除。

## 在允许集合内做检索

查询规划器会估算**选择率**（|allowed| / |总量|），再选执行策略。会破坏召回率的是后置过滤。

| 选择率 | 策略 | 工作方式 | 代价 |
| --- | --- | --- | --- |
| 允许集合很小（如几千条） | 暴力扫描 | 只对允许的向量打分 | 精确，而且在这个规模下很快 |
| 允许集合很大 | 带过滤的 HNSW 遍历 | 照常走图；不允许的节点只当跳板，不进入结果 | 召回率和速度接近无过滤时 |
| 中低（约 1–10%） | 过滤感知的图或分区 | 允许的节点稀疏，图会断开；用额外的边（ACORN、Qdrant payload 链接）或按租户物理分区 | 最难的区间，一定要做基准测试 |
| 任意（反模式） | 后置过滤 | 先搜 top-K，再删掉不允许的结果 | top-10 静默变成 top-2 |

常见引擎的做法（细节以最新文档为准）：

- **Qdrant**——用 payload 索引估算过滤基数；集合小就全量扫描，否则走可过滤的 HNSW。
- **Weaviate**——用倒排索引生成 allow-list；低于 `flatSearchCutoff` 时走平铺搜索；新版本支持 ACORN。
- **Milvus**——由 filter 生成 bitset，传入索引搜索。
- **pgvector**——先走 HNSW 再做 `WHERE`，本质上是后置过滤；0.8 版本加入了 iterative index scan 来缓解。

评估向量库时问一个问题：引擎是在遍历时**带着** bitmap 搜索，还是先搜完再删？

## 参考实现

查询侧根据用户身份构建 filter，然后作为前置过滤交给向量库。

```python
def secure_search(q, user, k=10):
    groups = expand_groups(user)          # 由 IdP / ReBAC 引擎展开
    f = {
      "tenant": {"$eq": user.tenant},
      "$or": [{"allow_users": {"$in": [user.id]}},
              {"allow_groups": {"$in": groups}}],
      "deny_users": {"$nin": [user.id]},
      "classification": {"$in": allowed_levels(user.clearance)},
      "regions": {"$in": [user.region]},
    }
    return vdb.query(embed(q), filter=f, top_k=k)  # 前置过滤，不要先搜再删
```

下面这个玩具向量库展示了 `vdb.query` 底下做了什么：倒排索引 → 允许集合 → 只在集合内算相似度。它走的是精确的暴力扫描路径；把它换成遍历时检查 `id in allowed` 就是 HNSW 路径。

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
                self.inv[field][x].add(iid)                 # 数组字段逐元素建倒排
        return iid

    def _eval(self, f):                                     # filter 树 -> 允许 id 集合
        ids = set(range(len(self.payload)))
        for field, cond in f.items():
            if field == "$or":
                s = set().union(*(self._eval(sub) for sub in cond))
            else:
                op, val = next(iter(cond.items()))
                vals = val if isinstance(val, list) else [val]
                hit = set().union(*(self.inv[field].get(x, set()) for x in vals))
                s = ids - hit if op == "$nin" else hit      # $eq/$in -> 并集；$nin -> 差集
            ids &= s
        return ids

    def query(self, qvec, filter, top_k=10):
        allowed = np.fromiter(self._eval(filter), dtype=int)   # 先算 D_u
        if allowed.size == 0:
            return []
        q = qvec / np.linalg.norm(qvec)
        scores = self.vecs[allowed] @ q                     # 只在 D_u 内算相似度
        top = allowed[np.argsort(-scores)[:top_k]]
        return [(int(i), self.payload[i]) for i in top]
```

未授权的向量从头到尾没有被打分，所以结果是精确的，不会像后置过滤那样缩水。

## 微软的做法：Azure AI Search

Azure AI Search 提供两种文档级裁剪方式，都是在搜索服务内部、查询时做权限检查，也就是前置过滤。

| 方式 | 摄取 | 查询 | 注意事项 |
| --- | --- | --- | --- |
| [原生文档级访问控制](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview)（preview） | Indexer 把 ADLS Gen2、Blob、SharePoint 的 ACL / RBAC 元数据带进索引；也能提取 Purview 敏感度标签 | 在 `x-ms-query-source-authorization` 请求头里带上用户的 Entra token；服务端验证并裁剪结果，不用自己写 filter，也不用展开嵌套组 | 仍是 preview；暂不支持 SharePoint groups；注意核对当前 API 版本 |
| [Security filters](https://docs.azure.cn/en-us/search/search-security-trimming-for-azure-search)（手动） | 你自己的流水线把权限主体字符串写进 `group_ids` 之类的字段 | 一个 OData filter，例如 `group_ids/any(g: search.in(g, 'finance,executives'))` | 字段只是字符串；正确性和时效性全靠你自己 |

同步滞后依然存在。[微软 ISE 的一篇博客](https://devblogs.microsoft.com/ise/?p=16628)提到：在 SharePoint 里撤销权限后，下一次 ingestion 跑完之前，用户在索引里可能仍能看到该内容——这正是上文 10:01 / 10:05 / 10:06 那个窗口。

## 上线检查清单

- [ ] 每个参与过滤的字段都建了 payload / 倒排索引；没建索引的字段会退化成逐条检查，很慢。
- [ ] 租户做物理隔离（collection、namespace 或分区），而不只是靠 filter。
- [ ] 处理组爆炸：摄取时压平组，或给每个用户缓存一份 allowed bitmap，由事件触发失效。
- [ ] 权限变更通过事件推送到索引，而不是 TTL。
- [ ] 描述符缺字段即拒绝；deny 名单覆盖 allow 名单。
- [ ] 缓存 key 包含权限指纹，答案绝不在不同权限集合之间复用。
- [ ] 引用和来源列表走与内容相同的过滤。
- [ ] 日志和 trace 对检索到的文本做脱敏或权限控制。
- [ ] 在低选择率（1–10%）下做召回率基准测试，而不只是在无过滤索引上测。

### 测试

- [ ] 单独取任意一个 chunk：不回查父文档，系统能否说清楚谁能看它？
- [ ] 撤销一个用户的权限后立刻查询：文档消失了吗？
- [ ] 对拒答措辞做红队测试：有没有哪句拒绝确认了文档的存在？

## 参考资料

微软文档（已打开核对）：

- [Document-level access control in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview)
- [Security filters for trimming results in Azure AI Search](https://docs.azure.cn/en-us/search/search-security-trimming-for-azure-search)
- [Azure AI Search 文档级访问控制发布公告](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/-/4418584)
- [微软 ISE 博客：SharePoint 权限同步，2026 年 4 月](https://devblogs.microsoft.com/ise/?p=16628)

论文与标准（凭记忆引用，未重新核对）：

- Pang et al., *Zanzibar: Google's Consistent, Global Authorization System*, USENIX ATC 2019
- Sandhu et al., *Role-Based Access Control Models*, IEEE Computer 1996
- Hu et al., *Guide to Attribute Based Access Control*, NIST SP 800-162, 2014
- Gollapudi et al., *Filtered-DiskANN*, WWW 2023
- Patel et al., *ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data*, SIGMOD 2024

课程资料：LLM and Enterprise RAG Bootcamp [第 09 周 Module 5（Enterprise Entitlement-RAG）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_09/week-09.zh.md)（§十一）、[第 06 周（Guardrails）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_06/week-06.zh.md)、[第 10 周（Access control）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_10/week-10.zh.md)。
