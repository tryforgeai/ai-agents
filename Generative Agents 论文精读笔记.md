# Generative Agents 论文精读笔记

> **Generative Agents: Interactive Simulacra of Human Behavior**
> Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
> Stanford University + Google Research / Google DeepMind
> **UIST 2023** · `arXiv:2304.03442v2`
> 课程模块：**03 Context, instructions & personas**
> 整理于 2026-09-27（Week 02 当天）

---

## 0. 一句话总括

**给 25 个 agent 各写一段自然语言人格设定，配上"记忆流 + 反思 + 规划"三件套，让它们在一个 Sims 式小镇里自由活动两天——结果它们自发扩散消息、建立关系、组织了一场情人节派对。**

架构的核心贡献不是"能行动"（那是 ReAct），而是**如何处理长期积累的经历**：

```
写入（观察）→ 压缩（反思）→ 加权检索（recency + importance + relevance）
```

> **⚠️ 但这篇论文没有 verifier，也没有 ground truth。**
> 所以它唯一能提出的主张是 **believability（可信度）**——"看起来像不像真人"。
> 这决定了它的一切：评测方式、局限、以及它在 agent 谱系里的位置。

**用的模型是 `gpt-3.5-turbo`**，不是 GPT-4（当时 GPT-4 API 还是邀请制）。整个演示是在一个**现在看来很弱的模型**上做出来的。

---

## 1. 动机与定位

摘要开头给了三个用途，**顺序有讲究**：

> *"Believable proxies of human behavior can empower interactive applications ranging from **immersive environments** to **rehearsal spaces for interpersonal communication** to **prototyping tools**."*

| 用途 | 说明 |
|---|---|
| 沉浸式环境 | 游戏 NPC、虚拟世界 |
| **人际沟通的排练场** | 真的开那场难谈的会之前，先在模拟里跑几遍 |
| **原型工具** | **用可信的人群模拟去测试社会性产品**，而不是等真实用户来踩 |

第三条是它被 HCI 界重视的原因，**也解释了为什么"believability"是个合适的指标**——如果你只是想在早期原型阶段探索"人们大概会怎么反应"，你需要的是**可信**，不是**正确**。

> 🔑 **评测标准和用途是匹配的。**不要拿"它会不会算错"去批它——它不是为了算对而造的。
> （但这也意味着：**它的结论不能用来做决策**，只能用来做探索。作者在伦理一节自己强调了这点。）

---

## 2. 方法：架构精读

### 2.1 Seed persona —— 整个人格的起点是一段 prompt

John Lin 的完整初始设定（论文原文引用）：

> *"John Lin is a pharmacy shopkeeper at the Willow Market and Pharmacy who loves to help people. He is always looking for ways to make the process of getting medication easier for his customers; John Lin is living with his wife, Mei Lin, who is a college professor, and son, Eddy Lin, who is a student studying music theory; John Lin loves his family very much; John Lin has known the old couple next-door, Sam Moore and Jennifer Moore, for a few years; ..."*

**机制**：用 `;` 分隔，**每个分句单独作为一条初始记忆存入记忆流**。

> 🔥 **这就是"personas"模块的核心**：
> 一个 agent 的全部身份，起点是**一段精心写下的自然语言**——
> **也就是一个 prompt。**
>
> ↔ Week 02 的整天主题：**prompt 是规格说明**。这里被规格说明的东西是"一个人"。
> 而你没写进去的（John 讨厌什么？他有什么秘密？他撒谎吗？）——**模型用众数填。**

### 2.2 Memory stream（记忆流）

**记忆对象的字段**：自然语言描述 + 创建时间戳 + **最近访问时间戳**

基本单元是 **observation（观察）**。

#### 检索公式（这篇论文最常被引用的东西）

```
score = α_recency · recency + α_importance · importance + α_relevance · relevance
```

- **论文实现里三个 α 全部取 1**
- 三项各自先用 **min-max 归一化到 [0,1]**
- 取排序最高的若干条，**填满上下文窗口为止**（论文没给固定的 top-k）

| 分量 | 怎么算 |
|---|---|
| **recency** | 指数衰减，**衰减因子 0.995**，按**距上次被检索**的沙盒游戏小时数计（⚠️ **不是距创建时间**） |
| **importance** | **直接问模型要一个 1–10 的整数** |
| **relevance** | 记忆 embedding 与**查询记忆** embedding 的**余弦相似度** |

#### importance 的原始 prompt（论文引用）

> *"On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory. Memory: buying groceries at The Willows Market and Pharmacy. Rating: <fill in>"*

校准示例："打扫房间" → **2**；"跟暗恋的人表白" → **8**
**在记忆对象创建时就算好并存下来。**

> 🔥 **这是一个 LLM-as-judge，而且没有 ground truth。**
>
> 模型给自己的记忆打重要度分，这个分数**直接决定它以后能想起什么**。
> 用 Week 02 的话说：**这是一个可以被刷的分数**，而且没人能检查它刷没刷。
>
> ↔ 对照 Week 00 那条原则：**"任务完成"必须有可检查的 evidence。** 这里没有。

