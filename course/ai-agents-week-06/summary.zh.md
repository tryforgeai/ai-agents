# Week 06 学习总结（2026-10-25 课 · 课后版）

> **课后版 · 截至 19:58**。已整合：上午 + 下午的 Toolcraft（门的揭晓 p.28–44）、17:12–17:44 三星推理分享、今晚 Act IV–XI 与 Coda（p.59–122）。p.123–130（WHY / WHAT / HOW、阅读、下周预告）和作业没有截图，未记录。
> 逐条细节：[notes.zh.md](notes.zh.md)（§0 板书、§3 门的揭晓、§4–§10 今晚各 Act、§14 推理分享）· 课中时间线：[learned-so-far.zh.md](learned-so-far.zh.md) · 门的记录：[lab-log.zh.md](lab-log.zh.md) · 截图：`uploads/`

## 一句话

**label 就是 prompt，模型只读 label；label 只能请求，盒子才能强制。** 下午的推理分享把同一句话推到了基础设施层：**应用给推理层的放置提示也是一种 label，推理层只能根据被告知的信息做决定。**

---

## 1. Toolcraft：今天学到的核心

### 1.1 label 的四站（+ 第五面）

| 站 | 决定 | 写什么 |
| --- | --- | --- |
| **description** | 调不调（whether） | 何时用 / 何时不用 / 代价（hammer's rule） |
| **schema** | 怎么调（how） | 格式、取值范围、必填；**对选择影响最大**（`2610.14334`：参数 schema 3.82 vs server 名 1.48） |
| **error** | 失败后下一步（what next） | **点名房间里存在的工具**，别指向终端 / 网页 |
| **contract** | 重试会怎样（what a retry does） | idempotency key；重试是否安全 |
| 返回值（第五面） | 下一步决策用什么 | 礼貌规则：只返回下一步需要的，为有预算的读者塑形 |

### 1.2 WWW H 骨架（板书 11:44）

**What / When / When Not / How / Why**。When Not 分**范围**（别的活不干）和**前置条件**；How 里的数值约束推进 schema；Why = **后置条件**（调用后什么为真）。

### 1.3 两种不确定（板书 12:00）

- **认知不确定**（模型缺信息）→ 写好 label 能消除
- **偶然不确定**（超时、执行了但回复丢了）→ label 治不了，靠**契约和盒子**：idempotency key、重试规则

### 1.4 门的揭晓（deck p.30–44）

| 门 | 教训 | 关键数字 / 原话 |
| --- | --- | --- |
| 1 Two Doors | **Say what the store wants**：两边都写——积分"首选、免费、先提"，退卡"金额 + $15、只在顾客要钱时用" | *"Nothing changed but the words, and the words were the program."* |
| 3 The Twins | **Nothing like leather**：两个工具都说能解决 → 模型随机挑；能少给选择就少给，非给不可由 label 裁决 | — |
| 4 Swiss Knife | schema 对选择影响最大 | `2610.14334` |
| 8 Polite Error | **Errors point out of the room → Name the door** | 150 个 server 的 3,001 条错误只有 949 条说下一步；凭证错误 62/67 指向工具接口外；改写后恢复率 **84% / 88%**（原来 GPT-6 Astra 6%） |
| 11 The Mirage | **没有通用的好描述**（DocsChisel：17 字段中 12 个效果随模型翻转）；**capability mirage**：夸大的 label 是模型会信的谎（8 模型易感性差 36×） | 用**读它的模型**测 label |
| 12 Paid Twice | **error ≠ 没执行**；契约 refund(k)∘refund(k) = refund(k)；同一调用到达两次有三条路（协议重发 / Hermes 传输失败 / Claude Code 2.1.287 线上 bug） | *"A retry should ask 'did it happen?', not place a second order."* |

### 1.5 我课上想通的几点

- **超时 ≠ 失败**：网关的事务已提交，丢的只是回复；跨系统没有共享事务（2PC 也有 in-doubt 状态），所以支付行业的标准答案是 **idempotency key**（Stripe 的 `Idempotency-Key` 同理）。**事务管"一个系统内别做一半"，幂等 key 管"跨系统同一件事只做一次"**
- **key 由调用方生成**（只有它知道是不是同一个意图），重试复用、新意图才换；server 存的是**结果**，不只是"见过"
- **`readOnlyHint` 标错的代价不对称**：漏标只少一次自动重放；错标写工具 → Hermes 自动重放 → 钱动两次
- **四种修法从轻到重**：description → schema → error → 改工具组成（拆 / 藏 / 放出）
- **"做多了"和"做少了"一样是 bug**：描述要写**在哪停**
- **room 的 12/12 ≠ Hermes 的 12/12**：换模型要重测

