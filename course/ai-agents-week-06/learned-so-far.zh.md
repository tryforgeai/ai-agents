# Week 06 学习进度 · 2026-10-25（已下课，最后一条 19:58）

> 课上实时整理。细节在 [notes.zh.md](notes.zh.md)（板书 + deck 课堂补充）和 [lab-log.zh.md](lab-log.zh.md)（门的记录）。下课后并入 [summary.zh.md](summary.zh.md) 课后版。

## 一句话

**label 就是 prompt，模型只读 label。** 每个工具描述都要写清：**什么时候用、什么时候不用、代价是什么**——而且只对**真正读它的那个模型**有效。label 只能请求，盒子才能强制。

## 1. 学到的概念（按上课顺序）

| 时间 | 来源 | 学到了什么 |
| --- | --- | --- |
| 11:15 | 复述 · deck p.5 | 一次工具调用经过 label 的**四站**：description → *调不调*；schema → *怎么调*；error → *失败后下一步*；**contract** → *重试会发生什么（一次还是两次）* |
| 11:44 | 板书 WWW H | 工具说明的骨架：**What / When / When Not / How / Why**。When Not 分两种：**范围**（别的活不干）和**前置条件**（没蚀刻不能敲）。How 里的数值约束应推进 schema。Why = **后置条件**（调用后什么为真） |
| 12:00 | 板书 Epistemic Uncertainty | 模型隔着协议看不到实现，它的不确定是**认知不确定**（缺信息）→ 写好 label 能消除。**偶然不确定**（超时、执行了没回话）label 治不了 → 靠幂等 key 和重试规则（盒子） |
| 12:03 | 板书 两种做法 | 工具进上下文两条路：**① 全部挂载**（工具少时，信息全但贵）；**② 搜索后拉入**（工具多时，便宜，但 label 要先赢搜索再赢选择）。PayPal 例：2,000+ 工具全挂 140k token → 搜索 1.3k |
| 16:05 | deck p.21 | 门的场景：顾客 → Hermes ⇄ MCP ⇄ refund-desk → ledger（店的损失）。上周 Refund Desk 三轮 = 今天门 1 / 8 / 12 |
| 16:10 | deck p.32 · 门 1 | **Say what the store wants**：积分写"首选、免费、先提"，退卡写"代价 +$15、只在顾客要钱时用"。= 锤子规则的退款版 |
| 16:15 | deck p.33 · 门 11 | **No universally good description**：DocsChisel（`2608.10037`）17 个字段里 12 个效果随设置翻转（去掉 "optional" 帮 Haiku 4.5 +7.5，害 GPT-4o / GLM-5）→ **用读它的模型测 label** |
| 16:20 | deck p.34 · 门 11 | **Capability mirage**（`2608.04719`）：描述承诺多于工具能做的。最能骗住**前沿模型**；8 个模型易感性差约 36 倍 → **夸大的 label 是模型会信的谎** |
| 16:25 | deck p.35 · 门 3 | **Nothing like leather**：两个工具都说能解决问题 = 木匠和皮匠在城门口吵架，模型随机挑。**能少给选择就少给；非给不可，由 label 裁决** |
| 16:50 | deck p.40–41 · 门 8 | **Errors point out of the room → Name the door**：3,001 条 MCP 错误信息只有 949 条说下一步；凭证错误里 62/67 指向终端 / 配置 / 网页，agent 走不了。改成点名 server 工具（`renew_session()` + 同一 `idempotency_key` 重试）后恢复率 84%（凭证）/ 88%（限流）。**agent 只能走 server 有的门** |
| 16:53 | deck p.42 · 门 12 | **The second refund**：网关已退款、回复超时丢失 → agent 看到 error 再请求一次 → 钱动两次。**error ≠ 没执行**；调用里没有任何东西表明是同一笔请求 → 解药是 `idempotency_key`（同 key 返回已存结果、不动钱）。label 治不了偶然不确定，契约 / 盒子才行 |
| 16:54 | deck p.43 · 门 12 | **Once, however often you ask**：refund(k)∘refund(k) = refund(k)。调用方每个意图生成一个 key → server 按 key 存结果 → 同 key 返回存好的结果、不动钱。**重试应该问"发生了吗？"，而不是再下一单**。key 必须由调用方生成，重试复用、新意图才换 |
| 16:55 | deck p.44 · 门 12 | **Three ways the same call arrives twice**：协议（多轮请求按设计重发原调用）· Hermes（传输失败只重放 `readOnlyHint` 工具，其余返回 `outcome_uncertain`）· Claude Code 2.1.287（线上修过"偶尔执行两次"）。**重复到达是常态 → 写操作必须幂等**；`readOnlyHint` 标错的代价不对称 |
| 17:12 | 另一份 deck · Inference | **Prefill**（读 prompt，算力瓶颈）→ **Decode**（逐 token 写，显存带宽瓶颈）→ **KV cache**（每 token 的笔记，随用户和 token 增长）。Llama 3.1 70B FP16：0.33 MB/token，128K 对话 43 GB，5 个对话 215 GB > 权重 140 GB（已核算）。**KV cache 能比模型还大** → 上下文里每个 token 都占显存 |
| 17:13 | 另一份 deck · Inference | **三种负载形状**：一次性长上下文（容量）· 多轮对话（保留：cache 要活过两轮之间）· agent 循环（放置：大的共享前缀 + 长空闲）。**放不下时**：8×80 GB = 640 GB，权重 140 + 11 用户 × 43 = 613，第 12 个放不下 → 排队 / 丢掉再重算（约 6 s prefill）/ 加卡（只为显存）/ **offload 到 CPU 内存或池**。闲置对话占 GPU 显存，便宜的内存层让它们去那里等 |
| 17:14 | 另一份 deck · Inference | **Agentic workloads make inference stateful**：按"多久后再用"放层——秒→HBM、分钟→Host DRAM、小时→Pooled、天→Local SSD。太早驱逐 → 重取落在 TTFT；留太久 → HBM 烧在没人读的 block 上。反例：编码 agent 大 block 被降级、下一轮就要用；小 agent 闲一周却停在 HBM。**放哪要靠应用告诉推理层**（≈ 给推理层写的 label：`ttlMs` / `cacheScope`、prompt cache TTL、`readOnlyHint`） |
| 17:17 | 另一份 deck · Inference | **What a memory shortage costs**：每 token 成本 = 每小时服务器成本（固定）÷ 每小时**有用** token（显存不够就下降）。延迟侧：被驱逐的用户首 token 多等约 6 s、新用户排队。成本侧：重算不产出新 token、批次变小（每次读权重分摊的人少）、为显存买卡算力闲置。**账单不变，有用 token 少 → 每个 token 都更贵** |
| 17:18 | 另一份 deck · Inference | **The inference server**：Users → Gateway（路由）→ Inference server（Scheduler 决定谁跑 · KV cache manager 管 block / 复用 / 驱逐 · Model runner 发 kernel）→ HBM（权重 / KV cache / 工作缓冲），溢出到 DRAM / CXL / SSD / pool。四步：到达 → 选 server → **编批 + 找或分配 cache** → 计算并流式返回。**第 3 步是内存决定点**。注意推理 gateway ≠ MCP gateway |
| 17:19 | 另一份 deck · Inference | **Multi-tenancy**（一张卡服务多人）：**Continuous batching**（每步都有请求进出，GPU 一直满批）· **Paged KV cache**（小块按需分配，不预留整段）· **Prefix sharing**（相同开头共用同一批 block，system prompt 只存一次）。**三者都依赖 block 留在显存里**。对 agent：工具列表稳定 + 不变的放前面，前缀才能共享 |
| 17:20 | 另一份 deck · Inference | **vLLM**：最常用的开源推理 server，让分页 KV cache 成为主流。PagedAttention（小块，像 OS 内存页）· continuous batching · prefix caching（**LRU 先驱逐**）。扩展点 **KV connector API** → LMCache / Mooncake / 其他，把本该驱逐的 KV 挪到 GPU 外的内存（= offload 的落地）。KV connector 也是一种"插头" |
| 17:21 | 另一份 deck · Inference | **SGLang**：围绕复用设计，缓存的前缀存成一棵树（system prompt 是根，每个对话 / agent 循环是分支）；新请求沿树走到匹配为止。**RadixAttention**（前缀树留在 GPU 显存）· **HiCache**（树延伸到 CPU 内存和存储）。agent 循环天然是一条长分支 → 前面任何一处改动，后面整条分支失效 |
| 17:21 | 另一份 deck · Inference | **NVIDIA Dynamo**：服务器之上的编排层，把 vLLM / SGLang / TensorRT-LLM 当 worker 跑。**KV-aware routing**（发给 cache 最多又不过载的 worker，靠 block events 知道谁有什么）· **Planner**（按流量增减 worker）· **Disaggregation**（prefill / decode 拆到不同 GPU，cache 走 NIXL）· **KV Block Manager**（每 worker 一个，在 GPU / CPU / SSD / 远程存储间搬 block）。**引擎管单机内存，Dynamo 管跨机内存** |
| 17:23 | 另一份 deck · Inference | **开源内存扩展：LMCache + Mooncake**。machine = 物理机，instance = 一个 vLLM 副本。LMCache 让同机 instance 共享 CPU 内存里的 cache；Mooncake Store 把多台机器的 CPU 内存拼成一个池，master 记 chunk 位置，RDMA 拉取、跳过 prefill。**同样的文本在任何 instance 上算出同样的 chunk ID** → 内容寻址，≈ 门 12 的 idempotency key（稳定身份把"第二次"变成"查第一次"） |
| 17:26 | 另一份 deck · Inference | **Composable heterogenous memory**：三种 SLA——latency（decode）· bandwidth（长上下文输入）· capacity（大块可复用上下文省重算）。九层金字塔 L0 SRAM → L1 HBM → L2 DRAM → L3 SSD → L4 存储服务器，AI 时代新增 **X.5 层**（3D 堆叠 DRAM、光互连 HBM、CXL / UALink 内存、以太网内存池）把数量级断崖补成阶梯。L3.5（~µs、几十 TB）就是 Mooncake 池所在层。**不同负载会跨不同传输组合使用异构内存** |
| 17:28 | 另一份 deck · Inference | **Composable memory = pooled（多 server 共享）+ tiered（每个 block 放合适的层）+ attachable（加内存不用加 GPU）**。智能放置看四个维度：latency · bandwidth · access size · persistence。核心主张：**内存和算力解耦**（≈ 插头论证在硬件层） |
| 17:29 | Samsung 分享 · Inference | **AI Memory Node（三星）**：1U 内存服务器（48 核 x86，最多 6 TB DRAM + CMM-D + SSD），100G 接在 4× B200 GPU 节点旁，作为 **L3.5 层**给 SGLang 扩 KV cache；推理 server 里接 **Cognos** 钩子管理。栈：coding agent → LiteLLM（可观测）→ Gemma4 本地 → SGLang → Cognos。**追问**："production-ready" 没给数字；100G 拉 43 GB 约 3.4 s，未必比 B200 重算快多少，收益应在部分命中 + 释放 GPU 时间 |
| 17:31 | Samsung 分享 · Inference | **Production results**（100 用户并发）：2 GPU + 内存节点 vs 2 GPU：ITL 5.9× / TTFT 3.4× / E2E 3.1×；**4 GPU 无内存节点反而比 2 GPU + 内存节点 ITL 差 1.4×、其余持平** → 一台 1U 内存节点 ≈ 两张 GPU；累计 1→4：ITL 6.9× / TTFT 5.6× / E2E 4.6×，KV 利用率 4.8×（已核算，内部自洽）。ITL 大涨大概是因为避免了抢占 + 重算拖慢 decode。**追问**：没绝对值、没负载细节、没价格对比、对照组是否开了 HiCache |
| 17:33 | Samsung 分享 · Inference | **绝对值（P50）**：TTFT 17.72 → 5.19 / 5.1 / **3.19 s**；E2E 20.3 → 6.6 / 6.88 / **4.45 s**；ITL 290 → 49 / 70 / **42 ms**；KV 命中 20 → 82 / 45 / **96%**；GPU 使用率 98 → 90 / 94 / **83%**。所有倍数用绝对值核过都对。**基线是严重超载**（TTFT 17.7 s）→ 收益是"从不可用到可用"。GPU 98% 忙却多在重算 → **GPU 利用率会骗人，看命中率和有用 token**。仍缺 P99 和价格 |
| 17:41 | Samsung 分享 · Inference | **Choosing a deployment**：先看负载，用**最小**的共享范围。单 server 多租户 → prefix caching + CPU offload；单机多 server → 节点内池（LMCache）；多 GPU、前缀重复 → 共享池 + cache-aware routing；超长 prompt → prefill / decode 分离 + 共享 KV 层。**先测 cache 命中率，它告诉你需要哪一步**（≈ 最小权限原则 + 先度量再修） |
| 17:42 | Samsung 分享 · Inference | **Deployment types**（内存离 GPU 越来越远、被越多 GPU 共享）：① 单 server 单 app（全在显存）② 多 app 共享本机内存 ③ 解耦内存（内存盒在 GPU server 外，= 三星 AI Memory Node）④ prefill / decode 拆分（cache 从 P 搬到 D）⑤ 一个内存盒供几台 server ⑥ 集群（每个 GPU 能访问所有内存盒）。**决定哪份 cache 放哪的是软件：LMCache、Mooncake、HiCache** |
| 17:44 | Samsung 分享 · Takeaways | **四条**：① 内存限制每张 GPU 的用户数（先于算力耗尽 → 用户等、token 贵）② 软件让内存可扩展（LMCache / Mooncake / HiCache / Dynamo）③ 可组合内存加容量不加 GPU（三星：一半 GPU 延迟持平或更好；**放置仍是开放问题**）④ 部署配合负载（先单 server + offload，共享需求变大再加池 / 解耦 / 集群） |
| 18:21 | deck p.59 · Act IV Quiz 4 | **弃用 ≠ 移除**：sampling 2026-07-28 被弃用，最早移除是 **2027-07-28 当天或之后**的第一个修订（12 个月时钟）；2027-03-30 只是提案。*"A deprecation clock turns 'it might change under me' into a date you can put in a project plan."* 计划里用移除下限，不用提案日期 |
| 18:23 | deck p.61 · Act V | **A courtship, then a pin**：7 月前连接要先 `initialize` / `initialized` 握手，HTTP 下再发 `Mcp-Session-Id`，之后每个请求都得回到同一台 server。桌面子进程无害，负载均衡后的集群是一笔税。**Ledger 第 2 条：stateless server 是运维早就会跑的基础设施**。对照推理：MCP 去掉便宜的状态；推理保留昂贵的 KV cache，但用"软 pin"（cache-aware routing），正确性不依赖它 |
| 18:37 | deck p.63 · Act V | **Fielding 2000（REST）**：无状态带来**可见性、可靠性、可扩展性**；代价是**重复**——每个请求带上 server 不再记得的东西。web 付了这个代价并赢了，26 年后 MCP 做了同样的交换。对照推理：重复的代价是重算 prefill（太贵）→ 推理保留状态；但 LLM API 对客户端仍是无状态的，状态藏在服务端 prefix cache 里 |
| 18:39 | deck p.64 · Act V | **2026-07-28 修订逐项**：无握手（版本和能力放每个请求的 `_meta`）· `server/discover` · 路由头 `Mcp-Method` / `Mcp-Name` · **list 结果带 `ttlMs` / `cacheScope`** · 问用户 = 返回 `input_required` 再发同一调用 · Tasks 挪到扩展。**每个请求都能被任何副本、任何 gateway 单独理解**。连线："再发同一调用" → 写操作必须幂等；可缓存的工具列表 → 推理侧 prefix cache 能命中 |
| 18:43 | deck p.65 · Act V | **Not abolished: relocated**：以前一台 server 的 session 装着"你是谁 / 能做什么 / 做了一半的 / 下一步告诉你什么"；现在拆到 client（对话）· `_meta`（版本和能力）· `requestState`（暂停的工作，不透明）· handles and stores（跨调用身份）· tool（什么都不装）。**问题从来不是有没有状态，而是状态是谁的问题——谁需要，谁显式拿着** |
| 18:47 | deck p.66 · Act V | **Published on a day, adopted over seasons**（截至 2026 年 10 月中）：Claude Code 是（HTTP 2.1.274 起，stdio 默认 2.1.292 起）· AWS AgentCore Gateway 是（opt-in）· Hermes 0.22.2 只在 `protocol: stateless` 下、且没有 MRTR · Inspector 2.11.0 是但默认 legacy · Codex 在 flag 后默认关 · Gemini CLI 否（1.x SDK）· 官方参考 server 只会握手。**引用这张表必须标日期** |
| 18:47 | deck p.67 · Act V | **Kill a replica; nobody should notice**（验收测试）：两个副本在负载均衡后，对话中途杀一个，下一个请求落到另一个上继续。前提：client 真说 stateless 协议；**两个副本要有相同的 server name 和 state key**。写操作中途被切 → Hermes 返回 `outcome_uncertain` → **idempotency key 回答它**。Act V（无状态）和 Door 12（幂等）在这页合流 |
| 18:50 | deck p.68–69 · Quiz 5 | **The 404 before the kill**：Hermes 默认 `auto` 先走旧握手 → 副本 1 发了 session → 负载均衡把下一个请求发给副本 2，它没见过这个 session → 404。**一行修法：`protocol: stateless`，没有 session 就没有可丢的**。*"A stateless server cannot save a client that insists on a conversation."*（✅ 和预答一致） |
| 18:52 | deck p.71 · Act VI | **Sampling：借调用方大脑的工具**。server 向宿主的模型要补全（不需要自己的模型和 key），宿主能看到并否决每条 prompt；但它需要调用中途回到 client 的通道 → 已弃用，需要模型的 server 现在直接调模型。**失去的是宿主对工具 prompt 的可见性，监督搬到 gateway 和审计日志**。Ledger 第 5 条：弃用走 12 个月时钟，必须有人盯着 |
| 18:54 | deck p.72 · Act VI | **Deprecated, removed, reborn**：Roots 弃用（范围属于参数、配置和 sandbox）· Logging 弃用、`logging/setLevel` 删除（遥测归遥测）· `ping` 直接删除（无状态请求不需要心跳）· **Elicitation 还活着**（改用多轮请求投递，不再推送）。每条都是"这件事本来就不该由 session 管" |
| 18:54 | deck p.74 · Act VI | **Deprecated is not dead**：时钟走完前，弃用特性仍是规范的一部分，但新工作别用。**FastMCP 4 用了更重的动词**：`ctx.sample()`、`ctx.list_roots()` 在所有协议版本下都删了（规范说弃用，库说删除 → 能不能用看库）。用词：说"elicitation 还在，没了的是推送"，别说"elicitation 被砍了" |
| 18:55 | deck p.78 · Act VII | **A registry of names, not of behavior**：官方 MCP Registry 只存元数据（每 server 一个 `server.json`，反向 DNS 命名，绑定验证过的 GitHub 账号或域名），marketplace 从它拉再加筛选；还在预览（`/v0.1/`）。**registry 担保谁发布，从不担保 server 做什么** → 按内容钉。Ledger 第 4 条：数字上董事会 slide 前必须带单位 |
| 18:56 | deck p.79 · Act VII | **Every count has a unit**：约 44,000 是官方 registry 的**条目**（10/15 自查）；124,267 是 17 个 marketplace 的**去重 server**（MCPacific）。抽 400 个 npm stdio server：**48.8% 完成握手、37.5% 根本没启动**（中间 13.7% 未标注，我倒算的）；8,900 个多版本 server 中 40.6% 悄悄改了能力。**条目不是 server，上架不等于能用，名字不承诺明天的工具** |
| 18:59 | deck p.80 · Act VII | **Numbers with their owners**："Tier-1 SDK 月下载量近 5 亿"（维护者 7 月、AAIF 9 月）——下载量被 CI 放大，不等于用户；"ChatGPT 用户的 MCP 工具调用 8 月是 1 月的 98 倍"——AAIF 原话，没给方法。**每次都说出来源和单位，数字才配上 slide**。#73 正式版：单位 + 主人 + 日期，倍数要带基数和方法 |
| 19:08 | deck · Interlude | **Decay runs from the frontier inward**（同心圆）：前沿（sampling、roots、session）几周内就被弃用或删除 → 中间（传输、授权流程）每个修订重建、按计划更新 → **核心（契约：幂等、礼貌规则、干净的核心）老到无聊、被证明是对的**。原理比它生出的表层活得久：表层松着拿、定期更新，原理抓牢。笔记分三档：核心进 kit、中间标协议版本、前沿标日期 |
| 19:09 | deck p.87 · Interlude | **两条遗忘曲线**：艾宾浩斯 = 事实从脑子里淡去，复习能找回；变化快的领域还有**第二种衰减：事实本身在烂，哪怕你记得一字不差**。重读笔记治第一种，只有重读世界（原始来源）治第二种。*"Teach surfaces as perishables, dated. Teach principles as the pension."* |
| 19:13 | deck p.90 · Act VIII | **The Grid：两个独立问题**。纵轴"模型看见什么"：mounted（全部定义）/ deferred（先给名字，搜索时给定义，如 `defer_loading`、Claude Code `alwaysLoad: false`）/ searched（目录藏在元工具后，如 **Hermes 默认三个 bridge 工具**、PayPal SCOUT）。横轴"怎么调用"：direct / code（写程序调）/ bash（读 `--help`，在协议之外）。**夏天的梯子只是 3×3 网格里的一条路**。⚠️ 修正：Hermes 默认是 searched，不是 deferred |
| 19:21 | deck · Act VIII | **Is bash all you need?**（arXiv `2609.11999`，MS + CMU，TheAgentCompany 任务完成率，作者自建 60 个 typed 工具）：typed tools 44.9% / 45.3% · **bash alone 69.4% / 67.1%** · programmatic tool calling 52.9% / 45.1%（Opus-4.8 / GPT-5.5）。bash 上再加 typed tools 没有可检测的提升。局限：一个 benchmark、自建目录。取舍：**有副作用的动作用 typed（可审计、可幂等），探索性工作给 sandbox 里的 bash** |
| 19:25 | deck p.95 · Act VIII | **辩论收敛**：Cloudflare `cf` CLI（9/28）"上周 agent 使用占 Wrangler 使用量的 48%"、"Agents love CLIs"；Armin Ronacher（10/6）"codemode 本质上是在某种语言里发起工具调用"、"bash 只能组合能跑起来的程序"。**问题不是"MCP 还是 CLI"，而是模型看见多少工具、直接调还是通过代码调**（= p.90 两条轴） |
| 19:27 | deck p.99 · Act IX | **Access and procedure**：Anthropic 的一句话测试（2025-12）——解释怎么做 = skill，需要访问某样东西 = MCP。多对多：一个 skill 用多个 server，一个 server 服务多个 skill。**MCP 给访问权，skill 给做法**。Ledger 第 1 条新问题：server 现在能连同访问权一起发做法（`skills/list`）——**谁来审这个做法？** |
| 19:28 | deck p.100 · Act IX | **Composition runs both ways**：skill → server（W3–W4：skill 点名并调用工具）；server → skill（9 月起 SEP-2640：server 把 SKILL.md 当 resource 发出来）。SEP-2640 自己的例子就是退款 skill `skill://acme/billing/refunds/SKILL.md`。**Stranger's Toolbox 现在可以把店规和工具一起发** → 门里写进 description 的店规本该是一个 skill |
| 19:34 | deck p.102 · Act IX | **A manifest before a single file**：每条 `skills/list` 带 frontmatter 原文 + 每个文件的 URI、SHA-256 和大小；上限每 skill 512 个 resource、16 MiB；宿主**不用下载就能估算和审批**。但 *"Digests are unsigned … A match proves the two are consistent, not that either is trustworthy."* → 摘要证明一致（完整性），不证明可信（真实性）。用法：把审过的 SHA-256 记进 allowlist，变了就重审 |
| 19:37 | deck p.103 · Act IX | **The harness still disposes**：通过 `resources/read` 读到 SKILL.md **不等于启用**——读只是传输。审批按 skill 逐个进行，启用嵌套 skill 要重新同意。*"Harness assembles, model proposes, harness disposes: Week 3's loop, written into a protocol."* 信任不沿引用自动传递 |
| 19:37 | deck · Act X | **One case per box（2026 判例）**：gateway = LiteLLM CVE-2026-59822（失败的 key 检查退回成空身份）· auth = 官方 SDK 的 OAuth client（规范新 MUST 几周没人强制）· harness = ChainDrop 蠕虫（通过项目级 agent 设置持久化）· registry = Plugin4Shell、Deadbugz（钉了没人查；server 变坏）。**去年教威胁模型，今年教判例**。共同点：盒子在该拦的地方放行（fail open） |
| 19:40 | deck p.113 · Act X | **A server that turned**：审过的 server 可以在第三次调用时变坏。Deadbugz（Pillar Security，2026-08）：74 分钟 23 个 PR，17 个加了一个远程 MCP endpoint，三次调用后切换成窃取凭证的指令；一个都没合并。*"Approved on Monday is not the same server on Tuesday. Pin, and watch for change."* → 钉住 + 每次调用比对；远程 endpoint 当高风险变更审 |
| 19:43 | deck p.114 · Act X | **两份要知道的标准**：CoSAI MCP Security v2.0（2026-08-12）四个保证级别 L1 Sandbox / L2 Internal / L3 Production / L4 Regulated；OWASP LLM Top 10 2026：Excessive Agency 从第 6 升到第 3；新增 LLM08 Hidden Context Exposure，明确包括**暴露给模型的工具 schema**。*"Your schema is a prompt, and also an exposure."* |
| 19:47 | deck p.116 · Quiz 10 | **哪个盒子失守**：LiteLLM → gateway；Plugin4Shell → registry 和 harness 一起（钉在市场里，缺的检查在 harness 里）；ChainDrop → harness。**每个盒子都存在，每个都在该强制的那个点放行了**。*"The architecture carries trust, and it fails like any other code. Test the boxes, not just the tools."* → 每个盒子写一个负面测试 |
| 19:53 | deck p.118 · Act XI | **决策路径五问（按顺序）**：① 到底要不要做成工具？（或围墙内用 CLI；契约要靠挣）② 自建、借用、包一层？（通用 server 已有；**只自建你的差异化部分**）③ 怎么让模型接触？（两条轴）④ 谁拿状态？（client、handles、`requestState`，**永远不是工具**）⑤ 谁来强制？（registry、gateway、harness、sandbox；**没有盒子就只是愿望**）。和讲义的上线前五问是前后两步 |
| 19:56 | deck · Act XI | **成熟度五阶段（stateless 版）**：0 能跑（demo 停在这）→ 1 看得懂（schema 诚实、label 当 prompt、hint 如实）→ 2 有礼貌（返回有边界、label 赢搜索）→ 3 安全（重试幂等、有授权 / 审计 / 闸门）→ 4 是基础设施（stateless、在 gateway 后、钉住、被观测；测试 = 杀副本没人察觉）。**十二扇门在 1–3 之间**。⚠️ 和讲义版不同，以 deck 为准 |
| 19:58 | deck p.120–122 · Act XI / Coda | **Rebuild the map**：不看回头复述——门 1 → whether → description → 审批闸门；门 4/6 → how → schema → server 校验；门 8 → what next → error → server 的工具；门 12 → retry → idempotency key → harness 重试规则；门 10 → label 管不了 → 结果是数据 → 最小权限。**Coda：Back to Beck，the label is the map**——地图帮陌生人做决定，但不会让火车停下；label 请求，盒子强制 |

