# Landscape of AI Agent Architectures 论文精读笔记

> **The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey**
> Tula Masterman\*, Sandi Besen\*, Mason Sawtell\*, Alex Chao（\* 共同一作）
> **Neudesic（IBM 旗下咨询公司）· IBM · Microsoft** —— 四位作者都在业界，没有学术单位
> `arXiv:2404.11584` · **v1 2024-04-17，只有这一版**（本笔记据 v1 PDF 全文 13 页 + arXiv HTML 版的图）
> 原文：[course/ai-agents-week-06/papers/2404.11584v1.pdf](course/ai-agents-week-06/papers/2404.11584v1.pdf)
> 课程：**Week 06 Toolcraft II 当周阅读**；和同周的 MARL 综述（Gronauer & Diepold）配对读
> 整理于 2026-10-25

> ⚠️ **venue 注意**：arXiv 页面没有 journal-ref，论文本身也没写发表场所。引用时按 arXiv preprint 写。
> ⚠️ **时效注意**：写于 **2024 年 4 月**——比 MCP 发布（2024-11）早 7 个月，比 MAST（`2503.13657`）早 11 个月。按 W6 Interlude 的说法，**里面点名的系统是"表面"，会过期；设计原则是"原理"，大部分还活着**。读的时候分开对待。

---

## 0. 一句话总括

**一篇 9 个系统的小综述：把 2024 年春的 LLM agent 分成单 agent 和多 agent（多 agent 再分纵向 / 横向），结论是"没有最好的架构，看用途；但表现好的系统，至少用了下面几招之一——清楚的 system prompt、明确的领导和分工、计划-执行-评估分阶段、动态组队、人或 agent 的反馈、消息过滤"。**

核心贡献不是新方法（**全文零实验**），也不是完整的文献地图（**38** 条参考文献，正文只拆了 **5** 个单 agent + **4** 个多 agent 系统），而是：

> **一套从业者用的设计词汇——leader、vertical / horizontal、message filtering、dynamic team、role definition——用来在动手前选架构。**

⚠️ **方法论硬伤，先挑明**：
- 没有检索协议、没有纳入标准，系统是 *"selected based on their contributions"* 挑的
- 摘要说的 *"insights gained from our observations of these systems in action"* ——**全文没有一条观察数据**：没有日志、没有计数、没有案例轨迹
- 所以它**只能主张"这些是反复出现的设计主题"**，不能主张"这些主题导致性能提升"。但 §5.3 和 §7 恰恰做了后一种主张（*"is likely to result in increased performance"*）。**读它当词典用，不要当证据用。**

---

## 1. 动机与定位

摘要列的三个目标，**顺序有讲究**：

> *"a) communicate the current capabilities and limitations of existing AI agent implementations, b) share insights gained from our observations of these systems in action, and c) suggest important considerations for future developments in AI agent design."*

🔑 从业者圈子转发这篇，是因为 **(b)**——"做过的人告诉你哪招有用"。但 (b) 恰恰是全文唯一没有证据支撑的部分。(a) 是对他人论文的转述，(c) 是 (b) 的推论。

### 它站在哪个时间点

开篇定位很清楚：ChatGPT 之后第一波应用是 **RAG**（"chat over a corpus of documents"），下一代的共同主题是 **agents**，起点是 AutoGPT 和 BabyAGI 这类开源项目。

> *"agentic systems have a notion of planning, loops, reflection and other control structures that heavily leverage the model's inherent reasoning capabilities to accomplish a task end-to-end."*

↔ 这正是 W1 讲过的"环是本质"——这篇把 planning / loops / reflection 当作 agent 的定义特征。

### 它要回答的争论

> *"While single agent architectures excel when problems are well-defined and feedback from other agent-personas or the user is not needed, multi-agent architectures tend to thrive more when collaboration and multiple distinct execution paths are required."*

这句在引言里就把结论先给了。⚠️ 注意它说单 agent 适合"**不需要用户反馈**"的场景——§5.3 会自相矛盾（见 §5）。

🔑 **评测标准要和用途匹配**：这是一篇 13 页的从业者综述，拿系统综述（PRISMA 那种）的标准去批它是错位的。但它在结论里做了因果主张，这部分就该按因果主张的标准来批。

---

## 2. 方法精读：分类法 + 9 个系统 🔥

综述的"方法"就是它的分类法和它选的例子。逐个拆。

