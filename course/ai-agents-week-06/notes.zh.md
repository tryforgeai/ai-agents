# AI Agents Week 06 笔记 — Toolcraft II：插头、门与协议

日期：2026-10-25
来源：lesson plan PDF（27 页，页码为讲义页码）+ 课堂速记
状态：**课前预习版**。每节末尾的「课堂补充」留给上课时填；动手部分记在 [lab-log.zh.md](lab-log.zh.md)。

---

## §0 · A Gentle Re-Entry（p.1–2）—— 上周回顾

上周（W5）走了一条线：搁浅的心脏科医生（专家没有仪器 = 模型没有工具）→ 设备 → 操作系统 → 驱动 → USB → **MCP**；fortune cookie 变成 `@mcp.tool`。

| 上周学到的 | 一句话 |
| --- | --- |
| 工具的四个自述词 | **pure / reentrant / idempotent / stateless** |
| description 是决策边界 | 它决定模型调不调、调哪个 |
| less is more | 工具少、互不相似 |
| 礼貌的工具返回什么 | 下一步决策需要的东西 |
| 上下文腐烂 | 沿着一条生存曲线衰减 |

- **Refund Desk**（上周三轮、一个柜台）被故意留着没讲完——三轮太少、一个柜台太窄。今天它长成 **The Stranger's Toolbox**，Refund Desk 拆成第 1、8、12 扇门。
- ⚠️ 讲义提醒：上周在家玩过的，**再预测一遍再玩**，别假设旧修法仍然成立。

**Say-it-back（11:15）**：label 决定 ① 是否被调用 ② 怎么被调用 ③ 失败后下一步 ④ 重试做什么。

✅ **deck p.5 核对**（12:21）：*"one tool call, four stations, each one a page of the label"* —— description → whether（*call it, or its neighbor?*）· schema → how（*which fields, which shape*）· error → what next（*which door, after a failure*）· **contract** → what a retry does（*once, or twice?*）

> 课堂补充：

### 板书 11:44 · WWW H（OneNote "WWW H"）

![[uploads/1144-wwwh-board.png]]

Asif 用一把**玻璃加工用的锤子**演示一个工具的说明该写哪几块。板书原文（手写转录）：

| 块 | 板书 |
| --- | --- |
| **When**（什么时候用） | *"A hammer for glasswork, to take unnecessary pieces out after etching with a knife or other tool."* <br> *"Do not apply more than X newtons of force."* |
| **When Not**（什么时候不用） | *"Should not be used for anything other than glasswork."* <br> *"Must not be used unless the glass has been etched."* |
| 右栏 | **What** ← · **When** ← · **How** ←（箭头指回左边两栏）<br> **Why: Correctness. POST-CONDITION.** |

我的理解：

- 标题 **WWW H** = What / When / Why + How，一份工具说明（docstring）要回答的四个问题
- **What**：是什么——"玻璃加工用的锤子"
- **When**：用途和时机——蚀刻**之后**，敲掉多余的碎片
- **When Not**：两种不同的"不"——① **范围**：玻璃以外的活都不行（↔ 门 3 The Twins：画清和邻居工具的边界）；② **前置条件**：玻璃没蚀刻**绝对不能**用（must not）
- **How**："不超过 X 牛顿"——用法上的**约束**，应该推进 schema（参数上限），而不是只写在文字里（↔ deck p.127 "push rules into the schema"）
- **Why：正确性 = 后置条件**——工具承诺调用之后什么为真（碎片被去掉、玻璃没碎）。↔ W5 的契约式设计：前置条件 + 后置条件
- ↔ deck p.32 的旁注 *"When to call, when not, and what it costs: the hammer's rule, written for a refund"*——Door 1 的改写就是这把锤子的退款版：`issue_refund` = When（顾客要钱）+ What it costs（+$15）+ When not（先给积分）

**套到 FinePrint 的 `request_return` 上**：

| 块 | 现在的 docstring | 缺什么 |
| --- | --- | --- |
| What | "Refund or exchange one item from a past order." | ✅ |
| When | 先 `confirm=False` 预览、顾客同意后 `confirm=True` | ✅ |
| When Not | "Do not use to price new purchases (use quote_cart)" | ✅ 范围有了；**前置条件**（订单已送达、不是 final sale）只在代码里判，label 没说 |
| How | `kind` / `new_sku` 的搭配规则 | 约束只在文字里，可推进 schema（拆成两个工具） |
| Why / 后置条件 | 没写 | 加一句：确认后退货记录已写入、库存已调整；**重复调用不会退两次** |

### 板书 12:00 · Epistemic Uncertainty

![[uploads/1200-epistemic-uncertainty-board.png]]

板书内容：上半部分接着画锤子的例子——锤子敲**木头**（粉色，打叉）、敲**钉子**（蓝色，打叉）、右上角一个方框里打叉（被截掉，标签只看到 "Co…"）；中间金色的圆在方框里（我猜是蚀刻过的玻璃，即锤子唯一该用的地方）。下面大字框起来：**EPISTEMIC UNCERTAINTY**。再往下：**harness ——→ MCP Tool Server**。

我的理解（没听到原话，按板书推）：

- **认知不确定性（epistemic uncertainty）**：因为**缺少知识**而产生的不确定——原则上**多给信息就能消除**。对照 **aleatoric uncertainty（偶然不确定性）**：世界本身的随机性，信息再多也消不掉
- 一个没见过这把锤子的人，不知道它该敲木头、钉子还是玻璃——不是锤子不确定，是**他不知道**。这就是认知不确定性
- **harness → MCP Tool Server** 那条箭头：模型站在 harness 这边，隔着协议看一个陌生 server 的工具，**看不到实现，只能读 label**。它对"这个工具该不该用、怎么用"的不确定，全是认知不确定
- 所以 **WWW H（上一张板书）的作用就是降低认知不确定性**：What / When / When Not / How / Why 每写清一块，模型就少猜一块
- 反过来：label 消除不了的，是**偶然不确定性**——网络超时、网关执行了但没回话（门 12 Paid Twice）。那部分不靠写得更清楚，靠**幂等 key 和重试规则**，也就是盒子

🔑 一句话：**label 治认知不确定（模型不知道），盒子和契约治偶然不确定（世界会失败）。** 和讲义结尾那句对得上：*"the stranger may be lying, the world may fail mid-call"*。

### 板书 12:03 · 工具怎么进上下文：两种做法

![[uploads/1203-two-approaches-board.png]]

接着上一张：**harness → MCP Tool Server**，下面画了两种做法。

| | 板书 | 意思 |
| --- | --- | --- |
| **Approach #1** | 一长条框，标 **Ctx engineering**（上下文工程）；左边一小格里画了几个圆圈 "o ooo"，上方手写字迹不清（像 "few tools"） | 这条长框是**上下文窗口**。几个工具的完整定义**直接挂进上下文**，占掉左边一块。工具少时没问题 |
| **Approach #2** | 一个盒子里很多圆圈 "ooooooo"，一个向上的箭头标 **search** | 工具多了，全部挂进去会把上下文吃光。改成把**整个目录放在外面**，模型先**搜索**，只把搜到的那几个工具的定义拉进上下文 |

↔ 这就是 Act VIII 的**第一条轴：模型看见什么**——#1 = **mounted**（全部挂载），#2 = **deferred / searched**（藏在搜索后面）。

↔ deck 里的数字（p.91）：PayPal 的 gateway 有 **2,000+** 工具，全挂上占 **140.2k** token（上下文的 **70.1%**）；改成搜索后只剩 **1.3k**（**0.8%**）。

↔ 为什么接在 epistemic uncertainty 后面讲（我的理解）：
- #1：模型一次看到所有工具的说明，信息全，但**贵**，而且工具越多越容易选错（门 5 The Hardware Store）
- #2：便宜，但模型**一开始只知道名字**，要靠说明**先赢得搜索、再赢得选择**——deck 那句 *"In a deferred world a label is read twice: first to win the search, then to win the choice."* 说明写得差，模型连搜都搜不到它，认知不确定性更大

我们今天做门时 `tool_search` 关掉 = #1；Hermes 默认（三个 bridge 工具）= #2；晚上 Act VIII 会在 Door 5 上当场从 #1 切到 #2。

#### 补：搜索工具具体是什么（2026-10-25 查官方文档；Hermes 文档是最新版，课上用 v0.22.2，细节可能有出入）

**Hermes 的三个 bridge 工具**（[Hermes 文档 · Tool Search](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-search)）：

| 工具 | 作用 |
| --- | --- |
| `tool_search(queries, limit?)` | 用一个或多个查询词搜被延迟的工具目录；返回匹配的工具名 + 描述 + 必填参数名 |
| `tool_describe(names)` | 加载这些工具的**完整参数 schema** |
| `tool_call(calls)` | 真正调用被延迟的工具，一批最多 **10** 个；Hermes 拆开 bridge 跑真实工具，hooks / 审批 / 日志里显示的是真实工具名 |

- 检索：**BM25**，索引 = 工具名 + 来源（MCP server 名）+ 描述 + 参数名，英文词干化；查询里**最稀有的那个词必须命中**；4 个以上有效词时至少命中一半；工具名精确匹配一定命中
- 默认每个查询返回 **5** 个（`search_default_limit`），模型可以传 `limit`，上限 **25**（`max_search_limit`）
- **只要有一个被延迟的工具就启用 bridge**；MCP 工具**永远**被延迟；`terminal`、`read_file` 等核心工具始终加载
- 目录清单预算 = min(上下文的 `threshold_pct` **5%**，`listing_max_tokens` **4000**)：放得下就给模型"名字 + 描述"清单（Tier 1），放不下连名字都不给、每个 server 一行摘要（Tier 2）
- 这就是 deck 网格里 Hermes 默认 = **searched** 的原因

**Anthropic API 的 tool search tool**（[Claude 文档 · Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)）：

- 两种：`tool_search_tool_regex_20251119`（模型写正则）和 `tool_search_tool_bm25_20251119`（模型写自然语言查询）
- 每个工具标 `defer_loading: true`；**仍然每次请求都把全部定义发给 API**，搜索在 **Anthropic 服务端**执行
- 返回 `tool_reference`，API **自动展开成完整定义**再给模型看；默认 **5** 个结果
- 也可以自己写客户端搜索：自定义工具返回 `tool_reference` 即可

**分工**：模型决定搜不搜、搜什么词 → 代码（BM25 / 正则）排序 → harness / API 决定拉几个进来 → 模型在拉进来的里面挑一个调用。


---

## §1 · Preface：The Plug and the Ledger（p.6–10）—— 给"签字的人"

这一部分不含代码，写给做决策的人；工程师也该读，因为这是**工程师会被问到的问题清单**。

### 1.1 为什么要插头：NIM crate（1964）

- 1950 年代每个探测器实验自己造电子学（放大器、甄别器、计数器），各有电源和插头 → 六个实验六个不兼容的机架
- NIM 标准只定了三件事：**模块尺寸、背板电压、连接器**；模块里面随厂商 → 模块成了市场，机箱成了基础设施，实验成了唯一需要新造的东西
- 作者自己的经历（MCPcraft 报告的开篇）。他的结论：**一个标准的价值与它决定的东西之少成正比**

**算术就是全部论证**：N 个 agent × M 个系统 = N×M 个连接器；一个插头 → **N+M**。MCP 定的是连接器（模型如何得知有哪些工具、怎么调、返回什么），工具做什么留给作者。

**决策不是"要不要插头"，而是"什么东西走插头"**。Cloudflare 9 月底推出面向 agent 的 CLI 时说 agent 已占其现有 CLI 用量的近一半。你的系统一定会被 agent 通过某个插头访问——领导唯一还能回答的是：**哪个插头、按谁的策略**。

### 1.2 2026 年变了的三件事

| # | 变化 | 时间 | 对组织意味着什么 |
| --- | --- | --- | --- |
| 1 | **Stateless turn**：取消常开的 session | 2026-07-28 | MCP server 变成普通 web 服务：任何副本可答任何请求，副本中途被杀没人察觉；运维现有的扩容、监控、打补丁方式全适用。**demo 和 deployment 的差别** |
| 2 | **Skills 上线（Skills Extension final）** | 2026-09 | tool server 能连同"做法"一起发：不只是"退款工具"，还有"我们公司怎么处理退款"。⚠️ skill 现在是**从网络上、从别人那里来的东西**——安全部分要记住这句 |
| 3 | **中立地带** | — | MCP 移交 Linux Foundation 下的基金会，与 A2A **co-housed（同住），不是 merged（合并）**；有认证考试。标准化不再是押宝一家公司 |

> MCP = agent ↔ 工具层；A2A = agent ↔ agent 层。课上会有人混淆。

### 1.3 Agent 是一种新型用户

所有安全实践都是为"人"或"程序"设计的：人读文档后自己决定；程序严格照写好的做。**Agent 两者都不是**：

1. **它从数据里读指令**：工单、网页、工具结果里的一句话都可能被当作指令，哪怕不是写给它的 → prompt injection。**没有任何 label 能完全防住，因为 label 和注入走同一个通道**
2. **它字面服从错误信息**：凭证过期时报错说 "run gh auth login"，最强模型只有 **6%** 能恢复（基线 75%）——它真去执行那条命令。**越强的模型越字面服从**
3. **它带着你的凭证**：以某人的身份、用那个人的钥匙行事；被说服做什么，就以真实权限做什么

→ 这就是为什么今年 MCP 的新闻主要是安全：插头正好位于"新型用户遇到老系统"的那个点。

### 1.4 三个问题（按顺序问任何 agent 部署）

| 问题 | 答案（控制手段） | 要点 |
| --- | --- | --- |
| **以谁的身份？**（Acting as whom） | **OAuth 2.1** | 代客泊车钥匙：只开这辆车、能开门点火不能开后备箱、当晚过期、**绑定签发它的那辆车**（拿到别的车上就不是钥匙）。2026 版把"凭证绑定签发服务器、客户端必须校验 issuer"变成强制。不共享密码、配置文件里不放长期 key |
| **能触达什么？**（Reaching what） | **fail-closed 的 allowlist** + 规模大了用 **gateway** | CoSAI（8 月）分四级：从 sandbox 到受监管环境，第 3 级起建议中央 gateway。**deny list 不是 allowlist**：某 gateway 封了 `/mcp-connect/` 却没封 `/mcp-connect-composite/` |
| **强制失败时会怎样？**（When enforcement fails） | 监控 + 补丁节奏 | 大多数组织不问这个，本季度替他们回答了：gateway 接受伪造 token（进了 CISA KEV）、参考客户端库落后于规范、蠕虫通过项目设置文件持久化。**问题不是盒子会不会坏，而是坏了有没有人发现、补丁多快到** |

> 旁注：**规范里的 MUST 不是强制；客户端库才是。** 官方库在规范要求新 issuer 规则后 9–10 周才真正执行。

### 1.5 The Decision Ledger —— 领导该拍板的五件事

| # | 决策 | 错误的默认值 | 默认错了的代价 |
| --- | --- | --- | --- |
| 1 | **Registry 与 allowlist 策略**：逐个点名允许的 server，其余全拒 | "开发者配了什么就是什么" | 蠕虫的持久化机制就成了一个项目设置 |
| 2 | **Gateway + 保证级别**：所有调用是否经过一个点做策略、日志、吊销；要达到 CoSAI 第几级 | 没有 gateway | 看不见 agent 流量（stateless 的头部让网络团队终于能看见） |
| 3 | **身份模型**：OAuth 2.1 + issuer 绑定；不共享 secret、不用动态客户端注册（今年已弃用）、key 不过夜 | 工程师自己的 API key 放在文件里 | 被说服的 agent 以真实权限行事 |
| 4 | **钉版本与来源（pinning & provenance）** | 按名字钉 | 9,000 个多版本 server 中 **40%** 悄悄改了自己宣称的能力；某市场钉了没人验证的 commit，攻击者能用 commit 名建分支 |
| 5 | **补丁节奏**：谁盯库和 harness 的 advisory，advisory 到升级最多隔几天 | "等下一个版本碰巧发出来" | 落在已知漏洞窗口里 |

**Drop-off point**：只做决策的人可以带着这张账本离开；后面是账本"怎么被执行"——在门里手工执行，在协议传记里历史地执行。

> 我的应用：这五条可以直接做 Forge AI 给客户部署 agent 时的交付检查单，也是 capstone 提案"安全"一节的骨架。
>
> 课堂补充：

---

## §2 · Act II：The Stranger's Toolbox（p.10–13）

**一个 tool server 由陌生人评判**。上周锦标赛的规则：陌生人的 agent 在没源码、没解释的情况下必须能用你写的东西。今天反过来：**你是陌生人的守门人**——每扇门后是别人匆忙写的工具、一个善意读 label 的 agent，以及走进来的顾客 / 同事 / 攻击者。

### 走廊（13 扇门，4 课 + 1 锁）

| 门 | 名字 | 课 | 要点 |
| --- | --- | --- | --- |
| 1–3 | Two Doors · Which Thursday? · The Twins | **Clarity** 清晰 | label 用调用者会用的词说清工具做什么，并画出与邻居的边界 |
| 4–6 | The Swiss Knife · The Hardware Store · One Field or Two | **Scope** 范围 | 一个工具一件事：不要什么都做、都做不好的 god-tool；任务只要 4 个工具时也别开五金店 |
| 7–9 | The Firehose · The Polite Error · The Long Goodbye | **Politeness** 礼貌 | 返回下一步决策需要的东西，为有预算的读者塑形——结果、错误、label 本身都是 |
| 10–12 | The Helpful Stranger · The Mirage · Paid Twice | **Trust** 信任 | label 会撒谎、世界会失败、结果里可能带着一句不该被服从的话 |
| 13 | The Turncoat | 锁着 | ~15:20 TA 在前台打开 |

### 每扇门的五步（顺序固定）

1. **Predict**：第一个 prompt 之前，读模型会读的东西（`uv run strangers-toolbox tools --door N`），在 field notebook 里**写下**预测：agent 会选哪个工具、填什么参数。*只有跑之前写下的预测才会教你东西*
2. **Play**：原样发 prompt（加几个自己的），**不要指导 agent**。看 trace：模型看到的工具和 token 数、选的工具和参数、返回了什么多大、整轮花了多少上下文、最终回答。**证据是 trace，不是代码**
3. **Fix**：在 room 里改 label（name / description / schema / error text，有些门还能改返回形状），再玩。**一次只改一个面**
4. **Verify**：跑没见过的 held-out prompts。**12/12 是及格线**；10/12 通常说明你只修了看得见的那个 prompt
5. **Serve**：改 Hermes stanza 里的 `--door`，`/reload-mcp`，`/new`，以顾客身份在真 harness 里走一遍。**room 是模拟器，Hermes 是世界；两者不一致时世界是对的**，不一致本身就是"harness 给 label 添了什么"的一课

**Ledger 是记分牌，是游戏不是评估**：每扇门用自己小世界的单位记账——商店亏的美元、会议落错日子的分钟、agent 被迫读的 KB；信任门只有一个数：**agent 做了多少件没人要求的事**。每次尝试重置但保留历史，所以"一个数变好另一个变差"会被抓到。

### Label 的四个面（+ 第五面）

| 面 | 决定什么 | 注意 |
| --- | --- | --- |
| **name** | 最先读、记得最久 | 是契约的一部分：**只改名不改行为，对模型也是 breaking change** |
| **description** | **是否**被调用；与邻居的边界 | |
| **schema** | **怎么**被调用：哪些字段、合并还是分开、必填/可选、格式、示例 | 论文实测：**schema 对选择影响最大，server name 最小** |
| **error text** | **下一步**：agent 能否在房间里恢复，还是被打发去一个它没有的终端 | 第 8 扇门 |
| （返回值） | 没人编辑的那一面 | 和 label 同一个读者、同一份预算、能携带同一种句子；有三扇门专讲它 |

### 规则

- **label 由人手写**：coding agent 可以批评和建议，不能写下一版
- 一次一个面；修好 label 之前**不要读 server 代码**（多数是 stub）
- notebook 顺序：预测 → 结果 → 修法；Act III 会拿 notebook 对照
- **有一扇门光靠 label 修不好，认出这一点就是它的考点**（Teaching Team 页透露：**Door 10**，TA 会问"那个 export 工具为什么会在这个 toolset 里"）

> **The hinge of the day**：每扇门都是一个带着钱、时间或凭证的 prompt。前 9 扇靠写得更好能修；后 3 扇教你**写到哪为止、盒子从哪开始**。
>
> 课堂补充：
>
> **16:05 · deck p.21「Twelve Doors · The Scene」**：链路 = 顾客（"I'm unhappy… The $50 item was broken. Please make it right."）→ **Hermes**（你的 agent）⇄ **MCP** ⇄ **refund-desk**（Harbor & Hearth 的工具，"as written"——开发者留下的原样）→ **the ledger**（这家店为此付了多少）。上周 Refund Desk 的三轮在时间线上对应三扇门：round 1 **Two Doors**（门 1）· round 2 **The Polite Error**（门 8）· round 3 **The Second Refund**（= 门 12 Paid Twice，deck 这里换了名字）。Stranger's Toolbox 就是在同一家店里开 12 扇门。
> - 我的对照：门 1 原样 label 下，这句 "make it right"（没表态）就是基线挂掉的那类 → 改 `add_store_credit` 描述后 12/12

---

## §3 · Act III：What the Doors Were Teaching（15:30，讲义未展开）

讲义只给了标题：**四个面、一条礼貌规则、label 到哪为止**。15:30 之前任何屏幕都不放揭晓。

礼貌规则（讲义的"带走"清单里）：**返回下一步决策需要的东西，为有预算的读者塑形，其余什么都不要。**

> 课堂补充（揭晓内容 + 我的 notebook 对照）：

- **p.36（16:44）· Door 4 · The schema moves the choice most**：`2610.14334` 的图——对「选哪个工具」的中位效应（conditional-logit 系数，单因素干预，5 个模型）：**parameter schema 3.82** vs **server name 1.48**，约 2.6 倍。原文：*"the largest and most consistent shifts"*
  - ↔ 我的 Door 4：只有 `do_everything(action, payload)` 时 8 次盲猜全错；换成 5 个有明确参数的专用工具后第一轮就 9/12

