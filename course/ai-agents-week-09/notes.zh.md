# Week 09 课堂笔记（2026-11-15）

> 讲义结构见 [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)；这里记课上讲义之外的口头补充和板书。

## 开场 · Deck 首页

- 标题：**The Hundred-Million-Year Prototype · An Experiential Prologue to Agent Memory**
- 副标题：*Eleven experiments on the only memory system in the room that already ships.*（= 人脑，进化了一亿年的原型）
- 页眉：AI Agents Bootcamp · Fall Cohort · Week 9 · SupportVectors
- 在线人数：18
- 今天议程（Parking Board 页眉）：**Orientation 11:00 → Experientials 12:00 → Deep dive 14:30 → Owl of Minerva 19:30 → Speakeasy 20:00**
- Parking Board 14:02 问题（Erwin）：*How do you measure both the complexity of tasks an agent can finish on its own and how long it can keep operating reliably without human intervention? Which benchmarks, and what would you test yourself before deploying?*
  - 我的思路：**复杂度** → METR time horizon（按人类完成时长衡量的任务难度，看 50% 成功率能到多长）、SWE-bench Verified、Terminal-Bench、OSWorld、GAIA；**可靠性 / 持续运行** → τ²-bench 的 **pass^k**（同一任务连跑 k 次都成功）、Vending-Bench（长时间运营的连贯性，和 Project Vend 同源）；**上线前自测** → 用自己的日志建 eval（W9 plant–distract–probe）、pass^k、人工介入率 / 平均无介入步数、故障注入、成本 / 延迟、no-regress ship gate（见 [tau2-bench 笔记](../../tau2-bench%20学习笔记（对照%20Capstone）.md)）
