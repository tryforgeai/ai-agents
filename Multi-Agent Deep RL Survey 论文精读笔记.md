# Multi-Agent Deep RL Survey 论文精读笔记

> **Multi-agent deep reinforcement learning: a survey**
> Sven Gronauer, Klaus Diepold
> **Technical University of Munich（TUM）**，电气与计算机工程系
> ***Artificial Intelligence Review* (2022) 55:895–943** · `doi:10.1007/s10462-021-09996-w` · 2021-04-15 在线发表 · CC BY 4.0 开放获取
> 原文：[course/ai-agents-week-06/papers/s10462-021-09996-w.pdf](course/ai-agents-week-06/papers/s10462-021-09996-w.pdf)（**49** 页，正文约 36 页 + 参考文献）
> 课程：**Week 06 当周阅读**。课程全名是 *AI Agents & Multi-Agents RL Bootcamp*——这篇是 "Multi-Agents RL" 那一半的地图
> 整理于 2026-10-25

> ⚠️ **先分清两种"多 agent"**（[[course/reading-list.zh.md|阅读清单]] 里已经提醒过）：这篇的 agent 是**训练出来的策略网络**，通过 reward 更新权重；本周另一篇 [[Landscape of AI Agent Architectures 论文精读笔记|Landscape]] 的 agent 是**被 prompt 出来的 LLM**，不训练、靠文字协作。这篇**一个 LLM 都没有**——写于 2020 年底、2021 年 4 月发表，比 ChatGPT 早一年半。课上借它的是**问题清单**（团队什么时候比单打独斗好、为什么难），不是方法。

---

## 0. 一句话总括

**把 2016–2020 年的多智能体深度强化学习（MADRL）切三刀：怎么训练（集中 / 分布 × 集中 / 分散执行）、会涌现什么行为（奖励结构 / 语言 / 社会情境）、有哪六个单 agent 没有的难题（非平稳、通信、协调、信用分配、规模、部分可观测）——结论是"训练时集中、执行时分散"（CTDE）是当下主流答案，而异质性和维度灾难是最难的两座山。**

核心贡献不是新算法（**零实验**），也不是理论（作者明说和 Zhang et al. 2019 的理论综述互补），而是：

> **一张"难题 → 解法 → 论文"的对照表（Table 3），加一张"趋势 → 它缓解了哪些难题"的表（Table 4）。拿到一个多 agent 问题，先查它属于哪个难题，再查有哪几条路。**

⚠️ **能主张什么、不能主张什么**：全文没有任何 benchmark 数字、没有对比表、没有元分析。所以它只能告诉你**某类方法被用来解某个问题**，不能告诉你**哪种方法更好、好多少**。读的时候想要数字，必须回到它引的原论文。

---

## 1. 动机与定位

### 1.1 为什么要多 agent

> *"A multi-agent system describes multiple distributed entities—so-called agents—which take decisions autonomously and interact within a shared environment"*（Weiss 1999）

难点在于 *"Specifying intelligent behavior a-priori through programming is a tough, if not impossible, task for complex systems"*——所以要让 agent 自己学，而学习最常用的框架就是 RL。

引言列的应用，**顺序是**：
1. 分布式系统协调——**自动驾驶**、**多机器人控制**
2. 通信网络的数据包路由
3. 金融市场交易

🔑 第一条是这个圈子被重视的原因：**多个决策者同时在一个环境里，每个人的最优策略取决于别人怎么做**。单 agent RL 的成功（Atari、AlphaGo、机器人）大多回避了这个问题。

### 1.2 它在综述谱系里的位置（§1.1）

| 综述 | 年份 | 关注点 |
| --- | --- | --- |
| Stone & Veloso | 2000 | 第一批；按同质 / 异质、能否通信分类 |
| Shoham et al. | 2003 | **批评 MARL 问题本身定义不清**，提了 4 个研究方向 |
| Busoniu et al. | 2008 | 好处（计算加速、经验共享）vs 难处（目标难定义、非平稳、协调、**agent 数增加时复杂度指数增长**） |
| Tuyls & Weiss | 2012 | 批评 RL + 博弈论主导、问题停留在 grid world；**规模化是"圣杯"** |
| Hernandez-Leal et al. | 2019 | 4 类：涌现行为、学通信、学合作、建模其他 agent |
| Nguyen et al. | 2020 | 5 个技术难题：非平稳、部分可观测、连续空间、训练方案、迁移 |
| Zhang et al. | 2019 | 理论视角 |
| **本篇** | 2021 | **比 Hernandez-Leal 和 Nguyen 更宽**；与 Zhang 互补 |

🔑 注意 Tuyls & Weiss 2012 那句"规模化是圣杯"——**九年后本篇在 §6.2 给出的"最难的问题"还是维度灾难**。这个领域最大的那块石头一直没搬动。

### 1.3 三刀切法（Figure 1）

| 章 | 切的是什么 | 子类 |
| --- | --- | --- |
| §3 | **训练方案** | 训练：集中 / 分布 × 执行：集中 / 分散 |
| §4 | **涌现行为** | 奖励结构 · 语言 · 社会情境 |
| §5 | **六大难题** | 非平稳 · 通信 · 协调 · 信用分配 · 规模 · 部分可观测 |