---

## 2. 动手：Stranger's Toolbox（模型 `gemini-3.8-flash`）

| 门 | 基线 | 最终 | 改的面 | 教训 |
| --- | --- | --- | --- | --- |
| 1 Two Doors | 6/12 | **12/12** | description | 缺的是**默认值** |
| 2 Which Thursday? | 6/12 | **12/12** | schema + error + 放出 `delivery_windows` + description | 格式进 schema；窗口外该**问顾客** |
| 3 The Twins | 5/12 | **12/12** | 两个 description + 参数说明 | 每个描述点名邻居 |
| 4 Swiss Knife | 8 次盲猜全错 | **12/12** | 拆 god-tool + description | 拆开后 schema 自己说明；写清"做完就停" |
| 12 Paid Twice | 已开 | 未提交 | — | 方向：schema 加必填 `idempotency_key`，description 写"超时后用同一 key 重试不会重复退款" |
| 5–11、13 | — | 未做 | — | — |

---

## 3. 推理分享（17:12–17:44，三星）：agent 让推理变成有状态的

### 3.1 主线

agent 的工作负载让推理**有状态** → 状态（KV cache）住在内存里 → **内存先于算力耗尽** → 解法是让 cache **留下来、放对层、能共享** → 放哪仍是开放问题，要靠**应用告诉推理层**。

### 3.2 关键概念

| 概念 | 一句话 |
| --- | --- |
| **Prefill / Decode / KV cache** | prefill 读 prompt（算力瓶颈）；decode 逐 token 写（显存带宽瓶颈）；KV cache = 每 token 的笔记，随用户和 token 增长 |
| **数量级** | Llama 3.1 70B FP16：0.33 MB/token；128K 对话 43 GB；5 个对话 215 GB > 权重 140 GB（已核算：80 层 × 8 KV head × 128 dim） |
| **三种负载形状** | 一次性长上下文（容量）· 多轮对话（保留）· agent 循环（放置：大共享前缀 + 长空闲） |
| **放不下时** | 排队 / 驱逐再重算（128K 约 6 s prefill）/ 加卡（只为显存）/ **offload** 到 CPU 内存或池 |
| **按"多久后再用"放层** | 秒→HBM · 分钟→Host DRAM · 小时→Pooled · 天→Local SSD；太早驱逐伤 TTFT，留太久烧 HBM |
| **每 token 成本** | = 每小时服务器成本（固定）÷ 每小时**有用** token；重算、批次变小、为显存买卡都让分母变小 |
| **多租户三招** | continuous batching · paged KV cache · prefix sharing——**都依赖 block 留在显存** |
| **vLLM** | PagedAttention + prefix caching（LRU 驱逐）；扩展点 **KV connector** → LMCache / Mooncake |
| **SGLang** | 前缀存成树（**RadixAttention**），**HiCache** 把树延伸到 CPU 内存和存储 |
| **NVIDIA Dynamo** | 跨 server 编排：KV-aware routing · Planner · prefill/decode 分离（NIXL 搬 cache）· KV Block Manager |
| **LMCache + Mooncake** | 单机共享 + 跨机内存池；**chunk ID 由 token 算出 → 任何 instance 都能对上**（内容寻址） |
| **RDMA** | 网卡直接读写远端内存，不经内核、不打扰对方 CPU；µs 级延迟、100–400 Gb/s → 跨机共享 cache 才划算 |
| **内存金字塔** | L0 SRAM → L1 HBM → L2 DRAM → L3 SSD → L4 存储服务器；AI 时代新增 **X.5 层**（3D DRAM、光互连 HBM、CXL 内存、以太网内存池）补断崖 |
| **Composable memory** | pooled + tiered + attachable；放置看 latency · bandwidth · access size · persistence；核心主张 = **内存和算力解耦** |
| **三星 AI Memory Node** | 1U、最多 6 TB（DRAM + CMM-D + SSD），100G 接 B200 节点，作 L3.5 层给 SGLang 扩 cache；Cognos 钩子管理 |

### 3.3 三星的实测（P50，100 并发，已逐项核算）

