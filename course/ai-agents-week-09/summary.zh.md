# Week 09 今天学了什么（课中版，2026-11-15）

> **Memory is not storage; it is policy.** 写什么、读什么、合并什么、忘什么。
> **The harness remembers, not the model.**

进度：上午 Prototype 11 个实验 ✅ → 下午 Orientation + Act I（到 deck p.51）✅ → Memory Palace 一楼三个房间 ✅ → Parking Board 讨论 ✅。Owl、Speakeasy 待补。

---

## 1. 上午：The Hundred-Million-Year Prototype（拿自己的大脑做实验）

| # | 实验 | 我的答案 / 观察 | lesson |
| --- | --- | --- | --- |
| 2 | The flood | **一碗好味噌汤的香气 → 20 年前在日本工作的日子** | 记忆一直存着，缺的是 cue；多数失败是**检索**失败 |
| 3 | Edited narrative | 一直记成「天将降大任于**斯**人也」，原文是「**是**人」（中文圈的曼德拉效应） | 每次回忆都是重写；只有原始记录能纠错 |
| 4 | Diary decision | 拍婚礼不拍通勤：通勤能从规律重建，婚礼不能 | 只写**无法再生**的东西；只记好事 → 记忆有偏 |
| 5 | Shoelaces | 描述漏了「从洞里穿过去形成第二个环」；学到结的名字：bow knot = double-slipped reef knot，方向错 = granny knot | **会做 ≠ 说得出**（procedural） |
| 6 | Answer as-of | 2015 / 2020 / 今天的答案没有一个是错的，只是过期 | 事实 = 值 + **有效区间** |
| 7 | Two clocks | 晚知道的消息需要**两个时间戳**：发生时间 + 知道时间 | 双时态；审计靠第二个时钟 |
| 9 | 演变 / 纠正 / 矛盾 | 搬家 = 演变；Pluto = 定义演变（陷阱）；Sydney→Canberra = 纠正；Alice 3 点 / Bob 4 点 = 矛盾 | naive memory 只会「newer wins」 |

收尾两页：人脑是一亿年进化搜出来的原型，**借蓝图，不借局限**；agent 能做人脑做不到的：逐字重放、移植记忆、共享 skill。

（实验 1、8、10、11 未截图，待录播补）

## 2. 下午：Act I 理论（deck p.5–46）

| 页 | 一句话 |
| --- | --- |
| p.5 两段题词 | Borges：记太多就不能思考（→ forget / consolidate）；Buñuel：没有记忆就没有连贯（→ write / read）；记忆策略在两者之间 |
| p.7 W8 Owl | 缺信息 → 优化 prompt；缺知识 → 检索；缺能力 → 换 / 训模型；0 分先查是不是拒答 |
| p.9–11 Stories | 没有 memory 的 agent = 西西弗斯；前八周的成果因为**写到磁盘**才算数；三笔欠账（Simulacra、MemGPT、memory 周）今天兑现 |
| p.12 边界 | 不在 context window 里 = **不存在**（不是「难找」） |
| p.13 定义 | memory = 窗口外**能被换入**的东西；核心动作是**跨越边界** |
| 白板 | 河 = 边界；**模型和 context window 在这岸**；对岸 = skills · semantic · episodic · tools；**摆渡人 = harness 的一部分**；高 / 低水位线 + 锯齿波 = compaction 的节奏 |
| p.14 | Context = RAM，memory = disk；context window / recall store / archival store 三层（MemGPT） |
| p.16 / p.40 | **四层**：working = 窗口；episodic = trace；semantic = 事实（读路径是 RAG）；procedural = skill library |
| p.17 / p.46 | **四个动词**：write · read · consolidate · forget；**storage 不在其中** |
| p.18 | 遗忘是功能：隐私、过期事实自信地答错、上季度的事实干扰本季度 |
| p.19 | ⭐ **Memory is not storage; it is policy** |
| p.20 | 三个开放问题：谁在记（harness）、压缩会丢什么（plant–compact–probe）、事实变了要不要删（不删，标过期） |
| p.35–36 | Checkpoint：窗口里的 token · paged into it · the harness |
| p.37 / 38 / 39 | Tulving（episodic vs semantic）· Squire（declarative vs procedural，H.M. 病人）· Baddeley（working memory = 书桌不是书架）→ 三人合起来 = 四层 |
| p.41 | procedural memory **就是** skill library，W3 的欠账还清；skill 的每个问题都有 memory 的孪生问题 |
| p.43 | SOAR 的 chunking（卡住 → 推理 → 编译成规则）= Voyager 的 skill 库；ACT-R 的频率 / 最近 / 相关 ≈ Smallville 打分 |
| p.47 | **VoR(m) = p·g − κ(c)**，> 0 才放进窗口；两个杠杆：**discriminative**（该用上时 p 高）+ **lean**（c 小） |
| p.48 | 例题：800 token 的经历门槛 0.25 > p = 0.20 → 不放；压成 150 token 摘要（原文留磁盘）门槛 0.047 → 放；只拉了「精简」杠杆 |
| p.49 | 召回 = 老虎机：UCB = ĝ + β√(ln T / n)；试得少的弱记忆被**故意**召回（0.94 vs 1.82），约 11 次后奖励消退 = 有上限的探索税 |
| p.51 | Checkpoint 3：四个动词 · storage 被排除 · 两个杠杆 · 探索奖励 |