---

## 2. 方法精读：形式化基础 + 训练方案 🔥

全文共 **12** 个编号定义（Def 1–12），构成了读懂所有 MARL 论文的最低词汇量。

### 2.1 单 agent：MDP（Def 1）

元组 **(X, U, P, R, γ)**：状态空间、动作空间、转移函数 P: X×U→𝒫(X)、奖励 R: X×U×X→ℝ、折扣 **γ ∈ [0, 1)**。

目标：学策略 π: X→𝒫(U)，最大化期望折扣回报

$$J = \mathbb{E}\left[\sum_{t=0}^{\infty}\gamma^t R(x_t, u_t, x_{t+1})\right]$$

价值函数 V^π(x)、动作价值函数 Q^π(x, u) 按常规定义。deep RL 就是用神经网络表示策略、价值函数或两者。

### 2.2 多 agent：Markov Game（Def 2，Littman 1994）

元组 **(𝒩, X, {U^i}, P, {R^i}, γ)**，其中 **N > 1**：
- **联合动作空间** U = U¹ × ⋯ × U^N
- 每个 agent **各有自己的奖励** R^i
- 转移函数由**联合动作**决定

关键变化：

$$V^i_{\pi^i, \boldsymbol{\pi}^{-i}}(x)$$

**agent i 的价值不只取决于自己的策略，还取决于所有其他人的策略 π^{−i}**。这一个下标改动，是后面所有难题的根源。

特例：**strategic-form game**（状态空间为空，一次性博弈，又叫 matrix game / normal-form game）；最常研究的是 **N = 2** 的 bi-matrix game。

### 2.3 解的概念（Def 3–5）

| 概念 | 意思 | 🔑 |
| --- | --- | --- |
| **Best response**（Def 3） | 别人策略固定时，我的最优策略 | 别人一变，我的最优就变 |
| **Nash 均衡**（Def 4） | 每个人的策略都是对其他人的 best response；**没人能单方面偏离而获益** | 可能不唯一 |
| **Pareto 最优**（Def 5） | 没有别的联合策略让所有人不差、至少一人更好 | 用来在多个 Nash 均衡里挑 |

### 2.4 三种任务设定（按奖励结构，沿用 Busoniu 2008）

| 设定 | 奖励 | 
| --- | --- |
| **完全合作** | R = R¹ = ⋯ = R^N，所有人同一个奖励 |
| **完全竞争** | 零和：Σ R^i = 0 |
| **混合** | general-sum，对目标没有限制 |

信息维度：**independent learners**（无视别人存在，看不到别人的动作和奖励）vs **joint-action learners**（事后能看到所有人的动作）—— Claus & Boutilier 1998。

### 2.5 多 agent 特有的病（§2.3，Def 6–9）

| 病 | 定义 | 一句话 |
| --- | --- | --- |
| **非平稳**（Def 6） | P(x′\|x,u,π¹…π^N) ≠ P(x′\|x,u,π̄¹…π̄^N)，因为别人的策略在变 | **移动靶**：Markov 假设不再成立 |
| **Shadowed equilibrium**（Def 7） | 一个均衡被另一个"遮蔽" | 从差的均衡偏离，看起来不比从好的偏离更糟 |
| **Relative over-generalization** | shadowed 的一种：**次优的 Nash 均衡被偏好于最优解** | 因为它和**任意**队友动作搭配都还行——稳但平庸 |
| **POMG / dec-POMDP**（Def 8） | 每个 agent 只看到 O^i ⊂ X；合作 + 共享奖励时叫 dec-POMDP | 策略要依赖**观察历史**，不能只看当前 |
| **信用分配**（Def 9） | 完全合作、共享奖励下，**个体无法判断自己的动作对团队成功贡献了多少** | |

> *"Hence, the Markov assumption of an MDP no longer holds, and agents face—without further treatment—a moving target problem"*

🔑 **relative over-generalization 是全篇最反直觉、也最值得记的概念**：合作场景里，agent 学会了一个"和谁配合都不太差"的动作，而不是"和对的人配合最好"的动作。↔ LLM 多 agent 里"谁都能接上话但谁都不负责"的平庸讨论。

⚠️ 作者在 §2 末尾承认：**相对过泛化 + 奖励随机性，连简单的表格世界都没解决**（如 climbing game 的变体）。

### 2.6 训练方案（§3，Figure 2，Table 1）

先分清两个词（⭐ 脚注 4）：**test** = 训练后评估、策略不再更新；**execution** = 按策略选动作。文献里常混用，作者刻意区分。

| 方案 | 定义 | 好处 | 坏处 |
| --- | --- | --- | --- |
| **CTCE**（Def 11） | 一个集中执行器 π: O→𝒫(U)，输入所有人的观察，输出所有人的动作 | 直接套单 agent 算法（A3C、PPO） | 状态-动作空间**随 agent 数指数增长**；**lazy agents**：一个学好了，另一个就没动力学 |
| **DTDE**（Def 10） | 每个 agent 只用本地观察，**不共享任何信息**，各学各的 | 简单、天然分布式 | 环境对每个人都非平稳；**scale 差**（Gupta 2017：不如集中训练；Foerster 2018b：独立 actor-critic 学得慢） |
| **CTDE**（Def 12） | 每个 agent 有自己的策略 π^i: O^i→𝒫(U^i)；**训练时额外给信息，测试时拿掉** | 训练时绕过非平稳（看得到别人动作）、测试时各自独立 | 训练需要共享计算或通信 |