| Stage | 配置 | TTFT | E2E | ITL | KV 命中 | GPU 使用 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2× B200 | 17.72 s | 20.3 s | 290 ms | 20% | 98% |
| 2 | 2× B200 + 内存节点 | 5.19 s | 6.6 s | 49 ms | 82% | 90% |
| 3 | 4× B200 | 5.1 s | 6.88 s | 70 ms | 45% | 94% |
| 4 | 4× B200 + 内存节点 | 3.19 s | 4.45 s | 42 ms | 96% | 83% |

- **一台内存节点 ≈ 两张 GPU**（Stage 2 ≥ Stage 3）
- **基线严重超载**（TTFT 17.7 s）→ 收益是"从不可用到可用"
- **GPU 98% 忙却多在重算** → GPU 利用率会骗人
- 仍缺：P99、负载细节、价格对比、对照组是否开了 HiCache；Cognos 无公开资料（别和 IBM Cognos 混）

### 3.4 部署选型（"先测命中率，再选最小共享范围"）

| 场景 | 方案 |
| --- | --- |
| 一台 server、多租户 | prefix caching → CPU offload |
| 一台机器跑几个 server | 节点内池（LMCache） |
| 多 GPU、前缀重复 | 共享池 + cache-aware routing |
| 超长 prompt | prefill / decode 分离 + 共享 KV 层 |

### 3.5 讲者的四条 takeaways

1. 内存限制每张 GPU 的用户数 2. 软件让内存可扩展 3. 可组合内存加容量不加 GPU（**放置仍是开放问题**）4. 部署配合负载

---

## 3½. 今晚 Toolcraft：Act IV–XI 与 Coda（18:21–19:58）

### Act IV · 协议传记（Quiz 4）

- **弃用 ≠ 移除**：sampling 2026-07-28 被弃用，最早移除是 **2027-07-28 当天或之后**的第一个修订（12 个月时钟）；2027-03-30 只是提案
- *"A deprecation clock turns 'it might change under me' into a date you can put in a project plan."* → 计划里用**移除下限**，不用提案日期

### Act V · The Stateless Turn

| 页 | 要点 |
| --- | --- |
| p.61 求爱再钉住 | 旧协议：`initialize` / `initialized` 握手 + `Mcp-Session-Id`，之后每个请求必须回到同一台 server。桌面无害，集群是一笔税 |
| p.63 Fielding 2000 | 无状态带来**可见性、可靠性、可扩展性**，代价是**重复**（每个请求带上 server 不记得的东西） |
| p.64 新版逐项 | 无握手（`_meta` 带版本和能力）· `server/discover` · 路由头 `Mcp-Method` / `Mcp-Name` · **list 结果**带 `ttlMs` / `cacheScope` · 问用户 = 返回 `input_required` 再发同一调用 · Tasks 挪到扩展 |
| p.65 不是废除是搬家 | session 里的东西拆到：client（对话）· `_meta`（版本和能力）· `requestState`（暂停的工作，不透明）· handles / stores（身份）· tool（什么都不装）。**问题不是有没有状态，而是状态是谁的问题——谁需要谁显式拿着** |
| p.66 采用表（10 月中） | Claude Code 是（HTTP 2.1.274 / stdio 默认 2.1.292）· AWS AgentCore Gateway opt-in · Hermes 0.22.2 只在 `protocol: stateless` 下且**没有 MRTR** · Inspector 默认 legacy · Codex flag · Gemini CLI 否 · 官方参考 server 只会握手。**引用必须标日期** |
| p.67 验收测试 | **杀一个副本，没人察觉**。前提：client 真说新协议；两副本**同 server name、同 state key**；写操作中途被切 → `outcome_uncertain` → **idempotency key 回答它**（Act V 和 Door 12 合流） |
| p.68–69 Quiz 5 | 没杀就 404：Hermes 默认 `auto` 先走旧握手 → session 只在副本 1 → 请求落到副本 2 → 404。一行修法 `protocol: stateless`。*"A stateless server cannot save a client that insists on a conversation."* |

### Act VI · What Grows Back

| 什么 | 状态 | 归哪 |
| --- | --- | --- |
| **Sampling**（server 借宿主的模型） | 弃用 | server 直接调模型；失去的"宿主看得见工具 prompt"→ **监督搬到 gateway 和审计日志** |
| Roots | 弃用 | 范围放进**参数、配置和 sandbox** |
| Logging | 弃用；`logging/setLevel` 删除 | 遥测归遥测 |
| `ping` | 删除 | 无状态不需要心跳 |
| **Elicitation** | **还活着** | 改用多轮请求投递，不再推送 |