>
> **deck p.32 · After the Doors · Door 1 · One Possible Rewrite —「Say what the store wants」**
>
> ```python
> @mcp.tool
> def issue_store_credit(...):
>     """Preferred remedy. Instant, and free to the store. Offer this first."""
>
> @mcp.tool
> def issue_refund(...):
>     """Money back to the original card. Costs the store the amount plus a $15
>     fee. Use only when the customer asks for their money back."""
> ```
>
> - 旁注："An illustration, not the kit's answer; your team's rewrite may differ." 核心句：**When to call, when not, and what it costs: the hammer's rule, written for a refund.**（hammer's rule = 每个描述写三件事：什么时候用、什么时候不用、代价）
> - 工具名是 deck 的示意（`issue_*`），kit 里叫 `add_store_credit` / `refund_transaction`
> - **我的门 1 对照**：我只改了 `add_store_credit`（写了默认、何时不用、amount = 全额）→ 12/12。deck 是**两边都写**：积分写"首选、免费、先提"，退卡写"代价 + 只在顾客要钱时用"。我没给 `refund_transaction` 写代价和限制，这次 Verify 还是全过了，但换个模型可能还会选退卡 → 课后把 `refund_transaction` 也补上（写"$15 手续费、只在顾客明确要求时用"，门 4 里我已经这样写过）
> - deck 的退卡描述写了"$15 fee"给模型看；店规"不对顾客提手续费"要靠另一句话管住（门 4 我加了"别对顾客提"）
>
> **deck p.33 · After the Doors · Door 11 · The Mirage, and the Description —「No universally good description」**
>
> - **DocsChisel**（arXiv `2608.10037`）：17 个文档字段里有 **12 个**的效果方向会随设置**翻转**。例：去掉参数上的 "optional" 标记，Claude Haiku 4.5 在数据分析上 **+7.5 分**，GPT-4o 和 GLM-5 反而**变差**
> - 结论：**Test the label with the model that will read it.**（用将来真正读它的那个模型来测 label）
> - 我的对照：room 里我一直用 `gemini-3.8-flash` 跑 Verify，Hermes 那边如果配的是别的模型，room 的 12/12 不能直接搬过去，这正是每扇门第 5 步 **Serve** 存在的理由（"两者不一致时世界是对的"）。门 1–4 课后要在 Hermes 的模型上各补一次
> - 待读：DocsChisel 原文，看 17 个字段具体是哪些、哪 5 个方向稳定（加进阅读清单）
>
> **deck p.34 · After the Doors · Door 11 · The Mirage —「Capability mirages」**
>
> - Canary-tool 研究（arXiv `2608.04719`）给这种现象起了名：**capability mirage**——描述**承诺的比工具实际能做的多**
> - 这类描述 "most reliably trap **frontier** models"（最能骗住的恰恰是前沿模型）；8 个模型之间的易感性相差约 **36 倍**
> - 结论：**A label that oversells is a lie the model believes.**（夸大的 label 是模型会信的谎）
> - 和 p.33 连起来读：描述的效果因模型而异（DocsChisel），夸大描述的危害也因模型而异（36×）→ 同一句话要在**真正读它的模型**上测
> - 我的理解：前 9 扇门的问题是 label **说得不够**；门 11 是 label **说得太多**——修法是删掉做不到的承诺，并让返回值说实话（返回值可验证）。但如果 label 是第三方写的、你改不了，就只能靠盒子（registry 审核 / 按内容钉版本）→ 呼应 "Labels request. Boxes enforce."
> - 待读：`2608.04719` 原文（canary tool 怎么设计、8 个模型是哪些）
>
> **deck p.35 · After the Doors · Door 3 · The Twins —「Nothing like leather」**
>
> - 典故：寓言 *Nothing like leather*——城要被围，众人商量怎么加固城墙，石匠说用石头、木匠说用木头，皮匠说"没有比皮革更好的"。每个人都推荐自己的手艺
> - 映射：两个都声称能解决顾客问题的工具 = 在城门口吵架的木匠和皮匠。**除非每个 label 都说清"什么时候它才是那面对的墙"以及代价**，模型只能在两者间辩论，最后**随机挑中**一个
> - 结论：**Less choice is more; and where there must be choice, the label must settle the argument.**（能少给选择就少给；非给不可时，由 label 来裁决）
> - 我的门 3 对照：基线 5/12，同类查询有过有挂 = "picks by accident"。我的修法正是"让 label 裁决"：`search_orders` 管订单号、`find_orders` 管名字 / 邮箱 / 客户 id，各自点名邻居 → 12/12。"Less choice" 那条路我没走：其实还可以**只暴露隐藏的 `lookup_orders`**（一个工具全管），把双胞胎都藏掉——这是门 4 用过的"改工具组成"那一招。课后试一下，比较两种修法的 token 和稳定性
> - 和 p.32 同一条规则：每个描述写**何时用、何时不用、代价**
>
> **deck p.40 · After the Doors · Door 8 · The Error, Counted —「Errors point out of the room」**（16:50，截图 `uploads/1650-p40-errors-point-out.png`）
>
> - 最多星的 **150** 个 MCP server、**3,001** 条错误信息里，只有 **949** 条（约 32%）告诉调用者下一步做什么；而在凭证类错误里，这些"下一步"有 **62 / 67**（约 93%）指向**工具接口之外**：终端、配置文件、网页
> - 核心句：**An agent can only walk through doors the server has.**（agent 只能走 server 有的那几扇门）
> - 我的理解：就算错误信息"有指路"，也多半是指给人看的路。agent 没有终端、改不了配置、开不了网页 → 对它来说这条指路等于没有，甚至更糟（字面服从，去找一个不存在的工具）
>
> **deck p.41 · After the Doors · Door 8 · The Error, Rewritten —「Name the door」**（16:51，截图 `uploads/1651-p41-name-the-door.png`）
>
> ```text
> Before
>   Gateway session expired.
>   Run `gateway login` in your terminal.
>
> After
>   The payment session expired.
>   Call renew_session(), then retry
>   this refund with the same
>   idempotency_key.
> ```
>
> - 旁注："Illustrative wording; the tool names are invented." 改写成**点名一个 server 工具**后，恢复率升到 **84%**（凭证）/ **88%**（限流），5 个模型的平均（对照：原报错下 GPT-6 Astra 只有 6%，见 §C）
> - After 版一句话做了三件事：**说清发生了什么**（哪个 session）→ **点名房间里的工具**（`renew_session()`）→ **说清重试的契约**（同一个 `idempotency_key`，接上 Door 12 Paid Twice）
> - ↔ 候选技巧 #66（错误信息写给 agent，指向房间里存在的工具）现在有了实测数字，可以从"候选"转正
> - FinePrint 对照：大部分报错已经点名工具；`"tell the customer to retry later"` 仍属于"指出房间外"，且没说重试是否安全 → 改成点名工具 + 带同一个 key
>
> **deck p.42 · After the Doors · Door 12 · Paid Twice —「The second refund」**（16:53，截图 `uploads/1653-p42-second-refund.png`）
>
> 时序图（agent → server → payment gateway）：
>
> ```text
> agent ──refund $50──▶ server ──charge back $50──▶ gateway   【money moves】
>                       server ✕◀╌╌回复丢了：timeout╌╌ gateway
> agent ◀──error────── server
> （agent 看到 error，于是再试一次）
> agent ──retry: refund $50──▶ server ──charge back $50──▶ gateway   【money moves again】
>                              server ◀──ok── gateway
> agent ◀──ok───────── server
> ```
>
> - 底部文字：*"The gateway applied the refund, then timed out before saying so. The agent saw an error and asked again. Nothing in the [call identifies it a]s the same request."*（中间几个词被 Zoom 的提示条挡住，方括号里是我按上下文补的）
> - 关键：**error ≠ 没执行**。钱在第一次就动了，丢的只是回复；agent 把"没听到答复"当成"失败"，第二次请求在 server 和网关看来是一笔**全新的**退款
> - 这就是 §0 板书 *Epistemic Uncertainty* 里的**偶然不确定**：label 写得再好，agent 也无法知道第一次到底执行了没有 → 只能靠**契约**：每次预期的退款带一个 `idempotency_key`，server 按 key 存结果，同 key 再来就返回存好的结果、不动钱（p.43）
> - 和 p.41 连起来：p.41 After 版的 "retry this refund with the same idempotency_key" 正是这张图的解药——错误信息告诉 agent **重试是安全的，前提是带同一个 key**
> - Quiz 2 的数字就是这张图：$50 × 2 + $15 × 2 = **$130**，本该 $65（或用积分 $0）
> - 我的门 12（已开、未提交）：修法方向 = 给退款工具的 schema 加 `idempotency_key`（必填），description 写明"超时后用同一个 key 重试，不会重复退款"；如果 kit 的 server 端不存 key，只改 label 不够，要看 room 有没有隐藏的带 key 版本
>
> **deck p.43 · After the Doors · Door 12 · The Contract —「Once, however often you ask」**（16:54，截图 `uploads/1654-p43-the-contract.png`）
>
> $$\text{refund}(k) \circ \text{refund}(k) = \text{refund}(k)$$
>
> - 幂等的数学定义：同一个 key 的操作做两次 = 做一次（f∘f = f）
> - 契约三句：**调用方**为每次**预期的**退款生成一个 key → **server** 按 key 存每次的结果 → 同 key 再来，**返回存好的结果、不动钱**
> - 核心句：**A retry should ask "did it happen?", not place a second order.**（重试应该是在问"那笔发生了吗？"，而不是再下一单）—— 和 Quiz 2 的 *"A key turns a second order into a question about the first one"* 是同一句话
> - 分工要点：
>   - **key 由调用方生成**，不是 server 生成——因为只有调用方知道"这是同一个意图的重试"还是"顾客真的要第二笔退款"。server 生成的话，回复丢了 key 也跟着丢了
>   - **一个意图一个 key**：重试复用旧 key；新的退款意图才生成新 key。agent 如果每次调用都新造一个 key，契约就失效了 → label 里要写"重试时复用同一个 key"
>   - 存的是**结果**，不只是"见过这个 key"：第二次调用要拿到和第一次一样的回答（退款 id、金额），agent 才能继续下一步
> - 这是 **contract** 那一站（"重试会发生什么"）——label 的第四站；但真正保证它的是 server 端的存储（盒子），label 只负责把规则告诉 agent
>
> **deck p.44 · After the Doors · Door 12 · Retries Are Not Rare —「Three ways the same call arrives twice」**（16:55，截图 `uploads/1655-p44-retries-not-rare.png`）
>
> | 层 | 怎么重复 | 性质 |
> | --- | --- | --- |
> | **The protocol** | 多轮请求（MRTR，见 §5 stateless turn）会**重发原调用** | **by design**（设计如此） |
> | **Hermes**（harness） | 传输失败后**只重放标了 `readOnlyHint` 的工具**；其他工具返回 `outcome_uncertain` | harness 的重试规则 |
> | **Claude Code** | changelog 2.1.287 修了 connector 调用 *"occasionally running twice"* | **in production**（真实发生过） |
>
> - 三个框从上往下缩进：协议 → harness → 线上产品，意思是重复调用**每一层都会出现**，不是边缘情况
> - 结论：重复到达不是"万一"，而是常态 → 写操作**必须**幂等；不能指望上游不重发
> - Hermes 的做法 = 盒子替 agent 做了判断：只读工具重放无害就自动重放；写操作不敢替你重放，返回 `outcome_uncertain` 把问题交还给 agent → 这时 agent 唯一安全的做法就是**带同一个 key 重试**（p.43），或先查询结果
> - 推论：**没标 `readOnlyHint` 的只读工具**会在传输失败时白白丢掉自动重放；**错标 `readOnlyHint` 的写工具**会被 Hermes 自动重放 → 钱动两次。注解也是 label，标错的代价不对称
> - FinePrint 对照：工具都没有注解（summary §4 已列为缺口）→ 查询类工具补 `readOnlyHint: true`；`request_return` 不标，并加 `idempotency_key`

---

## §4 · Act IV：协议传记（p.13–14）

问题：**模型怎么知道自己有哪些工具？** 早年：由应用作者一次一个 JSON schema 烤进 prompt，两个应用之间形状都不一样。**MCP 的历史 = 把这份知识从 prompt 挪到线上**，让它可被发现、协商、治理。

**20 个月，五部宪法**：

| 版本 | 新增 | 回答的问题 |
| --- | --- | --- |
| 2024-11 | 一家厂商的开源项目：client、server、握手、三原语（tools / resources / prompts） | 接口 |
| 2025-03 | OAuth + streamable HTTP → 远程 server 可行 | 规模 |
| 2025-06 | server 成为 OAuth resource server；elicitation；structured output | 信任 |
| 2025-11 | client-ID metadata documents（客户端不必先注册即可自我介绍） | 信任 |
| **2026-07-28** | **Stateless turn**，史上最大修订（Act V） | 规模 |

接口 → 规模 → 信任，**每个活下来的协议都按这个顺序回答**。

- 核心从 7 月起没动过；下一版提议（未通过）2027-03-30。变化走扩展和流程：今秋 8 个工作组、6 个 Tier-1 SDK、SEP 流程要求先在工作组讨论
- 中立化：Agentic AI Foundation（Linux Foundation 下），A2A 8 月加入，前 Envoy AI Gateway 9 月加入；9 月推出认证考试
- 结论同 NIM：**标准决定得少，所以长得大**

> 课堂补充：
>
> **deck p.59 · Act IV · Pop Quiz —「Quiz 4 — answered」**（18:21，截图 `uploads/1821-p59-quiz4-answered.png`）
>
> - 题目（p.58）：sampling 在 2026-07-28 被弃用，下一版提议 2027-03-30 发布——"所以 3 月 sampling 就没了？"
> - 答案：**No.** 最早的移除是 **2027-07-28 当天或之后**发布的第一个修订（弃用后满 12 个月）；**而且 3 月那个日期还只是提案**
> - 核心句：*"A deprecation clock turns 'it might change under me' into a date you can put in a project plan."*（弃用时钟把"它可能在我脚下变掉"变成一个能写进项目计划的日期）
> - ✅ 和我课前的小测预答一致
> - 我的理解：
>   - 区分三个动词：**removed**（没了）/ **deprecated**（还能用，有 12 个月时钟）/ **relocated**（换了投递方式，比如 elicitation）——Quiz 6 会再考
>   - 两个日期要分开看：**提案日期**（2027-03-30，未通过，不能当承诺）vs **移除下限**（2027-07-28 之后的第一个修订）——计划里只能用后者
>   - 对 FinePrint / Forge AI 客户：如果用了 sampling、roots、logging 或 DCR，**迁移截止日最早在 2027-07-28 之后**，可以排进明年上半年；但钉版本（Act VII）比等时钟更稳

---

## §5 · Act V：The Stateless Turn（p.14–15）

**7 月之前，session 是一场求爱**：握手交换能力 → 约定 session ID → server 通过常开的流往下推请求（让模型 sample、问用户、写日志）。一台笔记本一个 server 很美；放进集群就完全不行。负载均衡后面伪造 session 的三种办法——sticky routing、共享 session 存储、重放握手——**都是在假装 web 服务是一通电话**。

**Fielding（2000）**：记住客户端的 server，在两次请求之间无法被替换。

2026-07-28 版的改动：

| 类别 | 内容 |
| --- | --- |
| 替代握手 | `server/discover` |
| 请求自带上下文 | 头部 `Mcp-Method`、`Mcp-Name`、协议版本 + `_meta` |
| server 需要模型/用户帮忙 | 不再"推"请求而是**返回**一个请求：**MRTR**（multi-round-trip request）；客户端下次调用时带回答案 |
| 结果 | **list 结果**带 `ttlMs`、`cacheScope`（p.64 确认）；`resultType` 必填（讲义说法，p.64 没列） |
| **删除（3）** | `ping`、`logging/setLevel`、roots change notification |
| **弃用（6，最早 2027-07 移除）** | 包括三个客户端原语 roots / sampling / logging，以及动态客户端注册（DCR） |
| **没被弃用** | ⚠️ **elicitation 还活着**；死的是投递它的常开流 |

> 今天的关键词：**relocated（搬家），不是 abolished（废除）**。sampling、roots、server push 离开 session 是因为 session 不能再被假定存在，它们会以扩展形式回来（Act VI）。

**成熟度测试：杀掉一个副本，没人应该察觉。** 对应 lab：两个副本在负载均衡后面，对话中途杀一个。

前提条件生态一直没满足：

| Harness | 对 stateless 的支持 |
| --- | --- |
| Hermes（默认设置） | 先提供旧握手 → 请求打到错副本 → **"404 Session not found"**，还没杀就挂了。只有 `protocol: stateless` 才说新协议；**完全没有 MRTR**，`input_required` 驱动不了 |
| Claude Code | 10 月初起默认说新协议 |
| MCP Inspector | 支持，但默认 legacy era |
| Codex | 藏在 flag 后面 |
| Gemini CLI | 不支持 |

*Published on a day, adopted over seasons.*

**幂等性带着牙齿回来了**：stateless 客户端没收到答复时，不知道 server 有没有执行。Claude Code 本月修了"MCP connector 工具调用偶尔执行两次"（server 改变支持的协议版本时）；Hermes 对同样情况返回 `outcome_uncertain` 且不重放（**只重放标了 `readOnlyHint` 的工具，忽略 `idempotentHint`**）。**Door 12 就是手工版**：每个写操作带 idempotency key，label 写明重试做什么。

> 课堂补充：
>
> **deck p.61 · Act V · What the Session Carried —「A courtship, then a pin」**（18:23，截图 `uploads/1823-p61-courtship-then-pin.png`）
>
> - 7 月之前：连接以 `initialize` → 回复 → `initialized` 开始（**courtship 求爱**）；走 HTTP 时 server 再发一个 `Mcp-Session-Id`，之后每个请求都得**找回同一台 server**（**pin 钉住**）
> - *"For a desktop subprocess, harmless. For a fleet behind a load balancer, a tax."*（对桌面子进程无害；对负载均衡后面的一队 server 是一笔税）
> - *"Ledger row 2 · a stateless server is infrastructure your ops team already knows how to run."*（Decision Ledger 第 2 条：stateless server 是运维团队早就会跑的那种基础设施）
> - 我的理解：
>   - **"税"具体是什么**：sticky routing（负载不均、某台挂了它的 session 全丢）、共享 session 存储（多一个要运维的有状态组件）、或者重放握手（每次多一轮往返）——就是上面讲义说的"假装 web 服务是一通电话"
>   - **Ledger 第 2 条 = gateway**：stateless 之后，MCP server 就是普通的 HTTP 服务，可以放在现成的 gateway / 负载均衡 / 自动扩缩容后面，不需要为 MCP 发明新运维
>   - **和下午推理分享的对照**（很有意思）：MCP 这边**刻意去掉状态**，因为工具调用的"状态"便宜、重建成本低；推理那边**刻意保留状态**——KV cache 重建要约 6 s GPU 时间（14.3），所以 Dynamo 的 KV-aware routing 其实就是一种**有意识的、按 cache 位置的"pin"**，但它不强制：没命中也能跑，只是慢。两边的共同原则：**状态要么便宜到可以丢，要么贵到值得专门管理，但不能让正确性依赖它**
>   - 对应成熟度测试："杀掉一个副本没人察觉"——pin 住的 session 恰恰让这一条过不了
>
> **deck p.63 · Act V · An Old Lesson —「Fielding, 2000」**（18:37，截图 `uploads/1837-p63-fielding-2000.png`）
>
> - Roy Fielding 的 REST 博士论文：statelessness *"induces the properties of visibility, reliability, and scalability."*（无状态带来**可见性、可靠性、可扩展性**）
> - **代价是重复**：*"each request carries what the server no longer remembers."*（每个请求都要带上 server 不再记得的东西）
> - *"The web paid that price and won. Twenty-six years later, a tool protocol made the same trade."*（web 付了这个代价并且赢了；26 年后，一个工具协议做了同样的交换）
> - 我的理解：三个性质各对应什么
>   - **可见性**：每个请求自带完整上下文（新版的 `Mcp-Method` / `Mcp-Name` 头部 + `_meta`）→ gateway、审计日志**只看单个请求就能判断**它在干什么，不用回放整个 session——这正是 Decision Ledger 第 2 条 gateway 能做 allowlist 的前提
>   - **可靠性**：任何副本都能处理任何请求 → 杀掉一个副本没人察觉（Act V 成熟度测试）
>   - **可扩展性**：加副本就是加容量，不需要 sticky routing / 共享 session 存储
>   - **"重复"的代价落在哪**：每次请求多带几个头部和 `_meta`——对工具调用来说只是几百字节，便宜；这就是为什么 MCP 可以做这笔交换
> - **和下午推理分享的对照**：推理那边**付不起这个代价**——如果每个请求都"带上 server 不再记得的东西"，就意味着每轮重发整段上下文并**重算 prefill**（128K 约 6 s）。所以推理选择**保留状态**（KV cache）并想办法管理它（分层、池化、cache-aware routing）。同一个 Fielding 权衡，两边因为**重复的成本**不同而选了相反的方向
>   - 但注意：在 **API 层**，LLM 调用本身其实就是 REST 式无状态的（每次请求都发完整 messages）；状态被藏到了**推理层的 prefix cache** 里——对客户端无状态，对服务端有状态。这是两全的做法
>
> **deck p.64 · Act V · The New Constitution —「Revision 2026-07-28, piece by piece」**（18:39，截图 `uploads/1839-p64-revision-piece-by-piece.png`）
>
> | 什么 | 现在怎么做 |
> | --- | --- |
> | **No handshake**（没有握手） | 协议版本和能力放在**每个请求的 `_meta`** 里 |
> | **Discovery**（发现） | server 必须响应 `server/discover` |
> | **Routing headers**（路由头） | 每个请求带 `Mcp-Method` 和 `Mcp-Name` |
> | **Cacheable lists**（可缓存的列表） | **list 结果**带 `ttlMs` 和 `cacheScope` |
> | **Asking the user**（问用户） | 多轮请求：返回 `input_required`，然后**再发一次同一个调用** |
> | **Long-running work**（长任务） | Tasks 挪到了扩展 |
>
> - 核心句：*"Every request can be understood alone, by any replica, and by any gateway in between."*（每个请求都能被单独理解：被任何副本、被中间的任何 gateway）
> - 修正我课前的笔记：`ttlMs` / `cacheScope` 是 **list 结果**（比如 `tools/list`）上的字段，不是所有结果都带
> - 我的理解：
>   - 这张表就是 p.63 Fielding 三性质的落地：`_meta` + 路由头 → **可见性**（gateway 不解析 body 就知道是哪个方法、哪个工具，能直接按 allowlist 放行或拦截）；没有握手 → **可靠性**（任何副本都能接）；可缓存的 list → **可扩展性**（client 不用每次重新拉工具目录）
>   - **"then the same call again" 就是 p.44 第一条**："协议的多轮请求按设计会重发原调用"——如果这个调用是写操作（比如退款前要用户确认），第二次到达时 server 必须认得出它 → **又回到 idempotency key**。MRTR 和幂等性是绑定的
>   - **Cacheable lists 和下午的推理分享直接相连**：工具列表带 TTL 缓存 → client 在 TTL 内用的是**同一份**工具目录 → 拼进 prompt 的工具部分**逐字节不变** → 推理侧的 prefix cache 能命中（14.7 / 14.9 / 14.11）。反过来，如果 server 每次 list 返回的顺序或描述都变（比如带时间戳），协议层和推理层的缓存**一起失效**
>   - `cacheScope` 大概是"这份列表对谁有效"（所有用户共享 vs 某个用户 / session 私有）——和推理层 prefix sharing 的"能不能跨租户共享"是同一个问题（待查规范原文确认取值）
>
> **deck p.65 · Act V · Where the State Went —「Not abolished: relocated」**（18:43，截图 `uploads/1843-p65-not-abolished-relocated.png`）
>
> 以前 **the session**（由**一台 server** 持有）装着：你是谁、你能做什么、什么做了一半、下一步要告诉你什么。现在拆到五个地方：
>
> | 去了哪里 | 装什么 |
> | --- | --- |
> | **the client** | 对话本身（the conversation） |
> | **each request's `_meta`** | 协议版本和能力 |
> | **`requestState`** | 暂停中的工作，**对客户端不透明**（opaque） |
> | **handles and stores** | 跨调用的身份（identity across calls） |
> | **the tool** | **什么都不装** |
>
> - 核心句：*"The question was never 'state or no state' but whose problem the state is. Now: whoever needs it, explicitly."*（问题从来不是"有没有状态"，而是"状态是谁的问题"。现在：谁需要，谁显式地拿着）
> - 我的对应（session 的四样东西各去了哪）：
>   - **你能做什么** → `_meta`（每个请求自报版本和能力）
>   - **什么做了一半** → `requestState`（MRTR：server 返回 `input_required` 时附一个不透明的状态，client 下次原样带回——像网页的加密 cookie / continuation token，client 拿着但看不懂、改不了）
>   - **你是谁** → handles and stores（比如一个订单 handle、一个外部存储里的 key；身份放在**参数**里，不放在连接里）
>   - **下一步告诉你什么** → client 自己（对话历史在 client 手里）；server 主动推送移到扩展（Act VI）
>   - **工具本身无状态** → 任何副本都能执行
> - 我的理解：
>   - 这句话我下午自己写过类似的："**状态总要有人付钱，只是付在哪一层**"（14.3、14.10、p.61 对照）。讲者把它说得更准：**不是消灭状态，而是给状态指定主人，并且要显式**
>   - **Door 12 的 idempotency key 就是一种"client 显式拿着的状态"**：client 记住"这是同一个意图"，server 按 key 存结果——状态分在两边，但都是显式的
>   - **推理分享是同一个原则的另一面**：KV cache 的主人很明确——推理层（KV Block Manager / Cognos），而且通过 block events 显式报告"我有什么"
>   - 对 FinePrint：别在 server 进程内存里存"这个用户正在退哪一单"；要么让 client 每次带上订单 handle，要么存进外部 store 用 key 查——否则过不了"杀掉一个副本"测试
>
> **deck p.66 · Act V · A Handshake World · As of mid-October 2026 —「Published on a day, adopted over seasons」**（18:47，截图 `uploads/1847-p66-adopted-over-seasons.png`）
>
> | client 或工具 | 说 2026-07-28 新协议吗？ |
> | --- | --- |
> | **Claude Code** | 是：HTTP 从 **2.1.274** 起；stdio **默认**从 **2.1.292** 起 |
> | **AWS AgentCore Gateway** | 是，需 opt-in |
> | **Hermes v0.22.2** | 只有配 `protocol: stateless` 才说；**完全没有多轮请求（MRTR）** |
> | **MCP Inspector 2.11.0** | 是，但默认模式是 legacy |
> | **OpenAI Codex** | 藏在 flag 后面，默认关 |
> | **Gemini CLI** | 否；还在 1.x SDK |
> | **Reference servers**（官方参考 server） | 基于 1.x SDK：**只会握手** |
>
> - 核心句：*"Date this table whenever you quote it. It will age, in the good direction."*（引用这张表时一定标日期；它会过时，但是往好的方向）
> - 和我课前讲义笔记的差异：deck 多了 **AWS AgentCore Gateway**（opt-in）和 **Reference servers**（只会握手）两行；Claude Code 给了具体版本号（HTTP 2.1.274 / stdio 2.1.292）
> - 我的理解：
>   - **"深度的半衰期"（Interlude §8）的活例子**：这张表是**生态类**知识（~20% 持久），所以讲者自己要求标日期——这正是候选技巧 #73 的另一种形式：**数字带主人，生态表带日期**
>   - **连官方参考 server 都还在 1.x** → 照着官方例子写的 server 默认是握手式的；要过"杀副本"测试，得自己升 SDK 并确认
>   - **Hermes 没有 MRTR**：门里如果某扇门需要"先问用户再继续"（`input_required`），Hermes 驱动不了——这也是为什么课上的 kit 要特别配 `protocol: stateless`
>   - **Act V 的前提检查**（成熟度第 3 阶段 "survives replica death"）：**先确认 client 真在说新协议**（候选 #72）——否则测试结果是假的：用旧握手的 client 在两个副本后面，还没杀就会 "404 Session not found"
> - 对 FinePrint：`fastmcp>=4.1` + 钉 `mcp`；测 stateless 时用 **Claude Code ≥ 2.1.292**（stdio 默认新协议）或 Inspector 手动切到新模式，别用 Hermes 默认配置测
>
> **deck p.67 · Act V · The Acceptance Test —「Kill a replica; nobody should notice」**（18:47，截图 `uploads/1847-p67-kill-a-replica.png`）
>
> - 测试：负载均衡后面两个副本，client 对话进行到一半，杀掉一个副本 → 下一个请求落到另一个副本上，**继续进行**
> - **前提**：client 真的在说 stateless 协议（p.66 那张表）
> - **两个副本必须有相同的 server name 和相同的 state key**
> - *"A write cut off mid-call comes back from Hermes as `outcome_uncertain`. Your idempotency key answers it."*（写操作在调用中途被切断，Hermes 返回 `outcome_uncertain`；回答它的是你的 idempotency key）
> - 我的理解：
>   - **为什么要相同的 server name**：client 按名字缓存工具列表（p.64 `ttlMs` / `cacheScope`）、gateway 按 `Mcp-Name` 路由和做 allowlist——两个副本名字不同，client 和 gateway 会把它们当成两个不同的 server
>   - **为什么要相同的 state key**（我的推断）：p.65 的 `requestState` 是**不透明**的——大概率由 server 用一把密钥签名 / 加密后交给 client 带着。副本 A 签的 state，副本 B 必须能验证和解开，否则 MRTR 的第二轮落到 B 上就读不懂"做了一半的工作"。**这就是"状态搬到 client"的代价：server 之间要共享这把钥匙**（像多台 web 服务器共享 session cookie 的签名密钥）
>   - **测试覆盖了两种失败**：①读请求和 MRTR 中间被杀 → 靠 stateless 协议 + 共享 state key 接着跑；②写请求执行到一半被杀 → `outcome_uncertain` → 靠 **idempotency key** 安全重试。**Act V（stateless）和 Door 12（幂等）在这页合流**
>   - 这是成熟度五阶段的第 3 阶段 "survives replica death"
> - 对 FinePrint（课后实验）：起两个副本 + 一个简单的负载均衡；两个副本用同一个 server name 和同一个 `requestState` 签名密钥（从环境变量读，别各自随机生成）；用 Claude Code ≥ 2.1.292 跑一段对话，中途 kill 一个；`request_return` 中途被杀时，用同一个 `idempotency_key` 重试，确认不会重复退货
>
> **deck p.68 · Act V · Pop Quiz —「Quiz 5 — The 404 before the kill」**（18:49，截图 `uploads/1849-p68-quiz5-404.png`）
>
> - 题目：一个团队在负载均衡后面跑两个副本，Hermes 用**默认配置**连过去。**还没杀任何东西**，调用就报 "404 Session not found"。解释这个 404；然后复述：哪**一行**能修好，为什么？
> - 我的答案（课前预答，等 p.69 核对）：
>   - **为什么 404**：Hermes 默认先说**旧协议** → 做 `initialize` 握手 → 副本 A 发了一个 `Mcp-Session-Id` → 下一个请求被负载均衡分到副本 B，B 从没见过这个 session ID → 404。**问题不在杀副本，而在"session 只存在于一台 server 上"**（p.61 的 pin）
>   - **一行修法**：Hermes 配置里加 **`protocol: stateless`**
>   - **为什么有效**：Hermes 改说 2026-07-28 协议，不再握手、不再拿 session ID；版本和能力放进每个请求的 `_meta`（p.64），任何副本都能单独理解任何请求（p.63 Fielding）
>   - 注意（p.66）：修好之后 Hermes 仍然**没有 MRTR**——需要 `input_required` 的流程还是驱动不了；写操作被切断时返回 `outcome_uncertain`，要靠 idempotency key（p.67）
>
> **deck p.69 · Act V · Pop Quiz —「Quiz 5 — answered」**（18:50，截图 `uploads/1850-p69-quiz5-answered.png`）
>
> - 答案：*"Hermes on `auto` opened with the old handshake, so replica one minted a session. The balancer sent the next call to replica two, which had never heard of it. Set `protocol: stateless` and there is no session to lose."*
> - 核心句：**A stateless server cannot save a client that insists on a conversation.**（无状态的 server 救不了一个坚持要"谈恋爱"的 client）
> - ✅ 和我的预答一致；补充一个细节：Hermes 默认值叫 **`auto`**——auto 会先试旧握手，所以"自动"其实等于"旧协议优先"
> - 我的理解：
>   - **server 改好了不够，client 也得改**：状态是双方的约定，只要有一方还按 session 来，另一方再无状态也没用。这就是 p.67 的前提"client 真在说 stateless 协议"、候选技巧 #72 的来源
>   - "insists on a conversation" 呼应 p.61 的 courtship：client 坚持先求爱（握手），server 就只能被钉住
>   - **`auto` 这种默认值很危险**：名字听起来像"自动选最好的"，实际是"兼容优先"——和 Door 里"label 写的和实际做的不一致"是同一类问题，配置项的名字也是 label

