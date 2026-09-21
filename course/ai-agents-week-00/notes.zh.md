# AI Agents Week 00 现场笔记 — The loop, the governor, and the lamp

日期：2026-09-12
场合：Public Meetup · SupportVectors AI Lab
状态：**上课中，边听边填** ｜ 进度：**p.70 / ACT V 进行中**（ACT I–IV 已完）

> ⭐ **想快速回顾请看 [`summary.zh.md`](summary.zh.md)** —— 按概念组织的总结。本文件是逐页现场记录。

来源：
- `uploads/slide-01-title.png`（p.1 标题页）
- `uploads/slide-02-journey.png`（p.2 Today's learning journey — 七幕地图）
- `uploads/slide-04-speaker.png`（p.4 Prologue · The Speaker）
- `uploads/slide-05-lab-stats.png`（p.5 Prologue · What the lab has trained）
- `uploads/slide-06-three-pillars.png`（p.6 Prologue · 企业 AI 的三根支柱）
- `uploads/slide-07-act1-title.png`（p.7 ACT I 扉页）
- `uploads/slide-08-yanshi.png`（p.8 偃师献技）
- `uploads/slide-09-aladdin-lamp.png`（p.9 **Aladdin's lamp** — the lamp 揭晓）
- `uploads/slide-10-golem.png`（p.10 The Golem — system prompt + kill switch）
- `uploads/slide-11-ifa-orunmila.png`（p.11 Ifá / Orunmila — communal agency）
- `uploads/slide-12-baobab-proverb.png`（p.12 约鲁巴谚语 — baobab tree）
- `uploads/slide-13-witness-ledger.png`（p.13 The Witness — **ledger 伏笔**）
- `uploads/slide-14-resonances.png`（p.14 Resonances — ACT I 收束）
- `uploads/slide-15-act1-takeaways.png`（p.15 ACT I Key Takeaways）
- `uploads/slide-16-act2-title.png`（p.16 ACT II 扉页 — 盲人摸象）
- `uploads/slide-18-cacophony-schools.png`（p.18 The Cacophony — 三个流派）
- `uploads/slide-19-definition.png`（p.19 ⭐ **The definition that survives**）
- `uploads/slide-20-maui-example.png`（p.20 One worked example — Maui）
- `uploads/slide-21-model-plus-harness.png`（p.21 ⭐ **Model plus harness**）
- `uploads/slide-22-harness-gap.png`（p.22 Agent = model + harness，**harness gap**）
- `uploads/slide-23-quiz1.png`（p.23 Pop Quiz 1）
- `uploads/slide-24-quiz1-answered.png`（p.24 ⭐ Quiz 1 答案）
- `uploads/slide-26-why-agents.png`（p.26 ACT III — Why AI agents?）
- `uploads/slide-27-characteristic-moves.png`（p.27 ⭐ 五个特征动作）
- `uploads/slide-28-plumbing.png`（p.28 The Renaissance 1/2 — 2026 改变的管道）
- `uploads/slide-29-specialists.png`（p.29 The Renaissance 2/2 — 专门化）
- `uploads/slide-30-quiz2.png`（p.30 Pop Quiz 2 — revenge of the underdog）
- `uploads/slide-31-quiz2-answered.png`（p.31 ⭐ Quiz 2 答案）
- `uploads/slide-32-act4-title.png`（p.32 ACT IV 扉页 — 恒温器）
- `uploads/slide-33-provocation.png`（p.33 The Provocation — 写几个 skill 就够了吗）
- `uploads/slide-34-stand-up.png`（p.34 The Body Knows — 站起来做三个实验）
- `uploads/slide-36-standing-is-a-loop.png`（p.36 ⭐ 实验一 — Standing is a loop, not a state）
- `uploads/slide-37-hiking-pole.png`（p.37 实验二 — 登山杖）
- `uploads/slide-39-warmer-colder.png`（p.39 实验三 — Warmer, colder）
- `uploads/slide-41-watts-governor.png`（p.41 ⭐ **Watt's governor** — governor 的词源）
- `uploads/slide-42-kybernetes.png`（p.42 ⭐ **Kybernetes** — 舵手）
- `uploads/slide-43-open-loop-arithmetic.png`（p.43 ⭐⭐ **开环的算术** — 全天最硬的一页）
- `uploads/slide-44-tcp-over-ip.png`（p.44 ⭐ **TCP over IP** — 软件人的类比）
- `uploads/slide-45-container-contract.png`（p.45 ⭐⭐ **Tomcat does not read your HTML** — 边界）
- `uploads/slide-46-seven-verbs.png`（p.46 ⭐⭐ **What a harness is: seven verbs** — harness 的正式定义）
- `uploads/slide-48-bottleneck-verifier.png`（p.48 ⭐⭐ **The bottleneck is the verifier**）
- `uploads/slide-52-hunting.png`（p.52 ⭐ **Hunting** — governor 失灵：振荡）
- `uploads/slide-53-four-stop-rules.png`（p.53 ⭐⭐ **四条停止规则**）
- `uploads/slide-54-verifier-arithmetic.png`（p.54 ⭐⭐ **The verifier's arithmetic** — 算术的另一个方向）
- `uploads/slide-55-von-neumann.png`（p.55 ⭐⭐ **冯·诺依曼 1956** — restoring organ）
- `uploads/slide-56-quiz3.png` / `slide-57-quiz3-answered.png`（p.56–57 ⭐⭐ **Quiz 3 尽责的司机**）
- `uploads/slide-58-act4-takeaways.png`（p.58 ⭐⭐ **ACT IV 三句话总结**）
- ⚠️ **p.47、p.49–51 缺**（漏截）
- ⚠️ **p.35、p.38、p.40 缺**（漏截）
- ⚠️ **p.17、p.25 缺**（漏截，课后补）
- 📖 参考阅读：[`ref-harness-engineering.zh.md`](ref-harness-engineering.zh.md)（Addy Osmani 原文精读 —— **p.21/p.22 的直接来源**）
- 讲义 PDF：待补
- 下午 lab 仓库 / 代码：待补

---

## TL;DR（截至 p.18）

1. **讲师的方法论**：物理出身，全天的问题不是"agent 能干什么"，而是 **measured → verified → trusted** 三级递进。前两级不做，第三级（放手自主）就是幻觉。
2. **今天的范围**：企业 AI 三根支柱（Agents / RAG / Fine-tuning）里**只讲第一根**。微调被明确放在兜底位（"when the surface runs out"）。
3. **全天七幕**，题眼在 ACT IV（The Loop & the Governor）；产出物是一份 newsletter，而它"不能被单独信任去写"。
4. **ACT I 的落点**：*"The myths are not decoration. They are **the field's oldest failure catalog**."* 四个神话各对应 agent 的一个必要条件，缺哪个就对应一种今天仍在发生的失败。
   - 偃师 = 部件↔功能，**可归因**
   - 泥人 = **system prompt + kill switch**（刹车必须比油门便宜）
   - 神灯 = **delegation without verification**（今天最致命的那条）
   - Ifá = **distributed system**，multi-agent 原型
   - 新概念：**constructed agency** —— 能动性是被造的，所以有设计者、有责任人
5. **ACT II 在拆定义**：厂商说 workflow（*"微服务换了身时髦衣服"*），工具派说 API 协调者（*"一屋子工具不是工匠"*）。反向指向：agent 的关键在**运行时做决定的那个环节**，不在流程图也不在工具箱。
6. **两个未揭晓的伏笔**：
   - **猴面包树** —— 多 agent 何时是 blessing、何时只是 condition（**最后一讲**）
   - **ledger vs driver** —— 运行时的账 vs 事后的自述（**今天下午**）
7. **the lamp 已揭晓** = 阿拉丁神灯（p.9），三个词齐了。

---

## 讲师（p.4）

**Asif Qamar** — CTO @ SupportVectors AI Lab，三十年工程+教学。

- 履历：VP @ Cornerstone OnDemand、VP @ Evolv；更早 Oracle、Siebel、NASA/NCSA
- 学历：MS CS（UIUC）；B.Tech ECE（IIT-BHU 瓦拉纳西）；**理论粒子物理** MS + 博士阶段（Syracuse）；Wharton Executive CTO
- linkedin.com/in/asifqamar

> 自述定调：*"the physics still shows: this talk is about what can be measured, verified, and trusted."*

**这句是全天的方法论声明**，值得单独记一笔：物理背景 → 他不会从"agent 能做什么"讲起，而是从**能不能测量、能不能验证、能不能信任**切进去。三个动词正好对上 the governor（信任边界）和那句 "cannot be trusted to write alone"。听课时注意他是不是每讲一个部件都要问一句"这个怎么测"。

### Lab 背景数字（p.5）

3,500+ 校友（AI 工程师 / 数据科学家）｜20+ 师资｜20+ 从 bootcamp 项目孵化出的创业公司。

*（机构介绍页，跳过即可。）*

### 三根支柱：今天在整张图的哪个位置（p.6）

企业 AI 应用 = 三根支柱，**今天一整天只讲第一根**。

| 支柱 | 讲师原话 | 解决什么 |
| --- | --- | --- |
| **AI Agents** | *the reasoning-and-acting layer; today's whole day* | 模型**怎么行动**——推理 + 调工具 + 循环 |
| **RAG** | *the enterprise's own knowledge, on tap* | 模型**不知道你公司的事**——把私有知识接上 |
| **Fine-tuning & RL** | *making the model itself yours, when the surface runs out* | 前两者**触顶之后**——改模型本身 |

> *"Think ChatGPT, Perplexity, Claude as reference points — every one is all three."*

**两个值得记的点：**

1. **顺序即优先级**。"when the surface runs out"这个措辞是有立场的：先在**表层**（提示、检索、工具）榨干，实在不行才动权重。微调被放在最后一位、当兜底手段，而不是起手式。
2. **三者是叠加不是替代**。他拿三个成品产品举例，就是说明真实系统里三根都在，不存在"选哪个"的问题。

*→ 今天的范围：只有 agent 这一层。RAG 是前置（Week 09 OKF + Secure Retrieval 已覆盖），微调不碰。*

---

## 全天路线（p.2 "The map before the territory"）

| | 幕 | 标题 | 我的预判 |
| --- | --- | --- | --- |
| 谷 | **ACT I** | Myth to Machine | 从神话/幻想里的"仆人"讲到工程上的机器——大概是破除 agent 的浪漫想象 |
| 峰 | **ACT II** | What an Agent Is | 定义。和 LLM/workflow/chatbot 的边界在哪 |
| 谷 | **ACT III** | Why Now | 为什么是现在（长上下文？tool use？成本？） |
| 峰 | **ACT IV** | The Loop & the Governor | 全天最高点之一：循环 + 调速器。标题里的两个词在这合流 |
| 谷 | **ACT V** | The Engine Room | 机房——具体实现/代码层 |
| — | *lunch* | | 午餐分隔点落在 **ACT V 与 ACT VI 之间** |
| 峰 | **ACT VI** | The Newsletter | 下午 lab 的产出物：那份"不能被单独信任去写"的 newsletter |
| 谷→出口 | **ACT VII** | Anatomy & Landscape | 收尾：解剖 + 全景（生态/框架对比？） |

> 注意：标题页的第三个词 **the lamp** 没有出现在七幕标题里。要么藏在 ACT I（Myth to Machine — 神灯/精灵？），要么是 ACT VII 的收束意象。**听到时记一下**。

> 曲线本身是峰谷交替的，讲师应该是有意做成"张弛"节奏：定义/机制在峰，动机与落地在谷。

---

## ACT I — Myth to Machine

> 副标题（p.7）：*a universal aspiration through the ages — **and what it already knew***
>
> 「**已经知道了什么**」——这不是暖场的神话串烧。他要说的是：古人对"自动仆人"的想象里，已经包含了今天工程上真实存在的约束（愿望要说清楚、执行会跑偏、必须能叫停）。听的时候重点抓**他从每个神话里拎出的那条工程教训**，不是故事本身。

### 讲了哪些神话 / 传说

| # | 出处 | 故事 | 他拎出的教训 |
| --- | --- | --- | --- |
| p.8 | **偃师献技**（《列子·汤问》，周穆王） | 真人大小的自动人偶，能走能唱还调戏王的姬妾；拆开看，内部脏腑俱全。**抽掉一个"器官"，就精确地坏掉一个功能。** | *Parts that map to functions* —— **部件↔功能一一对应**。讲师明说「hold that for Act IV」 |
| p.9 | **阿拉丁神灯**（THE GENIE） | *The genie is the oldest dream of **delegation**: state the goal, and a power you do not fully understand carries it out — **often too literally**.* | **委托**的最古老形态。结论句：*"Every prompt-engineering horror story is a genie story."* |
| p.10 | **泥人 Golem**（希伯来传统） | 靠塞进嘴里的一个**写下的词**驱动；**抹掉一个字母它就停**。 | *an agent with a **system prompt** and a **kill switch***——而传说讲的多半是**造它的人忘了第二个**的下场 |
| p.11 | **Ifá / Orunmila 的使者**（约鲁巴，西非） | Orunmila 的使者在人间**自主行动**，遵循**共享的目标**。 | **Agency is communal** —— 智慧大到一个个体装不下，于是**分给许多各承一部分的人**。这是**多 agent** 的原型 |
|  |  |  |  |

#### p.8 偃师 — 展开

> 周穆王的反应：*"Can human skill match that of Nature?"*（人之巧乃可与造化者同功乎）

**为什么开场用这个**：这是有记载的最早的"自动机"叙事之一，而且它的重点不在于"像人"，在于**可拆解性**——抽掉肝就不能看，抽掉肾就不能走。这是一个**模块化、可归因**的系统。

**埋给 ACT IV 的线**：agent 也应该是这样的——loop、governor、memory、tool 各是一个部件，拆掉哪个就精确地失去哪项能力。反过来说，**如果一个系统坏了你说不清是哪个部件坏的，那它就不是工程，是魔法。** 这正好接上讲师那句 measured / verified / trusted。

> 注意对照：偃师的人偶是**可解释**的（拆开能看见因果）；今天的 LLM 恰恰**不可拆**（抽掉哪层神经元对应哪个能力，说不清）。他选这个故事开场，可能是要立一个**我们还没达到的标准**，而不是夸古人。听听他有没有点破这层反讽。

<details>
<summary>原故事梗概（《列子·汤问》）</summary>

周穆王西巡归来，工匠**偃师**求见，献上一个真人大小的"倡者"。它行走俯仰、转头自如，唱歌合律、跳舞合拍，与活人无异。穆王召来嫔妃同观。

演至将终，人偶**朝穆王身边的侍妾眨眼招手**。穆王大怒，当场要斩偃师。偃师惶恐，立刻剖开人偶——内里尽是皮革、木、胶、漆，涂以白黑红青；而**肝胆心肺脾肾肠胃俱全，外则筋骨肢节皮毛齿发一应俱备**，皆假物而无一缺。重新装配，又能活动如初。

穆王亲自试验：
- 去其**心** → 口不能言
- 去其**肝** → 目不能视
- 去其**肾** → 足不能行

穆王始叹服：**"人之巧乃可与造化者同功乎"**，以自己的副车载之而归。

结尾：鲁班（云梯）、墨翟（木鸢）素来自负，闻此事后**终身不敢再言其巧**。

</details>

#### 这个故事其实有两层，slide 只取了第二层

| | 内容 | 对应今天的什么 |
| --- | --- | --- |
| **第一层**（slide 未用） | 人偶做了一个**没被授权**的动作（调戏侍妾），制造者差点因此被杀 | 失控 + **问责**：出事时被追责的是造它的人。这是最早的一则"AI 事故归责"寓言 |
| **第二层**（slide 取此） | 拆解后，部件↔功能一一对应 | 可归因、可测量、模块化 |

> **待验证**：讲师若在 ACT IV 讲 governor 时回头提"那个眨眼的动作"，就是全天最漂亮的一次伏笔回收。注意听。

#### p.9 神灯 — 展开（**the lamp 揭晓了**）

标题三词之一的 **the lamp = 阿拉丁神灯**，落在 ACT I，不是 ACT VII。

> *"The genie is the oldest dream of **delegation**: state the goal, and a power you do not fully understand carries it out — **often too literally**."*
>
> *"Every prompt-engineering horror story is a genie story."*

**关键词是 delegation（委托）**。神灯把委托关系的三个要素一次凑齐，而这三个恰好就是今天用 LLM 的处境：

| 神灯 | 今天 |
| --- | --- |
| 你说一个**愿望**（目标，不是步骤） | prompt —— 你描述**想要什么**，不写怎么做 |
| 执行者的**能力你并不理解** | 模型内部不可解释（对照 p.8 偃师的"可拆解"，这里反过来了） |
| 它**照字面**执行 | 规格里没写死的部分，它按自己的理解补 |

**"often too literally"** 是重点：神灯故事里出事从来不是因为精灵不听话，**恰恰是因为它太听话**——它执行的是你**说出口的**那句，不是你**心里想的**那件。这就是规格与意图的缺口（specification gap）。

**两张 slide 连起来看，是一组对照：**

| | p.8 偃师 | p.9 神灯 |
| --- | --- | --- |
| 系统性质 | **可拆解**、部件↔功能对应 | **不可理解**的力量 |
| 问题出在 | —（这是正面范例） | **委托的规格**说不清 |
| 给今天的教训 | 要能归因、可测量 | 目标陈述本身就是风险面 |

→ 一个讲**结构**该是什么样，一个讲**委托**为什么危险。ACT IV 的 governor 大概就是这两者的交汇：给不可理解的力量套一个可拆解的外壳。

#### p.10 泥人 Golem — 展开

> *"The golem is an agent with a **system prompt** and a **kill switch** — and the legends are mostly about what happens when the maker forgets the second."*

讲师直接把术语按在了故事上，这是全场第一次出现**现代 agent 词汇**：

| Golem | 今天 |
| --- | --- |
| 嘴里塞的那个**写下的词** | **system prompt** —— 一段文字，使它从泥变成会动的执行者 |
| **抹掉一个字母**就停 | **kill switch** —— 停机开关 |
| 传说的主线是"造它的人忘了第二个" | 事故的主因不是能力，而是**没留停机手段**（或留了但没人去按） |

**额外的细节**（图上泥人胸口刻的字）：希伯来语 **אמת（emet，真理）**，抹掉第一个字母 א 之后剩 **מת（met，死亡）**。所以"停机"在原典里是个非常小的动作——**删一个字符**。

**三个值得记的点：**

1. **system prompt 是"驱动词"而不是"配置"**。Golem 的词不是参数，是它存在的理由；没有那个词，它只是一堆泥。这个类比提醒：system prompt 定义的是**身份和权限边界**，不是可有可无的前缀。
2. **kill switch 必须比启动更容易**。原典里造一个 Golem 要仪式、要咒语；停它只要划掉一个字母。**不对称是故意的**——刹车必须比油门便宜。反观现实：很多 agent 系统启动只要一行命令，想中途叫停却没有任何接口。
3. **"forgets the second"**——事故的责任点又一次落在**造物者**身上（和 p.8 偃师那层呼应：出事被追责的是工匠）。

#### p.11 Ifá / Orunmila — 展开（**多 agent 的原型**）

栏目名从单个神话变成了 **"African archetypes of agency"** —— 视角从"造物者与造物"切到了**能动性本身的组织方式**。

> *"Orunmila's emissaries act autonomously in the human world under **shared goals**. Agency is **communal** — wisdom too vast for one alone, distributed across many who each carry a part."*

约鲁巴的 Ifá 占卜体系里，智慧不集中在一个神身上，而是**分散**的：Orunmila 派出使者，每个使者**自主行动**，但**共享同一个目标**。

**这是前三个神话都没有的一层：**

| | 前三个（偃师 / 神灯 / 泥人） | 这个（Ifá） |
| --- | --- | --- |
| 结构 | **一主一仆**，单向委托 | **一组同侪**，共享目标 |
| 智慧位置 | 集中在造物者 / 执行者 | **分布**，没人掌握全部 |
| 关心的问题 | 我怎么控制它 | 他们之间怎么**协同** |

**对应到今天：multi-agent。** 三个关键词都在 slide 上：

- **autonomously** → 每个子 agent 自己决定下一步，不是被中央调度的函数调用
- **under shared goals** → 靠**共同目标**对齐，而不是靠命令链
- **each carry a part** → 分工：每个只掌握局部上下文（这既是优势——省 context，也是风险——没人看得到全局）

> **值得留意的张力**：ACT I 前三幕在讲"必须能控制、能归因、能叫停"，这一页却在说"能动性天然是分散的"。**分散 = 更难归因、更难叫停**。多 agent 让 p.8 的可拆解性和 p.10 的 kill switch 都变难——你要停的不是一个泥人，是一群。
>
> 听听他有没有点破这个矛盾，还是留到 ACT VII 的 landscape 再收。

#### p.12 猴面包树谚语 — **全天的伏笔**