- **Deprecated is not dead**：时钟走完前仍是规范一部分，但新工作别用；**FastMCP 4 直接删了 `ctx.sample()` / `ctx.list_roots()`**（规范说弃用，库说删除——能不能用看库）
- 用词：说"**elicitation 还在，没了的是推送**"，别说"elicitation 被砍了"
- Ledger 第 5 条：弃用走 12 个月时钟，**必须有人盯着**

### Act VII · The Bazaar and the Ledger

- **Registry 是名字的登记，不是行为的登记**：官方 MCP Registry 每 server 一个 `server.json`，反向 DNS 命名，绑定验证过的 GitHub / 域名；仍是预览（`/v0.1/`）。**担保谁发布，从不担保做什么**
- **每个数字都有单位**：约 44,000 是 registry **条目**（10/15 自查）；124,267 是 17 个市场的**去重 server**（MCPacific）；抽 400 个 npm stdio server，**48.8% 完成握手、37.5% 根本没启动**；8,900 个多版本 server 中 **40.6%** 悄悄改了能力
- **数字要带主人**："月下载近 5 亿"（维护者 / AAIF）——下载含 CI，不是用户；"工具调用 98 倍"——AAIF 原话，没给方法
- *"Entries are not servers, listings are not working servers, and a name is not a promise about tomorrow's tools."*
- 主旨：**集市可以逛，账要自己记**——信任不能从 registry 或大数字里来，要靠 allowlist + 按内容钉 + 定期复核

### Interlude · 深度的半衰期

- **衰减从前沿向内**：前沿（sampling、roots、session）几周内弃用 → 中间（传输、授权）每个修订重建 → **核心（契约：幂等、礼貌规则、干净核心）老到无聊、被证明是对的**
- **两条遗忘曲线**：① 我忘了 → 重读笔记；② **事实本身烂了**（记得一字不差也没用）→ 只有回原始来源才能治
- *"Teach surfaces as perishables, dated. Teach principles as the pension."*
- **笔记三档**：核心进 kit（不标日期）· 中间标协议版本 · 前沿标日期并定期回源复核

### Act VIII · 两条轴，不是梯子

- **3×3 网格**：看见什么（mounted / deferred / searched）× 怎么调用（direct / code / bash）
  - mounted × direct = 扁平工具箱（**我们的 lab**）
  - deferred × direct = `defer_loading` + search；Claude Code `alwaysLoad: false`
  - **searched × direct = Hermes 默认的三个 bridge 工具**；PayPal SCOUT 两个元工具（⚠️ 我课前写成 deferred，已修正）
  - mounted × code = programmatic tool calling（Anthropic Python / OpenAI JS）
  - bash 列 = 在协议之外，模型读 `--help`
- **夏天的梯子只是网格里沿对角线的一条路**（Quiz 8：PayPal = searched × direct；Claude Code = deferred × direct；OpenAI V8 = mounted × code）
- **Is bash all you need?**（arXiv `2609.11999`，MS + CMU，TheAgentCompany 任务完成率）：typed tools 44.9% / 45.3% · **bash 69.4% / 67.1%** · programmatic 52.9% / 45.1%（Opus-4.8 / GPT-5.5）。局限：一个 benchmark、作者自建 60 个工具。原因未证明（模型熟 shell？可组合？自建 label 差？）
- **typed tools** = 有名字、description、JSON schema 的工具（MCP、function calling）；输出结构化参数，可校验、可 allowlist、可强制幂等 key
- **取舍**：有副作用（钱、客户数据）→ typed，可审计可幂等；探索性（查数据、翻日志）→ sandbox 里的 bash
- **辩论收敛**（p.95）：Cloudflare `cf`"agent 占 Wrangler 使用量 48%"；Ronacher"codemode 只是在某种语言里发工具调用，bash 只能组合能跑起来的程序"。**问题不是 MCP 还是 CLI，而是模型看见多少工具、直接调还是通过代码调**

### Act IX · Procedure 走线上

- **Access vs procedure**（Anthropic 2025-12 一句话测试）：解释怎么做 = **skill**；需要访问某样东西 = **MCP**。多对多
- **Composition runs both ways**：skill → server（W3–W4）；**server → skill**（SEP-2640，9 月起：`skills/list` / `skills/get`，SKILL.md 当 resource 发）。SEP-2640 的例子就是**退款 skill** → Stranger's Toolbox 可以把店规和工具一起发
- **Manifest 先于文件**：每条 `skills/list` 带 frontmatter 原文 + 每个文件的 URI、SHA-256、大小；上限 512 个 resource、16 MiB；宿主不下载就能估算和审批。但**摘要没签名：对上只证明一致，不证明可信**
- **读到 ≠ 启用**（p.103）：`resources/read` 只是传输；审批按 skill 逐个，嵌套 skill 要重新同意。*"Harness assembles, model proposes, harness disposes"*——W3 的循环写进了协议
- Ledger 第 1 条新问题：server 能连同访问权一起发做法——**谁来审这个做法？**
- 名词区分：tool（单个函数）· MCP server（一组 tool = 访问权）· skill（做法）· ChatGPT app（MCP + 界面）· plugin（打包分发格式，两家含义不同；ChatGPT 7 月起的说法来自第三方博客，待官方核实）

