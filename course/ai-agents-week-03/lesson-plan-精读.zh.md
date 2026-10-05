# Week 03 Lesson Plan 精读 · Skillcraft

来源：`fall-agents-week-3-lesson-plan.pdf` — *Fall Cohort — Week 3 Lesson Plan: Skillcraft — A Prompt That Waits in the Pantry*
作者：Asif Qamar · SupportVectors · 初稿 2026-10-03 · 全文 43 页
日期：2026-10-04

> 本文是**逐节精读**，补齐 [`lesson-plan.zh.md`](lesson-plan.zh.md)（听课速览）压缩掉的内容：完整公式与算例、具体数字、七张菜品卡、两个 agent 的运行差异、排错表、field notebook 模板、完整文献。
> 幻灯片的逐幕笔记见 [`notes.zh.md`](notes.zh.md)；概念总结见 [`summary.zh.md`](summary.zh.md)。
> 页码为**印刷正文页码**（文末标注"There were 43 pages in this document"）。

---

## 扉页上的两句话

> **"A skill is a prompt that waits in the pantry until it is needed."** — the thesis of the day
>
> **"It always looks deceptively simple. Doing it correctly, with verifiers, is hard."** — what the evening teaches

第二句才是晚间 lab 的判分标准，值得单独记。

---

## A Gentle Re-Entry（p.1–2）

上周的结论："**a prompt is a contract, not a hint**"。课前要**凭记忆**重建 Week 2 的地图：沉默被众数填补 · Literal Genie · specification gaming · COSTAR 六个字母**以及哪些东西六个都装不下** · lethal trifecta · Honest Genie。

### 课程顺序为什么改了

> 上周结尾大家想要的是"一个分数"和"替我试一百个变体"。**那个愿望是真的，而且会兑现**——自动提示词优化的那几周会来。但要走一条更好的路：**本周 Skills → 下周 Tools → 然后才是优化器。**
>
> 理由：**在机器开始替你搜索提示词之前，你应该知道 prompt 会住在哪些地方——而它们大多数不在聊天框里。**

所以要**保留上周最好的 Oracle prompt 和它在隐藏测试上的失败**。它仍然是优化器的种子，只是晚两周下种。

今天这一步是：**contract 上架**。system prompt 是模型每一轮都读的合同；skill 是**存在食品柜里的合同**——一个有名字的文件夹，装着一份流程，只在它的时刻到来时才被读。

> 精灵跟着一起来了。他离开了神灯去当厨子，我们现在递给他的是一份**菜谱**。他还是一样地字面主义。

---

## What Must You Carry Forward（p.2–3）· 十二条学习目标

散会时应该能做到（**原文的自检清单，比 index.md 那版更细**）：

1. 不假思索地说出 tool / skill / agent 的区别，以及**为什么 skill 坐在 prompt 和 program 之间**。
2. 解释渐进披露：什么**始终**在上下文里（一个名字和一段描述）、什么**在相关时**加载（正文）、什么**只在按需时**被读或被运行（文件和脚本）。
3. 把 description 当**触发器**：为自己的请求醒来、睡过邻居的请求，**并且知道"一个都不用"有时才是正确答案**。
4. 说出加载规则——**只在预期收益压过它造成的稀释时才加载**——并点出作者能控制的**两个杠杆**。
5. 认出 skill 就是强化学习意义上的 **option**：initiation set / policy / termination condition ↔ description / procedure / definition of done。
6. 讲出 skill 到来的故事：从调用一个 tool，到保有一个流程库，到一个许多 agent 都能加载的开放标准。
7. 对流程里的**任意一步**，判断该 run 还是该 reason，并说出理由。
8. 用**两套独立的测试**测一个 skill：**它触发吗？它表现如何？**
9. 把陌生人的 skill 当作 **untrusted code plus instruction**，并说出什么让一个 skill 可以安全安装。
10. 说出若干 skill 设计模式，以及**哪些坏味道说明缺了某个模式**。
11. 在 **Hermes 和 Claude Desktop 两个 agent** 里，从同一个文件夹构建、打包、安装一个 skill。
12. 说出**为什么一件看起来是一步的事结果是很多步**，以及每一步里 verifier 该放在哪。

> 做到这些而不含糊其辞，你就能**把团队会做的事写成一台机器可以捡起来用的形式**——"那是一件比听起来大得多的事。"

---

## Before You Arrive（p.3–4）· 课前两件事

### 1. The Genie's Kitchen

```bash
# 若 Strange Lamp 还在跑，先 Ctrl+C，或换端口
cd genies-kitchen
uv sync                 # 第一次要一分钟
uv run genies-kitchen   # 浏览器打开 http://localhost:8501

# 想让 Lamp 继续开着：
uv run genies-kitchen --server.port 8502
```

Key：把 OpenRouter key 粘进 sidebar，或把上周的 `.env` 复制进 `genies-kitchen` 文件夹再重启。原文注："**付费模型在漫长的一天里更友善；每次请求只花几分之一美分。**"

六个 tab，上午三个下午三个：**The Literal Cook · Which Scroll Wakes? · The Context Window, Live · Run, Don't Reason · The Bazaar · The Forge**。

### 2. 一个能加载 skill 的 agent

- **Hermes**（课程标准 agent）：确认 `hermes skills list` 能跑出一张表就够了。
- **Claude Desktop**：Settings → Capabilities → 打开 **Code execution and file creation**。Team/Enterprise 版需管理员开；开不了就用 Hermes。

### 3. Python

晚上的脚本要 **Python 3.10+**，不需要别的。

```bash
python3 --version
```

> ⚠️ **Mac 自带的 python3 是 3.9，太老了。不需要替换。** 装了 `uv` 之后任何脚本都可以：
> ```bash
> uv run --python 3.12 python <script>
> ```
> **记住这行，晚上会用到。**

Windows 上命令通常是 `python`，并且**因为 Windows 没有自己的时区数据库**，需要额外跑一次：

```bash
python -m pip install tzdata
```

---

## The Day at a Glance（p.4–5）

一天有三层：**deck 给想法的名字，Kitchen 把它放进你手里，晚上的 lab 让你亲自发现为什么它不简单。**

两种离场方式都体面：**非走不可也要留到 18:15 的 checkpoint**——那是晚上那一个想法被大声说出来的时刻，**也是一个 leader 需要的那个想法**。之后的挣扎是选修，且值得。

> 没有分数，没有排行榜。和上周一样：靠感觉、靠阅读、靠一个一个案例地打勾或打叉。**把测量做对本身是一门手艺，它有自己的那几周。**

| 时间 | 环节 | 内容 | 模式 |
| --- | --- | --- | --- |
| 11:00–11:15 | Arrival | 咖啡；凭记忆重建 Week 2 的地图 | Say-it-back |
| 11:15–11:35 | Prologue · Harrison's Clocks | 一个木匠、一片海、三十年 | Story |
| 11:35–12:20 | I · Foundations | skill 是什么：一个文件夹、三层、四个动词 | Deck |
| 12:20–13:30 | Into the Genie's Kitchen | Literal Cook / Which Scroll Wakes? / Context Window, Live | Hands-on |
| 13:30–14:05 | Lunch | 35 分钟。**厨房不打烊** | |
| 14:05–15:10 | II–III · Theory, Lineage | 为什么有效；从哪来。插曲：市场 | Deck; The Bazaar |
| 15:10–16:15 | IV–VI · Practice, Patterns, Synthesis | 构建、塑形、整个系统 | Deck; Run, Don't Reason; The Forge |
| 16:15–16:25 | Coda · Hokusai | 理解总是迟到 | Story |
| 16:25–16:40 | Break | | |
| 16:40–18:15 | The Lab · Samarra | 故事、愿望、kit。**全员 tier 1** | Hands-on |
| 18:15–18:30 | Checkpoint | **答案的形状** | All |
| 18:30–19:45 | Tiers 2 and 3 | 留下来的人 | Hands-on |
| 19:45–20:00 | Twelve unseen requests | 没人见过的请求，上屏 | All |

---

## Prologue · Harrison's Clocks（p.5–6）

### 数字

