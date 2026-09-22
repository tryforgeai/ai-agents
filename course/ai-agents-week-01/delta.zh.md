# Week 01 增量 — 相对 Week 00（2026-09-20）

> 规则：Week 00 已讲过的**不重复写**，只在这里记四类东西。
> 基线：[`../ai-agents-week-00/summary.zh.md`](../ai-agents-week-00/summary.zh.md)

## ① 新增 — Week 00 完全没有的

### 1.1 Skill vs Agent（subagent）的区分

Week 00 讲了 harness，但没拆过 harness **内部**的这两种扩展方式。

| | **Skill** | **Agent（subagent）** |
| --- | --- | --- |
| 本质 | 按需加载的**指令 + 附带脚本/资源** | **独立的 Claude 实例**，自带 context 窗口和工具白名单 |
| 谁执行 | 当前 Claude，在当前对话里 | 新开的 Claude，跑完把**结论**返回主 Claude |
| 何时用 | "做这类任务要按这个流程/标准" | "这活要读 50 个文件，别把垃圾塞进主上下文" |
| 成本 | 只加载 SKILL.md（几百 token） | 一整个新对话 |

> **不互斥。** Skill 的第 N 步可以写"派一个 subagent 去做 X"。
> 🔑 **Skill 是剧本，Agent 是演员。**

判据：`SKILL.md + 脚本 + 编号步骤 + 一次 MCP 调用` → 这是 **Skill**，不是 Agent。

### 1.2 ⭐ 记忆的三分法（Week 00 明确缺失，今天补上）

Week 00 把「memory 架构」列在**未展开缺口**里。今天用认知心理学经典三分（Tulving）给 agent 记忆分层：

| | 内容 | 讲师的例子 | 特性 |
| --- | --- | --- | --- |
| **Episodic**（情景） | 带时间地点的**经历** | *went to Paris, June 15 2026* | 第一人称、可追溯、会遗忘 |
| **Semantic**（语义） | 脱离情境的**事实** | *Eiffel Tower is in Paris* | 非人称、可共享、**"books contain semantic memory"** |
| **Procedural**（程序） | **know how** | 怎么骑车 | 说不清、只能演示 |

**关键是三者的关系，不是并列：**

- **Semantic 从 Episodic 蒸馏而来**（consolidation）：去过几次巴黎 → 沉淀出"铁塔在巴黎" → **原始经历可忘，事实留下**
- **Procedural 最难外化** —— 读一百本骑车的书也不会骑，所以书本装不了它

**映射到 agent：**

| 人 | agent |
| --- | --- |
| Episodic | **trajectory / 会话历史**（这次跑了哪些步、工具返回什么） |
| Semantic | **知识库 / RAG / profile 事实字段** |
| Procedural | **skills / tools / playbook**（= SKILL.md 那套） |

**三个判断：**

1. **三层写入权限完全不同**：episodic 系统自动只追加；semantic 要蒸馏（**谁批准？**）；procedural 通常人写
2. ⚠️ **"蒸馏"那一步是风险点** —— 客户随口说"这次要便宜的"（episodic 事实）→ 模型记成"该客户价格敏感"（semantic 断言）= **未经验证的 consolidation**。对应 Week 00 失败模式表的 **Wrong belief in the record**（"no path back"）
3. **Voyager 那篇讲的就是 procedural memory** —— 把成功做法固化成**可执行 code skill** 而非文字总结，因为 procedural 本来就说不清、只能演示

**第四件事：三层怎么检索和注入？**

分类容易，难的是每轮往 context 塞哪些、塞多少。塞太多——老客户的 context 无限增长，成本和不稳定性一起上；塞太少——agent 忘了它本该知道的事。

> ✅ **老师明确说本课程后面会讲。** 不是缺口，是伏笔。
> 推测落点：**模块 03「Context, instructions & personas」**（决定什么进 context 窗口）。但大纲 16 个模块目前只看到 9 个，也可能有专门的 memory 模块在后半段。
>
> **到那时要带着问的**：检索策略是按相关性、新近性、还是重要性加权？（Generative Agents 那篇用的是三者加权）