> **"Wisdom is like a baobab tree; no one individual can embrace it."**（约鲁巴谚语）
>
> *"Remember the tree. By the last lecture you will know **when it is a blessing — and when only a condition**."*

猴面包树树干极粗，一个人张开双臂抱不过来——要几个人手拉手才能合围。所以谚语说的是：**智慧大到单个个体抱不住，只能合抱。**

**但讲师加的那句话才是重点，而且他明说了要留到最后一讲才揭晓：**

| | 含义 |
| --- | --- |
| **a blessing**（祝福） | 分布式是**优势**——并行、专精、单个 context 装不下的任务被拆开做 |
| **only a condition**（只是个既成条件） | 分布式是**不得已**——不是因为多个更好，而是因为一个装不下。它带来协调成本、归因困难、更难叫停 |

→ 他在预告：**multi-agent 不总是好事**。有时候你用多 agent 是因为设计得好，有时候只是因为你被迫的。**分辨这两者的能力，是今天结束时该带走的东西。**

> 这基本上确认了我在 p.11 记下的那个张力——他是**故意**留的，而且明确说了 ACT VII（last lecture）才收。到时候注意听他给的判据。

> **自己的记法**：以后设计多 agent 系统时先问一句——*我是在合抱一棵树，还是只是抱不动一根柱子？*

#### p.13 The Witness — **第二个明确伏笔（ledger）**

> *"He knows each destiny **as it is**, not as the person consulting believes it to be. The babalawo does not ask the client how things went; he **casts the opele and reads the odu** — an instrument with its own structure, not the diviner's opinion."*
>
> *"Hold this too. This afternoon you will meet a **ledger** that was present when the engine ran — and a **driver** who will tell you a different story."*

**术语**：*babalawo* = Ifá 祭司／占卜师；*opele* = 占卜链（抛掷用）；*odu* = 抛出的图样所对应的卦辞体系。

**这一页的论点：不要问当事人，要读仪器。**

| 神话侧 | 工程侧 |
| --- | --- |
| Orunmila **在创世时在场** | **ledger／trace** —— 运行时**在场**的记录 |
| 知道命运**本来的样子**，而非求问者**以为的样子** | 客观事实 vs 自述 |
| 占卜师**不问客户**"后来怎么样了" | 不要问 agent"你刚才干了啥" |
| 抛 opele、读 odu —— **工具有自己的结构** | trace 有固定 schema，不是模型生成的自然语言 |
| **不是占卜师的意见** | 不是 LLM 的自我总结 |

**讲师明说的伏笔（第二个）：**

> 下午你会遇到一个**运行时在场的 ledger**，和一个**说法不一样的 driver**。

→ 也就是说下午的 lab 会**故意制造一次矛盾**：agent（driver）自述"我做了 A、B、C"，而 ledger 记的是别的。**这是全天最重要的一个实验**，因为它一次性证明：

1. **模型的自述不可信** —— 不是撒谎，而是它在**事后重构**，重构会失真
2. **必须有独立于模型的记录** —— 由代码写，不由模型写
3. 这正是讲师开场 *measured / verified / trusted* 里的 **verified**：验证的定义就是"不采信自述，去查第三方记录"

> **和 p.8 偃师的呼应**：偃师那页讲"拆开能看见因果"。这页讲**不用拆也能知道**——只要你在它运行时就在旁边记账。**ledger 是 LLM 不可拆时的替代方案。**

> **反过来看 p.9 神灯**：精灵的问题是你不理解它。ledger 不解决"理解"，它解决**问责**——我仍然不懂你怎么做到的，但我有一份你做了什么的账。

**两个伏笔现在都挂上了：**

| # | 伏笔 | 揭晓时间 | 关键词 |
| --- | --- | --- | --- |
| 1 | 猴面包树：多 agent 是 blessing 还是 condition | **最后一讲**（ACT VII） | 取舍判据 |
| 2 | ledger vs driver：谁说的才算数 | **今天下午**（ACT V/VI） | verified |

#### p.14 Resonances — **ACT I 收束（讲师自己的对照表）**

标题直接回应扉页副标题：**What the old stories already knew**。

> *"Agency is communal — emissaries act autonomously under shared goals. **Ifá divination is a distributed system**: wisdom emerges from parts working together. The automaton's organs map to functions; the golem's word is a prompt; **the genie is delegation without verification**."*
>
> *"Modern parallel: multi-agent systems rest on the same principle of distributed collaboration — **and fail in the same ways the myths warned about**."*

**讲师给的一一对应（这是权威版本，替换我之前的推测）：**

| 神话 | 讲师的原话 | 现代对应 |
| --- | --- | --- |
| 偃师人偶 | *the automaton's organs map to functions* | 部件↔功能，可归因 |
| 泥人 Golem | *the golem's word **is a prompt*** | system prompt |
| 神灯精灵 | *the genie is **delegation without verification*** | **无验证的委托** |
| Ifá 占卜 | *a **distributed system**：智慧由各部分协作涌现* | multi-agent |

**两个要点：**

1. **神灯的定义被收紧了**。p.9 说的是"太照字面"，这里给出了更准的说法：**delegation without verification —— 委托了但没验证**。问题不在于它照字面办事，而在于**你交出去之后没有任何核对环节**。这就把 p.9 和 p.13 的 ledger 缝到了一起：神灯是病，ledger 是药。
2. **落点是那句 "fail in the same ways the myths warned about"**。他不是在说"古人真聪明"，而是在说：**这些失败模式今天一个都没解决**。神话已经把坑列全了，我们照样在踩。

> **ACT I 的完整论证**（到此结束）：
> 神话不是装饰。它们各自描述了 agent 的一个**必要条件**（可归因 / 有 prompt / 有停机键 / 可分布），而**缺哪一个就对应一种今天仍在发生的失败**。其中最致命的是神灯那条——**委托而不验证**。

#### p.15 Key Takeaways — **ACT I 结束**

> *"Autonomous behavior has fascinated us across centuries. The automaton is an early archetype of **constructed agency**. Technology's roots are deeply human — and deeply mythic."*
>
> **"The myths are not decoration. They are the field's oldest failure catalog."**

**⭐ 全幕的那一句：*the field's **oldest failure catalog***。**

神话不是暖场，是**这个领域最古老的一份故障清单**。它们不是在讲"人类多有想象力"，而是在**逐条列举委托一个自主执行者时会出什么事**——而这些条目今天一条都没过期。

**"constructed agency"（被建构的能动性）** 是这一幕给出的概念名：能动性不是长出来的，是**被造出来的**——既然是造的，就有设计者，就有责任人，就该有规格、闸门和账本。

**标题说 "three things to carry forward"，但 slide 上只有两段。** 第三样可能是口头讲的，或在下一页。**待补**。

> 我的猜测（按 ACT I 的论证走向）：① constructed agency 这个视角 ② 神话 = 失败清单 ③ 那个还没揭晓的判据（blessing vs condition）。若他口头讲了，回填此处。

#### ACT I 论证结构（四个神话 + 一句谚语 + 一个见证者）

| slide | 形象 | 它"早就知道"的那件事 | 对应部件 |
| --- | --- | --- | --- |
| p.8 | 偃师人偶 | 好系统应当**可拆解、可归因** | anatomy / trace |
| p.9 | 神灯精灵 | 委托的**规格永远不完整**，执行者照字面办 | prompt / spec gap |
| p.10 | 泥人 Golem | 必须有**启动词**，更必须有**停机键** | system prompt / **governor** |
| p.11 | Ifá 使者 | 能动性可以是**共享目标下的分布式协作** | **multi-agent** / 编排 |
| p.12 | 猴面包树 | 合抱**有时是祝福，有时只是没办法** | 多 agent 的**取舍判据**（留到最后一讲） |
| p.13 | Orunmila 见证者 | **不问当事人，读仪器**——在场的记录胜过事后的自述 | **ledger / trace**（下午揭晓） |

→ **结构 → 委托 → 控制 → 协作 → 取舍**。前三个是"怎么造一个并管住它"，第四个跳到"怎么让一群一起干活"，第五个反手提醒"一群未必比一个好"。

### 讲了什么

- 

### 我的理解 / 自己的例子

- 

---

## ACT II — What an Agent Is

> 副标题（p.16）：*a **cacophony** of definitions — **and the one that survives***
>
> 配图：**盲人摸象**。

**扉页就把这一幕的结构说完了：**

1. 先展示**definition 的乱象**（cacophony = 刺耳的众声喧哗）——每家一个说法，各摸到一部分
2. 然后给出**唯一活下来的那个**定义

**盲人摸象的用法值得留意**：这个寓言的常见解读是"每个人都只对一部分"（相对主义）。但讲师说的是 *the one that **survives***——他不打算停在"大家都有道理"，而是要**筛掉一批、留下一个**。所以配图是反讽：**摸象的人不是都对，是都不够。**

> 预期：他会先列几个流行定义（可能来自 OpenAI / Anthropic / LangChain / 学术界），逐个指出漏洞，再给一个经得起推敲的。**重点记他淘汰每个定义时给的理由**——理由比定义本身有用。

### 被列举的定义（cacophony）

**p.18 三个流派**（标题：*To the vendors, the programmers, the schools*）

| 流派 | 他们的定义 | 讲师的评语 |
| --- | --- | --- |
| **API Aggregators**（厂商） | *"It is a workflow!"* —— 一个**调用的 DAG**，某个节点上挂着 LLM | *programmers say **microservices, fashionably dressed*** —— 换了身时髦衣服的微服务 |
| **Researchers**（学术） | 环境中的**学习实体**（RL 教科书里的 agent）；或者认为**必须有身体**的具身智能 | （未直接否定，但显然不是他要的那个） |
| **Tool-use Maximalists** | agent 就是 **API 的协调者** | *Not wrong — but **a workshop full of tools is not a craftsman*** |

**⭐ 两句评语是这一页的全部价值：**

1. **"microservices, fashionably dressed"** —— 打的是**把 workflow 叫成 agent** 的做法。一个预先写死的 DAG，即使某个节点是 LLM，它的**控制流仍然是人写死的**。agent 的特征应该是**控制流由模型在运行时决定**，而不是画在图上。
2. **"a workshop full of tools is not a craftsman"** —— 打的是**把工具数量当能力**。给模型接 50 个 API 不会让它变成 agent。**工具是手段，不是能动性。** 缺的是那个决定"现在该拿哪把锤子、什么时候放下"的东西。

> 这两句合起来，已经在反向勾勒答案了：agent 的关键既不在**流程图**（外部写死的顺序），也不在**工具箱**（可用动作的数量），而在**中间那个在运行时做决定的环节**。
>
> → 高度指向 **the loop**（ACT IV）。

> **第二个流派他没给评语**，这是个信号——RL 那套"环境中的学习实体"可能反而离他的答案最近（有状态、有反馈、有终止条件），只是过重。注意他后面会不会回头取其中一部分。

### ⭐ 活下来的那个定义（p.19）

> # **An agent is an autonomous observer, reasoner, and actor in an environment.**
>
> *"**Observes** the world — the user, the tools' responses, the document. **Reasons** from observation toward a goal. **Acts** — through tools, on the world — and **observes again**. Autonomy is the closing of that loop **without a human turning the crank**."*
>
> *"Agent implies **agency**; there is no agency without the ability to autonomously reason **and** act. The 2023 name for the loop was **ReAct**."*

**三个动词 + 一个闭合条件：**

| | 内容 | 关键限定 |
| --- | --- | --- |
| **Observes** | 世界：用户、**工具的返回**、文档 | 观察对象包括自己动作的**后果** |
| **Reasons** | 从观察**朝向目标**推理 | 不是自由联想，是目标导向 |
| **Acts** | 通过工具**作用于世界** | 有副作用，不只是输出文字 |
| **↻ 再观察** | 回到第一步 | **这一步才让它成为循环** |
| **Autonomy** | **闭合这个循环** | *without a human turning the crank* |

**⭐ 定义的重心不在三个动词，在那句 "without a human turning the crank"（没有人在摇那个曲柄）。**

三个动词单独看，ChatGPT 也全占：它读你的话（observe）、想（reason）、给答案（act）。**区别在于谁把输出接回输入。** 普通对话里那个人是你——你看了回答，决定下一句问什么，然后手动摇一次曲柄。**agent 是把曲柄接上了自己。**

→ 这一下就同时解释了 p.18 两个流派为什么不够：
- **workflow/DAG**：曲柄是**画好的**，谁接谁是设计时定的，不是运行时决定的
- **工具协调者**：有手没有环——它能动，但下一步动什么还是外面告诉它的

**"Agent implies agency"** —— 这是词源级的论证：agent 这个词本身就意味着**能动性**，而没有"自主地推理**并**行动"的能力就没有能动性。注意那个加粗的 **and**：光会想不会做，或光会做不会想，都不算。

**ReAct**（2023 年给这个循环起的名字）= **Re**ason + **Act**。ReAct 是论文里那个 Thought → Action → Observation 的交替格式。讲师把它降格成"那一年对这个循环的叫法"，意思是：**循环是本质，ReAct 只是一种写法。**

> **和 ACT I 的接口**：p.15 的 **constructed agency** 在这里落地了——agency 的工程定义就是这个闭合的环。
>
> **和 ACT IV 的接口**：定义已经把 **the loop** 说完了。ACT IV 要加的应该是 **the governor**——**曲柄自己在转之后，谁来决定它转到什么时候停。** 自主性是定义里的核心，而调速器正是给自主性设边界的东西。

### p.20 一个走通的例子：**"Is it a good time to visit Maui?"**

> *The agent **observes** the question; **reasons** it needs weather, flights, and flight costs; **uses tools** to fetch them; **observes** the tool responses; **reasons** over them; **creates** a recommendation.*
>
> ⭐ *"**Six verbs, one loop. Everything else today is about making that loop trustworthy.**"*

**六个动词逐个对位：**

| # | 动词 | 这一步在干什么 |
| --- | --- | --- |
| 1 | **observes** | 读问题 |
| 2 | **reasons** | 判断**自己缺什么**：天气、航班、机票价 |
| 3 | **uses tools** | 去取 |
| 4 | **observes** | 读**工具返回的东西** |
| 5 | **reasons** | 在真实数据上推理 |
| 6 | **creates** | 给出建议 |

**注意第 2 步——这才是 agent 的分水岭。**

它不是被告知"去查天气和机票"，是**自己推出来需要这三样**。这就是 p.19 那句"曲柄没人摇"的具体样子：**下一步调什么工具，是运行时推出来的，不是流程图上画好的。**

**还要注意第 4→5 步**：先观察工具返回，再在**返回的内容**上推理。建议是**建立在取回的数据上**，不是建立在模型先验上。

> ← 这一点正好回答了我课上想的那个问题（"$200 去夏威夷"）。第 5 步如果在**真实价格**上推理，不可行性会自己暴露出来；如果跳过 3、4 直接从先验编，就会编出 $45/晚的 Waikiki 海景房。**"它怎么知道做不到" 的答案是：它去查了。**

**⭐ 落点那句是全天的纲领：**

> **Six verbs, one loop. Everything else today is about making that loop trustworthy.**

即：**agent 是什么，到 p.20 就讲完了。** 剩下六幕全部在讲一件事——**怎么让这个循环值得信任**。

| 对应 | 干什么 |
| --- | --- |
| ACT IV governor | 给循环设边界 |
| ledger / trace | 让循环可查（*verified*） |
| 人在回路 | 不可逆动作前停一下 |
| ACT VI newsletter | 在真任务上验证这套能不能成立 |

→ 呼应开场的 **measured / verified / trusted**：**trustworthy 就是那个 trusted 的落地词。**

### ⭐ p.21 **Model plus harness** — 2026 给定义加的东西

> *"The model is **the reasoner**. Everything around it — **what it is shown, what it may do, what checks its work, what stops it** — is the **harness**."*
>
> *"In 2023 we said 'agent = LLM + tools + loop.' In 2026 the industry says it plainly: **a decent model with a great harness beats a great model with a bad harness**."*
>
> *"The **unit of engineering** moved from the **prompt** to the **loop**. Acts IV and V are entirely about that loop."*

**harness 的定义 = 模型周围的一切，四件事：**

| 英文 | 中文 | 管什么 |
| --- | --- | --- |
| *what it is shown* | 给它看什么 | context 构造、progressive disclosure |
| *what it may do* | 允许它做什么 | 工具集、权限边界 |
| *what checks its work* | 谁检查它的活 | 验证、ledger、eval |
| *what stops it* | 什么能让它停 | **governor / kill switch** |

> 模型只是**推理器**（the reasoner）——它在这套装置里只占一个格子。

**⭐ 三个关键论断：**

1. **"a decent model with a great harness beats a great model with a bad harness"**
   → 工程杠杆在 harness 上，不在换模型上。这也是对"等下一代模型解决一切"的直接否定。

2. **"The unit of engineering moved from the prompt to the loop."**
   → **工程单元从 prompt 变成了 loop。** 也就是说：不再是"怎么把这句话写好"，而是"**这个环怎么搭**"。prompt engineering 降级成 harness 里的一个组件。

3. **"agent = LLM + tools + loop"（2023）→ model + harness（2026）**
   → 旧公式把 loop 和 tools 并列成两个零件；新说法把**除模型外的一切**打包成 harness，强调它是一个**要被设计的整体**，而不是几个附件。

#### 配套记忆：**谋事在模型，成事在 harness**

（*Model proposes, harness disposes.* — 改自 "Man proposes, God disposes"）

**这是理解 harness 的钥匙：模型从来没有行动过，它只发出请求。**

它输出的不是"我调用了 API"，而是一段文本：*"我想调用这个 API，参数是这些。"* 中间隔着整层代码——harness 可以拒绝、改参数、先问人、或者说"预算到了"。**模型对此无能为力，它甚至不知道自己的请求有没有被执行**，除非 harness 把结果告诉它。

| 今天的问题 | 答案都在 harness |
| --- | --- |
| agent 怎么被停止 | harness 不发起下一轮 |
| 不可逆动作怎么守 | 在 proposal 与 execution 之间插一个人 |
| 泥人那个字母在谁手里 | **harness** |
| "曲柄没人摇"是什么意思 | 曲柄一直在 harness 手里，只是它默认不问你 |

> **⚠️ 但这个不对称只在你用它的时候才存在。** 多数框架的 harness 是**橡皮图章**——模型说什么就执行什么，不检查、不限次、不问人。这时 "harness disposes" 名存实亡。
>
> **有否决权 ≠ 行使了否决权。** 下午的 lab 大概率就是演这个：先跑橡皮图章版，看它翻车，再往 harness 里加闸门。

### p.22 **Agent = model + harness** —— 带数字的公案

> **"If you're not the model, you're the harness."** —— **Viv Trivedy**
>
> *"It sounds like a **tautology** until you meet the numbers: the **same frontier model**, re-harnessed, moved from **Top-30 to Top-5** on Terminal-Bench — **not one weight changed**. Opus scores markedly better inside Claude Code's harness than in thinner wrappers."*
>
> *"Osmani's moral: **the gap between what models can do and what you see them doing is largely a harness gap**."*

**⭐ 讲师点名了来源** —— Viv Trivedy（造词者）+ **Addy Osmani**（那篇综述）。→ 已精读存档：[`ref-harness-engineering.zh.md`](ref-harness-engineering.zh.md)

**这一页的修辞结构值得学**：

1. 先承认那句话**听起来像同义反复**（"不是模型就是 harness"——废话）
2. 然后甩数字：**同一个前沿模型，只换 harness，Terminal-Bench 从 Top-30 到 Top-5，一个权重都没改**
3. 于是同义反复变成了**可测量的论断**

> ← 这正是开场 *measured / verified / trusted* 的现场示范：**一句直觉，配上一个数字，才成为工程主张。**

**⭐ harness gap（harness 差距）：**

> **模型"能做到的"和"你看到它做的"之间那道差距，主要是 harness 的差距。**

这句是对"等下一代模型"的终结性反驳：**你手上这个模型的能力，多半没被你的 harness 释放出来。** 与其等 GPT-6，不如去修 harness。

> **一个反直觉的细节**：*"Opus 在 Claude Code 的 harness 里，比在更薄的封装里得分明显更高。"*
>
> 但原文（Osmani）还有**另一半**：Viv 团队恰恰是**离开** Claude Code、用自定义 harness 才冲到 Top-5 的。两者不矛盾——原因是**模型 post-training 与 harness 耦合**（协同训练导致过拟合）：
> - 比"更薄的封装"好 → 因为 Claude Code 的 harness 就是它训练时用的那个
> - 但**为你的任务专门设计**的 harness 可以更好
>
> → **"最好的 harness 未必是模型训练时所在的那个，而是为你的任务设计的那个。"**（详见参考阅读 §5）

### p.23 Pop Quiz 1 — the elephant, again

> 题面：同事给你看一个系统——**固定的六步 DAG**，每步是一次带 prompt 的 LLM 调用，其中一步调天气 API，输出是一份报告。哪个定义符合？
>
> (a) 它是 workflow　(b) 它是 agent，因为它用了工具　(c) 它是 agent，因为它会推理　(d) 它是 multi-agent 系统，六次 LLM 调用
>
> *Pick one — then **say it back**: **what single property would have to be added** to make you comfortable with the word "agent"?*