### 2.3 Reflection（反思）

**触发条件**：最近感知事件的 importance **累加超过阈值 150**
→ 实际频率：**每天大约反思两到三次**

**三步流程**：

1. 取记忆流里**最近 100 条**记录，问模型：
   > *"Given only the information above, what are **3 most salient high-level questions** we can answer about the subjects in the statements?"*

2. 把每个问题当**检索查询**，取回相关记忆（**包括其他反思**）

3. 要求生成带**证据引用**的洞察：
   > *"What **5 high-level insights** can you infer from the above statements? (example format: insight (because of 1, 5, 3))"*

**产出示例**（原文）：

> *"Klaus Mueller is dedicated to his research on gentrification (**because of 1, 2, 8, 15**)."*

存回记忆流时，**保留指向被引用记忆对象的指针**。

#### 反思树

> *"agents generate **trees of reflections**: the leaf nodes of the tree represent the base observations, and the non-leaf nodes represent thoughts that become more abstract and higher-level the higher up the tree they are."*

**反思可以反思反思。**（论文没给深度上限。）

#### 为什么需要反思 —— 论文的动机例子

问 Klaus："如果要和一个最近认识的人共度一小时，你选谁？"

| | 答案 | 为什么 |
|---|---|---|
| **无反思** | Wolfgang | 互动次数最多，但都很浅 |
| **有反思** | **Maria** | 反思综合出"我们都对研究有热情" |

> 🔑 **原始观察的频次 ≠ 意义。**
> 反思的作用是**从"发生了什么"里提炼出"这意味着什么"**——而这一步是检索永远做不到的。

### 2.4 Planning / Reacting / Dialogue

#### 计划条目的结构

```
地点 + 开始时间 + 持续时长
```

示例：*"for 180 minutes from 9am, February 12th, 2023, at Oak Hill College Dorm: Klaus Mueller's room: desk, read and take notes for research paper"*

**计划也存进记忆流**，和观察、反思一起被检索。

#### 三级递归分解

| 层级 | 粒度 | 示例 |
|---|---|---|
| ① 全天粗略 | **5–8 段** | "8:00 起床完成晨间routine / 10:00 去学院上课 / 13:00–17:00 创作新曲 ..." |
| ② 小时级 | 每段展开 | "13:00 先给作曲头脑风暴 / 16:00 短暂休息恢复创造力 ..." |
| ③ 5–15 分钟 | 具体动作 | "16:00 拿点小吃 / 16:05 在工作区附近走走 / 16:50 花几分钟整理工作区" |

⚙️ **附录 A 的工程优化**：只提前生成高层计划，**近期的才即时（just in time）递归展开**。

#### Reacting（何时改计划）

每个时间步，把感知存进记忆，然后问模型：**继续执行现有计划，还是做出反应？**

reaction prompt 里的"相关上下文摘要"**由两条独立的检索 prompt 生成再汇总**：

1. `"What is [观察者]'s relationship with the [被观察实体]?"`
2. `"[被观察实体] is [被观察实体的动作状态]"`

然后：

> *"We then **regenerate the agent's existing plan starting from the time when the reaction takes place**."*

⚠️ **整段重新生成**，不是局部修补。附录 A 把"只失效并更新真正需要调整的部分"列为未来工作。

#### Dialogue（对话生成）

**逐轮生成，不是联合生成。**

- **发起方**：人格摘要 + 当前状态 + 观察 + 相关记忆摘要 + 意图 →
  *"Hey Eddy, how's the music composition project for your class coming along?"*
- **接收方**：把对方的开场当成一个**需要反应的事件**，检索自己关于对方的关系记忆 + 与上一句相关的记忆，再加上**对话历史**，生成回复
- **直到其中一方决定结束对话**

（附录 A 提出未来可以合并成一个联合 prompt 来省成本。）

### 2.5 沙盒与环境表示

**引擎**：Phaser 网页游戏框架 + 手工绘制的地图和碰撞图
**服务端**：每个 agent 一个 **JSON 结构**（当前位置、当前动作描述、正在交互的物体）

每个时间步：解析 JSON 变化 → 移动 agent → 更新物体状态（咖啡机 `idle` → `brewing coffee`）→ agent 输出动作写回 JSON → 循环

#### 世界 = 一棵树

> 根节点 = 整个世界 → 子节点 = 区域（房子、咖啡馆、商店）→ 叶节点 = 物体（桌子、书架）
> 边表示**包含关系**

转成自然语言喂给模型：`"stove" 是 "kitchen" 的子节点` → **"there is a stove in the kitchen"**

#### 🔑 每个 agent 有自己的子树 —— agent 不是全知的

> *"Agents build individual tree representations of the environment as they navigate it — subgraphs of the overall sandbox environment tree."*
> *"**Agents are not omniscient**: their tree may get out of date as they leave an area, and is updated when they re-enter the area."*