## 3. Memory Palace 一楼（详见 [lab-log](lab-log.zh.md)）

| 房间 | 结果 | lesson |
| --- | --- | --- |
| 🏛️ Foyer G1 | 第 15 轮 recent turns 421 / 773 token 最大；第 3 轮反而是 system prompt 最大 | 哪段最大取决于第几轮；历史线性增长，迟早要压缩 |
| 🏛️ Foyer G2 | 只关 pinned notes 仍答出 $4,800（对话历史里也有）；再关 recent turns → 说「不知道」，没编 | 不在窗口里 = 不存在；同一事实可能冗余；Haiku 会 abstain |
| 🏛️ Foyer G3 | 检索放在历史前：命中率 64% → 37%，成本 +58% | **band 顺序就是成本决策** |
| 🌊 Flood F1 | 原问题 e13 不在前 8；改写成「Meera decide Diya floor lamp brass base」→ 进前 3 | 先改 cue，不改权重 |
| 🌊 Flood Verify | 论文等权重只答对 5/12；relevance 2.5 → 11/12（recency 再降到 0.5 → 12/12） | **relevance 必须领头**；权重就是策略 |
| 👟 Shoelaces | 离线 6/6 规则、170 token；在线：no memory 0/12 · five traces 12/12（838 token）· my skill 12/12（170 token） | 正确率打平，skill 省 80% token；episodes 进、规则出 = consolidation |

## 4. 课上搞清楚的几个问题