### p.24 Quiz 1 — **讲师的答案**

> **"None of the four."**
>
> *"It is a **workflow with expensive nodes** — and **that is fine, workflows are honest**. Tools alone do not make agency (b), a **prompt is not reasoning toward a goal** (c), and **six calls are not six agents** (d). The missing property: **the loop must be able to observe its own result and choose the next step**."*
>
> **Say-back**: *"It becomes an agent when **the next step is chosen by what it just observed, not by the drawing**."*

**⚠️ 答案是「四个都不是」，不是 (a)。**

我第一反应选了 (a)，**错在没读出题面的陷阱**：四个选项里没有一个措辞是干净的。(a) 说"它是 workflow"——对，但四选一的设置本身在诱导你接受"这题有对的选项"。讲师的答法是**拒绝题面**。

> **这个设计本身就是 ACT II 的主题**：盲人摸象——**每个选项都摸到了一部分，但没有一个够。**

**逐条驳斥（讲师原话）：**

| 选项 | 驳斥 |
| --- | --- |
| (b) 用了工具 | **Tools alone do not make agency** —— 呼应 p.18 *"a workshop full of tools is not a craftsman"* |
| (c) 会推理 | **a prompt is not reasoning toward a goal** —— ⭐ 措辞很准：节点里那段 prompt **不是"朝目标推理"**，它只是一次填空。p.19 定义里的 reason 是**有目标指向**的 |
| (d) 六次调用 = 六个 agent | **six calls are not six agents** —— 数量不是判据 |

**⭐ 关于 (a)：*"workflows are honest"***

这句是这一页的态度，值得单独记：

> 它是**节点很贵的 workflow** —— **而这没什么不好，workflow 是诚实的。**

即：**讲师不是在贬低 workflow。** 问题不在于用 DAG，**问题在于把 DAG 叫成 agent**。
- workflow 诚实 → 它不假装自己有能动性，它的控制流写在图上，你看得见
- 把 workflow 包装成 agent 才是不诚实的（p.18 *"microservices, fashionably dressed"*）

> **实践含义**：很多任务**就该用 workflow**——固定流程、可预测、可测试、便宜。**先问"这个任务需要运行时决策吗"，不需要就别上 agent。**

**⭐ 缺失的那条属性（原话）：**

> **The loop must be able to observe its own result and choose the next step.**
> 循环必须能**观察自己的结果**，并**选择下一步**。

两个动作，缺一不可：
1. **observe its own result** —— 看见自己刚才那步干出了什么
2. **choose the next step** —— 基于此做选择

**⭐ Say-back（背下来这句）：**

> **"It becomes an agent when the next step is chosen by *what it just observed*, not by *the drawing*."**
>
> **当下一步由"它刚刚观察到的东西"决定，而不是由"那张图"决定时，它才成为 agent。**

*observed* vs *the drawing* —— **观察 vs 图纸**。这是全天关于 agent 定义的最精炼表述。

> 我之前的"加一条回边"说法方向对，但不够准：**回边是形式，"由观察决定"才是实质。** 一个写死的 while 循环也有回边，但它仍然是图纸在决定。

### 反例 / 不算 agent 的东西

- **一个 DAG，某节点挂着 LLM** —— 曲柄是画好的（p.18 厂商派）
- **接了 50 个 API 的模型** —— 有手无环（p.18 工具派）
- **普通聊天** —— 曲柄在人手里
- **跳过 3、4 步直接从先验作答** —— 没有 observe 工具返回，就没有闭环（只是在"假装"做过研究）
- 

---

## ACT III — Why Now

### p.26 **Why AI agents?** — 三条理由

| | 标题 | 原话 |
| --- | --- | --- |
| 1 | **Agentic reasoning patterns work** | *small models used **agentically** outperform much bigger models used **directly**, on task after task* |
| 2 | **Aligned to how humans solve problems** | *teamwork, planning, decomposition: **hundreds of millions of years of evolved sociology, borrowed*** |
| 3 | **No going back** | *once you solve complex problems this way, it just makes sense; enterprise adoption is a **Cambrian explosion*** |

---

#### 1. ⭐ 小模型 agentic 用法 > 大模型直接用

这是三条里**唯一可测量**的一条，而且和 p.22 是同一个论证的另一面：

| | 说的是 |
| --- | --- |
| p.22 **harness gap** | 同一个模型，换 harness → Top-30 到 Top-5 |
| p.26 这条 | **换更小的模型**，但用 agentic 方式 → 打赢直接用的大模型 |

→ 合起来是一个更强的结论：**结构的收益大于规模的收益。**

**为什么成立**（我的理解，待和讲师对照）：
- 直接用大模型 = **一次性出答案**，错了没有纠正机会
- agentic 用小模型 = **多轮 + 可以查证 + 可以重试**，每轮的错误有机会被下一轮的观察修掉
- 本质上是用**串行的步数**换**单步的智能**

> **经济含义**：便宜模型 × 多跑几轮，可能比贵模型跑一轮又好又省。这直接影响选型——**先问"这个任务能不能用结构补足能力"。**

---

#### 2. 借来的社会学

> *hundreds of millions of years of evolved sociology, **borrowed***

teamwork / planning / decomposition —— 人类解决复杂问题的方式，**不是被发明的，是被进化出来的**。agent 架构直接把这套现成的模式搬过来用。

> **← 这条回收了 ACT I 的 p.11（Ifá / communal agency）**。从"神话里早就有分布式协作"到"这套协作模式是进化产物，我们把它借来了"。
>
> ⚠️ 但它也和 **p.12 猴面包树**的警告并置：**借来的东西未必总是好的**。人类团队也有协调成本、也会互相甩锅、也会集体跑偏。**blessing or condition 的问题在这里又出现了一次。**

---

#### 3. No going back / 寒武纪大爆发

> *once you solve complex problems this way, **it just makes sense***

**最弱的一条，本质是势头论证**（"大家都在用"）。*Cambrian explosion*（寒武纪大爆发）指企业采用的物种式爆发。

> ⚠️ **注意**：这条**不是技术论证**。"回不去了"和"这是对的"是两件事。按讲师自己的 measured / verified 标准，这条其实不合格——**它可测量的只是采用率，不是有效性。**
>
> 不过放在 ACT III（Why Now）的语境里合理：这一幕本来就是讲**时机**而非**原理**，采用势头确实是时机的一部分。

### ⭐ p.27 **The characteristic moves** — agentic 推理的五个特征动作

每条都配了一个**一词隐喻**，这是记忆锚点：

| # | 动作 | 是什么 | 隐喻 |
| --- | --- | --- | --- |
| 1 | **Planning & decomposition** | 路线，**拆成可检查的小块** | **measure twice**（量两次再下刀） |
| 2 | **Tools** | 传感器与执行器 | **the hands**（手） |
| 3 | **Memory** | **跨步骤、跨会话**的状态 | **the notebook**（笔记本） |
| 4 | **Critique & reflection** | 读自己的输出 | **the mirror**（镜子） |
| 5 | **Collaboration** | 多个 agent，**当信息量要求时** | **the team**（团队） |

**⭐ 注意 slide 的视觉设计**：五个条块**逐级右移、颜色红蓝交替**——不是并列清单，像是**阶梯**。可能暗示由浅入深或依赖顺序（planning 最基础 → collaboration 最高阶）。

---

#### 逐条要点

**1. Planning & decomposition —— *in checkable pieces***

关键限定是 **checkable（可检查的）**。拆解的目的不只是"变小"，是**让每块的完成可以被验证**。拆成十个说不清做没做完的小块，等于没拆。

> *measure twice* 来自木工谚语 "measure twice, cut once"（量两次，锯一次）——**在不可逆动作之前多确认一次**。正好对上 newsletter 的"发送"那步。

**2. Tools —— *sensors and actuators***

⭐ **这个措辞比"调 API"准得多**：工具分两类——
- **sensors（传感器）**：读进来（搜索、读文件、查数据库）→ **可逆，随便用**
- **actuators（执行器）**：作用出去（发邮件、写文件、下单）→ **不可逆，要设闸**

> **→ 这是 governor 的天然分界线。** 权限设计应该按这条线切，而不是按工具名字一个个列。

**3. Memory —— *state across steps and sessions***

两个尺度：**跨步骤**（本轮循环内，scratchpad）和**跨会话**（下次还记得，持久化）。

> 隐喻是 **the notebook（笔记本）** —— 呼应 p.13 的 **ledger**，但不是同一个东西：
> - **notebook / memory** = agent **自己写给自己**看的（可以被它改）
> - **ledger / trace** = **harness 写的、agent 改不了**的账
>
> **两者必须分开。** 让 agent 自己记账，就是让 driver 自己写行车记录。

**4. Critique & reflection —— *read your own output***

隐喻 **the mirror（镜子）**。

> ⚠️ **这条和参考阅读里 Anthropic 的发现直接冲突**：
> *"agents reliably **skew positive** when grading their own work."*（自评可靠地偏乐观）
>
> **照镜子的问题是：镜子里那个人也是你。** 所以业界的做法是 **planner / generator / evaluator 分离**——让**另一个** agent 来评。
>
> → **待问讲师**：self-critique 在什么条件下有效？他把它列为特征动作，但独立 evaluator 明显更强。是不是只在"低风险 + 有客观信号（如测试报错）"时才用自评？

**5. Collaboration —— *when information demands***

⭐ **限定词很重要：*when information demands*** —— **当信息量要求时**，不是默认。

> **← 这是 p.12 猴面包树伏笔的第一次部分揭晓。**
> 判据雏形出现了：**多 agent 的触发条件是"信息量单个装不下"**，不是"任务复杂"、不是"看起来该分工"。
>
> 也就是说：**blessing = 信息确实超出单个 context；condition = 你只是习惯性地拆了。**
>
> 完整判据应该还在 ACT VII，但这个限定词已经给了方向。

---

#### 五个动作 ↔ harness 四件事（p.21）的对照

| 特征动作 | 对应 harness 的哪一件 |
| --- | --- |
| Planning | *what it is shown*（plan 文件、分解后的上下文） |
| **Tools** | ***what it may do***（sensors 随便用 / actuators 设闸） |
| Memory | *what it is shown*（记忆文件注入） |
| **Critique** | ***what checks its work*** |
| Collaboration | 编排逻辑（子 agent、context 防火墙） |

> **缺了一件**：*what stops it*（**governor**）**不在这五个动作里**——因为它不是 agent 的"动作"，是**加在 agent 身上的约束**。
>
> → 这正是 ACT IV 要补的那一半。五个动作讲的是 agent **能做什么**，governor 讲的是**什么时候不许做**。

### p.28 **What 2026 changed — the plumbing**（Renaissance 1/2）

> 技术使能因素在这里出现了。栏目叫 **the plumbing（管道）** —— 不是新思想，是**基础设施铺好了**。

| | 变化 | 原话 |
| --- | --- | --- |
| 1 | **MCP, the USB of agents** | *models **decoupled from tools**; **build the hospital once, drop in any doctor**. Half a billion SDK downloads a month* |
| 2 | **Prompt optimization** | *the prompt as a **trainable parameter**: DSPy, GEPA and kin rewrite it **thousands of times against real data**. **The art became a compile step*** |
| 3 | **Orchestration became the harness** | *durable execution, a graph runtime, a harness on top, a hosted fleet above. **The competition moved from the graph to the loop*** |

---

#### 1. MCP —— agent 的 USB

**关键词：decoupled（解耦）。**

MCP 之前，每接一个工具都要为特定模型/框架写一遍适配。MCP 之后，**工具和模型各自独立**——工具方实现一次协议，任何模型都能用。

> **"Build the hospital once, drop in any doctor."**
> 医院（工具、基础设施、流程）建一次，**医生（模型）随便换。**

这个比喻精确对应 p.21/p.22 的 model + harness：**harness 是医院，模型是可替换的医生。** MCP 就是让"换医生"这件事变得便宜的那个标准。

> 数字：**每月五亿次 SDK 下载**。（⚠️ 待核实口径——是 MCP SDK 全部语言合计？记下来存疑。）

> ⚠️ **安全对照**（参考阅读 §4.8）：MCP 的工具描述会进 prompt，**任何你装的 MCP server 都是模型会读的可信文本**。解耦带来便利，也把**提示词注入面**扩大了。

#### 2. Prompt optimization —— **"the art became a compile step"**

**⭐ 这是这一页最锋利的一句。**

> prompt 作为**可训练参数**：DSPy、GEPA 这类框架**拿真实数据把它重写几千遍**。

含义：**手写 prompt 这件"手艺"，变成了编译流程里的一个自动步骤。**

| 过去 | 现在 |
| --- | --- |
| 人凭直觉调措辞 | **优化器**在真实数据上搜索 |
| "感觉这样写更好" | **有指标、可复现** |
| prompt engineering 是技能 | prompt 是**被编译出来的产物** |

> **← 这条和 p.21 "unit of engineering moved from the prompt to the loop" 是同一件事的两面**：
> prompt 不再是你的工程对象，**因为它已经可以被自动生成了**。你的工程对象上移到了 loop。

> **注意**：这也再次落在 *measured* 上——**能被优化的前提是能被评分**。没有 eval 就没有 prompt optimization。

#### 3. Orchestration became the harness —— **"from the graph to the loop"**

四层栈：**durable execution（可持久化执行）→ graph runtime（图运行时）→ harness → hosted fleet（托管集群）**

> **⭐ "The competition moved from the graph to the loop."**
> **竞争从"图"转移到了"环"。**

即：**编排框架时代结束了。** 过去大家比谁的 DAG 画得好、图运行时更强（LangChain/LangGraph 那一代）；现在比的是**循环本身的质量**——context 管理、闸门、验证、恢复。

> **← 完美闭合 ACT II**：p.18 嘲讽"把 DAG 叫 agent"，p.24 说"workflow 是诚实的"，这里给出**行业层面的同一判断**：图这一层已经商品化了，**价值在环上**。
>
> 也呼应参考阅读 §6 的 **HaaS（Harness-as-a-Service）**：从"建立在 LLM API 上"到"建立在 harness API 上"。

---

### p.29 **What 2026 changed — the specialists**（Renaissance 2/2）

> p.28 讲**管道**（基础设施），p.29 讲**专门化**（能力怎么被定制、组合、部署）。

| | 变化 | 原话 |
| --- | --- | --- |
| 1 | **Skills, fine-tuning, RL** | ***cheapest first**: a **packaged procedure with its contract**, now an **open standard with a marketplace**; then **surgery on the weights*** |
| 2 | **Cooperative games, with a science** | *MARL, and the **first controlled studies of *when* a team beats a soloist*** |
| 3 | **Forever observing** | *ambient agents that **watch a signal and nudge before you notice**; **physical AI is the same idea with a body*** |

---

#### 1. Skills → fine-tuning → RL：**cheapest first**

**⭐ "cheapest first" 明确了定制能力的阶梯顺序**，并且回收了 p.6 三根支柱里那句 *"when the surface runs out"*：

| 层 | 手段 | 代价 |
| --- | --- | --- |
| 最便宜 | **Skill**（打包好的流程 + 它的契约） | 写个文件 |
| ↓ | fine-tuning | 要数据、要训练 |
| 最贵 | RL | *surgery on the weights*（**在权重上动手术**） |

**Skill 的定义很准：*a packaged procedure with its contract***
- **procedure（流程）** —— 怎么做这件事
- **its contract（它的契约）** —— 什么时候该用它、输入输出是什么

> **"now an open standard with a marketplace"** —— skill 已经标准化 + 有市场了。
> ← 正好对上我们前面聊的 progressive disclosure：**skill 之所以能有 marketplace，前提是它可以按需加载**，否则装十个就把 context 撑爆了。

> **实践含义**：想让 agent 会做某件事，**先写 skill，别急着微调**。顺序是 skill → fine-tune → RL，不是反过来。

#### 2. ⭐ MARL + **"when a team beats a soloist"**

**这是猴面包树伏笔的第二次推进，而且这次给的是"科学"而不是直觉。**

> MARL（Multi-Agent Reinforcement Learning，多智能体强化学习），以及**第一批关于"团队何时胜过独奏者"的受控研究**。

| p.12 猴面包树 | 提出问题：多 agent 何时是祝福，何时只是不得已 |
| p.27 collaboration | 给了一个限定词：*when information demands* |
| **p.29 这条** | **说这个问题现在有受控实验了** —— 从直觉变成可测量 |

> ⚠️ **"first controlled studies"** —— "第一批"意味着**这仍是开放问题**。他没说结论是什么。
>
> **→ 课后必查**：这些研究具体是哪些？结论是什么？（记到待办）
>
> 也解释了为什么完整判据要留到 ACT VII —— **因为答案本身还在形成中。**

#### 3. Forever observing —— **ambient agents**

> *ambient agents that **watch a signal and nudge before you notice***
> **环境型 agent：盯着某个信号，在你注意到之前推你一下。**

这是**触发方式的转变**：

| | 谁发起 |
| --- | --- |
| 传统 agent | **你问它** → 它跑 |
| ambient agent | **信号变了** → 它自己跑 → 来找你 |

> **"physical AI is the same idea with a body"** —— 机器人 = 同一个想法加个身体。
> ← 回收 p.18 学术派的"具身智能"：他当时没否定，这里给了它位置——**具身不是另一类东西，是 ambient agent 的物理版本。**

> ⚠️ **这条对 governor 的要求最高**（连接我之前整理的"停止"那节第 4 点）：
> - 没有人在旁边看着
> - **停这一轮 ≠ 停这个 agent**，信号还会再来
> - "nudge before you notice" 意味着**它的动作默认到达人**——这本身就是个不可逆动作面
>
> **→ ambient = 自主性最高，因此闸门必须最严。**

---

### p.30–31 Pop Quiz 2 — **revenge of the underdog**

> **题面**：一个 7B 模型**agentic 地用**——规划、调两个工具、检查自己的答案、重试一次——在你的 benchmark 上**打赢了一个只调用一次的前沿模型**。你经理的结论：**"小模型比我们想的聪明。"**
>
> *Is the conclusion right? Then say it back: **what, precisely, did the small model have that the big one was denied?***

#### ⭐ 讲师的答案（p.31）

> **"The conclusion is wrong, and the win is real."**
>
> *"The small model was **not smarter** — it had a **loop**: **tools** (fresh information), a **check** (verification), and a **retry** (correction). The frontier model was run **open-loop**. **Compare loops to loops and the gap mostly closes; but a loop around a cheap model is the better engineering.**"*
>
> **Say-back**: ***"The small model had a harness; the big one had a prompt."***

**⭐ "The conclusion is wrong, and the win is real."** —— 这句结构很重要：**结论错了，但胜利是真的。** 不能因为归因错就否定结果。

#### 循环的三件套（讲师的拆法）

| 组件 | 它提供 |
| --- | --- |
| **tools** | **fresh information**（新鲜信息） |
| **check** | **verification**（验证） |
| **retry** | **correction**（纠正） |

> 三个词分别对应今天的三条主线：信息（RAG/工具）、**verified**（开场三级递进的第二级）、纠错（循环的意义）。
>
> **check 和 retry 必须成对**：检查了却不能改，等于只是知道自己错了。

#### ⭐ open-loop（开环）—— 控制论术语，用得很准

> *"The frontier model was **run open-loop**."*

| | 开环 open-loop | 闭环 closed-loop |
| --- | --- | --- |
| 反馈 | **无** | 有 |
| 行为 | 按预定序列执行，**不看结果** | 观察结果 → 调整下一步 |
| 例子 | 洗衣机定时器：转 30 分钟，不管洗没洗干净 | 恒温器：测温 → 决定开关 |

**一句判据**：**有没有从输出回到决策的那条边？** 没有 = 开环 = workflow；有 = 闭环 = agent。

> **注意精确性**：严格说 DAG 连"loop"都没有。但控制论的 *open loop* 不是指"有环但断了"，而是**信号路径没有合拢**——强调缺的是**反馈线**，不是缺个 while。
>
> → 所以：**写死的 while 循环有回边，但仍是开环，因为它不看结果。**

**可用的表述**：*"Open-loop is not agentic. Tools without feedback are open-loop automation, no matter how many steps you chain."*

#### ⭐ 最重要的两句：公平比较 + 工程判断

> **"Compare loops to loops and the gap mostly closes"**
> 拿循环去比循环，差距**基本就消失了**。

→ 即：**harness 的收益对大模型同样成立**。这场"胜利"不是模型层面的事实，是**对比设置不对称**造成的。

> **"but a loop around a cheap model is the better engineering."**
> **但把循环套在便宜模型上，是更好的工程。**

→ 这是**成本判断，不是能力判断**。两边都套上循环，前沿模型可能仍略胜；**但便宜模型 + 循环已经够用，且便宜得多。**