### 2.1 分类法（§1.1，Figure 1）

| 术语 | 论文的定义 | 🔑 我的注 |
| --- | --- | --- |
| **Agent** | 能"plan and take actions to execute goals over multiple iterations"的 LM 实体；采用 Xi et al. [31] 的 **brain / perception / action** 三件套 | 最低要求定义，不含记忆 |
| **Persona** | 角色、性格和指令；**"Personas also contain descriptions of any tools the agent has access to"** | ⭐ 工具说明被放在 persona（system prompt）**里面**——这就是 W6 Act IV 说的"烤进 prompt"时代 |
| **Tools** | "any functions that the model can call"，用来拉取或推送外部数据 | 只当能力，不当接口（见 §7 批判 ②） |
| **Single agent** | 一个 LM 做全部推理、规划、执行；没有来自其他 agent 的反馈，可以有人的反馈 | |
| **Multi-agent** | ≥2 个 agent，可同模型可不同模型，可同工具可不同工具，通常各有 persona | |
| **Vertical** | 一个 leader，其他 agent 向它汇报；可以只和 leader 说话，也可以共享对话；**特征是有 leader + 分工清楚** | ↔ MARL 的 master-slave / CTCE |
| **Horizontal** | 平等，一个群聊，人人看到所有消息；可以**自愿**认领任务或调工具 | ↔ MARL 的 broadcasting 通信 |

> *"It is important to keep in mind that these categories represent two ends of a spectrum, where most existing architectures fall somewhere between these two extremes."*

⭐ **Figure 1**（论文第一张图）只有两行字：*所有 agent 都有 persona，知道自己工具的用途和用法*；*大多数 agent 实现都有推理、规划、工具调用能力*。图角落标着 **"Source: Neudesic, an IBM Company"**——这是一张公司宣传风格的图。

### 2.2 推理与规划（§2.2）

没有推理的 agent 会 *"misinterpret the query, generate a response based on a literal understanding, or fail to consider multi-step implications"*。

规划分 **5** 类，全部转引 Huang et al. [12]：

1. **task decomposition** —— 拆成子任务
2. **multi-plan selection** —— 生成多个计划选一个
3. **external module-aided planning** —— 借用外部现成计划
4. **reflection and refinement** —— 按新信息修改计划
5. **memory-augmented planning** —— 用外部信息改进计划

另外点名 **PLaG**（Plan Like a Graph）：把计划表示成**有向图**，独立的步骤并行执行。

🔑 这一节是全文最"教科书"的部分，信息量全来自 [12]。如果你要深入规划，直接读 Huang et al.（`2402.02716`）。

### 2.3 工具调用（§2.3）

论文说的只有三件事：
1. agent 相对裸 LM 的关键好处是**调多个工具**
2. 需要大量工具调用的问题，往往也需要复杂推理
3. 单 agent 在**长序列**上容易失败 [22, 6]；多 agent 可以让每个 agent 用**自己独立的工具集**解一个子问题

🔑 **标题里有 "Tool Calling"，正文里没有一句话谈工具的说明怎么写、参数怎么设计、报错怎么写、返回值多大。** 这一节讲的是"调工具这件事很重要"，不是"怎么让模型调对工具"。这正是 W6 补上的那一半（见 §6 ↔ 一节）。

### 2.4 单 agent 五例（§3）

选择理由：*"based on their contributions to the reasoning and tool calling capabilities of agents"*；共同点：**每个都在行动前有专门的推理阶段**。

| 系统 | 机制 | 论文报的好处 | 论文报的局限 |
| --- | --- | --- | --- |
| **ReAct** [32] | Thought → Action → Observation 循环 | 可解释、可信；HotpotQA 上"幻觉" **6% vs CoT 14%** | 反复生成相同 thought/action，出不了循环；建议加人类反馈 |
| **RAISE** [16] | ReAct + 记忆：**scratchpad**（短期）+ **相似样例数据集**（长期）；微调 | 长对话保持上下文；比 ReAct 效率和质量都好；小模型微调后最好 | 复杂逻辑不行；**角色幻觉**——没定义清角色的销售 agent 会开始写 Python |
| **Reflexion** [23] | 用 LLM evaluator 基于成败、轨迹、持久记忆给语言反馈 | 成功率更高、幻觉更少（vs CoT、ReAct） | 陷入 *"non-optimal local minima solutions"*；长期记忆是**滑动窗口**，受 token 上限约束 |
| **AutoGPT+P** [1] | 物体检测 + Object Affordance Mapping + LLM 选 **4** 个工具之一（Plan / Partial Plan / Suggest Alternative / Explore）+ **PDDL 经典规划器**执行 | 显著好于纯 LLM 的机器人规划 | 工具选择不准、会卡循环；在错的地方找东西；**不能问用户澄清，用户也不能中途修改或终止计划** |
| **LATS** [36] | 受 MCTS 启发的树搜索：状态 = 节点，动作 = 边；LM 启发式 + 状态评估器 + 自我反思 | 自我反思让性能"dramatically"提升 | 更耗算力和时间；只在简单 QA 上测过，**没测工具调用和复杂推理** |