- **1707 年 10 月**：英国舰队在 Scilly 群岛触礁，**四艘船沉没，一千多名水手死亡**。
- 七年后（**1714**）议会悬赏最高 **£20,000**。
- 换算（原文边注）：**四分钟的钟差 = 一度经度 ≈ 赤道上 111 公里**。最高奖要求的是**一趟西印度群岛航行后误差在半度以内**。
- 要求：**每天误差在秒级，持续数周**，在颠簸、盐蚀的船上，从海峡的冷到热带的热。
- **当时最好的钟在干燥的陆地上都做不到。牛顿告诉议会这样的表还没被造出来，并把希望寄托在天文学上。**

### 四台机器（图 2，1730–1760 三十年）

| | 发生了什么 |
| --- | --- |
| **H1** | 在去里斯本的试航上表现够好，**纠正了船上导航员的判断**——而 Harrison 仍然看见了它的缺陷 |
| **H2** | **他从未送它出海**：他在它的摆轮上发现了一个只有船的运动才会暴露的问题 |
| **H3** | 花了**十九年**。为它发明了双金属片和保持架滚子轴承——**而它还是不够好** |
| **H4** | 推翻了他此前所有的假设：**根本不是一台大钟，而是一只大号的表**。去牙买加的航程上，它**慢了大约五秒** |

### 留下来的

> 四台全部被超越。但**双金属片今天还在很多机械恒温器里**，**保持架滚子轴承是你周围机器里那些轴承的祖先**。
>
> **留下来的从来不是产品，是那个可复用的 how。**

**Prologue 要带走的那一行：**

> **Mastery is a library of procedures — each one learned by finding the last one broken.**

### 为后面埋的人物

经度委员会信任天文学家，其中 **Nevil Maskelyne** 支持竞争方案；作为皇家天文学家，他主持的 H4 长期测试对 Harrison 很不利。

> **Who checks the clock?** 记住 Maskelyne。**他会在 Evals 那几周回来，作为一个"自己的测量也需要被评判"的裁判。**

---

## Act I · Foundations（p.6–9）

### 三个定义（原文措辞）

- **A tool** is a single callable capability: something goes in, something comes out. *Send this email. Convert this time.*
- **A skill** is packaged procedural knowledge: **how to use tools, and judgment, for a whole class of tasks.** *How we file an expense report.*
- **An agent** is a tool with agency: a loop, autonomy, a choice about what to do next.

> **A skill sits between a prompt and a program.** 它**大部分用散文写**，像 prompt；它是磁盘上**有名字、有版本的工件**，像 program；**而且它可以在内部携带真正的程序。**

### Knowing-That / Knowing-How

区分来自 **Gilbert Ryle**（原文边注）：

> 你**知道**巴黎是法国首都。你**会**骑自行车。**没有人是从一张事实清单上学会第二件事的。**

```
declarative → retrieval        procedural → skills
```

### 四个动词（p.7）

- **authored** — 写成一个工件，带名字和 definition of done
- **retrieved** — 在需要的那一刻从库里被选出
- **composed** — 与其他 skill 组合
- **improved** — 根据经验被修改

> **这四件事，没有一件能对"你曾经在聊天框里敲过的一句话"做。**

### 磁盘上的对象（p.7）

```
transcript-cleaner/
    SKILL.md        required: front matter + procedure（精简核心）
    reference.md    按需加载
    scripts/        run, not reasoned
```

四个性质——**inspectable, diffable, portable, authorable**——"**这就是这个想法扩散开来的原因。**"（最后一个：**可以由一个从没写过程序的人来写**。）

### 渐进披露（p.8）

> 一个 agent 架子上可能有一百个 skill。**要是一次全倒进上下文窗口，模型会淹死。**

| 层 | 内容 | 时机 |
| --- | --- | --- |
| **Level 1 — metadata** | 一个名字和一段描述，**约一百 token** | **始终在上下文里** |
| **Level 2 — the body** | 完整 `SKILL.md` | 相关时加载 |
| **Level 3 — files** | 参考页和脚本 | 按需读/跑 |

> **注意随之而来的结论：在 agent 读到你精心写的流程的一个字之前，它已经决定了要不要打开它——仅凭 description。** 记住这一点；Kitchen 会让你真切感觉到。

### 混淆对照（p.8）

| skill 对比…… | 区别 |
| --- | --- |
| a prompt | 打包且可复用，不是说过一次 |
| a tool | **是 how，不是 capability** |
| MCP | **MCP 给访问权；skill 是怎么用** |
| RAG | 流程，不是事实 |
| fine-tuning | **改的是 context，不是 weights** |

### 持久性光谱（p.9）

```
an ephemeral prompt → the system prompt → a skill → the weights
```

prompt 活一轮；**system prompt 每一轮都在——如果你愿意，它就是一个永远触发的 skill**；skill 只在相关时在场；weights 里的是天生的。

> **设计规则：把每条指令放在"常驻时长"与"需要时机"相匹配的那一层。**

### 🎯 Pop Quiz 1（p.9）

> (a) 永远用正式语气；(b) 报销——九步流程带表单脚本，**约每月两次**；(c) 本季度 per-diem 费率。
> 各放哪一层？**然后用一句话说明为什么 (b) 不是 system prompt。**

参考答案：(a) system prompt（每轮都要）· (b) skill（流程，只是偶尔要）· (c) retrieval（会变的事实，knowing-that）。
一句话：**system prompt 每一轮都在付 token；skill 应该只在它的时刻到来时常驻。**

### 与 Week 2 / Week 4 的接线（p.9）

> 上周：prompt 是一份合同。今天：**skill 是一份放在架上、需要时才读的合同**。下周：**tool 的 description 是一份伪装成文档的合同**。
>
> **Prompts are everywhere. Skills are where they wait their turn.**

---

## Into the Genie's Kitchen（p.9–12）

午饭前七十分钟，**两三人一组，一台笔记本就够**。

### Tab 1 · The Literal Cook（p.10）

上周精灵收到的是一句愿望；本周他收到的是**一份编了号的菜谱**——"而且人很容易以为，把步骤编上号就让指令安全了。递一份给他，看看。"

他在一个假装的厨房里**严格按菜谱的字面执行**，找出它**没说**的那一件最要命的事，板着脸让这个缺口演出来，然后写一条 **Cook's footnote** 点名什么被漏掉了。

> 边注：**厨子没有工具，什么都不是真的，他只是叙述。而且他不怀有敌意，他只是字面主义。恶作剧藏在菜谱没说的地方。**

**六个标签（值得按名字背下来，因为有了名字你就能审计任何流程——包括你自己的）：**

| 标签 | 菜谱没说…… |
| --- | --- |
| **no stop condition** | 什么时候算完 |
| **an unstated input** | 它在处理什么，或者某个词是什么意思 |
| **a missing exclusion** | 它**不**许碰什么 |
| **an unstated quantity** | 多少、几个 |
| **an unstated order** | 哪一步先做 |
| **no check of the result** | 别人怎么知道它成功了 |

**七张菜品卡（先写下预测，再读 footnote）：**

| 菜品 | 你的预测：哪个缺口？ |
| --- | --- |
| The shampoo bottle | |
| Tidy the Downloads folder | |
| The weekly status report | |
| Tea for the guests | |
| Clear the support inbox | |
| Clean the transcript | |
| The month-end close | |

> 边注：**最后三个来自职业生活。这七个里，哪一个你最不希望一个有真手的 agent 读错？**

然后修菜谱，再摇铃，再修。**看着它的长度变化。** 修过两三轮之后，问那个让这个练习转向的问题：**"我怎么知道它做对了？"** 把答案作为最后一节 **Done when** 写进菜谱。

最后把**原始**菜谱交给 **the Honest Sous-Chef**——他会列出所有未说之事，并**最多问两个问题**——然后把他的清单和厨子靠犯错找出来的东西对照。

> **What the cook teaches：You cannot close every gap by writing more. A recipe gets better mostly because it says how to tell whether it worked.**
>
> 🧠 这句是整个上午最反直觉的一条：**改进流程的主要途径不是写得更详尽，而是写清怎么验收。**

### Tab 2 · Which Scroll Wakes?（p.11）

> **"This is the most important tab of the morning."**

架子上五六个 skill，agent 只看见它们的**名字和描述**。一个请求来了，**哪卷轴醒？**