### 1.3 教学 demo 的四条设计约束

（针对"10 分钟内让人看懂为什么需要 skill"这个目标，不是通用工程建议）

1. **必须有失败对照** —— 不用 skill 时 Claude 怎么做（随意、不可复现）→ 用了之后怎么做。没这个对比，观众只会觉得"这不就是 prompt 吗"。
2. **Python 脚本要承担 LLM 干不好的活** —— 脚本管确定性计算（切分 / 去重 / 哈希 / 统计 / 打分），LLM 管判断（这块内容有价值吗）。脚本干的事若 LLM 也能干，就演示不出分工。
3. **MCP 调用要在脚本之外** —— MCP 是 Claude 调的，Python 脚本拿不到 MCP 连接。这个边界最容易搞错，值得专门设计一步来展示。
4. **步骤数 7–8 刚好** —— 少于 5 步显得不需要 skill，多于 10 步演示跑不完。

### 1.3 七到八步骨架（以 RAG corpus prep 为例）

```
1. 确认范围        ← 和用户对齐：哪个 space、多久之内
2. MCP 拉取        ← Claude 调 Confluence/SharePoint MCP，落盘成 raw/
3. 检查一份样本     ← Claude 读 1 个文件确认结构（教"先探查再批处理"）
4. 跑 Python 脚本   ← 切分 + 去重 + 统计 → chunks.jsonl + report.json
5. 读 report       ← Claude 只看统计，不看全量数据（教"上下文预算"）
6. LLM 抽检        ← 对 report 标红的 chunk 做判断——这步只有 LLM 能做
7. 产出 + 已知问题   ← index-ready 文件 + 一份"这批数据的坑"
8. 验证            ← 重跑确认幂等 / 抽 3 条回查原文
```

**第 4 步 vs 第 6 步的对比 = 整个 demo 的教学核心：**

> 🔑 **能算的别让模型猜，要判断的别写死在代码里。**

---

**⚠️ 我对上面几条的核查**

- 约束 3「脚本拿不到 MCP 连接」——在 Claude Code / Cowork 这套 skill 机制里**成立**：脚本是 bash 起的子进程，不在 MCP client 会话里。但严格说这是**架构约定而非物理限制**——脚本自己带凭证去实现一个 MCP client 也能连，只是那样就绕开了 Claude 的审批与审计，不该这么做。教学时说成"**边界是故意画的**"比说成"做不到"更准确。
- 「只加载 SKILL.md（几百 token）」——对，这是 progressive disclosure：描述常驻、正文按需、脚本只在执行时读。
- 步骤数 7–8、10 分钟 —— 这是**经验值**，无出处，当作 demo 手感即可。

**↔ 与 Week 00 的关系**：这整块是 p.21「model + harness」那张图的**下一层展开**——harness 不是一坨，它内部有"剧本/演员"的分工。Week 00 的 [`ref-harness-engineering.zh.md`](../ai-agents-week-00/ref-harness-engineering.zh.md) 只讲到 harness 边界，没讲这层。

**待定（原讨论里悬着的）**
- [ ] 选题：RAG corpus prep（演示"数据进来"）vs RAG eval harness（演示"质量出去"）——后者 MCP 部分更有"哇"效果（从 Slack/Jira 真实提问挖 golden questions），但脚本复杂
- [ ] 现场跑 vs 学员自己装着跑 —— 决定 SKILL.md 要写多少防呆
- [ ] Zoom 三个 MCP server 当前 401 连不上，演示不可用；Confluence / Slack / SharePoint 通
- [ ] ⚠️ 真实企业数据投屏泄露风险 —— 需要准备 sanitized space

## ② 讲法不同 — 同一个概念，换了框架/比喻/术语