## 2. 动手做到哪了（Stranger's Toolbox，模型 `gemini-3.8-flash`）

| 门 | 基线 | 最终 | 改的面 | 教训 |
| --- | --- | --- | --- | --- |
| 1 Two Doors | 6/12 | **12/12** | description（积分 = 默认） | 缺的是**默认值**：顾客没表态时选哪扇门 |
| 2 Which Thursday? | 6/12 | **12/12** | schema + error + 放出 `delivery_windows` + description | 格式写进 schema；窗口外的请求正确答案是**问顾客**，不是乱试 |
| 3 The Twins | 5/12 | **12/12** | 两个双胞胎的 description + 参数说明 | 不是描述太短，是**没画边界**；每个描述点名邻居 |
| 4 Swiss Knife | 0（8 次盲猜全错） | **12/12** | 工具组成（拆 god-tool）+ description | 拆开后 schema 自己说明怎么调；再写清"做完这步就停" |
| 5–12 | — | — | — | 未做 |
| 13 Turncoat | — | — | — | 未做（15:20 已开） |

## 3. 我自己串起来的几条

1. **四种修法，从轻到重**：写清 description → 收紧 schema → 让 error 指路 → 改工具组成（拆 / 藏 / 放出）。门 1、3 第一种就够；门 2 四种全用；门 4 必须第四种
2. **"做多了"和"做少了"一样是 bug**：门 2（乱试时段）、门 4（取消后又退卡）——描述要写**在哪停**
3. **label 说得不够 vs. 说得太多**：门 1–9 是不够；门 11 是太多（mirage）。前者靠补，后者靠删 + 让返回值说实话
4. **room 的 12/12 ≠ Hermes 的 12/12**：DocsChisel 说描述效果随模型翻转，换模型要重测（每扇门第 5 步 Serve 的意义）
5. **label 治认知不确定，盒子治偶然不确定**——门 12 Paid Twice 和门 10 Helpful Stranger 会证明这一点
6. **（17:12–17:44 三星推理分享）agent 让推理变成有状态的**：KV cache 先于算力耗尽 → 要让 cache 留下、放对层、能共享。三句带走：**GPU 利用率会骗人**（看命中率）· **稳定前缀就是钱**（工具列表逐字节不变）· **先测命中率，再选最小共享范围**。和 Toolcraft 同构：放置 hint = 给推理层的 label；chunk ID ≈ idempotency key