### Act X · When the Boxes Fail Open

- **One case per box（2026 判例）**：gateway = LiteLLM CVE-2026-59822（key 检查失败退回成空身份）· auth = 官方 SDK 的 OAuth client（规范新 MUST 几周没人实现）· harness = ChainDrop 蠕虫（借 `.claude/settings.json` / `.vscode/tasks.json` 持久化）· registry = Plugin4Shell（钉了 SHA 没人验）、Deadbugz
- **A server that turned**（p.113）：Deadbugz（Pillar Security，2026-08）74 分钟 23 个 PR，17 个加了远程 MCP endpoint，**第三次调用后**切换成窃取凭证的指令；一个都没合并。*"Approved on Monday is not the same server on Tuesday. Pin, and watch for change."*
- **两份标准**（p.114）：CoSAI MCP Security v2.0（2026-08-12）四级 L1 Sandbox / L2 Internal / **L3 Production（要中央 gateway）** / L4 Regulated；OWASP LLM Top 10 2026：**Excessive Agency 升到第 3**，新增 **LLM08 Hidden Context Exposure**（包括暴露给模型的工具 schema）。*"Your schema is a prompt, and also an exposure."*
- **Quiz 10**：LiteLLM → gateway；Plugin4Shell → **registry + harness 一起**（钉在市场，缺的检查在 harness）；ChainDrop → harness。*"Each box existed. Each failed open, at the exact point meant to enforce."* → **"Test the boxes, not just the tools"**：每个盒子写一个负面测试
- 名词：CoSAI = Coalition for Secure AI（行业联盟，OASIS Open 托管）；OWASP = Open Worldwide Application Security Project；LiteLLM = 开源 LLM / MCP 网关

### Act XI · The Toolwright's Procedure

- **决策路径五问**（p.118，动手之前）：① 要不要做成工具（或围墙内 CLI；契约要靠挣）② 自建 / 借用 / 包一层（**只建差异化部分**）③ 怎么接触模型（两条轴）④ 谁拿状态（**永远不是工具**）⑤ 谁来强制（**没盒子就是愿望**）
- **成熟度五阶段**（deck 版）：0 能跑 → 1 看得懂 → 2 有礼貌 → 3 安全 → 4 是基础设施（杀副本测试）。**十二扇门在 1–3 之间**
- **Rebuild the map**（p.120）：门 1 → whether → description → 审批闸门 · 门 4/6 → how → schema → server 校验 · 门 8 → what next → error → server 的工具 · 门 12 → retry → idempotency key → harness 重试规则 · 门 10 → label 管不了 → 结果是数据 → 最小权限

### Coda · Back to Beck

- **the label is the map**：Beck 的地铁图只画乘客做决定需要的东西；label 也是画给陌生人做决定的。但**地图不会让火车停下**——label 请求，盒子强制，toolwright 两样都要画
- 一句话：**画好地图让陌生人走对路，装好信号让走错的人停下来**

### Act X · When the Boxes Fail Open（2026 判例，每盒一案）

| 盒子 | 管什么 | 案例 | 怎么失守 |
| --- | --- | --- | --- |
| **gateway** | 流量路径上的策略 | **LiteLLM CVE-2026-59822**（Wiz） | key 检查失败后退回成一个**空的已认证身份**，伪造 token 就能开 session |
| **auth** | 身份、issuer、audience | **官方 SDK 的 OAuth client** | 规范的新 MUST 几周没人强制（issuer 检查、token 发给任意授权服务器） |
| **harness** | agent 被允许做什么 | **ChainDrop** npm 蠕虫（MS Security） | 借 `.claude/settings.json` SessionStart hook、`.vscode/tasks.json` 持久化，打开项目就执行 |
| **registry** | 谁发布、哪个版本 | **Plugin4Shell**；**Deadbugz**（Pillar Security，2026-08） | 钉了 SHA 但 harness 不验 → 同名分支被装；74 分钟 23 个 PR，17 个加了远程 MCP endpoint，**第三次调用后变坏**（没合并） |

