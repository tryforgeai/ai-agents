# Week 07 Lesson Plan 精读 · Gradient Descent for Sentences

来源：[`uploads/fall-agents-week-7-lesson-plan.pdf`](uploads/fall-agents-week-7-lesson-plan.pdf) — *Fall Cohort — Week 7 Lesson Plan: Gradient Descent for Sentences — the Workshop, the Frontier and the Tether*
作者：Asif Qamar · SupportVectors · 初稿 2026-10-27 · 正文 32 页（PDF 34 页）
日期：2026-11-01（上课当天，课前精读）

> 本文是**逐节精读**，补齐 [`lesson-plan.zh.md`](lesson-plan.zh.md)（听课速览）压缩掉的内容：完整公式与算例、所有数字、GEPA 七步循环、frontier 手算、DSPy 代码、优化器对照表、文献。
> 页码为**印刷正文页码**（= PDF 页序 − 2）。
> 🧭 标「我的接线」的段落是我自己加的联想，不是讲义原文。
> ⚠️ 讲义说 debrief（14:30）会揭晓每个 bench / door 在文献里的名字，**讲义里没印**——本文不猜，留空等课上补。

---

## 扉页上的两句话（p.1）

> **"Ever tried. Ever failed. No matter. Try again. Fail again. Fail better."** — Samuel Beckett, *Worstward Ho*
>
> **"When a measure becomes a target, it ceases to be a good measure."** — Goodhart's law（Marilyn Strathern 的表述）

第一句是**循环**（GEPA 的 loop），第二句是**警告**（metric 被最大化就会变形）。整天就是这两句的张力。

---

## A Gentle Re-Entry（p.1–2）

### 上周回顾（Week 6）

十二扇门、Stranger's Toolbox：每扇门的工具 label 用一种方式误导 agent——**clarity、scope、politeness、trust**。固定动作：predict → play → read the trace → rewrite the label → verify → serve 到 Hermes。带走的东西：

- 一份 tool description 的 rubric
- **$50 退款付了两次**，以及本可阻止它的 idempotency key
- **stateless river**：模型是函数，harness 负责记忆
- **castle 先有墙后有塔** → 细节在自学材料 *No Castle Without Walls*

课前复述题（边注）：**说出 tool label 必须告诉模型的五件事**。每一条都是模型每轮都读的一句话——一个 prompt。**今天这个 prompt 从「被打磨的东西」变成「被搜索的东西」。**

> 🧭 我的接线：Week 6 的答案 = description / schema / error / contract 四站 + 返回值（第五面）。见 [Week 06 lesson-plan](../ai-agents-week-06/lesson-plan.zh.md)。

### 课程的上半场结束了

prompt 在前六周的四种形态：**Week 2 手写** → **Week 3 打包成 procedure（skill）** → **Week 5–6 伪装成 tool description**。上周结尾的承诺："**Now we'll go from lower-division to upper-division.**"

upper-division 的第一个问题：***can a machine write it better than I can?* Sometimes** —— 今天大部分时间在讲「什么时候」。

### 三颗之前埋下、今天发芽的种子

| 周 | 种子 | 今天变成 |
| --- | --- | --- |
| **W2** · Literal Genie + Goodhart | "Get our test coverage to 100%" → 机器照字面实现，写出**什么都不 assert 的测试** | 精灵**拿到了一台搜索引擎**，还要参加**你出的考试**（Genie's Exam） |
| **W3** · Harrison's clocks + 糖果店 | H1→H4 每台都证明上一台不完整；**Maskelyne = 需要被评判的评判者**。糖果店：糖 2 paise、éclair 25 paise、孩子有 2 卢比——"Pareto 前沿上的点：改进一个目标就必须牺牲另一个" | **前沿回来了，坐标轴换了标签**（见 GEPA：坐标是 instance 不是 objective） |
| **W6** · introns + 人类草稿 | DSPy 问答："Genetic approaches have a problem. They produce **introns**" —— 优化后 prompt 里**细看毫无意义**的子句，或只是**碰巧在 demo 里成立**的输入输出关系 | 治法 = 一种节奏："人写好草稿 → 机器改进 → **仍当草稿，人再改** → 跑 eval → 重复" |

W6 同一个下午还有一个问题预演了今天：一个网络为了把 loss 压到 0，把所有 embedding 塌缩成同一个向量——"**The machine has essentially found a loophole in your loss function. Do you see a resonance of that to prompting?**"

### 今天要带走的那一句（p.2，p.9 框内重复）

> **A prompt is a parameter — a point in a discrete space with no gradient — and prompt optimization is search over that space, steered by a pseudo-gradient written in words. The optimizer is only ever as good as the metric it is handed.**

拆成三段记：
1. **prompt = 参数**（离散空间里的一个点，没有梯度）
2. **优化 = 搜索**，方向靠「**用文字写出来的伪梯度**」
3. **底下的警告**：优化器的上限 = 你给它的 metric

---

## 全天路线图（p.3，图 1）

**第一个按「循环」而不是按「主题顺序」组织的周日。**

```
Orientation ─ Harrison's ─ Steam ─ Genie's ─│─ Deep Dive ─────── Owl of ─ Speakeasy → 下周: memory
  11:00       Workshop     Drill    Exam    │   14:30              Minerva    20:00
              12:00        13:35    13:45   │  (橙色栅栏)          19:30
 上周 Owl、   十张 bench； 全场一块  三翼    │  最重要的先讲；       五行       可选；
 小测、field  午饭在 bench  屏幕     九门    │  底部开放             带走       停车板问题、两条 walk
 notes、六条
 headlines   └──── Cycle 2 · experientials，按设计 150 分钟 ────┘
```

---

## What Must You Carry Forward（p.3–4）· 十二条学习目标

下课时应能**不含糊地**做到：

1. 说出**那一句**，并说清参数 **θ = (π, δ)** 里装了什么、**什么是冻结的**（→ 权重冻结）
2. 说出**三个诅咒**——**离散且巨大、有噪声、昂贵**——以及每个诅咒淘汰哪种经典工具
3. 解释「**用文字写的伪梯度**」，并**念出这个比喻应得的墓志铭**（→ 真梯度是 local / linear / directional / consistent，文本梯度一样都不是）
4. 用三课讲 field notes——**苦活是数据、思考是 metric、保险是 tether**——并说出三课之前的那个 **gap**（→ resolution gap）
5. 用**七步**写出 **GEPA 的循环**；说出 **feedback pool** 和 **Pareto pool** 各自干什么，以及**为什么接受分两阶段**
6. 说出**核心纠正**——**frontier 是在训练 instance 上，不是在 objective 上**——手算一个小 frontier，说出 **2026 年 10 月的库**加了什么（→ 四种 frontier 类型）
7. 写一个**会说话的 metric**：分数 + 反思模型能据以行动的文本
8. **三分**数据——**burned、pressured、clean**——说明为什么只有 held-out 数字（**跨 seed、分 slice**）可信
9. 说出 **judge 的病理**，并引用那个说明 judge 需要 rubric 的数字（→ 46.4% vs 73.8%）
10. 用**机制**解释 **intron**，以及优化之后那次**人工编辑**是干什么的
11. **把优化器匹配到 artifact**——紧凑 prompt / 增长的 playbook / skill 文件 / 决策阈值 / 分解结构——并说出关于 **elitism** 的那场未决争论
12. 说出**什么时候不该优化**，带上 **coin-flip 结论和它的限定条件**

> 做到这些，就可以进下周：**一个「增长而不是压缩」的 playbook，最后会变成一个关于记忆的问题。**

---

## How the Day Runs, and Why（p.4–5）

### 为什么改成循环

旧方式：从第一个主题讲起，钟停在哪就讲到哪——**最后那个主题通常最难，也通常是最新的学员最需要的**。循环日倒过来：

| Cycle | 名字 | 设计意图 |
| --- | --- | --- |
| 1 | **Orientation** | 先把**整个论证讲一遍**，只有故事和 headlines，**没有机制**。上周 Owl + 小测 *Six Questions, One Trap*。**小测放在开头**：一周后在一点压力下回忆，才是固化记忆的东西——"**it is a verifier, and it will make you laugh**" |
| 2 | **Experientials** | 在任何人命名之前先让论证落到手上：Workshop → Steam Drill → Genie's Exam 连着来。**本周 150 分钟，按设计**：做中学的东西比听来的持久 |
| 3 | **Deep Dive** | **前端有栅栏**：不管上午怎样，**14:30 准时开始**；**底部开放**：按重要性往下讲，钟咬到的是**最不重要的尾巴** |
| 4 | **Owl of Minerva** | **固定 19:30** |
| 5 | **Speakeasy** | 20:00 后，可选，**没有承重内容** |