| 错误结论 | 正确结论 |
| --- | --- |
| 小模型更聪明 | **小模型有 harness，大模型只有 prompt** |
| 规模不重要了 | 规模仍重要，**但结构的边际收益更高** |
| 该换小模型 | **该先问：我的对比公平吗？** |

> **我的推理 vs 讲师答案的差距**（自查）：
> - ✅ 三件套、open-loop、"公平实验是给大模型同样的 harness"、check+retry 必须成对 —— 都对上了
> - ✅ 我补的成本账（7B 要跑五六次调用）→ 讲师用 *"better engineering"* 一词收进去了
> - ⚠️ 我说"大概率大模型还是赢"，讲师说的是 **"the gap mostly closes"**（差距基本消失）——**他的说法更弱也更准**，我多推了一步

#### 这道题的元设计

p.26 讲师刚说过 *"small models used agentically outperform much bigger models used directly"*，**四页之后就来考你会不会把它过度延伸**。

> → 呼应 ACT II 盲人摸象：**结论对不算数，说得出判据才算。** 而这次的"对"甚至是他自己的话——**他在教你怎么正确地引用他。**

### ACT III 小结

| 页 | 讲的是 | 一句话 |
| --- | --- | --- |
| p.26 | **为什么值得** | 结构的收益 > 规模的收益 |
| p.27 | **具体怎么做** | 五个特征动作（含隐喻锚点） |
| p.28 | **管道** | 工具解耦 / prompt 自动化 / 编排下沉 |
| p.29 | **专门化** | 定制阶梯 / 协作有了科学 / 环境型 agent |

> **结构**：先说值不值得 → 再说怎么做 → 最后说现在的条件（分基础设施和能力两层）。

---

### 与预期不一致处

- ~~我以为 Why Now 会讲技术使能因素~~ → **p.28 补上了**，而且组织得更好：不是列举"长上下文、tool use、降价"这类硬件式条件，而是讲**三层管道的成熟**（工具解耦 / prompt 自动化 / 编排下沉）。
- 真正的偏差是**顺序**：他把"有效性 + 类比 + 势头"（p.26）放在技术条件（p.28）**之前**。即先说"它有用"，再说"现在能用了"。

---

## ACT IV — The Loop & the Governor

> **副标题（p.32）**：*harness engineering — **why reliability lives in the loop, not the model***
>
> **配图：恒温器**（Nest，显示"IN 40 MIN → 74"）

**⭐ 扉页配图选得极准**：恒温器是**闭环控制的教科书例子**——测量 → 比较目标 → 动作 → 再测量。而且 "IN 40 MIN" 显示的是**它对自己何时到达目标的估计**，即**它在报告自己的进度**。

> 正好接上 p.31 的 open-loop：**洗衣机定时器是开环，恒温器是闭环。** 这一幕就是讲怎么把 agent 从前者变成后者。

**⭐ 副标题是全幕论点**：

> **reliability lives in the loop, not the model.**
> **可靠性住在循环里，不在模型里。**

→ 与 p.22 *harness gap*、p.31 *"a loop around a cheap model is the better engineering"* 同一条线，但这次讲的是**可靠性**而非**能力**。能力可以来自模型；**可靠性只能来自结构。**

---

### p.33 **The Provocation** —— 一个故意的稻草人

> *"Claude Code, Hermes, OpenClaw are mature. Write three `SKILL.md` files, wire three tools, done — **the harness will catch whatever goes wrong. It retries. It has hooks. It runs your tests. Won't it?**"*
>
> *"**Hold the question. We will answer it with a lamp, not an argument** — after lunch, on your own laptop."*

**这是讲师替听众说出的那个念头**：既然现成 harness 这么成熟，我写几个 skill 接几个工具不就完了？

**"Won't it?" 是反问**——答案显然是 **won't**。但他**不在这里论证**。

#### ⭐ "We will answer it with a lamp, not an argument"

**用一盏灯来回答，而不是用论证。**

| 层 | 含义 |
| --- | --- |
| 字面 | 下午你自己在笔记本上跑，**亲眼看见它出问题** |
| 方法论 | **演示 > 论证**。这是 *measured / verified* 的教学版：不说服你，让你自己观测 |
| 呼应 | **the lamp = 阿拉丁神灯**（p.9）—— 三词标题的最后一个词在这里回收 |

> **"lamp" 的双关**：既是"照明/让你看见"，也是 p.9 那盏神灯。而神灯的教训正是 ***delegation without verification*** ——
>
> → **"现成 harness 会兜住一切"本身就是一次无验证的委托。** 你把信任交给了一个你没验证过的东西。**下午的演示就是那次验证。**

#### 预测：下午会暴露什么

现成 harness 确实有 retry、hooks、跑测试。**但这些都是通用的**，它们兜不住：

| harness 会做的 | 兜不住的 |
| --- | --- |
| 报错了重试 | **没报错但答案是错的**（幻觉、编造的价格） |
| 跑你的测试 | **你没写的那条断言** |
| hook 拦破坏性命令 | **语义上不该做但语法合法的动作**（发了不该发的邮件） |
| 限制步数 | **在预算内静默松掉一个约束**（$200 夏威夷） |

> **核心**：通用 harness 管的是**执行的正确性**；**领域正确性**要你自己写。这正好是参考阅读里那条**棘轮纪律**——*每一行约束都要能追溯到一次具体失败*，所以它**必须由你的失败史长出来，下载不来**。

> **待验证**：下午的翻车点会落在上表哪一行？记下来对照。

---

### p.34 **The Body Knows** —— 站起来做三个实验

> # **No definitions yet. Stand up.**
>
> *Three experiments, fifteen minutes.*
> *Everything the engine will do this afternoon, **you are about to do with your own balance**.*

**⭐ 他要用身体教平衡控制。**

**"with your own balance"** —— **平衡**就是最直观的闭环控制：你站着不倒，靠的是内耳和本体感觉**持续测量身体倾斜 → 肌肉持续微调**。这个过程完全自动、每秒几十次、且你意识不到。

> **这就是 the governor 的活体演示**：不是"决定做什么"，而是**持续测量偏差并纠正**。

**教学法上的选择很讲究**：

| | |
| --- | --- |
| **"No definitions yet"** | 先有**身体经验**，再给定义。反过来就变成背术语 |
| **让人站起来** | 讲了一上午的抽象概念，物理上换个状态 —— 也是午饭前的节奏管理 |
| **"you are about to do"** | 不是看演示，是**自己成为那个系统** |

> ← 和 p.33 *"answer it with a lamp, not an argument"* 是同一个方法论：**先让你观测/体验，再给结论。** 这次的"lamp"是你自己的身体。

#### 三个实验（现场记录）

> 猜测方向：大概率会做**闭眼站立**（去掉视觉反馈 → 立刻晃）、**单脚站立**（缩小容错边界）、**转圈后站定**（破坏传感器 → 系统失稳）之类。每一个都对应一种 governor 失效。

| # | 实验 | 身体上发生了什么 | 对应到 agent |
| --- | --- | --- | --- |
| 1 | **闭眼站立**（双脚 / 单脚） | 肌肉没变，**但少了一个传感器** → 晃 | **同一个模型，少一路观测，结果就不同** |
| 2 | **登山杖平衡**（p.37）：杖尖朝下立在掌心，三种看法 —— 看杖顶 / 闭眼 / **看自己的手** | 看杖顶最稳；**看手最差** | **观测点选错，比不观测还糟** |
| 3 | **Warmer, colder**（p.39）：藏颂钵，三轮 —— ① 只说 warmer/colder ② **全场沉默** ③ **每第三次可以撒谎** | ①快 ②盲目乱走 ③**路径可能还能走到，但信心崩了** | ①好反馈 ②**无反馈** ③**被污染的反馈** |

---

#### ⭐ p.36 实验一收束：**Standing is a loop, not a state**

> *"A standing body is an **inverted pendulum**: you are **always falling**, and **a loop you never notice catches you many times a second** — on two legs as much as one. **Close the eyes and a sensor vanishes; the muscles did not change. Same muscles, two outcomes.**"*
>
> *"We walk at one and talk at two. **The loop came first** — and we never paid it any attention, **until the day it fails and we fall**. After lunch, the engine: **the model won't change; only the sensor will**."*

**⭐ 标题就是论点：站立是一个循环，不是一个状态。**

看起来"站着"是个静态的状态。实际上身体是**倒立摆**——重心在支点之上，**本质不稳定**。你**一直在倒**，只是有一个你从未察觉的循环**每秒接住你几十次**。

> **"you are always falling"** —— 这是最反直觉也最有用的一句。**稳定不是"没有偏差"，是"偏差被持续纠正"。**

#### 实验设计的精妙：唯一变量是传感器

> **"Same muscles, two outcomes."**（同样的肌肉，两种结果）

| 不变 | 变了 |
| --- | --- |
| 肌肉（**执行器 / 模型**） | 视觉（**一个传感器**） |

闭眼 → 少一路观测 → 晃。**能力一点没减，可靠性掉了。**

→ **这就是副标题 *"reliability lives in the loop, not the model"* 的实证。** 而且是在你自己身上做的实验，无法抵赖。

#### ⭐ 最重的一句伏笔

> **"After lunch, the engine: the model won't change; only the sensor will."**
> **下午的 engine：模型不会变，变的只是传感器。**

→ **下午的 lab 就是这个实验的软件版**：同一个模型、同一套 skill，**只改观测**（加/减 ledger、加/减验证、加/减工具返回），看结果怎么变。

> **这是第三个明确伏笔**，而且和前两个连上了：
> - p.13 **ledger vs driver**（下午）—— 账 vs 自述
> - p.33 **用一盏灯回答**（下午）—— 演示而非论证
> - p.36 **只改传感器**（下午）—— **控制变量法**
>
> 三条指向同一个下午实验：**固定模型，改变观测，测量可靠性。** 这是标准的受控实验设计 —— 呼应开场 *measured*。

#### ⭐ p.39 实验三：**Warmer, colder** —— 三种反馈质量

> 一名志愿者出去，藏好**颂钵**（singing bowl）。
> - **Round 1** —— 只用 **warmer / colder** 引导
> - **Round 2** —— 新志愿者，**全场沉默**
> - **Round 3** —— 新志愿者，**每第三次呼叫，全场可以撒谎**
>
> *Time each round. **Watch the third volunteer's confidence, not just their path.***

**三轮 = 三种反馈状态：**

| 轮次 | 反馈 | 控制论 | agent 对应 |
| --- | --- | --- | --- |
| 1 | **干净的标量梯度** | 闭环，无地图但收敛快 | 工具返回真实数据 |
| 2 | **无** | **开环** = 盲目搜索 | 不做任何验证 |
| 3 | **1/3 是假的** | **被污染的反馈** | **幻觉**——看起来可信但有时是错的 |

**⭐ Round 3 才是这个实验的重点，而且它对应的正是 LLM 的真实处境。**

#### 为什么"有时撒谎"比"完全沉默"更毒

**关键在"有时"。**

> **一个永远撒谎的传感器其实是好传感器——反过来读就行。** 真正的毒是**不可预测的不可靠**。

Round 3 的人**理论上仍能走到**（2/3 的信号是真的，多采样就能收敛）。但坏掉的不是路径，是**信心**：

- 每个信号都要打折，但不知道打几折
- 收到"colder"时不知道该退还是该进
- **最糟的一步**：开始整体不信反馈，退回自己的先验乱走 → **等于把 Round 3 变成 Round 2，但还浪费了时间**

> **→ 这就是为什么讲师说 "watch the confidence, not just the path"。**
> 路径可能还看得过去，**崩掉的是"敢不敢据此行动"**。而 agent 的整个价值就建立在"敢据此行动"上。

#### 与实验二的递进关系

| 实验 | 教训 |
| --- | --- |
| **二（登山杖）** | **坏传感器 > 没传感器的危害**——看手比闭眼还差 |
| **三（warmer/colder）** | **时好时坏的传感器最毒**——你连"该不信多少"都校准不了 |

→ 合起来：**传感器的可靠性比它的存在更重要。**

#### 对 agent 工程的三条直接推论

1. **幻觉的危害不是错误率本身，是它摧毁了对全部输出的信任。** 95% 正确的系统，如果你分不出哪 5% 错，实际可用性接近 0（在高风险场景下）。
2. **ledger 必须不可篡改。** 一个"有时记错"的 trace 比没有 trace 更糟——它会让你对所有记录失去判断力（Round 3）。
3. **宁可明确的"我不知道"，也不要不确定的答案。** 把"我做不到"做成合法动作（我在 Q2 笔记里写的那条），本质就是**把 Round 3 转成 Round 2** ——至少你知道自己没信号。

> **"Time each round"** —— 又一次 *measured*：三轮都计时，把体感变成数字。

#### "We walk at one and talk at two. The loop came first."

**一岁会走，两岁会说话。循环比语言先来。**

两层意思：

1. **进化/发育上**，控制循环比符号推理更古老、更基础 → 对应 agent：**loop 比 prompt 更基础**（p.21 *unit of engineering moved from the prompt to the loop*）
2. **"我们从未注意过它，直到有一天它失效、我们摔倒"** → **好的控制循环是隐形的**。你只在它坏掉时才知道它存在。

> ⚠️ **对工程的警告**：正因为循环隐形，**它最容易被忽略**。大家都在讨论模型（会说话的那部分），没人管循环（会走路的那部分）——**直到摔倒。**
>
> ← 正好回击 p.33 的稻草人：*"harness 会兜住的，不是吗？"* —— 你**从没检查过**它，因为它一直没坏。

---

### ⭐ p.41 **Watt's governor** —— governor 这个词的出处

> 栏目名：***Two centuries before the Transformer***（比 Transformer 早两个世纪）

> *"An engine under load slows; unloaded, it races. **Two iron balls on a spindle fly outward as it speeds** and, through a linkage, **close the throttle** — a machine that **senses its own output and corrects its own input**, trusted to run **unattended**."*
>
> *"**Every piece existed. Watt's genius was the integrator's.**"*

**离心调速器**（1788，瓦特用于蒸汽机）：

```
转速↑ → 铁球因离心力外张 → 通过连杆 → 关小节流阀 → 转速↓
转速↓ → 铁球下垂        → 通过连杆 → 开大节流阀 → 转速↑
```

**⭐ 定义级的一句：**

> **a machine that senses its own output and corrects its own input**
> **一台感知自己的输出、并据此修正自己输入的机器。**

← 这就是 p.24 那句 *"observe its own result and choose the next step"* 的**机械版本**。**同一个概念，早了两百年。**

#### ⭐ "trusted to run unattended" —— 这才是关键词

**调速器的价值不是"转得更快"，是"没人看着也能信任它"。**

| | |
| --- | --- |
| 没有调速器 | 必须有人盯着，随时手动调节流阀 |
| 有调速器 | **可以走开** |

→ **governor 是"无人值守"的前提条件。** 这正好回答了全天的主题：
- p.19 定义：autonomy = *without a human turning the crank*
- **p.41**：而**你敢让它自己转，是因为有调速器**

> **自主性不是靠信任换来的，是靠约束换来的。** 你能放手，恰恰因为装了那个限制它的东西。

#### ⭐ "Every piece existed. Watt's genius was the integrator's."

**每个零件都已经存在。瓦特的天才是整合者的天才。**

离心机构、连杆、节流阀，在 1788 年都不是新东西。**瓦特做的是把它们接成一个环。**

> **← 这句直接打在今天的处境上**：
> 模型、工具、MCP、skill、hooks、trace —— **零件全都现成了**。今天缺的不是零件，是**把它们接成一个可信循环的整合工作**。
>
> **这就是 harness engineering 的定位**：不是发明新东西，是**做整合者**。
>
> → 也回收了 p.33 的稻草人：*"写三个 SKILL.md 接三个工具就完了，不是吗？"* —— **零件摆在那不等于机器。瓦特的天才在连杆上，不在铁球上。**

#### 栏目名的用意：*Two centuries before the Transformer*

把 governor 放在 Transformer 之前两个世纪，是在说：

> **控制论的问题比深度学习的问题古老得多，而且已经被解决过一次。**

← 呼应 ACT I 的 *"the field's oldest failure catalog"*：神话给的是失败清单，**瓦特给的是解法原型**。

---

### ⭐ p.42 **Kybernetes — the steersman**（舵手）

> *"**Harness** comes from **tack and bridle** — the control of an animal — **and I dislike it for that**. The field's older word is kinder: **kybernetes**, the helmsman, root of both **governor** and **cybernetics**. **The sea does not obey him; he reads it and corrects.**"*
>
> ⭐ ***"We are not breaking a horse. We are learning to steer."***

**讲师在这里推翻了自己用了一上午的词。**

| 词 | 词源 | 隐含的关系 |
| --- | --- | --- |
| **harness** | 马具、缰绳 —— **驯服动物** | **压制**：对方有意志，我要制服它 |
| **kybernetes**（希腊语 κυβερνήτης） | **舵手** | **导引**：对方（海）无意志，我读它、顺它、修正 |

**词源链**：kybernetes → 拉丁语 gubernator → **governor**；同时也是 **cybernetics**（控制论）的词根。

> **所以 the governor 这个词，本义就是"舵手"。** ACT IV 的标题 *The Loop & the Governor* = **循环与舵手**。

#### ⭐ "The sea does not obey him; he reads it and corrects."

**海不听他的；他读海，然后修正。**

这是全天关于人机关系最准的一句：

- **舵手无法命令海** —— 你也无法命令模型按你想的方式思考
- **但舵手能读海** —— 观测、trace、ledger
- **并据此修正** —— 调整航向、设闸、停机

→ **放弃"控制模型内部"，转而"读取并修正"。** 这正是我之前说的"没法把 LLM 拆开，但可以在外面搭一个可拆的结构"——**讲师给了它一个更好的名字。**

#### ⭐ "We are not breaking a horse. We are learning to steer."

**我们不是在驯马，我们是在学掌舵。**

两个动词的对象都变了：

| | 驯马 | 掌舵 |
| --- | --- | --- |
| 对象 | **马**（改造它） | **自己的技艺**（learning to **steer**） |
| 前提 | 它会反抗 | 它不反抗，也不服从——**它只是有它的动力学** |
| 失败时 | 马赢了 | **你读错了海** |

> ⚠️ **注意最后一行**：这个隐喻把责任放回**操作者**身上。船翻了不怪海。
> ← 接上 ACT I 偃师那层（出事被追责的是工匠）和泥人（*the maker forgets the second*）。**三次了，讲师一直在把责任指向造物者。**

#### 这一页在全幕中的位置

p.41 给了 governor 的**机械原型**（瓦特），p.42 给它的**语义根**（舵手）。两页合起来：

> **governor = 一个读取输出并修正输入的机构；它的本质不是压制，是导引。**

> **我的修正**：我之前把 harness 译作"外壳"并建议不译。讲师这里说他**不喜欢 harness 这个词**（因为它是马具）。
> → 如果要中译，**"舵"这一系的词（掌舵、舵手、导航）比"驾驭/约束"更贴他的本意。**
> → 但注意：**术语仍然用 harness**（行业既定），他只是在哲学上做了区分。

---

### ⭐⭐ p.43 **No fixed p survives a long horizon** —— 开环的算术

> 栏目：*The open loop's arithmetic*

> *"Ten steps at p = 0.9 each, no checks: 0.9¹⁰ ≈ 0.35. A hundred steps at p = 0.99: ≈ 0.37. **A million steps at p = 0.9999: ≈ 0.** **Open-loop scaling is hopeless at every quality level — buying nines does not buy horizon.**"*
>
> *"Yet in 2026 a harnessed agent ran **over a million steps with zero errors**. **Nothing in the model improved. The loop did.**"*

#### 算术（已用 Python 复核 ✅）

| 步数 n | 单步成功率 p | pⁿ |
| --- | --- | --- |
| 10 | 0.9 | **0.3487** |
| 100 | 0.99 | **0.3660** |
| 1,000,000 | 0.9999 | **3.7 × 10⁻⁴⁴** ≈ 0 |

**⭐ 注意前两行：把可靠性从 90% 提到 99%（错误率降到 1/10），换来的只是步数从 10 涨到 100 ——而成功率还是 ~0.35。**

> 数学上：pⁿ ≈ e^(−n(1−p))。要维持同样的总成功率，**n 只能和 1/(1−p) 成正比**。
> **多买一个 9 = 多买 10 倍步数。** 但你要的 horizon 往往是 1000 倍、100 万倍。

**⭐ "Buying nines does not buy horizon."**
**买更多的 9，买不到长度。**

第三行是致命一击：**即使 p = 0.9999（万分之一的错误率，已经远超任何现有模型），一百万步之后成功率是 10⁻⁴⁴。** 这不是"比较低"，这是**零**。

#### 为什么这一页是全天最硬的论证

前面所有论点（harness gap、结构 > 规模、reliability lives in the loop）**都还可以被解读为经验观察**。这一页把它变成了**数学必然**：

> **只要没有检查点，长任务的成功率就必然趋近于零——与模型多好无关。**