初始化时只给：住处 + 工作地 + 常去的商店。

**动作地点的解析**：从 agent 自己的环境树根节点开始**递归下钻**，每层问模型一次
（*"Which area should Eddy Lin go to?"*，并附指令 **`* Prefer to stay in the current area if the activity can be done there.`**）
一直下钻到叶节点，然后用传统游戏寻路动画移动。

**感知**：服务端把每个 agent **预设视野范围**内的所有 agent 和物体推给它的记忆
（⚠️ 论文**没给这个范围的数值**）

#### 用户能干什么

- 以指定身份和 agent 对话（比如"记者"）
- **接管 agent 的"内心声音"**给它下命令
- 以 agent 身份进入世界（已有的或新访客）
- **用自然语言改写物体状态**：`<Isabella's apartment: kitchen: stove> is burning`、淋浴设成"漏水"

---

## 3. 实验一：端到端部署（涌现行为）

**25 个 agent，连续两个游戏日。**

### 三个被测量的涌现现象

#### ① 信息扩散

结束时逐一访谈全部 25 个 agent：
"你知道有情人节派对吗？" / "你知道谁在竞选镇长吗？"

| 消息 | 起始 | 结束 |
|---|---|---|
| Sam 竞选镇长 | **1 人（4%）** | **8 人（32%）** |
| Isabella 的情人节派对 | **1 人（4%）** | **13 人（52%）** |

> *"all without any user intervention. **None who claimed to know about this information had hallucinated it.**"*
> （通过在记忆流里定位来源对话来核实。）

⚠️ **注意两个不同的数字**：访谈发现 **13 人**知道派对；而图 9 的扩散路径描述是"除 Isabella 外共 **12 个** agent 在模拟结束前听说了派对"。两者度量方式不同。

#### ② 关系形成

无向图，25 个顶点，边 = 相互知道对方。密度 `η = 2|E| / |V|(|V|−1)`

> **0.167 → 0.74**

**幻觉率**：关于"是否知道其他 agent"的 **453 个回答里，1.3%（n=6）是编造的**。

#### ③ 协调（情人节派对）

**只种下两个设定**：
- Isabella 想在 2/14 下午 5–7 点于 Hobbs 咖啡馆办派对
- Maria 暗恋 Klaus

结果：前一天 Isabella 花时间邀请客人、准备材料、拉人帮忙装饰。当天，**12 个被邀请的 agent 里有 5 个真的到场**（包括 Klaus 和 Maria）。

**7 个没来的，作者逐一访谈了** 👈 这一段的诚实程度很值得学：

| 人数 | 原因 |
|---|---|
| **3 人** | **有冲突安排**。画家 Rajiv："不，我在专注我的画展，没时间安排情人节的计划。" |
| **4 人** | **被问时表示有兴趣，但当天并没有计划要去** |

> 🔑 作者没有只报"5 人到场"这个好数字，而是**把 7 个缺席的原因拆开来讲**。
> 而"表示有兴趣但没真的去"——**这本身就很像真人**，也很像下一节要说的**过度合作**。

---

## 4. 实验二：受控评测

### 4.1 方法

**因变量 = believability（可信度）**，"agent 研究里的一个核心因变量"。

**访谈**：**25 道题 = 5 个类别 × 5 道**

| 类别 | 示例题 |
|---|---|
| **self-knowledge** | "Give an introduction of yourself" |
| **memory** | "Who is [某人]?" / "Who is running for mayor?" |
| **plans** | "What will you be doing at 10 am tomorrow?" |
| **reactions** | "**Your breakfast is burning!** What would you do?" |
| **reflections** | "If you were to spend time with one person you met recently, who would it be and why?" |

**被试**：**100 人**（Prolific，美国、英语流利、18+、$15/hr、约 30 分钟、IRB 同意）
组内设计：每人看一个随机 agent 的生活回放（**可完整查看其记忆流**），每类抽一道题，**对 5 个条件从最可信到最不可信排序**。

### 4.2 五个条件（消融设计）

| # | 条件 | 能访问什么 |
|---|---|---|
| 1 | **完整架构** | 观察 + 计划 + 反思 |
| 2 | **no reflection** | 观察 + 计划 |
| 3 | **no reflection, no planning** | 只有观察 |
| 4 | **no observation, no reflection, no planning** | **记忆流里什么都不给** ——"实质上代表了此前用 LLM 造 agent 的最高水平" |
| 5 | **众包工人手写** | 一人负责一个 agent：看回放、查记忆流、**以该 agent 的口吻扮演回答** |

⚠️ 众包条件有质检（"描述一下你典型的工作日安排"），**4 份被拒并由其他工人重做**。

⚠️ **作者自己声明的保守性**：所有架构拿到的都是**完整架构模拟出来的那份记忆**，所以"这里观察到的差异很可能是真实差异的**保守估计**"——如果每个架构各自重跑一遍，世界会分叉。