AutoGPT+P 那句值得原文记下：

> *"LLMs currently lack the ability to directly translate a natural language instruction into a plan for executing robotic tasks, primarily due to their constrained reasoning capabilities"*

🔑 **AutoGPT+P 是五个里唯一把"判断计划对不对"交给非 LLM 组件（PDDL 规划器）的**——也是唯一一个在严肃领域（机器人）里报"显著优于纯 LLM"的。↔ W3–W5 反复讲的"LLM 读、代码判"。

⚠️ **ReAct 那个 6% vs 14% 被转述错了**，见 §5 不一致一节。

### 2.5 多 agent 四例（§4）

主题：**按技能智能分工**，以及**多个 persona 的反馈**。很多架构**分阶段**动态组建和重组团队。

| 系统 | 结构 | 机制 | 关键数字 / 发现 |
| --- | --- | --- | --- |
| **Guo et al.** [9]（Embodied LLM Agents Learn to Cooperate in Organized Teams） | 纵向 + 横向混合 | 有 leader；其他 agent 也能彼此说话；*criticize-reflect* 步骤生成计划、评估、反馈、重组团队 | 有 leader 的队完成任务快"nearly **10%**"；**没有 leader 时约 50% 的通信在互相下命令**；有 leader 时 leader **60%** 的通信是发指令；**人当 leader 效果最好**；**轮换领导的动态团队**时间最短、通信成本最低 |
| **DyLAN** [18] | 横向 | 每轮评估每个 agent 的贡献，**只让贡献最高的进入下一轮** | 算术和通用推理 benchmark 上有提升（无具体数字） |
| **AgentVerse** [2] | 可横可纵 | **4** 阶段：recruitment → collaborative decision making → independent action execution → evaluation，循环到目标达成 | **横向适合咨询类协作；纵向适合需要清楚隔离工具调用责任的任务** |
| **MetaGPT** [11] | — | 要求 agent 输出**结构化产物**（文档、图）而不是聊天；**publish-subscribe** 信息共享：大家发到一处，各自只读和自己相关的 | HumanEval、MBPP 上显著好于单 agent（无具体数字） |

🔑 **四个例子里，有三个的核心机制是"减少废话"**：Guo 的 leader 减少互相下命令，DyLAN 踢掉不贡献的，MetaGPT 用结构化产物和订阅制挡掉闲聊。多 agent 的主要工程问题不是"怎么让它们更聪明"，而是"怎么让它们少说话"。

---

## 3. 实验？—— 论文没有实验，§5「讨论与观察」就是它的发现

⚠️ 这一节按论文的"发现"来拆，每条标出**它的依据是什么**。

### 3.1 单 vs 多 agent 的选择条件

| 选单 agent | 选多 agent |
| --- | --- |
| 工具列表窄、流程定义清楚 | 多个 persona 的反馈有益（例：一个写文档，另一个给反馈） |
| 实现简单，只定义一个 agent 一套工具 | 需要在不同任务 / 工作流之间并行 |
| 没有队友的坏反馈和闲聊干扰 | **没有示例时**多 agent 比单 agent 好（Wang et al. [26]） |
| 风险：推理和修正能力不够时卡在执行循环里 | 风险：更复杂，需要对话管理和清楚的领导 |

最重要的一句是转引 Wang et al. [26]：

> *"multi-agent discussion does not necessarily enhance reasoning when the prompt provided to an agent is sufficiently robust"*

论文据此建议：**按用例的大背景选单/多，不要按需要多强的推理能力选**。

