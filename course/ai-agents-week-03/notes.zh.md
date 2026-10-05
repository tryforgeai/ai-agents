# AI Agents Week 03 笔记 — Skillcraft：当流程成为一等公民

日期：2026-10-04
来源：`skillcraft-slides.pdf`（113 页，SupportVectors · Fall Cohort · Week 3，Asif Qamar）
状态：**课后按幻灯片逐幕整理**（非现场速记；页码为幻灯片右下角编号）

> ⭐ 概念性总结看 [`summary.zh.md`](summary.zh.md)，时间表与实验清单看 [`lesson-plan.zh.md`](lesson-plan.zh.md)。本文按**讲课顺序**走一遍整副 deck，保留原文金句。
>
> ⚠️ 提取说明：幻灯片上的数学符号（p_s、g_s、κ、VoL、UCB 等公式）在 PDF 文本层里是图形，抽取时丢失。本文凡出现具体公式与数字，均来自 lesson plan 的中文整理（见 `summary.zh.md` §5），已在相应位置注明。

---

## 全天地图（p.2–4）

```
PROLOGUE  Harrison's Clocks  ─ 故事
ACT I     Foundations        ─ skill 是什么
                 ↓ Into the Genie's Kitchen（hands-on 12:20）
ACT II    The Theory         ─ skill 为什么有效
ACT III   The Lineage        ─ skill 从哪来
                 ↓ interlude · the marketplace
ACT IV    Practice           ─ 怎么写
ACT V     Design Patterns    ─ 什么形状
ACT VI    Synthesis          ─ 放回系统里
CODA      Hokusai            ─ 故事
THE LAB   Samarra            ─ 晚间实验
```

全场定调的一句话，封面就给了：

> **"A skill is a prompt that waits in the pantry until it is needed."**

以及 p.4 的两种离场方式：deck 给名字，kitchen 放到手里，**晚上的 lab 让你在一件看起来很简单的事上失败——那个失败本身就是课**。18:15 checkpoint 之前是全员必修，之后的挣扎是选修。

---

## PROLOGUE · Harrison 的航海钟（p.5–12）

**1707（p.6）** 英国舰队在 Scilly 群岛触礁，四艘船沉没，一千多名水手死亡——原因是不知道自己在哪。1714 年议会悬赏最高 £20,000 求解经度问题。

**问题"看起来简单"（p.7）** 带一只走家乡港时间的钟，和当地正午比；每差一小时就是 15° 经度。一句话说得完，难点在于：在颠簸、盐蚀、从英吉利海峡到热带的船上，每天误差要控制在秒级。

**木匠的手艺（p.8）** John Harrison 是林肯郡木匠，最早的钟是木头做的。他的第一批技艺来自本行：会自己出油的愈创木（lignum vitae）、蚱蜢擒纵机构、烤架式摆。

> **"He did not start from the problem. He started from what his hands already knew."**

**四台机器（p.9）** H1→H4，**每一台都证明了上一台不完整**。

**留下来的不是机器（p.10）** 他为 H3 发明的双金属片，今天还在很多机械恒温器里；他的保持架滚子轴承是现代保持架轴承的祖先。

> **"A skill is the reusable procedure — not the product it first made."**

**谁来检查这只钟？（p.11）** 经度委员会信任天文学家，而其中一位 Nevil Maskelyne 支持竞争方案（月距法），还亲自在格林尼治主持了一场对 Harrison 不利的长期测试。讲义埋了伏笔：**Maskelyne 会在 Evals 周回来——作为一个"自己的测量也需要被评判"的裁判**。

**这一幕的题眼（p.12）**

> **"Mastery is a library of procedures — each one learned by finding the last one broken."**

> 🧠 我的理解：这和 Week 00 的 harness / verifier 是一条线。Harrison 的故事同时给了两件事——*积累可复用流程*（今天的主题）和*裁判本身也需要被裁判*（Evals 周的主题）。

---

## ACT I · Foundations：skill 到底是什么（p.13–24）

**那个总也定不下来的问题（p.14）** 工程师第一次接触 agentic 系统时问得最多的：agent、tool、skill 到底有什么区别？讲义承认这个区分"确实滑溜"，所以要从地基往上搭。

**三件不同的东西（p.15）**

| | 定义 |
| --- | --- |
| **Tool** | 一个可调用的能力，input → output |
| **Skill** | 打包好的*流程性知识*——针对一类任务，如何使用这些 tool |
| **Agent** | 带 agency 的 tool：一个循环、自主性、选择 |

> **"A skill sits between prompt and program."**

**Knowing-that vs knowing-how（p.16）** RAG 提供 *knowing-that*（按需取到正确的事实）；skill 提供 *knowing-how*（在相关时加载正确的流程）。

**四个动词（p.17）** skill 与"仅仅是一条提示词"的区别，在于它可以被：

- **Authored** — 写成一个带名字、带 definition of done 的工件
- **Retrieved** — 在需要的那一刻从库里被选出来
- **Composed** — 与其他 skill 组合
- **Improved** — 根据经验修改

**磁盘上的对象：skill 就是一个文件夹（p.18）**

```
transcript-cleaner/
  SKILL.md        # frontmatter + procedure（精简核心）
  reference.md    # 按需加载
  scripts/        # 拿来跑，不是拿来推理
```

> 可检视（inspectable）· 可 diff · 可移植 · **非程序员也能写**。

**承重的那个想法：渐进披露（p.19）**

| 层 | 内容 | 时机 | 成本 |
| --- | --- | --- | --- |
| **L1 Metadata** | name + description | **始终在上下文中** | 约一百 token |
| **L2 Body** | 完整 `SKILL.md` | 判定相关时加载 | — |
| **L3 Files** | 脚本与资源 | 按需读取/执行 | — |

**和邻居们的区别（p.20）**

- vs. prompt — 打包且可复用，不是说过一次就没了
- vs. tool — 是 *how*，不是 capability
- vs. MCP — MCP 给**访问权**，skill 是**怎么用**
- vs. RAG — 是流程，不是事实
- vs. fine-tuning — 改的是 **context，不是 weights**

**持久性光谱（p.21）** `Ephemeral prompt → System prompt → Skill → Weights`