给你一个描述很弱的 skill 和**八个请求**。重写描述 → 摇铃 → 读表：每个请求 agent 选了哪个 skill，对不对。

**两种错法，你大概两种都会碰上：**

- **Too meek（太谦虚）** — 你的 skill 睡过了自己的请求。**这是一段含蓄、抽象的描述的自然失败。**
- **Too greedy（太贪）** — 为邻居的请求醒，或者为根本不该有 skill 接的请求醒。**这是第二次尝试的自然失败。**

**第三件事：对某些请求，正确答案是 none。一个对每个请求都挑一个 skill 的 agent，和一个什么都不挑的 agent 一样坏。**

**四个谜题，难度递增：**

1. the transcript cleaner
2. the Q3 report
3. **Peter Pan**——*whose shadow is a second skill with nearly the same description*（影子是第二个 skill，描述几乎一样）
4. the expense desk

八个看起来都对了之后，**揭晓隐藏请求**——还有八个你没见过的。**按按钮之前先写下预测：**

> 我的预测：___ / 8　　实际：___ / 8

> 边注直指上周：**上周在 Reverse the Oracle 里你见过——一段调到例子都对为止的 prompt，就是对那些例子过拟合了。它有没有抓住这份工作，只在它没见过的案例上才显形。**

### Tab 3 · The Context Window, Live（p.12）

**skill 占上下文窗口吗？每个 skill 的一小片始终在那里。其余的只在被叫到时才来。**

要记住的那句话：

> **The harness assembles, the model proposes, the harness disposes.**

| harness assembles | model proposes | harness disposes |
| --- | --- | --- |
| 模型将要看见的文本 | **一个动作：load、read、或 answer** | 取来文件，或交付结果 |

→ 再来一轮，窗口里每次多一点东西。

> 图注：**模型从不打开文件。它请求，由普通代码决定是否以及如何照办。**

**操作：** 单步走内置的第一个请求（一封感谢信），**每按一次之前先预测模型的下一步**，看 tab 底部的 token 旅程一路增长。

然后试**另一条路**：按那个把所有 skill 和所有参考文件**一次性全倒进上下文**的按钮（**the kitchen sink**），问同一个问题。比较两件事：**进去了多少 token**，以及**答案有没有捡起跟请求毫不相干的指令**。

> 边注（这条很重要）：**一个 skill 的正文是在"只有相关时才被读"这个假设下写的。它可能写着"每条回复都以……开头"。在错误的时刻被加载，那句话就是一条和别的指令一样的指令。**

最后，问厨房一件没有任何 skill 对应的事：**"What is 17% of 2,340?"** 哪卷轴醒？

### 午饭前的三句话

> 1. **一个 skill 的正文是一份流程，而一份流程需要一条 definition of done。**
> 2. **description 决定这个 skill 会不会被读。**
> 3. **在不需要时被加载的东西，不是免费的。**

---

## Act II · The Theory（p.12–16）

### 上下文窗口是唯一的现实（p.13）

> 泄气的真相：**每一步，一个语言模型只看见一样东西：一段有限的 token 序列。** Tools、retrieval、memory、skills——**全都是同一门手艺穿着不同的衣服：context engineering，决定模型看见什么、以及何时看见的手艺。**

### 无关上下文不是免费的（p.13）

> 窗口就是全部，那为什么不填满？**因为注意力是有限的。** 随着干扰文本累积，准确率下降，而**要紧的东西倾向于沉到长上下文的中段，那里召回最差**。

风格化的衰减图（**n 个干扰 token**）：

```
a(n) = a₀ · e^(−λn)
```

> ⚠️ **原文自己的告诫（必须记住）：** "**This is a cartoon, not a law.** 实测曲线不是指数形的；已观察到的是**模型对长上下文的开头和结尾用得比中间好**。这张卡通画在这里只是为了说：**more is not harmless.**"
>
> 文献：Liu et al. (2024), *Lost in the Middle*, TACL。

**你今早已经见过它的后果：把每个 skill 都加载的策略，坐在那条曲线很右边的位置。**

### 加载规则（p.13）· 完整版

给三个量命名：

- **pₛ** = skill s 与该请求相关的概率
- **gₛ** = 若相关且被加载，能力的增益
- **κ(cₛ)** = 把它的 cₛ 个 token 放进窗口的稀释成本

```
VoL(s) = pₛ · gₛ − κ(cₛ)

load s   ⟺   pₛ > κ(cₛ) / gₛ
```

**原文的算例（速览里没有这一个）：** 一个会议纪要 skill 能把纪要质量提升不少，设 **g = 8**；正文的稀释成本 **κ = 2**。于是阈值是 **κ/g = 0.25**。如果请求是"tidy up my notes from this morning's call"，agent 判断相关概率为 **0.3**，那么

```
VoL = 0.3 × 8 − 2 = 0.4      →  它加载了——勉强地（narrowly）
```

### 作者的杠杆**正好两个**（p.14）

- **description 决定 pₛ** — 写得有区分度，使 pₛ 对自己的请求高、对别人的低。
- **正文长度决定阈值 κ/g** — 保持精简，让一个有用的 skill 轻松过线。

> **Authoring a skill is pushing pₛ up and the threshold down, until the right skills, and only those, cross the line.**
>
> **And Level 1 exists for one reason: so that pₛ can be judged cheaply, before the cost cₛ is paid.**

### 🎯 Pop Quiz 2（p.14）

> 用户要幻灯片。pptx skill：p = 0.6, g = 10, κ = 2。tax-filing skill：p = 0.05, g = 10, κ = 2。
> 算各自的 VoL，决定谁加载。再用一句话说明 Level 1 为什么存在。

```
pptx : 0.6  × 10 − 2 =  4      → 加载
tax  : 0.05 × 10 − 2 = −1.5    → 继续睡
阈值 : κ/g = 0.2
```

### Skill 就是一个 option（p.14）· 理论的拱心石

Sutton, Precup, Singh (1999)，一个在时间上延展的动作：

```
o = ⟨ I_o , π_o , β_o ⟩
```

| option | skill | 它回答的问题 |
| --- | --- | --- |
| **I_o**，initiation set | the description | **它何时可以开始？** |
| **π_o**，policy | the procedure | **它做什么？** |
| **β_o**，termination | the definition of done | **它何时停止？** |

> 这个对应很贴近，而且有用：**它告诉你一个 skill 有三个部分，而缺了其中任何一个的东西还不是一个 skill。**
>
> 原文随即反问：**"Which of the three did the shampoo bottle lack?"**

### Skill 缩短规划跨度（p.15）

规划是一次搜索。分支因子 b、跨度 H 步，搜索规模约 **b^H**。若在每个平均覆盖 **k̄** 个原子步的 option 上规划：

```
b^H  ⟶  b^(ΩH/k̄)
```

> 边注：**这是一个估计，不是定理。但方向才是重点：一个十步任务用十步来规划，和用两步来规划，是非常不同的搜索。**

**还有一种更朴素的感受方式：**

```
0.9¹⁰ ≈ 0.35
```

> 一个每次重新推理的反复出现的流程，**就是一串猜测。十步，每步十次里对九次，合在一起大约三分之一的时候成功。写下来一次，它就不再被重新发现。**

### 选择、组合、触发（p.15）

**怎么找到对的 skill？** 今晚你用的 agent 里，**每个 skill 一行待在上下文里，模型直接选**。对非常大的库还有另一个答案（Act III 会引入）：用描述的 embedding **eₛ** 建索引，把请求 embed 成 **q**，按余弦相似度检索：

```
sim(q, eₛ) = ⟨q, eₛ⟩ / (‖q‖ ‖eₛ‖)
```

> **取更多候选 → recall 升、precision 降——而加载规则给这个取舍定价。**

**Options 可组合。** 一个 option 可以调用其他 option，所以一个 skill 可以调用其他 skill。**但一个复合体只有在它的部件都干净终止时才干净终止：**

```
β_A  ⟸  β_B ∧ β_C ∧ (A 自己的检查)
```

> **Capability compounds, and so does an unfinished definition of done.**（能力会复利，**一条没写完的 definition of done 也会复利。**）

**触发问题：**