> 🧭 我的接线：这本身就是一个设计模式——**把不可压缩的东西放在固定时间点，把可压缩的放在尾部**。和 W6 讲的「落后时砍什么、不砍什么」是同一个思路，只是这次写进了结构。

### 两个习惯

- **Parking Board**：值得更多时间但当下塞不下的问题 → 扫幻灯片上的 QR 贴上去；白天可以互相回答；Speakeasy 从房间没解决的问题开始
- **Reservoir**：配套讲义 `fall-agents-week-7-reservoir.pdf`，**十二个编号章节**，形式同上周的安全自学。下面每段 refresher 都标了深度在哪一节。"**Nothing is silently dropped.**"

### 当天时间表（p.5，表 1）

| 时间 | Cycle | 内容 | 形式 |
| --- | --- | --- | --- |
| 11:00–11:05 | Orientation · 上周 Owl | Week 6 的五行，一页 | Deck |
| 11:05–11:25 | Orientation · 小测 | *Six Questions, One Trap*；**只重讲房间答错的** | Quiz |
| 11:25–12:00 | Orientation · 故事 | field notes（无机制）；六条 headlines；那一句 | Deck, story |
| 12:00–13:35 | **Harrison's Workshop** | 午饭前配对；core path（**Bench 2, 4, 7, 9, 10**）；**~12:30 在 bench 吃午饭**；Bench 10 等讲师信号；**13:35 前导出** | 两人一组 |
| 13:35–13:45 | **The Steam Drill** | Bench 11，全场同时解锁 | 全体 |
| 13:45–14:30 | **The Genie's Exam** | 同一搭档；core path（**Door A1, A3, B1, C1**） | 两人一组 |
| 14:30– | **The Deep Dive** | 两个 experiential 的 debrief；问题的形式化；GEPA 全貌；纪律；field notes 兑现；优化器配 artifact；综合 | Deck, board |
| 19:30–19:50 | **Owl of Minerva** | 五行，每行带 why；通向下周的桥 | Deck |
| 20:00 后 | *Speakeasy* | 可选：停车板未决问题；code walk 或 paper walk | Talk |

**只有两个时间是固定的：14:30 和 19:30。** 其余随房间弯曲，deep dive 的休息落在房间需要的地方。

> ⚠️ **课上实际议程（deck 首页，11:00）**：Orientation 11:00 → Experientials 12:00 → Deep dive 14:30 → **Guest lecture 17:00** → **Deep dive, continued 18:00** → Owl of Minerva。讲义里**没有** guest lecture；deep dive 被切成 14:30–17:00 和 18:00–19:30 两段，中间少了一小时。按「底部开放、最重要的先讲」的设计，被砍的会是尾部：优化器配 artifact 和综合 → 讲不到就补读 Reservoir §9、§11、§12。
>
> | Guest lecture（17:00） | 课上填 |
> | --- | --- |
> | 讲者 / 主题 | |
> | 要点 | |
> | 和今天主线的接线 | |

### 给「做决定而不是动手」的人（p.5 框）

Orientation 就是写给你的：**field notes + 六条 headlines = 整个论证**，零代码。能留就留到 experiential，**尤其是 Genie's Exam**——当 45 分钟「一台照你考试复习的机器」的考官，是最快体会「"更好"需要先有 rubric，机器才能追」的方式。14:30 后的 debrief、纪律、优化器对照表回答的正是你会被问的三个问题：

> ***Should we optimize this prompt, with what, and how will we know it worked?***

> 🧭 我的接线：这三个问题可以直接当成我在 Rakuten 评审任何「我们上 DSPy/GEPA 吧」提案时的 checklist。

---

## Before You Arrive（p.5–6）

### 两个新 kit

- 从 portal 本周 experiential 栏下载 **`harrisons-workshop.zip`** 和 **`genies-exam.zip`**，**各解压到独立文件夹**
- 每个 README 给出**一条命令**在浏览器里打开 kit，并说明 OpenRouter key 放哪；**第一次运行会装好一切**
- 确认两个都能打开——**然后课前不要打开任何 bench 或 door**
- 两个 kit 都能**不用 key 回放预录输出**，用来跟课
- 每桌两张打印卡：**workshop card**（`workshop-card.pdf`）和 **exam card**（`exam-card.pdf`），写着标题、core path、规则；远程学员在 portal 上拿

边注：**周日不需要再装别的**。deep dive 里的代码是**拿来读的**；周二、周四的 session 才是跑代码的地方。

### Week 6 的两个尾巴

1. 如果你的 `strangers-toolbox.zip` **早于 10 月 26 日**，重新下载：**Door 1 的 verification 现在会回应一个「主动提出给店内积分然后等待」的 agent**——这正是房间里争论出的「好 agent 该做的」
2. 还没读 ***No Castle Without Walls*** 的这周读；它的答疑轮在周二、周四

### 搭档

**中午、食物送到之前选定搭档**，两个 experiential 都不换。**一台电脑两人用就够，而且常常更好。** 远程学员在 breakout room 配对，用同样的 kit。

---

## Cycle 1 · Orientation：The Field Notes（p.6–7）

> 一整个故事，**先讲、讲完整、不带机制**。来自给一家大型企业客户做的生产系统；**能识别客户的东西（名字、日期、确切数量）都刻意删掉了，对课有用的一样没删。**

### Many problems wearing one prompt

- **任务**：读一份产品文档，判断它触发了**几十种**合规风险中的哪几种。漏掉一个风险**不是统计数字，是事故**
- 客户工程师**做了好几年**：一个精心手写的 prompt **同时覆盖所有风险类型**，**从来没好到可以信任**
- **修复不是从优化器开始的**，是从「**把它们看成很多个**」开始的：一个 prompt 管几十种风险 = 把几十个问题压扁成一个，压扁后的问题**藏起了自己的结构**——每种风险的定义、它的代价、它被漏掉的方式
- 失败**不是能力 gap**（模型做得到），是 **resolution gap（分辨率 gap）**

边注："**Keep the phrase.** 当一个本该能用的东西不能用时，**先问你看的是一个问题，还是几个穿着同一身衣服的问题。**"

> 🧭 我的接线：这就是目标 4 里「三课之前的那个 gap」。也和 W3 的 skill 拆分、W6 的 Swiss Knife（一个工具干太多事）是同一种病。

### Three lessons from a few hard weeks

| 课 | 原话 | 要点 |
| --- | --- | --- |
| **The grunt work is the data** | 大部分时间花在 **demonstrations**（风险存在/不存在的样例）上 | 每一条都**人工审过**才给机器看——因为改写 prompt 的机器会**读**它们，**一条错例 = 它写进指令里的一条错误教训**。团队保留了太多版本的参考集，**以至于不确定哪个是真的**：**one blessed set, one owner, every change logged** 本身就是方法的一部分 |
| **The thought is the metric** | 风险不等价时，「它答对了吗？」**不是一个问题** | 最严重的：**漏报远比误报糟** → metric 大幅偏向召回；其他的用平衡 metric 就行。**每种风险一个旋钮**，外加**推理质量**和**指向正确证据**的部分分。**逐个风险设这些旋钮，是项目的智力核心** |
| **The insurance is the tether** | 优化器**照字面**理解你给的 measure | 追分时它会**悄悄删掉专家认为必需的规则**，或写出**听起来像监管语言但毫无意义**的句子——因为分数恰好没惩罚它。解法来自 RL 防止模型偏离起点的做法：**校准规则和风险定义被设为不可改写**，机器可以改写它们周围的一切，**永远不能改它们**。"**A regulator does not grade on a curve.**" |

**结局值得记住**：因为 measure 奖励**认真的推理**、tether 守住了规则，系统给出的解释**认真到客户现在用它来培训新入职的人类员工**。"**Literalness, pointed at the right target and fenced in the right places, produced teaching.**"

边注：这个故事撑起整天——一个还是多个 prompt；搜索；measure 以及它被多字面地读；governor。**三课不只是讲：13:45 它们就是 Genie's Exam 的三翼，你亲手玩**；deep dive 再带着机制回到每一课。

---

## Cycle 1 · Orientation：Six Headlines（p.7–9）

> 六个想法，各一个故事，**还没有机制**。这是地图；下午走它。

### ① A prompt is a parameter

- prompt engineering（W2）是**手工活**：快、可解释、**局部**——"**each of us is trapped in a local optimum of our own linguistic imagination**"
- 墙外有一句标志性的话：给数学应用题找更好的指令时，机器找到了 ***"Take a deep breath and work on this problem step by step,"***，比人写的 "Let's think step by step" **高约 8 个点**（OPRO, Yang et al. 2024, `2309.03409`）。**没人写它，是机器爬出来的**
- **engineering 和 optimization 之间的分界线是一个 metric**——同一个循环，把人从内层迭代里拿掉，换成 **held-out 数据上的一个数**
- 顺序：**手工做到 baseline → 在做的过程中发现「好」是什么意思 → 再把那个 measure 交给机器**