- 一次性 prompt：只活一轮
- system prompt：**一个永远会触发的 skill**（always resident）
- skill：只在相关时常驻
- weights：天生的，烤进去了

> **设计规则：把每条指令放在"常驻程度"与"需要时机"匹配的那一层。**

**与 Week 2 的接线（p.22）**

> Week 2：prompt 是一份合同。今天：skill 是**一份放在架子上、需要时才取下来读的合同**。下周：tool 的 description 是**一份伪装成文档的合同**。
>
> **"Prompts are everywhere. Skills are where they wait their turn."**

### 🎯 Quiz 1 — 报销助手（p.23–24）

团队 agent 要：(a) 永远用正式语气回答；(b) 处理报销——九步流程带表单脚本，每月两次；(c) 知道本季度的 per-diem 费率。各放哪一层？

**答案：** (a) **system prompt**，每一轮都需要。(b) **skill**，是流程，只是偶尔需要。(c) **retrieval**，会变的事实，是 knowing-that 不是 knowing-how。

> **"A system prompt pays its tokens on every turn; a skill should be resident only when its moment comes."**

---

## 插曲 · Into the Genie's Kitchen（p.25–27）

精灵离开了神灯，去当了厨子。同一套装置，同一把钥匙：解压 `genies-kitchen.zip` → `uv sync` → `uv run genies-kitchen`。

> **"You have the names. Now handle the thing."**

上午三个 tab 对应 ACT I 的三个想法：

| Tab | 你做什么 | 对应的想法 |
| --- | --- | --- |
| The Literal Cook | 交一份菜谱过去；读那条脚注 | **正文就是流程本身** |
| Which Scroll Wakes? | 写一条 description；摇铃 | **L1 才是触发器** |
| The Context Window, Live | 一次调用一次调用地走循环 | **渐进披露** |

（下午还有 Run, Don't Reason / The Bazaar / The Forge 三个，见 `lesson-plan.zh.md`。）

---

## ACT II · The Theory：为什么 skill 有效（p.28–39）

**泄气的真相（p.29）** 每一步，模型看到的只有一样东西：**一段有限的 token 序列**。Tools、RAG、memory、skills——全都是同一门手艺：**context engineering，决定模型在何时看见什么**。

**注意力的经济学（p.30）** 无关的上下文不是免费的。干扰 token 越多准确率越衰减，而且**重要文本会沉进召回率最低的中段**（呼应选读 *Lost in the Middle*）。

> "把所有 skill 都加载进来"这个朴素策略，运行在曲线最右端。

**加载规则（p.31）** 令 `p` 为相关性、`g` 为能力收益、`κ(c)` 为稀释成本：

```text
VoL(s) = p_s × g_s − κ(c_s)      ← 公式转写自 lesson plan
```

> **Level 1 存在的唯一理由，就是让 `p` 能被便宜地判断——在支付 `κ` 之前。**

**杠杆在哪（p.32）** 两个抓手：

- **description 决定 `p`** → 写得有区分度
- **正文长度决定阈值** → 保持精简

> **"Authoring = 把 p 推上去、把 c 压下来，直到该过线的 skill 过线，且只有它们过线。"**

**拱心石：skill 就是一个 option（p.33）** Sutton–Precup–Singh, 1999，时间上延展的动作：

| Option 三元组 | Skill |
| --- | --- |
| initiation set | **description** |
| policy | **procedure** |
| termination | **definition of done** |

**技能库缩短规划跨度（p.34）**

> **"Tools widen what the agent can touch; skills shorten how far it must think."**

**选择有几何结构（p.35）** Voyager 式的库里，skill 用 description 的 embedding 建索引，按 cosine similarity 检索。**检索阈值放宽 → recall 升、precision 降**，而这个取舍由上面的加载规则定价。

**组合（p.36）** Options 在组合下封闭——一个 option 可以调用其他 option。**只有在每个子 skill 都干净终止时才安全。** 能力因此复利增长。

**触发问题（p.37）**

> **"A skill that never fires is dead weight; one that always fires is a saboteur."**
>
> **"The description is an ROC curve on one line of YAML."**

对精简的 skill 而言，误触发的代价相对低，所以**写得主动（pushy）**，但**用排除条款把它框住**。

### 🎯 Quiz 2 — 两个 skill，一个上下文（p.38–39）

用户要做幻灯片。pptx skill 和 tax-filing skill 各自算 VoL，谁加载？

**答案（数值取自 lesson plan 整理）：** pptx `0.6 × 10 − 2 = 4` → 加载；tax `0.05 × 10 − 2 = −1.5` → 继续睡。

> **"Level 1 lets the model judge relevance for tens of tokens, before it pays for the body."**

---

## ACT III · The Lineage：skill 从哪里来（p.40–51）

**从"调用"到"保留"（p.41）** Toolformer / Gorilla 教会模型**调用**一个能力——一次动作、一个 API。相变发生在：**从单次调用，到可复用的多步流程**。

**正典案例：Voyager（p.42）** Minecraft 里的 LLM agent，**不做微调，却会变强**。三个器官：

1. **自动课程**（automatic curriculum）——提出下一个可达任务
2. **不断生长的代码技能库**——用 embedding 检索
3. **自验证**——不断打磨程序，直到 critic 确认任务完成

**为什么 Voyager 重要（p.43）** 它的 skill 是：**时间上延展的**（正是 options）、**可解释的**（代码和散文，不是权重增量）、**可组合的**（能力复利，而且缓解遗忘）。这是"丰富的技能库是一种持久的使能器"这一主张最强的论据。

**开放式的引擎（p.44）** 自动课程提出的下一个任务要**尽可能新，但仍然可达**。太简单没学到，太难也没学到。这个甜点就是维果茨基的**最近发展区**——一份骑在能力前沿上的、自己生成的教学大纲。

**为什么用代码而不是散文（p.45）** Voyager 把 skill 存成**可执行代码**：确定、可用普通函数调用组合、**可由执行来验证**。

> **"Agent Skills generalize the idea: the prose decides *when*, the code guarantees *how*."**

**没有梯度的学习（p.46–47）** Reflexion：失败之后，把一段**口头批评**写进 memory，再试一次。ExpeL：把跨任务的教训蒸馏成可复用洞见。