🔑 这是全文**唯一一条有外部实证支撑的选型建议**，而它说的是"prompt 写好了，多 agent 不一定更强"。和 MAST 的结论方向一致（↔ 阅读清单"多 agent 把 harness 问题乘了 N 倍"）。

### 3.2 异步执行

单 agent 也能同时发多个异步调用，但它**必须等这一批都回来才能评估下一步**；多 agent 里每个 agent 独立推进，不被别人的状态卡住。

依据：**纯概念推理，没有引用、没有测量**。⚠️ 这个论点在 2026 年看已经不太成立：并行 tool call、Tasks extension（W6 Act VI）让单 agent 也能不阻塞地派发长任务。

### 3.3 反馈与人类监督

- LM 倾向于**在回答早期就下结论**，造成偏离目标的"**雪球效应**"[34]——所以需要反馈
- 加入人类验证和反馈 *"yields more reliable and trustworthy results"* [4, 9]
- **谄媚**：LM *"tend to mirror the user's stance"* [20]；AgentVerse 发现 **agent 会接受其他 agent 的反馈，即使反馈不对**，导致整队走向错误计划 [2]
- 缓解：robust prompting，但要知道风险

🔑 **同伴谄媚是多 agent 特有的放大器**：单 agent 只会附和用户一个人；多 agent 里每个 agent 都可能附和另一个 agent，错误在团队里传染。

### 3.4 群聊与信息共享

- 多 agent 更容易陷入寒暄，问彼此 *"how are you"*；单 agent 没有团队要经营，所以更专注
- **横向**架构最严重：共享群聊，每条消息人人可见
- 解法：**消息订阅或过滤**
- **纵向**架构的问题相反：leader **忘了把关键信息传下去**，还没意识到别人看不到 → 团队困惑或结果幻觉
- 解法：*"explicitly include information about access rights in the system prompt"*

🔑 **横向的病是"信息太多"，纵向的病是"信息太少"**——同一个问题（上下文分配）的两个极端。↔ W2 的上下文膨胀、MemGPT 的"每轮塞什么"。

### 3.5 角色定义与动态团队

- 单 agent：角色定义让它专注、调对工具、**少幻觉自己没有的能力**（↔ RAISE 写 Python 的销售）
- 多 agent：每个 agent 知道自己负责什么、不越界；**明确的组长**简化分工；清楚的 system prompt 可以**直接要求 agent 别闲聊**
- 动态团队：按需进出，保证每轮参与的都适合这一轮

### 3.6 §5.3 的配方

> *"When constructing an agent team that needs to collaborate on complex goals, it is beneficial to deploy agents with at least one of these key elements: clear leader(s), a defined planning phase and opportunities to refine the plan as new information is learned, intelligent message filtering, and dynamic teams whose agents possess specific skills relevant to the current sub-task."*

**4** 个要素，"至少一个"。

### 作者没报的

- **没有一个成本数字**：多 agent 比单 agent 多花多少 token、多少延迟？只有 LATS 被提了一句"更耗算力"
- **没有失败率**：每种架构多常卡死、多常给错答案？
- **没有一个系统被作者自己跑过**——"observations of these systems in action"在正文里找不到落点

---

## 4. 论文自己的局限一节（§6）：评测问题

这一节其实写得比 §5 扎实，因为它在批评别人的方法，每条都有引用。

| 问题 | 论文怎么说 |
| --- | --- |
| **各自为政的 benchmark** | 很多团队随方法一起发布自己的 benchmark，没法横比；手工打造的复杂评测集**人工打分**，*"the ones developing the method are also the ones writing and scoring the results"* [2] |
| **随机性** | agent 多次运行答案不一致；小而复杂的评测集上，这个随机性问题更大 |
| **数据污染** | 题目稍改，模型表现就显著变差 [8, 38, 37] → 怀疑 benchmark 分数的真实性 |
| **静态 benchmark** | *"existing datasets usually fail to match the models' ever-evolving capabilities, because the complexity level of existing benchmarks is usually static and fixed"* [37]；对策：动态 benchmark、合成 benchmark——但人参与少了，正确性有风险 |
| **范围与迁移** | MMLU、GSM8K 是单轮、无工具的，不是 agent 的好代理；StrategyQA 多步但只有 Yes/No |
| **agent 专用 benchmark** | AgentBench（网页、命令行、游戏）、SmartPlay：成功率、与人类回答相似度、效率。但**工具使用效率、可靠性、规划鲁棒性**同样重要且难测，常要专家评估 |
| **真实世界** | 很多 benchmark 是逻辑谜题和游戏；**WildBench** 来自 WildChat 的 **570,000** 条真实 ChatGPT 对话；**SWE-bench** 是真实 GitHub issue，但只覆盖 Python |
| **偏见与公平** | agent *"less robust, prone to more harmful behaviors, and capable of generating stealthier content than LLMs"* [25]；被要求从某政治立场辩论时仍会回归模型自身的社会偏见 [24]；**真正鲁棒的偏见评测必须有人类评估** |