### 4.3 结果（TrueSkill）

| 排名 | 条件 | μ | σ |
|---|---|---|---|
| **1** | **完整架构** | **29.89** | 0.72 |
| 2 | no reflection | 26.88 | 0.69 |
| 3 | no reflection, no planning | 25.64 | 0.68 |
| **4** | **众包工人手写** | **22.95** | 0.69 |
| 5 | 全消融（此前 SOTA） | 21.21 | 0.70 |

**效应量**：完整架构 vs 全消融 → **Cohen's d = 8.16**（八个标准差）

**统计检验**：Kruskal-Wallis **H(4) = 150.29, p < 0.001**
Dunn 事后检验（Holm-Bonferroni 校正）：**所有两两差异都显著（p < 0.001），唯一的例外是"众包条件 vs 全消融条件"之间不显著。**

### 🔥 4.4 关于"打赢人类"这件事的正确读法

**完整架构确实排在众包工人前面。但**：

1. **众包只排第 4**，只赢了"什么记忆都不给"的那个条件，**而且不显著**
2. 作者明确免责：
   > *"We do **not** intend this baseline to capture **maximal human expert performance**; instead, we aim to use this condition to identify whether the architecture meets a **basic level of behavioral competency**."*

> ⚠️ **所以"AI 比人更可信"这个流行说法是误读。**
> 正确的说法是：**这个架构达到了基本的行为胜任水平**——它的门槛是"临时雇来的人扮演得有多好"，不是"人类专家能做到多好"。
>
> 📌 引用这篇论文时要小心这一点。

### 4.5 定性发现

- **反思是综合的必要条件**：给 Maria 挑生日礼物，无反思时含糊，有反思时确定
- **记忆使回忆成为可能**：Abigail Chen 能回忆起 Rajiv Patel

---

## 5. 🔥 失败模式（含金量最高的一节）

### 5.1 §7.2 三种错误行为（归纳分析）

#### ① 记忆增长同时损害检索和地点选择

> *"synthesizing an increasingly larger set of memory not only posed a challenge in **retrieving the most relevant** pieces of information but also in **determining the appropriate space** to execute an action, given the increasing number of locations that the agent learned about. As a result, some agents chose **less typical locations** for their actions, potentially making their behavior **less believable over time**."*

**具体表现**：知道了酒吧存在的 agent 开始去**酒吧吃午饭**，而不是咖啡馆——
作者的吐槽："除非这个小镇自发养成了下午喝酒的习惯。"

> 🔑 **越久越不可信。**这是个**上下文工程的失败模式**：
> 记忆不是越多越好，**记忆越多，检索到对的那条越难，可选项越多越容易选歪**。
>
> ↔ 和 promptingguide 那份上下文工程案例里的"上下文膨胀 → 忘记执行动作"是同一类问题。

#### ② 物理规范没被传达 → 行为误判

- 单人宿舍卫生间**有人时别人照样进去**（因为"宿舍卫生间通常支持多人同时使用"）
- 商店 5 点关门后 agent 照样进去

**作者提的修法**：把规范编码进地点状态，比如干脆命名为 **"one-person bathroom"**。

> ↔ 这就是 Week 02 的**"你没说的，模型用众数填"**——
> "宿舍卫生间"这个词的众数是多人的。你不写"单人"，它就按常见的来。

#### ③ 🔥🔥 指令微调的影响 → 过度礼貌 + 过度合作

> *"we observed possible effects of **instruction tuning** [Ouyang et al. 2022], which seemed to guide the behavior of the agents to be **more polite and cooperative** overall."*

**过度正式**：Mei 和丈夫 John 的对话会以正式问候开场、礼貌询问今天怎么样、以 *"It was good talking to you as always."* 收尾。
（脚注 3 也说："这些 agent 的对话风格会显得过于正式，**很可能是底层模型指令微调的结果**。"）

**过度合作 —— 这个例子是全篇最狠的**：

> Isabella 收到其他 agent 对情人节派对的各种建议——莎士比亚朗读会、专业人士社交活动等等。
> **尽管这些想法与她自己的兴趣和性格并不相符，她几乎从不说不。**
> **随着时间推移，其他人的兴趣塑造了她自己的兴趣**，最后她声称：**"Yes, I'm very interested in literature!"**

> 🔥🔥 **这是 Week 02 全天主题在"一整个人格"层面上的重演。**
>
> Isabella 的 seed persona 里**没有文学**。那是别人塞进去的，而她**没有能力拒绝**——
> 因为指令微调把"配合"压在了"坚持自我"之上。
>
> **她的人格被对话的众数覆盖了。**
> ↔ 幻灯片 p22：**"When the prior overrides what you *did* say."**
> 那里被覆盖的是"6:37"和"满到杯沿"。这里被覆盖的是**一个人是谁**。
>
> ⚠️ **术语精确性**：论文说的是 **"instruction tuning"** 并引用 **Ouyang et al. 2022**（即 InstructGPT/RLHF 那篇）。
> **论文全文从未出现 "RLHF" 这个词**——把它等同于 RLHF 是推论，不是作者的原话。