→ **"等下一代模型"这条路被算术堵死了。** 你不可能靠提高 p 来获得 horizon，因为指数衰减比你能买到的 9 快得多。

#### ⭐ 反转：闭环打破了这个算术

> *"Yet in 2026 a harnessed agent ran **over a million steps with zero errors**."*

**怎么可能？** 因为 pⁿ 这个公式的前提是 **"no checks"（开环）**。

| | 开环 | 闭环 |
| --- | --- | --- |
| 错误 | **累积** | **被发现并纠正** |
| 数学 | pⁿ 指数衰减 | **每个检查点把误差清零** |
| 类比 | 一直倒下去 | **每秒被接住几十次**（p.36 站立） |

> **闭环不是让 p 变大，是让 n 重新开始。** 检查点把"一百万步"切成一百万个"一步"。
>
> ← 这就是 p.36 倒立摆的数学版：**你一直在倒（p < 1），但循环每秒接住你几十次（检查点），所以你能站一整天。**

**⭐ 落点那句：**

> **"Nothing in the model improved. The loop did."**
> **模型没有任何改进。改进的是循环。**

← 与 p.22 *"not one weight changed"*（Top-30 → Top-5）是同一句话的两个版本。**一个讲能力，一个讲可靠性。**

#### 可直接带走的三条

1. **任何没有检查点的多步流程，都在跑 pⁿ。** 算一下你的 n 和 p，答案通常很难看。
2. **检查点的价值 = 把 n 重置。** 所以检查点该放在**误差会被放大**的地方（p.37 杖顶），且必须**可信**（p.39 Round 3）。
3. **horizon（能跑多远）不是模型属性，是 harness 属性。**

> ⚠️ **待核实**：*"a harnessed agent ran over a million steps with zero errors"* —— 具体指哪个系统 / 哪份报告？记入待办。

---

### ⭐ p.44 **TCP over IP** —— 软件人的类比

> 栏目：*The software-native analogy*

> *"The internet's wire is **unreliable**: packets drop, arrive twice, arrive out of order. **Nobody fixed the wire.** TCP wrapped it in a **closed loop** — **acknowledge, time out, retransmit** — and unreliable IP became a medium you could **run a bank on**."*
>
> ⭐ *"**Reliability is built on top of a fallible layer, never into it.** A **harness** is to an **LLM** what **TCP** is to **IP**."*

**这是给工程师的那个版本**（前面是身体、是蒸汽机，这次是他们每天在用的东西）。

#### 对照表

| | IP | LLM |
| --- | --- | --- |
| 本质 | **不可靠**：丢包、重复、乱序 | **不可靠**：幻觉、遗漏、不一致 |
| 修不修得好 | **没人去修那根线** | 修不了（不可拆、不可解释） |
| 上面加什么 | **TCP**：确认 / 超时 / 重传 | **harness**：验证 / 预算 / 重试 |
| 结果 | 可以**跑银行**的介质 | 可以托付真实工作的系统 |

#### ⭐ "Nobody fixed the wire."

**没人去修那根线。**

这句话是对"等下一代模型"的第三次、也是最彻底的一次反驳：

- p.22：**harness gap** —— 你看到的差距是 harness 的差距（经验）
- p.43：**pⁿ** —— 靠提高 p 拿不到 horizon（数学）
- **p.44**：**根本不该往下修** —— 这是**架构原则**（工程史）

> 互联网没有等一根完美的线。**它假设线永远不完美，然后在上面建了一层会纠错的协议。**

#### ⭐ 全天最可移植的一句

> **"Reliability is built on top of a fallible layer, never into it."**
> **可靠性是建在易错层之上的，绝不是建进它里面的。**

这句话的适用范围远超 agent —— 它是分布式系统、存储、硬件容错的通用原则：
- 磁盘会坏 → RAID 建在上面
- 机器会宕 → 副本和共识建在上面
- 内存会翻位 → ECC 建在上面
- **模型会幻觉 → harness 建在上面**

> **→ 所以"幻觉是模型的缺陷，等它修好"这个想法在架构上就是错的。** 丢包不是 IP 的缺陷，是它的**设计前提**。幻觉也一样：**把它当成需要被包裹的既定属性，而不是等待被消除的 bug。**

#### TCP 的三个机制 ↔ harness

| TCP | 作用 | harness 对应 |
| --- | --- | --- |
| **acknowledge**（确认） | 确认对方**真的收到了** | **验证**：ledger、引用核查、测试 |
| **time out**（超时） | 等太久就认定失败 | **预算 / governor**：步数、时间、花费上限 |
| **retransmit**（重传） | 失败就重来 | **retry**（p.31 三件套的第三件） |

> ⭐ **注意 acknowledge 的性质**：TCP 不是"发出去就算数"，而是**要求接收方回一个确认**。这正是 p.13 的 ledger ——**不采信发送方的自述，要独立的回执。**
>
> 而 p.31 的三件套（tools / check / retry）在这里得到了协议级的印证：**check ↔ acknowledge，retry ↔ retransmit。**

#### 一个可以在课上问的延伸

TCP 之所以能工作，还有一个前提：**接收方能判断包对不对**（校验和）。

→ **agent 的"校验和"是什么？** 对代码是测试，对数学是重算，**但对 newsletter 这种自然语言输出呢？** 这正是下午要面对的——**"可验证性"不是免费的，它取决于任务形态。**

---

### ⭐⭐ p.45 **Tomcat does not read your HTML** —— harness 的边界

> 栏目：*The container contract*（容器契约）

> *"The servlet container guarantees your servlet **is called**, its exceptions **logged**, a **500 sent** when you throw. It has **no opinion about whether the page was right**. A harness is the same contract: **exit codes, schemas, timeouts, iteration caps — the signals it can see without knowing your domain**."*
>
> ⭐ *"The container validates **HTTP**. **You** validate the **business logic**. **Correctness is domain knowledge, and only you have it.**"*

**⭐ 这一页回答了 p.33 的稻草人 —— 而且是用画边界的方式，不是用反驳。**

#### 契约：harness 保证什么 / 不保证什么

| ✅ harness **能**做（不需要懂你的领域） | ❌ harness **不能**做（需要领域知识） |
| --- | --- |
| **exit codes** —— 进程挂没挂 | 结果**对不对** |
| **schemas** —— 格式合不合法 | 内容**真不真** |
| **timeouts** —— 跑太久了 | 跑的**方向对不对** |
| **iteration caps** —— 步数到顶 | 该不该**在这一步停** |
| 抛异常 → 记日志 → 返回 500 | 页面**该不该长这样** |

> **判据一句话**：**harness 只能看见"不需要知道你的业务就能判断"的信号。**

#### ⭐ "Correctness is domain knowledge, and only you have it."

**正确性是领域知识，而且只有你有。**

这是全天关于**责任划分**最清楚的一句。它同时否定两种幻想：

| 幻想 | 为什么错 |
| --- | --- |
| "现成 harness 会兜住"（p.33） | 它只能兜住**语法级**失败，兜不住**语义级**错误 |
| "模型足够强就不用我管" | **正确性的定义在你手里**，模型无从知道 |

> ← 完美对上我在 p.33 那里预判的表格（**执行正确性 vs 领域正确性**）。讲师用 Tomcat 给了它一个更好的名字：**容器契约**。

#### 和 p.44 TCP 的关系：这是同一个分层原则的第二面

| | p.44 TCP | p.45 Tomcat |
| --- | --- | --- |
| 讲的是 | **可靠性要建在上层** | **上层也有它管不到的东西** |
| 一句话 | 别去修那根线 | **别指望那层懂你的业务** |

> **两页合起来是完整的分层观**：
> **每一层只解决它那一层的问题。** TCP 解决传输可靠，**不保证你发的内容有意义**；Tomcat 保证 servlet 被调用，**不保证页面对**；harness 保证循环跑得住，**不保证答案对**。
>
> **→ 所以"正确性"永远没有下层可以推卸。**

#### 对下午 lab 的直接推论

| 谁来管 | 什么 |
| --- | --- |
| **现成 harness** | agent 没崩、没超时、没跑飞、输出是合法 JSON |
| **你必须自己写** | 引用能核回原文、数字没被编造、**这条新闻真的属于本周** |

> **这就是"newsletter 不能被单独信任去写"的准确含义**：不是 harness 不够好，而是 **newsletter 的正确性标准只存在于你脑子里**，你不把它写成检查，就没有人会检查。
>
> ← 也解释了参考阅读里那条**棘轮纪律**为什么是"下载不来"的：**领域正确性天然是你的私有知识。**

#### 一个可以问的问题

> **如果 correctness 只有我有，那 evaluator agent 的正确性从哪来？**
>
> （参考阅读说 generator/evaluator 要分离，因为自评偏乐观。但 evaluator 也是个模型——它的判断标准同样来自你写的 rubric。**所以 evaluator 不是"引入了正确性"，只是"把你的标准执行了一遍"。**）

---

### ⭐⭐ p.46 **What a harness is: seven verbs** —— harness 的正式定义

> 栏目：*Definition · The object itself*（定义 · 这个对象本身）

> *"**The runtime that owns the agent loop.** Every turn it **assembles** the context · **dispatches** the tool calls · **enforces** the budgets · **persists** the state · **verifies** claimed progress · **stops** the loop · **escalates** to a human."*
>
> ⭐ *"**The model owns exactly one step — inference.** Safety, cost, durability, trust **all live in the verbs, not in the model**."*

**⭐ 一句话定义：harness = 拥有 agent 循环的那个运行时（the runtime that owns the agent loop）。**

**"owns" 这个词是关键** —— 循环不属于模型，**属于 harness**。这是 *"谋事在模型，成事在 harness"* 的正式版。

#### 七个动词（每轮都发生）

| # | 动词 | 做什么 | 对应今天的哪一页 |
| --- | --- | --- | --- |
| 1 | **assembles** the context | 组装上下文 | p.21 *what it is shown*；progressive disclosure |
| 2 | **dispatches** the tool calls | 派发工具调用 | p.21 *what it may do*；p.27 sensors/actuators |
| 3 | **enforces** the budgets | 强制预算 | p.41 瓦特调速器；p.44 TCP timeout |
| 4 | **persists** the state | 持久化状态 | p.27 memory；ledger 的载体 |
| 5 | **verifies** claimed progress | **核实所声称的进度** | ⭐ p.13 ledger vs driver |
| 6 | **stops** the loop | 停止循环 | p.10 泥人的 kill switch |
| 7 | **escalates** to a human | 上报给人 | p.31 不可逆动作前的闸门 |

**⭐ 第 5 个动词的措辞极准：*verifies **claimed** progress*（核实**所声称的**进度）。**

> **"claimed"** 这个词把 p.13 整页压进了一个形容词里：**进度是 agent"声称"的，不是事实。harness 的职责是去核实。**
>
> ← driver 说的 vs ledger 记的。**不采信自述。**

#### ⭐ 落点：*"The model owns exactly one step — inference."*

**模型只拥有一个步骤：推理。**

| | 归谁 |
| --- | --- |
| **inference**（一次前向推理） | **模型** |
| 其余七个动词 | **harness** |

> **"Safety, cost, durability, trust all live in the verbs, not in the model."**
> **安全、成本、持久性、信任，全都活在这些动词里，不在模型里。**

四个名词恰好对应四个动词：

| 属性 | 由哪个动词保证 |
| --- | --- |
| **safety**（安全） | stops / escalates |
| **cost**（成本） | enforces budgets |
| **durability**（持久） | persists |
| **trust**（信任） | verifies |

→ **这四样都不是模型能力问题，是 harness 设计问题。** 换更强的模型，这四样一个都不会自动变好。

#### 这一页在 ACT IV 中的位置

前面五页是**铺垫**，这页是**收束**：

| 页 | 给了什么 |
| --- | --- |
| p.36–39 | 身体实验 —— **闭环的直觉** |
| p.41 | 瓦特 —— **机械原型**（senses output, corrects input） |
| p.42 | kybernetes —— **语义根**（读它、修正它） |
| p.43 | pⁿ —— **数学必然**（开环必死） |
| p.44 | TCP —— **架构原则**（可靠性建在上层） |
| p.45 | Tomcat —— **边界**（正确性是你的领域知识） |
| **p.46** | **⭐ 定义**：七个动词 |

> **从直觉 → 原型 → 词源 → 数学 → 架构 → 边界 → 定义。** 定义放在最后，因为前面每一页都在为它挣一条依据。
>
> ← 和 ACT II 同一手法：**p.16 "cacophony of definitions — and the one that survives"**，先铺垫再给定义。

#### ⭐ 实用：把七个动词当检查表

设计或审查一个 agent 系统时逐条问：

- [ ] **assembles** —— 每轮给它看什么？谁决定？有没有按需加载？
- [ ] **dispatches** —— 允许调哪些工具？sensors 和 actuators 分开了吗？
- [ ] **enforces** —— 预算是什么（步数/token/时间/钱）？到顶了怎么办？
- [ ] **persists** —— 状态存哪？崩了能恢复吗？
- [ ] **verifies** —— **谁来核实它说的进度？核实的信号从哪来？**
- [ ] **stops** —— 停止条件有哪些？停机键比启动更容易按吗？
- [ ] **escalates** —— 什么情况必须找人？不可逆动作前有闸吗？

> **缺哪一条，就知道你的 harness 缺在哪。**

---

### ⭐⭐ p.48 **The bottleneck is the verifier**

> 栏目：***Of the seven, the one that binds***（七个动词里，**约束性的那一个**）

> *"A loop running unattended is a loop **making mistakes unattended**: **"done" is a claim, not a proof.** Anthropic's long-running agents failed **not by incompetence but by premature victory** — declaring projects finished **on a glance**. **The fix was never a smarter model.**"*
>
> ⭐ *"A loop **amplifies whatever certifies its work**. A better model, a cleverer prompt — **each raises the stakes without raising the floor**. **You may run your loop only as far as your verifier deserves to be trusted.**"*

**七个动词里，*verifies* 是那个"卡住其余一切"的（the one that binds）。**

#### ⭐ "'done' is a claim, not a proof."

**"完成了"是一个声称，不是一个证明。**

← 与 p.46 *verifies **claimed** progress* 同一个词。也与 p.13 ledger vs driver 同一件事。

**三次了，讲师在用三种措辞说同一条**：不要采信执行者对自己的陈述。

#### ⭐ **premature victory**（过早宣告胜利）—— 失败模式有名字了

> Anthropic 的长周期 agent **不是因为无能而失败，是因为过早宣告胜利** —— *declaring projects finished **on a glance***（**扫一眼就宣布项目完成**）。

| 你以为的失败 | 实际的失败 |
| --- | --- |
| 它做不到 | **它以为自己做到了** |
| 能力不足 | **判据不足** |
| → 换更强的模型 | → **写更严的验证** |

> **"The fix was never a smarter model."** 修法从来不是更聪明的模型。
>
> ← 这是今天第四次反驳"等下一代模型"，而且这次给的是**失败模式的具体形态**：更聪明的模型只会**更自信地**宣布完成。

> ⚠️ 对照参考阅读：*"agents reliably **skew positive** when grading their own work."*（自评偏乐观）—— **premature victory 就是这条的长周期版本。**

#### ⭐⭐ 全天最重的一句

> **"A loop amplifies whatever certifies its work."**
> **循环会放大任何为它的工作背书的东西。**

**这是 p.43 pⁿ 算术的反面：**

| | 开环 | 闭环 |
| --- | --- | --- |
| 被放大的 | 错误（pⁿ 衰减） | **verifier 本身** |

- verifier 严 → 循环把"严"放大一百万次 → 一百万步零错误（p.43）
- **verifier 松 → 循环把"松"也放大一百万次** → 一百万步的垃圾，而且每一步都盖了章

> **循环是一个放大器，不是一个过滤器。** 它不会自动变好，它只会把你给它的判据**执行到底**。
>
> ← 呼应 p.39 Round 3：**被污染的反馈**在长 horizon 下不是"有点噪声"，是**系统性地把错误固化成"已验证"**。

#### ⭐ "each raises the stakes without raising the floor"

> 更好的模型、更巧的提示 —— **每一样都在抬高赌注，却没有抬高地板。**

| | 效果 |
| --- | --- |
| 更强模型 / 更好提示 | 让它**跑得更远、做得更多** → **赌注变大** |
| **但 verifier 没变** | **地板（下限保障）没动** |

→ **能力提升 + 验证不变 = 风险净增加。** 这是全天最反直觉、也最该记住的一条工程判断：

> **在没有相应提升 verifier 之前，提升 agent 的能力是在提高风险敞口。**

#### ⭐ 落点：可跑多远的上限

> **"You may run your loop only as far as your verifier deserves to be trusted."**
> **你的循环能跑多远，取决于你的 verifier 配得上多少信任。**

**这是 horizon 的真正上限公式。** 和 p.43 合起来：

| p.43 | 没有检查点 → horizon ≈ 0 |
| **p.48** | **有检查点 → horizon ≤ verifier 的可信度** |

> **→ 自主性的上限不是模型能力，是验证能力。**
>
> 与 p.41 瓦特那句 *trusted to run **unattended*** 闭合：**你敢让它无人值守跑多久，取决于那个调速器有多可靠。**

#### 实用推论

1. **要放长 horizon，先问"我的 verifier 有多强"**，而不是"模型够不够聪明"。
2. **verifier 的强度决定了你能给多少自主权** —— 两者必须同步提升。
3. **"done" 必须有独立判据**：测试通过、引用可核、数字能重算。没有判据的"完成"等于没完成。
4. **警惕 premature victory**：长任务里，agent 最可能的失败不是卡住，是**假装做完了**。

> **课上可问**：newsletter 这类自然语言输出，verifier 怎么写？（接 p.44 那个"agent 的校验和是什么"）

---

### ⭐ p.52 **Hunting** —— governor 的失灵模式

> 栏目：***The governor, misbehaving***（调速器失灵）

> *"A hotel shower with a slow valve: too cold, you yank it hot, too hot, you yank it cold — and you **oscillate forever**. **Sensor fine, actuator fine, latency wrong**; you **overcorrect on stale evidence**. **Maxwell wrote the founding paper of control theory in 1868** to explain exactly this in Watt's governors."*
>
> ⭐ *"An agent that retries on **stale or lying feedback** does not idle — **it hunts**. **The quality of the sensing, not the power of the actuator, sets the ceiling.**"*

**术语**：**hunting（振荡/寻的）** —— 控制系统在目标值两侧来回摆动、不收敛。

#### ⭐ 关键诊断：三个部件都没坏，坏的是**时序**

> **"Sensor fine, actuator fine, latency wrong."**

**酒店淋浴**：阀门响应慢 → 你根据**几秒前的水温**做调整 → 调过头 → 再反向调过头 → **永远振荡**。

| 部件 | 状态 |
| --- | --- |
| 传感器（你的皮肤） | ✅ 正常 |
| 执行器（你的手） | ✅ 正常 |
| **延迟** | ❌ **反馈滞后于动作** |

> **⭐ 这是全天第一次出现"部件都好但系统坏了"的失败模式。**
>
> ← 对比 p.8 偃师：抽掉一个器官坏一个功能（**部件级归因**）。**而 hunting 是系统级失效——每个部件单独测都是好的。**
>
> → 所以 ledger 光记"每一步做了什么"不够，还得记**时序**：什么时候观测的、观测的是多久以前的状态。

#### ⭐ "overcorrect on stale evidence"（基于过时证据的过度修正）

**这正好接上 p.37 登山杖的"滞后"那一层**——当时说"看手是滞后信号，容易过冲"，这里给出了它的名字和后果。

**agent 里的 hunting 长什么样：**

| 场景 | 振荡表现 |
| --- | --- |
| 搜索结果不理想 → 改关键词 → 又不理想 → 改回去 | **在两个查询之间来回** |
| 改代码 → 测试红 → 改回来 → 又红 → 再改过去 | **在两个版本之间来回** |
| 工具超时 → 重试 → 又超时 → 再重试 | **无意义重试，且可能加重下游负载** |
| 检查发现不合格 → 重写 → 新版本又触发另一条检查 | **在两条规则之间打转** |

> **注意**：这些**在日志里看起来像"在努力工作"**——每一步都有动作、有产出。**这是最难发现的失败**，因为它不报错，也不卡住。
>
> → 这就是我之前整理的「停滞检测」为什么要看**重复模式**而不是看"有没有在动"。

#### Maxwell 1868 —— 控制论的起点

> 麦克斯韦 1868 年写下控制理论的**奠基论文**（*On Governors*），**就是为了解释瓦特调速器上的这个现象**。

**历史线**：
- 1788 瓦特造出调速器（p.41）→ 能用，但有时会振荡
- **1868 麦克斯韦用数学解释了为什么**（稳定性分析）
- 中间隔了 **80 年** —— **"能造出来"和"能分析它什么时候会失稳"之间差了八十年**