> *"The CTDE paradigm presents the state-of-the-art practice for learning with multiple agents"*

**CTCE 的补救**：把联合策略分解成独立子策略 P(U) = ∏ P(U^i)（Gupta 2017）；把联合价值分解成本地价值之和 Q = Σ Q^i（Russell & Zimdars 2003）。

**DTDE 的补救**（都在合作场景）：
- **CERT**（Omidshafiei 2017）：分布式经验回放，让样本更稳
- **Leniency**（Palmer 2018）：回放中每个样本带一个**衰减温度**，早期乐观更新 → 克服 relative over-generalization
- **NUI-DDQN**（Palmer 2019）：识别并删除导致协调失败的样本
- **分位数估计器**（Lyu & Amato 2020）：按回报似然识别非平稳样本
- **基于种群的训练**（Jaderberg 2019、Liu 2019）：差的 agent 被好的 agent 的变异版替换

**CTDE 按 agent 结构再分**：

| 结构 | 方法 | 代表 |
| --- | --- | --- |
| **同质** | **参数共享**：所有 agent 用同一个网络，因观察不同而行为不同 | Gupta 2017 等，被"thoroughly demonstrated"能加速学习 |
| 同质 | **价值分解**：联合价值拆成个体价值 | VDN、QMIX、QTRAN（详见 §4 信用分配） |
| **异质** | **每个 agent 一个集中式 critic** | **MADDPG**（Lowe 2017）：critic 看所有人的策略，actor 只看本地观察 |
| 异质 | **所有 agent 共享一个集中式 critic** | **COMA**（Foerster 2018b）：反事实基线，把单个 agent 的动作"边缘化掉" |
| 异质 | 降方差 | Wu 2018：包含其他 agent 信息的动作依赖基线 |
| 混合 | **master-slave** | Kong 2017：master 收集各 slave 的本地信息、回传自己的内部状态，slave 据此行动 |

🔑 **CTDE 的本质是"训练时有一个全知的老师，考试时老师离场"**。集中式 critic 就是那个老师——它看得见所有人的动作，所以能告诉每个 actor"你那一步到底好不好"。↔ RLVR 里的 verifier：训练时有特权信息（标准答案），推理时没有。

---

## 3. 实验与证据：涌现行为（§4，Table 2）

⚠️ 这一章**不是作者的实验**，是他们对"分析涌现行为"的论文的分类。作者明说：这一节关注的是**分析**行为的论文，不是**提出**新方法的论文。

### 3.1 奖励结构 —— 最主要的影响因素

| 发现 | 论文 |
| --- | --- |
| **团队奖励相对个体奖励越大，合作意愿越强** | Leibo 2017 |
| **一个 agent 失败就惩罚全队**，也能诱导合作：agent 学会帮队友避免失败 | Tampuu 2017（Pong） |
| 竞争奖励越高，agent 越会用**高级策略**压制对手（反弹球、加快球速） | Tampuu 2017（Pong） |
| **对抗训练能学出比环境本身更复杂的行为**（3D 物理里的跑、挡、扑） | Bansal 2018 |

**内在奖励**（奖励稀疏时）：两大类（Pathak 2017 的划分）——
1. 鼓励去**没见过的状态**（用模型估计状态访问分布，Bellemare 2016）
2. 鼓励**降低对自己动作后果的不确定性**（学环境动力学，预测误差大 = 新奇）

### 3.2 语言

**指称游戏**（referential games）：说话者把目标通过消息告诉听者。
- Lazaridou 2017：agent 只靠交互就能学出通信协议，语言有语义属性；**人类可解释性"有限但令人鼓舞"**
- Mordatch & Abbeel 2018：**超过 3 个** agent 参与对话 + **惩罚词汇量过大** → 收敛到一致的词汇、避免歧义词，还学出了**句法结构**
- Li & Bowling 2019：**组合性语言更容易传给别的 agent**；训练中**更换听者**能促使语言更结构化

**对话**：
- Lewis 2017：两个 agent 用自然语言谈判分物品 → **学会了欺骗**来获得更高回报
- Das 2017：一个看图提问、一个回答，都用自然语言

> *"numerical performance measurements provide evidence but do not give insights about the communication abilities learned by the agents"*

Lowe 2019 整理了评估通信质量的指标；Eccles 2019 用归纳偏置促进有意义通信。

🔑 **Mordatch & Abbeel 的"惩罚词汇量"就是 MARL 版的"少说话"**——和 Landscape 那篇里 MetaGPT 用结构化产物压闲聊是同一个方向，早了 6 年。

### 3.3 社会情境

**社会困境**：个人利益 vs 集体利益。矩阵博弈里是一次性决定（合作还是背叛），**sequential social dilemmas**（Leibo 2017）把它扩展到时间上。