> 奖励变成了一条被记住的指令——**一个 skill 开始改写自己正文的种子**。
>
> Act · evaluate · update · retry——和 policy gradient 是同一个循环，只是**更新目标从权重挪到了一个字符串上**。这就是 text-space optimization 的起点。

**从想法到标准（p.48）** 2025 年 10 月 Agent Skills 成为一门手艺；2025 年 12 月成为开放标准。skill 是一个文件夹——打成 zip 分享、推到 Git、被 40+ 个 agent 客户端加载（2026 年 9 月已列 46 个）。

> **"The USB-C moment for procedure."**

**血统谱（p.49）** 动作（Toolformer/Gorilla）→ 可检索的 option 库（Voyager）→ 从经验改进库（Reflexion/ExpeL）→ 可移植、自我生长的身体（开放标准）。**静态 skill 至此组装完毕，下一步是前沿。**

### 🎯 Quiz 3 — Voyager 为什么变强？（p.50–51）

选项：(a) 模型更大 (b) 用 RL 在 Minecraft 奖励上训练 (c) 上下文窗口更长。

**答案：none of these。** 模型是固定的。长大的是**库**：课程提出下一个任务，新 skill 以代码形式保留，**自验证在保留之前检查了每一个**。

> **"Voyager improved by keeping what worked, as code, after checking it."** —— 而且有时候正确答案就是：以上都不是。

---

## 插曲 · The Skill Marketplace（p.52–57）

**标准催生了市场（p.53）** 因为 skill 是可移植的文件夹，它变得**可交易**——从 Anthropic 2025 年 10 月的自有仓库，到几个月内铺开的一批市场。**一个陌生人的 skill 现在可以武装你的 agent。这是巨大的好处。**

**一根轴把它排开（p.54）** 官方/经审 → 精选且做过安全审查（信任本身就是产品）→ 自由社区（轻度审核）→ 大型聚合站（号称上百万，从 GitHub 爬来，**买家自负**）。**选市场就是在一条前沿上选一个点。**

**阴影（p.55）**

> **"A skill is untrusted code-plus-instruction."**

两个攻击面：**会操纵决策的散文**，和**会执行的脚本**。两者都要审：prompt injection · 外传 · 读密钥 · 危险命令 · 混淆 · 提权。**把每一个第三方 skill 当作不可信，直到被证明可信。**

**解药是策展（p.56）** 知道来源 · 过自己的 eval · 钉住一个 canonical source · 给脚本上 sandbox · **信任边界上站一个人**。

> **"The marketplace is why the governor exists at organizational scale."**

**飞越：自进化 skill（p.57）** 会改写自己的 skill——GEPA 的反思式演化、ACE 的 playbook、把 skill 选择当 bandit，以及一个自写库所需要的 governor。**完整内容在 deck 末尾的附录，正式讲在提示词优化周。**

---

## ACT IV · Practice：怎么写（p.58–66）

**一份完整的 SKILL.md（p.59）**

```markdown
---
name: transcript-cleaner
description: Cleans raw speech-to-text lecture
  transcripts. Use when the user gives a noisy
  transcript and asks to clean or de-mangle it.
  Do NOT use for summaries.
---
## Procedure
1. Read reference.md (the glossary) first.
2. Run scripts/normalize.py for deterministic fixes.
3. Repair by meaning; preserve voice.
## Done when
The transcript reads as the author would have written it.
```

注意这份样例的三件事：description 里**写死了触发词，并明确写了 Do NOT**；procedure 第 2 步**把确定性修复交给脚本**；最后有一条**可检查的 Done when**。

**最高杠杆的那一行（p.60）** description 就是 initiation set，**始终常驻**，并且决定 `p`：

- 用**第三人称**写，描述这个 skill
- **点名字面触发词**
- **写得主动，并写清什么时候不要触发**

> **"A brilliant procedure behind a vague description is a book with no catalog entry."**

**保持核心精简（p.61）** 砍正文不只是省 token——**它降低了一个有用的 skill 得以加载的阈值**。常见路径放核心，罕见材料放 L3 文件，正文里只留一行指针。

**代码边界（p.62）**

| Code（跑） | Prose（推理） |
| --- | --- |
| 确定性、重复、正确性关键 | 判断、适应 |
| **代码本身永远不进上下文——只有它的输出进** | 自然语言表达 |

> L3 脚本是一种**特权**：least privilege · sandbox · **read before you run**。

**两种失败，两套测试（p.63）**

- **Firing test** — `p` 对不对？用 F-score 打分；**漏触发比误触发更贵时，取 β > 1**。
- **Behaviour test** — `g` 对不对？用 rubric：硬约束、质量维度、definition-of-done。

> **"Agent A authors; Agent B, with no memory, tests."**（写的人和测的人要隔离）

**发布与观察（p.64）** skill 是文件夹 → 天然继承版本控制。**一个 canonical source。** 每次运行都要埋点：**是否触发 · 是否有帮助 · 花了多少 · 有没有撞车**。

> **"You cannot improve a library you cannot watch."**

### 🎯 Quiz 4 — 洗发水瓶子（p.65–66）

学生写的正文：1. 取出所有 open ticket。2. 逐条总结。3. **重复。**

**答案：** 缺的是 **termination（definition of done）**。补一行："Done when every ticket open at 9 AM today has one summary; one pass only."

> **"Apply, rinse, repeat — with no stop condition you empty the bottle."**

---

## ACT V · Design Patterns（p.67–77）

**压缩过的经验（p.68）** 按 Christopher Alexander 的 pattern language 体例：**context · problem · forces · solution · consequences**。一个健康的 skill 同时实例化好几个模式。

**怎么读一个模式（p.69）** 它解决的问题 / 张力中的受力 / 解法的形状 / **代价**——你得到什么、你付出什么。

> **"Recognize the shape; don't memorize the rule."**

**结构类（p.70）**

- **Lean Core + Appendix** — 常见路径进正文，其余延后
- **Single Canonical Source** — 一个家，不漂移
- **Checklist-Carrier** — 长流程自带自查
- **Template-Bearer** — 精确格式，随包携带

**行为类（p.71）**

- **Pushy Trigger** — 偏向触发（代价不对称）
- **Definition-of-Done** — 可检查的终止
- **Guardrail** — 硬约束上的 check-and-refuse
- **Router** — 识别情形，分派给专家