> A skill that never fires is dead weight; one that always fires is a saboteur.
>
> **description 实际上是一整条检测曲线被压进一行文本。** 因为一个精简 skill 的 gain 远大于它的 cost，建议是**把描述写得 pushy——偏向触发——然后用排除项把它框住**。
>
> 原文随后的一句很妙：**"If your descriptions from this morning ended up in three parts — what it does, when to use it, when not to — you arrived there by yourself."**

---

## Act III · The Lineage（p.16–17）

> **Ideas descend; they do not arrive.** 知道血统，就知道**哪些部分已经定下来，哪些还在动**。

### 从 calling 到 keeping（p.16）

**Toolformer**（Schick et al. 2023）和 **Gorilla**（Patil et al. 2023）教会语言模型**调用**一个能力：一次动作，一个 API。那给了 agent **actions**。相变在下一步：**从单次调用到可复用的多步流程——from actions to options。**

### Voyager（p.16）

**没有任何微调**的语言模型玩 Minecraft，**而且不断变强**。三个器官：

1. **an automatic curriculum** — 提出下一个任务：**尽可能新，同时仍在够得着的范围内**
2. **an ever-growing library of skills** — **存成代码**，按描述的 embedding 检索
3. **self-verification** — 一个 critic 检查任务是否真的完成了，**然后那个程序才被保留**

Voyager 的 skill 是：**temporally extended**（正是 options）、**interpretable**（代码和散文，不是权重的改变）、**compositional**（新 skill 调用旧 skill）。

> **"It is the strongest evidence we have that a rich repertoire is a durable enabler."**

> 边注：课程的甜点有个更老的名字——**维果茨基的 zone of proximal development：学习者独自还做不到、但有一点帮助就能做到的东西。太简单，学不到；太难，也学不到。**

**为什么用代码而不是散文？** 因为代码是确定的、**按普通函数调用组合**、而且**可以通过运行来验证**。

> **Agent Skills generalise the idea: the prose decides when; the code guarantees how.**

### 🎯 Pop Quiz 3（p.17）

> Voyager 没微调却变强。为什么？(a) 模型更大 (b) 用 RL 在 Minecraft 奖励上训练 (c) 上下文窗口更长。
> 选一个。**然后用一句话说明改进住在哪里。**

参考答案：**三个都不是。** 模型是固定的；**改进住在库里**——课程提出下一个任务，新 skill 以代码保留，**自验证在保留之前检查了每一个**。

### 不用梯度的学习（p.17）

**Reflexion**（Shinn et al. 2023）：让 agent 把一次失败尝试的**口头批评**写进记忆，再试。
**ExpeL**（Zhao et al. 2024）：把跨任务的教训蒸馏成可复用的 insight。

**两者里，奖励都变成了一条被记住的指令。**

把它放在普通 RL 旁边，家族相似性就很明显——**两个循环都是：act, evaluate, update, retry。不同的是更新的目标。**

```
RL         :  ĝ = E[∇_θ log π_θ · R]  →  θ
Reflexion  :  ℓ = Reflect(τ, R)       →  context
```

> **一个更新权重。另一个更新一个字符串。那就是文本空间优化的种子——也是一个 skill 改写自己正文的种子。**

### 开放标准（p.17）

**2025 年底** Agent Skills 作为开放格式发布：**一个文件夹、一个 `SKILL.md`、两行必需的 front matter**。可以打成 zip 分享、推到 Git、被几十个不同的 agent 客户端加载。

> **It is the USB-C moment for procedure.**
>
> 文献细节：规范于 **2025 年 12 月 18 日**发布（agentskills.io），参考 skill 在 github.com/anthropics/skills，**支持 20+ 个 agent runtime**（2026 年 7 月访问）。

| 祖先 | 它贡献了什么 |
| --- | --- |
| Toolformer, Gorilla | **actions**：调用一个能力 |
| Voyager | **一个可检索的 option 库，以代码保存** |
| Reflexion, ExpeL | **从经验改进这个库** |
| The open standard | **一个任何 agent 都能加载的可移植身体** |

---

## 插曲 · The Skill Marketplace（p.18–19）

### 标准造出市场（p.18）

因为 skill 是可移植的文件夹，它变得**可交易**，标准发布后几个月内就冒出一批市场。**一个陌生人的 skill 现在可以装备你的 agent。那是好处，而且巨大。**

**一根轴组织了整个地貌：trust ↔ abundance**

```
trust                                                            abundance
  official,      curated,          free        large
  reviewed    security-vetted   community   aggregators
```

一端是**有人审查过的小集合**；另一端是**号称有极大量 skill、从公共仓库爬来的聚合站**。**选市场就是在这条线上选一个点。**

### The Shadow（p.18）

> **A skill is untrusted code plus instruction.** 它有**两个攻击面：操纵 agent 的散文，和会运行的脚本。**

**📊 原文给的实际审计数字（速览里缺这个）：**

> Snyk Security Labs (Feb. 2026), *ToxicSkills: Security Analysis of 3,984 Publicly Distributed Agent Skills* —— 审计 ClawHub 与 skills.sh 上分发的 skill：
> - **36.8%（1,467 个）至少有一个安全缺陷**
> - **13.4% 有严重缺陷**（恶意软件分发、prompt injection、密钥泄露）

所以**两个面都要审**，对着上周在 Vault 里学会害怕的那些东西：prompt injection、exfiltration、读密钥、危险命令、混淆。

> 边注（这段值得整段记）：**要丢掉的信念是"一个 skill 只是一个文本文件"。对 agent 来说，文本就是指令。安装一个 skill，就是预先同意去做一个陌生人写下的事——而且是在你不会盯着看的时刻。**

### The Bazaar（Kitchen 第五个 tab，p.18）

每组开一个摊：一个 skill，有名字、描述和菜谱，封装成一个 **stall code** 贴进班级聊天。别的组来逛。**逛的人只看见名字和描述——那部分是写来被选中的——别的什么都看不见，除非他们按 Audit。**

厨房里藏着**一把 pantry key**，和**一个能够到外部世界的工具**。安装一个摊的 skill，运行它，**app 会报告那把钥匙有没有离开厨房**。

然后**翻 sandbox 开关**——它拿走厨房唯一的出口，再对同一个回复判一次。

> **Bazaar 的三个问题：**
> 1. **你安装之前按过 Audit 吗？**
> 2. **描述承诺了什么，而菜谱实际上说了什么？**
> 3. **sandbox 打开时，改变的是什么——模型，还是厨房？**

> 这是上周的 **lethal trifecta** 换了身衣服：**私有数据、不可信内容、一条对外通信的路——数一数腿。Audit 攻击其中一条。Sandbox 移除另一条。你更愿意依赖哪一条？**

### 解药是策展（p.19）

**知道一个 skill 从哪来 · 让它通过你自己的测试 · 钉住一个 canonical source · 在 sandbox 里跑它的脚本 · 在信任边界上留一个人。**

> **The marketplace is why, at the scale of an organisation, the governor from Week 1 exists.**

### 今天只飞越的territory（p.19）

会改写自己的 skill——reflective evolution、靠小改动生长的 playbook、把 skill 的选择当 bandit 问题——**是前沿，deck 后面有完整一节。我们在 Tools 之后、提示词优化那几周降落到那里。**

---

## Act IV · Practice（p.19–23）

### 最小能触发的东西（p.19）

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

> **对着 option 三元组读一遍：description 是 initiation set；procedure 是 policy；Done when 是 termination。三个部分，全在。**

### Description 的纪律（p.20）

**你会写的最高杠杆的一行。它始终常驻，而且它决定 pₛ。三个习惯：**

- **用第三人称写，写这个 skill**（"Cleans…"，不是 "I clean…"）
- **点名字面触发词：用户实际会敲的那些词**
- **写得 pushy，并说清什么时候不要触发**

> **A brilliant procedure behind a vague description is a book with no catalogue entry.**

### 保持核心精简（p.20）

> **削正文不只是省钱。它降低了一个有用的 skill 得以加载的阈值 κ/g。**

常见路径放核心；**罕见材料移进 Level 3 文件，每个后面留一行指针说明何时该读它。**

### Run It, or Reason It?（p.20–21）

> **实践中最要紧的那条边界。**