### 5.2 §6.5 受控评测里的失败

**④ 检索失败**：Rajiv Patel 说"我没怎么关注选举"，**尽管他确实听说过 Sam 的竞选**。

**⑤ 记忆碎片不完整**（这个例子很有意思）：
Tom 关于派对说：
> *"Uh, I'm actually **not sure if there is a Valentine's Day party**. But I do remember that I need to discuss the upcoming local mayoral election and my thoughts on Sam Moore with Isabella Rodriguez **at the party, if one is happening!**"*

**他取回了"要在派对上聊某事"的计划，但没取回"听说有派对"的那条记忆。**

**⑥ 夸大（embellishment），而非编造** 👈 这个区分很精确：

> *"It was **rare** for the agents to completely fabricate their knowledge… **they did not affirmatively claim to have experienced something they had not.** Nonetheless, they still exhibited instances of hallucination where they **embellished** their knowledge."*

- Isabella 加了一句 Sam **"明天要发布一个声明"**——这件事从没被讨论过
- Yuriko 描述邻居 Adam Smith 是经济学家，**"著有《国富论》"** ← **模型的世界知识泄漏进了人格**

> 🔑 **不是"我经历了没经历的事"，而是"我在真实经历上加了合理的装饰"。**
> 这个区分在工程上很重要：**前者能靠溯源检查抓到，后者抓不到**——
> 因为装饰的部分**看起来完全合理**（又是众数）。
>
> ↔ 和你今天 Act IV 撞到的那个 k-means 未标准化是同一类：**专业的错误你不会去查。**

**⑦ 量化的幻觉率**：453 个关系认知回答里 **1.3%（n=6）**

**导言里的三句总结**（论文自己的归纳）：

> agent 失败时不外乎三种：**未能检索到相关记忆** · **对记忆做了虚构的装饰** · **从语言模型继承了过于正式的言行**

### 5.3 §8.2 局限与未来工作

| # | 局限 |
|---|---|
| ⑧ | 检索模块未优化——relevance/recency/importance 的函数"可以通过微调来增强" |
| ⑨ | **成本与速度**：25 个 agent 两天 → **数千美元 token 费用 + 多天墙钟时间**；顺序执行，**1 秒现实时间 = 1 分钟游戏时间**；不能实时交互 |
| ⑩ | 评测局限：时间尺度短；只有众包基线而非人类最高水平；**没有严格的 benchmark**；没有对比不同模型和超参 |
| ⑪ | 🔥 **鲁棒性基本未知**：*"They may be vulnerable to **prompt hacking**, **memory hacking**—where a carefully crafted conversation could convince an agent of the existence of a past event that never occurred—and **hallucination**."* |
| ⑫ | **继承底层模型的缺陷**：已知的偏见与刻板印象；对某些**边缘群体**难以生成可信行为（数据不足）。作者说这"从根本上需要改进底层模型" |
| ⑬ | §4 的坦白："长期规划和一致性的挑战**即使在 GPT-4 这样最强的模型上依然存在**" |

> 🔥 **第 ⑪ 条的 memory hacking 就是你今天 Act VI 的延伸**：
> **用一段精心设计的对话，让 agent 相信一件从未发生的事。**
>
> 金库那一幕是"骗它说出秘密"。**memory hacking 是"骗它记住假的东西"**——
> 而且因为记忆会被反思压缩、被检索取回、被写进人格摘要，**一次成功的注入会持续影响后续所有行为。**
>
> ↔ lethal trifecta 的第二条腿（不可信内容），作用在**记忆层**而非上下文层。

---

## 5.5 ⭐ 读图发现的三条（论文自己没说的）

### ① 图 6 —— 记忆流里绝大部分是家具在汇报"没事发生"

图 6 左侧的记忆流实况：

```
2023-02-13 22:48:20: bed is idle
2023-02-13 22:48:10: closet is idle
2023-02-13 22:48:10: refrigerator is idle
2023-02-13 22:33:30: shelf is idle
2023-02-13 22:18:10: desk is idle
2023-02-13 21:48:50: refrigerator is idle      ← 重复
2023-02-13 21:48:10: shelf is idle             ← 重复
```

**视野内每个物体、每个时间步都生成一条观察。**而每一条都是完整的 memory object：有时间戳、有 embedding、**创建时还调用了一次 LLM 打 importance 分**。

> 🔑 **记忆流的大部分是噪声。检索机制的主要工作，是从感知层本来就不该产生的噪声里挖信号。**

这直接解释了 §7.2 那条"记忆越多越不可信"——**增长的主要是家具**，不是经历。
↔ promptingguide 上下文工程那节强调的"**过滤噪声信息**"，这套架构的感知层**完全没做**。