**组合类（p.72）**

- **Skill-of-Skills** — 编排者点名子 skill
- **Pipeline** — 固定的变换链
- **Skill + MCP** — 流程覆盖在访问之上
- **Subagent-backed** — skill 内部的有界 agency

> 层级下的 option 封闭性，**靠干净的终止来保持诚实**。

**近距离看一个模式：Dry-Run / Preview（p.73）**

- **Problem** — 后果重大、难以撤回的动作
- **Forces** — 自主与速度 vs. 做错一件不可逆的事的代价
- **Solution** — 先预览"它将会做什么"，提交前要求确认
- **Consequence** — 错误在咬人之前被抓住；**它是幂等性在流程层面的表亲**

**反模式与坏味道（p.74）**

| 坏味道 | 本质 |
| --- | --- |
| **Kitchen-Sink** | 没有渐进披露（`c` 太大） |
| **Silent** | 从不触发（`p` 太低） |
| **God-Skill** | 什么都接（`p` 不加区分） |
| **Collision** | 触发词重叠 |
| **Stale** | 悄悄过期 |

> **每一种坏味道，都指回 ACT II 的某个量。**

**问题 → 模式（p.75）**

| 问题 | 模式 |
| --- | --- |
| 罕见情形的长尾 | Progressive-Disclosure Ladder |
| 精确的输出格式 | Template-Bearer |
| 不可违反的约束 | Guardrail + Escalation |
| 不可逆的动作 | Dry-Run + Idempotent |
| 近似重复的触发词 | Router |
| 需要外部数据 | Skill + MCP |

### 🎯 Quiz 5 — 四个 skill，四种形状（p.76–77）

(1) 给客户打退款的 skill · (2) "report" 同时唤醒 pptx 和 xlsx · (3) 发票必须匹配精确版式 · (4) 绝不引用上季度价格

**答案：** (1) Dry-Run + Idempotent · (2) Router · (3) Template-Bearer · (4) Guardrail + Escalation

> **"A guardrail refuses what is forbidden; a dry-run shows what is about to happen, so a wrong but permitted action can still be stopped."**
>
> 🧠 这句是全场最值得记的区分：**guardrail 挡的是"被禁止的"，dry-run 挡的是"被允许但是错的"。**

---

## ACT VI · Synthesis：放回系统（p.78–92）

**蓝图（p.79）** Agent loop → retrieval / router → 渐进披露 loader → 技能库 + tool/MCP 层，**全部在一个 governor 之下，全部被 observability 看着**。

> **保持四件事彼此分开：access · procedure · selection · governance。**

**一张图，五个面（p.80）**

| | 提供什么 |
| --- | --- |
| Tools | capability |
| MCP | access |
| RAG | facts |
| Memory | the past |
| **Skills** | **procedure** |

全都是 context engineering：**在每一步选择模型看见什么**。

> 🎙️ **课堂补充（deck 上没有）：harness 里的四种记忆。** 上表 Memory 那一格，课上展开成四种：
>
> | | 存什么 | 在 harness 里是什么 | 谁写 |
> | --- | --- | --- | --- |
> | **Operational** | 当下这一步需要的状态 | 上下文窗口、本轮 scratchpad、刚才的工具返回、已加载的 skill 正文 | harness 每轮**重新组装**（七个动词的 *assembles*） |
> | **Episodic** | 带时间地点的经历 | trajectory / 会话历史 | 系统自动，append-only |
> | **Semantic** | 脱离情境的事实 | 知识库 / profile → RAG 取回 | **从 episodic 蒸馏——谁批准？** |
> | **Procedural** | 做法 | **skills**（本周主题） | 通常人来写 |
>
> 几条：
> - **只有 operational 会消失**——另外三种是存储，它是每轮被重新拼出来的。**渐进披露管的就是"这一轮往 operational memory 里放什么"**，`VoL = p·g − κ` 算的正是这件事。
> - 课上用的词是 **operational**，不是认知科学常用的 **working**（Baddeley）。Week 01 的三分法（episodic / semantic / procedural，见 [`../ai-agents-week-01/delta.zh.md`](../ai-agents-week-01/delta.zh.md)）前面补上这一种就是四种。学术上对应 **CoALA**（Sumers, Yao, Narasimhan & Griffiths, 2023）。
> - **semantic 的蒸馏那步没人把关**：客户说"这次要便宜的"（episodic 事实）→ 模型记成"该客户价格敏感"（semantic 断言）。
> - **procedural 抗外化**，所以 Voyager 存成可执行代码而非文字总结——代码自带验证，对应 p.45 *"the prose decides when, the code guarantees how"*。
> - ⚠️ 别和 Week 00 的 **notebook vs ledger** 混：四种记忆讲**存什么**，notebook/ledger 讲**谁有写权限**。让 agent 自己记 episodic，就是让司机自己写行车记录。

### 🎙️ 课堂口述：他用两个比喻讲完了整套机制

**① 乒乓球和后院烧烤 —— 不该触发的那一侧。**

> *"the reality we face at a given moment **ignites** a particular skill… causes that skill to be **retrieved into our operational memory**."*
> *"the one procedural memory that doesn't pop out is **how do you barbecue in your backyard**."*

工单来了，烧烤和轮滑**没有被加载**。🔑 **这是 `κ` 的人类版**——你的大脑一直在替你付这笔钱，而且付得很好。如果每条技能都触发，那不是"你会很多"，是"你什么都做不成"（deck p.37 的 *saboteur*）。

**② ⭐ 厄立特里亚食谱 —— 渐进披露的人类版，比 deck 讲得更狠。**

> *"A recipe… that you have written **is your procedural memory**. But it is **not a procedural memory that is instantly there**."*
> *"while that memory may reside **on the shelf**… you still carry with you that **little bit of a hook**."*
> ⭐ *"**you could not have retrieved the recipe if you did not have in your operational memory the fact that you have the recipe**."*

```
书架上的食谱     = L2，正文，不常驻
"我有这份食谱"   = L1，name + description，约一百 token，始终在
```

**最后那句就是讲义 p.31 那句的生活版：** *"Level 1 exists so pₛ can be judged cheaply, before paying cₛ."* **你脑子里不装一百份食谱，你装一百个钩子。钩子便宜，食谱贵。**