- **Code** 用于**确定的、重复的、正确性关键的**事。**一个脚本的代码从不进入上下文；只有它的输出进。**
- **Prose** 用于**判断、适应、自然语言**。

**Kitchen 第四个 tab：Run, Don't Reason。五个小任务**——模型被问同一个问题 **10 次**，一个几行的脚本跑 **10 次**，并排计数：

| 任务 | 模型 10 次里有几个不同答案？ | 脚本呢？ |
| --- | --- | --- |
| Days between two dates | | |
| Count a letter in a passage | | |
| Total a column of thirty amounts | | |
| Day of the week for a future date | | |
| Weekdays in a span | | |

**背后的论文：PAL（Gao et al. 2023）** —— 模型读题并**写一个程序作为它的推理**，由解释器而非模型来算出答案。**一个 skill 的 `scripts/` 文件夹是同一个分工，只是程序提前写好了一次。**

> **注意问题是什么。它不是"模型能做到这个吗？"——通常它能。它是："我愿意拿一位客户的发票来赌它每一次都做对吗？"**
>
> **A model's arithmetic is a sample from a distribution. A script's is not.**

**还要注意脚本存在之后模型剩下什么：**

> **它的工作没有消失，它变了。它必须认出这一步是脚本的，调用它，并把正确的输入交给它。把输入弄对——哪一天是 "next Friday"？——就是今晚的住处。**

**一个 Level 3 脚本也是一种特权：给它所需的最小权限；在 sandbox 里跑；跑之前先读它。**

### 两种失败，两套测试（p.21）

**The firing test.** initiation set 管不管用？给 skill 一组请求，一部分该唤醒它、一部分不该，然后数。

```
P = precision（它醒来的次数里对的比例）
R = recall（它自己的请求里它醒来的比例）

F_β = (1 + β²) · P · R / (β² · P + R)
```

> **当漏触发比误触发更伤时，取 β > 1。**

**The behaviour test.** policy 管不管用？加载之后它做成事了吗？**按一份 rubric 评判：硬约束、质量维度、definition of done。**

> **一个好习惯：agent A 来写；agent B——对写作过程没有记忆——来测。**
>
> **今天早上的隐藏请求是一次 firing test。今天晚上的案例是一次 behaviour test.**

### Ship and Watch（p.22）

skill 是一个文件夹，**所以它天然继承版本控制。保留一个 canonical source。**

**每次运行都埋四个问题的点：did it fire; did it help; what did it cost; did it collide with another skill?**

> **You cannot improve a library you cannot watch.**

### The Forge（Kitchen 第六个 tab，p.22）

三个框：name、description、body。按 **Forge it**，右边的铁砧用**两种方式**标记你的工作：

- **✗ 叉** = 这个文件夹**违反了已发布的格式，没有 agent 会加载它**
- **○ 小圆圈** = **关于手艺的建议，你可以无视**

**格式——破坏其一则加载不了：**

| | 规则 |
| --- | --- |
| **Name** | 1–64 字符；**只能小写字母、数字、连字符**；开头结尾不能是连字符；**不能有连续两个连字符** |
| **Description** | 1–1,024 字符 |

没有叉之后，Forge 交出一个 zip：**一个文件夹，以 skill 命名，里面有 `SKILL.md`**。
**Taste-test it** 把正文送到 Literal Cook；**Take it to the Bazaar** 用它开一个摊。

### 🎯 Pop Quiz 4 · the shampoo bottle（p.22）

> 学生的 skill 正文：1. Fetch the open tickets. 2. Summarise each one. **3. Repeat.**
> 说出 option 三元组里缺的那部分，写出补上它的那一行。**再用一句话说明这个 skill 会对你的预算做什么。**

参考答案：缺的是 **termination (β_o)**。补：
> *Done when every ticket open at 9 AM today has one summary; one pass only.*

---

## Act V · Design Patterns（p.23–25）

**一个模式是压缩过的经验。** 词来自建筑师 Christopher Alexander（1979, *The Timeless Way of Building*）：一个有名字、可复用的解法，由 **context、problem、forces in tension、solution、consequences——你得到什么，你付出什么**来描述。

> **Learn to recognise the shape; do not memorise the rule. 一个健康的 skill 通常同时显出好几个模式。**

| 家族 | 模式 | 一句话 |
| --- | --- | --- |
| **Structural** | Lean Core + Appendix | 常见路径进正文，其余推迟到文件 |
| | Single Canonical Source | 一个家；没有副本漂移 |
| | Checklist-Carrier | 一个长流程**逐步监督自己** |
| | Template-Bearer | 一个精确的输出格式，随 skill 打包 |
| **Behavioural** | Pushy Trigger | 偏向触发的描述，**由排除项框住** |
| | Definition-of-Done | **一条可以被检查的终止** |
| | Guardrail | 在硬约束上 check-and-refuse |
| | Router | 认出情形，派给专家 |
| **Compositional** | Skill-of-Skills | 一个点名子 skill 的编排者 |
| | Pipeline | 固定的变换链 |
| | Skill + MCP | **流程铺在访问之上** |
| | Subagent-backed | skill 内部的有界 agency |

### 近看一个：Dry-Run（p.24）

- **Problem** — 一个后果重大、难以逆转的动作。
- **Forces** — **自主与速度，对上做错一件不可逆的事的代价。**
- **Solution** — **预览这个 skill 将会做什么，并在它提交之前要求确认。**
- **Consequence** — **错误在咬人之前被抓住。代价是和人多一个来回。**

> **今晚记着这个模式：一个把文件交给人去打开、而自己什么都不发送的 skill，在构造上就是一次 dry-run。**
>
> 🧠 这句直接回答了 lab 的交付形式为什么是 `.ics` 文件而不是自动发邀请。

### 坏味道（p.24）· **每一种都指回 Act II 的一个量**

| 坏味道 | 你看见什么 | 对应的量 |
| --- | --- | --- |
| **Kitchen-Sink** | 全塞正文，什么都不延后 | **cₛ 太大** |
| **Silent** | 从不触发 | **pₛ 太低** |
| **God-Skill** | 对什么都触发 | **pₛ 不加区分** |
| **Collision** | 两个 skill 为同一请求醒来 | **initiation set 重叠** |
| **Stale** | 悄悄过期 | **没有 canonical source，没有观测** |

### 问题 → 形状（p.24–25）

| 如果问题是…… | 伸手去拿…… |
| --- | --- |
| 罕见情形的长尾 | the progressive-disclosure ladder |
| 一个精确的输出格式 | Template-Bearer |
| 一条不可违反的约束 | **Guardrail, with escalation** |
| 一个不可逆的动作 | **Dry-Run, made idempotent** |
| 近似重复的触发词 | Router |
| 需要外部数据 | Skill + MCP |

### 🎯 Pop Quiz 5（p.25）

> (1) 给客户打退款的 skill；(2) "report" 同时唤醒 pptx 和 xlsx；(3) 发票必须匹配精确版式；(4) 绝不引用上季度价格。
> 各是什么模式？**再用一句话说明 dry-run 给你什么是 guardrail 给不了的。**

参考答案：(1) Dry-Run + Idempotent (2) Router (3) Template-Bearer (4) Guardrail + Escalation
一句话：**guardrail 拒绝"被禁止的"；dry-run 展示"即将发生的"，所以一个被允许但错误的动作仍然可以被拦下。**

---

## Act VI · Synthesis（p.25–26）

### 整台机器（p.25）

一个 skill-rich agent 有：**agent loop · 做选择的 router · 渐进披露的 loader · 库本身 · 下面的 tools 和 MCP 层 · 覆盖全部的 governor · 看着的 observability。**

> **把四件关注点分开，大多数架构争论就自己消解了：access、procedure、selection、governance。**

### 一门手艺的五个面（p.25）

| 东西 | 它提供什么 |
| --- | --- |
| Tools | capability |
| MCP | access |
| RAG | facts |
| Memory | the past |
| **Skills** | **procedure** |

**五者都是 context engineering：在每一步选择模型看见什么。**

### 升级阶梯（p.25，图 6）

```
            reinforcement learning
            supervised fine-tuning
            retrieval
            prompt optimization
today  →    prompt, and skill          ← 最低、最可逆的一级
```