## 4. 课后待办（从今天的课里冒出来的）

- [ ] 门 1：给 `refund_transaction` 也补"$15、只在顾客明确要求时用、别对顾客提"
- [ ] 门 3：试"少给选择"那条路——只暴露 `lookup_orders`，和现在的修法比 token 与稳定性
- [ ] 门 1–4 在 Hermes 实际用的模型上各补一次 Verify
- [ ] 门 5–13 跑完；门 5 记 tool search off / on 两次
- [ ] 读 DocsChisel（`2608.10037`）、capability mirage（`2608.04719`）
- [ ] FinePrint `request_return`：补前置条件和后置条件（WWW H 对照表在 notes §0）
- [ ] FinePrint 杀副本实验：两副本 + LB，共享 server name 和 `requestState` 签名密钥（环境变量），Claude Code ≥ 2.1.292 跑对话中途 kill；`request_return` 用同一 key 重试
- [ ] 门的课后实验：把门 1–4 写进 description 的店规抽成 `refunds` SKILL.md，比较两种做法的 Verify 分数
- [ ] 门 12 提交：schema 加必填 `idempotency_key` + description 写重试契约
- [ ] 推理分享 Q&A 结果补进 notes §14.20（Cognos / CXL / RDMA / P99 / 价格）
- [ ] 查 SGLang HiCache 默认是否开启；Mooncake 现在接了哪些引擎
- [ ] 每周开课前：挑上周笔记里标了日期的条目，回原始来源复核（不只重读笔记）

## 5. 还没讲到的（今晚）

~~Act IV 协议传记~~（18:21 讲到 Quiz 4）· ~~Act V stateless turn~~（18:23–18:50 已讲）· ~~Act VI~~（18:52–18:54）· Act VII（18:55 进行中）· ~~Act VIII 两条轴~~（19:13–19:25）· Act IX（19:27 进行中）· ~~Act X~~（19:37 进行中） · ~~Act XI~~（19:53 进行中） · 19:15 作业