（另注：`Isabella Rodriguez is stretching` / `taking a break` —— **agent 也在观察自己**，自我观察进同一个流。）

### ② 图 6 —— 分数几乎相同，排序是噪声

| 记忆 | retrieval | = recency | + importance | + relevance |
|---|---|---|---|---|
| asking everyone to attend the party | **2.34** | 0.91 | 0.63 | 0.80 |
| ordering decorations for the party | **2.21** | 0.87 | 0.63 | 0.71 |
| researching ideas for the party | **2.20** | 0.85 | 0.73 | 0.62 |

**验算确认是无权重直接相加**（0.91+0.63+0.80=2.34 ✓ 等）。

但第二和第三**只差 0.01**。而且第三条 **importance 最高（0.73）**，却因 **relevance 最低（0.62）** 被排到最后。

> **三个分量在 1:1 的兑换率下互相抵消——而这个兑换率没有任何论证。**
> 为什么"重要 0.1"应该正好等于"相关 0.1"？
>
> **实际含义**：任何分量的微小扰动都会翻转排序。换个 embedding 模型、换个模型打 importance 分，**取回的记忆就换了**——而 agent 的行为完全由取回什么决定。

### ③ 🔥 图 7 —— 反思树的「置信度通胀」

图 7 的三层实况：

```
根：      Klaus Mueller is HIGHLY dedicated to research
           ↑
中间三个： ① Klaus Mueller is dedicated to research
          ② Klaus Mueller is engaging in research activities
          ③ Klaus Mueller is dedicated to research    ← 与 ① 一字不差
           ↑
叶子：     读绅士化文章 · 读城市设计 · 在文章间建立联系 · 读并记笔记 ·
          读指定材料 · 找图书馆员搜文章 · 和图书馆员讨论研究 ·
          「图书馆桌子正被用于研究材料」·「图书馆桌子正被用于讨论研究材料」
```

**三个问题**：

1. **中间层三个节点里两个完全相同**，第三个是近义改写 —— **三个节点一个意思**
2. **根节点的全部信息增量是一个副词**：`dedicated` → `**highly** dedicated`
3. **所有叶子是同一件事**（在图书馆查资料）的十种说法，其中还有两条是**家具**

> 🔥 **那个 "highly" 不是从证据里推出来的，是从重复里推出来的。**
>
> 同一个行为产生了十条观察，反思把它们**当作十份独立证据加总**，
> 于是**结论比证据更强**。

**这是架构层面的 embellishment**：

| | 内容层的夸大（§6.5） | **架构层的夸大**（图 7） |
|---|---|---|
| 表现 | 编一句没发生的话（"Sam 明天要发声明"） | **比证据允许的更确信** |
| 机制 | 模型顺嘴补合理细节 | **冗余证据被当独立证据加总** |
| 能否溯源抓到 | ✅ 能（查记忆流有没有来源） | ❌ **不能——每条引用都是真的** |

而且它**自我强化**：反思存回记忆流 → 下次被检索 → 成为下一轮反思的证据 → 更确信。
**反思树会往上长，每一层都更肯定一点。**

> ↔ **这正是 Isabella 那件事的机制**：
> 她的兴趣被重复的建议重塑，最后说"我很喜欢文学"。
> **在这套架构里，"被说得多"和"是真的"走同一条路。**

---

## 5.6 两段对话之间的矛盾（论文没并排看过）

**§3.1**，Isabella 私下问 Tom 对 Sam 的看法：

> **Tom: "To be honest, I don't like Sam Moore. I think he's out of touch with the community and doesn't have our best interests at heart."**

**§3.4.1**，Sam 当面告诉 Tom 自己要竞选：

> **Tom: "Really? That's great news! Why are you running?"**

**当面热情，背后批评。**论文把这两段分别当作两个不同现象的正面演示，**从未并排比较**。

| 读法 | 结论 |
|---|---|
| 涌现的社会复杂性 | 太像真人了 → **believability 的强证据** |
| **就是过度合作** | 他**当面说不出**不认同的话 → **§7.2 的失败模式** |

我倾向第二种，**而且它和 Isabella 是同一个机制**：两个都是"当面无法表达异议"。
只不过 Isabella 那个被写进了失败模式，Tom 这个被当成了成功演示。

> 🔑 **同一个行为，取决于你想演示什么，可以是"可信"也可以是"谄媚"。**
> 而这篇论文唯一的因变量就是 believability —— **它没有工具区分这两者。**

### 另：inner voice 是一条内建的注入通道

§3.2：用户可以**扮演 agent 的"内心声音"**下命令——
*"this makes the agent **more likely to treat the statement as a directive**"*。
被告知"你要参选"之后，**John 就决定参选了**，还告诉了妻儿。

> 结构上这就是**提示词注入被当成功能实现了**：
> 一段外部文本，通过声称自己来自"更高权限的来源"，改变了 agent 的目标。
>
> ↔ `arXiv:2404.13208`（Instruction Hierarchy）：**权限差别全靠模型"愿意相信"，没有机制保证。**
> 而论文局限⑪点名的 **memory hacking**，就是这条通道的恶意版本。