🔑 §6.2 那句"开发方法的人也是写题和打分的人"——**这篇综述自己的 §5 正好也是这个结构**：作者观察、作者总结、作者下结论，没有外部检验。

---

## 5. 失败模式与局限 🔥

论文没有失败模式专节，但它在 9 个系统里散落地报了一堆。收拢起来：

| 失败 | 出现在哪 | 🔑 属于哪一类 |
| --- | --- | --- |
| 重复同样的 thought/action，出不了循环 | ReAct、AutoGPT+P、单 agent 总论 | **控制流**：没有进展检测 / 退出条件 |
| 幻觉自己没有的能力（销售写 Python） | RAISE | **角色规格**：persona 没画边界 |
| 陷入局部最优 | Reflexion | **验证**：自评者和执行者同源 |
| 长期记忆被 token 上限截断 | Reflexion（滑动窗口） | **上下文分配** |
| 工具选错、探索方向不合理 | AutoGPT+P | **工具说明**（↔ W6 门 1–3） |
| 不能问澄清、用户不能中止 | AutoGPT+P | **人机接口**：没有 ask / abort 出口 |
| 闲聊、寒暄 | 横向多 agent | **通信**：信息太多 |
| leader 漏传关键信息 | 纵向多 agent | **通信**：信息太少 |
| 接受同伴的错误反馈 | AgentVerse | **验证**：同伴谄媚 |
| 早期下结论后滚雪球 | 总论 [34] | **验证**：缺中途检查 |
| 算力和时间成本高 | LATS | **成本** |

🔑 把右列再并一次，就是 **MAST 的三大类**：**系统设计**（控制流、角色规格、人机接口）/ **agent 间错位**（通信两极）/ **任务验证**（自评、同伴谄媚、雪球）。这篇 11 个月前**列举**了它们，MAST 用 **1,600+** 条轨迹**测量**了它们。

### ⚠️ 论文内部的不一致

**⚠️ ① ReAct 的"6% vs 14%"被转述错了。**
论文写：*"the ReAct method only hallucinated 6% of the time, compared to 14% using the chain of thought (CoT) method"*。
查 ReAct 原文 Table 2（见 vault 里的 [[ReAct 论文精读笔记]] §3.7）：**6% / 14% 是 false positive 率——只在 50 条"答对了"的轨迹里数，指"答案对但推理里有幻觉"**。在失败轨迹里，幻觉占 ReAct 的 **0%**、CoT 的 **56%**。所以"ReAct 只有 6% 的时候在幻觉"既不是整体幻觉率，也低估了 ReAct 相对 CoT 的优势。另外这句同时引了 [29]（CoT 原论文），而这个数字只来自 [32]。

**⚠️ ② 配方里到底有几个要素？§5.3 说 4 个，§7 说 6 个。**
§5.3：clear leader(s) / planning phase + refinement / message filtering / dynamic teams —— **4** 个。
§7：well defined system prompts / clear leadership and task division / reasoning-planning-execution-evaluation phases / dynamic team structures / **human or agentic feedback** / intelligent message filtering —— **6** 个。
多出来的"system prompt"和"feedback"在 §5.3 里本来是**单 agent** 的条件。结论把单、多 agent 两份清单合并了，但没说。

**⚠️ ③ 单 agent 到底需不需要人类反馈？**
§1 引言：单 agent 适合 *"feedback from other agent-personas or the user is not needed"* 的问题。
§5.3：*"Single agent patterns perform well when given a defined persona and set of tools, **opportunities for human feedback**, and the ability to work iteratively"*。
两处说法相反。可能的调和：引言说的是"任务本身不需要"，§5.3 说的是"实现上给了会更好"——但论文没做这个区分。