### ② You cannot do calculus on a sentence

- "Can't we just do gradient descent?" prompt 是 token 序列：**没有光滑空间**，**两个好 prompt 的中点不是 prompt**
- **牛和马之间没有光滑路径——给牛加只角，你得到一头 unicow，困在自己的孤岛上**
- 所以改进方向**必须被制造出来**；目前最好的办法：让模型**读自己失败的记录，用文字说出该改什么**。**A gradient written in words.**

### ③ The optimizer reads your metric literally

- **Literal Genie 现在有了搜索引擎**。优化器读分数**像律师读合同，读几千遍**
- loss function 也是 Literal Genie：只要求两个 embedding 匹配，网络就把一切映射到一个向量
- **Introns** = prompt 里的同一种漏洞：无意义的子句，或**编码了优化器见过的样例里的巧合**
- 把它的输出当**草稿**：**人写草稿 → 机器改进 → 人再改 → 测量 → 再来一轮**

### ④ Keep the specialists

- **糖果店换了坐标轴回来了**。不问「哪个 prompt 平均最好？」，问「**哪个在哪个样例上赢？**」
- 一个平均平庸、但**唯独它答对 example 17** 的 prompt，握着别人都没有的东西；因为平均分扔掉它，**example 17 的教训也一起扔了**

### ⑤ Small steps, a memory of failure, a gate

- **Harrison 没有从 H1 跳到 H4**。每台钟修上一台的失败；学到的东西一样没扔，**包括失败的**；最后一台在海上被一场**它从没见过的试验**评判
- 持久的改进往往长这样——**在钟表匠的作坊里，和在一个改写 prompt 的循环里**
- → 三个部件：**小步**（bounded edit）、**失败的记忆**、**闸门**（held-out gate）

### ⑥ Know when not to optimize

- 优化器**只能赢回模型本来就给得出的东西**；否则它空转，有时还**面不改色地递给你一个运气好的失败者（lucky loser）**
- **2026 一项仔细的研究**（Zhang et al., `2604.14585`, *Prompt Optimization Is a Coin Flip*）：**一个模型、六种方法、四个任务、72 次优化运行 → 49% 的运行最后低于起点的 zero-shot prompt**；在**唯一一个**「模型能输出、但默认不输出」的**结构化输出任务**上，**六种方法全部提升**
- **十月关于 judge 的最好数字**（Huang et al., `2605.23899`）：让 LLM 在两个 agent skill 里挑更好的，**无标准 → 46.4%（一枚硬币）**；**给 rubric → 73.8%**

---

## Cycle 2 · Harrison's Workshop（p.10–12）

### 背景（p.10）

Harrison 在工作台前约三十年。每台钟修上一台的失败，**下一台学会之前一台都不扔**。H4 最后在去牙买加的航程上试验，**慢了约 5 秒**；经度委员会的评委**并不公正**——**Nevil Maskelyne 力推一个竞争方法**——Harrison 又花了好几年争论他的钟到底证明了什么（Dava Sobel, *Longitude*, 1995）。

> 🧭 我的接线：Maskelyne = **judge 有自己的立场**。下午「The judge is not an oracle」那节就是这个人的现代版。W3 精读里 H1–H4 的细节见 [Week 03 精读 · Prologue](../ai-agents-week-03/lesson-plan-精读.zh.md)。

**Workshop = 房间用手、慢慢做机器之后几分钟内做完的事。** 结构同上周的 Toolbox：**十张小 bench、四课**，每张有自己的任务、seed prompt 和几条输入，外加**锁着的第十一张**。每张 bench 让你对 prompt **手工做一件事**，然后注意发生了什么。**每张在教什么，14:30 才命名**；在那之前只需要标题。

### 工作台（表 2）

| Bench | 标题（**粗体 = core path**） | 课 |
| --- | --- | --- |
| 1–3 | The Clock That Already Keeps Time · **Many Clocks in One Case** · The Restless Hand | **I. 参数：你在搜索什么** |
| 4–6 | **Write Down Why** · Three Turns of the Screw · The Losers' Ledger | **II. 读失败：用文字写的梯度** |
| 7–8 | **The Specialist on Example 17** · Two Watchmakers | **III. 保留什么：前沿** |
| 9–10 | **Which Is Better?** · **The Sea Trial** | **IV. 「更好」是什么意思，用眼睛判断** |
| 11 | *The Steam Drill* | *锁定。13:35 全场一起开* |

**先走 core path：Bench 2, 4, 7, 9, 10。** 90 分钟到不了十张——**上周也没人走完十二扇门**——但 core path 触及每一课。其余五张做完 core 再做，周日没时间就留给周二/周四。

> 🧭 我的预判（**课前写下，课后对照，不是讲义内容**）：
> - Bench 2 *Many Clocks in One Case* ↔ field notes 的「many problems wearing one prompt」→ resolution gap，可能要求把一个 prompt 拆成多个
> - Bench 4 *Write Down Why* ↔ 「gradient written in words」→ 先写出失败原因，bench 才允许改
> - Bench 7 *The Specialist on Example 17* ↔ instance-wise Pareto frontier
> - Bench 9 *Which Is Better?* ↔ judge 无 rubric 就是硬币
> - Bench 10 *The Sea Trial* ↔ held-out 测试（"judged at sea, by a trial it had never seen"）——用 Bench 2 的最终 prompt
> - Bench 11 *The Steam Drill* ↔ 名字像 John Henry 和蒸汽钻的比赛：人手干了 90 分钟的活，机器（优化器）10 分钟跑完

### 怎么运行（p.11）

- **12:00** 两人一组（午饭前选好，两个 experiential 同一搭档）；远程在自己的 breakout room，同一 kit
- **~12:30** 在 bench 吃午饭
- **快结束时**：**Bench 10 由全场一起玩**，讲师开启；**它用你在 Bench 2 的最终 prompt → 先做完 Bench 2 并保留它**
- **13:35 前**：一键把团队成果导出成**一个 Markdown 文件**（prompts、你写下的东西、记录的决定）。带去 debrief；TA 可能要一份

### 每张 bench 的固定动作

1. **先读 bench**（任务、seed prompt、输入），**运行前**说出你预期 seed 会错在哪
2. 运行 seed，**判断任何一条之前先读完所有输出**
3. **用眼睛判断，并大声用一句话说出为什么。** 说不出一条输出为什么更差，**你就还不知道该改什么**
4. 做 bench 要求的事。有的要决定，有的要写，有的要选或比较；**bench 可能拒绝你的编辑，直到你先做完它要求的事——这个拒绝是 bench 的一部分**
5. **记录，然后往下走。** app 保留每个版本；**不要整理你的历史**

### 规则

- **每次编辑都由人手写。** 同锦标赛和门：chatbot 可以**评论**你的 prompt，**永远不能写下一版**
- **没有分数。** app 显示输出，人来判断。不打分，不排名
- **什么都留着。** 更差的版本仍然是证据
- **只在 bench 要求时才和邻桌合作。** 有一张会要求
- **锁着的 bench 保持锁着。** Bench 11 全场同时开

### 带回 debrief 的问题

> 每队一句诚实的话：***How did you decide "better"?***

---

## Cycle 2 · The Steam Drill（p.12）

**13:35** 讲师为全场解锁 Bench 11。**10 分钟、一块屏幕、自己电脑上什么都不用做。** 像看别人**快速**做你刚花一个半小时手工做的活那样看它，**注意你会怎么做得不一样**。它是两个 experiential 之间的铰链，两边都因它更好懂。

---

## Cycle 2 · The Genie's Exam（p.12–13）

精灵在这门课有连锁店：W2 照字面实现愿望；W3 在 Kitchen 照你的菜谱做饭。**这周它参加考试——并且像所有学生一样，照着考试复习（studies to the test）。** **你是考官**：你要发现你的考试**实际奖励了什么**，然后出一份更好的。

**field notes 在这里是玩出来的，不只是讲**：早上故事的三课 = 考试的三翼；每扇门要你发现什么，debrief 揭晓。

### 三翼九门（表 3）

| 翼 | 门（**粗体 = core path**） |
| --- | --- |
| **A. The thought is the metric**（考试的规则） | **A1 Twelve Words** · A2 The Magic Words · **A3 Out of Ten** · A4 The Board's Rule |
| **B. The grunt work is the data**（考试的题目） | **B1 Tuesday's Child** · B2 The Answer Key · B3 The Question Nobody Set |
| **C. The insurance is the tether** | **C1 The Careful Clause** · C2 Pinned |
| 锁定 | *The Examiner's Answer* —— debrief 时打开 |

**先走 core path：A1, A3, B1, C1**，覆盖每一翼；其余留周二/周四。