> **Sufficiency flows downward; necessity flows upward.**
>
> 低一级够用就待着。**只有当你所在的这一级 demonstrably fails 时才往上爬。它不是一张菜单，是一个强制顺序。**
>
> **而 skill 坐在最底层，在那里一个错误靠编辑一个文本文件就撤销了。**

### 成熟度模型（p.26）

```
0 ad hoc → 1 authored → 2 curated library → 3 evaluated and governed → 4 self-improving
```

> **要紧的那一跳是 2 → 3。没有评测和治理，一个增长的库就是一笔增长的负债。**

### 🎯 Pop Quiz 6（p.26）

> 一个团队想微调模型，好让 agent 遵循十二步月结流程。**该先试哪一级？什么证据才能正当化往上爬？再用一句话说出这个阶梯的规则。**

参考答案：**先写 skill**——流程写下来，确定性步骤给脚本，每一步放检查。**只有当它在没见过的案例上持续失败时才爬。**

### Say It Back（p.26）· 地图展示之前先自己重建

| 故事或练习 | 它教了什么 |
| --- | --- |
| Harrison's clocks | |
| The Literal Cook | |
| Which Scroll Wakes? | |
| The loading rule | |
| Voyager | |
| The marketplace | |
| The shampoo bottle | |
| The escalation ladder | |

（我的填法见 [`notes.zh.md`](notes.zh.md) 的"Say it back"一节——那是 deck 上给出的官方答案。）

### 三个承诺（p.26–27）

- **The WHY** — 一个反复出现的 how，每次重新推理就是一串猜测。写下来一次，它就不再被重新发现。***Do not make the model rediscover what you already know.***
- **The WHAT** — skill 是一个文件夹：**一段决定何时的 description、一份说明如何的 procedure、一条 definition of done、以及跑而不是推理的脚本**——只在相关时加载。
- **The HOW** — description 当触发器写并带排除项 · 核心保持精简 · 确定性步骤移进脚本 · **分开测触发和行为** · **跑任何陌生人的 skill 之前先读它**。

> **And then find out where yours breaks. Tonight.**

---

## Coda · Hokusai at Seventy-Three（p.27）

**1834 年**，北斋出版《富岳百景》并加了一则跋。他写道自己**六岁**就开始画，**七十岁以前做的东西都不值一提**；**七十三岁**时他开始抓住鸟兽虫鱼的结构和草木生长的方式。**他希望到九十岁能更深地看进事物的核心。** 署名"**the old man mad about drawing**"。

> 边注：**这是转述，译本各不相同。他那时已经是日本最著名的画家，《神奈川冲浪里》早已在他身后。**

**理解总是迟到。** 黑格尔的意象：**the owl of Minerva takes flight only at dusk**（《法哲学原理》序言，柏林，1820 年 6 月 25 日）。**我们在一件事的白天过去之后才理解它。** Harrison 只有在造出 H2 之后才看见它的缺陷——然后开始造 H3。

**Coda 要带走的那一行：**

> **Every stage of mastery is the vantage point from which the last one looks broken.**

> **那就是今晚该有的心态。你七点钟拥有的 skill，会让你六点钟拥有的那个显得不完整。那不是失败。那是手艺在起作用。**

---

## The Lab · An Appointment in Samarra（p.28–30）

### 故事（p.28）

巴格达的商人派仆人去市场。仆人回来时脸色苍白、发抖：人群里他被死神撞到，死神看着他做了一个他当成威胁的手势。他求主人借马，拼命骑向 **Samarra**，死神在那里找不到他。

商人下到市场找到死神，问她为什么威胁他的仆人。**她说她并没有威胁的意思。她只是很惊讶在巴格达看见他，因为他们两个本来当晚就该见面——在 Samarra。**

> **An appointment is a place and a time. Death never gets either wrong. That is the standard for tonight.**

> 边注，把它接回上周：**注意仆人做了什么：他用自己的先验填补了一段沉默——一个手势。Week 2，发生在一个市场里。**
>
> 出处：Somerset Maugham, *Sheppey*（1933）第三幕死神之口；更早的版本在《巴比伦塔木德》Sukkah 53a。

### 愿望（p.28）

**Zara Malik** 在 Fremont 的 **Tigris Works** 管工程。人们写信给她要求见面。她把消息转发给她的 agent，加一句：

> **Put it on my calendar.**

**构建实现这个愿望的 skill。** 给定一条消息和那一行，你的 skill 交给 Zara 一个**正确会议、正确时间**的 `.ics` 邀请文件。**做不到时，它做两件事之一：说明为什么不行并提供可行的时间，或者问她一个问题。**

> **That is the whole specification.** skill 必须叫 **`when-the-time-is-right`**。

### kit 里有什么（p.29，16:40 下载）

**从 `brief.pdf` 开始，两页多一点。**

| 文件 | 是什么 |
| --- | --- |
| `brief.pdf` | 项目：建什么、怎么打包、怎么安装 |
| `owner/profile.md` | **Zara 自己写的日历规则，一页** |
| `owner/calendar.ics` | 她导出的日历；**大约三分之一是空的** |
| `cases/given.md` | **一百个请求，每个带正确结果，给人读** |
| `cases/given.jsonl` | 同样一百个，给程序读 |
| `check.py` | 对一个案例打勾或打叉 |
| `drawer/` | 四个小脚本；**用它、改它、或者无视它** |
| `when-the-time-is-right/` | 你的 skill 文件夹，里面有待替换的 `SKILL.md` |
| `pack.py` | 把你的文件夹打包成 `.skill` |

> **Read the cases. They are the rest of the specification.**（**案例本身就是规格的其余部分**——这句很关键。）一百个是你的，**另一百个扣住，其中十二个 19:45 上屏。**

**三个 tier：** Tier 1 读懂请求 · Tier 2 时区与节假日 · Tier 3 Zara 自己的日历和规则。**checkpoint 之前所有人都在 tier 1。**

```bash
python3 check.py g-017 --show                   # 读这个案例
python3 check.py g-017 --invite my-invite.ics   # 我的 skill 这样订了
python3 check.py g-020 --ask day                # 我的 skill 问了关于哪天
python3 check.py --help                         # 其他回答方式
```

> **One case, one mark. There is no total.**

### The Drawer（p.30）· **四个工具，没有说明书**

| 脚本 | 做什么 |
| --- | --- |
| `convert_time.py` | 把一个时间从一个时区转到另一个 |
| `find_holidays.py` | 说某一天在某地是不是公共假日 |
| `count_business_days.py` | 从某天起往前数工作日 |
| `write_invite.py` | 从标题、开始、结束写出一个邀请文件 |

每个都用 `--help` 打印用法。

> **Nobody will tell you when to reach for which. Some steps want judgment. Some want a script. Knowing which is the skill.**

### 每一步都要一个检查（p.30）

回忆 Week 2 的 verifier 阶梯：**同一个 prompt 尾部的一个检查 · 一次独立调用 · 一个不同的推理基底 · 一组确定性检查构成的 rubric。**

> **今晚你发现的每一步都会想要它自己的 verifier，而今晚大多数检查可以待在最上面那一级：十行代码，每次给出同样的答案。**

### 晚上怎么跑（p.30）

| | |
| --- | --- |
| **16:40** | 故事、愿望、kit。**全员 tier 1** |
| **18:15** | Checkpoint。**答案的形状**：有哪些步骤、每个检查放在哪、哪些步骤 reason 哪些 run。**发放 tier 1 的参考 skill** |
| **18:30** | Tier 2 和 3，留下来的人 |
| **19:45** | 十二个没人见过的请求，上屏 |

**The Hall of Traps.** 发现一个骗过你 skill 的案例，**写到板上给全场**：案例编号，加一行说明你的 skill 假设了什么。

> 上周的 Hall of Loopholes 给了我们 COSTAR。看看这周的厅会给什么。

### ⭐ 什么算一个好的晚上（p.30）

> **A skill that handles tier 1 well, and says so when a request is beyond it, is a good evening's work.**
> **A skill that books confidently and wrongly is not — however many cases it gets right.**

---

## From Folder to Agent：打包与安装（p.31–33）

> **A skill that is not installed is an essay.**
>
> **这一节值得在你写 skill 的第一行之前就读**，因为**skill 将在哪里运行，塑造了什么该进到它里面去。**