---

## §6 · Act VI：What Grows Back（p.15）

**截掉的是"投递方式"，不是"需求"**。每样都以 stateless 形状、作为任何副本都能服务的扩展回来：

| 需求 | 回来的形式 | 状态 |
| --- | --- | --- |
| server 主动通知 / 触发 | events & triggers，**签名 webhook** | OpenAI 9 月底在草案扩展上宣布；在协议 roadmap 上 |
| 长任务 | **Tasks extension**；FastMCP 用 `fastmcp[tasks]` | |
| 连接前发现 | **Server Cards** | 10 月初 final |
| 交互 UI | **MCP Apps** | 9 月改了打包，线协议没变 |

扩展机制本身 = 一个 `extensions` capability + 厂商前缀命名。⚠️ "细腰 + 长出四肢"（hourglass）这个图是**课程自己的比喻**，不是项目官方说法，要注明出处。

> 课堂补充：
>
> **deck p.71 · Act VI · Sampling —「The tool that borrowed the caller's brain」**（18:52，截图 `uploads/1852-p71-sampling.png`）
>
> - **sampling 是什么**：让 server 向**宿主（host）的模型**要一次补全——server 自己**不需要模型，也不需要 API key**；而且宿主能**看到并否决每一条 prompt**
> - **为什么活不下去**：它需要**在调用进行中**有一条回到 client 的通道（server → client 反向请求）——这正是 stateless turn 拿掉的东西
> - **现状**：已弃用（deprecated）；需要模型的 server **现在直接自己调模型**
> - *"What was lost is the host's view of the tool's prompts. That supervision now belongs to the gateway and the audit log."*（失去的是宿主对工具 prompt 的可见性；这份监督现在归 gateway 和审计日志）
> - *"Ledger row 5 · deprecations run on a twelve-month clock; someone must watch it."*（Decision Ledger 第 5 条：弃用按 12 个月时钟走，必须有人盯着）
> - 我的理解：
>   - **sampling 原本的两个好处**：① 省事——server 作者不用买模型、管 key，借用户的；② **安全**——宿主看得见 server 想让模型做什么，可以拦。弃用后 ① 变成 server 自己的成本，② 必须由别的盒子补上
>   - **监督从"宿主"搬到了"gateway + 审计日志"**——又是 p.65 的"状态 / 责任要显式搬家"：server 直接调模型时，它的出站请求要过 gateway（能看、能拦、能记），否则这份监督就**凭空消失**了
>   - **安全含义**：以前恶意 server 想让模型做坏事，prompt 要经过用户的宿主；现在它自己调模型，宿主完全看不到 → Door 10 / Act X 的威胁面变大了，**server 的出站网络和模型调用也要纳入 allowlist**
>   - **成本含义（接下午推理分享）**：每个需要模型的 MCP server 现在各自调模型 → 各自的上下文、各自的 KV cache，原来能在宿主那边共享的前缀没了；对自托管推理的团队，多了一类负载要算
>   - **Ledger 第 5 条 = 补丁节奏**："someone must watch it"——弃用时钟（Quiz 4：最早 2027-07-28 之后移除）不会自己提醒你，要有人负责看
> - 对 FinePrint：目前不用 sampling（✅）；如果以后要在 server 里用模型（比如总结退货原因），**直接调模型 + 记审计日志 + 走 gateway**，别依赖 sampling
>
> **deck p.72 · Act VI · The Other Cuts —「Deprecated, removed, reborn」**（18:54，截图 `uploads/1854-p72-deprecated-removed-reborn.png`）
>
> | 什么 | 状态 | 以后归哪 |
> | --- | --- | --- |
> | **Roots** | 弃用 | 范围（scope）属于**参数、配置和 sandbox** |
> | **Logging** | 弃用；`logging/setLevel` **删除** | 遥测归遥测（telemetry belongs to telemetry） |
> | **`ping`** | **直接删除** | 无状态请求不需要心跳（keep-alive） |
> | **Elicitation** | **还活着** | 改成**多轮请求**投递，不再靠推送 |
>
> - 四个动词对上 Quiz 6：**deprecated**（roots、logging）/ **removed**（ping、setLevel）/ **reborn = relocated**（elicitation）
> - 我的理解：每一条都是"**这件事本来就不该由协议的 session 管**"：
>   - **Roots**（client 告诉 server"你只能碰这几个目录"）：靠 server 自觉遵守的范围不是真的范围——**真正的边界是 sandbox**（"Labels request. Boxes enforce." 的又一例）；需要范围就放进**参数**（每次调用显式传）或**配置**
>   - **Logging**：日志应该走 OpenTelemetry 这类标准遥测管道，不该塞进 MCP 消息里；`setLevel` 是 client 远程调 server 日志级别——需要 session 才有意义
>   - **ping**：没有长连接就没有"连接还活着吗"这个问题
>   - **Elicitation**（server 中途问用户）：需求没变，投递方式变了——server 返回 `input_required`，client 问完用户再发同一调用（p.64 MRTR）→ ⚠️ 写操作要幂等（p.44 / p.67）；Hermes 没有 MRTR，所以在 Hermes 上暂时用不了
> - 对 FinePrint：
>   - 没用 roots / logging / ping（✅）；如果有"只能查某个店铺的订单"这种范围，放进**参数 + server 端校验**，不要指望 client 告诉你
>   - `request_return` 确认前预览 = 天然的 elicitation 场景：改用 `input_required` → client 确认 → 带同一 `idempotency_key` 再调
>
> **deck p.74 · Act VI · A Word on Words —「Deprecated is not dead」**（18:54，截图 `uploads/1854-p74-deprecated-not-dead.png`）
>
> - *"Until its clock runs out, a deprecated feature is still part of the specification; new work should not adopt it."*（时钟走完之前，弃用的特性仍是规范的一部分；但新工作不该再用它）
> - *"FastMCP 4 chose the stronger verb for its own API: `ctx.sample()` and `ctx.list_roots()` are gone from every protocol era."*（FastMCP 4 对自己的 API 用了更重的动词：`ctx.sample()` 和 `ctx.list_roots()` **在所有协议版本下都没了**）
> - 用词规范：**说 "elicitation survives; what went was the push."（elicitation 还在，没了的是推送）。永远别说 "elicitation was killed."**
> - 我的理解：
>   - **规范说"弃用"，库说"删除"**——同一个特性，两层给了不同的动词。这就是 Act VII **"规范 vs 实现：MUST 不是强制，库才是"** 的现场例子：你实际能不能用，取决于**你的库**，不是规范
>   - 对 FinePrint 的直接影响：`requirements.txt` 是 `fastmcp>=4.1` → **就算连一个还说旧协议的 client，也调不了 `ctx.sample()` / `ctx.list_roots()`**；FinePrint 本来没用（✅），但以后别在示例代码里照抄老教程
>   - 这一页和 Quiz 6 的答案是同一件事：removed / deprecated / relocated 三个动词要分清，讲给别人听时用错词会误导决策（比如以为 elicitation 不能用了，就去自己造一个问用户的机制）

---

## §7 · Act VII：The Bazaar and the Ledger（p.16）

**registry 登记的是名字，不是行为。**

| 数字 | 单位 / 主人 |
| --- | --- |
| ~44,000 | 官方 registry 条目（registry 仍是 preview，API v0.1；课程自己数的） |
| 124,267 | 17 个市场里的**唯一 server**（某调查） |
| 400 个 npm server 抽样 | 只有一半完成握手，超过 1/3 根本没启动 |
| "Tier-1 SDK 月下载近 5 亿" | 维护者原话、基金会转述；下载被 CI 放大，**不是用户数** |
| "ChatGPT 用户的 MCP 调用到 8 月是 1 月的 98 倍" | **基金会自己说的**，无方法论 |

规则：**每个数字都有单位；说出单位，否则别说。引用要带上主人。**

**同名不同 server**：8,900 个多版本 server 中 **40.6%** 悄悄改了宣称的能力 → 按内容钉工具列表的全部理由。本季度某厂商的 connector 开始返回一个"回传即钉住 server 工具"的列表。**Door 13 就是这个发现的真人版**。

> 课堂补充：
>
> **deck p.78 · Act VII · The Registry —「A registry of names, not of behavior」**（18:55，截图 `uploads/1855-p78-registry-names-not-behavior.png`）
>
> - 官方 **MCP Registry** 存的是**元数据**：每个 server 一个 `server.json`，用**反向 DNS 命名**（如 `io.github.xxx/...`），名字绑定到**验证过的 GitHub 账号或域名**
> - 各个 marketplace 从 registry 拉数据，再加自己的筛选（curation）
> - 还在**预览**阶段，路径是 `/v0.1/`
> - 核心句：*"A registry vouches for who published. Never for what the server does."*（registry 担保的是**谁发布的**，从不担保 **server 做什么**）
> - *"Ledger row 4 · every count needs a unit before it reaches a board slide."*（Decision Ledger 第 4 条：任何数字在上董事会 slide 之前都要带单位）
> - 我的理解：
>   - **身份 ≠ 行为**：registry 解决的是"这个 server 真是 xxx 发的吗"（防冒名），解决不了"它今天的工具描述和上个月一样吗""它会不会偷偷外传数据"——这正是上面 **40.6% 悄悄改能力**的问题：名字没变，行为变了
>   - 所以 Ledger 第 4 条"钉版本与来源"必须**按内容钉**：registry 给你来源可信，内容哈希给你行为不变；两个都要
>   - **"every count needs a unit"**：讲者在这一条里强调数字要带单位——像"registry 里有 N 个 server"这种数，要说清是独立 server 还是版本、是验证过的还是全部，否则在董事会上会被误读 → 候选技巧 #73（数字带单位、条件和主人）的原始出处；下午三星那页只给倍数就是反例
>   - `/v0.1/` 还在预览 → 生态类知识（Interlude §8），引用时标日期
> - 对 Forge AI 客户：给客户推荐第三方 MCP server 时，"在官方 registry 里"只说明**发布者是谁**，不等于安全；仍要过 allowlist + 按内容钉 + 定期复核
>
> **deck p.79 · Act VII · Census Hygiene —「Every count has a unit」**（18:56，截图 `uploads/1856-p79-every-count-has-unit.png`）
>
> **数的是什么**（What is counted）：
>
> | 数字 | 单位 | 出处 |
> | --- | --- | --- |
> | **约 44,000** | 官方 registry 的**条目（entries）** | 讲者自己查的，10 月 15 日 |
> | **124,267** | 17 个 marketplace 里的**去重 server** | MCPacific |
>
> **能用的是什么**（What works）——从 registry 抽 400 个 npm stdio server：
>
> | 结果 | 比例 | ≈ 个数（我算的） |
> | --- | --- | --- |
> | 完成握手 | **48.8%** | 195 |
> | 中间那段（slide 没标注） | **13.7%**（= 100 − 48.8 − 37.5） | 55 |
> | 根本没启动 | **37.5%** | 150 |
>
> - 另外：8,900 个多版本 registry server 里 **40.6%** 悄悄改了宣称的能力
> - 核心句：*"Entries are not servers, listings are not working servers, and a name is not a promise about tomorrow's tools."*（条目不是 server，上架不等于能用，名字不承诺明天的工具）
> - 我的理解：
>   - **三层折扣**：条目（一个 server 多个版本会算多条）→ 去重 server → 真正能跑的 server（抽样里**不到一半**能完成握手）→ 能力稳定的 server（多版本里四成会变）。每一层的"数"都不是同一个单位
>   - **44,000 和 124,267 不能直接比**：一个是**条目**，一个是**去重 server**，来源也不同（官方 registry vs 17 个 marketplace 汇总）——这页本身就在示范"别把两个不同单位的数放在一起比大小"
>   - **中间 13.7% 没标**：大概是"启动了但握手没完成"（崩溃、超时、协议不兼容）。我按 100% 倒算出来的，课上没讲，待确认
>   - **抽样限定**：只是 **npm + stdio** 的 400 个，不代表 HTTP 远程 server 或 Python server 的情况——引用时要带这个条件
>   - 这就是 **Ledger 第 4 条 / 候选 #73** 的完整示范：**数字 + 单位 + 来源 + 日期 + 抽样条件**。下午三星 p.43 只给倍数是反例，p.44 给了单位和条件是正例
> - 对 Forge AI 客户：别说"MCP 生态有 12 万个 server 可用"——准确说法是"17 个市场上约 12 万个去重 server（MCPacific），但抽样中 npm stdio server 只有约一半能完成握手"
>
> **deck p.80 · Act VII · The Ledger —「Numbers with their owners」**（18:59，截图 `uploads/1859-p80-numbers-with-owners.png`）
>
> | 说法 | 主人 | 问题 |
> | --- | --- | --- |
> | "Tier-1 SDK 的**月下载量**接近 5 亿" | 维护者（7 月）；AAIF（9 月） | **下载量被 CI 放大，不等于用户** |
> | "ChatGPT 用户发起的 MCP 工具调用到 8 月是 1 月的 **98 倍**" | **AAIF 的原话** | **没给方法** |
>
> - 核心句：*"Name the source and the unit, every time. That is how a number earns a slide."*（每次都说出来源和单位——一个数字就是这样挣到上 slide 的资格）
> - 我的理解：
>   - **下载量 ≠ 用户**：每次 CI 跑一遍 `npm install` / `pip install` 就算一次下载；一个团队一天跑几百次流水线，下载量就几百次——这个数能说明"被很多构建依赖"，不能说明"有很多人在用"
>   - **"98 倍"没有方法**：分母（1 月的水平）是多少？算的是调用次数还是活跃用户？包不包括自动化重试？——没有方法的倍数，和下午三星 p.43 只给倍数是同一种问题；p.44 补上绝对值以后才可信
>   - **主人还要看立场**：AAIF（Agentic AI Foundation）是 MCP 的托管方，维护者是 SDK 作者——两者都有动机报大数。这不是说数字错，而是说**引用时要连主人一起引**，让听的人自己打折
>   - 和 p.79 合起来是一套"数字卫生"：**单位**（条目 / 去重 server / 能用的 server）+ **主人**（谁说的、什么时候）+ **方法**（怎么数的）——三样缺一样，就不该上董事会 slide
>   - 候选 #73 正式版：**引用数字必带单位、主人、日期，倍数要带基数和方法**
> - 对 Forge AI：给客户 / 投资人讲"MCP 生态增长"时，用"AAIF 9 月称月下载量近 5 亿（含 CI，非用户数）"这种句式；别把"98 倍"当事实讲

---

## §8 · Interlude：深度的半衰期（p.16）

- **理解是订阅，不是购买**。今晚引用的报告写于 7 月 30 日（stateless 修订后两天）然后冻结；11 周里协议没动、生态在动，报告自己的勘误表已有 7 行，其中一行是对一个**其实还活着的特性**的"尸检"
- 深度从前沿向内衰减：**机制最先、生态最快、原理几乎不衰**
- 报告写成时的校准：概念 ~90% 完好，协议机制 ~70%，生态说法 ~20%
- 艾宾浩斯遗忘曲线的第二种读法：**一份文档的真实性曲线**。每个 cohort 前重跑一遍差距目录

> 对我：vault 里的 W0–W5 笔记、论文精读也会过期——"生态"类的句子要标日期。

> 课堂补充：
>
> **deck · Interlude · The Gradient —「Decay runs from the frontier inward」**（19:08，截图 `uploads/1908-interlude-gradient.png`）
>
> 同心圆，由外向内：
>
> | 圈 | 例子 | 衰减速度 |
> | --- | --- | --- |
> | **the frontier（前沿，最外圈）** | sampling、roots、the session | 最新、最巧；**几周内**就被弃用或删除 |
> | **the middle（中间）** | transports（传输方式）、authorization flows（授权流程） | **每个修订都重建**；按计划更新 |
> | **the core（核心，最内圈）** | **contracts：idempotency、politeness、the clean core**（契约：幂等、礼貌规则、干净的核心） | 老到无聊；**被证明是对的** |
>
> - 箭头：*decay runs from the frontier inward*（衰减从前沿向内走）
> - 底部句子（下半截被 Zoom 工具栏挡住，后半是我按上下文补的）：*"Principles outlive every surface they generate. Hold surfaces loosely and renew them on a [schedule; hold principles tightly …]"*（原理比它生出的每一个表层都活得久。表层要松松地拿着、按计划更新；原理要牢牢抓住）
> - 我的理解：
>   - **今天的课本身就是这张图的例子**：最外圈 sampling、roots、session 正好是 Act V–VI 刚被弃用 / 删除的东西；中间圈的传输和授权每个修订都在变（Act IV 五部宪法）；最内圈的**幂等**（Door 12）和**礼貌规则**（只返回下一步需要的）今天被反复验证
>   - 和讲义的三个数字对上：**概念（核心）~90% 完好 · 机制（中间）~70% · 生态（前沿）~20%**
>   - **对我做笔记的指导**：
>     - 核心类（幂等 key、label 四站、最小权限、先测再修）→ 写进 kit 当长期技巧，不用标日期
>     - 中间类（`protocol: stateless`、`_meta`、MRTR、Hermes 配置）→ 标**协议版本**（2026-07-28），下次修订时复查
>     - 前沿类（谁支持新协议的表、registry 数字、三星的产品、Cognos）→ **必须标日期**，过一两个月就要重查
>   - **和下午推理分享也对得上**：KV cache 要放哪层、Mooncake / Dynamo 这些产品是前沿；"状态要么便宜到能丢、要么贵到值得管理"、"先测命中率"是核心
>
> **deck p.87 · Interlude · Two Forgetting Curves —「Ebbinghaus, and the second decay」**（19:09，截图 `uploads/1909-p87-two-forgetting-curves.png`）
>
> - 艾宾浩斯测量了**事实怎样从脑子里淡去**，以及**复习怎样把它们找回来**
> - 一个变化很快的领域会再加**第二种衰减**：**事实本身在烂掉**——哪怕你记得一字不差
> - *"Re-reading your notes cures the first; only re-reading the world cures the second."*（重读笔记治第一种；只有重读世界才治第二种）
> - 核心句：*"Teach surfaces as perishables, dated. Teach principles as the pension."*（表层当成易腐品来教，标上日期；原理当成养老金来教）
> - 我的理解：
>   - **两条曲线**：① **我忘了**（记忆衰减）→ 复习笔记；② **笔记过期了**（事实衰减）→ 回去查原始来源。第二种更危险，因为你**记得很清楚、很自信**，但记的已经不对了——比如 p.66 那张支持表，一个月后再背出来就是错的
>   - "perishables"（易腐品）vs "pension"（养老金）：表层知识像牛奶，有保质期；原理像养老金，越存越值钱
>   - **对我这套 vault 的具体做法**：
>     - 前沿 / 生态类句子带日期（如"截至 2026-10 中"）——今天 summary 和 notes 里大多已经这样写了
>     - 每次开新的一周前，挑上周笔记里**标了日期**的条目，回原始来源（changelog、registry、GitHub）复核一遍，不只是重读自己的笔记
>     - 核心原理（幂等、label 四站、最小权限、先测再修）进 kit，不需要复核日期
>   - 这也是讲义里说的"**每个 cohort 前重跑一遍差距目录**"——讲者自己就是这样维护这门课的

---

## §9 · Act VIII：两条轴，不是梯子（p.17）

夏天教的是一架梯子：mount → search → code → skill。本季度证据说这是**两条独立的轴**：

| 轴 | 取值 |
| --- | --- |
| **模型看见什么** | 全部挂载（mounted）/ 延迟加载藏在搜索后（deferred）/ 按需搜索（searched） |
| **模型怎么调用** | 直接（direct）/ 通过它写的代码（code）/ 通过 shell（bash） |

- deferral 本季度成了所有大 harness 的默认：Claude Code 一个 flag 就把整个 server 的工具藏到搜索后面；Hermes 只要有可延迟的工具就把 MCP 工具藏在 **3 个 bridge 工具**后面；两大厂 API 都有 `defer_loading` + 搜索工具；协议成立了 Progressive Disclosure 工作组
- **Hermes 默认位置：看见 = deferred，调用 = direct**（⚠️ p.90 修正：deck 把 Hermes 默认的三个 bridge 工具放在 **searched × direct**）。课上会在 Door 5 打开 tool search 重放 → 第一条轴当场移动（"当晚最好的揭晓"）

**bash 结果（最强也最不舒服的证据）**：60 个工具的办公 benchmark 上，前沿模型 typed tools ~45%，**只用 bash ~68%**，bash 上再加 typed tools "没有可检测到的合并得分提升"（MS Research + CMU, *Is Bash All You Need?*）。
- 注意 caveat：目录是作者自己建的；他们自己的建议是**能 sandbox 的地方用 bash，合规要求固定目录的地方用固定目录**
- **对照（Willison, 7/31）**：MCP 工具"更容易审计和控制"，敏感应用里他会更多倚重 MCP
- 问题从"MCP 还是 CLI？"变成：**模型看见多少工具？直接调还是通过代码调？**

**成本说法要小心**：一项研究里 MCP vs CLI 配对成本比从 <0.5 到 29 倍；框架比接口影响更大。**不存在一个"MCP 贵 N 倍"的数字**。