行为按人类心理变量分类，共 **5** 个：个人收益、对未来后果的恐惧、对他人行为影响的评估、信任、情绪。

Kollock 1998 的二分：
- **commons dilemmas**：个人短期收益 vs 长期共同利益
- **public goods dilemmas**：公共资源有限，必须可持续使用；**公地悲剧**（Hardin 1968）预言自利 agent 会过度开采

### 作者没报的

**这一整章没有一个效应量**：团队奖励大多少倍时合作率是多少？Pong 里竞争奖励多高时出现反弹球？全是定性描述。想要数字，只能去读原论文。

---

## 4. 实验与证据续：六大难题（§5，Table 3）—— 最长的一章 🔥

作者刻意**排除**单 agent 也有的问题（稀疏奖励、探索-利用）。**非平稳和规模**在所有设定里都有；**信用分配、协调、通信**主要在合作设定里。

### 4.1 非平稳（§5.1）

天真做法：无视别人，当独立学习者。**简单确定性环境里能行**（Tan 1993、Claus & Boutilier 1998），**复杂或随机环境里通常很差**；还会**过拟合到训练时队友的策略**、测试时泛化失败（Lanctot 2017）。

| 路线 | 机制 | 代表 |
| --- | --- | --- |
| **经验回放** | 回放里的旧样本过时了 → ① 衰减旧样本 + **重要性采样**纠正 off-policy；② 给状态加上其他 agent 策略的估计——**fingerprint**（让价值函数知道数据"有多老"） | Foerster 2017 |
| 经验回放 | **leniency**：每个样本一个随访问次数衰减的温度 | Palmer 2018 |
| **集中训练** | 集中式 critic（每人一个 / 全队一个）；价值分解 | MADDPG、COMA、QMIX |
| **元学习** | 把非平稳看成**一串平稳任务**，学会利用相邻任务间的依赖 | Al-Shedivat 2018 |
| 元学习 | 学会**给别的 agent 建模**并预测其未来动作 | Rabinowitz 2018 |

⭐ 脚注 5：fingerprint 的灵感来自 **Tesauro 2004**——把其他 agent 策略的估计作为条件，这个想法比 deep RL 早十年。

### 4.2 学习通信（§5.2，Figure 3）

agent 不仅要决定**说什么**，还要决定**什么时候说、对谁说**。通信能同时缓解非平稳（知道别人做了什么，环境就平稳了）、协调、部分可观测。标准框架是 **dec-POMDP**。

| 寻址方式 | 机制 | 代表 |
| --- | --- | --- |
| **广播** | 每条消息发给所有人 | **RIAL**（DRQN + 独立 Q 学习 + 参数共享）、**DIAL**（离散通道松弛成可微，集中训练）——Foerster 2016；**CommNet**（纯连续协议，Sukhbaatar 2016）；**BiCNet**（双向协调，StarCraft 里协调异质 agent，Peng 2017） |
| **定向** | 用 **attention** 决定何时、说什么、对谁 | **ATOC**（只在需要时、只对一组 agent 发；**选择性是它胜过 CommNet 和 BiCNet 的原因**，Jiang & Lu 2018）；**VAIN**（CommNet + attention，Hoshen 2017）；**TarMAC**（Das 2019）；**IC3Net**（混合设定，**门控机制**可以挡掉来信，Singh 2019） |
| **网络化** | 只和邻居通信 | Zhang 2018（与邻居共享 critic 信息）；**NeurComm**（交通信号控制，降低排队长度和路口延迟；**空间折扣因子**稳定训练，Chu 2020） |

> *"They argued that attention is essential for large-scale settings because agents learn to decide which information is most useful for decision-making."*

🔑 **从广播到定向，是 MARL 在 2016→2019 年学到的最可迁移的一课：规模一大，"说给所有人听"就输了**。↔ Landscape 里横向架构的闲聊、MetaGPT 的 publish-subscribe；↔ W6 Act VIII 的"模型看见多少工具是一个策略，不是默认值"。

### 4.3 协调（§5.3）

协调失败的典型形式：**action shadowing**——一个 agent 的探索行为干扰了另一个的搜索空间，导致找到次优解。

三条路（本节只讲**不靠通信**的）：

| 路线 | 机制 | 代表 |
| --- | --- | --- |
| **独立学习者 + 乐观** | **Hysteretic Q-learning**：**两个学习率**，涨的时候快、跌的时候慢（乐观），对抗随机性造成的高估 | Matignon 2007 |
| 独立学习者 + 乐观 | **Leniency**：早期探索多时宽容，常访问的状态-动作对逐渐不宽容 | Panait 2006 |
| **给他人建模** | 两个网络：一个捕捉对手策略、一个估对手 Q 值 | He 2016（DRON） |
| 给他人建模 | 策略更新**考虑自己对别人学习的影响**；用最大似然从轨迹推对手参数 | Foerster 2018a（LOLA） |
| 给他人建模 | 估计别人的**隐藏状态**嵌入自己的策略 | Raileanu 2018 |
| 给他人建模 | 用所有公开观察算**公共信念** | Foerster 2019（BAD） |
| 给他人建模 | 学一组对手模型 + **切换机制**，应对快速变化的对手 | Everett & Roberts 2018（SAM） |
| **层级** | 高层协调、低层技能；高层控制器引导，每步只和**一个**其他 agent 通信 | Kumar 2017 |
| 层级 | options 框架 + **动态终止条件**，可以中途退出 option 应对别人的变化 | Han 2019 |
| 层级 | feudal 两层，层级靠**奖励**而非状态目标 | Ahilan & Dayan 2019 |
| 层级 | 多时间尺度表示，混合合作竞争 | Jaderberg 2019（FTW） |