| 概念 | Week 00 的讲法 | Week 01 的讲法 | 我的判断 |
| --- | --- | --- | --- |
| **agent 的公式** | `agent = LLM + tools + loop` 被明确标为 **2023 年的旧说法**，当场推翻 → *"In 2026 the industry says it plainly: a decent model with a great harness beats a great model with a bad harness."*（notes p.21 段） | 先**口头**给出 `agent = LLM + tools + loop`（`loop = observe→reason→act ↻`），**下一页 p.21 照旧推翻** | ✅ **已确认：无降级。** p.21 原样保留 2026 那句反转。只是讲述节奏不同——口头先抛公式，翻页再打掉 |

> 补充：`LLM + tools + loop` 是**零件清单**，p.19 的定义是**行为定义**。清单说不出「谁在摇曲柄」，这正是他当初要换掉它的理由。

## ③ 被修正 — Week 00 的说法在正式课里被改了

*（待填。这类最值钱，记的时候连同"为什么改"一起记。）*

## ④ 被砍掉 / 降权 — meetup 讲了但正式课不提

*（待填。可能是 meetup 的煽动性内容，不进正式体系。）*

---

## 现场 Q&A

### Q1（我问的）：DeepSeek Harness Desktop vs Hermes Agent，该用哪个？

**得到的回答（原文要点）**

| 对比 | DeepSeek Harness Desktop | Hermes Agent |
| --- | --- | --- |
| 核心侧重 | 桌面工作台、插件扩展、项目管理 | 长期助手、记忆、技能积累、自动化 |
| 桌面体验 | 插件面板、会话管理、文件改动撤销 | 有桌面版，同时支持 CLI 和消息渠道 |
| 长期记忆与学习 | 非核心卖点 | 明确支持持久记忆、历史会话、自动生成技能 |
| 定时任务 | 内置调度面板，保留执行记录 | 通过 gateway 支持无人值守定时任务 |
| 编程工作流 | Git worktree 隔离、回合快照与撤销 | 终端、隔离环境、子 Agent |
| 消息渠道 | 通过 DSH-IM 接入微信 / 飞书 / 钉钉 | Telegram / Discord / Slack |

结论：长期积累经验、自动执行 → Hermes；桌面工作台 + 插件 + 代码项目管理 → DSH Desktop。

**⚠️ 我事后核查的三点**