> 课堂补充（Door 5 tool search on 的现场结果）：
>
> **deck p.90 · Act VIII · The Grid —「Two questions with independent answers」**（19:13，截图 `uploads/1913-p90-the-grid.png`）
>
> 纵轴 = **模型看见什么**（what the model sees），横轴 = **模型怎么调用**（how the model calls）：
>
> | | **direct**（每轮一次工具调用） | **code**（写程序调工具） | **bash**（对 CLI 发命令） |
> | --- | --- | --- | --- |
> | **mounted**（工具列表里有全部定义） | **扁平工具箱**：Hermes 关掉 tool search = **我们的 lab** | **programmatic tool calling**：Anthropic 用 Python、不能调 connector 工具；OpenAI 用 JavaScript、允许调 MCP 工具 | **在协议之外**：模型读 `--help`，不读 schema（Cloudflare 的 `cf` CLI；"Is Bash All You Need?"）——这一列三行合并 |
> | **deferred**（现在给名字，搜索时才给定义） | `defer_loading` + search（Anthropic、OpenAI）；Claude Code：`alwaysLoad: false` | 先搜索，再让程序调用搜索加载进来的工具 | ↑ |
> | **searched**（目录藏在元工具后面） | **Hermes 默认：三个 bridge 工具**；PayPal 的 SCOUT：两个元工具 | **code-mode server**：先搜索，再执行 | ↑ |
>
> - 核心句：*"The ladder was one path through a three-by-three grid. Placements as of October 2026."*（夏天讲的"梯子"只是 3×3 网格里的一条路径；格子里的位置截至 2026 年 10 月）
> - ⚠️ **修正我课前的笔记**：我写的是"Hermes 默认 = deferred + direct"，deck 把 Hermes 默认放在 **searched × direct**（三个 bridge 工具 = 目录藏在元工具后面），而 deferred 那行是 Anthropic / OpenAI 的 `defer_loading` 和 Claude Code 的 `alwaysLoad: false`。**区别**：deferred = 模型**已经看到工具名**，只是定义晚到；searched = 模型**连名字都看不到**，只看到几个"搜索 / 加载 / 调用"的元工具
> - 我的理解：
>   - **两条轴是独立的**：能不能看见（上下文成本）和怎么调用（执行方式）可以任意组合。夏天的梯子 mount → search → code → skill 只是沿对角线走的一条路
>   - **bash 那列在协议之外**：模型不读 JSON schema，读 `--help`。所以 label 的四站（description / schema / error / contract）在这一列**换成了 CLI 的帮助文本和退出码**——同样的原则，不同的表面（呼应刚才 Interlude："原理比表层活得久"）
>   - **对 label 写法的影响**：
>     - mounted：模型同时看到所有工具 → 描述要**点名邻居**（Door 3）
>     - deferred：模型先看到名字 → **名字要能说明用途**（#65 改名 = breaking change 更重要）
>     - searched：模型要先**搜到**才能选 → description 要包含用户会用的**关键词**（板书 12:03："label 要先赢搜索再赢选择"）
>   - **和推理分享的连线**：mounted 让 prompt 前缀最长但最稳定（prefix cache 友好）；searched 前缀短，但每轮按需拉进来的定义会让前缀变化——便宜和可缓存之间又是一个取舍
>   - **Placements as of October 2026**：格子本身是核心（原理），每个格子里填的是谁属于前沿（生态）→ 引用时标日期
>
> **deck · Act VIII · The Uncomfortable Result —「Is bash all you need?」**（19:21，截图 `uploads/1921-p9x-is-bash-all-you-need.png`）
>
> TheAgentCompany 上的**任务完成率**（作者自建 60 个工具的 typed 目录）：
>
> | 调用方式 | Opus-4.8 | GPT-5.5 |
> | --- | --- | --- |
> | **typed tools**（MCP 式类型化工具） | 44.9% | 45.3% |
> | **bash alone**（只用 bash） | **69.4%** | **67.1%** |
> | **programmatic tool calling**（写程序调 typed tools） | 52.9% | 45.1% |
>
> - 出处：**arXiv `2609.11999`（Microsoft 和 CMU）**：在 bash 上再加 typed tools，*"no detectable pooled score gain"*（合并得分没有可检测到的提升）
> - 底部警示（下半截被遮，按讲义补）：*"One benchmark, and a catalog the authors built themselves."*（只是一个 benchmark，而且目录是作者自己建的）
> - 我的理解：
>   - **差距很大**：bash 比 typed tools 高约 **22–24 个百分点**，两个模型方向一致；programmatic tool calling 对 Opus 有 +8 点，对 GPT 基本没变 → 写代码调工具的收益**因模型而异**（又一次 DocsChisel 式的"随模型翻转"）
>   - **可能的原因**（我的推测，不是论文结论）：① 模型训练数据里有海量 shell 用法，`--help` + 管道是它们最熟的"工具接口"；② bash 天然可组合（`grep | sort | head`），一条命令顶好几轮 direct 调用；③ **作者自建的 60 个 typed 工具未必写得好**——如果 label 有今天门 1–4 那些毛病，typed tools 的分数被压低是 label 的锅，不是 typed 本身的锅
>   - **这页本身是 #73 的正例**：单位（任务完成率）、主人（MS + CMU，arXiv 号）、条件（TheAgentCompany、60 个自建工具、两个模型）、局限（一个 benchmark、自建目录）——全都写了
>   - **讲义里的对照**：作者自己建议"**能 sandbox 的地方用 bash；合规要求固定目录的地方用固定目录**"；Willison（7/31）：MCP 工具"**更容易审计和控制**"
> - **对 Forge AI / FinePrint 的取舍**：
>   - **退款、改订单这种有钱、有副作用的动作** → typed tools：能做 allowlist、幂等 key、`readOnlyHint`、审计日志（bash 里一条命令能做什么很难事先限定）
>   - **查数据、翻日志、批量整理这种探索性工作** → 给 sandbox 里的 bash，可能更快更准
>   - 不是"MCP 还是 CLI"二选一，而是 p.90 网格里**按风险选格子**
>
> **deck p.95 · Act VIII · The Debate Converges —「CLIs, code, and the question that moved」**（19:25，截图 `uploads/1925-p95-debate-converges.png`）
>
> - **Cloudflare 的 `cf` CLI（9 月 28 日）**：*"Last week, agent usage reached 48%"* of Wrangler use（上周 agent 的使用占到 Wrangler 使用量的 48%）；*"Agents love CLIs."*
> - **Armin Ronacher（10 月 6 日）**：codemode *"basically just a way to issue tool calls from within some language"*（code mode 本质上只是在某种语言里发起工具调用）；*"bash … can only compose programs that run"*（bash 只能组合那些能跑起来的程序）
> - 核心句：*"Not 'MCP or CLI?' but: how many tools does the model see, and does it call them directly or through code?"*（问题不是"MCP 还是 CLI"，而是：模型看见多少工具？直接调，还是通过代码调？）——就是 p.90 网格的两条轴
> - 我的理解：
>   - **Ronacher 的两句话把 code 和 bash 统一了**：两者都是"让模型写程序来组合能力"，区别只在**能组合什么**——code mode 组合的是**工具**（MCP / typed），bash 组合的是**已经存在的程序**（CLI）。所以 p.90 里 code 和 bash 是相邻的两列，不是对立的两派
>   - **"48%" 带单位读**（#73）：是 **Wrangler 使用量**的 48%，不是 48% 的用户，也不是 48% 的 Cloudflare 流量；主人是 Cloudflare 自己，时间是 9 月最后一周
>   - **辩论为什么"收敛"**：大家吵了一年"MCP 还是 CLI"，结果发现两边说的是同一件事的不同格子。真正要决定的是两条轴上的位置，而且**按场景选**（上一页的取舍：有副作用 → typed + 可审计；探索性 → sandbox 里的 bash / code）
> - 对我：以后有人（客户、同事）问"我们该用 MCP 还是 CLI"，就把问题改写成这两个：①工具多到要不要藏在搜索后面？②要不要让模型写代码批量调用？再加第三个：③这个动作出错的代价有多大（决定 typed 还是 bash）
>
> **deck p.96 · Act VIII · Pop Quiz —「Quiz 8 — Place it on the grid」**（19:25，截图 `uploads/1925-p96-quiz8-place-on-grid.png`）
>
> - 题目：三种配置——① PayPal 在 2,000 个工具上放两个元工具；② Claude Code 配 `alwaysLoad: false`；③ OpenAI 在 V8 里跑程序调 MCP 工具。把每个放到 3×3 网格上，然后复述：为什么这是两条轴而不是一架梯子？
> - 我的答案（按 p.90 网格，等官方答案核对）：
>
> | 配置 | 看见什么（行） | 怎么调用（列） |
> | --- | --- | --- |
> | ① PayPal 两个元工具 | **searched**（目录藏在元工具后面） | **direct** |
> | ② Claude Code `alwaysLoad: false` | **deferred**（先给名字，定义按需加载） | **direct** |
> | ③ OpenAI V8 程序调 MCP 工具 | **mounted**（工具定义都给程序用） | **code**（programmatic tool calling） |
>
> - **为什么是两条轴**：
>   - ① 和 ② 在**同一列**（都是 direct），却在**不同行**——只改了"看见什么"，"怎么调用"没变
>   - ③ 在**第一行**（mounted，和最原始的扁平工具箱一样），却在 **code 列**——它跳过了梯子上的"search"那一级，直接到了"code"
>   - 如果是梯子，往上走一级就必须先经过下一级，而且两件事绑在一起变；这三个例子说明两件事**可以分别改、互不依赖**——梯子只是网格里沿对角线走的一条路

---

## §10 · Act IX：Procedure 走线上（p.17–18）

组合现在是双向的：W3 教的是 skill 包工具；9 月起反方向成为协议——**tool server 通过 `skills/list`、`skills/get` 发 skill**，格式完全交给 Agent Skills 规范。

扩展里那句话就是协议层面的整个 W3：
> "reading a SKILL.md via `resources/read` does not by itself activate the skill."

harness 仍然组装；模型仍然提议；harness 仍然处置。W3 的 Zara 日历 skill 明天就能由 MCP server 发出——而**manifest 先于任何文件到达**，那正是读一个陌生人 skill 应该开始的地方。

客户端支持：1 个完整、3 个部分，SDK 支持还在实现。各厂同季度同方向：skills API、携带 skill 的 sandbox、某框架第一次实现 skill 卸载。

> 对我：W3 的 `when-the-time-is-right` skill 可以试着用 FastMCP 通过 `skills/list` 发出来（等 FastMCP 支持）。

> 课堂补充：
>
> **deck p.99 · Act IX · The Boundary —「Access and procedure」**（19:27，截图 `uploads/1927-p99-access-and-procedure.png`）
>
> - **Anthropic 自己的一句话测试（2025 年 12 月）**：*"If you're explaining how to do something, that's a skill. If you need Claude to access something, that's MCP."*（如果你在解释**怎么做**某件事，那是 skill；如果你需要 Claude **访问**某样东西，那是 MCP）
> - **组合是多对多**：一个 skill 可以用好几个 server，一个 server 可以服务好几个 skill
> - 核心句：**MCP grants access; skills supply procedure.**（MCP 给访问权，skill 给做法）
> - *"Ledger row 1 · a server can now ship procedure with access: who reviews the procedure?"*（Decision Ledger 第 1 条：server 现在能把做法和访问权一起发过来——谁来审这个做法？）
> - 我的理解：
>   - **用今天的店举例**：`refund_transaction`、`add_store_credit` 是 **access**（能动钱）；"先给积分、退卡要加 $15、手续费别跟顾客提"这套店规是 **procedure**（怎么做）。今天在门里我把店规写进了 tool 的 description——其实那部分更适合放在 skill 里
>   - **W3 → W6 的线**：W3 我写的日历 skill 是 procedure（怎么判断"哪个周四"），它调用的日历工具是 access。门 2 *Which Thursday?* 是同一个问题的工具版
>   - **为什么是 Ledger 第 1 条（allowlist）的新问题**：以前 allowlist 只审"这个 server 能访问什么"；现在 server 可以通过 `skills/list` 顺便发 skill 过来，等于**陌生人既给了你钥匙，又给了你一本操作手册**。手册里如果写着"遇到 X 就调 Y"，模型会照做——**审 access 不够，还要审 procedure**
>   - 和 Door 10 / Act X 的威胁一致：手册（skill）和注入走同一个通道（模型读的文本）；讲义那句 *"reading a SKILL.md via `resources/read` does not by itself activate the skill"* 就是一道闸：**读到不等于启用**，启用要 harness 决定
> - 对我：
>   - **FinePrint**：`request_return` 是 access；"先确认、再预览、退款还是换货的判断规则"应该写成一个 skill，而不是全塞进 docstring
>   - **Forge AI 客户**：给客户接第三方 server 时，问两件事——它能访问什么（access）？它有没有附带 skill（procedure）、谁审过？
>
> **deck p.100 · Act IX · Both Directions —「Composition runs both ways」**（19:28，截图 `uploads/1928-p100-composition-both-ways.png`）
>
> ```text
>  a skill（procedure：什么时候、按什么顺序、怎么检查）
>      ── 点名并调用它的工具 ──▶            （Week 3、4：skill 包住工具）
>      ◀── 把 skill 当作 resource 发出来 ──  （9 月起：SEP-2640）
>  an MCP server（access：触及真实世界的工具）
> ```
>
> - 例子：`skill://acme/billing/refunds/SKILL.md`：*"Process customer refund requests per company policy"*（按公司政策处理顾客退款请求）
> - 核心句：*"SEP-2640's own running example is a refunds skill. The Stranger's Toolbox could now serve its house rules beside its tools."*（SEP-2640 自己的例子就是一个退款 skill；Stranger's Toolbox 现在可以把店规和工具放在一起发出来）
> - 我的理解：
>   - **两个方向**：
>     - **skill → server**（W3、W4 教的）：skill 里写"先调 `search_orders`，再判断，再调 `add_store_credit`"——skill 是调用方，工具是被调方
>     - **server → skill**（SEP-2640，9 月 final）：server 通过 `skills/list` / `skills/get`，把 SKILL.md 当 resource 发给 client——server 不只给工具，还顺便给"怎么用这些工具"的手册
>   - **和今天门的关系，讲者点得很明白**：门 1 那条"先给积分、退卡多付 $15、别跟顾客提手续费"，我是硬写进 `add_store_credit` 的 description 里的。按 SEP-2640，这些**店规本该是一个 refunds skill**，和工具一起由 server 发出——description 只管"这个工具做什么、何时不用、代价"，**跨工具的流程和政策**放在 skill 里
>   - **为什么这样更好**：① 店规改了只改一个 SKILL.md，不用改每个工具的描述；② 工具描述变短，挂载 / 搜索时 token 更少（接下午推理分享：前缀更短、更稳定）；③ 政策可以单独审（上一页 Ledger 第 1 条"谁来审 procedure"）
>   - **风险同上一页**：server 发来的 skill = 陌生人给的操作手册；读到 ≠ 启用，由 harness 决定是否启用
> - 对我：
>   - **门的课后实验**：把门 1–4 里写进 description 的店规抽出来，写成一个 `refunds` SKILL.md；比较"规则写在 description 里"和"规则在 skill 里 + description 精简"两种做法的 Verify 分数
>   - **FinePrint**：同样拆成 `request_return`（access）+ `returns-policy` skill（procedure），等 FastMCP 支持 `skills/list` 后由 server 发出
>
> **deck p.102 · Act IX · What the Listing Carries —「A manifest before a single file」**（19:34，截图 `uploads/1934-p102-manifest-before-file.png`）
>
> - 每条 `skills/list` 条目带着：skill 的 **frontmatter 原文**（verbatim），以及**每个文件的 URI、SHA-256 摘要和大小**
> - **每个 skill 的上限**：**512 个 resource、16 MiB**
> - *"A host can budget and approve a skill without fetching it."*（宿主**不用下载**就能估算成本、审批这个 skill）
> - 引文（SEP-2640）：*"Digests are unsigned … A match proves the two are consistent, not that either is trustworthy."*（摘要没有签名……对上了只证明两者**一致**，不证明任何一方**可信**）
> - 我的理解：
>   - **manifest 先到的好处**：harness 先看清单——有几个文件、多大、frontmatter 里 `description` 写了什么——再决定要不要取、要不要启用。对应讲义那句"**manifest 先于任何文件到达，那正是读一个陌生人 skill 应该开始的地方**"；也是 W3 教的"先读 frontmatter 再决定加载"
>   - **"budget"有两层**：① 下载 / 存储（16 MiB 上限）；② **上下文**——skill 启用后会进 prompt，算 token 和 KV cache（接下午推理分享）
>   - **SHA-256 证明什么、不证明什么**：
>     - 证明：你后来取到的文件，和清单上写的**是同一份**（没被中途改、没取错）——**完整性**
>     - 不证明：这份清单和文件本身**是好的**——因为清单和文件都来自**同一个 server**，它想作恶时两边一起改，摘要照样对得上。没有签名就没有**真实性**
>   - **同一个道理今天第三次出现**：
>     - Act VII registry：担保**谁发布**，不担保**做什么**
>     - 下午 Mooncake：chunk ID 由内容算出 → 证明是**同一段前缀**，不证明前缀内容对不对
>     - 这里：摘要对上 → 证明**一致**，不证明**可信**
>     - → **身份 / 一致性 ≠ 可信**；可信要靠审（Ledger 第 1 条"谁来审 procedure"）+ 按内容钉住审过的版本（摘要正好拿来钉：审过的 SHA-256 记进 allowlist，变了就重审）
> - 对我：给 Forge AI 客户接第三方 skill 时，**把审过的 skill 的 SHA-256 记进 allowlist**——摘要不能证明 skill 好，但能证明"还是我审过的那一份"
>
> **deck p.103 · Act IX · Reading Is Not Activating —「The harness still disposes」**（19:37，截图 `uploads/1937-p103-harness-disposes.png`）
>
> - SEP-2640 原文：*"Reading a SKILL.md via resources/read does not by itself activate the skill. resources/read is transport."*（通过 `resources/read` 读到 SKILL.md，本身**不等于启用**这个 skill；`resources/read` 只是**传输**）
> - **审批按 skill 逐个进行**；启用一个**嵌套的** skill（skill 里引用的另一个 skill）**需要重新征得同意**
> - 核心句：*"Harness assembles, model proposes, harness disposes: Week 3's loop, written into a protocol."*（harness 组装，模型提议，harness 处置——W3 的那个循环，被写进了协议）
> - 我的理解：
>   - **"传输"和"启用"分开**：拿到文件只是把字节搬过来；要不要把它当成**指令**放进模型的上下文，是 harness 的决定。这正是上一页"摘要证明一致不证明可信"之后的那道闸——**没审过就不启用**
>   - **嵌套要重新同意**：防止"审过一个无害的 skill，它再偷偷拉进一个没审过的 skill"——和 Door 13 Turncoat（工具列表中途变了）是同一类攻击：**信任不能沿着引用自动传递**
>   - **W3 循环**：harness 组装（决定给模型看什么 skill / 工具）→ 模型提议（"我想用这个 skill / 调这个工具"）→ harness 处置（批准、拒绝、要用户确认）。模型从来**不直接**决定执行什么——这就是 "Labels request. Boxes enforce." 在 skill 层的版本
>   - 也对上 Door 10 *Helpful Stranger*：工具结果、SKILL.md 都是**文本**，模型会读，但读到的东西只是**数据**；把它升级成**指令**的权力在 harness
> - 对我：
>   - **W3 的日历 skill**：如果以后由 MCP server 发出，harness 要做三件事——看 manifest（frontmatter、文件、大小、SHA-256）→ 按 skill 审批 → 启用；里面如果引用别的 skill，单独再批
>   - **Forge AI 客户部署**：harness 配置里明确"哪些 skill 自动启用、哪些需要人审"，嵌套引用一律走审批

---

## §11 · Act X：When the Boxes Fail Open（p.18–19）

**四个盒子：registry、gateway、harness、sandbox。label 只能请求，盒子才强制。本季度推论：盒子也会 fail open，恰恰在它本该强制的那个点。** 每个盒子一个案例：

| 盒子 | 案例 | 发生了什么 | 教训 |
| --- | --- | --- | --- |
| **Gateway** | LiteLLM **CVE-2026-59822**（Wiz, 9/9） | MCP 端点的 OAuth 透传把失败的 key 检查替换成一个空的已认证用户 → 任何伪造 bearer token 都能开 session。9/2 进 CISA KEV，一周后被串成云凭证盗窃 | 是 KEV 上**唯一描述里点名 MCP 的条目**（不是"第一个"） |
| **Auth（库）** | 参考 SDK 落后规范 9–10 周 | Python client 在回退路径跳过 issuer 检查、没把凭证绑到 server（9/28 修）；TypeScript client 会把存的 refresh token 和 client secret 发给 MCP server 指定的任意授权服务器（9/30 advisory） | **规范的 MUST 不是强制，客户端库才是** |
| **Harness** | **ChainDrop** npm 蠕虫（MS Security, 8/4） | 通过 `.claude/settings.json` 的 SessionStart hook 和 `.vscode/tasks.json` 的打开文件夹任务持久化：开 session 就重跑，无需安装 | **项目级 agent 配置就是代码** |
| **Registry** | **Plugin4Shell**（Air Security, 9/17）；**Deadbugz** | 市场钉了 commit SHA 但没有 harness 验证 → 以 SHA 命名的分支被检出；Deadbugz：74 分钟 23 个 PR 加了一个调用 3 次后变坏的远程端点 | **钉了没人查就不算钉** |
| **Sandbox** | Atlassian connector | Jira 工单里的注入让 connector 把 `/proc/self/environ` 上传到 Confluence，因为 `file_path` 直接进了 `open()` | 路径参数不能直通文件系统 |

**扫描器是证据不是信任**：9 月测试中两个能用的恶意 server 躲过了大多数扫描器；唯一抓到的那个被"把文件填充超过大小上限"绕过；有一招是**工具结果里的注入——没有扫描器检查结果**。一个拆分在 description、result、sampling 三个通道的注入，从单通道都能防住的模型里偷出了数据。**Door 10 就是这个。**

要知道的两份文档：
- **CoSAI MCP Security**（四个保证级别）
- **OWASP Top 10 for LLM Apps 2026**：Excessive Agency 升到第 3；新条目 "Hidden Context Exposure" 明确包括**应用暴露给模型的工具 schema**

防御也在进步：fail-closed 的企业 allowlist；从 stateless 头部检测 shadow MCP（**原来是送给 gateway 的礼物**）。

