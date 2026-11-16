# 记忆存储怎么选、怎么存：向量库、关系库、chunking、embedding 与 metadata

2026-11-15 · W9 课上问答整理 · English: [memory-storage-guide.md](memory-storage-guide.md) · 可跑的例子：[learning/2026-11-15-memory-store-filters](../../learning/2026-11-15-memory-store-filters/README.md) · 姊妹篇：[权限感知检索](permission-aware-retrieval.zh.md)

> **一句话：存储方式由你要问的问题决定。** 确定的事实放关系表，模糊的回忆放向量索引，原始经过放日志；每条记录都带好 metadata，过滤、时效、权限、审计和删除才做得到。
> 讲义原话：*Substrate follows query shape.* · *Storage is easy. The policy is the whole game.*

---

## 1. 先分清三个容易混的东西

| 名字 | 是什么 | 在哪一层 | 谁负责 |
| --- | --- | --- | --- |
| **KV cache** | 推理时缓存已算过的注意力 key/value，下一个 token 不用重算；G3 的「前缀缓存」就是它 | 模型服务内部，**context window 之内** | 基础设施，测吞吐量 |
| **向量库** | 把文本转成向量，按「意思相近」检索 | **窗口之外**的记忆库 | 你的 harness，测召回和行为 |
| **关系库** | 表、列、索引，按精确条件查 | 窗口之外的记忆库 | 你的 harness |

讲义 Act II「两种驱逐，两个海拔」：KV cache 的驱逐是服务优化，记忆的回收是设计决策，混在一起会在错误的层上 debug。**RAG 用的是后两者，不是 KV cache。**

## 2. 教材推荐：按查询形状选基底（Practice I）

| 基底 | 答得好的问题 | 答不好的 | 写入成本 |
| --- | --- | --- | --- |
| **追加日志**（append-log） | 发生了什么、按什么顺序 | 其他都差 | 几乎为 0；**永远保留**，是 ground truth，抽取逻辑改进时能重建其他索引，也是评测语料 |
| **关系表** | 有类型、按 key 的事实：时区、会员等级、交货期 | 「意思相近」 | 几乎为 0 |
| **向量索引** | 联想召回：「跟这个情况类似的记忆」 | 「周二到周五之间变了什么」 | 每次写入一次 embedding 调用 + 多一个服务要运维 |
| **时序图** | 关系和时间：谁和谁有关、什么时候变的 | — | 每次写入一次 **LLM 抽取**调用（最贵） |

**默认路线（要背）：** 先用 **日志 + 关系表** → 召回确实不够时**加向量索引** → 只有当关系或时间类查询**证明**需要边时才加**图**。

**自研还是用框架（Letta / Mem0 / Zep）：** 框架的默认策略比你这季度能写出来的好 → 用框架；策略就是你产品的核心 → 自研。

## 3. 什么时候用哪个

| 场景 | 用 | 例子（Memory Palace / Harbor & Hearth） |
| --- | --- | --- |
| 按 key 查一个确定的值 | **关系表** | 「Kolkata 交货期几周？」「Jaipur 最少几箱？」 |
| 需要事务、JOIN、和业务数据放一起 | **关系表** | 订单、库存、发票审批人 |
| 事实会变、要查「当时是什么」 | **关系表**（`valid_from` / `valid_to`）或时序图 | 旧仓库地址 → 新仓库地址 |
| 用户问法和存储用词不一样 | **向量索引** | Flood F1：「一直倒的东西」↔「落地灯一直晃」 |
| 从大量经历里找「类似的情况」 | **向量索引** | 「上次供应商延误我们怎么处理的？」 |
| 两者都要：先按条件圈范围，再按意思排序 | **向量 + 过滤**（Postgres + pgvector，或 Qdrant + payload） | 「Meera 的、仍有效的、关于物流的记忆里，最相关的 5 条」 |
| 记录发生了什么 | **日志** | 每轮对话、工具调用、结果 |

**判断口诀：** 能写成 `WHERE key = value` 的，用关系表；只能说「像这个」的，用向量；要回答「当时」的，加时间字段。

## 4. 一条记录长什么样：文本 + 向量 + metadata

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

### 为什么必须有 metadata

只有向量，你只能问「哪些最像」。下面这些事全靠 metadata：