- 🧭 Prototype 的 9 条 lesson 已列在 [lab-log](lab-log.zh.md#the-hundred-million-year-prototype研究人脑这个已上线的-memory-系统)，11 个实验名出来时对号入座

## 上午 · Hundred-Million-Year Prototype（整段 ≈ 60–70 min）

### Deck p.4 · The rules of the lab

- 每个实验都跑在**你自己的记忆**上：不用设备，不用电脑
- **Write, don't just think.** → 然后两人对比 → 志愿者向全班汇报
- 每个实验的时间写在幻灯片页眉
- > *You are the dataset this morning. The theory this afternoon will only give names to what you will have already felt.*
- 🧭 「先写下来」和 W8 的「跑之前先写预测」是同一条纪律：不写下来，事后记住的就会是另一个版本（这本身就是今天要做的实验：**每次回忆都是一次重写**）
- 🧭 按 [lab-log](lab-log.zh.md) 的表一个实验一行记：**我写的 / 搭档写的 / 全班汇报 / 对应哪条 lesson**

### Deck p.7 · Experiment 2 · The flood（≈ 5 min，pair share）

> *A hint once brought back what you didn't know you still had — the street you grew up on, a song, the smell of a classroom. First bicycle, first day of school, first love. In detail.*
> **Where was it, before you "remembered" it?**

- 🧭 **它一直在**，只是在窗口外休眠。讲义对 memory 的定义正是「窗口外、可以被换入窗口的一切」；记起来 = **跨越边界**的那一刻
- 🧭 唤回它的是 **cue**（一首歌、一股气味），不是你主动去搜。对 agent：没被召回 ≠ 没存；**先查 query/cue，再怪 store**（Memory Palace 的 Flood 房间会再考一次）
- 🧭 气味、歌曲这种 cue 往往和**问题文字**毫无语义关系，却能精确命中 → cosine relevance 不是唯一的检索通道；也是讲义说「Does that still work for you?」检索不到东西的反面例子
- 我的例子：**一碗好味噌汤的香气 → 20 年前在日本工作的日子**。按 Smallville 的 γ = 0.995/h，20 年 ≈ 17.5 万小时，recency ≈ 0.995^175200 ≈ e^−878 ≈ 0；只靠 recency 早该沉底了，能被捞回来靠的是 **importance**（人生重要阶段）+ **cue 命中（relevance）** → 正好说明为什么要三项相加，而不是只看 recency。cue = **气味**（嗅觉是经典的强 cue，即「普鲁斯特效应」，正好对上 slide 上的「the smell of a classroom」）（和「日本工作」在文字上毫无关系，却精确命中）。⚠️ 因为「每次喝都会想起」，这条记忆一直在被复习（衰减从上次访问算起 → soft LFU），算「常被唤起的联想」；最符合 flood 的是味道**意外带出一个以为早忘了的具体细节**（某家店、某位同事、某个早晨）
- 搭档 / 全班：

### Deck p.8 · Experiment 3 · The edited narrative（≈ 5 min）

> *Something you **knew** happened — until a photo, a diary, a sibling corrected you. Where did the false version come from? How did it form — and **why**?*
> Stuck? 整个文化一起记错：Darth Vader 从没说过 "Luke, I am your father"，原台词是 **"No, I am your father."**；Casablanca 里也没人说 "Play it again, Sam"（原台词是 "Play it, Sam"）。

- 🧭 **每次回忆都是一次重写**：记忆不是录像回放，是每次按「现在觉得合理的样子」重新拼一遍，拼完再存回去
- 🧭 Vader 那句为什么加了 "Luke"？脱离上下文后 "No, I am your father" 不知道在对谁说 → 大家传播时自动补上名字，让它**自包含**。= 摘要 / compaction 为了独立可读而**改写原文**；反复转述（复习）让改写版取代了原版 → 讲义的「摘要是有损拷贝」「compaction 重写它保留的东西」
- 🧭 照片 / 日记 / 兄弟姐妹 = **外部的原始记录**（append-log，episodic trace）。纠错靠的是**从没被改写过的 ground truth** → 讲义说 append-log 要永远保留、永不编辑
- 我的例子：小学学的，一直记成 **「天将降大任于斯人也」**；《孟子·告子下》原文和课本是 **「故天将降大任于是人也」**。一个字之差，很多人都记成「斯人」，是中文圈有名的集体记错。
  - 来源：「斯人」比「是人」更像文言（「微斯人，吾谁与归」）；「是」在现代汉语里是系动词，读起来别扭，大脑就换成更「合理」的字。再加上大家互相引用，改写版被反复复习，盖过了原版
  - 这类集体记错叫 **曼德拉效应**（Fiona Broome 2009 命名：很多人「记得」曼德拉 80 年代死于狱中；实际 1990 年出狱、1994–99 任总统、2013-12-05 去世）。机制：①记忆是重建，存的是要点不是原文；②**图式补全**，缺口用「最合理」的版本填；③**来源混淆**，把别人的事（如 1977 年死于羁押的 Steve Biko）安到他身上；④**社会传播 + 复习**，错版本被反复说，越熟越像真的（流畅感 ≠ 正确）。→ agent 对应：摘要只留 gist、LLM 补全空缺 = confabulation、没有 provenance 就分不清来源、被常访问 ≠ 仍为真
  - 🧭 能纠错的只有**原始记录**（课本原文 = append-log）；凭记忆去纠记忆只会再改写一次（= 拿摘要修摘要）
- 搭档 / 全班：

### Deck p.9 · Experiment 4 · The diary decision（≈ 4 min）

> *You journal vacations, photograph weddings, write memoirs of happy summers. Nobody photographs the commute. **Why not?***

- 🧭 **只写无法再生的东西**：通勤天天一样，随时能从「我每天走这条路」这个模式重建出来，记了也是重复；婚礼只发生一次、错过就没了 → 值得写
- 🧭 = **write policy / salience gate**（「三个 session 后这还重要吗？」）；也对上驱逐分数里的 **rederivable** 因子：能重新推导的就别占地方
- 🧭 另一面：只拍开心的事 → 存下来的「过去」是**被策展过、有偏的**。写策略决定了以后能回忆起什么；agent 只记成功不记失败，也会得到一个过度乐观的 memory
- 🧭 讲义 Diary Decision 房间的 lesson：「写路径才出事故；**provenance 和 privacy 是否决项，不是权重**」——有些东西再重要也不该写（隐私）
- 我的答案：
- 搭档 / 全班：

### Deck p.10 · Experiment 5 · Shoelaces（30 秒）

> *Describe, in words alone, exactly how you tie your shoelaces. Go ahead. The room is listening.*

- 🧭 **能力和回忆分开住**：手会系，嘴说不清。系鞋带是 **procedural memory**（knowing-how），不是 declarative（knowing-that）→ H.M. 病人：不记得练过，镜像画图却越来越好
- 🧭 = **procedural = skill library**：skill 是「合并过的程序」，episodes（练过很多次）进，一条规则出；而且写成文字后会丢东西 → W3 写 SKILL.md 时的感受
- 🧭 讲义 Postscript 的呼应：J-space 外 93% 的激活里跑的是解析、流畅、熟练回忆 = **能做但说不出**
- 我的描述：
- 全班：

- 补充：系鞋带 = 两个半结（half knot）；第二个用环代替绳头 = **bow knot / double-slipped reef knot（双活扣平结）**；第二个结方向和第一个相同 = **granny knot**（环竖着、易松）。手做了几千次，名字今天才知道

## Deck p.11 · Milestone · Act II of II：Facts in Spacetime

> *A fact is not a row in a table. It is a **world-line** — a birth, a death, and a trajectory between.*

- Prototype deck 分两幕：**Act I = 实验 1–5**（记忆怎么写、怎么读、怎么改写、能力 vs 回忆）；**Act II = 实验 6–11**（事实和时间）
- 🧭 「world-line」借自相对论：一个物体在时空里的轨迹。事实也一样：**出生**（开始成立）→ **轨迹**（会变化）→ **死亡**（不再成立）
- 🧭 「不是表里的一行」= 反对把事实压成一个**无时态的当前值**（`city = Santa Clara`）。对应讲义 Act III：**双时态**（valid time + transaction time）、**invalidate 而不是 delete**、矛盾是一等公民
- 接下来的实验：6 Answer as-of（区间）、7 Two clocks（两个时间戳）、8 World-line（画轨迹）、9 演变 / 纠正 / 矛盾、10 Zombie fact（复习 ≠ 有效）、11 When did it end?（结局不打招呼）

### Deck p.12 · Act II · Experiment 6 · Answer as-of（≈ 3 min）

> *Your job title. Your address. Your favorite food. Answer each three times: as of 2015 · as of 2020 · today. Was any answer ever **wrong**?*

- 🧭 答案：**没有一个是错的**，每个答案在它的时间段里都是对的，只是**过期**了。事实 = 值 + **有效区间**（valid from … to …）
- 🧭 「as-of 查询」是数据库里的正式概念（temporal database / time-travel query：`AS OF '2015-01-01'`）。只存当前值的表回答不了「2015 年时他住哪？」
- 🧭 agent 对应：新值来时 **close 旧值的有效窗口**（invalidate），不要 overwrite / delete → 讲义 Zep/Graphiti、Mem0 的 DELETE = invalidate
- 我的答案：（个人信息只写纸上）

### Deck p.13 · Act II · Experiment 7 · The two clocks（≈ 4 min）

> *A divorce, a departure, a death — that you learned about **months late**. Place it on a timeline. How many timestamps does it need? And in March, answering in perfectly good faith — what would you have said?*

- 🧭 **两个时间戳**：① **event time / valid time**：事情在世界上发生的时间（如 1 月）；② **ingestion time / transaction time**：你**知道**的时间（如 6 月）
- 🧭 3 月时你会**真诚地说出旧事实**：对世界是错的，对「你当时相信什么」是对的，不是撒谎。两者之间的空档就是**审计住的地方**
- 🧭 讲义例子：「agent 为什么订了飞往旧办公室的机票？」→ 要重建**行动那一刻它相信什么**，只有第二个时钟能回答。= **bi-temporal**（Zep / Graphiti 的双时态边）
- 🧭 只存一个时间戳的 memory：要么分不清「什么时候变的」，要么分不清「什么时候知道的」→ 没法区分 agent **犯错**和 agent **信息滞后**

### Deck p.14 · Experiment 8 · Draw the world-line（未截图）

### Deck p.15 · Act II · Experiment 9 · Evolution, correction, or contradiction?（classify each pair aloud）

> *Naive memory systems apply one rule to all four: **newer wins.***

- 四组分类和处理见 [lab-log 实验 9](lab-log.zh.md#实验-9-配对)
- 🧭 三种情况要三种操作：evolution → **close 有效窗口**（supersede）；correction → **tombstone**；contradiction → **`conflicts-with` 边，读时解决**
- 🧭 「newer wins」= 覆盖写 = 讲义说的「急切解决 = 穿着整洁外衣的数据丢失」。对 Alice/Bob 尤其危险：谁后说谁赢，是随机的
- 🧭 Pluto 是陷阱题：看起来像纠错，其实是**定义演变**（2006 IAU）

### Deck p.16–18 · Experiments 10–11（未截图：Zombie fact、When did it end?）

### Deck p.19 · Coda · The motivation for the whole day：The hundred-million-year prototype

> *Every agentic memory architecture we build today is **anthropomorphically inspired** — tiers, cues, consolidation, forgetting, write policies. All borrowed from the mind.*
> *Evolution ran that design search for **a hundred million years**, across species — against the very constraints we face: finite attention, costly storage, action under uncertainty.*
> *Borrowing it was our surest bet — an **a posteriori belief**, backed by the longest field test ever run. The great miracle: it seems to have worked.*

- 🧭 标题的意思揭晓：「一亿年的原型」= 人脑。进化是一场跑了一亿年的设计搜索（像 GEPA 的搜索，只是 budget 是一亿年）
- 🧭 为什么照抄人脑合理：约束相同 → **有限注意力**（= context window）、**昂贵的存储**（= token 成本）、**不确定下行动**（= agent 要在信息不全时做决定）
- 🧭 **a posteriori**（后验）：不是先验推理出来「应该这样设计」，而是**看结果**：人脑这套跑了一亿年还在用，所以值得借。讲义 Postscript 呼应：Anthropic 在权重里也找到了类似的工作区 → 「the wager paid a second time」
- 🧭 上午 11 个实验 = 把这套原型的每个器官（tiers、cues、consolidation、forgetting、write policy）亲手摸一遍；下午理论只是给它们起名字
- ⚠️ 讲义的提醒：借的是**蓝图，不是局限**（we borrowed the blueprint, not the limits）

### Deck p.20 · Coda · And one twist to leave burning：We borrowed the blueprint — not the limits

> *Agents already do what evolution never granted us: **verbatim replay** of any episode · **transplantable memories** — one mind's past, copied into another · **shared procedural memory** — one skill, a thousand agents.*
> *The anthropomorphic design is the launchpad, not the ceiling. This afternoon, we build past it.*

| agent 能做、人脑不能 | 对比上午的实验 | 对应机制 |
| --- | --- | --- |
| **逐字重放**任何一段经历 | 实验 3：人脑每次回忆都在重写（斯人 / Vader） | append-log 原样保存，永不编辑 |
| **可移植的记忆**：一个 agent 的过去复制给另一个 | 人脑的经验只能靠讲述，传的过程就失真 | memory 文件 / 向量库直接拷贝；sub-agent 回传 report |
| **共享程序性记忆**：一个 skill，一千个 agent 用 | 实验 5：系鞋带的手艺说不出口、教不过去 | skill library：写成 SKILL.md 就能分发 |

- 🧭 「launchpad, not the ceiling」：人脑是起点，不是上限。照抄结构，但不照抄它的毛病（重写、失真、不能共享）
- 🧭 反面风险（讲义 Act III）：能复制、能共享 = 也能**复制错误和投毒**（一条被投毒的 memory 传给一千个 agent）→ 所以需要 governor
- 上午 Prototype 结束 → 下午理论

## 下午 · Act I 理论

（新 deck：**A Garbage Collector for the Mind · Fall Weeks 9–10**）

### Deck p.7 · Orientation · Last week's Owl：Week 8, in five lines

1. **优化器加不了事实**：缺的是关于你系统的**信息** → 优化；缺**知识** → 检索；缺**能力** → 换 / 训模型
2. 缺信息时，**prompt 优化过的便宜模型**能追平或超过前沿模型
3. **反馈通道承载证据**：一句点名失败原因的话，才是 Reflecting Genie（GEPA）学习的东西
4. **示例能装下指令说不出的东西**（Stall 2 Taxonomy：MIPROv2 靠 demos）
5. **把 0 分当分数读之前，先查是不是拒答**（0 可能是模型拒绝 / 格式失败，而不是能力不行）

- 🧭 对照我的 [W8 worksheet](../ai-agents-week-08/lab-log.zh.md)：Registry GEPA 30/30、MIPRO 0 = 第 2、3 条
- 🧭 第 1 条和今天的桥：「知识 → 检索」= memory 的 semantic 层读路径（RAG）；今天要补的是 **write / consolidate / forget**
- 🧭 第 5 条 = 今天 Flood 实验的同一句话：**先查 cue / 管道，再下结论**

### Deck p.9 · Story of the Day 1/3：An agent that cannot remember is Sisyphus（约 13:20）

> *Condemned to roll the boulder up and watch it roll back, forever — a Groundhog Day in which nobody ever learns the piano.*
> *An agent without memory is Sisyphus with a fresh context window — **every session a first day, every lesson re-derived at full price** —*
> *Not a metaphor of mood. A precise engineering statement about where the value of eight weeks either **compounds** or **leaks away**.*

- **Sisyphus（西西弗斯）**：希腊神话，被罚永远把巨石推上山，到顶又滚下来，从头再推
- **Groundhog Day（《土拨鼠之日》，1993 电影）**：主角被困在同一天无限循环；电影里他靠记住每一天，最后学会了弹钢琴。slide 反过来说：如果连他也记不住，就永远学不会
- 🧭 「re-derived at full price」：没有 memory 的 agent 每次都要**重新付 token 和推理成本**把上次学会的东西再推一遍 → 讲义「Sisyphus got a notebook: externalization 让巨石停在昨天推到的地方」
- 🧭 「compounds or leaks away」：前八周的成果（prompt、skill、GEPA 优化出的指令）**写到磁盘**才会复利；只在 context 里 → 下次 session 就蒸发（讲义 A Gentle Re-Entry）
- 课堂 chat：有同学问午饭时间（13:20）

### Deck p.10 · Story of the Day 2/3：For two weeks the prompt became trainable

> *GEPA bred candidate texts under a validation gate; in the Bazaar, a cheap model with an optimized prompt beat a frontier model on the Registry. But notice what quietly made any of it matter: the improved instruction was **written to disk**.*
> *In the context window alone, the whole overnight run evaporates at the next session boundary. This week, the past becomes manageable.*

- 🧭 W7–W8 的成果之所以有用，是因为优化出的 prompt **存成了文件**（DSPy `save()` / 我 W8 `runs/` 里的输出）。不存盘，跑一晚上的优化下次 session 就没了
- 🧭 = 我自己的 W8：Registry GEPA 30/30 的那份指令如果没存，下次还得再花 ~$0.8/seed 重跑 → Story 1 的「re-derived at full price」
- 🧭 「written to disk」= 讲义的 **EXTERNALIZE**：写到持久存储，eviction 就变成 paging，能完整找回
- 口头：**compare with frontier models and open weight models**（讲师提到；具体内容待录播核实）
  - frontier = 闭源最强模型，只能经 API 调用（只能改 prompt / context）；open-weight = 权重公开，可自己部署、微调、控制 KV-cache
  - 🧭 memory 住在 **harness** 里，所以对两者都适用；W8 的结论：缺信息时，便宜/开源模型 + 好 prompt + 好 memory 可以追平 frontier
- 🧭 「the past becomes manageable」：这两周讲的不是「存起来」，而是**怎么管**

### Deck p.11 · Story of the Day 3/3：Three debts fall due together

三张欠条今天一起兑现：

1. **Simulacra 论文**（Generative Agents），W2 读过 ——「almost the founding paper for how memory would be created」→ 今天讲它的 stream + 三项打分 + reflection（[我的精读](../../Generative%20Agents%20论文精读笔记.md)）
2. **MemGPT**，W2 那晚和 W3 都说「another paper we'll do」→ 今天：context = RAM，store = disk，agent 自己分页
3. **一整周的 memory 架构**，Skills day 承诺的 → 现在是两个周日（W9 + W10）

> *Today the tangential becomes thorough — centered deliberately on the part every curriculum skips: **the context lifecycle**.*

- 🧭 「每门课都跳过的部分」= 回收：compaction、GC、有意遗忘（讲义 Act II，W10 的重头戏）
- 🧭 W3 欠的那条：skill library = **procedural memory**，今天正式给出四层分类来还债
### Deck p.12 · Headline I · The Boundary：One hard boundary orbits everything

> *At the moment of generation, the model conditions **only** on the tokens resident in its context window. Whatever is not there, at the instant of the forward pass, **does not exist** for it. Not "exists but is hard to reach." Does not exist. No back-channel to the disk, no wormhole to last week's conversation.*

- 🧭 = 讲义 §2.1（[精读](lesson-plan-精读.zh.md#21-边界以及harness-在记)）：memory = 窗口外、**可以被换入**的东西；memory 系统的核心动作是**跨越边界**
- 🧭 和人脑的对比：上午 Flood 实验里，味噌汤的记忆「一直存着，只是没被唤起」= **exists but hard to reach**。模型不是这样：不在窗口里就是**不存在**，没有气味能把它勾出来，只有 harness 把它放回窗口
- 🧭 所以「the model remembers」是错的说法；记住的是 **harness**（我们的代码）
- 🧭 权重里的知识（训练学到的）不算这里的「memory」：那是 parametric，改不了也换不进换不出

### Deck p.13 · Headline I · Memory, defined

> ***Memory is everything outside the context window that can be paged into it** — the dormant remainder, eligible to be summoned.*
> **context window = the resident present** · **memory = the dormant, pageable rest**
> *The defining act of a memory system is not storage. It is the **crossing of the boundary** — the right dormant token at the right living moment.*

- 🧭 两个词：**resident**（常驻、此刻在场）vs **dormant**（休眠、不在场但可召回）；**paged into** 借自 OS 分页：从磁盘把一页换进内存
- 🧭 关键在「**can be** paged into」：存了但永远调不回来的不算 memory，只是存储
- 🧭 「right token at right moment」= 读策略的两个问题：**什么**（relevance）+ **什么时候**（timing）。对应 VoR = p·g − κ(c)：时机对了 p 才高
- 🧭 和上午 Flood 的对应：味噌汤的香气 = 让「对的记忆在对的时刻」跨过边界的那个 cue

### 板书 ① · 河、船、摆渡人（OneNote，p.13 之后）

**画面**：
- 中间一条**河**（两条波浪线之间），标「river」
- 河上一条**船**，标「**context window**」，船里有几个 token（小圆圈）
- 船边一个**摆渡人**（ferryman），在划桨
- 船 → 箭头向上 → **Model (llm)** → 箭头向下 → **response**
- 河的另一边（底部）写着：**skills, knowledge / semantic memory, episodic memory**

**结构**（课上确认：**模型和 context window 在同一岸**）：

| 这一岸（上） | 河 | 对岸（下） |
| --- | --- | --- |
| context window + **Model (llm)** → response | 硬边界 | skills · knowledge / semantic memory · episodic memory |

**课上确认**：ferryman 是**把东西放进 context window 的那个角色**，是 **harness 的一部分**（不是 harness 的全部：harness 还包括 agent loop、工具调用、compaction、guardrail 等）。⚠️ 术语注意：把东西放进窗口，讲义叫 **read / page in**；**write** 指的是反方向：从窗口写到对岸的 memory store。

**我的理解**：
- 🧭 **河 = 那条硬边界**；模型住在 context window 这一岸，**永远过不了河**；memory 的各层（procedural / semantic / episodic）都在对岸
- 🧭 **摆渡人 = harness**：把对岸的东西运过河、送进 context window（read / page in），也把这边的东西运回对岸存起来（write / externalize）。「the harness remembers, not the model」
- 🧭 模型只看见自己这岸的东西 → p.12「不在窗口里就不存在」
- 🧭 「crossing of the boundary」= 摆渡这个动作本身；memory 系统的价值全在摆渡

**板书 ①b · 加上两样**：

1. 船（context window）旁边用蓝笔写了 **Context Engineering**
   - 🧭 = 决定船上放什么的手艺。讲义收尾：prompts、skills、tools、prompt 优化、memory 五周 = **同一门学问：context engineering**
2. 左下角画了一个**容器**（蓝框），里面粉色斜线填到一半，两条刻度：**high water mark**（高水位）和 **low water mark**（低水位）
   - 🧭 = 讲义 Act II 的**水位线**（W10 内容提前出现）：context 填到**高水位**（如 0.85·B）就触发回收 / compaction，回收到**低水位**（如 0.55·B）就停，**永远不清到 0**，否则策略来回抖动（thrash）
   - 🧭 两条线之间的空档 = 给下几轮对话和摘要本身留的余量；也是 Practice I 里「70–80% 触发，别在 99% 恐慌压缩」
   - 容器底部还有一层**黄色**（低水位以下），推测 = 压缩后**留下来的部分**：pinned roots（system prompt、约束、目标）+ 摘要 + 最近的工作集（⚠️ 待核实）
4. 对岸清单末尾用粉笔加了 **tools**（下面画了两道线强调）→ 对岸现在是：**skills · knowledge / semantic memory · episodic memory · tools**
   - 🧭 工具也在窗口外：工具的**定义**（schema）和工具的**结果**都要由 harness 摆渡进窗口才对模型存在
   - 🧭 讲义 Act II：工具结果是窗口里**最大的垃圾来源**（动辄几万 token 的文件 dump）→ 先清旧工具结果，再考虑有损压缩；W5–W6 Toolcraft 讲的 tool 描述也一样要占船位
3. 底部画了一条粉色**锯齿波**（sawtooth）
   - 🧭 = context 占用随时间的曲线：每轮对话**慢慢涨**（斜线上升）→ 碰到高水位 → compaction **一下掉**到低水位（竖线下降）→ 再涨 → 再掉
   - 🧭 讲义原话「Act II derived the sawtooth; here we set its teeth」：锯齿的**齿高** = 高低水位之差，**齿距** = 多久压缩一次。压缩太频繁 → 每次都全价重算缓存（Manus 的缓存账）；太少 → 窗口太满，注意力被稀释（context rot）
   - 🧭 每一次下降都是一次**有损**操作 → 递归压缩会让细节几何衰减（0.9¹⁰ ≈ 0.35）→ 所以要 anchored summarization + preservation gate

### Deck p.14 · Headline I · Drawn：Context is RAM; memory is disk

金字塔三层（上小下大）：

| 层 | 内容 | 性质 |
| --- | --- | --- |
| **context window** = working memory（RAM） | 模型此刻能看到的 | fast, tiny, priced；**the only reality the model acts on** |
| ——— **the context boundary — absolute** ——— | | |
| **recall store** | recent sessions, searchable | 中间层 |
| **archival store** | all sessions · facts · skills | disk：slow, vast, cheap |

- 左箭头 **page out（write, evict）**：窗口 → 下层；右箭头 **page in（retrieve）**：下层 → 窗口
- > *The only traffic that matters is the paging across the boundary. Everything on the right is invisible until something copies it left.*
- 🧭 = **MemGPT / Letta** 的三层：core（窗口里的常驻 block）/ recall / archival（讲义 §3.4、§4.1）
- 🧭 和白板对上：金字塔顶 = 河这岸的船；虚线 = 河；下两层 = 对岸；两条箭头 = 摆渡人来回（page in = read，page out = write / evict）
- 🧭 「priced」：窗口里每个 token 每轮都要付钱 + 注意力税 → VoR = p·g − κ(c)

### Deck p.16 · Headline 3 · The most useful table of the day：Four tiers, four agent realizations

（p.15 未截图）

| Human tier | What it holds | Agent realization | 上午实验 |
| --- | --- | --- | --- |
| **Working** | what is thought **now** | **the context window itself** | 白板上的船 |
| **Episodic** | what **happened** | the trace store — transcripts, logs | 1 Three days、2 Flood（味噌汤） |
| **Semantic** | what is **true** | extracted facts — read-path **is RAG** | 6 Answer as-of、9 分类 |
| **Procedural** | how things are **done** | **the skill library** | 5 Shoelaces |

> *"We gave the agent memory" + a vector store of facts = the semantic tier, and nothing else.*

- 🧭 和白板对岸清单一一对上：episodic memory / knowledge·semantic memory / skills；working = 船本身
- 🧭 底下那句是警告：很多人说「给 agent 加了 memory」，其实只是接了个向量库 → 只做了**一层的读路径**；没有 episodic（原始日志）、没有 procedural（skill）、也没有 write / consolidate / forget
- 🧭 procedural = skill library「不是类比，是同一个东西」→ W3 的债还清；Shoelaces 实验的身体感受 = 会做 ≠ 说得出
- 🧭 episodic → semantic 的转换 = **consolidation**（从「发生了什么」里提炼「什么是真的」）；episodic → procedural = 从经历里编译出 skill（SOAR chunking / Voyager）

### Deck p.17 · Headline 4 · Four verbs：Write · read · consolidate · forget

一个循环（WRITE → READ → CONSOLIDATE → FORGET → WRITE），中心是 **one optimization：what deserves the context window, under a scarce budget**

| 操作 | slide 原文 | 理论根基（斜体小字） | 上午实验 |
| --- | --- | --- | --- |
| **WRITE** | what deserves an entry — importance triaged **at birth** (ι_i) | semantic triage | 4 Diary decision（拍婚礼不拍通勤） |
| **READ** | recency × importance × relevance; paged in only if **VoR(m) > 0** | scoring + paging economics | 2 Flood（cue） |
| **CONSOLIDATE** | lossy compression against **behavior** — **append, never rewrite** | rate–distortion | 3 Edited narrative（重写的危害） |
| **FORGET** | eviction by policy: soft LRU, TTL, supersession, the user's right | cache theory | 10 Zombie fact、11 When did it end? |

> *Four faces of one optimization: what, under a scarce budget, deserves to occupy the only reality the model inhabits.*

- 🧭 slide 上 READ 是 **recency × importance × relevance**（乘号）；讲义里 Smallville 原式是**加权和**（三项 min-max 归一化后相加，权重都是 1）。⚠️ 待核实是 slide 的简写还是有意改成乘法（乘法的话一项为 0 就整体为 0）
- 🧭 **ι_i**（iota）= importance，写入时 LLM 打一次分（1–10），存下来不再重算
- 🧭 **VoR(m) = p_m·g_m − κ(c_m)**：相关概率 × 收益 − token 注意力税；> 0 才值得换入
- 🧭 **rate–distortion**（率失真，信息论）：压得越狠（rate 低）失真越大；consolidation 要按「**行为**是否还对」来衡量失真，而不是按文字像不像
- 🧭 **soft LRU**：Smallville 的 recency 从**上次访问**算起 → 常用的不衰减，像 LRU 缓存；**TTL** = 生来就有有效期；**supersession** = 被新值取代（tombstone）；**the user's right** = 被遗忘权
- 🧭 「Storage」不在四个动词里：存很容易，**策略**才是全部

### Deck p.18 · Headline 5 · The most humanistic point：Forgetting is a feature, thrice over

| 理由 | slide 原文 | agent 例子 | 上午实验 |
| --- | --- | --- | --- |
| **Privacy** | a system that cannot forget on request is **unshippable** | 用户要求删除；GDPR 被遗忘权 → 要追到索引、摘要、衍生物里一起删 | — |
| **Staleness** | an expired truth is worse than none — it is **confidently wrong** | 用户搬家了，agent 还按旧地址寄 | 10 Zombie fact（童年电话号码） |
| **Relevance drift** | last quarter's facts distract from this quarter's task | 上季度的价格 / 方案混进这次回答 | 6 Answer as-of |

> *Borges filed the definitive engineering report in 1942: **Funes**, who forgot nothing, could no longer think — because **thinking is forgetting a difference**. The librarian who never throws anything away does not own a library; the library owns him.*

- **Funes**：博尔赫斯短篇《博闻强记的富内斯》（*Funes el memorioso*, 1942）：主角记得一切细节，却无法抽象、无法思考
- 🧭 「thinking is forgetting a difference」：抽象 = 忽略差异（三条狗各不相同，忘掉差异才有「狗」这个概念）= **consolidation**：从 episodic 细节里提炼 semantic 事实，必须丢掉细节
- 🧭 「confidently wrong」比「不知道」更糟：不知道 agent 会去查；记着过期事实会**自信地答错** → 要 TTL、supersession、tombstone
- 🧭 对 agent：全都塞进窗口 = Funes → 注意力被稀释（context rot）；什么都不删的 store = 那位图书管理员

### Deck p.19 · Headline 6 · The one sentence to carry out of today：Memory is not storage; it is policy

> *What to **write** out of the context window · what to **read** back in · how to **consolidate** the raw past without collapsing it · what — deliberately, defensibly — to **forget**.*
> *Storage is easy. The policy is the whole game.*

- ⭐ **今天的一句话**（= 讲义开篇那句）
- 🧭 四个动词的方向都以 **context window** 为中心：write = 写**出**窗口；read = 读**回**窗口
- 🧭 「without collapsing it」= 合并时别把细节压成糊糊（ACE 的 context collapse；讲义 Act II 的 compaction amnesia）
- 🧭 「deliberately, defensibly」：遗忘要**有意**（有策略，不是被动丢）且**可辩护**（能说清为什么忘、留审计记录）
- 🧭 存储是商品（向量库、文件、数据库随便选）；差异全在策略上 → 也是 capstone 该花力气的地方

### Deck p.20 · Orientation · Three open questions：Three questions we cannot yet answer

1. *A chatbot greets you by name three turns later. **What, exactly, did the remembering** — the model, or something else?*
2. *The window fills; the harness summarizes the history and continues. **What can silently vanish — and how would you prove nothing did?***
3. *A fact changes — "deploy to `us-east`" becomes "deploy to `us-west`". **Is deleting the old fact the right move?***

我的预答（讲义里有答案，Deep dive 后核对）：

| # | 预答 | 讲义位置 |
| --- | --- | --- |
| 1 | **harness**，不是模型：代码把名字存下来，下一轮重新塞进 prompt。模型跨调用无状态 | Act I §2.1 |
| 2 | 会悄悄丢掉**事后才显出重要的事实**（compaction amnesia），比如中途的一次更正；证明方法 = **plant → compact → probe**：压缩前准备一组「必须还能答出」的问题，压缩后断言都能答对（preservation gate） | Act II §3.2、Practice I §5.4 |
| 3 | **不对**。这是 evolution（演变），应 **invalidate 不 delete**：关闭旧事实的有效窗口（valid_to = 变更时间），新事实生效；保留历史才能回答「上个月部署到哪」「agent 为什么部署错了」（两个时钟） | Act III §4.2；上午实验 6、7、9 |

- 🧭 三个问题分别对应三幕：Q1 = Act I（谁在记），Q2 = Act II（context 生命周期），Q3 = Act III（时间与治理）

### Deck p.22 · 12:45 · Paper and pen, now：You are the dataset

> *Laptops closed. One worksheet, one pen. Eleven short experiments on the only memory system in the room that already ships.*
> *Then laptops open, and **the Genie remembers nothing at all**.*

- Orientation deck 的最后一页 = 过渡到 Prototype 实验（原定 12:45；实际上午已经做完，这里是回顾）
- 🧭 「Then laptops open」= 下一段：**Memory Palace** 实验（kit `labs/genies-memory-palace`），从一个**什么都不记得的 Genie** 开始，一层层给它加 memory（Foyer → Flood → Shoelaces …）
- ⏭️ 待下载手册和 kit

### Deck p.27 · The Memory Palace · In every room：Predict, play, read, change, verify

| 步骤 | 做什么 |
| --- | --- |
| **Predict** | 按任何键之前，先写下你认为会发生什么 |
| **Play** | 运行，读那条 bar：Genie **看到了什么**，一个 band 一个 band、一个 token 一个 token |
| **Change** | 改**策略**，永远不改 Genie：一个权重、一个 pin、一个 prompt、一条规则 |
| **Verify** | 用**十几个没见过的 case** 检验，打分用**不调用模型**的确定性检查 |

- 🧭 「never the Genie」= 模型不动，只动 harness 的策略（memory is policy）
- 🧭 Verify = W7/W8 的 sealed test + 讲义「plant–distract–probe」；不用 LLM judge 打分 → 避开 judge 偏差

### Deck p.28 · The Memory Palace · Logistics：Partners, keys, lunch

- **Setup**：`uv sync`，然后 `uv run memory-palace`；先读手册前两页
- **Key**：用已有的 OpenRouter key；默认开启 zero data retention
- **No key?** 每个房间都有不调用模型的 **replay 模式**
- **Lunch**：在座位上吃；告诉邻座 Genie 忘了什么

### Deck p.29 · Before the Flood · A quick one, out loud：Answer instantly, together, on three

> ***How many animals of each kind did Moses take on the ark?*** One… two… three —
> *Say it before you think. That is the experimental condition, not a trick.*

- 答案：**一只都没有**，造方舟的是**诺亚**，不是摩西。多数人会脱口而出「两只」
- 🧭 = 心理学的 **Moses illusion**（摩西错觉，Erickson & Mattson 1981）：问题和记忆**大致匹配**（都是圣经人物），大脑就不检查细节，直接检索出答案
- 🧭 Flood 房间的 lesson：**先查 cue，再怪 store**。记忆库里的事实没错，是**查询（cue）本身有错**，检索却照样返回了「看起来对」的答案
- 🧭 agent 对应：向量检索按**语义相似**匹配，「Moses + ark」和「Noah + ark」embedding 很近 → 检索器会自信地返回诺亚的事实；问题里的错误前提没人发现 → 讲义「the agent must ask the right question of its own memory」+ query rewrite

### Deck p.31 · 15:00 · Close the laptops：Two questions for the deep dive

1. *In the Flood, which weight had to **lead** — and why did the paper's equal weights fail?*
2. *In Shoelaces, what did your recipe keep that **no single trace** contained?*

> *Hold your answers. Act I gives them names.*

我的预答（⚠️ 我没跑 kit，按讲义推断，做完房间后改）：

| # | 预答 | 依据 |
| --- | --- | --- |
| 1 | 多半是 **relevance**（和当前问题的相关度）要领头。Flood = 大量记忆涌进来，其中很多**很新**或**看起来很重要**但和问题无关；三项权重都是 1 + min-max 归一化时，recency / importance 会把真正相关的那条挤下去 | 讲义：「recency, importance and relevance each catch a different failure; **the weights are policy**」；retrieval config 里 relevance = 1.0 是基线 |
| 2 | **跨多次经历的规律**：哪些步骤每次都一样（不变量）、在什么条件下要变、为什么这样做。单条 trace 只记了「那一次」怎么做，规则是从多条里**归纳**出来的 | 讲义 Shoelaces lesson：「a skill is consolidated procedure: **episodes in, a rule out**」；SOAR chunking / Voyager |

- 🧭 Q1 = Act I §2.4 的 Smallville 打分 + 消融病症；Q2 = §2.2 procedural = skill library + consolidation

### Deck p.5 · Two epigraphs to hold all day：Funes, and the loom

> *To think is to forget a difference, to generalize, to abstract. In the teeming world of Funes, there were nothing but details.* — Jorge Luis Borges, *Funes the Memorious*
> *Memory is our coherence, our reason, our feeling, even our action. Without it, we are nothing.* — Luis Buñuel, *My Last Sigh*
> *The first is the engineering warning. The second is the reason we bother. Every slide today lives between them.*

- 🧭 两句话是今天的两极：**Borges = 记太多的危险**（什么都不忘就不能抽象 → forget / consolidate）；**Buñuel = 记太少的代价**（没有记忆就没有连贯性 → 西西弗斯）
- 🧭 Buñuel（布努埃尔，西班牙电影导演）晚年回忆录开篇写他母亲失忆，认不出自己的孩子
- 🧭 memory 策略就是在两极之间找平衡：留够让 agent 连贯的，忘掉会淹没它的

## Deep dive

### Deck p.32 · The map of the deep dive：Three acts over two Sundays

| 站 | 名字 | 周 | 讲义章节 |
| --- | --- | --- | --- |
| Prologue | **The Debts**（三笔欠账：Simulacra、MemGPT、memory 周） | W9 | Story 3/3 |
| Act I | **The Tiers**（边界、四层、四个动词、Smallville 打分） | W9 | [精读 §2](lesson-plan-精读.zh.md#2-act-iw9--memory-是什么) |
| Act II | **The Lifecycle**（heap、compaction、GC、回收三难） | W10 | 精读 §3 |
| Act III | **The Governor**（谱系、两个时钟、分区、写策略、评测、治理） | W10 | 精读 §4 |
| Postscript | **The Wild & the Weights**（生产系统 Claude Code / OpenClaw / Hermes + 权重里的工作区 J-space） | W10 Speakeasy | 精读 §7 |

### Deck p.35 · Act I · Checkpoint 1：Say it back

| 问题 | 答案 |
| --- | --- |
| 生成那一刻，模型**唯一**依赖的是什么？ | **context window 里的 token**（不在窗口里 = 不存在） |
| 补全定义：memory 是窗口外所有能被 ___ 的东西 | **paged into it**（换入窗口 / summoned） |
| 聊天机器人三轮后叫出你的名字，是谁在记？ | **harness**（代码存下名字、下一轮再塞进 prompt），不是模型 |

- p.36 揭晓 ✅ 三题全对：
  1. *The tokens resident in the context window. Whatever is not there, at that instant, does not exist for it.*
  2. *Paged into it — the dormant, pageable rest, eligible to be summoned.*
  3. *The harness. The model is stateless across calls; **the remembering mind is manufactured, every turn, by plumbing**.*
- 🧭 Foyer G2 亲手验证过第 1、3 题：关掉 pinned notes + recent turns，Genie 就不知道 $4,800

### Deck p.37 · Act I · The taxonomy, first cleaving：Tulving, 1972: episodic vs. semantic

| | Episodic | Semantic |
| --- | --- | --- |
| 记什么 | **events**（事件） | **facts**（事实） |
| 特点 | time-stamped, first-person, re-livable（有时间戳、第一人称、可重温） | de-contextualized, tenseless（脱离情境、无时态） |
| 例子 | What I had for breakfast | Paris is the capital of France |
| agent | trace store（日志、对话记录） | 抽取出的事实库（读路径 = RAG） |

> *You know Paris is a capital; you have long forgotten the afternoon you learned it. **The event decayed; the fact consolidated.***

- 🧭 「first cleaving」= 分类学的第一刀（Tulving 1972）；第二刀是 Squire 的 declarative vs. procedural（下一页）
- 🧭 「event decayed, fact consolidated」= **consolidation**：从多次经历里提炼出事实，经历本身可以忘 → 刚才 Shoelaces：838 token 的 traces → 170 token 的 skill；味噌汤：记得「在日本工作过」（事实）+ 具体某天（经历）
- 🧭 我的例子：「天将降大任于是人也」是 semantic（原文），小学那堂课是 episodic（早忘了）
- ❓ 我的问题：**情绪算哪一层？** 整理：
  - 情绪**不是单独一层**，它出现在两个地方：① 作为 episodic 记忆的**调节器**：情绪强烈的事件记得更牢（杏仁核增强海马体的编码和巩固）；② 在 Squire 分类里，**情绪条件反射**（比如被狗咬过后见狗就紧张）属于 **nondeclarative（非陈述性）** 记忆，和 procedural 同一边
  - **闪光灯记忆**（flashbulb memory）：情绪越强越觉得记得清楚，但准确度不一定更高 → 自信 ≠ 正确（= 实验 3 被改写的记忆）
  - 味噌汤：嗅觉直通杏仁核和海马体，所以气味 cue 特别能勾起带情绪的回忆
  - **更正**：情绪也是记忆的**内容**：情绪词汇 / 概念 = semantic；某次经历里的感受（「那次我很愤怒」）= episodic 的一部分；身体反应 = nondeclarative；强度 = 调节器
  - 例：「某次被冤枉，很愤怒」→ 事件 + 愤怒 = **一条 episodic**；记得特别牢 = 强度高（importance 高）；提起就火大 = 非陈述性反应；总结出「我讨厌被冤枉」= consolidation 成 **semantic**；每次回忆愤怒程度会变 = 回忆即重写
  - 🧭 agent 对应：Smallville 的 **importance** 就是情绪显著性的替身：原论文让 LLM 给记忆的 **poignancy**（触动程度）打 1–10 分，刷牙 = 1、分手 = 10 → 情绪 ≈ 写入时的权重，而不是一个记忆层

### Deck p.38 · Act I · Second cleaving：Squire: knowing-that vs. knowing-how

- **Declarative**（陈述性）— what you can **state**；**Procedural**（程序性）— what you can only **do**
- *You can declare that a bicycle has two wheels, but you can only ride.*
- > *The haunting natural experiment: the patient **H.M.**, unable to form new declarative memories, improved at mirror-drawing across sessions he swore he had never attended. Procedural memory, intact, learned what declarative memory could not even record.*
- 配图：Larry R. Squire（神经科学家）
- 🧭 = 上午实验 5 Shoelaces：会系，说不清
- 🧭 H.M.（Henry Molaison）：1953 年为治癫痫切除了双侧海马体，此后再也形成不了新的陈述性记忆，但镜像描画一次比一次好 → 两种记忆由**不同脑区**负责
- 🧭 agent 对应：declarative = episodic + semantic（trace + 事实库）；procedural = **skill library**（Shoelaces：流程写成 skill）
- 🧭 两刀合起来：declarative 再分 episodic / semantic（Tulving），加 procedural（Squire），再加 working（Baddeley）= 四层

### Deck p.39 · Act I · Third distinction：Baddeley: a desk, not a shelf

- *Working memory is not a passive short-term **store**; it is an **active workspace** — limited capacity, a central executive that **manipulates**, not merely holds.*
- *The word that matters is **active**. It is where thought actually happens.*
- > *Put Tulving, Squire, and Baddeley together, and four tiers fall out — cleanly.*
- 🧭 书桌 vs 书架：书架只是放东西；书桌上的东西正在被**加工**（摊开、比较、改写）
- 🧭 agent 对应：working memory = **context window 本身**，唯一「不存在别处」的一层；模型的推理就发生在这里
- 🧭 「limited capacity」= 窗口预算有限（Foyer：4000 token）；「central executive」≈ 模型在窗口里注意力的分配；也呼应 Postscript：权重里的 J-space 只能同时容纳约 25 个概念
- 🧭 三位学者 → 四层：Baddeley（working）+ Tulving（episodic / semantic）+ Squire（procedural）

### Deck p.40 · Act I · The taxonomy, drawn：The four tiers

| 层 | 名字 | 例子 | 一句话 |
| --- | --- | --- | --- |
| **working memory** | The context window（the resident present） | system prompt · recent turns · tool results | what is thought **now** |
| ┆ the boundary: **crossed only by paging**（page in ← / page out →） | | | |
| **episodic memory** | Event traces | transcripts · action logs · observations | what **happened** |
| **semantic memory** | Extracted facts | preferences · entities · distilled truths | what is **true** — read-path: **RAG** |
| **procedural memory** | The skill library | `transcript-cleaner/` · `study-roadmap/` · `expense-report/` | how it is **done** — SKILLCRAFT |

右边三层框在虚线里：*the external store — dormant on disk, eligible to be paged in*

> *Working memory is the one tier not stored anywhere — it **is** the agent's living present. The other three sit dormant, eligible to be paged in.*

- 🧭 = p.14 金字塔 + p.16 表格 + 白板（河 = 虚线边界；船 = 左框；对岸 = 右三框）合成一张图
- 🧭 skill 例子都带 `/` = 文件夹（W3 Skillcraft：SKILL.md + references/ + scripts/）；SKILLCRAFT = W3 那套讲义
- ❓ 课间问：RAG 为什么不用关系数据库？→ 先分清 **KV cache**（推理时的注意力缓存，窗口之内）≠ **向量库**（窗口外的记忆库）；讲义 Practice I：**substrate follows query shape**，默认就是先用 **日志 + 关系表**，召回不够才加向量索引；关系表擅长精确 key 查询和 `valid_from/valid_to` 失效，查不了「意思相近」（Flood F1）；生产常用 Postgres + pgvector 混合
- 🧭 Memory Palace 一楼三房间 = 这张图的三块

### Deck p.41 · Act I · The debt paid：Procedural memory is the skill library

- *Not analogous. Not adjacent. **The same object under two names** — a thesis, not a throwaway.*
- *On Skills day you heard it called **the recipe-book memory**, with a promise of a whole week for the rest. **Consider the debt paid.***
- 右栏：*Every hard question about memory now has a twin you already answered for skills:*

| skills 的问题（W3–W4） | ↔ | memory 的问题（W9–W10） |
| --- | --- | --- |
| what to author | ↔ | what to write |
| when to trigger | ↔ | when to recall |
| consolidate without drift | ↔ | compress without collapse |
| retire | ↔ | forget |

- 🧭 「debt paid」= Story 3/3 三笔欠账里的第三笔（W3 承诺的 memory 周）
- 🧭 Shoelaces 刚亲手验证：5 条 trace → 一个 SKILL.md = episodic → procedural 的 consolidation
- 🧭 skill 的 description 决定何时被加载（W3 的 trigger）= memory 的 relevance 决定何时被召回（Flood 的 cue）

（p.42 未截图）

### Deck p.43 · Act I · The lineage runs deeper than 2023：SOAR's chunking, four decades early

- *SOAR hits an **impasse** — no rule applies — resolves it by laborious subgoal reasoning, then **compiles** the resolution into a rule that fires automatically thereafter.*
- *Episodic experience becoming procedural memory: **the automatic authoring of a skill**.*
- 右栏：*Voyager's growing skill library is SOAR's chunking wearing a language model's clothes. And **ACT-R's activation equation** — frequency, recency, contextual relevance — is a score we will re-meet within the hour.*
- **SOAR**（Laird, Newell, Rosenbloom，1980 年代）：认知架构；卡住 → 慢慢推理解决 → 把解法编译成规则，下次直接用 = **chunking**
- **ACT-R**（Anderson）：另一个认知架构；记忆的「激活值」由**使用频率、最近使用、和当前情境的相关度**决定
- 🧭 SOAR chunking = Voyager（[我的精读](../../Voyager%20论文精读笔记.md)）= 刚才 Shoelaces：卡住（Meera 纠正）→ 推理（她解释规则）→ 编译成规则（SKILL.md）
- 🧭 ACT-R 的三项 ≈ Smallville 的 recency / importance / relevance（见下）

### Deck p.46 · Act I · The four operations：Every memory system answers four questions

- **Write** — what is worth remembering at all?
- **Read** — what deserves to cross into context **now**?
- **Consolidate** — how does a flood of shallow events become a few durable understandings?
- **Forget** — what should decay, expire, or be superseded?
- > *Notice what is absent: **storage**. The policy on these four verbs separates a system that **remembers** from one that merely **stores**.*
- 🧭 = p.17 循环图的文字版；Memory Palace 一楼：Flood = read，Shoelaces = consolidate；二楼 Diary = write，Two Clocks = forget / supersede
- 🧭 课外实验 [记忆库 metadata 与过滤](../../learning/2026-11-15-memory-store-filters/README.md)：write（填字段 + 按 slot 取代）、read（过滤后检索）、forget（被遗忘权删除）

### Deck p.47 · Act I · The read decision has exact economics：The value of recall

$$\mathrm{VoR}(m) = p_m\, g_m - \kappa(c_m), \qquad \text{page in } m \iff \mathrm{VoR}(m) > 0$$

| 符号 | 意思 |
| --- | --- |
| $p_m$ | 这条记忆**此刻相关**的概率（信念） |
| $g_m$ | 需要时它**在窗口里**能带来的收益 |
| $c_m$ | 它占多少 token |
| $\kappa(c_m)$ | 这些 token 的**注意力税**：成本 + 稀释其他内容 |

- 阈值形式：$p_m > \kappa(c_m)/g_m$ → 相关概率要高过「成本 / 收益」才值得放进来
- 两个杠杆（skills 周已经学过）：让记忆 **discriminative**（该相关时 $p_m$ 高）和 **lean**（$c_m$ 小）
- 例：Shoelaces → skill 170 token vs traces 838 token，收益一样（都 12/12），$c_m$ 小 5 倍 → VoR 更高
- 例：Flood → 调高 relevance 权重 = 提高 $p_m$ 的估计准确度，把相关度低的（e47）挡在窗口外
- 例：Foyer G3 → 放的位置不对，$\kappa$ 涨 58%（缓存失效）
- 🧭 W3 skills：skill 描述要能区分（只在该触发时触发）+ 正文要短（每轮都付费）= 同一笔账

### Deck p.48 · Act I · Work it once：An 800-token episode at the bar

条件：$c_m = 800$ token，$g_m = 0.16$，稀释 = 每 1,000 个驻留 token 0.05，$p_m = 0.20$

| | $\kappa(c_m)$ | 门槛 $\kappa/g$ | vs $p_m = 0.20$ | VoR = $p g - \kappa$ | 结果 |
| --- | --- | --- | --- | --- | --- |
| 原始 episode（800 token） | 0.05 × 0.8 = **0.04** | 0.04 / 0.16 = **0.25** | 0.25 > 0.20 | 0.032 − 0.04 = **−0.008** | **stays out**（不放进窗口） |
| 合并成 150 token 摘要（原文留在磁盘） | 0.05 × 0.15 = **0.0075** | ≈ **0.047** | 0.047 < 0.20 | 0.032 − 0.0075 = **+0.0245** | **pages in**（放进窗口） |

（VoR 一列是我验算的，slide 只给了门槛）

> *You pulled the **lean** lever; the **discriminative** lever never moved. A write-and-consolidate policy is machinery for controlling $p_m$ and $c_m$.*

- 🧭 内容的有用程度（$p_m$、$g_m$）一点没变，只是变短了，就从「不值得」变成「值得」
- 🧭 「leaf kept on disk」：原始 800 token 不删，留在磁盘，需要细节时再调（= externalize；讲义 Act II 回收三难里的 pointer）
- 🧭 = 我的 Shoelaces：838 token traces → 170 token skill
- 🧭 另一个杠杆 discriminative = 提高 $p_m$：Flood 调高 relevance 权重 / F1 改写 cue

### Deck p.49 · Act I · The skills deck's bandit returns：Recall is an explore / exploit gamble

- 每条记忆 = 老虎机的一根臂；$\hat g_m$ = 「召回它有没有帮上忙」的**滑动平均**；按 **UCB** 决定召回：

$$\hat g_m + \beta \sqrt{\frac{\ln T}{n_m}}$$

- $\beta = 1$，$T = 100$（$\ln T \approx 4.605$）：
  - $m_a$：$n_a = 40$，$\hat g_a = 0.6$ → $0.6 + \sqrt{4.605/40} \approx$ **0.94**
  - $m_b$：$n_b = 2$，$\hat g_b = 0.3$ → $0.3 + \sqrt{4.605/2} \approx$ **1.82**
  - → **较弱的记忆被召回，故意的**（它被试得太少，不确定性大）
- *Set the scores equal: $m_b$ stops winning near $n_b \approx 11$. A mediocre memory costs a **bounded** number of wasted recalls before the bonus fades — exploration as a tax.*（验算：$0.3 + \sqrt{4.605/n} = 0.94$ → $n \approx 11.2$ ✓）
- 🧭 W3 skills deck 里同一个 bandit（选哪个 skill）又出现了
- 🧭 $\hat g_m$ 从哪来？要**记录每次召回后有没有帮上忙** → 需要 append-log（见下方问答）

### Deck p.51 · Act I · Checkpoint 3：Say it back

| 问题 | 我的答案 |
| --- | --- |
| 每个记忆系统都要回答的四个操作？ | **write · read · consolidate · forget** |
| 哪个词被**故意**排除在外？ | **storage** |
| VoR = pg − κ(c) 里，让记忆过门槛的两个杠杆？ | **discriminative**（该相关时 p 高）+ **lean**（c 小） |
| bandit 为什么有时故意召回较弱的记忆？ | 它被试得少，**不确定性大**，UCB 给探索奖励；试够次数（约 11 次）奖励就消退，浪费有上限 = 探索税 |

（p.50 未截图；p.52 揭晓答案待核对）

### Parking Board（讲师后台，约 19:00，Open 5）

| 票数 | 提问人 | 问题 | 我的预答 |
| --- | --- | --- | --- |
| 1 | Erwin（14:01） | 怎么衡量 agent 能独立完成的任务复杂度和无人干预的持续可靠运行？用哪些 benchmark？上线前测什么？ | 见上方 14:02 记录：METR time horizon、SWE-bench Verified；τ²-bench pass^k、Vending-Bench；自建日志 eval + no-regress gate |
| 0 | Senthil（18:33） | consolidation 能生成 procedural memory 吗？目前只讲了推断成 semantic | **能**：Shoelaces（5 条 trace → SKILL.md）、SOAR chunking（p.43）、Voyager 的 skill 库；讲义：「a skill is consolidated procedure: episodes in, a rule out」 |
| 0 | Raphaël | Hermes 推荐哪些 memory 插件？ | 待讲师答；讲义只提 Hermes 的做法：memory 文件 session 开始读一次并冻结、辅助压缩模型、固定模板摘要；kit 里的 🪶 Hermes 房间会读本机 `~/.hermes` |
| 0 | Raphaël | DeepSeek harness 概览 | 有官方开源项目：[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)（`dsh`，MIT，developer preview）。要点见下方「DeepSeek Harness 速读」 |
| 0 | Manisha | Flood 里「recency halving about every 5.8 days」是什么意思？讲义又说「half-life of six days」 | **同一件事**：论文 γ = 0.995 / 小时，半衰期 = ln 0.5 / ln 0.995 ≈ 138 小时 ≈ **5.76 天**；kit 写 5.8，讲义取整为 6；意思是「每过约 6 天，recency 分数减半」 |

### DeepSeek Harness 速读（读 README + docs/architecture.md，2026-11-15）

- **是什么**：DeepSeek 官方开源的 agent harness，命令 `dsh`，口号 *Everything is a Plugin*；MIT；developer preview（会有不兼容改动）；`npx @deepseek-ai/dsh web` 起本地 Web UI
- **底座 Cordis**：插件框架；模型适配器、工具注册表、session log、**连 agent loop 本身都是插件**，都能通过配置替换；没有「特权内核」
- **Profile / bundle**：`web` / `headless` / `sdk` / `acp` 等 profile 由多层 bundle 叠出来；`dsh-base` 提供模型适配、工具、持久化、沙箱与审批、凭据、遥测
- **核心包**：`core/session`（**append-only SessionEvent log**）· `core/system-prompt`（prompt 分段 + 工具 schema 拼装）· `core/tools` · `core/agent` · `core/agent-loop` · `llm/llm`
- **turn / step**：step = 一次模型请求 + 它调用的工具；turn = 零到多个 step；拼 prompt → 调模型 → 工具执行 → 下一步
- ⭐ **「Model-visible means logged」**：模型看到的每一次请求都必须能从 log 重建；`deriveMessages()` 从 log 投影出模型历史；fork、恢复、记录、遥测、持久化全部从 log 派生
- **存储**：JSONL 文件（可 zstd 压缩），按版本号分代（`session.vN.jsonl`），**已提交的文件永不改名、替换或删除**，格式升级时写新一代文件
- **扩展点**：加模型 = 在 `ctx.llm` 注册；加工具 = 在 `ctx.tools` 注册（schema 自动进 prompt）；加上下文 = `agent.inject()`；加持久状态 = 扩展 `SessionEventMap`；换存储后端 = 实现 `SessionPersistence`；还有 subagent、Agent Teams、沙箱、审批
- 🧭 和今天的课对上：
  - append-only log 是 ground truth，其他都从它派生 = 讲义 Practice I + 我刚问的「log 怎么用在 harness」
  - 「model-visible means logged」= 能回放「当时模型看到了什么」（两个时钟、审计）
  - system-prompt 包负责拼窗口 = 白板上的摆渡人 / Memory Palace 的 Glass Harness
  - 一切皆插件、可替换 = harness 就是策略，模型不变（「Change a policy, never the Genie」）
- ⚠️ 架构文档里没看到专门讲 memory / compaction 的章节（可能在 subsystems 文档里），没有核实前不下结论；repo 首页显示 27 万 star，日期是 2026 年，在我的训练资料之后

### ❓ 课间问：append-log 怎么用在 RAG / recall / harness 里？LLM 为什么需要 log？

- 模型本身不需要 log（它不记事）；**是 harness 需要**。log 是所有其他记忆的源头：

| 用途 | 怎么用 | 课上对应 |
| --- | --- | --- |
| ground truth / 重建 | 事实库、向量索引、图都是从 log **派生**的；换抽取逻辑或 embedding 模型时从 log 重建 | Practice I：log 永远保留 |
| 写入 / 合并的原料 | 后台任务读新增 log → 抽事实进 semantic、归纳规则进 procedural | Shoelaces：5 条 trace → skill |
| episodic recall | log 本身被检索：「上次怎么处理的」；窗口里的 recent turns = log 的尾巴 | Smallville 的 memory stream 就是 append-only log |
| 压缩后的「原件」 | 摘要进窗口，原文留在 log；需要细节时按指针调回 | p.48「leaf kept on disk」；回收三难的 externalize |
| 出处 / 审计 / 删除 | 每条事实的 `source` 指向 log 某一行；能回放「当时相信什么」；删除时顺着找到所有衍生物 | 两个时钟、governor、被遗忘权 |
| 召回统计 | 记录「召回了哪条、答对没有」→ 算 $\hat g_m$、$n_m$ | p.49 UCB |
| 评测语料 | 从真实 log 里做 plant–distract–probe 测试 | Practice II |
| 缓存 | 窗口按 append-only 增长 → 前缀不变 → 命中缓存 | Foyer G3、Manus |

- RAG 里的对应：文档和权限的**变更日志**（事件驱动同步）、**查询日志**（做评测）；但日志本身也是泄漏面，要做权限控制和脱敏（权限检索笔记的第 6 个泄漏面）

（原 p.43 的补充）ACT-R 的三项 ≈ Smallville 的 recency / importance / relevance（「within the hour」= 马上要讲 Smallville 打分）；区别：ACT-R 用 **frequency**，Smallville 用 importance，但 Smallville 的 recency 从**上次访问**算起，等于偷偷包含了 frequency（讲义：soft LFU）：Foyer = 左框；Flood = episodic；Shoelaces = procedural（episodic → procedural 的 consolidation）

### Deck p.33 · Three acts（目录展开版）

### Deck p.33 · Three acts（目录展开版）

| 部分 | 内容 | 时间 |
| --- | --- | --- |
| **Act I — What memory is** | 边界、harness、四层分类、四个操作、Smallville 打分规则 | W9（今天） |
| **Act II — The context lifecycle** | managed heap、compaction 和它的失忆、GC done properly、回收三难 — **the anchor act（重心）** | W10 |
| **Act III — Building and governing** | 谱系、两个时钟、分区抽屉、写策略、memory 评测、governor | W10 |
| **Postscript — the organs in the wild** | Claude Code、OpenClaw、Hermes 拆开看 | W10 Speakeasy |
| **Postscript II — the workspace in the weights** | 2026 年 7 月 Anthropic 论文（J-space） | W10 Speakeasy |

- 🧭 已在精读笔记里全部预读：Act I = §2，Act II = §3，Act III = §4，Postscripts = §7
- 🧭 曲线形状：Act I 在高处（概念清晰），Act II 掉到谷底（最难、每门课都跳过的回收），Act III 往上爬到 governor，Postscript 插旗收尾

- （以下为原 p.10 的补充）「the past becomes manageable」：这两周讲的不是「存起来」，而是**怎么管**：写什么、读什么、合并什么、忘什么

### 板书 ①

### 板书 ②

## 下午 · Memory Palace 一楼

## Owl of Minerva / 收尾

## 待核实

- [ ] Palace 一楼 / 二楼 / 大厅各包含哪些房间
- [ ] 今天有没有客座讲座


---

# 课外问答：权限感知检索与 MemGPT / System 5

> 课间在另一个会话里的问答和产出（原 `notes.zh 2.md`，已合并到这里）。文件列表见 [index.md](index.md)「课外」一节。

## 幻灯片

**Orientation deck p.6 · Milestone · Orientation · 11:15**（截图未存）

> MILESTONE · ORIENTATION · 11:15
> **Orientation**
> last week's owl, one story, six headlines — no mechanism before 15:00
>
> 里程碑 · 定向 · 11:15
> **定向**
> 上周的猫头鹰、一个故事、六个标题——15:00 之前不讲机制。

- 这是今天的路线图页。左侧表盘显示 11:00，右上的指针暗示"现在在哪、往哪走"。11:15 是开场定向。
- **"last week's owl"**：= 上周 **Owl of Minerva** 收尾环节的五行总结 → 新 deck p.7「Week 8, in five lines」（已核实）。
- **"one story, six headlines"**：Story of the Day（p.9–11）+ Headline 1–6（p.12 边界 → p.19 Memory is not storage; it is policy）。
- **"no mechanism before 15:00"**：下午 3 点前只讲现象和问题，机制留到下午。和 RAG Bootcamp Week 09 Module 5"先定义问题 → 数学 → 动手 → 证明"的结构是同一种讲法。

## 问答记录

### Q1 · "ACL boundary search" 从哪来，paper 是什么？

- 这不是标准术语，也没有专门的 paper。正式说法是 **permission-aware retrieval / secure retrieval**，搜索引擎领域叫 **security trimming**。
- 出处是 RAG Bootcamp 讲义：[Week 09 Module 5](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_09/week-09.zh.md)（主讲：`D_u` 公式、Prevention vs Suppression、六个泄漏面、ACL/RBAC/ABAC/ReBAC、归一化描述符、两条流水线），[Week 06](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_06/week-06.zh.md) 第 ⑧ 条护栏"ACL at retrieval, not after"，[Week 10](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_10/week-10.zh.md)"pre-filter, never post-filter"。
- 相关文献：Zanzibar（ReBAC）、Sandhu 1996（RBAC）、NIST SP 800-162（ABAC）、Filtered-DiskANN、ACORN（带过滤的向量检索）。

### Q2 · "有个 Microsoft 的文件是做这个的"

- 是 **Azure AI Search** 的两篇文档：
  - [Document-level access control](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview)（preview）：索引时带入 ADLS Gen2 / Blob / SharePoint 的 ACL，查询时在 `x-ms-query-source-authorization` 头里传 Entra token，服务端自动裁剪。
  - [Security filters for trimming results](https://docs.azure.cn/en-us/search/search-security-trimming-for-azure-search)：手动方案，自己写 `group_ids` 字段 + OData filter。
- 同样有同步滞后问题（[ISE 博客](https://devblogs.microsoft.com/ise/?p=16628)）：SharePoint 撤权后，下次 ingestion 前仍可能检索到。

### Q3 · `vdb.query(..., filter=f)` 底下怎么实现？记录怎么存？

- 每个 chunk 存三处：向量（进 HNSW/IVF）、payload、每个字段的**倒排索引 → Roaring bitmap**。数组字段逐元素建倒排。
- filter 编译成 bitmap 的交、并、差，结果就是 `D_u`；没有 `classification` 字段的 chunk 自动被排除，天然 fail-closed。
- 规划器按选择率选策略：小集合暴力扫描；大集合在 HNSW 遍历时带 bitmap；1–10% 是难点区（图断开，用分区或 ACORN）。pgvector 本质是后置过滤。
- 完整代码（`secure_search` + `TinyVDB`）见 [`permission-aware-retrieval.md`](permission-aware-retrieval.md)。

### Q4 · MemGPT 能不能做 System 5 的基础？

按 Stafford Beer 的可行系统模型（VSM）理解 System 5（身份与政策，裁决 S3 与 S4 的冲突）。

- **结论：** MemGPT 只能当 System 5 的**记忆底座**，不能当 System 5 本身。
- **能借用的：** core memory 的 persona 块常驻上下文、跨会话保留，适合放身份与原则；分层存储让完整政策放 archival，用时再取。
- **不能直接用的原因：**
  1. agent 能改写自己的 persona → 身份可被 prompt injection 或"自我优化"改掉。边界只是请求，不是控制。
  2. MemGPT 管的是"什么进上下文"，属于资源调度（接近 S2/S3），没有裁决角色。
  3. core memory 是可变当前状态，没有版本与审计。
- **建议架构：** S5 单独存放、对 agent 只读、带版本、改动需人工审批、确定性执行；MemGPT 把 S5 精简版注入为只读块；S3/S4 agent 自由管理工作记忆，冲突上交 S5。
- 待核对：Letta 是否支持只读 memory block；课程里的 "System 5" 是否就是 VSM 的定义。
- 提交稿（英文）：[`memgpt-as-system-5.md`](memgpt-as-system-5.md)

## 与已有笔记的联系

- "边界是请求，不是控制"同时出现在 Q1（权限检索）和 Q4（System 5 身份保护）：凡是必须无条件成立的约束，都要从 prompt 层挪到基础设施层。
- 两条流水线的时间戳缝隙（Q1）和 System 5 的版本化要求（Q4）是同一条原则：被治理的状态必须能回答"这是哪个时刻的快照"。