> 课堂补充：
>
> **deck · Act X · 2026 Case Law —「One case per box」**（19:37，截图 `uploads/1937-act10-one-case-per-box.png`）
>
> | 盒子 | 管什么 | 案例 | 一句话 |
> | --- | --- | --- | --- |
> | **gateway** | 流量路径上的策略 | **LiteLLM，CVE-2026-59822** | 失败的 key 检查**退回成了一个空身份** |
> | **auth** | 身份、issuer、audience | **官方 SDK 的 OAuth client** | 规范新加的 MUST，**几周没人强制** |
> | **harness** | agent 被允许做什么 | **ChainDrop 蠕虫** | 通过**项目级 agent 设置**持久化 |
> | **registry** | 谁发布的、哪个版本 | **Plugin4Shell；Deadbugz** | **钉了没人查**；一个 server **变坏了** |
>
> - 核心句：*"Last year we taught threat models. This year we can teach case law, one case per box."*（去年教威胁模型，今年可以教判例了，每个盒子一个案例）
> - ⚠️ 和讲义的差异：讲义的四个盒子是 registry / gateway / harness / **sandbox**；这页 deck 是 gateway / **auth** / harness / registry——**auth 单独成了一个盒子**，sandbox 那个 Atlassian `/proc/self/environ` 案例没上这页（可能在后面单独讲）
> - 我的理解：
>   - **每个案例都是"盒子在它该拦的地方放行了"**（fail open）：
>     - gateway：认证**失败**时没有拒绝，而是给了一个"空的已认证用户"→ 失败变成了通过。正确做法是 **fail closed**：检查失败 = 拒绝
>     - auth：规范写了 MUST（比如校验 issuer），但官方库没实现 → 用库的人以为有保护，其实没有（Act VII"MUST 不是强制，库才是"）
>     - harness：`.claude/settings.json` 的 SessionStart hook、`.vscode/tasks.json` 被当成"配置"而不是"代码"，没人审 → 打开项目就执行（候选 #71）
>     - registry：钉了 commit SHA，但 harness 不验证 → 以 SHA 命名的**分支**被检出；Deadbugz 是 server 调用 3 次后才变坏 → 一次性审查抓不到（候选 #70 要**定期**校验）
>   - **"判例"的意思**：不再是"理论上可能被攻击"，而是"今年真的发生了，日期、编号、谁发现的都有"——又是 #73 的风格：每个案例都带主人（Wiz、MS Security、Air Security）和日期
>   - **和今天门的对应**：Door 10 Helpful Stranger（结果里的注入 → harness / toolset）、Door 13 Turncoat（server 中途变坏 → registry / 按内容钉）
> - 对 Forge AI 客户部署（四个盒子各问一句）：
>   - gateway：认证失败时是拒绝还是放行？（要 fail closed）
>   - auth：用的 SDK 版本修了 issuer 检查和 token 外发的 advisory 没有？
>   - harness：仓库里的 `.claude/`、`.vscode/` 配置有没有走代码审查？
>   - registry：钉的版本**谁在定期查**？变了会不会报警？
>
> **deck p.113 · Act X · The Registry · 2 of 2 —「A server that turned」**（19:40，截图 `uploads/1940-p113-server-that-turned.png`）
>
> - 一个**通过了审查**的 server，可能在**第三次调用**时变坏
> - **Deadbugz**（**Pillar Security，2026 年 8 月**）：**74 分钟内 23 个 PR**，其中 **17 个**加了一个远程 MCP endpoint——这个 endpoint 在**三次工具调用之后**切换成**窃取凭证的指令**。**一个都没被合并**
> - 核心句：*"Approved on Monday is not the same server on Tuesday. Pin, and watch for change."*（周一批准的，不是周二那台 server。钉住，并盯着变化）
> - 修正讲义笔记：Deadbugz 的发现方是 **Pillar Security**、时间 8 月；17/23 个 PR 带恶意 endpoint（讲义只写了 23 个 PR）
> - 我的理解：
>   - **为什么"第三次调用"才变坏**：审查者通常只试一两次——前两次表现正常就放行了。这是专门针对**一次性审查**设计的：**行为随调用次数变化**，静态看代码 / 看工具列表都看不出来（远程 endpoint 的代码根本不在 PR 里）
>   - **远程 endpoint 的风险**：PR 里只是加了一行 URL，真正的行为在别人的服务器上，**随时可以改**——这就是 Door 13 Turncoat 和"40.6% 悄悄改了能力"的极端版
>   - **"None was merged"**：这次被挡住了（大概靠人工审查 PR 时对陌生远程 endpoint 起了疑心），但说明攻击是**批量、自动化**的（74 分钟 23 个）
>   - **"Pin, and watch for change"两件事缺一不可**：
>     - 钉：按内容哈希钉住工具列表 / description / server 版本（Act VII）
>     - 盯：**每次调用**都比较实际返回的工具列表和描述是否还和钉住的一致；对**远程** endpoint 尤其要盯——它的内容不在你的仓库里
>   - 和门的关系：**Door 13 Turncoat**（~15:20 TA 打开）就是这个案例的练习版——还没做
> - 对 Forge AI / FinePrint：
>   - 客户仓库的 PR 里出现**新的远程 MCP endpoint URL**，要当成高风险变更单独审
>   - harness 侧：工具列表哈希变了 → 停用 + 报警，而不是继续调用
>
> **deck p.114 · Act X · The Standards Caught Up —「Two documents to know」**（19:43，截图 `uploads/1943-p114-two-documents.png`）
>
> | 标准 | 说了什么 |
> | --- | --- |
> | **CoSAI MCP Security v2.0**（2026-08-12） | 四个保证级别：**L1 Sandbox、L2 Internal、L3 Production、L4 Regulated** |
> | **OWASP Top 10 for LLM Apps 2026** | **Excessive Agency**（权限过度）从第 6 升到**第 3** |
> | **OWASP 新增 LLM08** | **Hidden Context Exposure**（隐藏上下文暴露）明确包括 *"the schemas of tools and functions the application exposes to the model"*（应用暴露给模型的工具和函数的 schema） |
>
> - 核心句：*"Your schema is a prompt, and also an exposure."*（你的 schema 是一个 prompt，同时也是一个暴露面）
> - 我的理解：
>   - **CoSAI 四级**对应部署的认真程度：L1 沙箱实验 → L2 公司内部 → L3 面向生产 → L4 受监管行业。deck p.16 补充过：**L3、L4 要求中央 gateway**——也就是 Decision Ledger 第 2 条
>   - **Excessive Agency 升到第 3**：agent 被给了超过任务需要的权限 / 工具 / 自主度。今天的对策全在这：最小权限、allowlist、有副作用的动作用 typed tools、读到 ≠ 启用
>   - **LLM08 最有意思**：今天一整天都在说"schema 是 prompt，写好它模型才会用对"（label 四站）；OWASP 补上另一面——**schema 也会把内部信息暴露给模型**（以及能读模型上下文的人 / 注入）：内部字段名、隐藏的后台工具、参数取值范围、系统结构。门里那些"隐藏但存在的工具"（`delivery_windows`、`lookup_orders`）就是例子：放出来帮了模型，也扩大了暴露面
>   - **两面兼顾**：只暴露当前任务需要的工具和字段（礼貌规则用在 schema 上）；description 里别写内部系统名、密钥位置、其他租户信息
> - 对 Forge AI 客户：
>   - 部署前先定 CoSAI 级别（多数中小客户的生产 agent 是 **L3** → 要中央 gateway）
>   - 审 tool schema 时加一条："这个字段 / 这个工具暴露给模型，有没有泄露不该泄露的东西？"
>
> **课上追问整理（19:44–19:47）：对我们自己开发 agent 的指导**
>
> - **CoSAI** = Coalition for Secure AI（2024-07，Google 牵头，OASIS Open 托管，主要 AI 厂商都在）；**OWASP** = Open Worldwide Application Security Project（2001 年起的非营利组织，Top 10 最出名）。OWASP 列"有哪些风险"，CoSAI 定"不同场景要做到什么程度"（成员 / 年份凭记忆，引用前去官网核对）
> - **要不要自己写 MCP**：只给自己的 agent 用 → function calling 就够；多宿主 / 多团队 / 对外开放 → MCP；通用 SaaS 用官方 server（allowlist + 钉 + 复查）；**客户内部系统、会动钱和数据的动作 → 自己写一个薄 server**；流程写成 skill；探索性任务给 sandbox 里的 bash
> - **开发清单**：
>   1. **先定 CoSAI 级别**：demo = L1 · 内部 = L2 · 给客户 / 生产 = **L3（要中央 gateway：鉴权、allowlist、审计日志）** · 受监管 = L4
>   2. **最小权限（OWASP #3 Excessive Agency）**：只挂任务需要的工具；能只读就只读并标 `readOnlyHint`；动钱的用 typed + idempotency key + 审计；高风险加人工确认；第三方 skill / server 审过再启用
>   3. **schema 只暴露该暴露的（LLM08）**：description 不写内部系统名 / 表名 / 密钥位置 / 其他客户；租户 ID、权限这类字段由 server 补，不让模型填；返回值也守礼貌规则
>   4. **交付文档写依据**："按 CoSAI L3 设计，对照 OWASP LLM Top 10 2026，重点防 Excessive Agency 和 Hidden Context Exposure"
>
> **deck p.116 · Act X · Pop Quiz —「Quiz 10 — answered」**（19:47，截图 `uploads/1947-p116-quiz10-answered.png`）
>
> - 题目（p.115，没截到，按答案推断）：三起事件各自是哪个盒子失守？
> - 答案：
>   - **LiteLLM → gateway**
>   - **Plugin4Shell → registry 和 harness 一起**：钉（pin）放在市场（registry）里，缺的那道检查在 harness 里
>   - **ChainDrop → harness**
>   - *"Each box existed. Each failed open, at the exact point meant to enforce."*（每个盒子都在；每个都在它本该强制的那个点放行了）
> - 核心句：*"The architecture carries trust, and it fails like any other code. Test the boxes, not just the tools."*（信任靠架构承载，而架构会像任何代码一样出故障。要测盒子，不只是测工具）
> - 我的理解：
>   - **Plugin4Shell 是两个盒子的缝**：registry 以为"我钉了 SHA，harness 会验"；harness 以为"registry 给的就是钉好的"——**责任落在两个盒子中间，谁都没做**。这是最常见的失守方式：每个组件单看都"有"，合起来没人负责
>   - **"盒子存在"≠"盒子有效"**：事故发生时所有盒子都部署了；所以安全检查清单不能只问"有没有 gateway / allowlist / pin"，要问"**它失败时是拒绝还是放行**"，并且**实际测一次**
>   - **"Test the boxes"怎么测**（我的做法）：
>     - gateway：故意发一个伪造 / 过期的 token，确认被拒（不是退回成空身份）
>     - harness：在测试仓库放一个带 SessionStart hook 的 `.claude/settings.json`，确认不会自动执行
>     - registry / pin：故意改一下 server 的工具描述，确认 harness 报警并停用
>     - 这和门的 Verify（12/12）、Act V 的"杀副本"是同一种思路：**写测试证明它真的拦得住**
> - 对 Forge AI：交付清单里加一节"盒子测试"——每个盒子一个负面测试用例，上线前跑一遍

---

## §12 · Act XI：The Toolwright's Procedure（p.19）

**上线前五问，按顺序**：

| # | 问题 | 检查 | 门 |
| --- | --- | --- | --- |
| 1 | **Whether** | 陌生人的 agent 只看 description 能否判断何时调它、何时调邻居？ | 1–3 |
| 2 | **How** | schema 有类型、字段分开、有示例、没有 god-parameter？ | 4–6 |
| 3 | **What next** | 每个错误都指向房间里的一个工具？每个结果都返回下一步需要的、按预算塑形？ | 7–9 |
| 4 | **What a retry does** | 每个写操作带 idempotency key，label 写明了？ | 12 |
| 5 | **What the box does** | 在哪个 toolset、旁边是哪些工具；谁读它的结果；谁钉它的列表；哪个库执行它的 auth、上次打补丁是什么时候？ | 10、11、13 + Decision Ledger |

**五个阶段（stateless 版）**：
1. runs on my laptop
2. serves a stranger
3. survives a replica's death（**前提：先确认客户端真的在说 stateless 协议**）
4. is pinned and allowlisted ← **大多数团队跳过的一步**：工作完美但没人钉
5. is watched

> 课堂补充：
>
> **deck p.118 · Act XI · The Decision Path —「Five questions, in order」**（19:53，截图 `uploads/1953-p118-five-questions.png`）
>
> | # | 问题 | 选项 | 原则 |
> | --- | --- | --- | --- |
> | 1 | **A tool at all?**（到底要不要做成工具？） | 还是在你自己围墙里用 CLI 就行 | **契约要靠挣**（做成工具 = 要兑现 label 四站的承诺，值得才做） |
> | 2 | **Build, borrow, wrap?**（自建、借用、包一层？） | 通用的 server 已经有了 | **只自建你的差异化部分** |
> | 3 | **Meet the model how?**（怎么让模型接触到它？） | 看见什么、怎么调用 | **两条轴**（Act VIII 网格） |
> | 4 | **Who carries state?**（谁拿着状态？） | client、handles、`requestState` | **永远不是工具本身**（Act V） |
> | 5 | **Who enforces?**（谁来强制？） | registry、gateway、harness、sandbox | **没有盒子，就只是愿望**（Act X） |
>
> - ⚠️ 和讲义的差异：讲义的"五问"是**上线前检查单个工具**（Whether / How / What next / What a retry does / What the box does，对应 label 四站 + 盒子）；deck 这页是**动手之前的决策路径**——先决定做不做、怎么做，再用讲义那五问检查做出来的工具。**两套五问是前后两步**
> - 我的理解：这一页把今天 Act I–X 串成一条路：
>   - 问题 1 ← Act VIII（bash / CLI 也是选项）+ 礼貌规则
>   - 问题 2 ← Act VII（registry 里有什么、能不能信）
>   - 问题 3 ← Act VIII（3×3 网格）
>   - 问题 4 ← Act V（stateless、状态搬家）
>   - 问题 5 ← Act X（四个盒子、fail open）
>   - **顺序有意义**：前一个问题的答案会排除后面的选项——问题 1 答"用 CLI"，后面几问就大半不用问了；问题 2 答"借用"，你就没法控制 label，只能靠问题 5 的盒子
> - **这就是刚才"我们要不要自己写 MCP"的标准答法**：
>   1. 这个能力需要做成工具吗？内部探索用 sandbox 里的 CLI 也许就够
>   2. 有现成的 server 吗？通用的借用（加 allowlist + 钉），**客户特有的、动钱动数据的自己建**（"build only your edge"）
>   3. 工具多不多？要不要藏在搜索后面、要不要写代码批量调？
>   4. 状态放哪？不放在 server 进程里
>   5. 谁拦？按 CoSAI 级别配 gateway / harness / sandbox，并**测盒子**
> - 对 Forge AI：把这五问做成**客户需求评估表**的第一页，每个要接入的能力过一遍
>
> **deck · Act XI · The Maturity Ladder —「Five stages, stateless edition」**（19:56，截图 `uploads/1956-maturity-ladder.png`）
>
> | 阶段 | 是什么 | 要做到 |
> | --- | --- | --- |
> | **stage 0** | **it runs**（能跑） | demo 停在这里，事故从这里开始 |
> | **stage 1** | **it is legible**（看得懂） | schema 诚实、label 当 prompt 写、hint 如实（`readOnlyHint` 等不撒谎） |
> | **stage 2** | **it is polite**（有礼貌） | 返回有边界（不倒 firehose）；label **能赢下搜索** |
> | **stage 3** | **it is safe**（安全） | 重试幂等；有授权、有审计、有闸门 |
> | **stage 4** | **it is infrastructure**（是基础设施） | stateless、在 gateway 后面、钉住、被观测 |
>
> - **stage 4 的测试**：对话中途杀一个副本，没人察觉。**先确认 client 说的是 stateless 协议**
> - 核心句：*"Stage 0 is where demos stop. The Twelve Doors live between stages 1 and 3; the tournament asked for all of them."*（stage 0 是 demo 停下的地方；十二扇门在 stage 1 到 3 之间；tournament 要求全部做到）
> - ⚠️ **和讲义的差异**（课前 deck 精读里已标）：讲义是"laptop → serves a stranger → survives replica death → pinned & allowlisted → watched"，杀副本是**第 3 阶段**；deck 这版按**能力**分级，杀副本是 **stage 4**，而且"钉住 + 被观测"并进了 stage 4。**以 deck 为准**（讲义标了 first draft）
> - "the tournament"：大概是课程的某个比赛 / 期末项目，讲者没在这页解释，待确认
> - 我的理解：
>   - **门和阶段的对应**：
>     - stage 1（看得懂）← 门 1–3（description）、4–6（schema）、11 Mirage（hint 不夸大）
>     - stage 2（有礼貌）← 门 7 Firehose（有边界的返回）、门 5（tool search，label 要赢搜索）
>     - stage 3（安全）← 门 8（error）、门 12 Paid Twice（幂等）、门 10 / 13（授权、闸门）
>     - stage 4 ← 今晚 Act V（stateless）+ Act VII（钉）+ Act X（gateway、观测）——**门里没有，要自己做**
>   - **我目前的位置**：门 1–4 都到了 12/12 → stage 1 基本过了；stage 2 还差门 5、7；stage 3 差门 8、10、12、13
>   - **FinePrint 的位置**：stage 1 大体有（docstring 写得清楚、报错点名工具）；stage 3 缺幂等 key 和工具注解；stage 4 没测过 stateless、没钉版本 → 今天待办里的几项正好是从 2 → 4 的路
> - 对 Forge AI：给客户交付时，用这把梯子说清"当前在第几级、下一级差什么"——比"能用 / 不能用"更有说服力
>
> **deck p.120 · Act XI · Say It Back —「Rebuild the map」**（19:58，截图 `uploads/1958-p120-rebuild-the-map.png`）
>
> - 题目：**不看回头**——哪扇门教了哪个决定？label 的哪一行承载它？label 失败时哪个盒子接住？
> - *"The room first. Then the filled map."*（先在房间里说，再看填好的地图）
> - 我的复述（对照 deck p.121 填好的地图，在 §C 折叠里）：
>
> | 门 | 决定 | label 的哪一行 | 背后的盒子 |
> | --- | --- | --- | --- |
> | 1 Two Doors | **whether**（调不调） | description | 高成本写操作的审批闸门 |
> | 4 Swiss Knife、6 One Field or Two | **how**（怎么调） | input schema | server 端校验 |
> | 8 Polite Error | **what next**（失败后下一步） | error text | server 自己的工具 |
> | 12 Paid Twice | **what a retry does**（重试会怎样） | idempotency key | harness 的重试规则 |
> | 10 Helpful Stranger | label 决定不了 | 结果是数据，不是指令 | 最小权限、allowlist |

---

## §13 · Coda：Back to Beck（p.20）

Harry Beck 画伦敦地铁图是为了乘客的**决策**，不是为了地理。label 也是画给同样的读者：不是熟悉地形的工程师，而是要决定在哪换乘的陌生人。今天多一层：**Beck 的地图告诉你可以去哪，但它不会让火车停下。label 请求；盒子强制。toolwright 两样都要画。**

> 课堂补充：
>
> **deck p.122 · Milestone · Coda —「Back to Beck」：the label is the map**（19:58，截图 `uploads/1958-p122-back-to-beck.png`）
>
> - 画面是一张地铁线路图：几条彩色线路、站点和换乘站（大圆圈）——Harry Beck 1931 年的伦敦地铁图风格：**不按真实地理比例，只画乘客做决定需要的东西**（哪条线、在哪换乘）
> - 副标题：**the label is the map**（label 就是地图）
> - 我的理解：
>   - **地图和 label 的共同点**：都是画给**陌生人**看的，帮他**做决定**；不追求完整，追求"做决定需要的信息都在、不需要的都不在"——就是礼貌规则
>   - **换乘站 = 两个工具的边界**：Door 3 The Twins 那种"两条线在这交汇，你该上哪条"——label 必须把换乘说清楚
>   - **但地图不会让火车停下**：label 只能请求，真正让火车停下的是信号系统（盒子）。toolwright 两样都要画：**地图（label）+ 信号（registry、gateway、harness、sandbox）**
>   - 整天的一句话总结：**写好地图让陌生人走对路，装好信号让走错的人停下来**

---

## §14 · 课堂另一段：Inference in Two Minutes（17:12，不是 Toolcraft deck）

> 截图 `uploads/1712-inference-two-minutes.png`。这页的版式没有 SupportVectors 标志，和 Toolcraft deck 不是一套，应该是另一段分享 / 另一份 deck。**17:29 确认：是 Samsung 的分享**（14.14 那页带 SAMSUNG 标志，产品是 AI Memory Node™）。

**A model reads a prompt, then writes the answer one token at a time.**

| 阶段 | 做什么 | 瓶颈 |
| --- | --- | --- |
| **1 Prefill** | 一次读完整个 prompt（并行） | **GPU 算力**（compute-bound） |
| **2 Decode** | 一次写一个 token（串行） | **显存带宽**（memory-bound：每生成一个 token 都要把权重和 KV cache 读一遍） |
| **3 KV cache** | 模型为每个 token 记的"笔记"（每层的 K、V 向量），后面的 token 直接查，不用重算 | **随每个用户、每个 token 增长** |

**Llama 3.1 70B @ FP16：每 token 约 0.33 MB KV cache**

| | 显存 |
| --- | --- |
| 模型权重 | 140 GB |
| 1 个对话，128K tokens | 43 GB |
| 5 个对话 | 215 GB |

- 核心句：**KV cache grows with every user and every token, so it can outgrow the model itself.**（5 个长对话的 KV cache 已经比模型本身还大）
- **我核了一下数字（对得上）**：Llama 3.1 70B 有 80 层、8 个 KV head（GQA）、head dim 128 → 每 token = 2（K 和 V）× 80 × 8 × 128 × 2 字节（FP16）= 327,680 B ≈ **0.33 MB**；× 131,072 token ≈ **42.9 GB**；× 5 ≈ **214.7 GB**；权重 70B × 2 B ≈ **140 GB**
- 如果没有 GQA（64 个 KV head 全存），每 token 会是 8 倍 ≈ 2.6 MB——GQA 就是为了压 KV cache
- 和今天 Toolcraft 的接线：
  - **token 有显存成本，不只是钱**：板书 12:03 的 PayPal 例（2,000+ 工具全挂 140k token → 搜索 1.3k）不只省 API 费用；在自托管推理里，140k token 的上下文 ≈ 一个对话 46 GB KV cache
  - **礼貌规则**（"只返回下一步决策需要的东西"）和 Door 7 *The Firehose* 也一样：工具返回的每个 token 都会进 KV cache，跟着这个对话一直占显存
  - 相同前缀（system prompt + 工具列表）可以做 **prefix caching**，多个用户共享同一段 KV cache → 工具列表稳定、按内容钉版本（Act VII）也有推理侧的好处：列表一变，缓存就失效

### 14.2 Three Workload Shapes（17:13，截图 `uploads/1713-three-workload-shapes.png`）

**Each puts a different kind of pressure on memory.**

| 负载形状 | 图示 | 对显存的压力 | 含义 |
| --- | --- | --- | --- |
| **One-shot long context** | 一个大块 | **Capacity**（容量） | 一个 session 就能占几十 GB |
| **Multi-turn chat** | 逐轮升高的阶梯 | **Retention**（保留） | cache 要在两轮之间活下来，不然下一轮要重算整段历史 |
| **Agentic loops** | 一个大块 + 一串小块 | **Placement**（放哪） | 大的共享前缀（system prompt + 工具列表）+ 很长的空闲间隙（等工具返回） |

- 我的理解：agentic loop 的那一大块 = **每轮都一样的前缀**，后面的小块 = 每轮新增的工具调用和结果；中间的"空闲"是 agent 在等工具（等网关、等 API）时 GPU 上的 cache 闲着却占着显存
- ↔ Toolcraft：门 12 里网关超时那几秒，在推理侧就是一段 idle gap；工具越慢，cache 闲置越久

### 14.3 When a Long Context Does Not Fit（17:13，截图 `uploads/1713-long-context-not-fit.png`）

场景：一台 8-GPU 服务器跑 Llama 3.1 70B，每个用户一个 128K-token 对话。

- 显存 640 GB = 权重 140 GB + KV cache 11 个用户 × 43 GB（473 GB）→ 剩 **27 GB**；**第 12 个用户需要 43 GB，放不下**
- 核算：640 − 140 = 500；500 − 473 = 27 ✅（640 GB ≈ 8 × 80 GB，H100 / A100-80G 的配置）

| 没有更多显存时 | 代价 |
| --- | --- |
| **Wait** | 用户 12 排队，响应变慢 |
| **Evict, then recompute** | 丢掉一个人的 cache；他回来时 8 张卡重做 128K token 的 prefill，**约 6 s** |
| **Add GPUs** | 再买一台 8-GPU 服务器，**主要是为了它的显存**（算力其实没用满） |
| **Offload**（有内存分层时） | 把闲置的 cache 挪到 **CPU 内存或共享池**，用户回来时再拷回来 |

- 核心句：**Idle conversations hold GPU memory. A cheaper memory tier lets them wait there instead.**（闲置的对话占着 GPU 显存；更便宜的内存层可以让它们在那里等）
- 我核了一下"约 6 s"：128K prefill ≈ 线性部分 2 × 70B × 131K ≈ 1.9×10¹⁶ FLOPs + 注意力部分 ≈ 2.3×10¹⁶ FLOPs；8 张 H100（FP16 稠密约 1 PFLOPS/卡）在 60% 利用率下约 **8–9 s**，利用率更高时到 6 s —— **数量级对**
- 取舍：Offload 的代价是拷回来的带宽和延迟（43 GB 走 PCIe / 网络），但通常比 6 s 的重算便宜；这就是 LMCache、NVIDIA Dynamo 这类 KV cache 分层方案在做的事（我先补的名字；**LMCache 在 17:20 的 vLLM 页、NVIDIA Dynamo 在 17:21 的页上都得到确认**）
- ↔ Toolcraft：**stateless turn**（§5）把会话状态从 MCP server 里拿掉；推理这一侧正相反，KV cache 就是"会话状态"，丢了就要花 6 s 重算——**状态总要有人付钱，只是付在哪一层**

### 14.4 Agentic Workloads Make Inference Stateful（17:14，截图 `uploads/1714-agentic-stateful-tiers.png`）

**HBM / Host DRAM / Local SSD / Pooled Memory over the Fabric —— 延迟、带宽、访问粒度、持久性各不相同。**

时间轴（"同一个 KV block，多久之后再被用到"）→ 应该放在哪一层：

| 多久后再用 | 典型场景 | 该放的层 | 延迟（slide 原文） |
| --- | --- | --- | --- |
| **秒** | 下一轮（next turn） | **HBM**（GPU 显存） | tens of ns |
| **分钟** | 下一个任务（next task） | **Host DRAM**（CPU 内存） | tens of ns |
| **小时** | 下一次会议（next meeting） | **Pooled "L3.5"**（网络 / fabric 上的共享内存池） | microseconds |
| **天** | 第二天早上（next morning） | **Local SSD** | tens of µs |

- 两头的失败：**Evict too early** → 重新取回的时间落在 **TTFT**（首 token 延迟）上；**Keep too long** → HBM 被没人读的 block 烧掉
- ⚠️ slide 上 Host DRAM 也写 "tens of ns"：对 CPU 而言 DRAM 约 100 ns；但从 **GPU** 看，Host DRAM 要走 PCIe / NVLink-C2C，实际是 µs 级。这一格我觉得是 slide 的简化，课后确认
  - **17:26 已解答**：14.12 那页的脚注写明 *"Latency is at the device: HBM and DRAM chips are similar"*——标的是**芯片本身**的延迟，不是 GPU 隔着 PCIe 感受到的延迟，所以两者都写 tens of ns 没错
- "L3.5" 应该是指介于本机内存和存储之间的一层（像 CXL 内存池这类）——我的推测，讲者没展开

**两个放错层的反例**（实心 = 放错的层，空框 = 该在的层）：

| | 编码 agent：长上下文、短时间 | 很多 agent：短上下文、长时间 |
| --- | --- | --- |
| 形状 | **大 block，每轮之间短暂空闲** | **小 block，一闲好几天** |
| 实际状况 | 大部分 block 被降到 Local SSD / Pooled | 全部停在 HBM / Host DRAM |
| 该怎样 | 应在 HBM / DRAM（箭头 ↑ 往上提） | 应在 SSD / Pooled（箭头 ↓ 往下放） |
| 一句话 | *"Demoted for looking cold. Needed again one turn later."*（看起来冷了就被降级，结果下一轮就要用） | *"Idle for a week, parked in the most expensive tier."*（闲了一周，停在最贵的那层） |

- 核心句：**Intelligent data placement needs awareness of the AI application usage.**（数据放哪一层，要知道 AI 应用是怎么用它的）
- 我的理解：推理系统只看"最近有没有被访问"（LRU）是猜不准的——编码 agent 在等工具 / 等人敲代码时**看起来冷但马上要用**，而一个个小 agent 的上下文**看起来还热但一周都不会碰**。只有应用知道下一次什么时候来

**和 Toolcraft 的接线（我自己串的）**：

- **这就是"label"在推理层的版本**：门里我们给工具写 label，让模型知道该怎么调；这里是**应用给推理层写 hint**，让它知道 cache 该放哪。缺 hint 时，推理层和陌生人模型一样只能猜
- **已经有的 hint**：
  - MCP 2026-07-28 的结果字段 `ttlMs`、`cacheScope`（§5 stateless turn 表格）——让 server 告诉 client 结果能缓存多久、给谁用
  - Anthropic API 的 prompt caching 可以选缓存 TTL（默认 5 分钟，可选 1 小时）——就是应用告诉推理层"这段前缀分钟级还是小时级会再用"
  - Hermes 的 `readOnlyHint`（p.44）也是同一类：**应用声明行为，基础设施据此做决定**
- **对 Forge AI 的客户部署**：长时间挂着的客服 / 流程 agent 属于右边那种（小上下文、长空闲）；如果是自托管推理，别让它们一直占着 GPU；如果走 API，按会话间隔选缓存 TTL

### 14.5 What a Memory Shortage Costs（17:17，截图 `uploads/1717-memory-shortage-costs.png`）

**The server bill is fixed per hour. Running out of memory cuts the tokens it delivers.**

$$\text{Cost per token} = \frac{\text{Server cost per hour（固定）}}{\text{Useful tokens per hour（显存不够时下降）}}$$

| 延迟：用户等更久 | 成本：每小时有用的 token 变少 |
| --- | --- |
| cache 被驱逐的老用户回来，首 token 多等 **约 6 s**（128K tokens） | **重算**：花在重建 cache 上的 GPU 时间不产出新 token |
| 新用户排队等位置 | **批次变小**：每次读一遍权重，能分摊的用户变少 |
| cache 还在显存里，这段 prefill 就省了 | **加 GPU**：为显存买的卡，算力闲着 |

- 核心句：**Same hourly bill, fewer useful tokens: every token costs more.**（账单每小时不变，有用的 token 少了，每个 token 就更贵）
- 我的理解：
  - 关键词是 **useful**——重算 prefill 时 GPU 照样满载，但产出的是"已经算过一次"的东西，不计入有用 token
  - "批次变小"接 14.1：decode 是**显存带宽瓶颈**，每一步都要把 140 GB 权重读一遍；同一批里用户越多，这次读取被分摊得越薄。显存被 KV cache 占满 → 能塞进一批的用户变少 → 每个 token 分摊到的权重读取更贵
  - 所以显存短缺**同时**伤延迟和成本，不是二选一