> 🧭 我的预判（课前，非讲义）：
> - A1 *Twelve Words*：长度限制类 metric → 精灵会凑字数/截断，满足字面不满足意图
> - A3 *Out of Ten*：LLM-judge 打 1–10 分 → 分数膨胀、verbosity bias
> - B1 *Tuesday's Child*：数据里的巧合（某个特征恰好和标签相关）→ intron
> - C1 *The Careful Clause*：一条必须保留的子句 → 优化器删掉它 → 需要 tether

### 每扇门的固定动作

1. **读考试**：任务 + 精灵被评分的规则/标准。对搭档说你认为考试在要什么
2. **读精灵写了什么、产出了什么**：它**已经照你的考试复习过了**，最好的 prompt 和输出都在眼前
3. **用自己的眼睛读输出**，问考官给的分**有没有意义**。你的考试**实际**奖励了什么？
4. **改该改的**：每扇门给一个短菜单，选一个或自己写
5. **看精灵接下来做什么**，然后决定是否结束

### 规则

- **精灵是真的优化器。** 每次回放都是课前录好的**真实运行**。你自己写的改动**只有配了 key** 才会启动一个小的 live run
- **分数是考官的，不是你的。** app 把考试自己的评判显示在输出旁，**因为精灵在追它，你需要看着它追**。不是你的分数，不排名；**每扇门的问题都是：这个分数值得相信吗？**
- **每次改动都由人手写**
- **每扇门记一行**（exam card 或笔记）：**考试奖励了什么、你改了什么、精灵接着做了什么**

### 带回 debrief 的问题

> 每队一句诚实的话：***What did your exam actually reward?***

---

## Cycle 3 · The Deep Dive（p.14–25）

**14:30 开始，不管上午如何。** 最重要的在前，一直到 Owl：两个 experiential 的 debrief → 问题的形式化 → GEPA 全貌 → 纪律 → field notes 兑现 → 优化器配 artifact → 综合。钟咬到的是尾巴，每段 refresher 都标了 Reservoir 里完整版的位置。

边注：**错过 experiential 的，先玩 core path 再往下读**（Bench 2, 4, 7, 9, 10；Door A1, A3, B1, C1）。

**Debrief 给你做过的事命名。** 带上：导出的 workshop 文件、exam card、两句 carry-back。**每张 bench、每扇门在 prompt 优化文献里都有一个名字**，debrief 逐一说出，配上你在桌上遇到它的那一刻；考试锁着的答案那时打开。**这是今天的揭晓，课前不印。**

### 📝 Debrief 揭晓（课上填）

| Bench / Door | 文献里的名字 | 我在桌上遇到它的那一刻 |
| --- | --- | --- |
| Bench 1 The Clock That Already Keeps Time | **the headroom test** · step zero | （未做）先测有没有提升空间，再决定优化 |
| Bench 2 Many Clocks in One Case | **the resolution gap** · decompose before search | 12 条消息其实是 5 类问题；先分类再改 prompt，v1→v5 |
| Bench 3 The Restless Hand | **the noisy objective** · re-run before you believe | （未做）同一 prompt 跑两次分数不同 |
| Bench 4 Write Down Why | **reflective mutation** · the feedback function µ_f | B 轮每个 not 写一句 why → 规则；v4 Note 5 一句修好 3/4/5 |
| Bench 5 Three Turns of the Screw | **a bounded edit budget** · a learning rate for text | （未做） |
| Bench 6 The Losers' Ledger | **the rejected-edit buffer** · a memory of failure: never repeat it | （未做） |
| Bench 7 The Specialist on Example 17 | **the instance-level Pareto frontier** | A 赢 5 题、B 赢 #15、C 赢 #17（西班牙语）→ 三个都留 |
| Bench 8 Two Watchmakers | **system-aware merge** · module by module | （未做）Bench 7 合并 A+B+C 已体验到 |
| Bench 9 Which Is Better? | **judge pathologies** · position and length sway you | 同一对题第二轮可能选反 |
| Bench 10 The Sea Trial | **the held-out set** · what you overfit to | （待做）用 Bench 2 的 v5 封存后在 12 条新消息上考一次 |
| Bench 11 The Steam Drill | **GEPA itself** · a real run, replayed | |
| Door A1 Twelve Words | | |
| Door A3 Out of Ten | | |
| Door B1 Tuesday's Child | | |
| Door C1 The Careful Clause | | |
| 🔒 The Examiner's Answer | | |

---

### The Problem, Formally（p.14–15）

**一个方程，整个下午都在攻击它。**

一个 prompt 优化的系统 = **程序 Φ**（LM 调用 + 工具 + 控制流），由**自由文本参数 θ = (π, δ)** 控制：

- **π** = 每个模块的**指令（instructions）**
- **δ** = **demonstrations**（worked examples）
- **µ** = metric，把输出和 reference 比较打分

$$\theta^\star = \arg\max_\theta J(\theta), \qquad J(\theta) = \mathbb{E}_{(x,y)\sim D}\,\mu\big(\Phi(x;\theta),\, y\big) \tag{1}$$

**念出来**：最好的 prompt，就是让程序在世界发来的输入上**获得最高期望 metric** 的那个。

- **模型权重不出现——它们是冻结的。**
- **prompt 优化是重新加权模型已有的行为；它不安装任何新东西。**
- **µ 是「好」进入的唯一入口** —— 所以**优化器只和它拿到的 metric 一样好**（DSPy, Khattab et al. 2024, `2310.03714`）

#### 三个诅咒，以及用文字写的梯度

看起来像你见过的每个优化问题，**其实不是**。J 的三个性质各淘汰一类经典工具：

| 诅咒 | 为什么 | **死在这里的工具** |
| --- | --- | --- |
| **I. 离散且巨大** | θ 是字符串。40 token 的指令 × 50,000 词表 → $50{,}000^{40} \approx 10^{188}$ 个候选，"一个用来结束关于穷举的讨论的数字" | **梯度下降、网格搜索** |
| **II. 有噪声** | 只能看到估计 $\hat J(\theta) = \frac1n\sum_i \mu(\Phi(x_i;\theta), y_i)$，被模型采样和 n 的有限性模糊 | **「分高了就保留」** |
| **III. 昂贵** | 每次测量 = 在 API 价格下跑 n 次复合程序；**货币单位是 value per rollout** | **穷举比较** |

**活过三个诅咒的方法都是同一个解剖结构**：**提出几个可信候选 → 自适应地花评估预算去比较 → 选出存活者。**

**给诅咒 II 一个数字，当反射记住：**

$$\mathrm{SE}_{\hat J} = \sqrt{\frac{p(1-p)}{n}}, \qquad p=0.7,\ n=50 \Rightarrow \mathrm{SE}\approx 0.065 \tag{2}$$

- **一次读数有 6.5 个点的雾**
- **真实质量差 5 个点的两个 prompt，在 50 个样例上分不开**

> 🧭 自己算一下 n 的代价：SE 降到 2 点（0.02）需要 n ≈ 0.21/0.0004 ≈ **525**；降到 3 点需要 n ≈ **233**。所以「50 条 dev set 上 +5」基本是噪声。

**没有坡度的空间里，每个方法都得制造一个方向**：采样运气、LLM 的建议、对一次失败的书面批评、变异+选择、统计代理模型——**无论方向从哪来，都叫 pseudo-gradient（伪梯度）**。目前最强的：**模型读自己失败的 trace，用文字说出要改什么**——"**this prompt never tells the model to check the units.**"

**这个比喻的墓志铭**（目标 3 要求能背）：

> **真梯度是 local、linear、directional、consistent 的，文本梯度一样都不是。** 仔细的消融实验发现，收益来自**在一个「好峰很多、重要方向很少」的地形上的探索 + 经过验证的选择**，**而不是来自比喻里的链式法则结构**。（Melcer et al., Dec 2025, *Textual Gradients are a Flawed Metaphor for Automatic Prompt Optimization*, `2512.13598`）

**值得优化的系统很少是一个字符串，而是 pipeline，小错会复利**：

$$0.9^5 \approx 0.59$$

五个模块各 90% 可靠，端到端只有 59%。**每阶段几个点 = demo 和产品的差别**——这也是优化器必须**同时调多个 prompt** 的原因。

📚 Reservoir：n 能买到什么 & 多重比较陷阱 **§3**；prompt 上的贝叶斯搜索（MIPROv2 里的 TPE）**§4**；谱系——APE、OPRO、**ProTeGi（比 TextGrad 早一年发明了 textual gradient）**、EvoPrompt、DSPy **§1**。

---

### GEPA in Full（p.16–19）

**GEPA = Genetic-Pareto，两条谱系在这里编在一起**：

- 从**进化**那条线：保留一个**在选择压力下繁殖的种群**
- 从 **textual-gradient** 那条线：**由读过失败的模型写出的编辑**