- *"Last year we taught threat models. This year we can teach case law, one case per box."*
- *"Approved on Monday is not the same server on Tuesday. Pin, and watch for change."*
- **两份标准**：**CoSAI MCP Security v2.0**（2026-08-12）四级 L1 Sandbox / L2 Internal / **L3 Production（要中央 gateway）** / L4 Regulated；**OWASP LLM Top 10 2026**：Excessive Agency #6 → **#3**，新增 **LLM08 Hidden Context Exposure**（包括暴露给模型的工具 schema）。*"Your schema is a prompt, and also an exposure."*
- **Quiz 10**：LiteLLM → gateway；Plugin4Shell → **registry 和 harness 一起**（钉在市场，缺的检查在 harness，责任落在两盒之间）；ChainDrop → harness。*"Each box existed. Each failed open, at the exact point meant to enforce."* → ***"Test the boxes, not just the tools."***
- **对我们开发 agent 的指导**：先定 CoSAI 级别 → 最小权限（只挂需要的工具、只读标 hint、动钱用 typed + 幂等 + 审计、高风险人工确认）→ schema 只暴露该暴露的（不写内部系统名 / 表名 / 密钥位置；租户 ID 由 server 补）→ 每个盒子写一个**负面测试**（伪造 token 被拒、hook 不自动执行、改工具描述会报警停用）

### Act XI · The Toolwright's Procedure

- **决策路径五问（动手之前，按顺序）**：
  1. **到底要不要做成工具？**还是围墙内用 CLI——契约要靠挣
  2. **自建、借用、包一层？**通用 server 已有——**只自建你的差异化部分**
  3. **怎么让模型接触？**——两条轴
  4. **谁拿状态？**client、handles、`requestState`——**永远不是工具**
  5. **谁来强制？**registry、gateway、harness、sandbox——**没有盒子就只是愿望**
- 和讲义的"上线前五问"（Whether / How / What next / Retry / Box）是**前后两步**：先决定做不做、怎么做，再逐个检查做出来的工具
- **成熟度五阶段（deck 版）**：0 能跑（demo 停在这）→ 1 看得懂 → 2 有礼貌 → 3 安全 → 4 是基础设施（杀副本测试）。**十二扇门在 1–3 之间**
- **Rebuild the map**：门 1 → whether → description → 审批闸门；门 4 / 6 → how → schema → server 校验；门 8 → what next → error → server 的工具；门 12 → retry → idempotency key → harness 重试规则；门 10 → label 管不了 → 结果是数据 → 最小权限

### Coda · Back to Beck

- **the label is the map**：Beck 的地铁图不按地理，只画乘客做决定需要的东西；label 也是画给陌生人做决定的
- **但地图不会让火车停下**：label 请求，盒子强制。toolwright 两样都要画
- **全天一句话**：**写好地图让陌生人走对路，装好信号让走错的人停下来**

### 今晚的一条主线

**身份 / 一致性 ≠ 可信**，今天出现了四次：Act X 的 Plugin4Shell（钉了 SHA 不等于验了）· registry 担保谁发布不担保做什么 · Mooncake chunk ID 证明同一段前缀不证明内容对 · skill 摘要证明一致不证明可信 → 可信要靠**审 + 按内容钉住审过的版本**。

---

## 4. 两段课的接线（今天最值得记的）

| Toolcraft | 推理层 | 同一个道理 |
| --- | --- | --- |
| label 是给模型的 prompt | 放置 hint 是给推理层的 label（`ttlMs` / `cacheScope`、prompt cache TTL、block events） | **执行方只能根据被告知的信息做决定** |
| 门 12 的 idempotency key | Mooncake 的内容寻址 chunk ID | **用稳定身份把"第二次"变成"查第一次"**（key 由意图方生成；chunk ID 由内容算出） |
| Labels request, boxes enforce | 应用 hint 请求，KV manager 强制 | 两边都会 fail open |
| 插头论证 N×M → N+M | KV connector · Dynamo worker 接口 · composable memory | 标准接口让异构组件可组合 |
| 最小权限 / allowlist | 最小共享范围 | 从最小开始，有证据再扩大 |
| 门的 Predict → Verify | 先测命中率再选方案 | 先度量再修 |
| Door 4 盲猜 8 次 | GPU 98% 忙在重算 | **看结果，不看活动量** |
| 礼貌规则 / Firehose | 每个 token 都占 KV cache | token 不只花钱，还占显存、挤小批次 |
| Act VII 按内容钉版本 | 工具列表逐字节稳定才能共享前缀 | **名字会骗人，内容不会** |
| Act V：MCP 刻意去掉状态（重建便宜） | 推理刻意保留 KV cache（重建要 ~6 s），用软 pin（cache-aware routing） | **状态要么便宜到能丢，要么贵到值得管理，正确性都不能依赖它** |
| Fielding：无状态的代价是重复 | 每轮重发上下文 = 重算 prefill，付不起 → LLM API 对客户端无状态，状态藏在服务端 prefix cache | 同一个权衡，因重复成本不同而选相反方向 |
| p.64 list 结果带 `ttlMs` / `cacheScope` | 工具目录稳定 → prompt 前缀稳定 → prefix cache 命中 | 协议层缓存和推理层缓存一起成立或一起失效 |