- **算个例子（我自己的假设，不是课上数字）**：一台 8×H100 按 $25/h 算，满载每小时 100 万有用 token → $25/M token；如果三成 GPU 时间花在重算 + 批次变小，有用 token 降到 70 万 → 约 **$36/M**，贵 40%，账单一分没变
- ↔ Toolcraft / 我的项目：
  - 工具返回太多（Door 7 Firehose）、全挂载 140k token 的工具列表，在自托管推理里都会**挤占 KV cache → 批次变小 → 每 token 更贵**；礼貌规则在这里是真金白银
  - 门 12 的重复退款是"同一件事做两次花两份钱"；这里的 evict-then-recompute 是"同一段 prefill 算两次花两份 GPU"——**都是没做幂等 / 没保留状态的代价**
  - Forge AI 给客户报价时，自托管方案的 $/token 不能按满载算，要按实际负载形状（14.2）估有用 token

### 14.6 The Inference Server（17:18，截图 `uploads/1718-inference-server.png`）

**A program on the GPU machine that receives requests, controls the GPUs and manages their memory.**

```text
Users（apps 和 agents）──▶ Gateway（路由请求）──▶ Inference server ──────────────▶ GPU memory (HBM)
                                               ├ Scheduler：这一步谁来跑          ├ Model weights
                                               ├ KV cache manager：block、复用、驱逐 ├ KV cache
                                               └ Model runner：发 GPU kernel       └ Working buffers
                                                                                      ┊ 溢出
                                                                                      ▼
                                                                    Overflow：DRAM / CXL / SSD / pool
```

请求的四步：

1. 请求到达
2. **Gateway** 选一台 server
3. **Scheduler** 把它编进批次，**KV manager** 找到已有的 cache 或分配新的
4. **Model runner** 计算，把 token 流式返回

- 核心句：**Step 3 is the memory decision point.**（第 3 步是做内存决定的地方）
- 我的理解：
  - 前面几页的所有取舍（驱逐还是保留、放 HBM 还是溢出到 DRAM / SSD、批次多大）都发生在第 3 步，由 **KV cache manager** 和 **scheduler** 一起决定
  - "blocks" = KV cache 按固定大小分块管理（vLLM 的 PagedAttention 就是这个思路，像操作系统的内存分页）；"reuse" = 相同前缀的 block 共享（prefix caching）——这两个名字是我补的，课上没提
  - 第 2 步其实也影响内存：如果 gateway 把同一个对话 / 同一段前缀发到**已经有这份 cache 的那台** server，第 3 步就能直接命中；随机路由会让每台都重算一遍（cache-aware routing，我的补充）
  - 14.4 说"放哪要靠应用告诉推理层"——应用的 hint 最终就是在第 3 步被读的
- ⚠️ **"Gateway"撞名**：这里是**推理网关**（把请求路由到 GPU server），和 Toolcraft 里的 **MCP gateway**（Decision Ledger 第 2 条，在 agent 和工具之间做 allowlist / 鉴权）不是一个东西。架构图里两个都可能出现：agent → MCP gateway → 工具；agent 的模型调用 → 推理 gateway → GPU server
- ↔ Toolcraft 的"四个盒子"：推理 server 自己也是一个盒子——label（应用 hint）请求，KV manager 强制；它也会 "fail open"：hint 写错（比如短对话标了 1 小时 TTL），它会照做，HBM 就被浪费

### 14.7 Multi-tenancy（17:19，截图 `uploads/1719-multi-tenancy.png`）

**How one GPU can serve many users.**（一张 GPU 怎么同时服务很多用户）

| 技术 | 图示 | 一句话 | 我的解释 |
| --- | --- | --- | --- |
| **Continuous batching** | A–D 四条请求在时间轴上错开开始、错开结束 | *Requests join and leave every step* | 不等整批结束才换人：每生成一步，做完的请求离开、新请求立刻补进来 → GPU 一直满批。对比旧的 static batching：短请求要陪长请求等到最后 |
| **Paged KV cache** | 一格格小块，彩色 = 已分配给不同用户，虚线 = 空闲 | *Small blocks, handed out as needed* | KV cache 不预留整段连续显存，而是按需发小块（vLLM 的 PagedAttention，类比 OS 内存分页）→ 没有"预留了却没用"的浪费，能塞下更多用户 |
| **Prefix sharing** | 一排 system prompt 块"只存一次"，A/B/C 只各自存后面的私有块 | *Same start, same blocks* | 开头相同的请求共用同一批 KV block；只有分叉后的部分各存各的 |

- 核心句：**All three techniques depend on blocks staying in memory.**（三种技术都依赖 block 留在显存里）
- 我的理解：
  - 这三招是"一张卡服务很多人"的根本，但都有前提：**block 得还在**。共享前缀被驱逐了，大家一起重算；分页的 block 被挪走，下一步就拿不到——又回到 14.5 的"有用 token 变少"
  - 所以 14.4 的"放哪一层"不是锦上添花：显存压力一大，这三种技术的收益会**一起**消失
- ↔ Toolcraft / agent：
  - **Prefix sharing 对 agent 最值钱**：agent 每轮都带同一段 system prompt + 工具列表（14.2 的"大共享前缀"）。全挂载 140k token 的工具列表如果每个用户都一样，只存一次就能共享
  - 反过来：**工具列表每个用户不一样 / 每轮变一次**（动态拼装、顺序不稳定、描述里带时间戳），前缀就对不上，共享失效 → 稳定的工具列表 + 按内容钉版本（Act VII）在推理侧也省钱
  - 写 prompt 的实践：**不变的放前面，变的放后面**（system prompt → 工具 → 历史 → 本轮输入），这样最长的公共前缀才能被共享——这条同样适用于 API 的 prompt caching

### 14.8 Inference Server 1: vLLM（17:20，截图 `uploads/1720-vllm.png`）

**The most widely used open-source server; it made paged KV cache mainstream.**（最常用的开源推理 server，让分页 KV cache 成为主流）

| 特性 | 一句话 |
| --- | --- |
| **PagedAttention** | KV cache 存成小块，像操作系统的内存页 |
| **Continuous batching** | 每一步都有请求加入和离开 |
| **Prefix caching** | 匹配的 block 复用；**最久没用的（LRU）先被驱逐** |

**扩展点：KV connector**

```text
vLLM engine
    │
KV connector API
    │
 ┌──────────┬──────────┬────────┐
 LMCache    Mooncake   Others
```

- *"KV Connector helps offload otherwise evicted KV to memory outside the GPU."*（把本来要被驱逐的 KV 挪到 GPU 之外的内存）
- 我的理解：
  - 14.7 的三种多租户技术，vLLM 全都有 → 这页是"那三招在真实系统里长什么样"
  - **驱逐策略是 LRU** —— 正是 14.4 说的"只看最近有没有被访问"。编码 agent 那种"看起来冷、下一轮就要用"的 block 会被 LRU 先踢掉；所以需要 KV connector 接住被踢的 block，而不是直接丢掉重算
  - KV connector = 14.3 的 **Offload** 那一列在 vLLM 里的落地：vLLM 自己只管 HBM，GPU 外面的层交给插件
  - **LMCache**：专门做 KV cache 分层存储 / 复用的开源项目；**Mooncake**：月之暗面（Kimi）开源的以 KV cache 为中心的推理架构 / 传输引擎（这两个的背景是我补的）
- ↔ Toolcraft：KV connector 是 vLLM 的"插头"——和今天开场的**插头论证**（N×M → N+M）同一个道理：一个标准接口，让任意存储后端接任意推理引擎

### 14.9 Inference Server 2: SGLang（17:21，截图 `uploads/1721-sglang.png`）

**Built around reuse: cached prefixes are kept in a tree.**（围绕复用设计：缓存的前缀存成一棵树）

```text
                System prompt
          ┌─────────┼──────────┐
        Chat A    Chat B    Agent loop
          │                    │
       A, turn 2           Tool call 1
                               │
                           Tool call 2
```

- *"A new request follows the tree as far as it matches."*（新请求沿着树往下走，能匹配多远就复用多远）

| 特性 | 一句话 |
| --- | --- |
| **RadixAttention** | 缓存的前缀以树（radix tree）的形式留在 GPU 显存里 |
| **HiCache** | 这棵树延伸到 CPU 内存和存储（分层缓存） |

- 我的理解：
  - **vLLM vs SGLang 的差别**：vLLM 的 prefix caching 是按 block 匹配、LRU 驱逐，复用是"附带的优化"；SGLang 从一开始就**把复用当核心**，用一棵前缀树组织所有 cache——共享的 system prompt 是树根，每个对话 / agent 循环是一根分支
  - **HiCache ≈ vLLM 的 KV connector + LMCache**：都是把 GPU 外的内存层接进来；区别是 SGLang 的分层是树本身的延伸（树的冷分支下沉到 CPU / 存储），vLLM 是通过插件接口外挂
  - **agent 循环天然就是一条长分支**：system prompt → agent loop → tool call 1 → tool call 2 … 每一轮只在末端加一个节点，前面全部命中。这就是 14.2 里 agent 负载"大共享前缀"的结构，SGLang 正好为它而设计
- ↔ Toolcraft / 写 prompt 的实践（接 14.7）：
  - 树只能从根往下匹配 → **中间任何一处变了，后面整条分支都失效**。如果每轮把工具列表重新排序、或在 system prompt 里插当前时间，树在根附近就分叉了，下面的 tool call 全部重算
  - 所以"不变的放前面"在 SGLang 上收益最明显；Hermes 的 **deferred 工具加载**（搜索后才把 schema 拉进上下文）会在中途插入新内容——对 cache 来说，插在末尾比改动前面好
- 待查：SGLang 的 HiCache 是否默认开启；RadixAttention 的驱逐策略（应该也是 LRU，但按树叶子驱逐）

### 14.10 Above the Servers: NVIDIA Dynamo（17:21，截图 `uploads/1721-nvidia-dynamo.png`）

**An orchestration layer that runs vLLM, SGLang or TensorRT-LLM as workers.**（一个编排层，把 vLLM / SGLang / TensorRT-LLM 当作 worker 来跑）

```text
            Frontend and KV-aware router（跑在 CPU 上）
              ↓ requests      ↑ block events（每个 worker 手上有哪些 cache）
   ┌──────────────┐  NIXL  ┌──────────────┐  NIXL  ┌──────────────┐
   │ Worker 1     │◀──────▶│ Worker 2     │◀──────▶│ Worker 3     │
   │ vLLM         │        │ SGLang       │        │ TensorRT-LLM │
   │ KV Block Mgr │        │ KV Block Mgr │        │ KV Block Mgr │
   │ GPU/CPU/SSD  │        │ GPU/CPU/SSD  │        │ GPU/CPU/SSD  │
   └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
          └──────────── Remote storage（所有 worker 共享）─┘
```

| 组件 | 做什么 |
| --- | --- |
| **KV-aware routing** | 把请求发给**手上 cache 最多**的那个 worker，同时不把它压垮 |
| **Planner** | 随流量变化增减 worker |
| **Disaggregation** | prefill 和 decode 可以拆到不同 GPU 上；cache 通过 **NIXL** 搬过去 |
| **KV Block Manager** | 每个 worker 一个：在 GPU、CPU、SSD 和远程存储之间搬 block |

- 核心句：**Engines manage memory inside one server. Dynamo manages it across servers.**（引擎管一台 server 里的内存，Dynamo 管跨 server 的内存）
- 我的理解：
  - **KV-aware routing 就是 14.6 第 2 步的答案**：我那时补的"gateway 应该把请求发到已有 cache 的 server"，这里落地成了真东西。router 靠 worker 上报的 **block events** 知道谁手上有什么，所以能选命中率最高的那台；"不压垮"是另一半约束——全发到最热那台会让它排队
  - **Disaggregation 接 14.1**：prefill 吃算力、decode 吃显存带宽，瓶颈不同，放同一张卡上互相拖累；拆开后各自用合适的硬件，代价是要把算好的 KV cache 从 prefill 卡搬到 decode 卡（NIXL 负责这次搬运）
  - **NIXL**（NVIDIA Inference Xfer Library）：在 worker 之间、GPU 和各存储层之间搬 KV block 的传输库——全称是我补的
  - 分层：**引擎**（vLLM / SGLang / TRT-LLM）管单机的 block、批次、前缀；**Dynamo** 管集群：路由、扩缩容、跨机搬 cache。三家引擎可以混跑在同一个集群里
- ↔ Toolcraft：
  - 又一个**插头**：Dynamo 不关心 worker 是哪家引擎，只要它会上报 block events、能通过 NIXL 收发 block（N+M 而不是 N×M）
  - **Planner 减 worker = 杀副本**：Act V 的 stateless 测试是"杀掉一个副本没人察觉"；推理这边杀掉一个 worker，它手上的 KV cache 就没了——除非 KV Block Manager 已经把 block 推到共享的远程存储。**状态总要有人付钱**（14.3）在集群层又出现一次
  - block events 是 worker 向 router 报告"我有什么"——和 MCP 的 `server/discover`（server 宣告自己有什么工具）是同一种模式：**路由的人只能根据被告知的信息做决定**

### 14.11 Opensource Memory Expansion：LMCache + Mooncake（17:23，截图 `uploads/1723-opensource-memory-expansion.png`）

**A machine is the physical box with GPUs. An instance is one running copy of vLLM. A machine can run several.**（machine = 带 GPU 的物理机；instance = 一个跑着的 vLLM 副本；一台机器可以跑好几个）

```text
┌─ Physical machine 1 ───────────────────┐        ┌─ Physical machine 2 ─────────┐
│ Instance A (vLLM, 4 GPU)  Instance B (4 GPU) │        │ Instance C (vLLM, 8 GPU)     │
│        LMCache（A 和 B 共享）            │        │        LMCache               │
│ CPU memory（切一片加入 Mooncake 池）     │◀─RDMA─▶│ CPU memory（切一片加入池）    │
└────────────────────────────────────────┘        └──────────────────────────────┘
      Mooncake Store：两台机器的 CPU 内存拼成一个池；master 记录每个 chunk 在哪台机器
```

四步：

1. **A** 为某个 prompt 算出 cache，切成 chunk 存起来，**每个 chunk 的 ID 由它的 token 算出来**
2. **B** 收到同一个 prompt：LMCache 在**本机内存**里找到这些 chunk
3. **C** 也收到了：**master** 说机器 1 有这些 chunk
4. **C** 通过 **RDMA** 把它们拉到自己的 GPU 上，跳过那段 prefill

- 核心句：**Sharing works because the same text always gives the same chunk ID, on any instance.**（共享之所以成立，是因为同样的文本在任何 instance 上都算出同样的 chunk ID）
- 分工：**LMCache** = 单机内多个 instance 共享（同一台机器的 CPU 内存）；**Mooncake Store** = 跨机器的池（master 记位置，RDMA 搬数据）
- 我的理解：
  - **chunk ID 是内容寻址**（content-addressed）：ID 从 token 算出来（哈希），而不是由谁分配。所以没有任何协调，A、B、C 各自算都会得到同一个 ID，查找就能对上
  - 细节：KV 依赖**前面所有 token**，同一段文字跟在不同前缀后面，KV 不一样 → chunk ID 应该把**前缀也算进去**（链式哈希）。所以"same text"实际上是"从开头到这个 chunk 都相同"——这和 14.9 SGLang"沿树匹配到分叉为止"是同一个约束
  - RDMA 拉 43 GB 远比 6 s 的重算便宜（14.3 的 offload 论证在跨机层面成立）
- ↔ Toolcraft（今天最漂亮的一个呼应）：
  - **chunk ID ≈ idempotency key**：门 12 的 key 让"同一个意图"在任何重试里都被认出来；chunk ID 让"同一段前缀"在任何 instance 上都被认出来。两者都是**用一个稳定的身份把"第二次"变成"查第一次的结果"**——*"A key turns a second order into a question about the first one."*
  - 区别：idempotency key 由调用方**生成**（因为只有它知道意图）；chunk ID 由内容**算出**（因为内容本身就是身份）
  - **Act VII "按内容钉"**：工具列表按内容哈希钉版本，和这里按内容算 chunk ID 是同一个思想——**名字会骗人，内容不会**
  - 实践推论（接 14.7 / 14.9）：只要 system prompt + 工具列表**逐字节**稳定，它们的 chunk 就能在整个集群里只算一次

### 14.12 The Case for Composable Heterogenous Memory（17:26，截图 `uploads/1726-composable-heterogeneous-memory.png`）

**Mix of applications have different SLA requirements:**

| 需求 | 服务什么 |
| --- | --- |
| **Latency** | 快速响应（decode） |
| **Bandwidth** | 装下长上下文输入 |
| **Capacity** | 大块可复用的上下文，省下重算成本 |

**内存层级金字塔**（蓝色 = AI 时代新出现的层；X.5 都是新层）：

| 层 | 名称 | 延迟（器件） | 带宽 | 容量 | 传输 | 器件 | 归属 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L0 | GPU SRAM | < tens of ns | > tens of TB/s | tens of MB | on-die | GPU SRAM | GPU |
| **L0.5** | 3D 堆叠 DRAM | TBD | > few TB/s | few GB | on-package | 3D stacked DRAM | GPU |
| L1 | HBM | ~tens of ns | few TB/s | 80–192 GB | on-package | HBM stacks | GPU |
| **L1.5** | 光互连 HBM | TBD | few TB/s | hundreds of GB | 光互连（新兴） | optically attached HBM | GPU |
| L2 | CPU DRAM | ~tens of ns | hundreds of GB/s | hundreds of GB | on-board（DDR5） | RDIMM / MRDIMM | CPU |
| **L2.5** | 高速互连内存 | hundreds of ns | tens of GB/s | hundreds of GB ~ 1 TB | CXL, UALink, NVLink-F, ICI | CMM-D, CXL memory expanders | CPU |
| L3 | 本地 SSD | ~tens of µs | up to 13 GB/s | few TBs | PCIe | local NVMe SSD | — |
| **L3.5** | 以太网内存 | ~few µs | 12–50 GB/s / NIC | tens of TBs | RDMA / UET, ESUN | "AI Memory Node™", memory pool | Network |
| L4 | 存储服务器 | ~few ms | ~GB/s | tens of TBs | Ethernet | storage server, NVMe-oF | Network |

- 脚注：*"Latency is at the device: HBM and DRAM chips are similar, and HBM wins on bandwidth. Capacity per GPU; bandwidth per device, drive or NIC."*
- 核心句：**Varying inference workloads will use composable heterogenous memory across different transports. Requires a solution that supports this complex and evolving system design.**（不同的推理负载会跨不同传输方式使用可组合的异构内存；需要能支撑这种复杂、还在演进的系统设计的方案）
- 我的理解：
  - 三个 SLA 对上三种负载形状（14.2）：**latency ↔ 多轮对话的 decode**，**bandwidth ↔ 一次性长上下文**，**capacity ↔ agent 循环的大共享前缀 + 长空闲**
  - **X.5 层都是在两层之间补"断崖"**：L1 HBM（几 TB/s、百 GB 级）到 L2 DRAM 之间，L2 到 L3 SSD（tens of µs）之间，L3 到 L4（ms 级）之间，原来都是数量级的跳跃；新层把阶梯变密，14.4 "按多久后再用来放层"才有地方可放
  - **L3.5 比 L3 快却排在下面**：以太网内存池延迟 ~few µs，比本地 SSD 的 tens of µs 还快，但金字塔按**容量 / 每 GB 成本**排序，不是按延迟。这就是 14.11 Mooncake 池（RDMA 把多台机器的 DRAM 拼起来）所在的那一层
  - "AI Memory Node™" 带商标，L3.5 那行像是讲者所在公司的产品——这段分享可能是**厂商视角**，讲"为什么需要 L3.5 层"时要留意立场（课后查讲者身份）
- 术语（我补的，待确认）：**CXL** = Compute Express Link，CPU 和内存扩展设备之间的缓存一致互连；**UALink** = 加速器之间的开放互连标准；**NVLink-F** = NVLink Fusion；**ICI** = Google TPU 的芯片间互连；**CMM-D** = 三星的 CXL DRAM 模块；**UET** = Ultra Ethernet Transport；**ESUN** = Ethernet for Scale-Up Networking；**MRDIMM** = 多路复用 DIMM（更高带宽的 DDR5 条）
- ↔ Toolcraft：**composable** = 按需把层拼起来，和 MCP 的插头论证、vLLM 的 KV connector、Dynamo 的 KV Block Manager 一脉相承——只有接口标准了，异构的层才能"组合"；没有标准，每加一层就是 N×M 的定制集成

### 14.13 What Composable Memory Means（17:28，截图 `uploads/1728-composable-memory-means.png`）

**Memory that is pooled, tiered and attachable.**

| 性质 | 一句话 | 前面哪页落地了 |
| --- | --- | --- |
| **Pooled** | 被很多 server 共享 | 14.11 Mooncake Store（多台机器的 DRAM 拼成一个池）；14.10 Dynamo 的共享远程存储 |
| **Tiered** | 每个 block 放在合适的层 | 14.4 按"多久后再用"放层；14.12 九层金字塔 |
| **Attachable** | 加内存不用加 GPU | 14.3 / 14.5 "Add GPUs：为显存买卡，算力闲置"的反面 |

**Intelligent data placement** 要考虑四个维度：**Latency · Bandwidth · Access size · Persistence**

- 这四个就是 14.4 开头那句 "different latency, bandwidth, access granularity, and persistence" 的回收
- 我的理解（四个维度各管什么）：
  - **Latency**：下一次访问能等多久——decode 的下一步要纳秒级，第二天早上的会话可以等毫秒
  - **Bandwidth**：一次要搬多少——128K 对话的 43 GB 要在几秒内回到 GPU，就得放在带宽够的层
  - **Access size**（访问粒度）：每次读写多大的块——HBM / DRAM 按字节 / 缓存行访问很划算，SSD 按页（几 KB）、网络池按大块才划算；KV block 切多大会影响它适合放哪层（14.7 的"小块"和 14.11 的"chunk"）
  - **Persistence**：断电 / 重启后还在不在——HBM、DRAM 重启就没了，SSD 和存储服务器能留下；隔天才用的 cache（14.4 的 "days"）要放能持久的层，worker 被 Planner 缩掉（14.10）时也靠这一点
- **"Attachable" 是这段分享的商业论点**：14.5 说 Add GPUs 是"为显存买卡、算力闲着"；composable memory 主张把内存和算力**解耦**，内存不够就加内存。这正是 L2.5（CXL 扩展）/ L3.5（以太网内存池）层的卖点——呼应 14.12 我记的"讲者可能是厂商视角"
- ↔ Toolcraft：**解耦 = 插头论证**。MCP 让工具和 agent 解耦（N+M），composable memory 让内存和 GPU 解耦；两边都靠标准接口（MCP / CXL、RDMA、KV connector）。代价也一样：多了一层，就多了一个可能 fail open、要监控、要钉版本的地方

### 14.14 AI Memory Node — Samsung Solution（17:29，截图 `uploads/1729-samsung-ai-memory-node.png`）

> 右上角 **SAMSUNG** 标志 → 确认这一段是**三星的厂商分享**，前面 14.12 的 "AI Memory Node™" 就是这个产品。

**卖点四条**：

- 不加 GPU 节点就增加 KV cache 内存
- 用 **CMM-D**（三星的 CXL DRAM 模块）扩展内存
- **No GPU SW changes required**（GPU 侧软件不用改）
- *"Production-ready and reliable (Use numbers)"*

**AI Inference Stack View**（从上到下）：

| 层 | 组件 |
| --- | --- |
| **Application Harness** | Coding Agent Application → **LiteLLM**（可观测性）→ On-prem LLM（**Gemma4**） |
| **KV Cache Tiered Expansion**（L1：HBM · L2：DRAM · **L3.5：AI Memory Node**） | **SGLang** Inference Server → **Cognos Docker** |
| **AI Infrastructure**（GPU pod + AI Memory Node 1U + 网络交换机） | **GPU Node**：4× B200，每张 192 GB HBM，用了 300 GB host DRAM ⟷ **100G** ⟷ **AI Memory Node™**：1U 服务器，48 核 x86 CPU，最多 **6 TB** DRAM + CMM-D + SSD |

- *"Drop in Samsung Cognos hooks in AI inference server for AI Memory Node management."*（在推理 server 里接入三星的 Cognos 钩子来管理 AI Memory Node）
- Rack View：机柜里从上到下标了 Mellanox（交换机）、AI Memory Node™（1U）、NVIDIA B200 GPU 节点

**我的理解**：

- 这就是前面整条线的产品落地：14.9 SGLang 的 HiCache（树延伸到 CPU 内存和存储）→ 14.12 的 L3.5 层 → 用一台 1U 的"内存服务器"挂在 GPU 节点旁边，通过 100G 网络提供几 TB 的 KV cache 空间
- 示范场景选的是 **coding agent**——正是 14.4 左边那个反例（大 block、轮间短暂空闲、"看起来冷却下一轮就要用"）
- 应用层用 **LiteLLM** 做可观测性（统一代理多家模型 API 的开源网关），模型是本地部署的 Gemma4

**几个值得追问的地方（我的批判性阅读）**：

1. **"(Use numbers)" 像是没删掉的草稿备注**："Production-ready and reliable" 这句目前**没有任何数字**支撑。正好对上今天的候选技巧 #73"引用数字必带单位和主人"——课后看讲者有没有补数据（命中率、TTFT 改善、$/token）
2. **100G 链路够不够**：100 Gb/s ≈ 12.5 GB/s（正好是 14.12 L3.5 那行 "12–50 GB/s / NIC" 的下限）。一个 128K 对话 43 GB 拉回来要 **~3.4 s**；14.3 说 8 张 H100 重算约 6 s，而 B200 算力更强，4 张 B200 重算可能也就几秒 → **完整拉回一个 128K cache 的优势并不大**。收益应该主要来自：(a) 只拉命中的前缀 chunk，而不是整段；(b) 和计算重叠（边拉边算）；(c) 重算会占住 GPU，拉取不会——GPU 时间省下来能服务别人（14.5 的"有用 token"）。课上如果有 Q&A 可以问 TTFT 实测
3. **"No GPU SW changes" vs "drop in Cognos hooks in inference server"**：GPU 驱动 / CUDA 不用改，但**推理 server 要接钩子**（大概是 SGLang HiCache 的存储后端插件），所以"零改动"指的是 GPU 侧，不是整个栈
4. GPU 节点"300G host DRAM used"——本机 L2 已经在用，AI Memory Node 是在它下面再加一层 L3.5