| 需要做的事 | 靠哪些字段 | 没有的后果 |
| --- | --- | --- |
| **分区 / 权限**：Alice 的不给 Bob | `user_id` `scope` `tenant` `allow_groups` | 检索器越准，泄漏越精准 |
| **时效**：只要仍有效的 | `valid` `valid_to` `superseded_by` | 旧地址诈尸（Flood F2），自信地答错 |
| **按时间回放**：「当时是什么」 | `event_time` + `ingested_at`（两个时钟） | 没法审计「agent 为什么订错票」 |
| **重排信号** | `importance` `event_time`（recency） | 只能按相似度排，最近和重要的事浮不上来 |
| **出处 / 防投毒** | `source` `ingested_at` | 分不清是谁写的、能不能信 |
| **删除 / 被遗忘权** | `user_id` `source` | 删不干净，也证明不了删过 |
| **少检索无关的** | `entities` `topic` `memory_type` | 噪声挤进 top-k（Flood 里 e47 靠「最近」排第 2） |

**关键性质：改 metadata 不用重算向量。** 标过期、改权限、调重要性都只改 payload 或列，所以权限和时效可以比内容变得快得多。

## 5. 写入流程：chunking、embedding、填 metadata

```
一轮对话 / 一份文档
  → ① 抽取：原子事实，代词现在就解析（"she said yes" 三次会话后没人懂）
  → ② 写入门槛：三个会话后还重要吗？琐事不进长期记忆（日志里还在）
  → ③ 填 metadata：权限和审计字段由代码填；语义字段由 LLM 抽取
  → ④ 切分（长文档）：每个片段继承父文档的全部过滤字段
  → ⑤ embedding：只对 text 算向量
  → ⑥ 比对已有记忆：新增 / 更新 / 取代 / 不变（Mem0 的 ADD / UPDATE / DELETE / NOOP）
  → ⑦ 写入：向量进向量索引，metadata 进 payload 或列；被取代的只标过期，不删
```

### 谁填哪些字段（要背）

| 字段 | 谁填 | 为什么 |
| --- | --- | --- |
| `user_id` `scope` `tenant` `source` `ingested_at`、权限字段 | **代码**，从会话上下文或源系统 ACL 取 | 权限和审计，**绝不交给 LLM 猜** |
| `text` `entities` `topic` `memory_type` `importance` `event_time` | **LLM 抽取**（结构化输出） | 需要理解语义 |
| `valid` `valid_to` `superseded_by` | **后续写入时更新** | 取代 = 关闭有效窗口 |

### Chunking：记忆和文档不一样

| | 对话记忆 | 长文档（RAG 语料） |
| --- | --- | --- |
| 单位 | **一条原子事实**一条记录，不按长度切 | 按段落 / 标题 / 固定长度切，带少量重叠 |
| 关键 | 写入时解析代词，让每条**自包含** | 每个片段**继承父文档 metadata**，必要时在片段前加一句上下文（「本段出自《X 合同》第 3 节」） |
| 原因 | 检索是按条发生的 | 检索是按片段发生的，单独被捞出的片段必须自己说得清「属于谁、什么时候的」 |

### Embedding 要注意

- 只对 `text` 算向量，**metadata 不进 embedding**（进去了就没法精确过滤，还会污染相似度）
- 查询前先**改写问题**：把「那个东西」「它」换成具体名词（Flood F1）
- 换 embedding 模型要**全部重算**；所以日志要保留，可以重建

## 6. 存在哪里：Qdrant vs Postgres + pgvector

| | Qdrant | Postgres + pgvector |
| --- | --- | --- |
| metadata | **payload**（每个 point 一个 JSON） | **普通列** + 可选 `jsonb` |
| 过滤索引 | `create_payload_index`（keyword / bool / datetime …），**要显式建** | B-tree；GIN（数组 / JSONB）；**部分索引** `WHERE valid` |
| 过滤方式 | 遍历 HNSW 时一起过滤；允许集合很小时改成暴力扫描 | 默认先 HNSW 再 `WHERE` = 后置过滤；0.8 起 `SET hnsw.iterative_scan = relaxed_order` 缓解 |
| 改 / 删 | `set_payload` / `delete(FilterSelector)` | `UPDATE` / `DELETE` |
| 适合 | 数据量大、过滤条件多变、过滤很严 | 中小规模、要事务和 JOIN、团队已经在用 Postgres |