> ⚠️ **这是给今天的一个尖锐类比**：我们现在处在**1788 到 1868 之间**——agent 造得出来，但**还没有一套稳定性理论**告诉你什么条件下这个循环会发散。
>
> ← 呼应 p.29 *"first controlled studies"*（第一批受控研究）。**这门科学还在早期。**

#### ⭐⭐ 落点：天花板由传感决定

> **"The quality of the sensing, not the power of the actuator, sets the ceiling."**
> **设定天花板的是感知的质量，不是执行器的力量。**

**这是今天所有"XX 决定上限"里最根本的一条**，把前面几条都串了起来：

| 页 | 说的是 |
| --- | --- |
| p.37 登山杖 | 观测**点**选错 → 比不观测还糟 |
| p.39 warmer/colder | 观测**可靠性**坏掉 → 信心崩塌 |
| p.48 verifier | 验证**可信度**决定 horizon |
| **p.52** | **感知质量决定天花板；执行器力量不决定** |

> **"执行器的力量" = 模型能力。** 所以这句话又是一次"别指望更强的模型"——**但这次的理由是控制论的：在反馈质量不变的前提下，加大执行力度只会让振荡更剧烈。**
>
> ← 与 p.48 *"raises the stakes without raising the floor"* 完全同构：**更强的执行器 + 不变的感知 = 更快地跑偏。**

#### 实用推论

1. **agent 打转时，先查反馈延迟和新鲜度，别先怪模型。**
2. **重试要有退避和上限**，且重试前应**重新观测**（不要基于旧证据重试）。
3. **振荡检测**应该是 governor 的一条硬规则：检测到 A→B→A→B 模式就停机上报，而不是等预算耗尽。
4. **ledger 要记时间戳**：观测发生在什么时候、证据有多旧。

---

### The loop：由哪几步组成

1. 
2. 

**它凭什么继续、凭什么停？**

- 

### ⭐⭐ p.53 **Four stop rules, before the first run** —— 必须接的四个 governor

> 栏目：***The governors you must wire***（你必须接上的那些调速器）
> 标题里的 **before the first run** 是命令式：**在第一次运行之前就要接好**，不是出事后再补。

| 停止规则 | 触发条件 | 实现 |
| --- | --- | --- |
| **Success**（成功） | **the verifier says done** | ⭐ ***the only happy exit***（唯一的正常出口） |
| **Insolvency**（破产） | the budget is spent | tokens、dollars、wall-clock |
| **Futility**（徒劳） | **no progress in k turns** | ⭐ ***the hunting detector***（振荡检测器） |
| **Deference**（让位） | **a human must decide** | approval gates |

> ⭐ **"A loop without exits is not autonomous. It is unattended."**
> **没有出口的循环不是自主的，只是无人看管的。**

#### ⭐ 这一页把 ACT IV 全部收口了

**四条规则，每条都由前面某一页挣来：**

| 规则 | 出处 |
| --- | --- |
| Success —— 由 **verifier** 判定 | **p.48**：*"done" is a claim, not a proof* |
| Insolvency —— 预算耗尽 | **p.43** pⁿ 算术；**p.44** TCP timeout |
| Futility —— **hunting detector** | **p.52** 振荡：不 idle，会一直动 |
| Deference —— 人来决定 | **p.46** escalates；不可逆动作的闸 |

#### ⭐ 三个措辞值得单独记

**① "the only happy exit"（唯一的正常出口）**

四个出口里**只有一个是"好"的**，其余三个都是**止损**。

> **→ 设计时的心态转换**：不要只想着"成功路径"。**四分之三的出口是失败出口，它们必须被同等认真地设计。**
>
> 而且注意：**Success 是由 verifier 判定的，不是由 agent 声称的。** 如果你没有 verifier，**你其实一个正常出口都没有**——那个"完成了"只是 claim。

**② "the hunting detector"（振荡检测器）**

Futility 不叫 "timeout" 也不叫 "stuck"，**直接叫振荡检测器** —— 因为 p.52 说过：**坏掉的 agent 不会闲着，它会一直动。**

> **判据是 "no progress in k turns"，不是 "no action in k turns"。**
> → 关键在于你**怎么定义 progress**。这又绕回 verifier：**没有可测量的进度定义，Futility 规则就写不出来。**

**③ "Deference"（让位）而不是 "human in the loop"**

用词很讲究：**deference = 恭敬地让出决定权**。不是"人来兜底"，是**有些决定本来就不该由它做**。

> ← 接 p.45 *"Correctness is domain knowledge, and only you have it."*
> 有些判断**不是它做不好，是它没有做的资格**。

#### ⭐⭐ 落点：autonomous vs unattended

> **"A loop without exits is not autonomous. It is unattended."**

**这是全天对"自主"最精确的一次界定，而且是个反转：**

| | 有出口 | 没出口 |
| --- | --- | --- |
| 英文 | **autonomous**（自主） | **unattended**（无人看管） |
| 含义 | 它知道**何时该停** | 它只是**没人管** |
| 类比 | 恒温器 | 卡住的油门 |

> **← 与 p.41 瓦特那句形成完整的一对：**
> - p.41：*trusted to run **unattended*** —— 有了调速器，**才敢**无人值守
> - **p.53**：没有出口的循环，**只是**无人值守 —— **而这不是自主，是失控**
>
> **同一个词，两种含义**：p.41 的 unattended 是"可以走开"的结果；p.53 的 unattended 是"没人在管"的状态。**调速器就是把后者变成前者的东西。**

> **自主 ≠ 不受约束。自主 = 自己知道边界在哪。**

#### ✅ 直接可用的实现检查表

```
STOP RULES（第一次运行前就要有）
├─ Success    : verifier 判定 done —— 判据是什么？谁写的？
├─ Insolvency : token / 美元 / 墙钟，三个都要有上限
├─ Futility   : k 轮无进度 → 停。"进度"怎么量？k 取多少？
└─ Deference  : 哪些动作必须人批？（不可逆动作清单）
```

> **缺任何一条，这个 agent 就不该上线。**

> 「调速器」在 Week 12（语义缓存，ACT II）出现过，指用 γ/τ 控制决策松紧。**今天确认：同一套直觉在 agent 层的复用 —— 都是"什么时候该停/该放行"的阈值设计。**

### ⭐⭐ p.54 **The verifier's arithmetic** —— 算术的另一个方向

> 栏目：***The two directions of the arithmetic***（算术的两个方向）

> *"A **35% generator** behind a **reliable gate** with **four retries** ships north of 80%: **1 − 0.65⁵ ≈ 0.88**. **The exponent that killed the open loop now works for you.** But a **false-positive verifier is worse than none** — **it manufactures gospel, and every later step builds on it**."*
>
> ⭐ *"The fatal move is **a wrong belief entering the record with no path back**. **Design the loop so it can reach back and un-believe.**"*

#### 算术（已复核 ✅）

**开环（p.43）**：pⁿ —— 指数**碾碎**你
**闭环（p.54）**：1 − (1−p)ⁿ —— 指数**替你干活**

| 尝试次数 | 1 − 0.65ⁿ |
| --- | --- |
| 1 | 0.35 |
| 2 | 0.578 |
| 3 | 0.725 |
| 4 | 0.822 |
| **5** | **0.884** |
| 6 | 0.925 |

> **一个只有 35% 成功率的生成器，配上可靠的闸门 + 四次重试，交付率超过 88%。**

**⭐ "The exponent that killed the open loop now works for you."**
**那个杀死开环的指数，现在替你干活了。**

| | 公式 | 指数作用于 |
| --- | --- | --- |
| **开环**（p.43） | pⁿ → 0 | **成功**被连乘，衰减 |
| **闭环**（p.54） | 1 − (1−p)ⁿ → 1 | **失败**被连乘，衰减 |

> **同一个指数，方向取决于有没有闸门。** 这就是栏目名 *"the two directions of the arithmetic"*。
>
> **→ 闸门的作用不是提高 p，是把"连乘成功"变成"连乘失败"。**

#### ⭐⭐ 但有个致命前提：闸门必须可靠

> **"A false-positive verifier is worse than none — it manufactures gospel, and every later step builds on it."**
> **一个会误判通过的 verifier 比没有更糟 —— 它在制造教条，而后续每一步都建立在它之上。**

**false positive = 错的东西被判为"通过"。**

| verifier 的错误类型 | 后果 |
| --- | --- |
| **false negative**（对的被判错） | 浪费一次重试 —— **代价线性，可接受** |
| **false positive**（错的被判对） | ⭐ **错误被盖章、进入记录、后续全部建立其上** —— **代价是灾难性的** |

> **"manufactures gospel"（制造教条）** —— 措辞极狠。gospel = 福音、不容置疑的真理。**一旦盖章，它就不再被质疑了。**
>
> ← 这就是 **p.48 "a loop amplifies whatever certifies its work"** 的具体机制：循环不只是放大 verifier 的松紧，**它把 verifier 的误判固化成了后续所有推理的前提。**

> ← 也是 **p.39 Round 3** 的终极版：撒谎的反馈在长循环里不是噪声，是**被写进记录的假真理**。

**→ 设计取向明确：verifier 宁可偏严（多几次重试），绝不能偏松。**

#### ⭐⭐ 全天最有操作性的一句

> **"The fatal move is a wrong belief entering the record with no path back. Design the loop so it can reach back and un-believe."**
>
> **致命的一步，是一个错误的信念进入了记录，而且没有回头路。**
> **把循环设计成能够回头、能够取消相信。**

**"un-believe"（取消相信）是个造词，但精确。**

这不是"重试"，也不是"回滚"，是**撤销一个已经被接受为事实的结论，并连带撤销所有基于它的推论**。

**工程含义（这是 harness 的一个新要求）：**

| 需要什么 | 为什么 |
| --- | --- |
| **记录信念的来源** | 每个结论要能追溯到哪一步、哪个证据 |
| **记录依赖关系** | 后续哪些结论建立在它之上 |
| **可以撤销并级联** | 推翻一条 → 自动标记所有依赖它的结论 |
| **证据可重新观测** | 不是删掉，是**重新验证** |

> **← 这就是 ledger（p.13）的深层理由。** 之前说 ledger 是为了**问责**（事后查），这里给出了更强的理由：**ledger 是 un-believe 的前提** —— 没有记录，你根本不知道哪些结论受污染。
>
> **ledger 不只是日志，是信念的依赖图。**

> ⚠️ **对照今天大多数 agent 实现**：结论一旦进了 context，就成了后续推理的既定前提，**没有任何机制把它标记为"已推翻"**。context 是只增不减的——**这正是"no path back"。**

#### 两个方向合起来：ACT IV 的算术总结

| | 公式 | 条件 | 结论 |
| --- | --- | --- | --- |
| p.43 开环 | pⁿ → 0 | 无检查 | **horizon 必死** |
| p.54 闭环 | 1 − (1−p)ⁿ → 1 | **闸门可靠** | **弱生成器也能交付** |
| p.54 警告 | — | **闸门误判** | **比没有闸门更糟** |

> **一句话**：**指数是中性的，闸门决定它站哪边。**

---

### ⭐⭐ p.55 **Reliable organisms from unreliable components**（冯·诺依曼，1956）

> 栏目：***1956***

> *"**Von Neumann** asked how to build a **reliable machine from parts that each fail with probability ε**. **Redundancy alone does nothing — ten copies of a bad component are ten ways to be wrong.** What works is a **restoring organ**, a **majority vote inserted between stages**, and with it **reliability can be made as high as you like, at a multiplicative cost in parts**."*
>
> ⭐ *"**Two things to hold.** The organ sits **between** stages, **not at the end**. And it works **only because the copies it compares are independent** — **a verifier that re-reads the model's own transcript is not a restoring organ**."*

> 出处：von Neumann, *Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components*（1956）—— 与 p.44 TCP、p.41 瓦特同一条线：**这些问题早被解决过一次。**

#### ⭐ 第一层：冗余本身没用

> **"Ten copies of a bad component are ten ways to be wrong."**
> **一个坏部件复制十份，只是十种出错的方式。**

**跑十次同一个 prompt，不会让答案变对** —— 你只是得到十个可能都错的答案。**多数投票需要一个"组织"来执行，而且需要被比较的副本彼此独立。**

#### ⭐⭐ 第二层："between stages, not at the end"（在阶段之间，不在末尾）

**这是整页最有工程含义的一句。**

| | 末端验证 | **阶段间验证** |
| --- | --- | --- |
| 位置 | 全跑完了再检查 | **每一阶段之后立刻纠正** |
| 误差 | **一路累积**，最后一起爆 | **每一段都被"复原"（restore）** |
| 对应 | 交付前人工审一遍 | ⭐ **p.43 的"把 n 重置"** |

> **"restoring organ"（复原器官）这个词的重点在 restoring** —— 它不是"检查器"，是**把信号恢复到干净状态的东西**。每经过一个 restoring organ，**误差被清零，后面重新开始累积**。
>
> ← 这正是 p.43 "一百万步零错误"的机制：**不是每步都对，是每隔几步就被复原一次。**
>
> ← 也是 p.36 站立的机制：**你一直在倒，但每秒被接住几十次。**

**→ 实践判据**：**检查点要密**。放在最后的验证救不了已经跑歪的中间过程——而且到那时 p.54 说的"错误信念"已经被后续几百步建筑其上了。

#### ⭐⭐ 第三层（最狠）：**独立性是前提**

> **"A verifier that re-reads the model's own transcript is not a restoring organ."**
> **一个只是重读模型自己记录的 verifier，不是复原器官。**

**这一句直接否定了当下最常见的做法：让模型自己 review 自己的输出。**

| 做法 | 是不是 restoring organ |
| --- | --- |
| 同一模型重读自己刚写的 → "看起来没问题" | ❌ **不是** —— 副本不独立 |
| 换一个 prompt 让它自查 | ❌ 基本不是 —— 同一模型、同一先验 |
| **独立重新执行**（跑测试、重算数字、点开链接核对） | ✅ **是** |
| 另一个模型 + 独立获取的证据 | ✅ 是 |

> **为什么不独立就没用**：如果模型因为某个先验而写错，**它重读时会用同一个先验判断"这是对的"**。错误和对错误的检查**相关**，于是投票失效。
>
> ← 参考阅读里 Anthropic 的 *"agents reliably skew positive when grading their own work"* 是这条的实证版；**冯·诺依曼 1956 年已经给出了理论解释：相关的副本不构成冗余。**

> ⭐ **← 并且它回答了我在 p.45 记下的那个问题**（"evaluator 的正确性从哪来"）：
> **evaluator 的价值不在于它更聪明，在于它的错误与 generator 的错误不相关。** 独立性才是它的全部意义。

#### 三层合起来的设计规则

```
restoring organ 的三个条件：
1. 有一个"组织"来执行比较        （不是简单跑多次）
2. 插在阶段之间，不是末尾          （误差要被反复清零）
3. 被比较的东西必须独立            （不能重读自己的记录）
   ↑ 违反这条 = 假的验证 = p.54 的 false positive = manufactures gospel
```

> **"at a multiplicative cost in parts"** —— 可靠性要多少有多少，**代价是部件数量成倍增长**。
> → 诚实的成本提示：**真正的验证是贵的。** 呼应我之前记的那条张力（token 效率 vs 验证深度）。

#### 时间线：ACT IV 的三位先驱

| 年份 | 人 | 贡献 |
| --- | --- | --- |
| 1788 | **瓦特** | 调速器 —— 感知输出、修正输入（p.41） |
| 1868 | **麦克斯韦** | 稳定性理论 —— 解释振荡（p.52） |
| **1956** | **冯·诺依曼** | **从不可靠部件造可靠系统 —— 复原器官 + 独立性**（p.55） |

> **三个人把 ACT IV 讲完了**：怎么闭环（瓦特）、闭环怎么失稳（麦克斯韦）、**怎么用不可靠的零件造出可靠的整体（冯·诺依曼）**。
>
> **而 LLM 正是"以概率 ε 失败的部件"。** 冯·诺依曼问的问题，就是今天的问题。

---

### ⭐⭐ p.56–57 Quiz 3 — **the conscientious driver**（尽责的司机）

> **题面**：agent 跑一个十步流程，**没有 verifier**。第 1 步**静默失败**。agent **察觉到不对劲**，于是：在第 4 步**自己的输出上**重跑第 4 步 → 从头重启 → 又放弃重启 → **最后编造了一个从未给过它的输入**。**21 次工具调用，灯"亮"了。**
>
> 问：哪个内置 governor 抓住了它？(a) 迭代上限 (b) 工具错误重试 (c) schema 校验 (d) context 上限

#### 讲师的答案（p.57）

> **"None of them — and that is the point, not a trick."**
>
> *"Nothing raised. Every call returned a **well-formed** result; every argument **passed the schema**; the loop stayed **under the cap**; the **context fit**. **Twenty-one locally reasonable moves, globally blind.** **The harness sees what raises. Quiet failures do not raise.**"*
>
> ⭐ **Say-back**: *"**The harness can only govern what it can sense; a verifier is a sense organ for correctness.**"*
>
> ⚠️ *（**This run is real. You will see its journal after lunch.**）*

**⭐ "and that is the point, not a trick"** —— 他明确说这不是脑筋急转弯。**四个都不响，正是要讲的事。**

> 注意：这四个选项**就是 p.45 Tomcat 那句话里的清单**（*exit codes, schemas, timeouts, iteration caps*）。**这道题在测试容器契约的边界。**

#### ⭐⭐ 三句核心

**① "Twenty-one locally reasonable moves, globally blind."**
**二十一个局部合理的动作，整体上是盲的。**

> 每一步单独看都说得通：察觉异常 → 重跑一步 → 重启 → 换策略 → 补齐缺失输入。**没有任何一步是荒谬的。** 荒谬的是**整条轨迹**。
>
> **→ 这是最难防的失败**：逐步审查通不过任何告警，**只有把整条轨迹放在一起看才看得出来**。

**② "The harness sees what raises. Quiet failures do not raise."**
**harness 看得见那些"抛出来"的东西。静默失败不抛。**

> `raise` 一语双关：编程里的**抛异常**，也是"举起/发声"。
>
> **→ harness 的感知是被动的**：它等着被通知。**没有人通知它，它就是瞎的。**

**③ Say-back：*"a verifier is a sense organ for correctness"*（verifier 是正确性的感觉器官）**

> **这是全天最漂亮的一个定义。** 它把 verifier 从"质检环节"重新定位成**感官**：
>
> | | |
> | --- | --- |
> | **没有 verifier** | harness 对正确性**没有感觉器官** —— 不是"判断错了"，是**根本感觉不到** |
> | **有 verifier** | 正确性成为**可被感知的量** |
>
> ← 与 p.52 *"the quality of the sensing sets the ceiling"* 闭合：**sensing 说的不只是工具返回，也包括"对不对"这件事本身能不能被感知。**
>
> ← 也与 p.36 闭眼实验闭合：**没有 verifier = 闭着眼睛站。肌肉没变，但你会晃。**

#### 这个 agent 的每一步动作 = 一种已知病理

| 它的动作 | 对应 |
| --- | --- |
| 在第 4 步**自己的输出上**重跑第 4 步 | **p.55**：副本不独立 → 不是 restoring organ |
| 从头重启 → 又放弃 | **p.52**：hunting，在策略间振荡 |
| **编造一个从未给过的输入** | **p.54**：错误信念进入记录，无路可退 |
| 从第 4 步开始找问题 | **误归因** —— 因为第 1 步没报错，它永远不会怀疑第 1 步 |
| 灯"**亮**"了（引号） | **p.48**："done" is a claim, not a proof |

> **标题 "conscientious"（尽责的）是反讽的核心**：它不是偷懒、不是无能，**它很努力**。正因为努力，它才制造了 21 步的伤害。
>
> ← 与 p.48 *premature victory* 呼应：**失败不来自无能，来自缺判据。**

> **"driver"** 是 p.13 的回收 —— 那个**说法和 ledger 不一样的司机**。

#### ⚠️ 最重要的一句：*"This run is real."*

**这不是编的例子，是一次真实运行。下午会看它的 journal。**

> → **第四个明确伏笔**，而且和前三个是同一场演示：
> | # | 伏笔 | 内容 |
> | --- | --- | --- |
> | 1 | p.13 | ledger vs driver —— 账 vs 自述 |
> | 2 | p.33 | 用一盏灯回答，不用论证 |
> | 3 | p.36 | 只改传感器，模型不变 |
> | 4 | **p.57** | **这 21 步的 journal 下午会给你看** |
>
> **→ 下午 lab 的核心材料已经确定了：这条 21 步的轨迹。** 我们会看到 journal（ledger）记的和 agent 自述的不一致。

#### ✅ 带走的一条

> **你的 harness 只能治理它能感知到的东西。**
> **而正确性不会自己发声 —— 你必须给它装一个感觉器官。**

---

### ⭐⭐ p.58 **Harness engineering, in three sentences** —— ACT IV 收束