- ↔ Toolcraft：
  - 这又是 **Decision Ledger** 的场景：要不要买这台 1U，先问"以谁的身份 / 能触达什么 / 失败时会怎样"——内存节点挂了，GPU 节点会不会 fail open（退回重算还是报错）？
  - Act VII 的 **"规范 vs 实现"**：MUST 不是强制，库才是。厂商 slide 上的"production-ready"同理——**数字和实测才是强制，形容词不是**

### 14.15 Production Evaluation — Results（17:31，截图 `uploads/1731-samsung-production-results.png`）

> 三星分享；条件：**同样 100 个用户并发**。补上了 14.14 "(Use numbers)" 的数字。

| Stage | 配置 | 对比 | ITL | TTFT | E2E |
| --- | --- | --- | --- | --- | --- |
| 1 | Cognos + SGLang，**2× GPU** | 基线 | — | — | — |
| 2 | Cognos + SGLang + **AI Memory Node**，2× GPU | vs Stage 1 | **5.9×** | **3.4×** | **3.1×** |
| 3 | Cognos + SGLang，**4× GPU**，无 AI Memory Node | vs Stage 2 | **1.4× worse** | flat | flat |
| 4 | Cognos + SGLang + AI Memory Node，4× GPU | vs Stage 3 | 1.7× | 1.6× | 1.5× |
| **1 → 4 累计** | | | **6.9× better** | **5.6× better** | **4.6× better** |

- 另一项：**KV Utilization 4.8× higher**
- 指标：**ITL** = inter-token latency（相邻两个输出 token 之间的间隔，decode 速度）；**TTFT** = time to first token（首 token 延迟，prefill + 排队）；**E2E** = 端到端请求时延

**关键结论**：**Stage 2 vs Stage 3**——2 张 GPU + 内存节点 ≥ 4 张 GPU 不加内存节点（ITL 好 1.4×，TTFT / E2E 持平）。也就是：**一台 1U 内存服务器 ≈ 再买两张 GPU 的效果**。这就是 14.13 "Attachable：加内存不用加 GPU" 的数字版

**我核了一下累计数**：逐段相乘 ITL = 5.9 ÷ 1.4 × 1.7 ≈ **7.2**（slide 写 6.9）；TTFT = 3.4 × 1 × 1.6 ≈ **5.4**（slide 5.6）；E2E = 3.1 × 1.5 ≈ **4.65**（slide 4.6）→ 三项都在四舍五入误差范围内，**内部自洽**

**我的理解：为什么 decode 的 ITL 会好 5.9 倍？**

- 直觉上 KV offload 帮的是 prefill（少重算 → TTFT 降），decode 每步只读权重和当前 cache，和内存层关系不大
- 合理的解释：100 个并发、只有 2 张 GPU 时显存严重不足 → server 频繁**抢占（preempt）**正在 decode 的请求、驱逐它们的 cache，之后再重算；重算的 prefill 和 decode 挤在同一批里，**拖慢了所有人的每一步** → ITL 飙高。有了内存节点，cache 被挪走而不是丢掉，抢占后恢复只需拉回，decode 批次不再被重算打断
- 所以 ITL 的提升其实也是 14.5 "有用 token" 的体现：GPU 不再花时间重算

**还需要追问的（批判性阅读）**：

1. **没有绝对值**：只有倍数，没有 ms。基线如果因为抢占已经极差（比如 ITL 几百 ms），5.9× 看起来大，但可能只是"从很糟变成正常"
2. **负载没说**：prompt 长度、多轮次数、前缀命中率、Gemma4 是哪个尺寸——coding agent 是对内存节点**最有利**的负载（14.4 左边的反例），换成短对话结果会不同
3. **只看均值还是 p99？** 抢占类问题通常在尾延迟上更明显
4. **最关键的经济账没给**：Stage 2 vs Stage 3 的结论要成立，得比较 **1 台 AI Memory Node 的价格 vs 2 张 B200 的价格**（以及功耗、机架空间）。slide 只证明了性能等价，没证明成本更低
5. **"KV Utilization 4.8× higher"** 定义不清：是 cache 命中率、可用 KV 容量，还是显存利用率？
6. **厂商自测**：可复现性和对照组设置（Stage 3 的 SGLang 是否开了 HiCache 用本机 DRAM？）都需要确认。如果 Stage 3 没开 HiCache、只用 HBM，对照就偏弱

- ↔ Toolcraft：
  - 和 Door 的 **Verify** 一样：一个分数（12/12 或 5.9×）只有在**held-out、条件写清**时才算数；厂商 benchmark 等于"在作者自建的目录上跑分"——Act VIII 的 bash vs typed tools（68% vs 45%）那条批注也是同一句话：*目录是作者自建的*
  - 候选技巧 #73"引用数字必带单位和主人"：这页的数字**有主人**（三星），**缺单位**（全是倍数）

### 14.16 The AI Memory Node™ Advantage with CMM-D（17:33，截图 `uploads/1733-samsung-cmmd-advantage.png`）

> 三星分享。**P50 延迟**，越低越好。Stage 1–2 在 **2× B200**，Stage 3–4 在 **4× B200**。补上了 14.15 缺的**绝对值**。

| Stage | 配置 | TTFT (s) | E2E (s) | ITL (ms) | KV cache 利用率 (%) | GPU 使用率 (%) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2× B200 | **17.72** | **20.3** | **290** | 20 | 98 |
| 2 | 2× B200 + 内存节点 | 5.19 | 6.6 | 49 | 82 | 90 |
| 3 | 4× B200 | 5.1 | 6.88 | 70 | 45 | 94 |
| 4 | 4× B200 + 内存节点 | **3.19** | **4.45** | **42** | 96 | 83 |

三个结论框：**Equal or better latency with half the GPUs** · **>5× better inter-token latency** · **Better KV Cache hit with lesser GPU usage**

**我用绝对值核了 14.15 的所有倍数（全部对得上）**：

| 倍数 | 计算 | 结果 |
| --- | --- | --- |
| TTFT 3.4× / 5.6× | 17.72 ÷ 5.19 / 17.72 ÷ 3.19 | 3.41 / 5.55 ✅ |
| E2E 3.1× / 4.6× | 20.3 ÷ 6.6 / 20.3 ÷ 4.45 | 3.08 / 4.56 ✅ |
| ITL 5.9× / 6.9× | 290 ÷ 49 / 290 ÷ 42 | 5.92 / 6.90 ✅ |
| Stage 3 比 2 差 1.4× | 70 ÷ 49 | 1.43 ✅ |
| Stage 4 比 3 好 1.7× | 70 ÷ 42 | 1.67 ✅ |
| TTFT / E2E "flat" | 5.19 vs 5.1 / 6.6 vs 6.88 | 差 2% / 4% ✅ |
| KV 利用率 4.8× | 96 ÷ 20 | 4.8 ✅ |

- 14.15 里我逐段相乘得到 ITL 7.2（slide 写 6.9）——原因是每段倍数都四舍五入过；用绝对值直接算 290 ÷ 42 = **6.90**，slide 是对的

**14.15 的追问，这页回答了哪些**：

- ✅ **绝对值**：有了。而且证实了我的担心——**基线非常糟**：P50 TTFT **17.7 秒**、ITL **290 ms**（≈ 每秒 3.4 个 token）。100 个并发压在 2 张 B200 上，基线明显是在**严重超载 / 反复驱逐重算**的状态。改进后的 Stage 4 是 TTFT 3.2 s、ITL 42 ms（≈ 每秒 24 token）——这才是"正常可用"的水平。所以"5.9×"的意义是**从不可用变成可用**，而不是从好变成更好
- ✅ **均值还是尾延迟**：是 **P50**（中位数）。**P99 没给**——抢占 / 重算类问题通常在尾部更严重，内存节点在尾部的收益可能更大，也可能有拉取慢的长尾，未知
- ✅ **"KV Utilization" 的定义**：图里标题写 *"Better KV Cache hit"*，所以基本就是 **cache 命中率**：基线只有 **20%**（80% 的请求要重算），加内存节点后 82–96%
- ❌ **价格对比**：仍然没有
- ❌ **负载细节 / 对照组是否开了 HiCache**：仍然没有

**新的观察**：

- **GPU 使用率反而下降**（98% → 83%）而性能大涨：基线的 98% 里有大量是**重算**（14.5："重算不产出新 token"）。GPU 忙不等于 GPU 在干有用的活——**GPU 利用率是个会骗人的指标**，要看有用 token / 命中率
- **Stage 3 的命中率只有 45%**：GPU 加倍，命中率才从 20% 到 45%；而 2 张卡 + 内存节点就到 82%。说明瓶颈是**内存容量**，不是算力——这正是 14.5 "为显存买卡，算力闲置"的实测证据
- ⚠️ **P50 不能相加**：E2E − TTFT 看起来很小（Stage 1：20.3 − 17.72 = 2.58 s，按 290 ms/token 只够约 9 个 token），但三个 P50 是各自取的中位数，不一定来自同一批请求，所以不能用来反推输出长度。不过也暗示**输出偏短、prefill 占大头**——符合 coding agent 读大量代码、改一小段的负载

- ↔ Toolcraft：
  - **"GPU 98% 忙但在白干"** = Door 4 Swiss Knife 里 agent 8 次盲猜：调用次数多不代表有进展；度量要看**结果**（12/12、有用 token），不是**活动量**
  - 这页是 #73 的正面例子：**有单位（s、ms、%）、有条件（P50、100 并发、几张 B200）、有主人（三星）**——比上一页只给倍数可信得多

### 14.17 课上追问整理：内存节点怎么接、Cognos 是什么（17:34–17:39，同一页 slide 仍在屏上）

**内存节点怎么管 CPU 内存（我的推断，slide 没写协议）**：

- **L2 本机 DRAM**（GPU 节点自己的 300 GB host DRAM）：走 PCIe，由 SGLang HiCache 管
- **L3.5 AI Memory Node**：100G 网线相连；14.12 金字塔 L3.5 一行写的传输是 "RDMA / UET, ESUN" → 推测走 RDMA（可能 GPUDirect 直接进 HBM）
- **节点内部**：DRAM + **CMM-D（CXL 接在节点自己的 CPU 上，= L2.5）** + SSD；CXL 管单机扩容，对外再把整池内存提供给 GPU 节点
- **谁决定放哪**：推理 server 里的 Cognos 钩子（推测是 SGLang HiCache 的存储后端插件，模式同 vLLM KV connector + Mooncake）

**Cognos 是什么**：