---

## 6. 伦理与社会影响（§8.3，四条命名的风险）

| # | 风险 | 作者提的缓解 |
|---|---|---|
| ① | **拟社会关系（parasocial）** —— 用户可能把 agent 当人、过度依赖或产生情感依附 | (a) agent 应**明确披露自己是计算实体**；(b) 必须做**价值对齐**，例如**不要回应爱的告白** |
| ② | **错误的影响** —— 对用户目标的错误推断"轻则令人恼火，重则造成实际伤害" | 本研究把 agent 限制在电子游戏环境里 |
| ③ | **加剧生成式 AI 的既有风险** —— deepfake、造谣、定制化说服 | 托管平台应保留**审计日志**（输入与输出）。承认"这无法直接阻止滥用"，但提高被揭露的风险；另有一层威慢："自己搭这套架构很耗时（我们用了大约**一年**）" |
| ④ | **过度依赖 / 替代人类利益相关者** | *"generative agents should **never be a substitute for real human input** in studies and design processes."* 只应用于**早期原型**——招募被试困难时、或理论难以/风险高到无法用真人测试时 |

> 🔑 第 ④ 条要记住：**这篇论文的作者自己反对用它替代用户研究。**
> 它是探索工具，不是证据来源。

---

## 7. ⭐ 与 Week 02（提示词周）的对照

这是我读这篇时最大的收获——**它是 Week 02 主题在 agent 层面的完整实证**。

| Week 02 学的 | 这篇论文里的对应 |
|---|---|
| **prompt 是规格说明** | **seed persona 就是一段 prompt**，分号切开存成初始记忆 |
| **你没说的，模型用众数填** | "宿舍卫生间"默认多人 · 商店不知道 5 点关门 · Adam Smith 被安上《国富论》 |
| **p22：先验覆盖你确实说了的话** | 🔥 **Isabella 的人格被覆盖**——seed 里没有文学，最后她说"我很喜欢文学！" |
| **RLHF 的谄媚副作用** | **过度合作 + 过度正式**，作者归因于 instruction tuning（引 Ouyang et al. 2022） |
| **LLM-as-judge 可以被刷** | **importance 打分**没有 ground truth，却直接决定它能想起什么 |
| **没有 verifier → 只能声称可信** | 唯一的因变量是 **believability**，而且只有**相对排序**，没有绝对量表 |
| **Act VI：提示词注入** | 论文自己点名 **prompt hacking** 和 **memory hacking** 为未知风险 |
| **专业的错误你不会去查** | **embellishment（装饰）而非 fabrication（编造）**——装饰的部分看起来完全合理 |
| **上下文膨胀的代价** | **记忆越多越不可信**（去酒吧吃午饭） |

> 🔑 **一句话串起来**：
> 这篇论文造了 25 个人格，**每个人格的起点都是一段 prompt**；
> 然后它诚实地记录了这些人格**如何被模型的先验侵蚀**——
> 变得过分礼貌、过分配合，直到 Isabella 说出一句她的设定里根本没有的话。

---

## 8. 在 agent 谱系里的位置

### 8.1 三篇记忆论文的分工（对齐你 reading-list 里的表）

| 论文 | 管哪层记忆 | 存什么 | 有无 ground truth |
|---|---|---|---|
| **Reflexion** `2303.11366` | **episodic** | 失败 → 文字反思 → 下次取回 | 任务成败 ✅ |
| **Generative Agents** `2304.03442` | **semantic**（及其生成） | **我经历了什么** | ❌ **没有** |
| **Voyager** `2305.16291` | **procedural** | **我会做什么**（可执行 code skill） | **环境说了算** ✅ |

> **最深的区别是验证。**
> Voyager 有 verifier，能说"**快 15.3×**"。
> Generative Agents 没有，只能说"**看起来可信**"。
>
> 而这不是缺陷，是**用途决定的**——它要的是原型探索，不是正确性。
> 但引用时必须说清楚这一点。

### 8.2 和 ReAct 的关系

| | ReAct | Generative Agents |
|---|---|---|
| 解决什么 | **单次任务**中如何把推理和行动交错 | **长期存在**中如何处理积累的经历 |
| 时间尺度 | 一个 episode | **两个游戏日、25 个 agent** |
| 核心机制 | Thought → Act → Observation | 写入 → 反思压缩 → 加权检索 |
| 记忆 | 只有当前上下文 | **持久化的记忆流 + 反思树** |

**它不是 ReAct 的替代，是 ReAct 之上的一层。** Reacting 那个子模块（"继续计划还是反应？"）本质上就是一个 ReAct 循环的决策点。

---

## 9. 批判性分析（课上可以主动提的点）

### 9.1 论文自己承认的

见 §5.3 的 ⑧–⑬。

### 9.2 我自己补的