🔑 建模他人还有一个副作用：**一旦知道别人的行为，原本说不清的转移就能归因到具体的人，环境又变回平稳的了**。协调和非平稳是同一个问题的两面。

⚠️ 层级方法的开放问题：**从数据中自主发现抽象目标**（Schaul 2015、Vezhnevets 2017）。

### 4.4 信用分配（§5.4）

即使完全可观测，看不到联合动作也很难判断谁贡献了什么。Claus & Boutilier 1998：独立学习者**甚至在简单的 bi-matrix 博弈里都分不清"队友在探索"和"环境有随机性"**。RL 的序列性让它更难——要评估的是一整串动作。

| 路线 | 方法 | 机制 | 分解的约束 |
| --- | --- | --- | --- |
| **分解** | **VDN**（Sunehag 2018） | Q_tot = Σ Q^i | **线性** |
| 分解 | **QMIX**（Rashid 2018） | 非线性组合，Q_tot 对每个 Q^i **单调** → 每个人各自 argmax 就能得到联合最优 | **单调** |
| 分解 | **QTRAN**（Son 2019） | 去掉线性和单调假设，允许任意非线性组合 | **任意** |
| **边缘化** | **COMA**（Foerster 2018b） | 集中 critic 算**反事实基线**：把我的动作换成别的、其他人不变，回报差多少 | — |
| 边缘化 | Nguyen 2018 | mean collective actor-critic，降梯度方差 | — |
| 边缘化 | 与 **difference rewards**（Tumer & Wolpert 2004）同源 | 我的动作 vs 所有人平均奖励 | — |
| **逆强化学习** | Lin 2018 | 从专家示范**反推奖励函数**；多 agent 能恢复与真值相关的奖励 | — |
| 模仿学习 | Yu 2019 | 从示范恢复每个 agent 的专家策略 | — |

🔑 **VDN → QMIX → QTRAN 是一条"放松约束"的线**：线性 → 单调 → 任意。越放松表达力越强，越难保证"各自 argmax = 联合最优"。这是 MARL 里最清楚的一条进化线，值得记三个名字和三个约束。

🔑 **COMA 的反事实基线**问的是"如果我刚才做了别的，团队会差多少"——这正是 Landscape 里 DyLAN"按贡献淘汰 agent"应该问、却交给 LLM 主观打分的那个问题。

### 4.5 规模（§5.5）

**每多一个 agent，计算量指数增长**；还要求对别人的策略变化鲁棒。

| 路线 | 机制 | 代表 |
| --- | --- | --- |
| **知识复用：参数共享** | 同质 agent 共用网络，可扩展到任意数量 | Gupta 2017 |
| 知识复用：迁移学习 | 知识库提取相关任务旧解；agent 当学生向老师请教，**同时学习的 agent 互相建议** | Da Silva & Costa 2017；Da Silva 2017 |
| 知识复用：**课程学习** | **从少量 agent 开始，训练中逐渐加人**；更好的泛化、更快收敛 | Gupta 2017、Long 2020、Narvekar 2016 |
| 知识复用：自动课程 | agent 自动生成课程；竞争中形成**军备竞赛** | Sukhbaatar 2017、Baker 2020（捉迷藏） |
| **降复杂度：平均场** | 和大量 agent 的交互 ≈ 和**邻居平均影响**的交互，拆成 agent-邻域的成对交互 | Yang 2018b |
| 降复杂度：因子分解 | 联合 Q 拆成独立分量 + 成对交互 | Chen 2018 |
| **鲁棒性：正则化** | 策略集成（每个 agent 训练多个子策略）、对策略混合做 best response | Lowe 2017、Lanctot 2017 |
| 鲁棒性：对抗训练 | 环境里加一个**专门捣乱**的对抗 agent | Pinto 2017 |
| 鲁棒性：**self-play** | 和旧版本的自己对打 | Heinrich & Silver 2016、OpenAI Five、AlphaGo |

⚠️ **Gleave 2020** 的反例：self-play 训出来的复杂策略，**会被看似随机、不协调的简单策略打败**；**观察空间维度越高，越容易被对抗攻击**。

### 4.6 部分可观测（§5.6）

dec-POMDP **计算上很难**（Bernstein 2002），面对真实世界复杂度**仍然不可解**（Amato 2015）——但视频游戏（StarCraft、Dota、捉迷藏、Quake）上已有不错结果。

两条路：**通信**（把本地观察传给别人；ATOC 学会**按需**而非固定频率通信）和**记忆**（DRQN 等循环网络；BAD 的公共信念）。