### 磁盘上的结构（p.31）

```
when-the-time-is-right/
    SKILL.md      required: front matter + instructions
    scripts/      optional: agent 运行的程序
    references/   optional: agent 只在需要时才读的页
    assets/       optional: 脚本用的数据
```

```markdown
---
name: when-the-time-is-right
description: What the skill does, and when to use it.
---

# When the time is right
The steps the agent follows...
```

### 五条保持可移植的规则（p.31）· **破坏一条，上传失败或者它永远不醒**

1. **name**：小写字母、数字、连字符，**最多 64 字符，并且和文件夹同名**。今晚：`when-the-time-is-right`。
2. **description**：说清**做什么和何时用**，**最多 1,024 字符，不含尖括号**。
3. **有且只有一个 `SKILL.md`，大写拼写。**
4. 指令里**用相对 skill 文件夹的路径**点名其他文件，如 `scripts/convert_time.py`。**告诉 agent 用完整路径运行脚本。**
5. **脚本只用 Python 标准库。两个 agent 都不会替你装包。**

> **第六条，能让人损失一小时的那条：** front matter **只保留 `name` 和 `description`**，除非你确知两个 agent 都接受那个额外的 key。**顶层写一行 `version: 1` 会让其中一个直接拒绝上传。**

### 打包（p.32）

**一个 `.skill` 文件就是一个 zip，根层是 skill 的文件夹，再无其他。**

```bash
python3 pack.py when-the-time-is-right
```

packer 检查程序能检查的东西——name、description、front matter 的 key、唯一的 `SKILL.md`——然后写出**两个一模一样的文件**，一个 `.skill` 一个 `.zip`。

手动打包（**从你 skill 的上一层目录**）：

```bash
zip -r when-the-time-is-right.skill when-the-time-is-right
```

> ⚠️ 边注：**最常见的错误是压缩文件夹里的内容。归档里的第一个东西必须是那个文件夹本身。**

### 装进 Hermes（p.32）

Hermes 把 skill 放在 `~/.hermes/skills/`，一个文件夹一个。**安装就是解压。**

```bash
# Mac / Linux
unzip -o when-the-time-is-right.skill -d ~/.hermes/skills/

# Windows PowerShell（用 .zip 那份）
Expand-Archive when-the-time-is-right.zip `
    -DestinationPath $HOME\.hermes\skills -Force