1. **两边都真实存在**，定位描述大体准确。Hermes Agent 是 Nous Research 的开源项目（[官网](https://hermes-agent.nousresearch.com/) · [GitHub](https://github.com/NousResearch/hermes-agent)），持久记忆确实是核心设计——靠 `MEMORY.md` + `USER.md`，另外挂 8 个外部 memory provider 插件（Mem0、Supermemory、Honcho 等）。
2. **"DeepSeek Harness Desktop" 不是一个东西。** DeepSeek Harness（dsh）内核是官方的，但**桌面壳有一大堆同名社区 fork**——`dsh-tauri/`、`alanpeng/`、`AleCyriaco/`、`fendouai/`、`Antony-Jia/`、`z16166/dsh-desktop`… 功能各不相同。回答里列的"插件面板 / 回退 / DSH-IM 微信接入"**具体属于哪个 fork 要单独确认**，不能当成 dsh 的通用能力。选型时必须锁定具体 repo。
3. **"自我学习" ≠ 模型再训练**——原回答这个 caveat 是对的。Hermes 的"学习"是把成功做法存成 skill 文件复用。Nous 自己的基准说"积累 20+ 技能后同类任务快 40%"，这是**厂商内部数据**，不是第三方实测。

**↔ 与 Week 00 的关系**：这题正好落在 ACT V（The Engine Room）和 [`ref-harness-engineering.zh.md`](../ai-agents-week-00/ref-harness-engineering.zh.md) 上——harness 就是 model 之外的那一层。Week 00 p.21「model + harness」那张图可以直接拿来解释这两个产品的差别：**它们比的不是模型，是 harness**。

**待办**
- [ ] 如果要真选，用**同一个模型 + 同一个任务**跑一遍对比——功能定位表不等于实测排名
- [ ] 锁定 DSH Desktop 具体 fork 再评估

---

## Lab 记录 — 环境搭建与第一个 execution trace

**⭐ 确认的增量：lab 题目换了。**

| | Week 00 | Week 01（今天下午） |
| --- | --- | --- |
| 产出 | **newsletter** | **travel agent + profiles** |

要求：*"需要符合真正的 AI agent —— observe → reason → act，and loop."*

> **为什么换题（推测）**：newsletter 是自然语言输出，**verifier 写不出来**（题眼那句 *a newsletter it cannot be trusted to write alone* 正是此意）。travel agent 是 p.20 Maui 例子的长大版，verifier 相对干净——字段齐不齐可机器判定。
>
> **profiles 这部分正好对上"如何为每个客户记住偏好"那个设计问题**（见上方 Q&A / 记忆三层架构）。

**原大纲目标**：Set up the Python and lab environment; inspect a first agent loop and its execution trace.

### 环境

| 项 | 版本 / 配置 | 踩坑 |
| --- | --- | --- |
| Python | | |
| n8n | | |
| Ray | | |

### ⭐ 第一份真实 execution trace —— 标注版

**场景**：讲师现场 demo，某桌面 harness（侧栏：Sessions / Bots / Capabilities / Messaging / Artifacts / Scheduled jobs）。任务：查 Ashburn VA 天气。

> **为什么这份 trace 值钱**：它在 7 分钟里同时演示了 **loop 的成立**、**两次过早宣告胜利未遂**、**一次自发验证**，以及 **四处静默失败**。比任何抽象讲解都具体。

#### 逐步标注

| # | 内容 | 判定 |
| --- | --- | --- |
| 0 | 用户首次提问 → `Your request was not processed. Send it again if you still want me to carry it out.` | ✅ **governor 活的**。默认不动；不弹 yes/no，只是拒绝并把负担推回用户。**刹车比油门便宜** |
| 1 | 💭 *"can use web_search or web_extract... Best: use a quick API like wttr.in"* | ✅ 先比较方案 |
| 2 | ⚡ `curl -s "https://wttr.in/Ashburn,VA?format=j1"` → exit 0 | 🟠 **结构问题 1**：万能 `bash` |
| 3 | 💭 *"Also get local time. Let me run date."* | ✅ ⭐ **这一步不在任何计划里** —— *the next step is chosen by what it just observed, not by the drawing*（p.24 判据现场成立） |
| 4 | ⚡ `TZ=America/New_York date` → exit 0 | |
| 5 | 💭 *"Data observed at 10:06 PM... hmm that's ahead of local time 7:20 PM."* | ✅ 异常正确检出（3 小时差） |
| 6 | 💭 *"...**whatever. Let me just report.**"* | 🔴 **未遂 #1 · premature victory**。若在此收工，输出会带着已知异常且毫无标记 |
| 7 | 💭 *"**Actually could be UTC-ish.**"* | 🔴 **失败 #1 · 编造解释（已出厂）**。无证据地给异常编了个原因，且**从未回头验证**。后面的二次核查解决的是**温度**，从没确认过时间戳为什么偏 |
| 8 | 💭 *"Let me just note the observation time discrepancy **or avoid it**."* | 🔴 **未遂 #2 · 蓄意绕过**。比 #1 更重——**它已经把缺陷命名了**，却在掂量要不要绕开 |
| 9 | 💭 *"I'll do a quick second source check."* | ✅ 自我纠正。⚠️ **但是模型自己选的，harness 没有任何规则要求它这么做** 🟠 **结构问题 2** |
| 10 | ⚡ `curl open-meteo...&timezone=America%2FNew_York` → exit 0，返回显式 `timezone` / `utc_offset_seconds` | ✅ 选源正确——这个源能真正消歧 |
| 11 | 📄 输出 `as of 7:15 PM EDT`，只字未提时间差异 | 🔴 **失败 #2 · 不确定性被抹平**。输出干净不是因为没有不确定，是因为不确定被删掉了 |
| 12 | 📄 *"a light shower was reported nearby earlier"* | 🔴 **失败 #3 · 无出处的调和**。两源合成一句自信的话，读者看不出发生过合并 |
| 13 | 📄 `feels like 81°F` —— 但 wttr 返回的是 `FeelsLikeC: 26` ≈ **79°F** | 🔴 **失败 #4 · 静默的数值覆盖**。约 2°F 的真实分歧，单方面采信 open-meteo。*（据可见片段推断，待用完整输出核对）* |

#### 统计

| | 数量 | 谁拦住的 |
| --- | --- | --- |
| 🔴 未遂 | 2 | ✅ **模型自己**，不是 harness |
| 🔴 出厂的失败 | 4 | ❌ 无 |
| 🟠 结构问题 | 2 | — |

**所有调用都是 `exit 0`。** 从 harness 的视角这一轮完美无瑕——所有有意思的内容（怀疑、异常、未遂）都活在**它不评估的推理文本里**。

> 🔑 **agent 能抓住的是它说出口的失败。出厂的那四个，全是它一声没吭的。**
>
> ← 对应 Week 00 失败模式表：**Silent failure**（*"The harness sees what raises. Quiet failures do not raise."*）

#### 结论：正确的修法

不是"让模型更靠谱"，而是 **p.44 的 TCP over IP —— "Nobody fixed the wire."**

```
模型内部（概率性）： 可能想起来查，也可能不
harness（确定性）：  时间戳 vs 当前时间 → 差值超阈值 → 强制标记
                    ↑ 纯计算，100% 可靠
```

那个时区检查**根本不需要智能，两个数相减而已**。让模型去"记得"做减法，是把确定性的事交给了概率性的部件。

> **policy 可以是 prompt；invariant 必须是 code。**
> **能算的别让模型猜。**

---

### 💡 把 pⁿ 用在「谨慎行为」上（我的推论）

课上 p.43 的算术讲的是**任务成功率**。但同一个指数可以作用在**「它记得去核查」这件事**上：

> 假设遇到异常时有 **95%** 概率去核查
> 一轮遇 5 次异常 → 全核查 = 0.95⁵ ≈ **77%**
> 一天跑 100 轮 → **每天二十多次漏检**

把 95% 提到 99% 也只是把漏检从 23% 降到 5%，步数一长照样归零。

**所以「这次模型心情好」不是巧合也不是能力——是倾向。** 倾向 = 分布，分布 = 有尾巴，**而尾巴上那些次你恰恰看不见**（失败是静默的，exit 0）。

抬高概率的可识别因素（都只是"更可能"，没有一条是"必然"）：

| 因素 | 作用 |
| --- | --- |
| 异常够刺眼（3 小时，不是 20 分钟） | 难以忽视 |
| 验证成本极低（再发个 curl） | 若要等 30 秒或花钱，选择会变 |
| **任务刚开始**，context 干净、预算充足 | **在第 40 步、预算见底时，大概率倒向 "just report"** |
| 模型训练倾向 | 习得的性情，不是偶然 |

**→ 答案不是"选个心情更稳的模型"，是把这件事从模型手里拿走。**

### 参考：pⁿ 速查

| 步数 | p=0.90 | p=0.99 | p=0.999 |
| --- | --- | --- | --- |
| 10 | **34.9%** | 90.4% | 99.0% |
| 20 | 12.2% | 81.8% | 98.0% |
| 100 | ~0% | 36.6% | 90.5% |

**闭环反转**（每步加一次重试，前提是失败能被检测）：

```
单步实际 = 1 − (1−0.9)² = 99%   →   十步 = 0.99¹⁰ = 90.4%
```

**35% → 90%，只加了一次重试。** 但整个算术挂在一个前提上：**你得知道失败了**。没有 verifier 就不知道该不该重试，失败会被当成成功传下去。

---

### ⭐ 下午 lab：reliability lab · 蒸汽机（ACT V）

**栈**

| | |
| --- | --- |
| tracing | **Phoenix**（Arize，开源），`localhost:6006`，project = `hermes-agent` |
| harness | **Hermes Agent** |
| 模型 | **deepseek-v4.1-flash** ← 故意用小模型（p.26 *small models used agentically*） |

**任务**：`skill_view(name="reliability-lab:engine-open")` → 十步工具链
`fill_boiler → light_burner → raise_pressure → open_valve → turn_flywheel → engage_belt → spin_dynamo → raise_voltage → …` → `engine_journal`

#### 三个设计细节

**1. `skill_view` = progressive disclosure 的现场。**
skill 不在 system prompt 里，agent **运行时才取**。命名 `namespace:skill-name`。
`engine-**open**` = 开环版 → 后面 B/C/D 同一批工具、不同 skill，即 *"Only the governor moves."*

**2. `fill_boiler(prev_token="cold")` —— 链式 token。**
每个工具要求传入上一步返回的 token，跳步或编造就对不上。
⭐ **判据被做进了函数签名——接口本身就是契约**（design by contract）。
⚠️ 但开环版里这个 token 大概率只记录不阻断，否则 A 不会只有 35%。

**3. ⭐⭐ `engine_journal` 是 p.68 的埋伏。**
journal 是 **agent 自己写的自述**；Phoenix 的 trace 是 **harness 记的账**。
**这是 notebook vs ledger 的实物对照。** Week 00 p.68 的真实运行：

| 司机的自述（journal） | 账本记的（trace） |
| --- | --- |
| 十步全 **done**，第 10 步 **"lamp lit"** | **1 genuine + 1 corrupt + 8 rotten**；第 10 步 *"built on rotten state"* |

> **它会说灯亮了。灯没亮。**

#### 成本结构（现场数据）

一次 LLM 调用：**prompt 23,434 / completion 206 / total 23,640**，6.4s；整条 trace 50.7s。

> ⭐ **输入是输出的 114 倍。** 十步 = 二十多万 token。
> **agent 贵在 context，不在生成。** 谈 compute economics 从这里算起。
>
> 另注：Pipeline A 标称成本 10、**实跑 21** —— 开环不是"省了检查"，是**在错误路径上多烧一倍**。

#### 四条 pipeline（p.63，Week 00 已有）

| | 谁拥有循环 | 成功率 | 成本 |
| --- | --- | --- | --- |
| **A** 开环 | **没人** | **35%** | 10（实跑 21） |
| **B** 末端验证 | 模型 | 88% | 25 |
| **C** 逐步验证 | 模型 | **99.99%** | 11 |
| **D** 工具内重试 | ⭐ **代码** | 99.99% | 11，**无额外 token** |

⭐ **A 的 35% 就是 verifier 算术里那个 35% 的生成器**；**B 的 88% = 1 − 0.65⁵**，那条算术的实物。

---

### Phoenix 接自己的 loop

见 👉 [`../../phoenix-instrumentation.zh.md`](../../phoenix-instrumentation.zh.md)

要点：OpenInference 的 span kind 里 **`EVALUATOR`（verifier）和 `GUARDRAIL`（闸门）** 正好对应七动词里的 `verifies` 和 `stops/escalates`。
**trace 里 span kind 的种类数 = 你实现了几个动词的可视化证明。**

---

### 我的问题

- [ ] 万能 `bash` vs 语义化工具——下午 lab 怎么处理 sensors/actuators 分界？
- [ ] 跑完把 `engine_journal` 输出和 Phoenix trace **并排对照**，差距有多大