> *"A severe concern in MADRL is that the memorization of past information is exacerbated by the number of agents involved during the learning process."*

---

## 5. 失败模式与局限

### 5.1 MARL 的失败模式（收拢全文）

| 失败模式 | 原文怎么说 | 🔑 更一般的问题 |
| --- | --- | --- |
| **移动靶** | 别人在学，我看到的环境在变 | 学习对象和评估标准同时在变 |
| **相对过泛化** | 选了"和谁搭都还行"的次优均衡 | **求稳的平庸**：局部最优被结构性地偏好 |
| **lazy agent** | 一个学好了，另一个没动力学（甚至学了会拖累第一个） | 共享奖励下的**搭便车** |
| **过拟合到队友** | 独立学习者过拟合训练时的队友策略，测试时泛化失败（Lanctot 2017） | 换了队友就不会玩 |
| **action shadowing / 协调失败** | 我的探索污染了你的搜索空间 | 探索的外部性 |
| **对抗策略** | 复杂策略被简单的怪招打败（Gleave 2020） | 鲁棒性不随能力自动提升 |
| **分不清队友探索和环境随机** | Claus & Boutilier 1998 | 信用分配的最小例子 |

### 5.2 领域的局限（§6 开头，作者自己说的）

- **相对过泛化 + 奖励随机性，连表格世界都还没解决**
- **可复现性**：单 agent 领域已经证明超参数、随机种子数、代码库对结果影响巨大（Henderson 2018），**作者提醒多 agent 很可能一样**
- **没有统一 benchmark**：环境很多（DeepMind Lab、Malmo、ML-Agents、StarCraft…），但**没有一个像 OpenAI Gym 那样**统一接口、能公平比较的

### 5.3 ⭐ 埋起来的洞察（从表里挖的）

- ⭐ **Table 4：CTDE 一个趋势覆盖了 5 个难题**（非平稳、协调、部分可观测、信用分配、规模），六个里**只差"通信"**。另外三个趋势：课程学习 → 规模（1 个）；记忆 → 非平稳、部分可观测（2 个）；通信 → 非平稳、协调、部分可观测（3 个）。**这张小表比正文任何一段都更能说明为什么 CTDE 是主流**。
- ⭐ **Table 3 的文献分布很不均**：知识复用、鲁棒性、建模他人三行各列了 **15** 篇；部分可观测只有一条路线（记忆），列 **5** 篇。可是作者在 §5 开头说部分可观测是"omnipresent"的问题之一。**最普遍的问题，解法最单薄**。
- ⭐ **§5 刻意排除了稀疏奖励和探索-利用**（单 agent 也有的问题）。但 §4.1 又用内在奖励讲了稀疏奖励，§2 讲了 alter-exploration。边界划得不完全干净。
- ⭐ 作者在 §5 开头承认：*"Much of the surveyed literature cannot be assigned to one particular but rather to several of the proposed challenges. Hence, we associate the subsequent literature to the one challenge which we believe best addresses it"*——**Table 3 的分类是作者主观归的，一篇论文只进一格**。COMA 同时解非平稳和信用分配，在表里只能出现在一个位置（实际上它出现在两行，见下 ⚠️）。

### 5.4 ⚠️ 论文内部的不一致

**⚠️ ① lazy agent 的病因放了两个地方。**
§3.2：lazy agents *"may occur in the CTCE setting"*——归因于**集中执行**。
§5.6：*"An additional difficulty elicited by partial observability is the lazy agent problem which can occur in cooperative settings"*——归因于**部分可观测**。
两处引的都是 Sunehag 2018。合理的读法是：lazy agent 是**共享奖励 + 无法归因个人贡献**的结果，CTCE 和部分可观测只是两种触发条件——但论文没这么说。**所以它其实是信用分配的症状**，却没出现在 §5.4。

**⚠️ ② "N × N 矩阵"的记号冲突。**
§2.2 说 strategic-form game 叫 matrix game *"because the reward function is represented by an N × N matrix"*。但 Def 2 里 **N 是 agent 个数**。一个 N 人博弈的收益是 |U¹| × ⋯ × |U^N| 的**张量**，不是 N×N 矩阵；只有两人博弈才是矩阵（行列数是各自的动作数）。

**⚠️ ③ 部分可观测的框架名前后不一。**
Def 8 定义的一般框架是 **POMG**；§5.6 却说 *"the common frameworks that deal with partial observability are POMPDs for general settings"*（还拼成了 POMPD）。单 agent 的 POMDP 和多 agent 的 POMG 被混用了。

**⚠️ ④ 同一篇论文在 Table 3 出现多次，"一篇只进一格"并不成立。**
Foerster 2018b（COMA）同时出现在：非平稳 / 集中训练、协调 / 独立学习者、信用分配 / 边缘化、部分可观测 / 记忆——**4** 行。和 ⭐ 第四条里作者说的"归到最合适的一个"矛盾。

**⚠️ ⑤ Table 3 网络化通信那一行写了两次 "Chu et al. (2020)"**——参考文献里确实有两篇 2020 年的 Chu et al.（一篇 ICLR 的网络化控制、一篇 IEEE T-ITS 的交通信号），但没有用 2020a / 2020b 区分，读者无法知道表里分别指哪篇。