- **episodic memory 在 agent 里** = 保存下来的 trace（对话、工具调用、结果、时间戳），append-only；**不整个发给 LLM**，只挑相关几条换入，或离线提炼成事实 / skill
- **semantic memory ≠ RAG**：RAG 只是它的**读**路径；完整的还有写、合并、遗忘。「RAG = 关掉写入的 memory」
- **术语方向**：把东西放进 context window 叫 **read / page in**；从窗口存到 store 叫 **write / page out**
- **情绪算哪一层**：不是单独一层；情绪词汇是 semantic，某次经历里的感受是 episodic 的一部分，条件反射是 nondeclarative，强度是调节器（agent 里 = importance 分数）
- **frontier vs open-weight**：memory 住在 harness，两者都适用；open-weight 还能微调、控制 KV-cache
- **Parking Board（Erwin）**：评估 agent 复杂度用 METR time horizon、SWE-bench Verified 等；可靠性看 τ²-bench 的 **pass^k**、Vending-Bench；上线前用自己的日志建 eval + no-regress gate
- **Parking Board 其他**：consolidation 能生成 procedural（Shoelaces、SOAR、Voyager）；「每 5.8 天减半」=「半衰期 6 天」= γ 0.995/小时，ln0.5 / ln0.995 ≈ 138 小时
- **append-log 在 harness 里**：LLM 不需要 log，**harness 需要**；log 是 ground truth，事实库、向量、skill、recent turns 都从它派生；还用于压缩后的原件、出处审计、删除、召回统计（UCB 的 ĝ、n）、评测语料、缓存命中。开发用 JSONL，上线用只追加的数据库表；agent 的 episodic log ≠ 程序运行日志
- **模型 vs harness vs App**：模型只生成；harness 拼窗口、管记忆和工具；App = 界面 + harness + 模型。豆包、DeepSeek 都既有模型也有 App
- **DeepSeek Harness**（[github](https://github.com/deepseek-ai/deepseek-harness)，2026 开源）：一切皆插件（Cordis），连 agent loop 都可替换；会话事件日志只追加、是模型所见上下文的来源；**「Model-visible means logged」**；JSONL 分代存储，已提交文件永不改写 → 印证今天讲的 log 原则
- **Cursor 规则包**（`CURSOR_RULES_FOR_WORKSHOP/`）：讲师的 14 条编码规范；`alwaysApply: true` 的长规则每轮都占窗口 = 交注意力税，和 VoR 是同一笔账

## 5. 记忆存储：向量库、关系库、metadata（完整版见 [memory-storage-guide.zh.md](memory-storage-guide.zh.md)）

- **KV cache ≠ 向量库**：KV cache 是推理时的注意力缓存（窗口之内）；RAG 和记忆用的是窗口外的向量库 / 关系库
- **教材推荐：substrate follows query shape**。默认路线：先 **日志 + 关系表** → 召回不够再加 **向量索引** → 关系 / 时间查询证明需要时才加 **图**
- **什么时候用哪个**：能写成 `WHERE key = value` 的用关系表；只能说「像这个」的用向量；要回答「当时」的加时间字段；生产常用 **Postgres + pgvector** 或 **Qdrant + payload** 两者结合
- **每条记录 = 文本 + 向量 + metadata**；metadata 支撑分区 / 权限、时效、按时间回放、重排、出处、删除；**改 metadata 不用重算向量**
- **谁填字段**：`user_id` / `scope` / `source` / `ingested_at` 由**代码**填，绝不让 LLM 猜；`entities` / `topic` / `importance` / `event_time` 由 **LLM 抽取**
- **chunking**：对话记忆按**原子事实**存、写入时解析代词；长文档切片时**每片继承父文档的过滤字段**；metadata 不进 embedding
- **存法**：Qdrant 用 payload + `create_payload_index`，遍历 HNSW 时一起过滤；Postgres 用普通列 / JSONB + B-tree / GIN / 部分索引，pgvector 默认后置过滤，0.8 起开 `hnsw.iterative_scan`
- **对[权限感知检索](permission-aware-retrieval.zh.md)的补充**：那篇讲透了「谁能看」，记忆库还要：时效字段（`valid_to` / `superseded_by`，默认只查有效的）、两个时钟、权限字段在 **agent 写入时由代码盖章**（没有源系统 ACL 可抄）、session 草稿不能升格成长期事实、写入要过 governor、被遗忘要追到摘要和衍生事实。决定**不改那篇**（RAG 项目和在线文档各有一份，改一处会不同步），补充写在 guide 第 8 节

## 6. 今天创建的东西

| 文件 | 内容 |
| --- | --- |
| [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md) | 讲义 37 页全本精读（W9 + W10）+ 自测 12 题 |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 速览 + 复述题 |
| [notes.zh.md](notes.zh.md) | 逐页课堂笔记：Prototype deck p.1–20、新 deck p.5–46、白板、课外问答 |
| [lab-log.zh.md](lab-log.zh.md) | 11 个实验 + Memory Palace 一楼三个房间的预测与结果 |
| [learned-so-far.zh.md](learned-so-far.zh.md) | 课中时间线 |
| [memory-storage-guide.zh.md](memory-storage-guide.zh.md) · [English](memory-storage-guide.md) | **课外**：向量库 / 关系库怎么选、metadata 为什么需要、chunking 和写入流程、Qdrant vs Postgres、对权限检索的补充 |
| [permission-aware-retrieval.md](permission-aware-retrieval.md) 等 4 个文件 + [memgpt-as-system-5.md](memgpt-as-system-5.md) | **课外**：权限感知检索（英 / 中 / 精简 / 幻灯片）、MemGPT 能否作为 System 5 的基础（提交稿）；出自 RAG Bootcamp Module 5 |
| [../../learning/2026-11-15-memory-store-filters/](../../learning/2026-11-15-memory-store-filters/README.md) | **课外**：记忆库 metadata 与过滤的可跑例子（Qdrant 版已跑通，Postgres 版未实跑） |
| [../../learning/2026-11-15-fine-tuning-lora/](../../learning/2026-11-15-fine-tuning-lora/README.md) | **课外**：LoRA / QLoRA 微调入门（设计图 + 代码，未实跑） |
| [../ai-agents-week-10/index.md](../ai-agents-week-10/index.md) | W10 入口 |

## 7. 待办

- [ ] 录播补：实验 1、8、10、11；deck p.15、p.42、p.44–45；Owl 五行；Speakeasy
- [ ] 核实：p.17 READ 是乘法还是加权和；白板容器底部黄色层的含义；摆渡人的原话；课程里「System 5」的定义
- [ ] 下载 Memory Palace 手册放进 `uploads/`
- [ ] 读 MemGPT、Zep、Lost in the Middle；重读 Generative Agents §4
- [ ] 跑 `pg_demo.py`（`docker compose up -d`）；试跑 LoRA 例子
- [ ] 读 DeepSeek Harness 的 session / subsystems 文档，看它怎么做记忆和压缩（对应 W10 Act II）