**③ 而"朋友从没说过 Eritrean"这一点，比钩子本身更重要。**

朋友说的是 *"let's have something different today"*——隐含"别做默认那个"，然后你的脑子**推理**了一下才点燃那道菜。

> **触发不是关键词匹配，是对着描述做语义判断。**

⚠️ **这里和 deck p.60 有一处张力，值得在课上提：** 幻灯片说 description 要 *"name the literal triggers: the words a user would actually type"*，而这个例子说的恰恰是**用户不会说出那个词**。
🔑 两者共存的方式：**L1 是被一个会推理的模型读的，不是被 grep 读的。** 字面触发词是在**抬高** pₛ（便宜、可靠），但不是必要条件。

**今晚的 lab 正是这个形状**——Zara 只说 "Put it on my calendar"，她不会说"时区""工作日""节假日"。

**④ 链条的方向不要搞反：**

```
情境（朋友那句话）  →  钩子（常驻，让触发有东西可触发）  →  正文（被取进 operational memory）
    是触发源              不是触发者，是被触发的那个
```

他原话：**"Context decides it."** 没有钩子，情境再对也点不着——**因为你根本不知道自己有这份食谱。**

**⑤ 他说这四种记忆是 1970 年代心理学家发现的，后面会细讲。** 先把名字放这儿（我补的，非课堂原话）：Baddeley & Hitch 1974（working）· Tulving 1972（episodic / semantic）· procedural/declarative 的分野稍晚（Cohen & Squire 1980），哲学源头是 **Ryle 1949** 的 knowing-how / knowing-that——**讲义 p.7 的边注引的就是 Ryle。**

> **"the cognitive architecture of agentic systems mirrors the cognitive architecture of human beings."** —— 这是这门课的一条大梁，记忆架构那周会回来。

**升级阶梯（p.81）** `prompt / skill → prompt optimization → retrieval → SFT → RL`

> **"Sufficiency flows downward; necessity flows upward."** 这不是菜单，是**强制顺序**。非爬不可才爬。skill 住在低处、可逆的那几级。

**技能成熟度模型（p.82）** `0 Ad hoc → 1 Authored → 2 Curated library → 3 Evaluated & governed → 4 Self-improving`

> **真正重要的那一跳是 2 → 3：没有评测和治理，一个不断增长的库是一笔负债。**

**共同的形状（p.83）** 转写清理 · 文档类 skill · 编码 agent 的约定 · 企业流程——每一例都是同一件事：**把一个反复出现的 how，从易错的重复推理里抬出来，变成一个可检视、可检索、可改进、且只在相关时加载的工件。**

### 🎯 Quiz 6 — 想去微调的团队（p.84–85）

团队想微调模型，好让 agent 遵循十二步月结流程。先试哪一级？

**答案：先写 skill**——把流程写下来，确定性步骤交给脚本，每一步放一个检查。**只有当它在没见过的案例上持续失败时，才往上爬。**

> **"Sufficiency flows downward: use the cheapest layer that works, and climb only when it demonstrably fails."**

**收束（p.86）**

> 一门手艺向来是手手相传的流程。skill 是这条血统里最新的成员——**第一个由机器持有、而且用我们自己的语言阅读它的成员。**
>
> **"We have, for the first time, a Library of Alexandria that tends its own shelves."**

**Say it back（p.87–88）** 讲师让全场先自己复原这张地图，再揭晓：

| 故事 / 练习 | 它教了什么 |
| --- | --- |
| Harrison's clocks | 技艺会累积；每一件作品让上一件显得不完整 |
| The Literal Cook | 流程会被**字面**执行——说清怎么做，和何时停 |
| Which Scroll Wakes? | description 就是触发器，**而且它会对自己的例子过拟合** |
| The loading rule | 相关性必须压过稀释；L1 让相关性判断变便宜 |
| Voyager | 一个库靠**检查之后保留有效的东西**而生长 |
| The marketplace | 陌生人的 skill 是不可信的代码加指令 |
| The shampoo bottle | 没有 definition of done，就没有 skill |
| The escalation ladder | 只有更便宜的那一层失败了才往上爬 |

**三句承诺（p.90–92）**

- **WHY** — 一个反复出现的 how，每次都重新推理，就是一串猜测：**十步、每步 90%，整体成功率约三分之一**。写下来一次，它就不再被重新发现。*"Don't make the model rediscover what you already know."*
- **WHAT** — skill 是一个文件夹：**决定何时的 description、说明如何的 procedure、一条 definition of done、以及跑而不是推理的脚本**——只在相关时加载。
- **HOW** — description 当触发器写并带排除项 · 核心保持精简 · 确定性步骤移进脚本 · **触发与行为分开测** · **跑别人的 skill 之前先读它**。

---

## CODA · 七十三岁的葛饰北斋（p.93–95）

**1834（p.94）** 在《富岳百景》跋里，北斋写道自己六岁就开始画，**七十岁以前画的东西都不值一提**；到七十三岁才开始抓住鸟兽虫鱼的结构和草木生长的方式。他署名"**画狂老人**"（the old man mad about drawing）。

**理解总是迟到（p.95）** 黑格尔：**密涅瓦的猫头鹰在黄昏才起飞**——我们在一件事的白天过去之后才理解它。Harrison 造出 H2 之后才看见 H2 的缺陷，于是开始造 H3。

> **"Every stage of mastery is the vantage point from which the last one looks broken."**

---

## THE LAB · An Appointment in Samarra（p.96–102）

**故事（p.97–98）** 巴格达的商人派仆人去集市。仆人面色苍白地跑回来：死神在人群里撞到他，做了个他当作威胁的手势。他借了主人的马逃往 Samarra。商人下市场找到死神，问她为何威胁他的仆人。死神说她没有威胁的意思——**她只是惊讶在巴格达看见他，因为他们俩当晚本来约在 Samarra 见面。**

> **"An appointment is a place and a time. Death never gets either wrong. That is the standard for tonight."**

**今晚的愿望（p.99）** 一条普通消息里的一句话："**Just put it on my calendar.**" 200 个 demonstration：100 个你看得见，100 个扣住。三层：读懂请求 · 时区与节假日 · 日历主人自己的日历和规则。