**⚠️ ④ 轮换领导"通信成本最低"，和它自己的 Figure 5 对不上（存疑）。** 见下一节 ⭐。

### ⭐ 埋起来的洞察（Figure 5，转载自 Guo et al.）

正文只引了 Figure 5 的两句话，图里的东西多得多。以下读数是**我从柱状图目测的，误差约 ±5，单位按原图**：

- ⭐ **人当 leader 的效果远大于任何 AI 当 leader**。3×GPT-4 团队完成时间：无 leader **~58**、固定 leader **~55**、选举 leader **~49**、**人当 leader ~28**——差不多**减半**。正文只用一句 *"most effective when the leader is a human"* 带过，没给量级。
- ⭐ **"快了将近 10%" 落在误差棒里**。固定 leader vs 无 leader（~55 vs ~58；GPT-3.5 团队约 ~93 vs ~103），两组的误差棒明显重叠。"nearly 10%"是点估计，原图看不出显著。
- ⭐⚠️ **选举 leader 的通信成本最高**：3×GPT-4 团队里约 **~135**，是其他配置（**~45–65**）的两倍多。而正文说 *"agents with a dynamic team structure with rotating leadership provide the best results, with both the lowest time to task completion and the lowest communication cost on average"*。**"选举 leader"和"轮换领导 + criticize-reflect"可能不是同一个实验条件**，我没读 Guo et al. 原文，没法确认——但读者只看这篇的话，会看到正文和图相反。**复习时别引"轮换领导通信成本最低"，除非去原文核对过。**
- ⭐ Figure 5(c)(d)：**2×GPT-4 + 1×GPT-3.5** 的团队通信成本（**~95**）明显高于 **1×GPT-4 + 2×GPT-3.5**（**~55**）。我的解读（未经原文确认）：**强模型更多，话也更多**。
- ⭐ arXiv HTML 版的 **Figure 2**（ReAct 对比图）只有图注没有图片，要看图得看 PDF。

---

## 6. 在 agent 谱系里的位置

和 vault 里**已读过**的论文并排：

| 论文 | 管哪一层 | 单 / 多 agent | **有没有 verifier / ground truth** | 证据类型 |
| --- | --- | --- | --- | --- |
| [[ReAct 论文精读笔记\|ReAct]] `2210.03629` | 循环本身 | 单 | ✅ benchmark 标签 | 实验 |
| [[Generative Agents 论文精读笔记\|Generative Agents]] `2304.03442` | 记忆 + 社会模拟 | 多（25 个） | ❌ 只能主张 believability | 实验 + 访谈 |
| [[Voyager 论文精读笔记\|Voyager]] `2305.16291` | 程序性记忆 / 技能库 | 单 | ✅ 环境判定 | 实验 |
| Reflexion `2303.11366`（阅读清单） | 情节记忆 / 自我反思 | 单 | ✅ 任务成败 | 实验 |
| **本篇** `2404.11584` | **架构选型词汇** | 单 + 多 | ❌ **没有任何数据** | 二手转述 |
| MAST `2503.13657`（阅读清单） | 多 agent 失败分类 | 多 | ✅ 人工标注，κ = **0.88** | **1,600+** 条轨迹 |
| [[Multi-Agent Deep RL Survey 论文精读笔记\|MARL 综述]]（本周另一篇） | 训练方案 + 多 agent 难题 | 多 | ✅ reward（各论文自己的环境） | 二手转述（RL 时代） |

**和本周 MARL 综述的对照**——同一组问题，两种 agent：

| 本篇（LLM 多 agent） | MARL 综述里的对应物 | 🔑 |
| --- | --- | --- |
| 纵向（有 leader） | master-slave（Kong 2017）/ CTCE | 集中决策，好协调，坏规模 |
| 横向（群聊） | broadcasting 通信（CommNet、RIAL） | 人人收到所有消息 |
| 消息过滤 / pub-sub（MetaGPT） | **targeted communication**（ATOC、TarMAC 用 attention 决定和谁说） | **MARL 2018 年就发现：选择性通信比广播好**——MetaGPT 是这条结论的 LLM 版 |
| DyLAN 按贡献排名淘汰 | **credit assignment**（COMA 的反事实基线、difference rewards） | DyLAN 用 LLM 评贡献，继承了谄媚问题；MARL 用反事实算 |
| 同伴谄媚 | 无直接对应；最近的是 **lazy agent**（一个学好了，另一个就不学） | LLM 特有 |
| 动态组队 | curriculum（从少量 agent 开始逐渐加） | |