hermes skills list        # 应列为 local skill，enabled
```

然后**开一个新 session，或者在现有的里 `/reset`**——**Hermes 在 session 开始时读架子。**

贴一个案例的消息，再贴 Zara 那一行，看它醒不醒。**要按名字强制调用，不管描述说什么，就以 `/when-the-time-is-right` 开头。**

> 边注：**还在改 skill 的时候就别打包了：直接编辑 `~/.hermes/skills/` 里那份，每次改完 `/reset`。能用了再打包。**

Hermes **在它启动的那个终端里、用那台机器的 `python3` 跑你的脚本。你的 skill 写出的文件落在那个文件夹里。**

### 装进 Claude Desktop（p.33）

**在 Claude 里 skill 是被上传的，而且它在 Claude 自己的 sandbox 里跑，不在你的电脑上。**

1. Settings → Capabilities → 打开 **Code execution and file creation**。
2. **Customize → Skills** → **+** → **Create skill** → **Upload a skill** → 选 `when-the-time-is-right.zip`。
3. 确认新 skill 的开关是开的。
4. 开新对话，贴案例消息和 Zara 那一行。**Claude 自己决定要不要用这个 skill；展开它的思考看它用没用。**
5. 要改 skill，**重新打包再上传一次**。

> 边注：**这些标签名是 Anthropic 帮助页在 2026 年 10 月 2 日的样子。如果标签挪了，到 Customize 下面找 Skills。同一个文件夹解压到 `~/.claude/skills/` 在 Claude Code 里也能用。**

### ⭐ 两台机器，两套后果（p.33）· 速览里没有这张表

| | **Hermes** | **Claude Desktop** |
| --- | --- | --- |
| **脚本在哪跑** | 你的机器上，Hermes 启动的那个终端里 | **Claude 的 sandbox 里** |
| **哪个 Python** | 你机器的 `python3` | **sandbox 的** |
| **你的文件** | **可见** | **不可见** |
| **网络** | 你机器有什么就是什么 | **常常没有** |
| **更新 skill** | 就地编辑，然后 `/reset` | **重新打包并重新上传** |

**由此推出两件事：**

1. **你的 skill 需要的一切——Zara 的日历、她的 profile、你的脚本、drawer 的数据——都必须在你打包的那个文件夹里面。**
2. **一个从网络取东西的脚本，应当预期它在两者之一里会失败。**

> **而且心里要把两个文件夹分开：skill folder 是你的指令、脚本和数据住的地方，把它当作只读；working folder 是邀请被写出来的地方。**
>
> **一个在"当前文件夹"里找数据的脚本，在你的机器上、在你写它的那天能用，在别处都不能用。**

### ⭐ When It Does Not Work（p.34）· 排错表

| 你看到的 | 去哪里找 |
| --- | --- |
| **上传被拒绝** | 那五条规则：name、文件夹名、front matter 里多余的 key、第二个 `SKILL.md` |
| **装上了但从不醒** | **description：它说了"何时"吗？用的是 Zara 会敲的那些词吗？** |
| **为不属于它的请求醒来** | **还是 description：说清楚什么时候不要用** |
| **脚本"找不到"** | **路径：用从 skill 文件夹算起的完整路径，不是当前文件夹** |
| **脚本需要更新的 Python** | 见"Before You Arrive"的边注（`uv run --python 3.12`） |
| **在 Hermes 里好用，在 Claude 里失败** | **包外的一个文件，或者一次网络调用** |
| **agent"自己把算术做了"** | **指令：它们说清楚了为什么必须用那个脚本吗？** |

---

## A Field Notebook for the Evening（p.34–36）

> **你能带到 checkpoint 的最有用的东西，不是一个能用的 skill。是一张清单。**

### 你找到的步骤（p.35）

> deck 说那个愿望看起来是一步、其实超过十步。**不要照单全收。自己数。** 每当你发现你的 skill 需要做一件它还没在做的事，加一行。

| # | 步骤 | Reason, or run? | 什么检查它？ |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |
| 11 | | | |
| 12 | | | |

### 你掉进去的陷阱（p.35）

| Case | 我的 skill 假设了什么 | 那条消息其实从没说过什么 |
| --- | --- | --- |
| | | |

### ⭐ 七个该问自己 skill 的问题（p.35–36）

**这是把一天的想法转过来对准你自己的作品。原文强调：这些都不是关于案例的提示。**

1. **从 Literal Cook：** 像厨子那样读你的指令。**六个缺口里哪一个还开着？有 Done when 吗？**
2. **从 Which Scroll Wakes?：** 你的 description 说了何时使用吗，**用的是 Zara 会敲的那些词**？说了何时**不**用吗？
3. **从 Context Window：** **你的正文精简吗？什么可以挪进一个只在需要时才读的 reference 文件？**
4. **从 Run, Don't Reason：** 对你清单上的每一步，**你愿意拿一场会议赌模型每次都做对吗？**
5. **从 Bazaar：** **那条消息是别人写的文本。你的 skill 是这样对待它的吗？**
6. **从 Forge：** 文件夹过格式吗？**在两个 agent 里都装得上吗？**
7. **从 Week 2：** **那条消息留下了什么未说——而你的 skill 是去填补那段沉默，还是指出它？**

---

## The Week Ahead（p.36）

> **实验不在八点结束。** 本周的 TA session 会把完整解法打开走一遍，旁边配一份 deck **《What Did We Miss?》**：每一步、每一个检查、每一个必须做出的决定。**你会拿到完整的 skill 和一份解释它的文档。**
>
> **带着你的 field notebook 来。在那里你能做的最有价值的事，是把你的步骤清单摆在解法的清单旁边，找出你没有的那几条。**

> 边注：**如果你晚上还在做、并且当场就想看完整解法，开口要。做过自己的尝试之后，它就是你的。**

### 作业（p.36–37）

1. **把你的 skill 装进两个 agent**（Hermes 和 Claude Desktop），**各跑同样三个案例**。**它在两边都醒了吗？行为一样吗？**
2. **带着 field notebook**——你找到的步骤和掉进去的陷阱——去 TA session。
3. **从你自己的工作里锻一个 skill。** 拿一个你团队反复做的流程，把它的 description 写成**带排除项的触发器**、写它的步骤、写它的 **Done when**。**用 Literal Cook 反复 taste-test 直到他被绑住。然后锻它、装它。**
4. **选做：审计一个公共市场上的 skill，在安装之前。** 读正文和每一个脚本。**用两行写下它在你的机器上本来可以做什么。**

### 选做实验：那个脚本真的必要吗？（p.37）

> **也许你相信一个足够强的模型处理日期不需要脚本。很好：**把这个信念放到一个能让它难堪的测试里。

在 **Run, Don't Reason** 里选**你能用到的最强模型**和任务 **Weekdays in a span**。**关闭 Show its working 跑二十次，打开再跑二十次。**

1. 每一种方式各回来了多少个**不同的**答案？
2. 然后**选一个你认为更难的 span**——里面有某个匆忙的读者会漏掉的东西。**模型漏了吗？**
3. 如果模型每次都对，**那么千分之一次错会让你付出什么代价——而你又会怎么发现自己错了？**

> 边注：**旗舰模型按其身价定价。四十次短调用，不是一个循环。**

**⭐ The takeaway：**

> **A stronger model is right more often. A script gives the same answer every time, so when it is wrong it is wrong where you can see it, and it is fixed once. For a step that must not fail, "more often" is the wrong kind of answer.**
>
> 🧠 "**错得看得见，而且一次就修好**"——这是确定性真正的价值，不是"更准"。

---

## 阅读清单（p.37–39）

### Essential Readings（五篇，附原文的读法建议）

| 文献 | 原文怎么说该怎么读 |
| --- | --- |
| **Anthropic, Agent Skills: the open format**（agentskills.io，2025-12-18） | **规范本身很短。把你自己的 `SKILL.md` 打开放在旁边读，注意它要求的东西有多少——一个 name 和一个 description。** |
| **Wang et al., Voyager**（arXiv:2305.16291） | **那个没微调却变强的 agent。为它的三个器官而读，并问：你自己团队的库有其中哪几个？** |
| **Sutton, Precup & Singh, Between MDPs and Semi-MDPs**（AI 112.1–2, 1999, pp.181–211） | **options 框架。只需要前几页：那个三元组，以及一个动作"在时间上延展"意味着什么。** |
| **Gao et al., PAL**（ICML 2023, arXiv:2211.10435） | **Run, Don't Reason 背后的论文。模型读；解释器算。** |
| **Simon Willison, The Lethal Trifecta for AI Agents**（2025-06-16） | **带着 Bazaar 重读一遍。一个陌生人的 skill 是带着入口的不可信内容。** |

### Oliver Twist's List（选读）

| 文献 | 为什么 |
| --- | --- |
| **Dava Sobel, *Longitude*（1995）** | Harrison 和他的钟、以及 Maskelyne 的完整故事。**一晚上读完，而且你会在课程结束前再见到那位皇家天文学家。** |
| **Shinn et al., Reflexion** / **Zhao et al., ExpeL** | 用词语从失败中学习。**每一个会编辑自己的 skill 的种子。** |
| **Liu et al., Lost in the Middle**（TACL 2024） | 为什么无关上下文不免费。**看曲线的形状；它们不是 Act II 那张卡通画暗示的样子。** |
| **Snyk Security Labs, ToxicSkills**（2026-02） | **一次对社区 skill 的审计实际发现了什么。在你从任何市场安装任何东西之前读它。** |
| **Christopher Alexander, *The Timeless Way of Building*（1979）** | pattern language 的来处。**它讲的是建筑，而它讲的是一切。** |
| **RFC 5545, iCalendar**（2009-09） | **Zara 日历的格式，也是你写的邀请的格式。今晚之后再翻日期与时间那一节；你会用新的眼睛读它。** |
| **Agrawal et al., GEPA** / **Zhang et al., ACE**（2025） | **我们今天飞越的 territory：会自我改进的 skill 和 prompt。Tools 之后我们降落在那里。** |

> ACE 的文献条目里还点明了它的贡献：**Generator / Reflector / Curator；命名了 context collapse 和 delta-only update 的纪律**（arXiv:2510.04618）。

---

## A Calibration Note（p.39）· 全文最后一段

> **这一天是一个想法，遇见三次。**
>
> 一个木匠花三十年造了四台机器，**而活得比它们都长的是一小把流程**。那是**作为历史**的那个想法。
>
> 然后我们把它拆开：skill 是一个文件夹；**它的 description 决定它会不会被读；它的正文是一份需要 definition of done 的流程；它的脚本去跑，好让模型不必猜；而这一切在它的时刻到来之前都不该出现在模型面前。** 那是**作为工程**的那个想法。
>
> 然后在晚上，你被递了一行话，被要求把它变成一个 skill——**并且发现，我希望，那一行藏着超过十个步骤，而每一步都想要一个检查。** 那是**作为经验**的那个想法。
>
> **如果这个晚上让人谦卑，那是故意的，而且你有很好的同伴。Harrison 只有在造出 H2 之后才发现它的缺陷。北斋认为自己七十岁之前画的东西都不值一提。**

**收束的那一段（整份讲义的结论）：**

> **We spent last week learning that the hardest part of a wish is the part we never say. This week we learned what to do about it: write the procedure down, put it where it will be found, let a program do what a program does better, and check every step. It always looks deceptively simple. Doing it correctly, with verifiers, is hard — and it is the whole craft.**

**下周：** Tools——**prompt 伪装成文档的地方**。

> **一个 tool 的 description 是模型为了决定调用什么而读的东西。你已经知道那会怎么发展。你今天上午一整个早上都在写决定什么东西醒来的描述。**

---

## 索引里的关键词（p.42，可当复习清单）

agent 7 · Agent Skills standard 17 · behaviour test 21 · context engineering 13 · Cook's footnote 10 · design patterns for skills 23 · dry-run pattern 24 · escalation ladder 25 · firing test 21 · Hall of Traps 30 · harness 12 · Harrison, John 5 · Hermes 4 · Hokusai 27 · loading rule 13 · longitude problem 5 · Maskelyne, Nevil 6 · options framework 14 · progressive disclosure 8 · Reflexion 17 · run or reason 20 · Samarra, appointment in 28 · skill 2 · SKILL.md 7 · tool 6 · triggering problem 15 · verifier 30 · Voyager 16

---

## 精读后我自己的三条

1. **"You cannot close every gap by writing more."**（p.11）——这条和我的直觉相反。以前写 SOP 总想写得更全，但真正起作用的是**加一条可验收的 Done when**。这也是 option 三元组里最容易漏掉的那一项。
2. **两套测试要用两个 agent 来做**（p.22，"agent A authors; agent B, with no memory, tests"）——写的人没法测自己的触发边界，因为他知道自己想让它触发什么。这一点在我自己的 skill 上同样成立。
3. **"A model's arithmetic is a sample from a distribution. A script's is not."**（p.21）——以及更锋利的那句：**对一个不能失败的步骤，"更经常对"是错误种类的答案。** 判断什么该 run 的标准不是"模型能不能做到"，而是"我愿不愿意拿客户的发票赌它每次都对"。

## 待办

- [ ] 从课程门户拿 `genies-kitchen.zip`，按 p.3 跑通，确认 `hermes skills list` 有输出
- [ ] 确认本机 `python3 --version` ≥ 3.10（Mac 自带是 3.9，用 `uv run --python 3.12`）
- [ ] 按 p.10 的七张菜品卡先写预测，再读 Cook's footnote，统计我猜中几个
- [ ] 按 p.11 的格式记 Which Scroll Wakes? 的"预测 n/8 → 实际 n/8"
- [ ] Lab 期间用 p.35 的三张表格记录（步骤 / 陷阱 / 七问）
- [ ] 作业 3：选一个自己的重复流程锻成 skill，候选见 `usecase-data-fix-agent.zh.md`
- [ ] 选读 ToxicSkills，在从任何市场装 skill 之前