---

## 6. 在 agent 谱系里的位置

和 vault 里**已读过**的论文并排：

| 论文 | agent 是什么 | 怎么变好 | 多 agent 怎么协作 | **有没有 verifier / ground truth** |
| --- | --- | --- | --- | --- |
| **本篇** MARL 综述 | 训练出的策略网络 | **reward 更新权重** | 环境里的动作 + 学出来的通信 | ✅ **reward 就是 ground truth**（每篇原论文自己的环境） |
| [[Landscape of AI Agent Architectures 论文精读笔记\|Landscape]] `2404.11584` | prompt 出的 LLM | 改 prompt / 改编排 | **自然语言对话** | ❌ 综述本身无数据 |
| MAST `2503.13657`（阅读清单） | prompt 出的 LLM | — | 自然语言 | ✅ 人工标注失败 |
| [[Generative Agents 论文精读笔记\|Generative Agents]] | prompt 出的 LLM | 记忆 + 反思（不改权重） | 自然语言，**社会情境**里自发涌现 | ❌ 只有 believability |
| [[Voyager 论文精读笔记\|Voyager]] | prompt 出的 LLM（单） | 技能库（程序性记忆） | — | ✅ 环境判定 |
| [[RLVE 论文精读笔记\|RLVE]] | LLM（单） | **RL 改权重** | — | ✅ 程序判分的环境 |

**MARL 难题 → LLM 多 agent 里的样子**——这是本周两篇放在一起读的意义：

| MARL 难题 | LLM 多 agent 里的对应物 | 🔑 |
| --- | --- | --- |
| **非平稳** | 每个 agent 的 prompt / 上下文在对话中不断变；别人说了什么改变了我该做什么 | LLM 不改权重，但**上下文就是它的"策略"**，同样是移动靶 |
| **通信**：广播 → 定向 | 横向群聊 → MetaGPT 的 pub-sub / 消息过滤 | **同一个结论，早了 6 年** |
| **协调**：建模他人 | leader 漏传信息时，下属不知道 leader 知道什么 | 缺的是"心智理论" |
| **信用分配** | DyLAN 按贡献淘汰；多 agent 出错时**到底是谁错了**（MAST 的标注难点） | MARL 有反事实基线可算，LLM 只能让另一个 LLM 主观评 |
| **lazy agent** | 讨论里"附和派"：同意别人、自己不贡献 | 共享目标下的搭便车 |
| **相对过泛化** | 多 agent 讨论收敛到"大家都能接受"的平庸方案 | **求稳的均衡** |
| **规模**：维度灾难 | 每多一个 agent，多一份上下文、多一次交接（"把 harness 问题乘 N 倍"） | |
| **规模**：课程（从少量 agent 开始） | 先用满一个 agent，按测到的瓶颈再拆（W5 Tools Prelude p.21） | 同一个工程建议 |
| **CTDE** | 训练时有特权信息的老师 = RLVR 的 verifier / 评估时的隐藏测试 | 课程 capstone（RLVR）的直接祖先 |

最后一句：**这篇不是 LLM 多 agent 的方法来源，而是它的问题清单**。LLM 多 agent 的每一个坑——闲聊、搭便车、谁的锅、平庸共识——在 MARL 里都有名字、有形式化定义、有至少一种算出来（而不是让 LLM 评出来）的解法。读 Landscape 和 MAST 时卡住了，回这篇查名字。

---

## 7. 批判性分析

### 论文自己承认的

§6 开头和 §6.2：表格世界里的病还没治好；可复现性；没有统一 benchmark；异质场景研究太少；维度灾难。

### 我自己补的

1. **没有一个数字，无法回答"哪个更好"。** 全文 49 页，没有一张横向比较表（哪怕是"在 SMAC 上 QMIX 比 VDN 高多少"这种各原论文都报过的数字）。作为入门地图够用，作为选型依据不够。一篇综述可以不做实验，但应该**汇总原论文的数字**——Henderson 2018 的可复现性警告恰好说明为什么汇总时要标出环境和种子数。

2. **对合作场景严重偏重，而作者自己说异质场景最重要。** §6.2 说异质性是两大最难问题之一、*"Limited research has been conducted in heterogeneous scenarios"*；可是 §5 的六个难题里，信用分配、协调、通信三个**主要在合作设定**，讨论通信的标准框架 dec-POMDP 本身就是完全合作的。综述的结构复制了它批评的领域偏差。

3. **"涌现"一章缺乏怀疑。** Lewis 2017 的"学会欺骗"、Mordatch & Abbeel 的"学出句法"、Lazaridou 的"可解释性有限但令人鼓舞"——这些都是**作者自己对 agent 行为的解读**，没有 ground truth。作者引了 Lowe 2019 说数值表现不等于通信能力，但没有用这个标准回头审视 §4 的论文。↔ 和 Generative Agents 的问题同构：只能主张 believability。