最后一句：**这篇不是 MAST 的替代，而是 MAST 之上的一层词汇**——它告诉你有哪些旋钮（leader、过滤、分阶段），MAST 告诉你转错旋钮会怎么坏、坏得多常见。要选架构，两篇一起读；要引数字，只引 MAST。

### ↔ Week 06 Toolcraft II

| 这篇（2024-04） | W6（2026-10） |
| --- | --- |
| 工具说明写在 persona（system prompt）里 | Act IV："from baked-in to discovered"——工具说明搬到线上，由 server 发布、按需搜索 |
| AutoGPT+P 工具选错、卡循环 | 门 1–3（Clarity）：description 决定**是否**调用 |
| 只说"调工具很重要"，不谈接口 | 四个面：name / description / **schema（影响最大）** / error text |
| MetaGPT：结构化产物而非闲聊 | 礼貌规则：只返回下一步决策需要的，为有预算的读者塑形（门 7–9） |
| 纵向 leader 漏传信息 → "在 system prompt 里写清访问权限" | **"Labels request. Boxes enforce."**——写进 prompt 的权限只是请求，不是强制（门 10） |
| **全文没有安全一节**；"安全"只出现在偏见和有害内容 | Act X 整幕：prompt injection、凭证、gateway / registry / harness / sandbox 失守 |
| 点名 AutoGPT、BabyAGI、RAISE、LATS | Interlude：**表面会腐烂，原理是养老金**——两年后这些系统名大多不再被提起，但"角色定义、过滤、反馈"还在 |

---

## 7. 批判性分析

### 论文自己承认的

见 §6 整节（评测碎片化、污染、静态、迁移、真实世界、偏见）。注意：**它承认的全是"领域"的局限，没有一条是"本综述"的局限**——没说选文偏差、没说没跑实验、没说时效。

### 我自己补的

1. **零证据的因果主张。** §5.3 和 §7 说"至少用一招就**很可能**提升性能"。没有对照、没有计数，连"在我们见过的项目里有几个这样"都没有。这种句子不可证伪：任何好系统都会"至少用了一招"，因为六招几乎覆盖了所有设计。

2. **标题有 Tool Calling，正文没有工具接口。** 全文没有一句讨论工具的描述怎么写、参数怎么设计、错误怎么写、返回值多大。W6 给的证据说明这恰恰是决定性的：**schema 对选择影响最大**（`2610.14334`），写给开发者的报错让最强模型的恢复率从 **75%** 掉到 **6%**、改写后回到 **84%**（`2609.35381`）。这篇把工具当成"有没有"的能力，没当成"写得好不好"的接口。

3. **没有安全一节。** 2024 年 4 月时 indirect prompt injection 已经是公开话题（Greshake et al. 2023，`2302.12173`），而这篇唯一的"安全"是偏见与有害内容。它在 §5.2 给纵向架构开的药方——把访问权限写进 system prompt——在 W6 的框架里正好是**错的那一半**：label 只能请求。

4. **转述数字时丢了分母。** ReAct 的 6% 是"答对的轨迹里有多少推理带幻觉"，被写成"有 6% 的时候在幻觉"；Guo et al. 的 10% 落在误差棒里，被写成结论。一篇当词典用的综述，最容易被人整句转引——数字错了会一路传下去。

5. **"单 vs 多"这个二分掩盖了真正的变量。** 它自己引的 Wang et al. 说 prompt 足够好时多 agent 讨论不一定更强。那真正起作用的可能是：**总调用次数、总 token、有没有独立的检查步骤**——而不是"有几个 persona"。**值得做的复现实验**：同一任务、**相同 token 预算**下，比较 (a) 一个写好 prompt 的单 agent + 一次自检，(b) 3 个 agent 纵向，(c) 3 个 agent 横向；记录成功率、总 token、闲聊 token 占比。拿 FinePrint 的退货任务就能做，校验器现成。

6. **"动态团队"其实是 MARL 的 credit assignment，作者没意识到。** DyLAN 按贡献排名淘汰 agent，问题是"怎么知道谁贡献了多少"——这正是 MARL 综述 §5.4 的整个章节。DyLAN 用 LLM 打贡献分，等于用一个**会谄媚的评分员**做信用分配；MARL 那边的反事实基线（COMA）是算出来的。这篇没有引用任何 MARL 文献。