> **"It looks like one step. It is more than ten."**

**抽屉里的工具，没有说明书（p.100）** 包里有：时区解析器 · 节假日查询 · 工作日计数器 · 邀请文件生成器 · 日历主人的日历。**没人告诉你什么时候该伸手拿哪一个。**

> **"Some steps want judgment. Some want a script. Knowing which is the skill."**

**阶梯回来了（p.101）** 你发现的**每一步都想要自己的 verifier**。回忆 Week 2 的阶梯：同一个 prompt 尾部加一个检查 · 单独一次调用 · 不同的推理基底 · 一组确定性检查的 rubric。

> **今晚大多数检查可以待在最上面那一级：十行代码，每次给出同样的答案。**

**晚上怎么跑（p.102）** 16:40 全员 Tier 1 · 18:15 checkpoint 对"答案的形状" · 之后 Tier 2–3 · 19:45 当场放 12 个没人见过的请求。**你发现的陷阱会上 Hall of Traps，给全场共享。** 完整解法走查在周中、和 TA 一起。

---

## 下周与结尾（p.103–104）

> **Tools — where prompts pose as documentation.** 一个 tool 的 description，就是模型用来决定调用什么的 prompt。Tools 之后是提示词优化：**让机器来搜索**。
>
> **"Tonight's skill becomes the baseline the optimizer must beat."**

收尾两句：

> **A rich repertoire of tools lets an agent touch the world.**
> **A rich repertoire of skills lets it act in the world — well.**

---

## 附录 · Self-Evolving Skills（p.105–113，提示词优化周才正式讲）

**三种进化（p.106）**

- **Model-centric** — 改权重（贵、不透明、难回退）
- **Environment-centric** — 改上下文和 skill（**便宜、可检视、可回退**）
- **Co-evolution** — 两者一起

> **"A skill is the cheapest unit of evolution — a bad one is undone with `git revert`."**

**GEPA（p.107–108）** Genetic-Pareto，文本空间里的优化：

- **Reflective mutation** — 模型读自己失败的 trace，提出一条修改。**反思就是搜索方向。**
- **Pareto selection** — 保留每一个"在某方面最好"的候选，从前沿繁殖。

> 只留平均分最高的，会丢掉那个你最想拿来繁殖的边缘情形专家。

**GEPA vs. GRPO（p.109–110）** 论文 v2 的六个任务上：平均 +6%，最高 +20%，**rollout 少至 1/35**。

> 讲义自己的保留意见：**当反馈真的只是标量（对/错）时，GEPA 的优势应该收窄；当失败可以被描述出来时，反思取胜。**
>
> 关于"GEPA 出来 RL 就死了"——**"In this field, everything dies every day."** 实情是 GEPA 在一类过去需要 RL 的问题上追平或超过了 GRPO，**于是 RL 被提拔去做更难的问题。技术不会死，它们被重新分配到更难的问题上。**

**ACE 与 playbook（p.111）** Generator 做任务 · Reflector 诊断 · Curator 合并 delta。

> 要怕的失败叫 **context collapse**——"重写得更好一点"会把辛苦得来的具体细节抹平。**按 delta 生长 skill，永远不要整体重写。**

**skill 选择即 bandit（p.112）** 每个 skill 是一只手臂，加载它得到一个带噪声的回报，UCB 规则决定何时加载。

> **那条"写得主动"的 description，本质是给还没挣到自己均值的 skill 的一笔探索奖励。**

**生长需要治理（p.113）**

| 风险 | 对策 |
| --- | --- |
| drift | 钉一份 spec + eval gate |
| collapse | 只做 delta 更新 |
| forgetting | 碰撞检查 |
| poison | provenance + sandboxing |

> **"Self-evolution without a governor is not learning — it is drift."**

---

## 📌 逐页补充（课上现场想到、deck 没明说的）

### p.47 其实是三周后那堂课的定义页

```
RL:        ĝ = E[∇_θ log π_θ R]  →  θ        永久、全局、昂贵、不透明
Reflexion: ℓ = Reflect(τ, R)     →  context   便宜、局部、可读——但用完即弃
```

**同一个循环，差别只在最后那个箭头指向哪。**

🔑 **"用完即弃"正是 skill 存在的理由。** Reflexion 的反思写进 memory，episode 一结束就没了；**写进一个 skill 文件夹，它就跨会话了。** 而 *"the seed of text-space optimization"* 里的 text-space optimization，**就是两周后优化器那堂课的正式名字**。

### p.48 ⚠️ USB-C 这个比喻有局限

**USB-C 统一的是接口形状，而这个标准约束的只有 `name` 和 `description` 两个字段——正文完全不管。**

**所以它更像"统一了信封尺寸"，不是"统一了语言"。** 这正好解释了第二场那几个数字：

```
46 个客户端都能加载    ←  标准做到的
63.8% 只是文字         ←  标准不管的
46% 重名               ←  标准不管的
36.8% 有安全缺陷        ←  标准不管的
```

🔑 **可移植性和质量是两件事，标准只解决了前者。** Forge 的 ✗/○ 分法说的是同一件事。

### p.49 四级其实分两段

```
Toolformer/Gorilla + Voyager     →  能做什么     （actions 𝒜 → options Ω）
Reflexion/ExpeL + Open standard  →  怎么改进、怎么流通
```

**前两级是能力，后两级是治理。** 这也解释了为什么成熟度的关键跳跃在 2→3——**血统本身就是这个形状。**

⚠️ 最后那句 *"The **static** skill is now fully assembled"* 的关键词是 **static**。而 SkillsBench 的 **+16.2（人写人审）vs −1.3（自生成）** 说明：**静态那一版现在仍然是更好的那个。** 这句话该读成"前沿值得研究，但还不到用的时候"。

### p.51 "改进住在哪里"可以答得比官方答案更准

官方答案是"长大的是**库**"。但消融数据说得更细：

| 从句（金句四拆） | 对应消融 | 掉多少 |
| --- | --- | --- |
| **what worked** | 随机课程 | **−93%** |
| **after checking it** | 去掉自验证 | **−73%**（论文称所有反馈类型里最重要的） |
| **as code** | 换 GPT-3.5 生成 | GPT-4 多 **5.7×** |
| **keeping** | 去掉技能库 | ⚠️ **论文没给数字** |