---

## 5. 候选技巧（编号接 #63，课后确认再写进 kit）

| # | 技巧 | 来源 |
| --- | --- | --- |
| #64 | 改 label 一次只改一个面，用 trace 判断哪个面起作用 | Act II 规则 |
| #65 | 改名 = breaking change：工具名当公共 API | 四个面 |
| #66 | 错误信息写给 agent：**点名房间里存在的工具**（实测恢复率 84% / 88%，**已转正**） | Door 8 · deck p.40–41 |
| #67 | 每个写操作带 idempotency key（调用方生成、重试复用），label 写明重试行为；只读工具标 `readOnlyHint`，写工具**绝不能**标 | Door 12 · p.42–44 |
| #68 | 先写预测再跑，用 held-out prompts 验证（12/12 才算） | 门的五步 |
| #69 | 工具结果当数据不当指令；toolset 组成是防线 | Door 10 / Act X |
| #70 | 按内容钉工具列表并定期校验 | Act VII / Door 13 |
| #71 | 项目级 agent 配置（hooks、tasks.json）当代码审 | ChainDrop |
| #72 | stateless 测试前先确认 client 真在说新协议 | Act V |
| #73 | 引用数字必带**单位、主人、日期**；倍数要带**基数和方法**；下载量 ≠ 用户、条目 ≠ server ≠ 能用的 server | Act VII p.79–80 · 三星 p.43 vs p.44 正反例 |
| **#74** | 描述写"何时用 / 何时不用 / 代价"，**两个竞争工具都要写**，并写"在哪停" | Door 1 / 3 / 4 |
| **#75** | **prompt 布局：不变的放前面，变的放末尾**（system prompt → 工具 → 历史 → 本轮）；工具列表不重排、不插时间戳 → 前缀 cache 可共享 | 推理 14.7 / 14.9 / 14.11 |
| **#76** | 评估自托管推理看**命中率和有用 token / $**，不看 GPU 利用率；按实际负载形状估成本 | 推理 14.5 / 14.16 |
| **#77** | 部署从最小共享范围开始（API prompt cache 或单机 + prefix caching），**先测命中率**再决定是否上池 / 集群 | 推理 14.18 |
| **#78** | 状态显式化：server 进程内存里不存会话状态；身份放参数 / handle，暂停的工作用签名的 `requestState`，多副本共享 server name 和 state key | Act V p.65 / p.67 |
| **#79** | 弃用看两层：规范的移除下限写进计划，但**以库为准**（FastMCP 4 已删 sample / roots）；指定专人盯弃用时钟 | Act IV / VI |
| **#80** | 选调用方式按风险：有副作用 → typed tools（可审计、可幂等）；探索性 → sandbox 里的 bash / code | Act VIII |
| **#81** | 跨工具的政策写成 skill，不塞进 tool description；第三方 skill 审过后把 SHA-256 记进 allowlist，摘要变了就重审 | Act IX p.100 / p.102 |
| **#82** | 笔记分三档：核心进 kit · 中间标协议版本 · 前沿标日期并每周回原始来源复核 | Interlude |
| **#83** | **测盒子，不只测工具**：每个盒子一个负面测试（伪造 token、恶意 hook、改工具描述），上线前跑 | Act X Quiz 10 |
| **#84** | 动手前过决策路径五问；交付时用成熟度阶梯说明"在第几级、下一级差什么" | Act XI |
| **#83** | **测盒子**：上线前每个盒子一个负面测试——伪造 token 要被拒、带 hook 的项目配置不能自动执行、改了工具描述要报警停用 | Act X Quiz 10 |
| **#84** | 部署前先定 CoSAI 级别（客户生产 = L3 → 中央 gateway）；schema 只暴露该暴露的（OWASP LLM08） | Act X p.114 |
| **#85** | 动手前过决策路径五问；交付时用成熟度阶梯说清"在第几级、下一级差什么" | Act XI |