7. **利益相关（我的推测，论文未声明）。** 四位作者都在做 agent 落地咨询的公司，Figure 1 带公司标。论文不报任何失败率、任何成本，结论偏向"多种架构都有用武之地"。不能说结论因此错了，但读的时候要知道这是**卖方视角**。

---

## 8. 复习自测题

1. 这篇综述正文拆了几个系统？单 agent 几个、多 agent 几个？一共多少条参考文献？
2. 纵向和横向架构各自的**定义特征**是什么？论文说它们是两个类别还是一条光谱的两端？
3. 规划的 5 类方法是什么？出自哪篇论文？
4. AutoGPT+P 的 LLM 从哪 4 个工具里选？实际执行计划的是什么组件？
5. "ReAct 只有 6% 的时候在幻觉"——这个 6% 在 ReAct 原论文 Table 2 里实际指什么？失败轨迹里 ReAct 和 CoT 的幻觉占比分别是多少？
6. Guo et al. 里没有 leader 时，大约多少比例的通信在互相下命令？有 leader 时 leader 的通信有多少比例是发指令？
7. 从 Figure 5 看，3×GPT-4 团队里人当 leader 的完成时间约是无 leader 的几分之几？哪个条件的通信成本最高？
8. AgentVerse 的 4 个阶段是什么？它发现横向和纵向分别适合什么任务？
9. MetaGPT 用哪两个机制减少闲聊？
10. §5.3 的配方有几个要素？§7 又列了几个？多出来的是哪几个？
11. 论文引 Wang et al. 的哪句话对"该不该上多 agent"最关键？
12. WildBench 来自哪个数据集，有多少条对话？论文说 SWE-bench 的局限是什么？
13. 横向架构和纵向架构的信息共享问题分别是什么？论文给纵向架构开的药方是什么？用 W6 的哪句话可以反驳它？
14. 把这篇的"消息过滤"和 MARL 综述里的哪一类通信方法对应？哪篇 MARL 论文用 attention 决定和谁通信？

---

## 9. 核心数字速查表

| 项目 | 数值 |
| --- | --- |
| 版本 | v1，2024-04-17（唯一版本），PDF 13 页 |
| 作者 / 单位 | 4 位；Neudesic（IBM）、IBM、Microsoft |
| 拆解的系统数 | 9 个 = 单 agent 5 + 多 agent 4 |
| 参考文献 | 38 条 |
| 规划方法分类 | 5 类（出自 Huang et al. [12]） |
| ReAct：false positive（答对但推理含幻觉） | 6% vs CoT 14% |
| ReAct 原文：失败轨迹里的幻觉占比 | ReAct 0% vs CoT 56% |
| AutoGPT+P 的工具数 | 4 |
| AgentVerse 阶段数 | 4 |
| Guo et al.：有 leader 快多少 | "nearly 10%"（误差棒重叠） |
| Guo et al.：无 leader 时下命令占通信 | ~50% |
| Guo et al.：leader 通信中发指令占比 | 60% |
| Figure 5（目测）3×GPT-4 完成时间：无 / 固定 / 选举 / 人 | ~58 / ~55 / ~49 / ~28 |
| Figure 5（目测）GPT-3.5 团队：无 / 固定 leader | ~103 / ~93 |
| Figure 5（目测）选举 leader 通信成本 vs 其他 | ~135 vs ~45–65 |
| Figure 5（目测）2×GPT-4+1×3.5 vs 1×GPT-4+2×3.5 通信成本 | ~95 vs ~55 |
| §5.3 配方要素 / §7 结论要素 | 4 / 6 |
| WildChat 对话数 | 570,000 |
| MAST（对照）：轨迹数 / κ | 1,600+ / 0.88 |
| W6 对照：报错写给开发者时最强模型恢复率 vs 基线 / 改写后 | 6% vs 75% / 84% |

---

*笔记据 arXiv:2404.11584v1 全文（PDF 13 页，与 HTML 版逐段核对）。Figure 5 的数值为笔记作者从柱状图目测，未查 Guo et al. 原文；§5 不一致 ④、§6 的 MARL 对照表和 W6 对照表、§7「我自己补的」均为笔记作者补充，非论文原文内容。*