（Agrawal et al., *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*, **ICLR 2026 Oral**, `2507.19457`）"**实践中用得最多，也最常被描述错的方法。**"

以模块 prompt $\Pi_\Phi = \langle \pi_1,\dots,\pi_{|M|}\rangle$ 为参数、权重冻结：

$$\Pi^\star_\Phi = \arg\max_{\Pi_\Phi} \mathbb{E}_{(x,m)\sim T}\,\mu\big(\Phi(x;\Pi_\Phi),\, m\big) \quad \text{s.t.}\quad \#\text{rollouts} \le B \tag{3}$$

- **m** = 评估器的 metadata：gold answer、rubric、测试套件
- **约束就是整个游戏**：一个 rollout = Φ 在一个 instance 上跑一次；GEPA 的主张是**每个 rollout 学到最多**

#### 反馈函数 µ_f

除了标量 µ，GEPA 还要一个返回**丰富文本记录**的函数：模块的推理、工具调用和输出、评估器的诊断——**编译错误、失败的测试、按 rubric 的分项、judge 的理由**。反思读它；**设计好它是 GEPA 最重要的实践杠杆。**

#### 两个池，两份工作

- **Feedback pool（小）**：提供 minibatch，反思读它们的 trace
- **Pareto pool（独立）**：**只用来给候选打分**，逐样例
- → **在反思刚刚没有过拟合过的数据上做选择**

#### GEPA 完整循环（必须能默写七步）

**Init**：池 $P \leftarrow \{\Pi_0\}$（seed），在 $D_\text{pareto}$ 的每个 instance 上打分。重复直到预算 B 花完：

| # | 步骤 | 做什么 |
| --- | --- | --- |
| 1 | **Parent selection** | 在 P 上建 **instance-wise frontier**；按**它当前赢下的 instance 数**成比例抽一个 parent |
| 2 | **Module choice** | 选一个模块变异（**round-robin**） |
| 3 | **Rollout and feedback** | 在 $D_\text{feedback}$ 的一个 minibatch 上跑 parent；经 µ_f 收集 trace |
| 4 | **Reflective mutation** | 反思模型诊断失败，**改写该模块的指令** → child（或：**merge 两条谱系**） |
| 5 | **Minibatch gate** | child 必须在**同一个 minibatch** 上**打败 parent**，否则**便宜地丢弃** |
| 6 | **Pareto evaluation** | 过了闸的 child 在 $D_\text{pareto}$ **每个 instance** 上打分，加入池 |
| 7 | **Prune** | 删除**逐 instance 严格被支配**的候选 |

**Return**：在 $D_\text{pareto}$ 上**聚合分最高**的候选。

**这个循环从不计算数值梯度、从不碰权重、从不只保留一个 incumbent。**

> 🧭 记忆口诀：**选父 → 选模块 → 跑+反馈 → 反思变异 → 小闸 → 全评 → 剪枝**。

#### 为什么接受分两阶段（步骤 5 + 6）—— 算一下

3 个样例的闸门、通过率 1/5、Pareto 池 200：

$$\text{每个提案平均成本} = 3 + 0.2 \times 200 = 43 \text{ rollouts}\quad(\text{而不是 } 200)$$

→ **同样的预算能探索近 5 倍（200/43 ≈ 4.65）的提案**。代价：**一个好 child 可能输在三个倒霉样例上。**

#### 一段话比一个数携带更多比特

- 标量 reward 只说「**错了**」
- "**You stopped after the first hop; you did not see that George Eliot and Mary Ann Evans are one person; you emitted prose where JSON was required**" 说了**哪里、哪类、改什么**，语言模型可以直接据此行动
- **权重上的 RL 必须从很多带噪标量里平均出一个梯度；GEPA 读一次诊断就编辑**

边注（推论，**准确**）：**GEPA 的优势活在 µ_f 的丰富程度里。** 当反馈真的是标量——一个证明要么对要么错——反思**无物可读，优势蒸发**。"**Design your failures to be legible in words.**"

#### 核心纠正：frontier 是在 instance 上（p.17）

**流行讲法**把 GEPA 的前沿画成「相关性、清晰度、简洁性」这样的轴——**直观、好教，但作为算法描述是错的。**

每个候选带一个**分数向量，每个 Pareto instance 一项**：

$$s(\Pi_k) = \big(\mu(\Pi_k, d_1), \dots, \mu(\Pi_k, d_m)\big)$$

支配关系在 instance 上读：