---

## 6. 对我的项目

- **FinePrint MCP**（`capstone/fineprint-mcp/`）
  - `request_return` = Door 1 + Door 12：加必填 `idempotency_key`，docstring 写重试契约；补前置 / 后置条件（WWW H）
  - 查询类工具补 `readOnlyHint: true`；`request_return` 不标
  - `"tell the customer to retry later"` 改成点名工具 + 同一 key 重试
  - 钉 `mcp` 版本（课上统一 `mcp==2.3.0`）；测 stateless + kill-a-replica
  - 工具列表和 docstring 保持稳定，不插动态内容（#75）
  - 不在进程内存里存"正在退哪一单"；多副本共享 server name 和 `requestState` 签名密钥（#78）
  - 拆成 `request_return`（access）+ `returns-policy` skill（procedure）；"确认前预览"改成 `input_required` + 同一 idempotency key 再调
  - 测 stateless 用 Claude Code ≥ 2.1.292 或 Inspector 新模式，别用 Hermes 默认
- **Forge AI 客户部署**
  - Decision Ledger 五条直接当部署检查单
  - 长期挂着的客服 / 流程 agent = "小上下文、长空闲"：走 API 时按会话间隔选 prompt cache TTL；自托管时别让它们一直占 GPU
  - 自托管报价按负载形状和命中率估 $/token（#76）；多数中小客户停在部署选型第 1–2 行即可（#77）

---

## 7. 开放问题 / 待办

**Toolcraft**

- [x] 今晚 Act IV–IX（18:21–19:34）
- [x] Act X、Act XI、Coda（19:37–19:58）
- [ ] p.123–130（WHY / WHAT / HOW、阅读、下周 PromptCraft 预告）和作业：看录播补
- [ ] 门 5–13 跑完（门 5 记 tool search off / on；门 12 提交）
- [ ] 门 1 给 `refund_transaction` 补代价和限制；门 3 试"只暴露 `lookup_orders`"
- [ ] 把门 1–4 的店规抽成 `refunds` SKILL.md，比较两种写法的 Verify 分数
- [ ] 门 5 开 tool search（Hermes searched 模式），看 description 能不能被搜到
- [ ] FinePrint 杀副本实验（两副本 + LB + 共享 state key + Claude Code ≥ 2.1.292）
- [ ] 查规范原文：`cacheScope` 取值；`requestState` 签名机制
- [ ] 门 1–4 在 Hermes 的模型上补 Verify
- [ ] 读 DocsChisel（`2608.10037`）、capability mirage（`2608.04719`）
- [ ] Door 10 该改什么——toolset 组成？由谁决定？
- [ ] Hermes deferred 默认下，description 怎么写才能被搜索找到？

**推理分享**

- [ ] Q&A：Cognos 是否支持 CXL managed memory（聊天区提问）；Cognos 基于什么（自研 / LMCache / Mooncake）；节点间走 RDMA 还是 CXL；P99；内存节点 vs 两张 B200 的价格
- [ ] 查 SGLang HiCache 是否默认开启、RadixAttention 的驱逐策略
- [ ] 去 GitHub `kvcache-ai/Mooncake` 确认现在接了哪些引擎

**承接**

- [ ] 候选技巧 #64–#85 写进 kit
- [ ] Capstone 提案补"Decision Ledger + 五问"


## 追加：10 月 27 日 MCP Guardrails Lab（10 月 29 日补记）

实操细节见 [lab-log](lab-log.zh.md#2026-10-27--mcp-guardrails-lab2026-10-29-补记)。工具投毒可以借 Agent 的文件权限读取内容，再通过天气工具参数外传；本次攻击者日志确认收到实验假密钥。换安全文件服务后，敏感读取被 PermissionError 拦截。secure_agent 的直接读文件请求得到模型拒绝，但这不能证明工具结果脱敏已经执行。

服务端先校验后读取，Agent 则在工具发现时清洗描述、在执行后脱敏结果。模型拒绝、描述清洗、输出脱敏、文件权限检查是不同层；证据应看实际工具调用与服务端结果。教学实现仍有名称黑名单漏项、符号链接边界、结构化字典秘密值漏脱敏等局限，详见实操记录。