代码见 [qdrant_demo.py](../../learning/2026-11-15-memory-store-filters/qdrant_demo.py)（已跑通）和 [pg_demo.py](../../learning/2026-11-15-memory-store-filters/pg_demo.py)。

## 7. 查询流程

```python
q = rewrite_query(question)                        # 1. 改写：代词 → 具体名词
f = {"user_id": me, "scope": ["user", "app"],      # 2. 过滤：本人 + 全局，仍有效，不含别人的 session
     "valid": True}
cands = store.search(embed(q), filter=f, k=20)     # 3. 多取：在允许集合里找 20 条
top = rerank(cands, w_rel=3, w_rec=0.5, w_imp=1)[:5]   # 4. 重排：Smallville 三项（Flood 调出来的权重）
context = render(top)                              # 5. 进 context window：放在历史之后（G3：顺序就是成本）
```

讲义的检索配置（Practice I）：`candidate_k: 20 · final_k: 5 · rerank: cross_encoder · exclude_superseded: true · query_rewrite: true`。

## 8. 和权限感知检索笔记的关系

[permission-aware-retrieval.zh.md](permission-aware-retrieval.zh.md) 已经讲透了「**谁能看**」：先过滤再检索、每个 chunk 带归一化安全描述符、缺字段即拒绝、deny 优先、权限靠事件同步、bitmap 怎么算、六个泄漏面。**这些对记忆库全部适用。**

今天的课补充了记忆库特有的几点，那篇里还没有：

| 记忆库额外要的 | 为什么 | 对应 |
| --- | --- | --- |
| **时效字段**：`valid` `valid_to` `superseded_by`，查询默认 `valid = true` | 文档改了会重新索引；记忆是**不断被新事实取代**的 | 实验 6、7、9；`exclude_superseded` |
| **两个时钟**：`event_time` + `ingested_at` | 要能回答「当时相信什么」 | Act III |
| **写入方是 agent 自己**，权限字段在写入时由代码盖章 | RAG 的权限来自源系统 ACL；记忆是 agent 自己写的，没有源系统可抄 | 分区抽屉、ADK 前缀 |
| **session 作用域**的草稿不能升格成长期事实 | 临时假设被当成事实 = 毒化以后所有回答 | 「20% 折扣」草稿 |
| **写入要过 governor**：出处、只追加、行为评测 | agent 能改自己的记忆 = 投毒面 | Act III 治理；你的 [MemGPT × System 5](memgpt-as-system-5.md)：agent 能读不能写 |
| **被遗忘要追到衍生物**：摘要、索引、缓存、提炼出的事实 | 删原文不算删；只留删除事件记录，不留内容 | 被遗忘权 = GC 规格 |

**建议：** 不改那篇（它在 RAG 项目和在线共享文档里各有一份，改一处会不同步），在本文第 8 节做补充；以后想合并，再给那篇加一个「附录：agent 记忆」。

## 9. 上线前检查清单

- [ ] 原始日志保留、只追加、不改
- [ ] 每条记录都有 `user_id` / `scope` / `source` / `ingested_at`，由代码填
- [ ] 每个要过滤的字段都建了索引
- [ ] 切分后每个片段都带父文档的过滤字段
- [ ] 取代只标过期，不删；查询默认排除已取代的
- [ ] 查询先过滤再检索；pgvector 开了迭代扫描或做了分区
- [ ] 查询前改写问题
- [ ] 删除能追到摘要、缓存、提炼出的事实，并留下删除记录
- [ ] 用自己的日志建评测：植入 → 干扰 → 提问；包括「事实已更新」和「从没说过」两类

## 10. 来源

- 讲义 [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)：§5.1 基底跟着查询形状走、§5.2 写策略、§5.3 检索配置、§4.2 两个时钟、§4.3 分区、§4.6 治理与被遗忘权、§3.5 两种驱逐
- Memory Palace 实验结果：[lab-log.zh.md](lab-log.zh.md)（Foyer G3、Flood F1/F2/Verify）
- 课堂问答：[notes.zh.md](notes.zh.md)