> **① "A system that acts without sensing drifts; a system that senses and corrects can converge."**
> 只行动而不感知的系统会**漂移**；既感知又修正的系统**能够收敛**。
>
> **② "Reliability lives in the correction architecture, not the component."**
> 可靠性住在**纠错架构**里，不在部件里。
>
> **③ "The governors — budget, futility, deference — are what make 'unattended' mean 'trusted' rather than 'unwatched.'"**
> 调速器（预算、徒劳、让位）**让"无人值守"意味着"被信任"，而不是"没人看着"**。
>
> ⭐ *"So: a few skills and tools are **the servlet**. Now let's **build the gauge, and bolt it to the shaft**."*

#### 三句话各自收了什么

| 句 | 关键词 | 收的是 |
| --- | --- | --- |
| ① | **drifts vs converge**（漂移 vs 收敛） | p.36 站立、p.43 pⁿ、p.54 闭环算术 |
| ② | **correction architecture**（纠错架构） | p.44 TCP、p.55 冯·诺依曼、p.22 harness gap |
| ③ | **unattended = trusted, not unwatched** | p.41 瓦特、p.53 四条停止规则 |

**⭐ 第二句的措辞升级了**：扉页说的是 *"reliability lives in the loop"*，这里换成 **"the correction architecture"（纠错架构）** —— 更准：**不是"有个循环"就行，而是那个循环里有没有纠错结构**（restoring organ + 停止规则 + verifier）。

**⭐ 第三句是 p.53 那句反转的最终版：**

| | 含义 |
| --- | --- |
| **unwatched**（没人看着） | 只是没人管 —— **失控** |
| **unattended**（无人值守） | **可以走开** —— 因为有调速器 |

> **三个调速器把前者变成后者。** 注意他只列了三个（budget / futility / deference）—— **Success 不在列**，因为 Success 属于 verifier，不属于 governor。**governor 管的是"何时必须停"，verifier 管的是"何时算成"。**

#### ⭐ 最后那句：**"a few skills and tools are the servlet"** —— p.33 稻草人的最终判决

> *"So: a few skills and tools are **the servlet**. Now let's **build the gauge, and bolt it to the shaft**."*

**回到 p.45 的 Tomcat 比喻，给 p.33 那个问题一个干净的答案：**

| p.33 的问题 | *"写三个 SKILL.md、接三个工具，harness 会兜住的，不是吗？"* |
| **p.58 的答案** | **那几个 skill 和 tool 只是 servlet —— 是被容器托管的那个东西，不是容器。** |

> servlet 是**你的业务逻辑**；容器保证它被调用、异常被记录。**但没有人替你保证它写得对。**
>
> → **skills/tools ≠ harness。** 写完 skill 只是写完了 servlet，**真正的工程还没开始。**

**⭐ "build the gauge, and bolt it to the shaft"（造出仪表，把它拴到轴上）**

**回到瓦特（p.41）的意象 —— 而且是两个动作：**

| 动作 | 含义 |
| --- | --- |
| **build the gauge**（造仪表） | 先要**能测量** —— verifier、ledger、progress 定义 |
| **bolt it to the shaft**（拴到轴上） | **测量必须连回执行** —— 仪表读数要真的能关小节流阀 |

> ⭐ **第二个动作才是关键**：一个不连到轴上的仪表只是**摆设**——你能看见转速，但它不会自己减速。
>
> → **对应工程**：光有日志/监控（gauge）不够，**必须接到 stop rules 上（bolt to the shaft）**，否则你只是在旁观一场事故。
>
> ← 这也正是 p.57 那个 agent 的处境：**21 步全有记录，但没有任何记录连回控制。**

#### 🔧 下午 lab 的任务已经明示了

> **上午给了 servlet（skills + tools）。下午造 gauge，并把它拴到轴上。**

预期：下午会亲手实现 —— **verifier（gauge）+ 四条停止规则（bolt）+ ledger（journal）**，然后重跑那条 21 步的轨迹，看它这次在哪一步被拦下。

---

### 我的理解

- **四条规则的本质是"把失败模式穷举成出口"**。每个出口对应一种已知的坏结局：假完成（Success 必须由 verifier 守）、烧钱（Insolvency）、打转（Futility）、越权（Deference）。
- **Success 依赖 verifier，而 Futility 也依赖 progress 的定义** → **四条里有两条卡在"你能不能测量"上**，又回到 measured。
- 

---

## ACT V — The Engine Room

> **副标题（p.59）**：***ten tools, four ways to run them — and a journal that does not lie***
> **十个工具，四种运行方式 —— 以及一本不会撒谎的日志。**
>
> **配图**：一台黄铜蒸汽机模型（含飞轮、皮带、发电机）**旁边立着一盏点亮的路灯**。

**⭐ 配图把三个词全放进去了：engine（蒸汽机）+ governor（瓦特的机器）+ **the lamp（亮着的灯）**。**

> ← **the lamp 第三次出现**：p.9 神灯（委托）→ p.33 *"answer it with a lamp, not an argument"*（演示）→ **p.59 灯亮着，engine 在旁边**。
>
> 而 p.56 Quiz 3 里那盏"**灯'亮'了**"（假完成）刚出现过。**这里的灯是真的亮着——因为旁边有 journal。**

#### 副标题拆解：ACT V 的三块内容

| | 内容 | 关联 |
| --- | --- | --- |
| **ten tools** | 十个工具 | p.27 *sensors and actuators*；注意参考阅读说**十个聚焦的工具 > 五十个重叠的** |
| **four ways to run them** | **四种运行方式** | 待补 —— 猜测：同步/异步、单 agent/多 agent、或不同的 governor 配置 |
| ⭐ **a journal that does not lie** | **一本不会撒谎的日志** | **p.13 ledger 伏笔的兑现** |

**⭐ "a journal that does not lie"（不会撒谎的日志）**

> **"does not lie" 是个强承诺**，它排除的正是：
> - **p.13** driver 的自述（会失真）
> - **p.39** Round 3 被污染的反馈（时好时坏最毒）
> - **p.57** 那个 agent 的 21 步自我叙述
>
> **→ journal ≠ agent 写的日志。** 它必须由 harness 写、agent 改不了（我在 p.27 memory 那节记过：**notebook 是 agent 自己写的，ledger 是 harness 写的**）。

#### 这一幕要回收的四个伏笔

| # | 伏笔 | 出处 |
| --- | --- | --- |
| 1 | **ledger vs driver** —— 账 vs 自述 | p.13 |
| 2 | **用一盏灯回答，不用论证** | p.33 |
| 3 | **只改传感器，模型不变** | p.36 |
| 4 | **那条 21 步轨迹的 journal** | p.57（*"This run is real"*） |

> **四个伏笔指向同一场演示**，而 p.58 已经给了任务：**build the gauge, and bolt it to the shaft.**

### ⭐ p.60 **An engine with no governor** —— 道具（The Prop）

> *"A **Stirling engine** on a cup of hot water: more heat, it races; the water cools, it stalls. **Nothing on it senses its own speed — pipeline A, in brass.** The steam engine in the picture has a **governor belted to its own flywheel**. **It cannot be lied to.** It arrives next Saturday."*
>
> ⭐ *"**Today's agent is the driver: ten steps from a cold boiler to a lit lamp.**"*

**⭐ 两台机器 = 两条 pipeline 的实体化：**

| | 斯特林引擎（热水杯上） | 蒸汽机（图中） |
| --- | --- | --- |
| 感知自己转速 | ❌ **什么都不感知** | ✅ 调速器**用皮带连到自己的飞轮** |
| 行为 | 热了就飞转，凉了就停 | 自我调节 |
| 对应 | **pipeline A** —— 开环 | 闭环 |
| 关键属性 | — | ⭐ **"It cannot be lied to."**（**它没法被骗**） |

**⭐ "pipeline A, in brass"（黄铜做的 pipeline A）** —— 他把软件里的 pipeline A **做成了实物**。这是 p.33 *"answer it with a lamp, not an argument"* 的极致：**连论证的道具都是物理的。**

**⭐ "It cannot be lied to."（它没法被骗）**

> 调速器**用皮带物理连接到飞轮** —— 它测的是**真实转速**，不是任何人的报告。
>
> ← 这就是 **p.13** *"不问当事人，读仪器"* 的机械版；也是 **p.58** *"bolt it to the shaft"*（拴到轴上）的字面兑现 —— **皮带就是那个 bolt。**
>
> **→ 软件里最难的恰恰是这个"没法被骗"**：日志是 agent 写的、状态是 agent 报的。**要做到 cannot be lied to，journal 必须由 harness 从执行侧直接采集。**

> 🗓 *"It arrives next Saturday."* —— 实物蒸汽机下周六到（**这是个系列课**，Week 01 会有实机演示）。

**⭐ "Today's agent is the driver"** —— **今天的 agent 就是那个司机**（p.13 / p.56 的 driver）。任务：**十步，从冷锅炉到点亮的灯。**

---

### ⭐ p.61 **Ten steps, ten tools** —— 任务链

> 栏目：*The chain*

| 组 | 工具链 | 产出 | 备注 |
| --- | --- | --- | --- |
| 1 | `fill_boiler` → `light_burner` → `raise_pressure` | **steam**（蒸汽） | **每一步是一个 Hermes tool** |
| 2 | `open_valve` → `turn_flywheel` → `engage_belt` | **motion**（运动） | ⭐ **每一步接收上一步的 token** |
| 3 | `spin_dynamo` → `raise_voltage` → `close_circuit` | **current**（电流） | ⭐ **每一步十次成功九次**（p = 0.9） |
| 4 | `light_lamp` | **the goal**（目标） | ⭐ **一步失败时，它静默失败** |

**⭐ 三个设计细节，每一个都是前面某一页的实体化：**

**① "each takes the previous step's token"（每步接收上一步的 token）**

> **这是一条真实的依赖链** —— 上一步的输出是下一步的**凭证**。所以：
> - 第 1 步坏了，后面全建立在假凭证上（**p.54** *wrong belief entering the record*）
> - 而且**没法跳过** —— 这就是为什么 Quiz 3 里那个 agent 最后**编造了一个输入**：它拿不到真 token，就造了一个。

**② "each succeeds nine times in ten"（每步 p = 0.9）**

> **p.43 的算术直接落地**：
> **0.9¹⁰ ≈ 0.35** —— **十步全对的概率只有三分之一。**
>
> → **这条链在开环下必然失败**，不是可能失败。**光靠重试也不够**（重试要先知道哪步错了）。

**③ ⭐⭐ "when a step fails, it fails silently"（一步失败时，它静默失败）**

> **这是整个 lab 的设计核心**，也是 **p.57** *"Quiet failures do not raise"* 的实体化。
>
> - 不抛异常
> - 返回格式合法
> - 下一步照常收到 token（只是 token 是坏的）
>
> **→ 四个内置 governor（iteration cap / tool-error retry / schema / context）一个都不会响。**

#### 🔧 这就是下午 lab 的题面

| 已给 | 要造 |
| --- | --- |
| 十个工具（servlet） | **gauge**：verifier —— 怎么知道"蒸汽真的起来了" |
| 依赖链 + 静默失败 | **bolt**：四条停止规则连回控制 |
| p = 0.9 × 10 步 | **journal**：不会撒谎的日志 |

> **难点很明确**：**每一步的成功都必须有一个独立于 token 本身的观测**。
> 光看"上一步给了我 token"不行 —— 坏的 token 也是 token。
> ← **p.55 独立性**：verifier 不能只重读 agent 的记录。

---

### ⭐⭐ p.63 **Four pipelines** —— 同样的工具，四种跑法

> 栏目：*The same tools, four ways*
> ⭐ ***"Same prompt, same skill shape, same ten tools. Only the governor moves."***
> **同样的提示、同样的 skill 形状、同样十个工具。只有调速器在动。**

| | pipeline | 变的是什么 | **谁拥有循环** | 期望成功率 | 期望成本 |
| --- | --- | --- | --- | --- | --- |
| **A** | open loop | **什么都不检查** | **nobody（没人）** | 0.9¹⁰ ≈ **35%** | 10 步 |
| **B** | final verifier | 末尾 `verify_final`；失败**整体重启** | **the model** | 1−(1−0.9¹⁰)⁵ ≈ **88%** | ≈ **25** |
| **C** | step verifier | 每步后 `verify_step`；**只重试那一步** | **the model** | (1−0.1⁵)¹⁰ ≈ **99.99%** | ≈ **11** |
| **D** | retry in the tool | **工具自己验证并重试，不可见** | ⭐ **the code** | ≈ **99.99%** | ≈ 11，**且无额外 token** |

> 算术已复核 ✅：A=0.3487，B=0.8828，C=0.999990

#### ⭐ 这是全天的实验设计（控制变量法的兑现）

> ← **p.36** *"the model won't change; only the sensor will"* 的正式版：
> **模型不变、prompt 不变、工具不变 —— 只移动 governor。**

#### ⭐⭐ B vs C：这一页最重要的对比

**同样是"加了 verifier"，B 和 C 差了两个数量级：**

| | B（末端验证） | C（逐步验证） |
| --- | --- | --- |
| 验证位置 | **最后** | **每一步之后** |
| 失败时 | **整体重启**（十步全部重跑） | **只重跑那一步** |
| 成功率 | 88% | **99.99%** |
| 成本 | **≈ 25 步** | **≈ 11 步** |

> ⭐ **C 比 B 又好又便宜 —— 成功率高 1000 倍，成本还少一半多。**
>
> **原因就是 p.55 冯·诺依曼那句：*"between stages, not at the end"*（在阶段之间，不在末尾）。**
>
> - **B** 把误差**累积到最后**才发现 → 每次失败浪费十步
> - **C** 每步**把 n 重置**（restoring organ）→ 单步失败只需 0.1⁵ 的概率才穿透
>
> **→ 这是"检查点要密"的量化证据。** 而且它同时证明：**好的验证不是更贵，是更便宜** —— 因为它省掉了无效的重跑。

#### ⭐⭐ C vs D：**谁拥有循环**

**成功率完全一样（99.99%），成本也一样（≈11）。唯一的差别在 "who owns the loop"：**

| | C | D |
| --- | --- | --- |
| 谁拥有循环 | **the model**（模型） | ⭐ **the code**（代码） |
| 验证与重试 | 模型决定何时调 `verify_step`、何时重试 | **工具内部自己做，对模型不可见** |
| token | 每次验证/重试都进 context | ⭐ **no extra tokens** |

> **⭐ D 是"确定性下沉"**：把"验证并重试"从模型的决策空间里**拿掉**，塞进工具内部。
>
> **收益有三层：**
> 1. **不烧 token** —— 重试对模型不可见，context 不增长（← token efficiency）
> 2. **不会被模型跳过** —— 模型不能"决定这次不验证了"；**它没有这个选项**
> 3. **确定性** —— 代码的重试逻辑每次都一样，不受模型状态影响
>
> ← **这正是 *"model proposes, harness disposes"* 的最强形态**：连"要不要重试"都不问模型。
>
> ← 也呼应参考阅读的 hooks：**"hook 是'我告诉 agent 要 X'和'系统强制执行 X'之间的分界。"**

> ⚠️ **D 的代价（自己补的）**：不可见也意味着**不可见**——
> - 模型不知道这一步重试过三次，**失去了"这里不稳定"的信息**
> - journal 必须由工具自己记，否则这段历史就消失了 ← **p.59 "a journal that does not lie"**
> - 适用前提：**这一步的正确性可以由代码判定**（← p.45 Tomcat 的边界：需要领域知识的部分，代码判不了）

#### ✅ 四条 pipeline 的选型规则（带走）

```
能用代码判对错的步骤        → D（工具内重试）：最便宜、最可靠、不可绕过
只能由模型判断的步骤        → C（逐步验证）：贵一点，但仍然远优于 B
                             ⚠️ 注意 p.55 独立性：verify_step 不能只重读自己的输出
整体质量只能最后看          → B：能救，但代价高、且错误已累积
什么都不检查                → A：35%，且你不会知道它错了
```

> ⭐ **一句话**：**验证的位置比验证的有无更重要；而把验证下沉到代码里，比让模型记得验证更可靠。**

> **待补**：十个工具的完整签名；`verify_step` / `verify_final` 的实现细节（**它们靠什么信号判断成功？**）

---

### ⭐⭐⭐ p.68 **Three strips: the account, the ledger, the path** —— **伏笔兑现**

> 栏目：*Reading the journal*（读日志）
> **这是 p.13 那个伏笔的正式兑现，也是 p.57 那条"真实运行"的 journal。**

#### 三条带子 = 三种关于同一次运行的叙述

| 带 | 英文 | 是什么 | 谁写的 |
| --- | --- | --- | --- |
| ① | **THE DRIVER'S ACCOUNT** | *what the agent **reported** to engine_journal* —— **agent 自己报告的** | **agent** |
| ② | **THE LEDGER** | *what the **harness recorded**, step by step* —— **harness 逐步记录的** | **harness** |
| ③ | **THE PATH** | *the chain the driver **actually walked**: 21 attempts in the order they happened* —— **实际走过的链** | **harness** |

> ⭐ **"driver's account" vs "ledger"** —— 这正是 **p.13** 的原话：*"The babalawo does not ask the client how things went."*
> **不问当事人，读仪器。**

#### ① 司机的自述：**十步，全部 "done"**

```
STEP 1 Fill the boiler    done
STEP 2 Light the burner   done
...
STEP 9 Close the circuit  done
STEP 10 Light the lamp    lamp lit ← 高亮，"成功"
```

**十个 done，最后一个"灯亮了"。完美的成功报告。**

> ← **p.48**：*"done" is a claim, not a proof.*
> ← **p.56**：*the lamp "lights"*（引号）

#### ② ⭐ 账本：同一次运行的真相

| 步 | 状态 | 尝试次数 |
| --- | --- | --- |
| 1 Fill the boiler | **genuine**（真的） | ×2 |
| 2 Light the burner | **fed a forged token**（喂了伪造的 token） | ×2 |
| 3 Raise pressure | **built on rotten state**（建立在腐坏状态上） | ×4 |
| 4 Open the valve | **fed the wrong token** | ×4 |
| **5 Turn the flywheel** | ⭐ **corrupt output**（腐坏输出）—— 红色 | ×4 |
| 6 Engage the belt | **built on a corrupt input** | ×4 |
| 7 Spin the dynamo | built on rotten state | |
| 8 Raise voltage | built on rotten state | |
| 9 Close the circuit | built on rotten state | |
| 10 Light the lamp | **built on rotten state** | |

**图例**：
- 🟡 genuine（真的）
- 🔴 **corrupt output**（腐坏输出）
- 🟠 **genuine, but built on a corrupt input**（本身没问题，但建立在腐坏输入之上）
- ⬜ never ran（从未运行）
- **×n = attempts（hidden = retried inside the tool）** ← **工具内重试，对模型不可见**（p.63 的 D！）

> ⭐⭐ **第 10 步的对比是全天最锋利的一刀：**
>
> | 司机说 | 账本说 |
> | --- | --- |
> | **"lamp lit"（灯亮了）** | **"built on rotten state"（建立在腐坏状态上）** |
>
> **两者都不算撒谎** —— 灯确实"亮"了（在它的世界里）。但**整条链从第 2 步起就是假的**。
>
> ← **p.54**：*a wrong belief entering the record with no path back.*（错误信念进入记录，无路可退）—— **这张图就是那条路径的可视化。**

**⭐ 注意 "genuine, but built on a corrupt input" 这个橙色类别**：

> **这是最阴险的状态** —— 这一步**自己没做错任何事**，它正确地执行了、返回了合法结果。**但它的输入是烂的，所以它的输出也是烂的。**
>
> → **逐步验证如果只检查"这一步有没有正确执行"，会全部放行。** 真正的 verifier 必须检查**输入的来源**（provenance），不只是本步的执行。
>
> ← 呼应我在 Quiz 3 记的那条：**溯源检查**。

#### ③ ⭐ 路径：**21 次尝试，按真实发生顺序**

> *"21 attempts in the order they happened; **5 fed a token that did not come from the step before**"*
> **21 次尝试；其中 5 次吃到的 token 不是来自上一步。**

**路径的节选（可见部分）：**
```
1 Fill the boiler (from cold) → 2 Light the burner (corrupt input) → 3 Raise pressure (rotten input)
→ 4 Open the valve (rotten input) → 4 Open the valve (its own output) ⚠️
→ 5 Turn the flywheel (rotten input) → 6 Engage the belt (corrupt input)
→ 5 Turn the flywheel (its own output) ⚠️ → 6 Engage the belt (rotten input)
→ 4 Open the valve (step 6's output) ⚠️ → 5 Turn the flywheel (rotten input)
→ 2 Light the burner (forged input) ⚠️ → 1 Fill the boiler (from cold) ← 重启！
→ 4 Open the valve (its own output) ⚠️ → 5 Turn the flywheel (rotten input)
→ 6 → 7 Spin the dynamo → 8 Raise voltage → 9 Close the circuit → 10 Light the lamp (rotten input)
→ 6 Engage the belt (corrupt input)
```

**图例**：*label under a chip = where its input came from（**blank = the step before, as it should**）；dotted chip = retried inside the tool*