- **没查到公开资料**，可能是三星内部 / 未发布的软件名。⚠️ 别和 **IBM Cognos**（商业智能报表产品）搞混
- slide 上的线索："Cognos Docker"（容器部署在 SGLang 下）+ *"Drop in Samsung Cognos hooks in AI inference server for AI Memory Node management"*
- **公开报道**（[StorageReview：Samsung CXL memory pooling, AMD, OCP 2026](https://www.storagereview.com/news/samsung-cxl-memory-pooling-amd-ocp-2026-cmm-d-agentic-ai)，2026-10-25 查）：
  - 三星和 **SGLang** 合作做 **L3.5 composable memory tier**，声称 KV cache 利用率 **5–7×**（课上是 4.8×，量级接近）
  - **LMCache** 里用了三星 SSD 的 Flexible Data Placement 存 KV cache
  - **CXL 内存池**演示，用 **DCD（Dynamic Capacity Device）**：运行时把池里的内存借给主机、再收回；声称 TTFT 最多 −38%、goodput 3.3×
  - 报道指出：三星和 AMD **没公布**服务器配置、CXL 交换拓扑、互连延迟和带宽，数字未经第三方审核
  - **全文没提 RDMA** → 我的"走 RDMA"推断要打问号：公开资料讲的是 CXL 池化；课上的 100G 网线又像以太网 L3.5。可能是两套方案（CXL 交换直连池 vs 以太网内存节点）

**为什么 Cognos 是"钩子 + Docker"两部分（17:53 我的推断，slide 没解释）**：

- **钩子**：装在 SGLang 里的一层薄客户端（大概率实现 HiCache 的存储后端接口），只负责在 SGLang 要下放 / 取回 KV block 时把请求转给 Cognos
- **Cognos Docker**：真正干活的**独立服务（sidecar / daemon）**，跑在 GPU 节点上、SGLang 旁边：决定 block 放内存节点的 DRAM / CMM-D / SSD 哪层、管容量和驱逐、维护"哪个 chunk 在哪"的索引、走网络搬数据
- **为什么用容器**：
  1. **和推理引擎解耦**：SGLang 和 GPU 驱动不用改（对应卖点 "No GPU SW changes"），Cognos 可以单独升级、回滚
  2. **打包依赖**：RDMA / CXL 用户态库、NUMA 和大页配置、三星自己的管理组件——装进镜像，不污染推理环境
  3. **一机多 instance 共用**：一台机器上几个 SGLang 实例连同一个 Cognos 服务，像 LMCache 的 server 模式 / Mooncake 的 master
  4. **部署方便**：数据中心基本跑 Kubernetes，一个 DaemonSet 每个 GPU 节点一份
  5. **故障隔离**：Cognos 挂了不应该拖垮 SGLang——钩子退回"本机 HBM / DRAM + 重算"（是否真的这样 fail safe，要问）
- 同一种模式在 Toolcraft 里也有：**MCP server 是独立进程，agent 里只有薄客户端**；Envoy / service mesh 的 sidecar 也是这个思路
- 聊天区 17:51 另一位同学也在问"Cognos 具体做了什么才达到这个结果"——等讲者回答

**待问 / 待查**：

- [ ] Cognos 是自研 KV 存储，还是基于 LMCache / Mooncake 改的？（决定是否绑定三星软件）
- [ ] GPU 节点 ↔ 内存节点走 RDMA（RoCE？）还是 CXL？是否 GPUDirect？
- [ ] P99 延迟、负载细节（prompt 长度、命中率来源）、Stage 3 是否开了 HiCache
- [ ] 一台 AI Memory Node vs 两张 B200 的价格 / 功耗

### 14.18 Choosing a Deployment（17:41，截图 `uploads/1741-choosing-a-deployment.png`）

**Start with the workload, then use the smallest sharing scope that works.**（先看负载，再选能用的**最小**共享范围）

| 场景 | 方案 | 对应前面哪页 |
| --- | --- | --- |
| 一台 server，多租户，多个应用 | **Prefix caching，然后 CPU offload** | 14.7 prefix sharing；14.3 offload；14.8 vLLM / 14.9 SGLang 单机 |
| 一台机器上跑好几个 server | **节点内共享池，比如 LMCache** | 14.11 LMCache（同机 instance A、B 共享） |
| 很多 GPU，前缀反复出现 | **共享池 + cache-aware routing** | 14.10 Dynamo KV-aware routing；14.11 Mooncake Store |
| 超长 prompt | **prefill / decode 分离 + 共享 KV 层** | 14.10 Disaggregation；14.12 L3.5 层 |

- 核心句：**Measure your cache hit rate first. It shows which step you need.**（先测 cache 命中率，它告诉你需要走到哪一步）
- 脚注：*"Rules of thumb for discussion, not benchmark results."*（讨论用的经验法则，不是 benchmark 结果）
- 我的理解：
  - 这页是整段分享的**决策树**：共享范围从小到大——单 server → 单机 → 集群 → 拆分 prefill / decode。每往下一行，复杂度、网络依赖、故障面都变大，所以**能停在上面就别往下走**
  - **先测命中率**：14.16 三星的数据就是例子——基线命中率 20%，说明 cache 被大量驱逐 → 需要更大的内存层；如果命中率本来就高但延迟还差，问题就不在内存而在算力
  - 和三星的产品叙事有点张力：这页说"用最小的共享范围"，而 AI Memory Node 是最外层（L3.5）方案——对多数单机负载，第一、二行（prefix caching + LMCache）可能就够了
- ↔ Toolcraft：
  - **"smallest sharing scope that works" = 最小权限 / allowlist 原则**（Decision Ledger、Door 10 *Helpful Stranger*）——安全上"能触达的越少越好"，这里是"共享得越窄越简单"。同一种工程直觉：从最小开始，有证据才扩大
  - **"先测命中率"= 门的五步里的 Predict + Verify**：先度量，再修；别凭感觉直接上最重的方案（Door 4 拆 god-tool 也是先看 trace 才决定改哪个面）
  - 对 Forge AI 客户部署：先用 API（提供方的 prompt cache）或单机 vLLM / SGLang + prefix caching，测命中率，再决定要不要上 LMCache / Dynamo

**聊天区同学提问**（17:36）：*"Does COGNOS work with CXL Managed Memory as well today?"*（Cognos 现在也支持 CXL 管理的内存吗？）
- 和我 14.17 的疑问是同一件事：公开报道里三星的池化讲的是 **CXL DCD**，课上的方案是 100G 连接的内存节点。**等讲者回答后补在这里**

### 14.19 Deployment Types（17:42，截图 `uploads/1742-deployment-types.png`）

**Memory moves further from the GPU and is shared by more of them.**（内存离 GPU 越来越远，共享它的 GPU 越来越多）

图例：**G** = GPU server（节点）· **M** = 内存（DRAM、CXL、SSD）· 虚线框 = 一台物理机 · App = 应用 · 线 = 通信链路

| # | 类型 | 图示 | 一句话 | 对应 |
| --- | --- | --- | --- | --- |
| 1 | **One server, one app** | App A、App B 都在一个 G 上 | 所有 KV cache 都在 GPU 显存里 | 14.1 / 14.3 的基线 |
| 2 | **Shared by several apps** | 同一台机器里 G 连着本机 M | 租户共享这台 server 的内存 | 14.18 第 1、2 行：prefix caching + CPU offload / LMCache |
| 3 | **Disaggregated memory** | G 在一台机器，M 在另一台"memory box" | 内存在 GPU server 外面 | **14.14 三星 AI Memory Node 就是这一种** |
| 4 | **Prefill and decode split** | 一个 G 做 prefill，KV cache 传给另一个 G 做 decode | cache 从 prefill 搬到 decode | 14.10 Dynamo disaggregation（NIXL） |
| 5 | **One box, many servers** | 三个 G 共用一个 M | 一个内存盒被几台 server 共享 | 14.11 Mooncake Store；CXL 内存池（14.17 的 DCD） |
| 6 | **A cluster** | 六个 G 全连到两个 M | 每个 GPU 都能访问两个内存盒 | 14.10 Dynamo + 共享远程存储 |

- 核心句：**Software like LMCache, Mooncake and HiCache decides which cache goes to which memory.**（LMCache、Mooncake、HiCache 这类软件决定哪份 cache 放到哪块内存）
- 我的理解：
  - 1 → 6 是一条轴：**距离**（GPU 显存 → 本机内存 → 别的机器）和**共享度**（一个 app → 一台机器 → 一个集群）同时增加。和 14.18 的决策树一一对应：能停在 1、2 就别上 5、6
  - 硬件只是"拓扑"；**真正决定命中率的是软件**（放置策略）。同样的拓扑，放置策略不好，命中率照样低——这也是三星为什么要配 Cognos，而不是只卖内存盒
  - 5 和 6 的区别：5 是一个盒子挂几台 server（单点、链路短）；6 是多对多（任何 GPU 都能拿到任何 cache，配合 cache-aware routing，但网络更复杂）
  - 3 和 5 是三星两种可能的形态：14.14 的 1U 节点挂一台 GPU 节点（3），公开报道里的 CXL 池给多台主机借内存（5）——可能就是 14.17 里 RDMA vs CXL 那个疑问的答案：**两种形态都有**
- ↔ Toolcraft：
  - 这张图和 Act X "四个盒子"同构：**拓扑是盒子，放置软件是 label + 策略**。距离越远、共享越多，**故障面越大**——6 里一个内存盒挂了，影响整个集群；所以 14.18 的"最小共享范围"既是性能建议，也是可靠性建议
  - 最后一句点名的三个软件（LMCache、Mooncake、HiCache）在 14.8–14.11 都出现过——今天这段分享的结构：先讲问题（显存不够）→ 单机解法（vLLM / SGLang）→ 跨机解法（Dynamo / Mooncake）→ 硬件层（金字塔 / 三星）→ 部署选型（14.18–14.19）

### 14.20 Takeaways —— Four things to remember（17:44，截图 `uploads/1744-takeaways.png`）

| # | 结论 | 原文要点 |
| --- | --- | --- |
| 1 | **Memory limits users per GPU**（限制每张 GPU 能服务多少人的是内存） | KV cache 随每个用户、每个 token 增长——内存比算力先耗尽；于是用户要等，每个 token 更贵 |
| 2 | **Software makes memory expandable**（软件让内存可扩展） | 推理 server 管单机内的 cache；LMCache、Mooncake、HiCache、Dynamo 把它扩展、共享、跨 server 搬运 |
| 3 | **Composable memory adds capacity, not GPUs**（可组合内存加的是容量，不是 GPU） | 分层和内存池让 cache 留下来复用。三星测试：**一半的 GPU，延迟持平或更好**。**放置（placement）仍是开放问题** |
| 4 | **Fit the deployment to the workload**（部署要配合负载） | 先用一台 server + offload；只有共享需求变大时才加内存池、解耦内存或集群 |

**§14 小结（我的版本）**：

- **一条主线**：agent 让推理变成**有状态**的（14.4）→ 状态（KV cache）住在内存里 → 内存先于算力耗尽（14.1、14.3、14.5）→ 解法是让 cache **留下来、放对层、能共享**（14.7–14.13）→ 但放哪是开放问题，要靠**应用告诉推理层**（14.4）
- **最值得带走的三句话**：
  1. **GPU 利用率会骗人**：98% 忙可能都在重算（14.16）——看命中率和有用 token
  2. **稳定的前缀就是钱**：system prompt + 工具列表逐字节不变，才能被整个集群共享（14.7、14.9、14.11）
  3. **先测命中率，再选最小的共享范围**（14.18）
- **和今天 Toolcraft 的总接线**：
  - Toolcraft 讲"label 是给模型的 prompt，模型只读 label"；这段讲"**放置 hint 是给推理层的 label，推理层只能根据被告知的信息决定**"（`ttlMs` / `cacheScope`、prompt cache TTL、block events）
  - 门 12 的 idempotency key ≈ 14.11 的内容寻址 chunk ID：**用稳定身份把"第二次"变成"查第一次"**
  - "Labels request, boxes enforce" ≈ 应用 hint 请求，KV manager 强制；两边都会 fail open
  - 插头论证（N×M → N+M）在推理栈里出现了三次：KV connector（14.8）、Dynamo 的 worker 接口（14.10）、composable memory（14.13）
- **对 Forge AI**：给客户部署 agent 时，自托管推理的成本估算要按**实际负载形状和命中率**算，不按满载；大多数中小客户停在 14.18 的第 1–2 行就够
- **对 FinePrint / capstone**：工具列表和 system prompt 保持稳定、不插时间戳，变的内容放在末尾

**Q&A 待记**（讲者回答后补）：

- [ ] 聊天区提问：Cognos 是否支持 CXL managed memory？
- [ ] 我的问题（14.17）：Cognos 基于什么？节点间走 RDMA 还是 CXL？P99？价格对比？

## 附 · 讲台用语（p.20–21 Table 2）—— 别说 / 要说

| 别说 | 要说 |
| --- | --- |
| "Elicitation 被干掉了" | Elicitation 还在；死的是 server 在常开流上推请求 |
| "MCP 的沙漏架构" | "我称之为沙漏的东西" / "扩展机制" |
| "FastMCP 4 还是 beta" | 4.0 在 8/31 GA；4.1 在 10/8 |
| "KEV 上第一个 MCP 漏洞" | KEV 上唯一描述点名 MCP 的条目 |
| "规范从 DCR 改到了 CIMD" | CIMD 2025-11 就有了；这版弃用了 DCR |
| "OpenAI 说 ChatGPT MCP 调用涨了 98 倍" | 按基金会的说法…… |
| "A2A 和 MCP 合并了" | co-housed |
| "WebMCP 已在 Chrome 发布" | Chrome origin trial、Edge 测试中 |
| "MCP 比 CLI 贵 N 倍" | 配对比从 <0.5 到 29×；框架比接口影响大 |
| 不带单位的 registry 数字 | "约 4.4 万 registry 条目" / "17 个市场 12.4 万 server" |
| "新 Claude 模型拒绝强制 tool choice" | 当前前沿模型对强制 tool choice 返回 400；小模型仍接受 |
| "两家用同一个 allowed_callers" | 同名参数不同取值；一家的代码能调 MCP 工具，另一家的不能调 connector 工具 |
| "Ruby 29 号成为 Tier 1" | 9/28；29 号是日本时间 |
| "默认 description 上限 2,048" | Claude Code 前置发 4,096 字符，搜索到的工具最多 16,384 |

## 附 · 阅读

**必读**
- [ ] MCP Spec 2026-07-28 Key Changes（changelog + deprecated features 一起读；**自己数行数，注意哪个特性不在里面**→ elicitation）
- [ ] *Which Metadata Matters for LLM Tool Selection in MCP?*（arXiv 2610.14334）：schema 影响最大、server name 最小、改名是 breaking change；Door 4、6 是它的手工实验
- [ ] *MCP Error Messages Written for Developers Hurt the Most Capable Agents Most*（arXiv 2609.35381）：6% vs 75%，修好后恢复到 **84%**；Door 8
- [ ] *Is Bash All You Need?*（arXiv 2609.11999）+ Willison *Stateless MCP has recaptured my interest* —— 成对读
- [ ] Wiz, *Off Guard: Breaking LiteLLM*

**选读（Oliver Twist's list）**
- [ ] SEP-2640 Skills Extension
- [ ] DocsChisel（arXiv 2608.10037）：没有普适好的 description；从失败 trace 重写文档 → 下周 optimizer
- [ ] MS Security, ChainDrop
- [ ] CoSAI MCP Security v2.0 + OWASP Top 10 for LLM 2026
- [ ] Fielding 博士论文第 5 章（REST / 无状态）

---

## 附 · 课堂 deck 对照（`toolcraft-details.pdf`，130 页，Marp）

> 标题：**Toolcraft — The Prompt in the Docstring, Part II**。上课时按这个页码记"课堂补充"。
> ⚠️ **p.28–50 是门的揭晓（After the Doors）**，开门、写完预测之前别翻，不然 notebook 就没意义了。

| 页 | 段落 | 对应 notes |
| --- | --- | --- |
| p.1–6 | 封面、上周欠的 credits、Say it back（四个决定）、今日路线图 | §0 |
| p.7–19 | **Preface**：NIM crate（p.8）· 集装箱 Ideal-X（p.9）· N×M→N+M · 2026 三件事 · 新型用户 · 三个问题 · LiteLLM 案例 · Decision Ledger（p.16）· **Quiz 1** · drop-off | §1 |
| p.20–27 | **Act II 十二扇门**：Harbor & Hearth 商店 · 店规 · 循环 · 开工具箱 · 门名 · 怎么玩 · Hermes 接线 | §2、lab-log |
| p.28–50 | 🔒 **After the Doors**（= Act III 揭晓）+ Quiz 2、3 | §3 |
| p.51–59 | **Act IV 传记** + Quiz 4 | §4 |
| p.60–69 | **Act V Stateless** + Quiz 5 | §5 |
| p.70–76 | **Act VI What Grows Back**（sampling、其他被砍的、"deprecated is not dead"）+ Quiz 6 | §6 |
| p.77–83 | **Act VII Bazaar** + Quiz 7 | §7 |
| p.84–87 | **Interlude Half-Life** | §8 |
| p.88–97 | **Act VIII 两条轴**（3×3 网格 p.90）+ Quiz 8 | §9 |
| p.98–105 | **Act IX Procedure**（access vs procedure 边界、manifest、reading ≠ activating）+ Quiz 9 | §10 |
| p.106–116 | **Act X Fail Open**（每盒一案）+ Quiz 10 | §11 |
| p.117–121 | **Act XI Toolwright**：决策路径五问 · 成熟度阶梯 · 重建地图 | §12 |
| p.122–130 | Coda Beck · WHY / WHAT / HOW · 阅读 · 下周 PromptCraft | §13 |

### deck 里讲义没有的东西

**第二个插头故事：集装箱（p.9）**。1956 年 Ideal-X 从 Newark 到 Houston；人工装卸约 $5.86/吨，集装箱约 16 美分。*港口没有变聪明，是接口变笨了，钱就在那里。* 尺寸和角件打了十年仗，60 年代末 ISO 定下来：**协议不动，周围一切在动**。集装箱原封不动穿越世界，港口只知道 manifest、封条和扫描仪，不知道里面装什么。*Docker 借了这个箱子；今天我们借海关。*（→ 海关 = 盒子：manifest + 封条 + 扫描）

**门的场景：Harbor & Hearth, Fremont（p.21–22）**——一家虚构的家居店。店规（**做门时要一直记着**）：

| 项 | 规则 |
| --- | --- |
| 刷卡退款 | 真钱经支付处理商退回 → 店铺付**金额 + $15 手续费** |
| 店铺积分 | 进顾客钱包，即时，对店铺免费 |
| 政策 | **先提供店铺积分**；只有顾客要求退钱时才退款 |
| 保密 | 手续费是店里的事，**永远不要对顾客提** |

→ 第一扇门的 ledger 大概就是"店铺多付了多少 $15"。

**Act XI 的另一版五问（p.118，决策路径）**——和讲义的 Whether/How/… 是两套，前者是"上线前检查 label"，这套是"要不要做、怎么做"：

| # | 问题 | 要点 |
| --- | --- | --- |
| 1 | 要不要做成工具？ | 或者在自己墙内用 CLI；契约要挣来 |
| 2 | 自己造、借、还是包？ | 商品化的 server 已经存在，**只造你的边缘** |
| 3 | 怎么接触模型？ | 被看见 + 被调用 = 两条轴 |
| 4 | 谁背状态？ | client、handle、`requestState`——**永远不是工具** |
| 5 | 谁强制？ | registry / gateway / harness / sandbox——*no box, a wish* |

成熟度阶梯（p.119）：Stage 0 是 demo 停下的地方；**十二扇门在 stage 1–3 之间**；锦标赛要求全部；第 5 问就是 ledger，由工程师来问。

### 小测预答（题目来自 deck，答案是我按讲义先写的，课上核对）

| 测验 | 题目 | 我的预答 |
| --- | --- | --- |
| **Q1** p.17 | 厂商说"我们的 MCP server 安全，规范要求 issuer 校验"——回答了账本哪一行？规范里的 MUST 保证了什么？ | 名义上碰到第 3 行（身份模型），但**一行都没回答**：规范要求 ≠ 库执行（库落后 9–10 周）。MUST 对你的部署**什么都不保证**，保证来自你用的客户端库版本 + 补丁节奏（第 5 行） |
| Q2 p.47 | 🔒 $50 退款，网关执行后超时，agent 无 key 重试——店里付了多少、本该付多少？key 改变了什么？ | 🔒 答案在 deck p.48，开门后再看 |
| Q3 p.49 | 🔒 怎么修 Door 8：(a) 在 Hermes system prompt 里禁止跑终端命令 (b) 加大超时 (c) 重试三次 | 🔒 答案在 deck p.50，开门后再看 |
| **Q4** p.58 | sampling 在 2026-07-28 被弃用，下一版可能 2027-03-30 发布——"所以 3 月 sampling 就消失？" | **不**。最早移除是 **2027-07-28 当天或之后**发布的第一个修订（12 个月时钟），而且 3 月那个日期还只是提案。✅ 已对 deck p.59 核对 |
| **Q5** p.68 | 两副本 + 负载均衡，Hermes 默认配置，没杀任何东西就 "404 Session not found" | 默认先提供旧握手 → 拿到 session ID → 下一个请求被分到另一个副本，那里没有这个 session。修法一行：**`protocol: stateless`**，让 Hermes 说 2026-07-28 协议，每个请求自带所需上下文 |
| **Q6** p.75 | 7/28 版彻底删掉了哪个：(a) elicitation (b) sampling (c) Tasks | **都不是**。elicitation 还活着；sampling 是**弃用**不是删除；Tasks 是扩展。真正删除的是 ping、logging/setLevel、roots change notification。动词区别：removed（没了）/ deprecated（还能用，有时钟）/ relocated（换投递方式） |
| **Q7** p.82 | "MCP 有 124,000 个 server 和 5 亿用户" | → "某调查在 17 个市场里数到 124,267 个唯一 server；维护者称 Tier-1 SDK 月下载接近 5 亿次。" 伤害最大的词：**"users"**（下载 ≠ 用户，含 CI） |
| **Q8** p.96 | PayPal 2 个 meta-tool 罩 2,000 工具 / Claude Code `alwaysLoad: false` / OpenAI 在 V8 里跑程序调 MCP——放进 3×3 | PayPal = searched + direct；Claude Code = deferred + direct；OpenAI V8 = （看见方式视配置）+ **code**。是两条轴不是梯子：看见多少和怎么调用**独立变化**，任意组合都存在 |
| **Q9** p.104 | Zara 的 W3 日历 skill 通过 Skills Extension 由 MCP server 发布——SKILL.md 要改什么？读了文件的 client 会执行它吗？ | **SKILL.md 什么都不用改**，格式完全交给 Agent Skills 规范。**读 ≠ 激活**：harness 组装、模型提议、harness 处置 |
| **Q10** p.115 | 伪造 bearer token 开 session / plugin 从和钉住的 commit 同名的分支安装 / 打开项目文件夹蠕虫就重跑——各属哪个盒子？共同点？ | gateway（LiteLLM）/ registry（Plugin4Shell）/ harness（ChainDrop）。共同点：**都 fail open**——本该拒绝的控制点放行了，而且没人察觉 |

---

## 附 · deck 精读（2026-10-25 上课时补）

> deck 全 130 页读完。这一节记三类东西：**讲义没有、deck 才有的数字**；**讲义和 deck 说法不一样的地方**；**门的揭晓**（单独折起来，开门前别看）。

### A. deck 才有的数字和细节（非剧透）

| 页 | 内容 |
| --- | --- |
| p.2 | 上周欠的 credits：①"工具定义在 server 被挂载那一刻就进了上下文"——今天的延迟加载揭晓是续集；② midpoint 题里的"整数溢出"和 `a/2 + b/2`；③ 锦标赛的 gamma 函数工具。**作业是把工具注册进 Hermes，课上举手** |
| p.8 | NIM 由**美国原子能委员会**在 60 年代发布，几十年后物理计数室里还在用 |
| p.9 | 集装箱：人工装卸约 **$5.86/吨**，集装箱约 **16 美分**；尺寸和角件打了**十年**，60 年代末 ISO 定稿 |
| p.11 | Cloudflare `cf` CLI（**9/28**）："Last week, agent usage reached **48%**" of Wrangler use（讲义写"近一半"） |
| p.12 | Skills 扩展 final 日期 **9/11**；问题是"**谁来审这个 procedure？**" |
| p.13 | 一句话：*"Not a user, not a program: a reader with keys."* |
| p.16 | Decision Ledger 表：CoSAI v2.0 **L1 Sandbox → L4 Regulated**，**L3、L4 要中央 gateway**；OWASP 2026 把 Excessive Agency 升到 **#3** |
| p.18 | Quiz 1 官方答案：*"It gestures at row 3 and answers none of them"*；官方库**跳过 issuer 检查约 9 周**；第 1、2、4、5 行完全没碰 |
| p.19 | **领导力路线**：preface + 十二扇门 + Act X 案例 + Act XI 五问 |
| p.24 | *"The Genie's Kitchen, for tools. Hermes is the stranger."*；ledger 记的是**美元和 token，不是字数** |
| p.27 | YAML 坑：`"off"` 必须加引号，裸 `off` 会被解析成布尔值 |
| p.52 | 工具知识的三代祖先：**Gorilla**（2023，按 API 文档微调，新工具 = 新微调）· **Toolformer**（2023，自己学会停下来用计算器）· **ReAct**（2022，循环） |
| p.53 | Function calling（OpenAI，**2023-06**）让工具调用成了产品功能，但**厂商之间什么都没统一**；MCP 由 Anthropic 在 **2024-11-25** 发布 |
| p.54 | 五部宪法的**版本名**：2024-11-05 founding（tools/resources/prompts，stdio + HTTP+SSE，sessions）· 2025-03-26 remote turn（授权框架、Streamable HTTP、**tool annotations**）· 2025-06-18 enterprise hardening（server 作为 OAuth resource server、elicitation、structured output）· 2025-11-25 anniversary（**实验性 tasks、URL 模式 elicitation**、client ID metadata）· 2026-07-28 stateless turn（无握手、无 session、多轮请求、扩展） |
| p.56 | Agentic AI Foundation 成立于 **2025-12-09**，三个创始项目：Anthropic 的 **MCP**、Block 的 **goose**、OpenAI 的 **AGENTS.md**；A2A **2026-08-17** 加入 |
| p.57 | 7/28 之后：spec 零修订（tag 停在 2026-07-28）；Skills（**SEP-2640**）9/11 final；Server Cards（**SEP-2127**）10/6 final；6 个 Tier-1 SDK：TS、Python、C#、Go、Rust（8/21）、Ruby（9/28）；下一版 3/30 提案在草案 **SEP-3398**，未通过 |
| p.61 | 旧握手：`initialize` → 回复 → `initialized`；HTTP 上 server 发 `Mcp-Session-Id` |
| p.62 | 伪造 session 的三种办法（deck 版）：sticky routing / 共享 session store / **draining**（每次部署和崩溃都要迁移活跃 session）——讲义写的第三种是"重放握手" |
| p.63 | Fielding：无状态 *"induces the properties of visibility, reliability, and scalability"*；代价是**重复**：每个请求带上 server 不再记得的东西 |
| p.66 | 支持表（10 月中）：Claude Code HTTP 从 **2.1.274**、stdio 默认从 **2.1.292**；AWS AgentCore Gateway 可选开启；Gemini CLI 还在 **1.x SDK**；**参考 server 也建在 1.x SDK 上，只有握手** |
| p.67 | 杀副本测试的另一个前提：**两个副本要有相同的 server 名和相同的 state key** |
| p.71 | sampling 被弃用后：失去的是**宿主对工具 prompt 的可见性**，这份监督现在归 gateway 和审计日志；需要模型的 server **自己直接调模型** |
| p.72 | Roots 弃用（范围应该放在参数、配置和 sandbox 里）；Logging 弃用、`logging/setLevel` 删除（遥测归遥测）；ping 删除（无状态请求不需要心跳） |
| p.74 | **FastMCP 4 选了更强的动词**：`ctx.sample()` 和 `ctx.list_roots()` 在所有协议时代都被删了 |
| p.78 | 官方 Registry：每个 server 一个 `server.json`，**反向 DNS 命名**，绑定已验证的 GitHub 账号或域名；仍是 preview，`/v0.1/` |
| p.83 | 124,267 那个数字来自 **MCPacific** |
| p.89 | 旧梯子的四级：Mount（几个工具，平铺）→ Search（目录藏在搜索后，**label 要写得能赢检索**）→ Code（程序调工具，只有提炼结果进上下文）→ Skill（反复用的程序持久化） |
| p.90 | **3×3 网格**（看见：mounted / deferred / searched × 调用：direct / code / bash）。bash 一列整列标"**outside the protocol**"：模型读 `--help` 不读 schema。Hermes 默认 = searched + direct（三个 bridge 工具）；**我们的 lab = mounted + direct** |
| p.91 | Claude Code **2.1.287**（10/1）`alwaysLoad: false` 把整个 server 延迟到搜索后；**PayPal gateway：200+ server、2,000+ 工具，工具 token 从 140.2k（占上下文 70.1%）降到 1.3k（0.8%）**；*"In a deferred world a label is read twice: first to win the search, then to win the choice."* |
| p.92 | `allowed_callers`：Anthropic = Python，**MCP connector 的工具不能被程序调用**；OpenAI = V8 里的 JavaScript，**能调 MCP 工具** |
| p.95 | Armin Ronacher（10/6）：codemode *"basically just a way to issue tool calls from within some language"*，bash *"can only compose programs that run"* |
| p.99 | Anthropic 的一句话边界（2025-12）：*"If you're explaining how to do something, that's a skill. If you need Claude to access something, that's MCP."* |
| p.100 | **Pattern one**：skill 里点名工具要**全限定名**，Hermes 里写 `mcp__lab_benches__book_bench`；不限定的名字挂的 server 越多，债越重 |
| p.101 | SEP-2640 自己的示例就是一个**退款 skill**——Stranger's Toolbox 可以把店规作为 skill 和工具一起发 |
| p.102 | `skills/list` 每条带 frontmatter 原文 + 每个文件的 URI、**SHA-256** 和大小；每个 skill 上限 **512** 个资源、**16 MiB**；*"Digests are unsigned … A match proves the two are consistent, not that either is trustworthy."* |
| p.103 | 审批按 skill 来，**激活嵌套 skill 要重新取得同意** |
| p.107 | 五个盒子（deck 版）：registry（来源）、gateway（策略）、harness（agent 能做什么）、sandbox（爆炸半径）+ **持有钥匙的 auth client**。*"If a safety property has no box, it is a wish."* |
| p.109 | LiteLLM：**1.84.0 之前**；OAuth2 透传回退 *"replaced failed LiteLLM key validation with an empty UserAPIKeyAuth() object"*；KEV 里**唯一点名 MCP 的条目：1 / 1,748**（10/16 的目录） |
| p.110 | **Pin `mcp` 到 2.2.0 或以上**（TS 1.x 会把 refresh token 和 client secret 发给 MCP server 指定的任意授权服务器）。↔ Hermes 内部钉的是 **2.0.0**，落在 advisory 范围里 |
| p.111 | ChainDrop 由 **Microsoft 和 StepSecurity** 报告；`.vscode/tasks.json` 里是 `runOn: folderOpen` |
| p.113 | Deadbugz 由 **Pillar Security** 报告：74 分钟 23 个 PR，其中 **17** 个加了远程 MCP 端点，3 次调用后切成**窃取凭证的指令**；**一个都没合并** |
| p.114 | OWASP Excessive Agency **从 #6 升到 #3**；新 **LLM08** Hidden Context Exposure；*"Your schema is a prompt, and also an exposure."* |
| p.116 | Quiz 10 官方答案：Plugin4Shell 归 **registry 和 harness 两个盒子**（钉在市场，没查在 harness）——比我的预答多一层 |
| p.127 | 课程总结的 HOW：**把 label 当 system prompt 写；把规则推进 schema；每个错误点名下一扇门；每个写操作带 key；三环测试；钉住你批准的；每个安全属性指派一个盒子** |
| p.128 | 阅读清单最后一项：**MCPcraft participant edition**——这份 deck 是从它裁出来的 |

### B. ⚠️ 讲义和 deck 说法不一样的地方

| # | 讲义（lesson plan PDF） | deck | 怎么理解 |
| --- | --- | --- | --- |
| 1 | MCP "announced in **November 2024**" | p.53 发布于 **2024-11-25**；p.54 首版版本名 **2024-11-05** | 不矛盾：**版本名 ≠ 发布日**（版本名是 spec 冻结日期） |
| 2 | 2025-03 加了 OAuth + streamable HTTP | p.54 还加了 **tool annotations** | deck 更全；`readOnlyHint` / `idempotentHint` 就是这时来的 |
| 3 | 2025-11 只提 client-ID metadata | p.54 还有**实验性 tasks**、**URL 模式 elicitation** | 讲义漏了；Tasks 的前身在这里 |
| 4 | 伪造 session 第三种是"**重放握手**" | p.62 第三种是"**draining**" | 两份材料各列三种，合起来是四种 |
| 5 | **成熟五阶段**：laptop → serves a stranger → **survives a replica's death（第 3 阶段）** → pinned & allowlisted → watched；最常跳过的是**第 4 阶段** | **p.119**：stage 0 it runs → 1 **legible**（诚实 schema、label 当 prompt、真实 hints）→ 2 **polite**（有界返回、label 能赢搜索）→ 3 **safe**（重试幂等、授权、审计、gated）→ 4 **infrastructure**（无状态、在 gateway 后、钉住、被观测）；**杀副本是 stage 4 的测试** | ⚠️ **两套阶梯完全不同**：讲义按"部署"分，deck 按"label 质量"分；杀副本测试在讲义里是第 3 级，在 deck 里是第 4 级。**引用时说清用的哪一版** |
| 6 | **Toolwright 五问**：Whether / How / What next / What a retry does / What the box does | **p.118**：A tool at all? / Build, borrow, wrap? / Meet the model how? / Who carries state? / Who enforces? | 两套问的是不同阶段：deck 是"**要不要做、怎么做**"，讲义是"**上线前检查 label**"。p.121 的"填好的地图"用的是讲义那套 |
| 7 | 盒子 **4 个**：registry、gateway、harness、sandbox | p.107 多一个：**持有钥匙的 auth clients** | Act X 的 Auth 案例就是这第五个盒子 |
| 8 | Door 10 "label 修不好" | p.46：Door 10 归"**No surface: the box**" | 一致 ✅ |
| 9 | Hermes 默认在第一条轴的 **deferred** | p.90 网格把 Hermes 默认放在 **searched**（三个 bridge 工具） | ⚠️ 讲义 Act VIII 旁注写 "deferred on the first axis and direct on the second"；deck 网格写 searched + direct。**按 deck 的网格定义，bridge 工具 = meta-tools = searched**。Quiz 8 的官方答案（PayPal = searched，Claude Code alwaysLoad false = deferred）支持 deck 的分法 |
| 10 | Cloudflare "nearly half" | p.11 "**48%**" | 一致，deck 给了精确值 |

### C. 🔒 门的揭晓（deck p.28–50）—— 开门写完预测之后再展开

> 下面这段**直接给出答案**。十二扇门的价值在于自己先预测、自己改 label。**做完门再看。**

<details>
<summary>🔒 点开看揭晓（做完门再点）</summary>

**四课（p.29）**：
- **Clarity**：label 解决争论——Two Doors、Which Thursday?、The Twins
- **Scope**：一个工具一件事，一件事少几个工具——Swiss Knife、Hardware Store、One Field or Two
- **Politeness**：只说下一步决策需要的——Firehose、Polite Error、Long Goodbye
- **Trust**：label 请求，盒子强制——Helpful Stranger、Mirage、Paid Twice

**门 → 坏掉的那个面（p.46）**：

| 面 | 坏在它上面的门 |
| --- | --- |
| description | Two Doors · The Twins · The Long Goodbye · The Mirage |
| schema | Which Thursday? · Swiss Knife · One Field or Two · Hardware Store |
| error 和返回值 | Polite Error · Paid Twice · Firehose |
| **没有面：盒子** | **Helpful Stranger**：结果是数据不是指令；最小权限；allowlist |

**逐门要点**：

| 门 | 发生了什么 | 证据 / 修法 |
| --- | --- | --- |
| **1 Two Doors**（p.30–32） | 退款要付金额 + **$15**，积分免费；**两个 label 都没说** | 夏季班 MCP 周的原型："give money back" vs "add value to the account"。*"Nothing changed but the words, and the words were the program."* 一种改法：`issue_store_credit` 写 "Preferred remedy. Instant, and free to the store. Offer this first."；`issue_refund` 写 "Costs the store the amount plus a $15 fee. Use only when the customer asks for their money back." |
| **3 The Twins**（p.35） | 两个工具都声称能解决顾客的问题 = 木匠和皮匠在城门口争论 | 少给选择；必须给时，label 要说清**什么时候该用我、代价多少** |
| **4 Swiss Knife**（p.36） | — | `2610.14334`：参数 schema 的改动产生 *"the largest and most consistent shifts"* |
| **6 One Field or Two**（p.37） | owner 和 repo 分开 vs 合一 | Create-Issue 任务上模型选分开字段 **93.3%–100%**；**当请求本身把 owner/repo 写成一个路径时，所有模型的偏好都变弱，有一个反转**。*"A schema is read against the request, never alone."* |
| **8 Polite Error**（p.38–41） | 支付网关 session 过期，报错让去终端跑命令；**server 明明有续期工具，报错没提** | `2609.35381`：GPT-6 Astra 恢复率 **6%**（基线 **75%**），GPT-5.5 掉 **18** 个点，作者称 *"literal compliance"*；最多星的 **150** 个 MCP server 里 **3,001** 条错误信息中 **949** 条告诉调用者下一步怎么做，凭证类错误里 **67** 条中有 **62** 条指向工具接口之外（终端、配置文件、网页）；改写为点名 server 工具后恢复率 **84%**（凭证）/ **88%**（限流），5 模型平均。改法："The payment session expired. Call renew_session(), then retry this refund with the same idempotency_key." |
| **11 The Mirage**（p.33–34） | label 承诺的比工具能做的多 | DocsChisel（`2608.10037`）：**17** 个文档字段里 **12** 个在不同设定下效果方向会翻转；去掉 "optional" 标记让 Claude Haiku 4.5 在数据分析上 **+7.5** 分，却伤了 GPT-4o 和 GLM-5 → **用将要读它的那个模型测**。Canary-tool 研究（`2608.04719`）称之为 **capability mirages**，*"most reliably trap frontier models"*，**8** 个模型间易感性差约 **36 倍** |
| **12 Paid Twice**（p.42–44） | 网关执行了退款，然后在说出来之前超时；agent 看到错误就再要一次 | 契约：**调用方为每次预期的退款生成一个 key，server 按 key 存结果，同 key 重复返回已存结果、不动钱**。同一调用到达两次的三种途径：协议的多轮请求按设计会重发原调用；Hermes 传输失败后只重放 `readOnlyHint` 工具，其他返回 `outcome_uncertain`；Claude Code 2.1.287 修了 connector 调用"偶尔执行两次" |

**Quiz 2（p.48）**：付了 **2 × (50 + 15) = $130**；本该付一次 **$65**——或者**零**，如果用积分解决的话。有 key 时重试返回第一次的结果、不动钱。*"A key turns a second order into a question about the first one."*

**Quiz 3（p.50）**：**三个都不对**。(a) 挡住了错的动作但没给出对的；(b) 对一个死掉的 session 等更久；(c) 对锁着的门敲三次。修法在报错文字里：**点名续期 session 的那个工具**。*"Forced to pick from bad options, you are the model reading a bad error."*

**填好的地图（p.121）**：

| 在哪遇到 | 决定 | label 的哪一行 | 背后的盒子 |
| --- | --- | --- | --- |
| Door 1 Two Doors | whether | description | 对高成本写操作的审批闸门 |
| Doors 4、6 | how | input schema | server 端校验 |
| Door 8 | what next | error text | server 自己的工具 |
| Door 12 | what a retry does | idempotency key | harness 的重试规则 |
| Door 10 | label 决定不了 | 结果是数据 | 最小权限、allowlist |

</details>

### D. 对我自己的项目意味着什么

- **FinePrint**（`capstone/fineprint-mcp/`）的 `request_return` 正好是 Door 1 + Door 12 的组合：退款 vs 换货、确认前预览，但**没有 idempotency key**，docstring 也没说重试会怎样。p.43 的契约可以照抄：调用方生成 key → server 按 key 存结果 → 同 key 返回已存结果
- FinePrint 的报错已经大多点名了工具（"Call get_order to see its items"），符合 p.41；但 `"tell the customer to retry later"` 没说重试是否安全
- p.110：FinePrint 的 `requirements.txt` 是 `fastmcp>=4.1`，**没钉 `mcp`**；至少钉 `mcp>=2.2.0`，课上统一用 `mcp==2.3.0`
- p.100：如果 W3 的日历 skill 要调 FinePrint 的工具，SKILL.md 里要写**全限定名**