4. **安全只占一句话。** §6.2 把 safe MADRL 列为未来方向，说它"still in its infancy"。但**对抗策略**（Gleave 2020）已经在 §5.5 出现了——一个训好的策略能被简单怪招打败，这本身就是部署安全问题，作者把它归到了"鲁棒性"而不是"安全"。↔ W6 Act X：盒子 fail open，恰恰发生在本该强制的地方。

5. **时效：它停在 LLM 前夜。** 2021 年发表时，MADRL 的代表成果是 StarCraft、Dota、捉迷藏、Quake——全是游戏。五年后多 agent 的主战场变成了 LLM 编排，而那里几乎不训练。这不是作者的错，但读的时候要知道：**方法部分（QMIX、MADDPG）对今天的 LLM agent 不直接可用，问题部分（§2.3、§5 的病名）仍然完全适用**。↔ W6 Interlude："原理是养老金，表面会腐烂"。

6. **值得做的复现 / 迁移实验**：把 COMA 的反事实基线思路搬到 LLM 多 agent——对一个 3-agent 讨论的最终答案，**依次把每个 agent 的发言替换成空、其他不变**，重跑看答案质量下降多少，用这个下降量做"贡献"。对比 DyLAN 式的 LLM 主观打分，看两者排序是否一致。如果不一致，说明 LLM 打分的信用分配不可信。

---

## 8. 复习自测题

1. Markov Game 的元组有哪几个元素？和 MDP 相比，哪两处是"每个 agent 各一份"？
2. agent i 的价值函数为什么写成 V^i_{π^i, π^{−i}}？这一个下标改动导致了哪个难题？
3. relative over-generalization 是什么？为什么它在合作场景里会让 agent 偏好次优均衡？
4. CTCE、DTDE、CTDE 各自的定义是什么？哪一个被作者称为 state-of-the-art？CTCE 的两个主要毛病是什么？
5. MADDPG 和 COMA 都用集中式 critic，区别在哪？（critic 的数量、critic 算的是什么）
6. VDN、QMIX、QTRAN 对联合 Q 和个体 Q 的关系分别做了什么约束？QMIX 的约束为什么能保证"各自 argmax = 联合最优"？
7. Hysteretic Q-learning 用了几个学习率？分别用在什么时候？要解决什么问题？
8. Foerster 2017 为经验回放提出的两个办法是什么？fingerprint 的灵感来自哪一年的哪篇工作？
9. 通信按寻址分三类，各举一个代表方法。ATOC 胜过 CommNet 和 BiCNet 的原因是什么？
10. Mordatch & Abbeel 2018 用哪两个条件让 agent 收敛到一致的词汇？
11. Table 4 里哪个趋势覆盖的难题最多？覆盖了几个？唯一没覆盖的是哪个？
12. Gleave 2020 发现了什么？作者把它归到了哪个难题下？
13. lazy agent 在这篇综述里被归因到哪两个不同的地方？你认为它更应该归到哪个难题？
14. 作者认为最难的两个问题是什么？
15. 把 Landscape 综述里 MetaGPT 的 publish-subscribe 对应到本篇的哪类通信？把 DyLAN 的按贡献淘汰对应到哪个难题、哪个方法？

---

## 9. 核心数字速查表

| 项目 | 数值 |
| --- | --- |
| 发表 | *Artificial Intelligence Review* (2022) 55:895–943；2021-04-15 在线 |
| 页数 | 49 |
| 参考文献 | 约 237 条（脚本粗数） |
| 编号定义数 | 12（Def 1–12） |
| 三刀 | 训练方案 / 涌现行为 / 六大难题 |
| 训练方案 | 3 种：CTCE、DTDE、CTDE |
| 涌现行为分类 | 3 类：奖励结构、语言、社会情境 |
| 多 agent 专属难题 | 6 个：非平稳、通信、协调、信用分配、规模、部分可观测 |
| 趋势（Table 4） | 4 个：课程、记忆、通信、CTDE |
| CTDE 覆盖的难题数 | 5 / 6（缺通信） |
| 通信 / 课程 / 记忆覆盖的难题数 | 3 / 1 / 2 |
| 最难的问题 | 2 个：异质性、维度灾难 |
| 折扣因子范围 | γ ∈ [0, 1) |
| Markov Game agent 数 | N > 1；bi-matrix 博弈 N = 2 |
| Mordatch & Abbeel：参与对话 agent 数 | 超过 3 个 |
| 社会困境的心理变量 | 5 个 |
| Hysteretic Q-learning 学习率数 | 2 |
| Table 3 文献最多的三行 | 知识复用 / 鲁棒性 / 建模他人，各 15 篇 |
| Table 3 部分可观测（记忆）行 | 5 篇 |
| COMA 在 Table 3 中出现的行数 | 4 |
| 关键年份 | Littman 1994（Markov Game）· Claus & Boutilier 1998 · Tesauro 2004（fingerprint 灵感） |

---

*笔记据 Artificial Intelligence Review 2022 正式版 PDF（DOI 10.1007/s10462-021-09996-w）全文 49 页。§6 的「MARL 难题 → LLM 多 agent」对照表、§5.3 ⭐ 的统计、§7「我自己补的」均为笔记作者补充，非论文原文内容。参考文献条数为脚本按格式粗数，可能有 ±5 误差。*