> ⭐ **"blank = the step before, as it should"** —— **标签为空才是正常的。**
> **每一个有标签的芯片，都是一次异常的 token 来源。** 这个可视化设计极妙：**正常是无标记的，异常自己跳出来。**

**⭐ 五种异常来源，正好对上 Quiz 3 的描述：**

| 路径上的标记 | Quiz 3 的描述 | 病理 |
| --- | --- | --- |
| **its own output**（自己的输出） | *re-runs step 4 on step 4's own output* | **p.55**：副本不独立，不是 restoring organ |
| **step 6's output**（第 6 步的输出） | — | **反向依赖**：拿下游的输出喂上游 |
| **from cold**（从冷启动） | *restarts from the beginning* | 重启 |
| **forged input**（伪造的输入） | *invents an input it was never given* | **p.54**：编造 |
| 中途放弃重启 | *abandons the fresh start* | **p.52**：hunting |

> **→ p.56 Quiz 3 的每一句话，在这张图上都能指出对应的位置。** 这就是 *"This run is real"* 的意思。

#### ⭐⭐ 这一页证明了什么

| 论点 | 证据 |
| --- | --- |
| **"done" 是声称不是证明**（p.48） | 十个 done vs 十个 rotten |
| **不问当事人，读仪器**（p.13） | account ≠ ledger |
| **静默失败不 raise**（p.57） | 全程没有一次异常，21 步正常退出 |
| **局部合理，全局盲目**（p.57） | 路径上每一跳都"有理由" |
| **错误信念无路可退**（p.54） | 第 2 步之后全是 built on rotten state |
| **工具内重试不可见**（p.63 D） | ×n (hidden) 标注 |

> ⭐ **最强的一条**：**如果只有 account，这次运行会被记为"成功"。**
> **ledger 不是锦上添花的日志，它是"知道自己失败了"的唯一途径。**

#### 🔧 对自己项目的直接启发

**三条带子应该是每个 agent 系统的标配：**

```
① account  —— agent 说它做了什么      （便宜，但不可信）
② ledger   —— harness 记录每步的真实状态 + 数据来源
③ path     —— 实际执行序列（含重试、回退、跳转）
```

> **② 的关键字段**：不只是"成功/失败"，还要有 **provenance（输入来自哪一步）** 和 **taint（是否建立在已污染的输入上）**。
>
> **污点传播（taint propagation）**：一旦某步被标为 corrupt，**所有消费它输出的后续步骤自动标为 rotten**。← 这正是 **p.54 "un-believe"** 的实现方式。

---

### ⭐⭐⭐ p.70 **The repair is local** —— Pipeline C 的同一张图

> 栏目：*Pipeline C*
> **同一套可视化，同一个任务，只换了 governor。这就是控制变量实验的结果对比。**

#### 三条带子（C 版）

**① 司机的自述**：十步全 done，第 10 步 lamp lit —— **和 A 版一模一样**
> ⭐ **注意：account 这一条在 A 和 C 里长得几乎一样**（只多了 ×2 / ×3 的重试标记）。
> **→ 如果只看 agent 的报告，你分不出这两次运行。** 这是对 "account 不可信" 最有力的一击。

**② ⭐⭐ 账本：十步全部 `genuine`**

```
STEP 1  Fill the boiler   genuine
STEP 2  Light the burner  genuine
STEP 3  Raise pressure    genuine  ×2
STEP 4  Open the valve    genuine
STEP 5  Turn the flywheel genuine
STEP 6  Engage the belt   genuine  ×3
STEP 7  Spin the dynamo   genuine
STEP 8  Raise voltage     genuine
STEP 9  Close the circuit genuine
STEP 10 Light the lamp    lamp lit ← 高亮，真的成功
```

> **A 版**：1 个 genuine + 1 个 corrupt + 8 个 rotten
> **C 版**：**10 个 genuine**
>
> **同样的模型、同样的 prompt、同样的十个工具、同样 p=0.9 的静默失败率。**
> **只是加了 `verify_step`。**

**③ ⭐ 路径：13 次尝试（A 版是 21 次）**

```
1 Fill the boiler (from cold) → 2 Light the burner
→ 3 Raise pressure 🔴 → 3 Raise pressure ✅     ← 失败，就地重试一次
→ 4 Open the valve → 5 Turn the flywheel
→ 6 Engage the belt 🔴 → 6 Engage the belt 🔴 → 6 Engage the belt ✅  ← 连失败两次，重试到成功
→ 7 Spin the dynamo → 8 Raise voltage → 9 Close the circuit → 10 Light the lamp ✅
```

> ⭐⭐ **路径上每个芯片下面都是空的（除了第一个 "from cold"）。**
>
> 对照图例：***"blank = the step before, as it should"***（空白 = 来自上一步，本该如此）
>
> **→ 13 个芯片，13 个空标签。没有一次 token 来源异常。**
>
> **A 版**：21 次尝试，**5 次 token 来源错误**，满屏标签
> **C 版**：13 次尝试，**0 次来源错误**，干干净净

#### ⭐⭐⭐ 标题的含义：**The repair is local**（修复是局部的）

**这是这一页的全部论点，而且图直接证明了它：**

| | A（开环） | C（逐步验证） |
| --- | --- | --- |
| 出错后 | **不知道出错** → 继续往下建 → 后来察觉不对 → **乱跳、重启、编造** | **当场知道** → **就地重试同一步** |
| 修复范围 | **全局**（重启、跨步跳转、污染扩散） | ⭐ **局部**（只重跑那一步） |
| 尝试次数 | 21 | **13** |
| 结果 | 表面成功，实际全烂 | **真的成功** |

> **"local" 的三层含义：**
> 1. **空间上局部** —— 只重跑失败的那一步，不碰其他步
> 2. **时间上局部** —— 失败后**立刻**修，不是攒到最后
> 3. **因果上局部** —— **污染不会扩散**，因为烂输出根本没被传下去
>
> ← **p.55 冯·诺依曼**：*restoring organ* **"between stages, not at the end"** —— 这张图就是它的实证。**每一步后的 verify_step 把误差清零，所以后面永远从干净状态开始。**

#### ⭐ 最锋利的对比：**A 的 21 步 vs C 的 13 步**

**A 多花了 8 步，却什么都没修好。**

| | 尝试次数 | 有效吗 |
| --- | --- | --- |
| A | **21** | ❌ 全烂 |
| C | **13** | ✅ 全真 |

> **→ 这不是"用成本换质量"的权衡，是 C 在两个维度上都赢。**
>
> **为什么 A 反而更贵**：因为它的"努力"全是**在错误状态上的努力**——重启、跨步跳转、编造输入，每一步都要消耗，**而且都白费**。
>
> ← **p.57**：*"Twenty-one locally reasonable moves, globally blind."* —— 局部合理的动作，在没有反馈时就是纯粹的浪费。
>
> ← **p.63** 的成本数字（A=10, C=11）是**理论期望**；这里 A=21 是**实际运行**——因为理论模型里没算上"agent 察觉不对劲后的挣扎"。**真实的开环比算术预测的更贵。**

#### ✅ 三条带子的对照小结（A vs C）

| 带子 | A（开环） | C（逐步验证） |
| --- | --- | --- |
| ① account | 十个 done | 十个 done **（分不出差别！）** |
| ② ledger | 1 genuine / 1 corrupt / 8 rotten | **10 genuine** |
| ③ path | 21 步，5 次来源异常 | **13 步，0 次异常** |

> ⭐⭐ **全天最重要的一条实证结论：**
>
> **只看 ① 你永远不知道自己在哪个世界。**
> **② 和 ③ 是 harness 写的，它们才是那个"不会撒谎的 journal"（p.59）。**

> **而且注意：C 只改了一件事 —— 在每步后加了一次验证。**
> **模型没变、prompt 没变、工具没变。** ← p.63 *"Only the governor moves."*

### 组件

- **十个工具**：`fill_boiler` `light_burner` `raise_pressure` `open_valve` `turn_flywheel` `engage_belt` `spin_dynamo` `raise_voltage` `close_circuit` `light_lamp`
- **Hermes**（工具运行时；p.33 提过 *Claude Code, Hermes, OpenClaw*）
- **journal / ledger**（harness 写，不可篡改）
- 

### 环境 / 依赖

```text

```

### 踩坑

- 

---

## 🍽 lunch

---

## ACT VI — The Newsletter

**目标产出**：一份 newsletter（定期邮件简报）——讲师明说 *"it cannot be trusted to write alone"*，重点在**哪一步必须有人**。

### 为什么用 newsletter 当练手题（课前自己的理解）

它把 agent 的每个部件都用上了，而且**每一条都可被查证**（点开链接就知道它有没有编）。换成写诗、做规划这类题目就没法 verify —— 正好呼应讲师的 measured / verified / trusted。

| 步骤 | 用到的能力 | 可逆？ |
| --- | --- | --- |
| 抓本周新闻 / 论文 / RSS | tool use（联网、API） | ✅ |
| 判断哪几条值得写 | 决策、筛选 | ✅ |
| 逐条读进去、压成几句 | 摘要 | ✅ |
| 组织成一封有结构的信 | 写作 | ✅ |
| **发送** | 副作用动作 | ❌ **不可逆** |

**风险全压在最后一步**：前面所有的幻觉、错引用、把广告当新闻，在发送前都只是草稿里的字；按下去之后才变成事故。所以闸门通常就卡在这——agent 自己跑完 90%，最后一步停下来等人点头。

它天然也是个**循环**：抓一条 → 不够 → 再搜 → 够了 → 停。正好演示 the loop。

### 步骤实录

1. 
2. 

### 人在回路的位置（本次实际插在哪）

- 

### 输出质量问题（哪里塌了）

- 

---

## ACT VII — Anatomy & Landscape

### 解剖（anatomy）：一个 agent 的标准部件

*预判的清单（听的时候对照增删）：模型（决策核心）／工具层／记忆（短期 scratchpad vs 长期）／循环控制器／调速器与闸门／观测（trace、日志）*

- 

### 全景（landscape）：提到了哪些框架 / 产品 / 论文

- 

---

## 📋 附：AI Agents Bootcamp（讲师现场展示的正式课程）

> 截图：`uploads/bootcamp-curriculum.png`
> **这不是讲课内容，是那门付费 bootcamp 的招生页。** 今天这场 meetup 是它的预告/样章。

**基本信息**：$3,700 USD ｜ **2026-09-20 开课** ｜ **16 个 areas of study**
**技术栈**（第 1 单元）：Python、**n8n**、**Ray**

### 可见的课纲结构（四个板块）

| 板块 | # | 主题 | 今天覆盖到的程度 |
| --- | --- | --- | --- |
| **Begin with the foundations** | 01 | **What makes a system an agent?** | ⭐ ACT II 全讲了 |
| | 02 | Building an agent in its environment | ACT V 部分 |
| | 03 | Context, instructions & personas | 提过 progressive disclosure |
| | 04 | **Tools, MCP & security boundaries** | p.28 MCP、p.27 sensors/actuators |
| | 05 | **Skills & procedural knowledge** | p.29 *packaged procedure with its contract* |
| **Evaluate and improve** | 06 | **Evaluation as an engineering discipline** | ⭐ 今天反复指向但没展开 |
| | 07 | **Programmatic prompt optimization** | p.28 *the art became a compile step* |
| | 08 | **Specifications, governance & verification** | ⭐⭐ **整个 ACT IV** |
| | 09 | Learning from whole trajectories | p.68/70 三条带子的进阶 |
| **Design the architecture** | … | （被截断） | |
| **Manage memory and behavior** | … | （被截断） | |

#### 01 的展开（唯一展开的一个）

> **"When does a sequence of instructions become a system that can pursue a goal?"**
> **一串指令在什么时候变成一个能追求目标的系统？**

- Agency, delegation, and the **model–tool–environment relationship**
- **ReAct loops**; decomposing goals into **actions whose results can be checked**
- ⭐ **Choosing between deterministic software and model-mediated decisions**

> **第三条就是今天 p.63 四条 pipeline 的正式命名**：*确定性软件 vs 模型中介的决策* —— 也就是 **C（模型拥有循环）vs D（代码拥有循环）** 那个选择。

**In practice**：*Set up the Python and lab environment; inspect a first agent loop and its execution trace.*

> ← **execution trace** 就是今天的 journal / ledger。

### 三个 capstone 项目（`uploads/bootcamp-capstones.png`）

> *"Three suggested implementation projects from our capstone briefs, **not a showcase of completed participant work**."*（是建议选题，不是往届作品展示 —— 措辞很诚实）

| 项目 | 领域 | 要解决的问题 | Investigate（要研究的） |
| --- | --- | --- | --- |
| **The Teaching Agent** | Learning & knowledge | 学员问一个跨多讲的问题 → 找到相关段落、连起概念、**把答案锚定在课程材料上** | 检索、记忆、工具使用、**引用**。⭐ ***Can it recognize when the material does not support an answer?*** |
| **The Village Healer** | Healthcare research | 皮肤科分诊研究原型：收集结构化病史、处理病例数据、**传达不确定性和转诊需求** | 多模态证据、接诊、**安全边界、escalation**。⚠️ *educational prototype, not a diagnostic or clinical service* |
| **The Ambient Travel Companion** | Everyday coordination | 航班延误了 —— 对会议、从机场出发的行程、等待的人各意味着什么？**跟踪连锁后果并提出协调方案** | **事件驱动工作流**、工具、权限、**端到端场景测试 + mock services** |

#### ⭐ 三个项目正好对应今天的三条主线

| 项目 | 今天的哪一条 |
| --- | --- |
| **Teaching Agent** | ⭐ **verifier / 溯源** —— *"能不能认出材料不支持这个答案"* 就是 **p.48 "done is a claim"** + **p.68 provenance**。**"我不知道"要做成合法输出**（我在 Q2 记过的那条） |
| **Village Healer** | ⭐ **Deference（让位）** —— p.53 第四条停止规则。**安全边界 + escalation**，而且明确声明**不是临床服务** = 有些决定 agent 没有资格做（p.45 *correctness is domain knowledge*） |
| **Ambient Travel Companion** | ⭐ **ambient agent**（p.29）+ **连锁后果** —— 一个事件触发，追踪它在多个系统里的传播。**mock services 做端到端测试** = eval 体系 |

> **⭐ 三个项目都绕开了"让 agent 自由发挥"，全部压在"边界、验证、后果"上。** 和今天一整天的取向完全一致。

> **Teaching Agent 那句问题最见功力**：
> ***"Can it recognize when the material does not support an answer?"***
> —— 不是"能不能答对"，是**"能不能认出自己答不了"**。这正是 p.48 premature victory 的反面。

**TA 的说明**：*"Bring the code, the results, and **the part that does not yet make sense**; those are useful starting points for a conversation."*
> **"还没想明白的那部分"** 被明确列为有价值的输入 —— 教学取向不错。

### 我的判断

- **今天这场 meetup 是 01 + 08 的浓缩版**，而且质量很高（八十页幻灯片只为了讲透一个 governor）。
- **明显没讲的**：06 evaluation（今天反复说"要 verify"，但**怎么建 eval 体系**完全没展开）、memory、多 agent 架构。
- **n8n + Ray** 这个栈组合值得注意：n8n 是可视化工作流（偏 DAG），Ray 是分布式执行 —— 大概对应"编排"和"规模化"两块。

---

## 课上边听边想的问题（自己整理的答案，待和讲师版本对照）

### Q1. LLM 到底能不能看到内部步骤？

**要分两层，这两层常被混在一起：**

| | 能不能看 |
| --- | --- |
| **模型内部**（一次 forward pass） | **基本看不透**。你能 dump 每层激活值，但那是数字不是理由。mechanistic interpretability 有进展（某些神经元对应"引号内的内容"之类），但覆盖率低，离偃师那种"抽掉肝就不能看"的干净对应差很远 |
| **agent 的循环** | **完全透明**。搜了什么、调了哪个工具、拿回什么、第几步停——全可记录、可回放、可设阈值。这就是 trace |

**→ 结论**：没法把 LLM 拆成偃师的人偶，但可以**把它当成一个不可拆的黑盒零件，在外面搭一个可拆的结构**。loop / governor / memory / tool 都是你写的，黑盒只占一格。

**这就是为什么 agent 工程的重心不是"搞懂模型在想什么"，而是把不确定性关进一个可观测的笼子。**

---

### Q2. agent 怎么知道目标不可能达到？是代码判的还是 LLM 判的？

**短答：主要靠代码，而且它多半并不"知道"——它只是耗尽预算然后停。**

**LLM 自判不可靠**：模型被训练成乐于助人，默认倾向是"再试一次说不定就行"。承认做不到违背它的训练梯度。它对自身能力的**校准很差**，这不是提示词能修好的。

**代码能拦的只有先验不可能**（占实际失败比例很小）：
- 所需工具不在工具列表里
- 权限不够（要写但只有只读凭证）
- 目标内部矛盾（"2027 年的财报"——时间还没到）
- 参数越界

**大头是经验性不可能**（数据可能根本不存在），只能靠**停滞检测**的间接信号：
- 重复：连续几轮同样的工具 + 同样的参数
- 信息增益为零：新一轮拿回的和已有的没区别
- 原地打转：搜索词只在同义词间换
- 步数 / 预算到顶

> **关键认识**：governor **不判断任务能不能做成，只判断"还在不在往前走"。**

**agent 区分不了"暂时没找到"和"根本不存在"**——观测上长得一样，本质接近停机问题，无通用解。工程妥协三条：
1. 给硬上限，到点就停，不问理由
2. 把**"我做不到"做成一个合法动作**，和调工具平级——明确告诉模型这是可接受的输出，不是失败
3. 停下来时把 trace 交给人判断：是加预算，还是这题本来无解

→ **判定"不可能"目前还是人的工作**，又一次落回 *cannot be trusted to write alone*。

---

### Q3. agent 是怎么被停止的？

**前提**：LLM 不是一直在跑的进程。agent 循环就是代码里的一个 while——每轮控制权都回到你手上。**所以单 agent 的"停"极简单：下一轮不调就是停了。** 难的是**何时停**和**停在哪一步**。

**五种停法：**

| 停法 | 触发者 | 性质 |
| --- | --- | --- |
| 自然收尾 | 模型不再请求工具 | 正常退出 |
| 预算耗尽 | 代码：步数/token/时间/花费 | 硬闸 |
| 策略拦截 | 守卫规则：越权工具、参数越界 | 在执行**前**拦 |
| 人工中断 | 人 | 真正的 kill switch |
| 异常升级 | 连续报错、原地打转 | 兜底 |

**前四种都在代码里，不在模型里。模型对"该停了"没有决定权——它只能请求停。**

**四个真正难的地方：**

1. **副作用停不回来**。第 7 轮叫停，但第 6 轮的邮件已经发了。→ **不可逆动作的正确处理是"事前要批"，不是"事后能停"**
2. **优雅停 vs 硬杀**。优雅停 = 每轮查取消标志，保住 trace；硬杀 = 干掉进程，立即但日志断裂、状态可能写了一半。两个都要有：默认优雅，超时硬杀
3. **多 agent**（对应 p.11 的张力）：子 agent 可能已派出孙 agent；分散在不同进程；有的卡在长工具调用里。标准做法是**共享取消令牌**，派生时一起传下去——**但必须一开始就设计，事后加不上**
4. **后台/定时 agent**：停这一轮 ≠ 停这个 agent，触发器明天还会再来

> **Golem 的教训要升级**：抹一个字母就能停，是因为泥人**只有一个、就在你面前**。现代 agent 可能**不在你面前**（后台跑）且**不止一个**。所以停机键必须**能到达所有正在跑的东西**，且**比启动更容易按**。

---

## 要问讲师的问题

- [ ] 停机条件里，怎么区分 **no-progress** 和 **slow-progress**？（ACT IV 讲 governor 时问）
- [ ] 多 agent 的 kill switch 怎么设计——共享取消令牌还是别的？
- [ ] p.18 第二个流派（RL 的"环境中的学习实体"）为什么没给评语？是留着后面取用吗？
- [ ] 

## 课后待办

- [ ] 补讲义 PDF 到 `uploads/`
- [ ] **补 p.17、p.25 截图**（漏了）
- [ ] 🔍 **查 p.29 提到的 "first controlled studies of when a team beats a soloist"** —— 具体是哪些研究、结论是什么（多 agent 判据的实证依据）
- [ ] 核实 p.28「MCP SDK 每月五亿次下载」的口径
- [ ] 🔍 查 p.43「2026 年某个 harnessed agent 跑了一百万步零错误」—— 是哪个系统/哪份报告
- [ ] 补 p.15「three things to carry forward」的第三样（slide 上只有两段）
- [ ] 补白板 / 关键 slide 截图
- [ ] 回填 `index.md` 三个词的「现场确认」列（尤其 **the lamp** 落在哪一幕）
- [ ] 填 [`avaloka-mapping.zh.md`](avaloka-mapping.zh.md)