🔑 **最像标题的那个词（库本身）恰恰是唯一没有数字支撑的。** 有数字的两个都是**守门的动作**，不是存储的动作。

> **库之所以让它变强，不是因为库存了东西，是因为有人守着门。**

#### 守门为什么是全程有效的（而库有门槛）

| | 机制 |
| --- | --- |
| **信噪比** | 一条未验证的坏 skill 不是 0 收益，是负的——占 κ、会误导、而且"长得像 skill"最难查 |
| **组合放大** | `craftWoodenPlanks` 调用 `mineWoodLog`。**底层没验证，上面全建在沙子上**，而且错误沉默向上传播（`β_A ⟸ β_B ∧ β_C`） |
| **课程的输入** | 课程依据 completed/failed 出题。**验证不准 → completed 是假的 → 推进太快** |
| **试错变学习** | critic 的回馈是"缺什么"（缺紫水晶碎片），不是"失败了" |

```
库的收益      = f(任务复杂度)   任务短时 ≈ 0，甚至为负（石器级 9±4 vs 11±2）
不守门的损失  = f(库规模)       单调增，从第一条就开始
```

🔑 **守门不是"让库更好"，是"防止库变成负资产"。** 它全程有效，因为**它防的那个损失是全程的**。

### p.54 Pareto 这张图是从市场经营者视角画的

**它假设 quantity 是正向目标。** 对经营者是（"1000+ skills" 是卖点）；**对你不是**——SkillsBench 实测 **2–3 个胜过 4+ 个**。

| | abundance 是什么 |
| --- | --- |
| 市场经营者 | **产品**（流量、估值） |
| **你** | **待筛选的负债**（要筛、要审、每轮付 κ） |

**同一根横轴，对他是资产，对你是成本。** 而且菜不买就不花钱，**skill 装上了每轮都收钱**。

⭐ **帕累托在这份 deck 里出现了两次，用法相反：**

```
p.54   用前沿【选一个点】（挑市场）
p.108  用前沿【拒绝只选一个点】（GEPA 保留每个"在某方面最好"的候选）
```

GEPA 那页的理由值得记：*"Keeping only the best average discards the edge-case specialist you'd want to breed from."* ——**平均分会杀死专才。** 而这正是 `trailofbits/skills` 那四十个**窄**安全 skill 的设计哲学。

### p.57 ⚠️ bandit 那条和 SRA 的实测直接冲突

**Bandit 框架的前提是：agent 在做一个探索-利用的决策。**

**SRA 实测：需要外部能力和不需要，加载率 36.9% vs 36.9%（Δ = +0.1pp）。** 🔑 **它根本没在做那个决策**——不是做得不好，是决策过程不存在。

**推论很实际：如果模型判断不了该不该加载，这个决策就该从模型手里拿走。** 而 SRA 的实验正好印证：

| 策略 | 谁做决策 | 结果 |
| --- | --- | --- |
| **LLM Selection** | 给 top-50，**模型只能挑一个** | **六个模型全胜** |
| Progressive Disclosure | 模型自己决定取几个、取不取 | 最大落后 **10.7pp** |

**前者赢，是因为它限制了模型的决策空间。** → **bandit 该实现在 harness 的 router 层，不是指望模型自己做。**

### p.63 两套测试 + p.64 四个埋点 —— 合起来才完整

```
Firing test     测  𝓘ₒ  (initiation set)
Behaviour test  测  πₒ  (policy)
βₒ (termination)  ← 没有自己的测试，被塞进 behaviour 的 rubric
```

⚠️ **这不够**：一个跑了 50 轮、烧了十万 token、最后答对的 skill，**rubric 打分很高**。今天那瓶洗发水第三轮就是这个形状——满足了 Done when，**而房间淹了、跑了四十分钟**。

**但 p.64 的四个埋点补上了这一块：**

| | 什么时候 | 管什么 |
| --- | --- | --- |
| p.63 两套测试 | **上线前** | 触发对不对、做得对不对 |
| p.64 四个埋点 | **上线后一直记** | 触发 · 有用 · **花多少** · 有无冲突 |

🔑 **四个埋点是两套测试的生产版本**，而第三、四个是测试阶段测不出来的：**成本要在真实分布上跑才知道，冲突要有别的 skill 在场才会发生。**

⚠️ **另外："Agent A authors; Agent B, with no memory, tests" 这条我今天违反了。** `paper-deep-read` 是我写的也是我测的——ReAct 那次隐藏测试算数（写时没看），**但 Voyager 那次行为测试不算，我在检查自己的作品。**

### p.65 Quiz 4 的官方答案有两个限定，不是一个

> *"Done when **every ticket open at 9 AM today** has one summary; **one pass only**."*

```
every ticket open at 9 AM today   ←  限定【集合】
one pass only                      ←  限定【轮次】
```

**只写一个不够。** 只说"每个 open ticket 都有摘要"——**那个集合是流动的**，你总结完一轮新工单又进来，永远不空。

🔑 **而这个形状今天亲眼见过：第一轮厨子拧开了第二瓶洗发水。**

```
"直到洗发水用完"  →  你还有一瓶        ← 集合在流动
"水冲清了"        →  会到达的状态      ← 所以第二轮闭合了
```

**写 Done when 时问两句：① 我限定的集合会不会变大？② 这是个【会到达的状态】，还是【可能永远差一点】的目标？**
（"直到找到一个所有人都有空的时间"是后者——可能永远找不到。）

### p.68 五个部分里，大家只拿 solution 走

| | 管什么 |
| --- | --- |
| **context** | 什么场景才适用 ← **这就是模式自己的 initiation set** |
| **forces** | 相互拉扯的那几股力 ← **最常被跳过** |
| solution | 解法的形状 |
| **consequences** | 你得到什么，**你付出什么** ← 第二常被跳过 |

🔑 **forces 和 consequences 是「模式」和「最佳实践清单」的全部区别。**

```
清单：  这样做
模式：  这里有两股力在拉扯，这个解法偏向一边，代价是另一边
```

↔ 和第二场那条 *"write in the imperative, with the reason attached"* 同一个原理——**理由让你能处理没列出来的情况。**