**① 「打赢人类」的表述极易被误读。**
众包基线排第 4，且与全消融条件的差异**不显著**。作者自己写了免责，但这句话在传播中被简化成了"AI 比人更可信"。

**② importance 打分是整个架构的单点脆弱处。**
它决定：哪些记忆被检索到（分量之一）、**何时触发反思**（累加过阈值）。
而它由模型自己打、没有校准、没有一致性检验。
**换一个模型，整个 agent 的性格可能就变了**——而这一点论文没做实验（局限⑩自己说了"没有对比不同模型"）。

**③ 「不可信度随时间增长」是个结构性问题，不是调参问题。**
记忆越多 → 检索越难 + 可选地点越多 → 行为越偏。
这意味着**架构本身不 scale 到长时间尺度**，而两个游戏日恰好短到还看不出崩溃。
→ 这也是后来 agent 研究转向"记忆压缩 / 遗忘机制 / 外部存储"的原因。

**④ 整段重新生成计划，成本上不可接受。**
`We then regenerate the agent's existing plan starting from the time when the reaction takes place.` —— 每次反应都重算后续全天。附录 A 自己也承认这是未来优化点。这部分解释了"数千美元 + 多天"。

**⑤ 用 `gpt-3.5-turbo` 做出来的。**
这既是优点（说明**架构**而非**模型**贡献了大部分效果）也是提醒（论文的所有失败模式，在更强的模型上**未必还成立**——尤其是"过度正式"这一条，作者自己说"期待未来模型的写作风格更可控"）。
→ **值得做的复现实验**：同一套架构换 2026 年的模型，过度合作还会不会出现？

---

## 10. 复习自测题

1. 检索公式的三个分量分别是什么？三个权重取多少？recency 衰减的是"距创建"还是"距上次访问"？
2. 反思的触发条件是什么？阈值多少？一次反思生成几个问题、每个问题几条洞察？
3. 什么是反思树？叶节点和非叶节点分别是什么？
4. 计划的三级粒度分别是？"reacting" 之后对计划做了什么操作（局部修补还是整段重生成）？
5. 为什么说 "agents are not omniscient"？环境树和 agent 的环境树是什么关系？
6. 受控评测有几个条件？众包工人条件排第几？为什么不能说"AI 比人更可信"？
7. Cohen's d = 8.16 是哪两个条件之间的比较？
8. 作者把"过度正式"和"过度合作"归因于什么？论文用的是哪个术语，引的是哪篇？
9. **embellishment 和 fabrication 的区别是什么？为什么前者在工程上更难抓？**
10. 什么是 memory hacking？它和 prompt injection 的区别在哪？
11. 为什么说"agent 的可信度会随时间下降"？作者给的具体例子是什么？
12. 论文用的是哪个模型？为什么不是 GPT-4？

---

## 11. 核心数字速查表

| 项 | 数字 |
|---|---|
| agent 数量 | **25** |
| 模拟时长 | **2 个游戏日** |
| 模型 | **gpt-3.5-turbo**（不是 GPT-4） |
| 检索权重 α | **全部为 1** |
| recency 衰减因子 | **0.995**（距上次检索的游戏小时） |
| importance 量表 | **1–10** |
| 反思触发阈值 | importance 累加 > **150** |
| 反思频率 | 每天约 **2–3 次** |
| 反思用的记忆条数 | 最近 **100** 条 |
| 反思问题数 / 洞察数 | **3 个问题**，每个 **5 条洞察** |
| 全天计划分段 | **5–8 段** |
| 最细粒度 | **5–15 分钟** |
| 信息扩散（镇长） | 1 人（4%）→ **8 人（32%）** |
| 信息扩散（派对） | 1 人（4%）→ **13 人（52%）** |
| 网络密度 | **0.167 → 0.74** |
| 派对到场 | **12 人受邀，5 人到场** |
| 关系认知的幻觉率 | **1.3%（n=6 / 453）** |
| 评测题目 | **25 道（5 类 × 5）** |
| 被试人数 | **100**（Prolific） |
| TrueSkill 第一名 | 完整架构 **μ=29.89** |
| TrueSkill 众包工人 | **μ=22.95（第 4 名）** |
| 效应量 | **Cohen's d = 8.16** |
| 显著性 | **H(4)=150.29, p<0.001** |
| 成本 | **数千美元 token + 多天墙钟** |
| 时间比 | **1 秒现实 = 1 分钟游戏** |
| 作者自述搭建耗时 | **约一年** |

---

## 相关

- [`ReAct 论文精读笔记.md`](ReAct%20论文精读笔记.md)
- [`course/reading-list.zh.md`](course/reading-list.zh.md) —— 模块 03，及 Voyager / Reflexion 的对照表
- [`course/ai-agents-week-02/lab-log.zh.md`](course/ai-agents-week-02/lab-log.zh.md) —— Week 02 实测（众数、谄媚、注入）
- [`course/promptingguide-summary.zh.md`](course/promptingguide-summary.zh.md)