$$s(\Pi) \succeq s(\Pi') \iff \forall i: s_i(\Pi) \ge s_i(\Pi') \ \wedge\ \exists j: s_j(\Pi) > s_j(\Pi') \tag{4}$$

**候选存活条件：至少在一个 instance 上最好，且没有被全面打败。** "**Specialists over examples, not specialists over objectives.**"

#### 2026 年 10 月的细节：知道你在跑哪种 frontier

纠正对论文和库的主入口成立。但 `gepa` 库现在提供**四种 frontier 类型**：

| 类型 | 含义 | 谁默认用 |
| --- | --- | --- |
| **instance** | 每个验证样例上最好的 | **`gepa.optimize`、`dspy.GEPA`** |
| **objective** | 每个命名 objective 上最好的 | — |
| **hybrid** | 两者 | **`optimize_anything`** |
| **cartesian** | 每个 (样例, objective) 对 | — |

- **分数是最大化的** → latency、cost 要**翻转**后才能当 objective
- **DSPy 3.3.1 起** metric 可以以命名的 **`objective_scores`** 报告它们
- "**Asking for objectives is now a setting, so know which frontier you are running before you read the one you got.**"

#### 手算一个 frontier（p.18）—— 先自己做再看答案

4 个候选、5 个 Pareto instance：

| | i1 | i2 | i3 | i4 | i5 | mean |
| --- | --- | --- | --- | --- | --- | --- |
| **A (seed)** | 0.9 | 0.7 | 0.2 | 0.8 | 0.3 | 0.58 |
| **B** | 0.6 | 0.8 | 0.2 | 0.9 | 0.1 | 0.52 |
| **C** | 0.4 | 0.5 | 0.9 | 0.4 | 0.2 | 0.48 |
| **D** | 0.8 | 0.6 | 0.2 | 0.7 | 0.3 | 0.52 |

<details><summary>答案（点开）</summary>

- **D 被 A 严格支配**（0.9≥0.8, 0.7≥0.6, 0.2≥0.2, 0.8≥0.7, 0.3≥0.3，且某处严格更好）→ **死**
- **Frontier = {A, B, C}**
- A 赢 i1、i5；B 赢 i2、i4；C 赢 i3 → parent 按 **2 : 2 : 1** 抽 → **A、B 各 0.4，C 0.2**
- 「选最好的」会**只加冕 A**，因为 C 平均分平庸就**安乐死它**——**尽管 C 握着 i3 的唯一钥匙**

</details>

这就是 **example 17 上的专家**。论文的消融很直接：**naive select-the-best 在同等预算下最多差 8.17%（聚合 6.4%）**。**保留的多样性是逃出局部最优的安全出口。** 糖果店的几何还在——一个只能沿着滑动的篮子柜台——**但坐标现在是样例**，在一个样例上最好、其他都差的篮子**留在柜台上**。

#### Merge：横向移动

- **Reflective mutation 是纵向移动；merge 是横向移动**
- GEPA **逐模块** merge 两条谱系，**从不拼接文本**
- **聚合约 +2%，有利任务最多 +5%，依赖模型**；当 frontier 上有几条**成熟谱系**时才有回报
- **DSPy 3.4 的 `dspy.GEPA` 默认开启**（`use_merge=True`，**最多 5 次 merge 尝试**）

#### 诚实的数字（ICLR 2026 版）

| 比较 | 结果 |
| --- | --- |
| 设置 | **6 个任务 × 2 个模型（Qwen3-8B、GPT-4.1 mini）** |
| vs **GRPO** | 平均 **+6%**，最高 **+20%**，rollouts **最多少 35×** |
| vs **MIPROv2** | **+10% 以上**（AIME-2025 上 **+12%**），prompt **最多短 9.2×** |

⚠️ **限定**：比较是**预算匹配的，不是渐近的**。RL 随算力继续爬；**在能力受限的任务上，权重优化仍然赢**。GEPA 在冻结权重里移动 prompt；RL 移动权重。

> **"You can steer the elephant brilliantly; you cannot steer it into a panther."**

#### GEPA in code：同一个 compile 动词（p.19）

DSPy 里优化器是**一个对象、一个动词**。metric **接收五个参数**，可以返回分数 + feedback；**反思模型必须强，任务模型可以便宜**。（按 DSPy 3.4 的 `dspy.GEPA` 接口）

```python
import dspy

def metric_with_feedback(gold, pred, trace=None, pred_name=None, pred_trace=None):
    notes = []
    if pred.category != gold.category:
        notes.append(f"said {pred.category}, expected {gold.category}")
    if not pred.evidence:
        notes.append("cited no evidence span")
    return dspy.Prediction(score=float(not notes),
                           feedback="; ".join(notes) or "correct")

optimizer = dspy.GEPA(
    metric=metric_with_feedback,
    auto="light",                     # or "medium", "heavy"
    reflection_lm=dspy.LM("gpt-5", temperature=1.0, max_tokens=32000),
)
compiled = optimizer.compile(program, trainset=trainset, valset=valset)
```

- **`trainset` 喂反思更新，`valset` 给 Pareto 打分**——论文两个池的另一个名字
- ⚠️ **没有 valset，trainset 两份工作一起做——正是纪律警告的那种过拟合**

> 🧭 读代码要点：这个 metric 的 feedback 正是 field notes 的缩影——**category 对不对**（the thought is the metric）+ **有没有引证据**（「指向正确证据的部分分」）。不过它的 score 是 0/1，注意和上面「标量反馈让优势蒸发」对照：分数粗，但 **feedback 字符串**是细的。

📚 Reservoir：GEPA 作为 **(µ + λ) 进化算法**——算子、archive、四种 frontier、多提案选择、什么能证明什么不能 **§5**；DSPy 机器与优化器动物园——从 **BootstrapFewShot（"the wheels beat the racing bicycle"）** 到 MIPROv2、SIMBA、`dspy.GRPO`，以及 3.3/3.4 版本 **§2**。

#### 十月的旋钮（边注，p.19–20）

`gepa` 0.1.2–0.1.4（2026 年 7 月）起：

- 一次迭代可以**采样并评估多个提案**，选择规则：`AllImprovements`、`BestImprovement`、`TopKImprovements(k)`
- **接受准则可插拔**：`strict_improvement`、`improvement_or_equal`、或自定义
- **反思步骤是可替换的接缝**（ReflectionLM protocol）
- **论文算法是默认值；库暴露了旋钮**

---

### The Discipline（p.19–22）

> **"A machine that maximizes a number will find every flaw in the number."** 你已经在 Genie's Exam 当过它的考官了。这里是考试让你想要的那套纪律。

#### 三个集合，三份工作

**头号大罪：在同一批样例上优化又评估。**

| 集合 | 状态 | 为什么 |
| --- | --- | --- |
| **Feedback minibatches** | **burned（烧掉了）** | 反思**细读**过它们；它们的分数**对泛化什么都不说** |
| **Selection（Pareto）set** | **pressured（受压的）** | 优化器在它的分数上做选择 → 赢家在这里的分数 = **几百次相关的带噪抽样的最大值** |
| **Holdout** | **clean（干净的）** | **只碰一次**、只由**唯一的赢家**、在**运行之后** —— **唯一可以相信的数字** |

报告纪律：

- **只报 holdout delta**
- 赢家**跨 3–5 个 seed 重跑**，报**均值和散布**
- **分 slice 读**：一个微笑的平均值不能掩盖一个流血的分层
- **盯着赢家的长度**：过拟合的 prompt 会**堆积 case-specific 的废话**
- **偷看了 holdout？它现在是 selection set 了；找一个新的。**

边注：回忆式 (2)——n=50 时雾有 6–7 点宽，一个在这 50 条上检查几百个候选的优化器会**真诚地**凭空造出一个「**+8**」。

#### Judge 不是神谕

当 metric 是一个模型，它是**一个有性格的选择压力**：

- 被一个「**工作就是找出它会打高分的输出**」的过程查询几千次，judge 的偏见会被找出来：**position、verbosity、self-preference** 各自变成一条 **reward hacking** 的通道
- **你得到的 prompt 是你放进去的 judge 的指纹**——严或松
- judge 可能在**容易的对比上和人一致**，却把**接近最好的候选排得很差**——**恰恰是优化器唯一会问的区域**
- **尺子会弯**：一个报告案例里，一个**固定的答案**每周重新打分，期间只迭代 judge 的 prompt，分数**从 6.1 漂到 7.3，答案一个字没改**

**十月最干净的数字**（Huang et al., May 2026, *From Raw Experience to Skill Consumption*, `2605.23899`）：

| 发现 | 数字 |
| --- | --- |
| 模型从自身经验写出的 skill：提升 / 变差 | **75% / 25%** |
| LLM 无标准地二选一挑更好的 skill | **46.4%**，"indistinguishable from random" |
| 差距**大**的时候（无标准） | 只有 **15.8%** 挑对 |
| **给 rubric** | **73.8%** |
| skill 的**格式** | **无显著差异**——起作用的是 skill **说了什么**，不是**长什么样** |

> 🧭 15.8% 比硬币还差得多——差距越大反而越挑错，说明无标准 judge 有**系统性偏好**（大概率偏向更长、更「像样」的那个），不只是噪声。⚠️ 这是我的推测，待读原文核实。

📚 Reservoir：偏见三件套及修法、disposition、hollow agreement、弯曲的尺子、一次坏运行的解剖、skill 研究全文 **§6**。

#### 让 metric 说话

建设性的另一面：**返回文本 + 数字的 metric**——**actionable side information**。

- 返回 `0.4` 的 metric
- 不如返回 `0.4 -- ignored the second hop; date wrong; schema violated` 的 metric

因为反思模型**读字符串并据此编辑**。"**A bare score is one bit per rollout; the feedback field in the code above is where the bits come from.**"

#### 怀疑者的书架，以及什么时候不该优化

**Coin flip，限定条件保留**（Zhang et al. 2026, `2604.14585`）：

- **72 次运行，全部在 Claude Haiku 4.5 上，全部是单 agent 任务**：6 方法 × 4 任务 × 每个 3 次重复
- 四个任务合计：**49% 的运行低于起点 zero-shot**
- 唯一有**可利用的输出结构**的任务（模型**能**产生、但**默认不**产生的格式）：**六种方法全部提升，最多 +6.8 点**
- → "**Optimization pays only where the model can but doesn't.**"

**Naive prompt optimization**（Chang & Chen, Aug 2026, `2608.27266`）：**单一谱系**、由 teacher 模型读 rollout 反馈逐次修订 → 在作者实验里**匹配或打败 GEPA，rollout 更少**；teacher 越强收益越大。（讲义注：**只读到摘要层面**）

**RLMOpt**（Bangalore Satheesha et al., Aug 2026, `2608.10471`）：把搜索策略做成一个**会分析失败、分配预算、决定何时停止的 agent** → 作者报告四个 benchmark 上最好的 held-out 结果；朴素发现：**收益主要取决于 seed prompt 的 headroom，而不是搜索预算**。论文自己的 caveat：**匹配比较只有单 seed**、对手是 **light 预算的 GEPA**、**四个 margin 里只有两个超过一个 paired SE**。

**什么时候不该优化**：

1. **10 分钟 headroom test** 没发现超过噪声的 gap：**zero-shot prompt vs 手写 10–20 个变体中最好的那个，在约 20 个 held-out 样例上**
2. 输出是**没有结构可修的自由文本**
3. **你的 metric 经不起被最大化**："**an optimizer is a metric amplifier, and a flawed µ is a knife aimed at yourself**"
4. **反思模型弱**：rollout 用便宜模型，**反思用强模型**
5. **开跑前先算价**：

$$R = K \times B \times I \text{ rollouts}\quad(\text{候选数} \times \text{minibatch} \times \text{迭代数})$$

在任务模型上，**再加上**强模型上的**每一次反思**——"**the forgotten line, and often the larger.**"

📚 相对于 serving 账单的回本 **§7**；书架全集 **§8**。

> 🧭 自己练一下算价：K=4、B=3、I=50 → 600 次任务模型 rollout + 50 次强模型反思；如果每次反思 prompt 塞进 3 条完整 trace + 当前 prompt，单次可能上万 token——反思那条线很容易比 rollout 贵。

---

### The Field Notes, Cashed In（p.22–23）

早上是故事，13:45 你玩过了，这里是**机制**：

| 课 | 机制 |
| --- | --- |
| **The grunt work is the data** | 反思模型**读 feedback minibatch 的 demo 和 trace，把读到的写进指令**。**一条坏 demo = 一个坏的文本梯度**：反思器**引用它、泛化它、供奉它，错误变成政策** |
| **The thought is the metric** | µ 是「好」进入式 (1) 的**唯一入口**。field 系统每个风险的 measure 是 **F_β**（见下） |
| **The insurance is the tether — KL for text** | 见下 |

#### F_β

$$F_\beta = \frac{(1+\beta^2)\,P\,R}{\beta^2 P + R} \tag{5}$$

P = precision，R = recall，**β 是每个风险单独设的旋钮**：**β > 1 偏重召回**；最严重的风险**大幅**偏向它，因为那里一次漏报就是一次事故。

> 🧭 手算感受一下：P = 0.5、R = 0.9
> - F₁ = 2·0.45 / 1.4 ≈ **0.643**
> - F₂ = 5·0.45 / (4·0.5 + 0.9) = 2.25 / 2.9 ≈ **0.776**
> 同一个「宁可误报」的分类器，在 β=2 下得分明显更高——旋钮把「漏报更贵」写进了数。

#### Tether = 文本版的 KL

RLHF 用惩罚把策略拴在起点附近：

$$\max_\pi \ \mathbb{E}[r] - \lambda\,\mathrm{KL}(\pi \,\|\, \pi_\text{ref})$$

Tether 把这一步搬到文本上，**并做成硬约束**：在 seed 里标一组 span **T**（校准规则、风险定义）为**不可编辑**，变异只作用于其余部分 → **每个 child 在 T 上都和 seed 一致**。"**A regulator does not grade on a curve**" → 所以这个约束**没有 λ 去软化它**。

#### Intron = 反思器泛化了的一个巧合

- minibatch **碰巧共享一个特征**——比如每个高风险案例**碰巧都引用了一个美元数字**
- 反思模型把它**写进指令当成规则**
- Pareto 集上**没有东西惩罚它** → **它存活**
- **治法 = 人工编辑**：**一次删一条子句**，保留承重的；**加一个反例让这个巧合不再划算**

#### ReAnchor：调阈值，不动 prompt

每个风险的 β 旋钮，**从 9 月起有了库原语**：**DSPy 3.4 的实验性 `ReAnchor`**（Stanford NLP, DSPy 3.4.0 release notes, 2026-09-25）

- **不改写任何指令、任何 demo**
- 拟合程序的**数值决策参数**：布尔输出在概率上的**切点**、分数的切分、选择的权重
- 一个设置**只有在严格更好**、**且收益在训练集 held-out 部分上的五折检查中保持**时才改变
- compile **返回一个副本**
- "**The field notes did this by hand, risk by risk. It is now a verb.**"

---

### Match the Optimizer to the Artifact（p.23–24）

> **问题不是哪个优化器最新，而是你在优化什么。**

| Artifact | 工具 | 为什么，要盯什么 |
| --- | --- | --- |
| **一个 token 预算下的紧凑 prompt** | **GEPA** | 把经验**压缩**成短指令。⚠️ introns；弱反思器；不会说话的 metric |
| **一个增长的 context 或 playbook** | **ACE** | **累积**：delta 追加、计数、剪枝，**从不整体重写**。⚠️ 矛盾悄悄混进来 |
| **一个 skill 文件** | **SkillOpt**，或 **gskill** | 有界编辑、被拒编辑的记忆、一道闸；或 `optimize_anything` 学一个 SKILL.md。⚠️ **闸太严会丢掉部分修复** |
| **一个决策阈值** | **校准它（ReAnchor）** | **字没问题，切点错了。动数字，别动 prompt** |
| **程序的分解结构** | **Flex**（实验性） | 程序结构变得可搜索；**优化器写的代码在 sandbox 里跑**。DSPy 3.3 新增 |

"**The wrong tool burns the budget and teaches nothing.**"

#### ACE：累积，不压缩

**Agentic Context Engineering**（Zhang et al., ICLR 2026, `2510.04618`）：

- 维护一个**逐条的、增长的 playbook**，由 **generator、reflector、curator** 三个角色照料
- **拒绝整体重写**，理由是测出来的：**context collapse**——让 agent **一次性重写**累积的 context，**约 18,000 token 塌缩成约 100 token，准确率跌到无 context baseline 以下**
- 治法是**架构性的**：**append、counter-update、delete——deltas, not drafts**

边注：**把 context collapse 留到下周。** 一个在一次重写里忘掉所知一切的 playbook 是**记忆失败**，而记忆是 **Week 8** 的起点。

#### SkillOpt = 带着梯度下降进口零件的 GEPA

（Yang et al., May 2026, `2605.23904`）

| 梯度下降的概念 | SkillOpt 里的对应 |
| --- | --- |
| **learning rate** | **有界编辑预算**：每轮少量 `ADD` / `REPLACE` / `DELETE` → 驯服「**忘掉有效规则的整体重写**」 |
| （GEPA frontier 缺的）**失败的记忆** | **rejected-edit buffer**：每个被拒编辑**连同它造成的分数下降**，送回同一 epoch 后续的反思 |
| **momentum** | **epoch-wise slow update**：跨 epoch 携带稳定的编辑方向 |
| **validation** | 每个被接受的编辑**过 held-out 闸** |

#### gskill：从 GEPA 那边走到同一个地方

（Tan et al., GEPA blog, 2026-02-18）

- `optimize_anything` 指向一个 coding agent 的 **SKILL.md**
- 每个仓库用 **SWE-smith 生成约 300 个任务**来学
- 博客图表：一个小 agent 在一个仓库 **55% → 82%**，另一个 **24% → 93%**；**skill 迁移到了 Claude Code**
- ⚠️ 作者自己的 caveat：**仓库特定**、**测试集小（约 60 个任务）**、**没有重复运行**、**生成的任务比真实工作简单**

#### 活着的争论：闸门该不该严？

**SkillNEO**（Ma et al., Oct 14 2026, `2610.20926`）说**不该**：

> "requiring immediate reward gains can discard useful partial repairs before their benefits emerge."

- 让**低分版本也继续接受编辑**
- **把「用哪个版本」和「继续改进哪个版本」分开**
- **86 个 SkillsBench 任务**：小模型平均 reward **49.1% → 66.4%**；**有些低分版本最终导向了被选中的 skill**

**又一次 exploration vs exploitation**：

| 方法 | 立场 |
| --- | --- |
| **SkillOpt** | **elitist + 失败的记忆** |
| **GEPA instance frontier** | **已经部分 non-elitist**——候选只要**某处赢**就存活 |
| **SkillNEO** | **显式 non-elitism** |

"**Nobody has settled it; know which side your tool is on.**"

---

### The Synthesis（p.24–25）

**整天在搭建的那句话：**

> **A self-improving skill is GEPA run over the skill's own text.**

W3 把 skill 教成「**用散文写的流程 + verifier**」；今天提供了这种文本所邀请的机器：

| 进化的部件 | 在 skill 优化里 |
| --- | --- |
| **genome** | skill 本身 |
| **pressure** | evaluation |
| **rewrite** | reflective mutation |
| **保留来之不易的专长** | instance frontier |
| **governor**（防止改进变成漂移） | ① 每个被接受编辑都要过的 **holdout gate** ② **seed 重跑**，不靠一次幸运抽样相信任何编辑 ③ **永不允许回退的 strata**，不管聚合怎么说 |

> **"Reflection is the seed of self-improvement, not self-improvement itself; what turns the seed into growth is measurement the system did not get to choose."**

**三个名字，一件事**：self-improving skills、reflective prompt evolution、gradient descent for sentences = **text-as-parameter, optimized by reflection, under a validation gate**。

- policy improvement、exploration vs exploitation、overfitting、momentum——**全部迁移**；**只有参数变了**，从数字向量变成字符串
- **优化单元在往上漂**：prompt → skill → **library**
  - **SkillOS**：策展一个库（加载什么、合并什么、退役什么）
  - **Selm**：按每个 skill 的 **confidence 和 utility** 管理，**按 utility 检索**、剪掉不再挣得位置的

📚 多轮 agent 里**哪一轮挣得梯度**（credit assignment）**§10**；整门手艺的**模式语言** **§11**；**运行手册**（从 headroom test 到人工编辑到上线）**§12**。

---

## Cycle 4 · The Owl of Minerva（p.25）

> "**The owl of Minerva spreads its wings only with the falling of the dusk.**" —— Hegel，《法哲学原理》序言：理解在一天能被整体看见时才到来。

**19:30，不管 deep dive 讲到哪，Owl 起飞**——今天必须熬过遗忘曲线的**五行**，每行附一行为什么重要。它们开启下周的 Orientation，并设定本周二、周四的 session。**讲义不印，在房间里见。**

### ✍️ 19:30 之前：先写我自己的五行

> 第一行出现之前写下一个月后最想记住的五件事。之后标出 Owl 也说了的；**没说的那些留着——那些是你的。**

| # | 我的五行（课前草稿，19:30 前修订） | Owl 也说了？ |
| --- | --- | --- |
| 1 | prompt 是参数；优化 = 在没有梯度的离散空间里搜索，方向靠文字写的伪梯度 | |
| 2 | 优化器是 metric 放大器——metric 必须会说话（分数 + 可行动的文字），且经得起被最大化 | |
| 3 | frontier 在 instance 上，不在 objective 上：保留 example 17 上的专家 | |
| 4 | 三分数据：burned / pressured / clean；只信 holdout，跨 seed、分 slice | |
| 5 | 先做 headroom test；模型「能但不做」时才优化；不可动的规则用 tether 锁死 | |

### 🦉 Owl 的五行（课上填）

| # | 原文 | why |
| --- | --- | --- |
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Cycle 5 · The Speakeasy（p.26）

20:00 后，可选，**无承重内容**。从停车板上没解决的问题开始，然后二选一：

- **Code walk**：`dspy.GEPA` 在一个小程序上**从 signature 到 compile**；独立 `gepa` 库的 `optimize_anything` 和 gskill 的 recipe；十月的旋钮
- **Paper walk**：**SkillOpt 的闸 vs SkillNEO 的 non-elitism** 并排——主张、设置、**什么会让你改变主意**

都指向 Reservoir **§5、§9**。

---

## If You Could Not Attend（p.26）

1. 读到六条 headlines
2. 和搭档玩 core path：Bench 2, 4, 7, 9, 10，然后 Door A1, A3, B1, C1。**Bench 10、Steam Drill、考试的锁定答案需要讲师或 TA 的 code**，周二/周四找
3. 看录播：14:30 debrief → 问题的形式化 → GEPA 全貌；**手算 frontier**；读 Reservoir **§5、§12**
4. **看录播里的 Owl 之前先写自己的五行**，再对照

---

## Essential Readings（p.26–27）· 必读，每篇是下午的一面承重墙

| 论文 | 读什么 / 注意什么 |
| --- | --- |
| **Agrawal et al., GEPA** (ICLR 2026 oral) `2507.19457` | **读 §2、§3**；**核对 frontier 的坐标是 instance**；**GRPO 的 caveat 一直带着** |
| **Khattab et al., DSPy** (ICLR 2024) `2310.03714` | 从源头把**程序和 prompt 分开**：signatures、modules、compile 动词 |
| **Zhang et al., ACE** (ICLR 2026) `2510.04618` | GEPA 的**对立极**——累积、deltas not drafts——以及 **context collapse**，通往下周的桥 |
| **Yang et al., SkillOpt** (2026) `2605.23904` | **给 skill 的梯度下降，做精确了** |

## Oliver Twist's List of Readings（p.27）· 选读

| 论文 | 一句话 |
| --- | --- |
| Yang et al., **OPRO** (ICLR 2024) `2309.03409` | "Take a deep breath" 的出处 |
| Pryzant et al., **ProTeGi** (EMNLP 2023) `2305.03495` | **textual gradient 的诞生** |
| Yuksekgonul et al., **TextGrad** (Nature 639, 2025) `2406.07496` | **在 ProTeGi 之后读** |
| Opsahl-Ong et al., **MIPROv2** (EMNLP 2024) `2406.11695` | **贝叶斯主力** |
| Huang et al., **From Raw Experience to Skill Consumption** (2026) `2605.23899` | **无 rubric 的 judge 在机会水平** |
| Ma et al., **SkillNEO** (2026) `2610.20926` | 反对严格闸；**和 SkillOpt 并排读** |
| Chang & Chen, **Naive Prompt Optimization** (2026) `2608.27266` | 一条谱系 + 强 teacher |
| Tan et al., **gskill** (GEPA blog, 2026) | 一个学出来的 SKILL.md，带 caveats |

讲义正文里另外引用、没列进阅读清单的：Melcer et al. `2512.13598`（文本梯度是有缺陷的比喻）、Zhang et al. `2604.14585`（coin flip）、Bangalore Satheesha et al. `2608.10471`（RLMOpt）、DSPy 3.4.0 release notes、gepa releases v0.1.2–0.1.4、gepa frontier types 文档、Sobel *Longitude*。

📚 ACE、SkillOpt、gskill、SkillNEO 全文，以及 hypothesis-driven skill optimization、SkillRL、SkillOS、Selm、「**tethered ACE**」这个开放想法：Reservoir **§9**。

---

## A Calibration Note（p.27）

第一个 upper-division 日，第一个按循环搭的日子。我们**手工**做了优化器做的事，**看了**一个优化器，**考了**一个精灵，**拆开了** GEPA：

| 旧意象 | 变成了 |
| --- | --- |
| 两卢比 | **rollout 预算** |
| 篮子柜台 | **frontier** |
| Literal Genie | **优化器本身** |

> **"Prompt engineering taught the machine to follow an instruction. Prompt optimization teaches it to improve one — held in check, always, by a measurement it did not get to choose."**

**下周：Memory。** 一次重写就忘掉一切的 context 是记忆失败；W6 的「**the harness remembers**」接着问：**记住什么？记多久？**

---

## 索引里的关键词（p.31–32，可当复习清单）

ACE 23 · actionable side information 21 · Beckett 1 · behavior quotient 14 · bits per trial 17 · coin flip result 9 · compound program 15 · context collapse 23 · core path 10 · data distillation 22 · elitism 24 · F-beta score 22 · feedback function µ_f 16 · field notes 6 · five-cycle day 4 · Genie's Exam 12 · GEPA 16 · goldset 7 · Goodhart's law 1, 2 · governor 24 · GRPO 18 · gskill 24 · Harrison's Workshop 10 · headroom 9 · headroom test 21 · introns 2, 8, 22 · KL divergence 22 · Literal Genie 2 · LLM-as-judge pathologies 20 · Maskelyne 10 · match the optimizer to the artifact 23 · metric amplifier 19 · minibatch gate 17 · objective J(θ) 14 · Owl of Minerva 25 · Pareto frontier over instances 17 · Parking Board 4 · pseudo-gradient 15 · ReAnchor 22 · Reservoir 4 · resolution gap 6 · self-improving skill 24 · Selm 25 · skeptic's shelf 21 · SkillNEO 24 · SkillOpt 23 · SkillOS 25 · Speakeasy 26 · Steam Drill 12 · system-aware merge 18 · tether 7, 22 · text-as-parameter 24 · three curses 14 · three-way split 20

> 索引里有、正文里我没找到明确定义的词：**behavior quotient**（p.14）、**data distillation**（p.22）、**goldset**（p.7）——推测分别对应「re-weights behaviors the model already has」「demo 的人工审核」「one blessed set」。⚠️ 待课上确认。

---

## 精读后我自己的三条

1. **「把它们看成很多个」先于任何优化器。** resolution gap 这个词值得留着：一个 prompt 怎么调都不好时，先数一下它里面装了几个问题。这和我在 capstone 里把 commerce agent 的检查拆成独立 verifier 是同一个动作。
2. **metric 才是工程本体，优化器只是放大器。** field notes 说「设旋钮是项目的智力核心」，GEPA 说「设计 µ_f 是最重要的实践杠杆」，coin-flip 说「metric 经不起最大化就是刀对着自己」——三处在说同一件事。我以前把 eval 当成优化之后的验收，其实它是优化之前的设计。
3. **先跑 headroom test，再决定要不要优化。** 49% 的运行比起点还差，这个数字足够让我在任何「上 GEPA」的提案前先问：zero-shot vs 20 个手写变体，在 20 条 held-out 上，gap 有没有超过 SE？没有就别开跑。

## 🧭 和 Capstone（Verifiable Commerce Agents）的接线

- **tether** ↔ 店规（"先给积分；退款 = 金额 + $15；手续费不对顾客提"）这类**业务硬规则**应当标成不可编辑 span，不能交给优化器改
- **F_β per risk** ↔ 不同错误的代价不同：重复退款（钱出去了）应当像「最严重的风险」那样偏召回
- **会说话的 metric** ↔ verifier 的输出别只给 pass/fail，要给「哪条规则、哪一步、哪个证据」
- **三分数据** ↔ tau2-bench 式的任务集要预留一份**只碰一次**的 holdout

## 待办

- [ ] 课上：填 **Debrief 揭晓表**和 **Owl 五行**；19:30 前修订自己的五行
- [ ] 课上：Bench / Door 记录见 [`lab-log.zh.md`](lab-log.zh.md)
- [ ] 拿到 `fall-agents-week-7-reservoir.pdf` 后放进 `uploads/`，重点读 **§5、§12**（缺席补课路径），再看 §3、§6、§9
- [ ] 必读 4 篇：GEPA（§2–3）、DSPy、ACE、SkillOpt —— 用 paper-deep-read 流程做精读笔记
- [ ] 核实：Huang et al. `2605.23899` 里 15.8% 的具体条件（「差距大」怎么定义）
- [ ] 核实：索引里 behavior quotient / data distillation / goldset 的确切含义
- [ ] 周二/周四 session：跑 deep dive 里的 `dspy.GEPA` 代码；补做非 core 的 bench / door
- [ ] Week 6 尾巴：重新下载 10/26 之后的 `strangers-toolbox.zip`，重跑 Door 1；读 *No Castle Without Walls*