**p.73 的 Dry-Run 是唯一写全五部分的**，而且 consequence 诚实地写了代价："**the cost is one more round-trip with a human**"。

⭐ **一个结构巧合：Alexander 的格式和 SKILL.md 是同构的。**

```
context  ↔  description      solution  ↔  procedure      consequences  ↔  Done when
```

**模式语言是 procedural memory 的另一种外化形式，比 skill 早了四十年。** 区别只在读者——Alexander 写给建筑师，SKILL.md 写给机器。↔ 这正是 deck 结尾那句的意思：skill 是这条血统里**第一个由机器持有、用我们自己的语言阅读它的成员**。

---

## ⚠️ 课后修订：这份 deck 被实测打到的六处

> 来自当天第二场（[`survey-notes.zh.md`](survey-notes.zh.md)）和两篇论文。**写进复习清单之前先读这一节。**

| 本 deck 说 | 实测 / 另一场说 |
| --- | --- |
| **Guardrail** 是 skill 的行为模式（p.71） | **"绝对不能发生"的事该是 hook 或权限，不是 skill 里的文字**——正文会被挤掉、被稀释、被覆盖；**hook 不经过模型** |
| 两个攻击面：散文 + 脚本（p.55） | **第三个：被复制的样例**。Agent 把 example 当可信参考抄进输出，而它既非指令性散文也非可执行脚本，**两个审查视角都可能漏掉** |
| 确定性步骤交给脚本（p.62） | **是最佳实践，不是现状**——市场上 **89.5%** 的 skill 没有脚本（Cao et al. 2026） |
| **渐进披露是 "the load-bearing idea"**（p.19） | ⚠️ **SRA 实测：六个模型上全不如一次性 LLM Selection**，最大落后 **10.7pp**。省下的 κ 被糟糕的加载决策吃掉了 |
| `VoL = p·g − κ`（p.31） | **SRA 实测 need-awareness Δ = +0.1pp**——**模型基本不看 g**。加载规则是**规范性模型**，不是行为描述 |
| "a rich repertoire is a durable enabler"（p.43） | **SkillsBench：2–3 个 skill 胜过 4+ 个；自生成 skill −1.3 分，精选 +16.2 分** |

### 🔑 "rich" 其实指两种不同的东西

| Voyager 的 rich | 市场的 rich |
| --- | --- |
| **自己造的** | 别人写的 |
| **每条都过了自验证才保留** | 36.8% 有缺陷、46% 重名 |
| **单一任务域** | 跨领域大杂烩 |

**Voyager 证明的是"自己造、经过验证、同域"的库有用；它没有证明"从市场装三万条"有用。** SkillsBench 的 **+16.2 vs −1.3** 说得更直白：**差别不在数量，在策展。**

↔ Voyager 自己的 Table 1 早有信号：**去掉技能库在石器级反而更快（9±4 vs 11±2）**，优势只在铁和钻石出现——**技能库有一个任务复杂度的启动门槛。**

### 🔥 p.46 那颗"种子"，三年后被测了

本 deck p.46 把 Reflexion / ExpeL 收在"**一个 skill 改写自己正文的种子**"。

**SkillsBench 测出来：自生成 skill −1.3 分。不是收益小，是负的。**

这不否定 Reflexion 的机制（它测的是单任务内的反思重试，不是生成可复用 skill），**但给"让 agent 自己写技能库"放了一个硬路标**——而那正是本 deck 附录 GEPA / ACE 的方向。

🔑 **于是成熟度模型里 2 → 3 那一跳（评测与治理）有了实证分量：没有策展的增长，实测是负收益。**

### 另有一个 deck 没画的结构：harness 里每个邻居住在哪

当天第二份材料给了一张 "Inside the harness" 图，补上了四样这份 deck 没讲的东西——**Hooks**（闸门的实物，红色=harness 强制）· **Scoped rules**（路径匹配时才进，不走模型判断）· **Subagent**（*only a summary comes back*，**烧的 token 不进父上下文**）· **Plugin**（把 skills + subagents + hooks + MCP config 打成一个 bundle）。

还有一个布局细节值得记：**L1 在 system prompt 区（每轮重发），L2 在 messages 区（追加一次）**——所以"约一百 token"是**每轮的单价**。详见 [`survey-notes.zh.md`](survey-notes.zh.md) 〇 节。

---

## 六道 Pop Quiz 速查

| # | 题 | 答案 |
| --- | --- | --- |
| 1 | 语气 / 九步报销 / 本季费率 | system prompt / skill / retrieval |
| 2 | pptx vs. tax 哪个加载 | pptx（VoL=4）加载，tax（−1.5）不加载 |
| 3 | Voyager 为什么变强 | **以上都不是**——长大的是库，不是模型 |
| 4 | "Repeat." 缺什么 | **termination**：写一条可检查的 Done when |
| 5 | 四个 skill 四种形状 | Dry-Run+Idempotent / Router / Template-Bearer / Guardrail+Escalation |
| 6 | 要不要先微调 | 先写 skill；只有在未见案例上持续失败才往上爬 |

## 五句话带走

1. **description 决定能不能被找到，正文决定怎么做，Done when 决定何时结束。**
2. **无关上下文是有成本的；"一个都不加载"可以是正确答案。**
3. **散文决定 when，代码保证 how；代码本身不进上下文，只有输出进。**
4. **触发正确和行为正确是两件事，必须分开测。**
5. **2 → 3 那一跳最关键：没有评测与治理，增长的技能库是负债。**

---

## 待办与存疑

- [ ] 跑完 Genie's Kitchen 六个 tab，把 *Which Scroll Wakes?* 的隐藏 8 例结果记进 `lab-log`
- [ ] 完成 Samarra Tier 1，按 lesson plan 的现场笔记模板填"发现的步骤 / Reason or Run / 检查方法"
- [ ] 在 Hermes 和 Claude Desktop 各跑同样三个案例，比较触发与行为（作业 1）
- [ ] 从自己工作里挑一个重复流程写成 skill（作业 3）——候选：周报汇总、数据修复流程（见 `usecase-data-fix-agent.zh.md`）
- ❓ p.35 的检索几何：课堂上用的相似度阈值和 top-k 具体怎么配，deck 里只给了定性结论
- ❓ 附录 GEPA/ACE 只是飞越，等提示词优化周回来补
