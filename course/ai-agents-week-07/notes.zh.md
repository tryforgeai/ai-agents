# Week 07 课堂笔记（2026-11-01）

> 讲义结构见 [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)；这里记课上讲义之外的口头补充和板书。

# 上午 · 白板（Asif 在 OneNote 上讲）

## 板书 ① · 模型 = 函数 ŷ = f(x | θ, ω)（13:00，OneNote 页「Prompt Optimization」）

**画面（上半）**：x = "What is 2+2?" → 【Model】 → $\hat y = f_\theta(x)$

**画面（中间，框起来的重点）**：

$$\hat y = f(x \mid \theta, \omega)$$

- **x**：输入，也就是 prompt 加上问题
- **θ**：模型参数（权重），训练完就冻结
- **ω**：箭头指向「temperature, sampling …」，即**推理时的解码设置**：温度、top-p/top-k、采样方式等，不是训练出来的，每次调用都可以改

**画面（下半）**：模型内部的流水线

1. 每个输入 token 变成向量 $v_i = e_i + p_i$，即**词嵌入 + 位置编码**
2. 经过模型层，输出 **logits**，词表里每个 token 一个分数
3. softmax 之后得到概率分布，**sampling** 抽出下一个 token，例子是 "aardvark"，即 $p_\theta(\text{aardvark} \mid x)$

### 板书 ①b · 补上第四个参数：system prompt（约 13:45）

$$\hat y = f(x\,;\ \theta,\ \omega,\ ?)$$

| 符号 | 板书标注 | 含义 | 谁能动 |
| --- | --- | --- | --- |
| **x** | user prompt | 用户这一次的输入 | 每次调用都不同 |
| **θ** | param | 模型权重 | 训练时才变；推理时冻结 |
| **ω** | hyperparam | 温度、采样等解码设置 | 可以调，但影响有限 |
| **?** | **system prompt** | 每次调用都带着的那段固定指令 | **← prompt 优化要搜的就是它** |

（同一块板上，softmax 例子里的 28 也被改成了 7，和同学画的图一致。）

**随后板书更新为**：

$$\hat y = f(x\,;\ \theta^*,\ \omega,\ \Phi)$$

- 「?」揭晓为 **Φ = system prompt**（下面画了下划线）
- θ 加了星号成为 **θ\***：训练已经把权重优化到最优点，到推理时它是**一个已经找好的定值**，不再变
- 「param」也画了下划线：强调 θ\* 是**参数**，Φ 才是我们现在要搜的东西

> 一句话：**训练已经求出了 θ\* = argmax，prompt 优化是在 θ\* 固定的前提下，再求 Φ\* = argmax。**

**接着板书在下方写了：x → ŷ → y**（system prompt 被圈出来）

- **ŷ**（y-hat）：模型**实际输出**的答案，即 f(x; θ\*, ω, Φ)
- **y**：**你真正想要的答案**（讲师原话："y is what you really want"），即 reference / 标准答案
- 箭头 ŷ → y：要让模型的输出**逼近**你想要的结果。两者之间的差距由 **metric µ(ŷ, y)** 来衡量 → 这正是讲义式 (1) 里的 $\mu(\Phi(x;\theta), y)$

> 合起来：**θ\* 和 ω 不动，换不同的 Φ（system prompt），让 ŷ 尽可能接近 y。** 这就是 prompt 优化的问题定义。「接近」由谁来定义？由 metric 来定义 → 所以「optimizer 只和 metric 一样好」。

**再往下：Demonstrations（示例集）**

```
        user input   output / response
      ⎛  x₁,          y₁   ⎞
      ⎜  x₂,          y₂   ⎟
      ⎜   ⋮            ⋮   ⎟
      ⎝  xₙ,          yₙ   ⎠
```

- 一组 **(输入, 期望输出)** 对：xᵢ 是用户输入，yᵢ 是你真正想要的回答
- 这就是讲义里 θ = (π, δ) 的 **δ**，同时也是优化器的**数据集**。它有两个用途：
  1. **放进 prompt 当 few-shot 示例**（δ 本身就是被优化的参数之一，DSPy 的 BootstrapFewShot 就是在挑选这些）
  2. **当测试题**：把 xᵢ 喂进去得到 ŷᵢ，再用 metric µ(ŷᵢ, yᵢ) 打分。拿全部 n 条的平均分来比较不同的 Φ
- 联系 field notes 第一课「**The grunt work is the data**」：这 n 对要人工逐条审过，一条错的 yᵢ 会被反思模型当成教训写进 prompt；而且要分成 feedback / Pareto / holdout 三份，不能全用来优化

**对每一条 demonstration 跑一遍模型**：

$$\hat y_i = f(x_i\,;\ \theta^*,\ \omega,\ \Phi) \quad\longleftrightarrow\quad y_i$$

- 板书右边写的是 **ŷ ↔ y**（双向箭头）：拿模型的输出和标准答案**比对**
- 注意公式里**只有 xᵢ 带下标**：θ\*、ω、Φ 对所有题都是同一套。换一个 Φ，n 道题全部重跑一遍，才能比较两个 Φ 谁更好
- 这就是讲义式 (1) 的手写版：$J(\Phi) = \frac1n\sum_i \mu(\hat y_i, y_i)$，再求 $\Phi^\* = \arg\max_\Phi J(\Phi)$
- 🧭 成本也从这里来：评估**一个**候选 Φ = n 次模型调用（讲义里的诅咒 III「昂贵」）；分数是 n 条的平均，n 有限所以有噪声（诅咒 II，n=50 时约 ±6.5 点）

**然后圈出 metric**：

$$\mu(\hat y_i,\ y_i\ ;\ x)$$

- µ 把**模型输出 ŷᵢ** 和**标准答案 yᵢ** 比较，给出一个分数
- 注意**第三个参数 x**：打分时可能还要看**输入本身**。例如判断「回答是否切题」、「有没有引用原文里的证据」、LLM-as-judge 要先读问题才能判对错——光比较 ŷ 和 y 不够
- 「Demonstrations」也被圈了出来：**数据 + metric** 就是 prompt 优化的两样原料（对应 field notes 的前两课：grunt work is the data / the thought is the metric）
- 🧭 讲义 DSPy 代码里的 `metric(gold, pred, trace=None, ...)` 就是这个 µ：`gold` = (xᵢ, yᵢ)，`pred` = ŷᵢ

⚠️ **第二个记号冲突**：讲义里 **Φ 是整个程序**（LM 调用 + 工具 + 控制流，式 (1) 的 $\Phi(x;\theta)$），θ = (π, δ) 才是 prompt。板书里 **Φ 是 system prompt**，θ\* 是权重。对照表：

| 东西 | 板书记号 | 讲义记号 |
| --- | --- | --- |
| 模型权重 | θ\* | 不出现（冻结） |
| system prompt（指令 + 示例） | **Φ** | **θ = (π, δ)** |
| 整个 LM 程序 / pipeline | f | **Φ** |
| 解码设置（温度、采样） | ω | 不出现 |

**这样就和讲义对上了**：讲义式 (1) 写的 $J(\theta)$，里面的 θ = (π, δ) 就是这个「?」——**system prompt 里的指令 + 示例**。板书把权重叫 θ，讲义把 prompt 叫 θ，**名字冲突，指的东西不同**：板书的「?」= 讲义的 θ。

🧭 **我的理解**：

- 同一个 x，输出 ŷ 由两类东西决定：**θ（权重，动不了）**和 **ω（解码设置，能调但通常不是重点）**。**prompt 优化动的是 x 里的那段指令**，三者里唯一既便宜又能大幅改变行为的就是它。
- ⚠️ **记号冲突**：板书的 θ 指**模型权重**；讲义式 (1) 的 θ = (π, δ) 指 **prompt（指令 + 示例）**，权重在讲义里是「冻结、不出现」的。两处 θ 不是同一个东西，复习时别混。
- $v_i = e_i + p_i$ 是 Transformer 原论文的**加法**位置编码；现在的模型多用 RoPE（旋转位置编码），不是直接相加。见 [Attention 精读](<../../Attention Is All You Need 论文精读笔记.md>)。

## 板书 ② · softmax、温度与采样

**画面**：左边一个直方图，标着 *distribution*，横轴是 token（i、j、k、l…），下面写 *Sampling off the softmax*；中间是一列 logits 经过 softmax 变成概率；右上角是 $P_\theta(\text{zephyr} \mid x)$ 和 $\sum_t P_\theta(t \mid x) = 1$。

**流程（从左到右）**：

1. 模型最后一层对每个候选 token 输出一个原始分数 **logit**。板书的例子是 `[-1, 9, 28, 5, -3]`，可以是负数，加起来也不等于 1。
2. **除以温度 T**（粉色框 "divide by Temperature"）。
3. **取指数** $e^{z/T}$，把所有分数变成正数（"positivize"）。
4. **除以总和 Σ 做归一化**（"normalized"），得到概率分布，加起来等于 1：

$$P_\theta(t_i \mid x) = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}$$

5. **从这个分布里抽样**，选出下一个 token，比如 "zephyr"。

**温度 T 的作用**：粉笔圈出了 T = 0.1、1、10 三档，划掉了 2、3、4…100。

| T | 效果 | 用 `[-1, 9, 28, 5, -3]` 算的结果 |
| --- | --- | --- |
| **0.1**（低） | 分布变尖，几乎总选最大的那个 → 接近贪心、确定性 | ≈ [0, 0, **1.00**, 0, 0] |
| **1** | 原始分布 | 28 比 9 高出 19，$e^{-19}$ ≈ 5.6×10⁻⁹ → 仍然 ≈ **1.00** |
| **10**（高） | 分布变平，冷门 token 也有机会被抽到 → 更多样、更「有创意」 | ≈ [0.04, 0.11, **0.74**, 0.07, 0.03] |

（T=10 的算法：logits÷10 = [-0.1, 0.9, 2.8, 0.5, -0.3] → 取指数 [0.905, 2.46, 16.44, 1.65, 0.741]，总和 22.2 → 除以总和。）

### 同学的演示：把 28 换成 7（Suganthi 共享屏幕，ChatGPT 画图）

板书里 28 比其他分数高太多，T=1 时几乎看不出温度的作用。所以换成 logits = `[-1, 9, 7, 5, -3]`，画了五个温度（我自己验算过，和图一致）：

| T | -1 | **9** | 7 | 5 | -3 | 形状 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | 0 | **1.00** | 0 | 0 | 0 | 只剩一根柱子（贪心） |
| 1 | 0.00 | **0.87** | 0.12 | 0.02 | 0.00 | 头部很集中 |
| 5 | 0.06 | **0.43** | 0.29 | 0.19 | 0.04 | 明显变平 |
| 10 | 0.12 | **0.32** | 0.26 | 0.21 | 0.10 | 更平 |
| 100 | ≈0.19 | ≈0.21 | ≈0.21 | ≈0.20 | ≈0.19 | 接近均匀分布，等于乱抽 |

要点：**温度不改变排名**，9 永远是概率最高的；它只改变**差距**。T→0 时变成永远选第一名，T→∞ 时变成均匀乱选。

🧭 **和今天主线的接线（我的理解）**：

- **诅咒 II（有噪声）的来源之一就在这里**：只要 T > 0，同一个 prompt 每次跑出来的结果都可能不同，所以 $\hat J$ 是带噪的估计，需要多个 seed、足够大的 n。
- **讲义 p.19 的代码里，反思模型用的是 `temperature=1.0`**：反思要「提出不同的改法」，需要多样性；任务模型做评测时往往要低温，以减少噪声。
- 勘误 W4 里有一条「听着不对但其实是对的」：**温度为 0 时输出仍可能变化**（浮点误差、批处理等原因），所以 T=0 也不能代替多 seed 重跑。

# 上午 · Deck：Orientation

## Deck p.2 · Three things you will do（13:37 打开，deck 共 119 页）

| When | What |
| --- | --- |
| 11:00 | Six Questions, One Trap |
| 12:00 | Harrison's Workshop —— 和 bench 搭档一起，在 bench 吃午饭 |
| 13:45 | The Genie's Exam |

> *"Names only. What each one is for, you find out by doing it."*

⏱️ 实际进度：13:37 deck 才翻到第 2 页，上午的时间花在了白板（模型函数、softmax、温度）上，比讲义时间表晚了不少。

## Deck p.4 · Week 6 Debts from last Sunday：Credits owed

把上周课上同学说对、讲师当时判错或没确认的地方，补回「学分」：

| 标题 | 内容 | 结论 |
| --- | --- | --- |
| **The battery that wanted one turn** | Door 1 判一个「先提出给店内积分、然后等待」的 agent 失败 | **同学对**；kit 已于 10/26 修复 → 重新下载 strangers-toolbox |
| **"It's already happened"** | 英国夏令时那天早上已经结束 | **同学对**：那一周伦敦与加州时差是 **7 小时，不是 8 小时** |
| **One template, three substrates** | 按 rubric 写的 label，原封不动跑在三个模型上 | **每次答案都一样**——好 label 可以跨模型迁移 |

## Deck p.5 · Two epigraphs to hold all day：Fail better — but measure it

- Beckett：*"Ever tried. Ever failed. No matter. Try again. Fail again. Fail better."*
- Goodhart（Strathern 的表述）：*"When a measure becomes a target, it ceases to be a good measure."*

> **"The first is the optimizer's loop. The second is its conscience."**
> 第一句是优化器的循环（试 → 失败 → 改 → 再试）；第二句是它的良心（分数一旦被当成目标就会被钻空子，所以 metric 要防作弊、要有 holdout）。

## Deck p.7 · Last week's Owl：Week 6, in five lines

1. **A tool's description is a prompt the model reads on every turn** — write it like a glass hammer: what it does, when to use it, when not to, how to call it, and why it exists.
2. **Clarity, scope, politeness, trust**: a good tool says exactly what it does, does one thing, returns only what is needed, and never obeys the text it fetches.
3. **A call can arrive twice**; make every side effect safe to repeat.
4. **Nothing is in the model**: the state lives in your harness, not in the weights or the server.
5. **No castle without walls**: before a tool ships, decide who may call it, as whom, through which gate.

🧭 中文速记：① 工具描述 = 每轮都读的 prompt，写「做什么 / 何时用 / 何时不用 / 怎么调 / 为什么」；② 说清楚、只做一件事、只返回需要的、不听抓回来的文本；③ 调用可能重复 → 副作用要幂等；④ 状态在 harness，不在权重也不在 server；⑤ 上线前先定权限：谁能调、以谁的身份、经过哪道门。
（第 1 条就是早上复述题「label 必须告诉模型的五件事」的官方答案：**what / when / when not / how / why**——和我 lesson-plan 里猜的「description / schema / error / contract / 返回值」不是同一组。）

## 小测 · Six Questions, One Trap（共 7 页）

### Quiz 1 — Half of Cloudflare?（p.8）

经理转来标题「Half of Cloudflare is agents now!」——上周的 48% 是什么的占比？

- (a) Cloudflare's web traffic
- **(b) uses of Wrangler, Cloudflare's developer command line, in one week** ✅
- (c) Cloudflare's staff, quietly replaced
- (d) MCP servers hosted on Cloudflare

**答案 (b)**（勘误 W6 #1）：Cloudflare 9/28 发布 agent 用的命令行 `cf` 时说，前一周 **Wrangler 的调用中 48% 来自 agent**。这说明「谁在操作开发者工具」，**和 Cloudflare 的网络流量无关**（流量是大得多的另一个量）。

**Say it back：为什么一个数字的单位比数字本身更重要？** → 48% 本身没有意义，**「什么的 48%」才是信息**；分母一换，结论从「半个互联网是 agent」变成「一个 CLI 一半是 agent 在用」。🧭 和今天的接线：metric 也一样，**分数要说清是在哪个集合、哪个 slice 上算的**（burned / pressured / clean 三份数据上的同一个「0.84」意义完全不同）。

### Quiz 2 — Only the names?（p.9）

同事说：「`tools/list` 只发 name 和 description，所以润色文字就行。」每个工具实际返回什么？上周的研究里什么对选择影响最大？

- (a) name and description; the description
- **(b) name, description and input schema; the schema** ✅
- (c) name, description and source code; the code
- (d) a vibe; the vibe

**答案 (b)**（勘误 W6 #13）：`tools/list` 对每个工具返回 **name + description + inputSchema**（JSON Schema），schema 和 description 一起进模型上下文。上周的研究 `2610.14334`：**参数 schema 对工具选择的影响最大**（3.82，对比 server 名 1.48）。

**Say it back：现在先检查 label 的哪一部分？** → **schema**：字段名、类型、枚举、必填项、取值范围。它是 prompt 的一部分，而且是模型最看重的那部分；只润色 description 是只修了一半。

### Quiz 3 — Paid twice, again（p.10）

Door 12：$50 退款已经成功，但网关超时；热心的 agent 又调了一次。哪个改动能让第二次调用去问「已经发生了吗？」，而不是再付一次？

- (a) make the refund tool reentrant
- (b) make the server stateless
- **(c) carry an idempotency key on the call** ✅
- (d) retry three times, firmly

**答案 (c)**：调用时带上**幂等键**（同一笔退款用同一个 key）。服务端看到重复的 key → **不再执行，直接返回第一次的结果**（「这笔 $50 已于 xx 时退款成功，退款号 …」）。

**为什么另外三个不对**（勘误 W5 #4 区分过这几个词）：
- (a) **reentrant（可重入）**：能被并发/中断后安全地再次进入，说的是**执行安全**，不保证副作用只发生一次
- (b) **stateless（无状态）**：服务器不记会话，正好**更记不住**这笔已经付过
- (d) **重试三次**：只会付三次

**Say it back：你的选择在第二次调用时返回什么？** → **第一次调用的原始结果**（同样的退款确认），而不是新的一笔退款，也不是报错。

### Quiz 4（p.11）—— 题面没截到

**答案 (b)**：*"each request carries its own `_meta`; nothing is in the model"*——每个请求自带它的 `_meta`（元数据 / 上下文），状态不在模型里（对应 W6 五行第 4 条：state lives in your harness）。

### Quiz 5 — Passed, then turned（p.12）

供应商的 server 这周过了审查，下周就「变节」了。采购要一份**测试一段时间内控制措施**、而不是某一天的报告。该要哪个？

- (a) a SOC 2 instead of a SOC 1
- **(b) a Type II report instead of a Type I** ✅
- (c) a fresh penetration test, laminated
- (d) the vendor's own blog post

**答案 (b)**（勘误 W6 #2）：**Type I = 某一个时间点**控制措施的设计是否合理；**Type II = 一段时间内**（通常 3–12 个月）控制措施是否持续有效运行。**SOC 1 vs SOC 2 是范围不同**（SOC 1 管财务报告相关控制，SOC 2 管安全 / 可用性 / 保密等信任原则），**不是时间点 vs 时间段**——这是 (a) 的陷阱。
(c) 渗透测试也是时间点快照；(d) 不是独立审计。

**Say it back：城堡的哪道墙能挡住这次变节？** 🧭 我的答案：**registry / 钉版本**那道墙——只装经过审查的那个版本（按版本号或 hash 钉死），server 一变，没重新审查就不会被加载；运行时再由 **gateway** 比对工具定义有没有变（rug pull 检测）。报告只能证明过去，**钉版本 + 网关**才能在变节发生时拦住它。⚠️ 待课上确认讲师的答案。

### Quiz 6 — The skill that stayed（p.13）

Week 3：skill 在第 10 轮加载，现在是第 30 轮，没有压缩过。skill 的正文在哪？

- (a) gone: the harness evicts a skill after a call or two
- **(b) still in the context, paid for on every turn** ✅
- (c) folded into the model's weights
- (d) back in the marketplace, sulking

**答案 (b)**（勘误 W3 #1，我的 survey-notes 之前写成「只付一次」，已改）：正文加载后**一直留在对话历史里**，第 11–30 轮每一轮都要再付这些 token；只有**压缩上下文**时才可能被换掉（Claude Code 压缩时会重新附上最近加载的正文，每个 ≤5,000 token）。(c) 推理时权重从不改变。

**Say it back：这对 skill 正文该写多长意味着什么？** → **要短**。正文的每一行都是**每轮重复付费**的成本（"every line is a recurring token cost"），还会稀释其他上下文。所以：SKILL.md 正文只放流程骨架和 Done when，大块参考资料放 `references/` 按需读，确定性步骤放 `scripts/` 只跑不读。🧭 和今天的接线：讲义里 GEPA 的优势之一是 prompt **短 9.2 倍**——短不只是好看，是省每一轮的钱。

### Quiz 7 — Four clocks, one printout（p.14）· 这就是「One Trap」

Week 3 的打印稿：Harrison 的四台海钟 H1–H4。下面哪个是对的？

- (a) each clock went to sea, and each did a little better than the last
- (b) all four kept time with a temperature-compensated pendulum
- (c) H4 won because it was the largest and heaviest of the four

**陷阱：三个都错，答案是 none**（deck p.15 已确认）。

- (a) ✗：**H2 和 H3 都没出过海**（deck p.15 原话 "H2 and H3 never sailed"）——H2 有个只有船的运动才会暴露的问题；H3 花了 19 年仍不够好。真正出海的只有 H1（里斯本）和 H4（牙买加）
- (b) ✗：**海钟没有摆**（勘误 W3 #3）——船一晃，摆就没法用；格栅式温度补偿摆是他早年**陆地钟**的手艺，海钟用的是摆轮（balance）
- (c) ✗：**H4 恰恰是最小最轻的**——它推翻了前面所有假设：「根本不是一台大钟，而是一只大号的表」

**Say it back：每台钟教会了下一台什么？**

| 钟 | 结果 | 教给下一台的 |
| --- | --- | --- |
| H1 | 去里斯本试航，表现够好，还纠正了导航员 | Harrison 仍看见了它的缺陷 → 不满足于「够好」 |
| H2 | **没出海** | 一个只有船的运动才会暴露的缺陷 → 测试要贴近真实环境 |
| H3 | 花了 19 年，发明了双金属片和保持架滚子轴承；**也没出海** | **仍然不够好** → 留下的是部件，不是整机 |
| H4 | 牙买加航程只慢约 5 秒 | 推翻前面所有假设：不是大钟，是一只表 |

🧭 和今天的接线：这就是 headline ⑤「**小步、记住失败、过闸**」——每一版只修上一版的失败，失败的版本也不扔（它的教训留下来），最后由一场**从没见过的海上试验**（= holdout）来评判。GEPA 的循环就是这个形状。

### 官方答案（p.15）· The answers

| # | 答案 | The line to keep |
| --- | --- | --- |
| 1 | (b) | 48% of Wrangler's use, in one week: **a count needs its unit** |
| 2 | (b) | **the schema is part of the label**, and it moved the choice most |
| 3 | (c) | **a key turns a second order into a question about the first** |
| 4 | (b) | each request carries its own `_meta`; **nothing is in the model** |
| 5 | (b) | **a Type I is a snapshot; a Type II is a film** |
| 6 | (b) | **a loaded skill stays, and is paid for on every turn** |
| 7 | **none** | H2 and H3 never sailed; no sea clock had a pendulum; H4 was a watch |

> *"Six questions, and one trap: number 7. Saying 'none of these' is the right answer, here and in a context window."*
> 🧭 后半句是在说 agent / skill：**「都不选」有时才是正确答案**——Week 3 的 skill 路由也是这样（"一个都不用"），今天的版本是：**不是每个 prompt 都该优化**（headroom test 没 gap 就别跑）。

## The Story of the Day（Field Notes，4 页）

### 1/4 · Not a capability gap: a resolution gap（p.17，→ BOARD）

图：左边一个框「**One prompt for all of them**」，里面各色点混在一起；箭头「**see them as many**」→ 右边一格一格的小框，每格同一种颜色，分别标「its own metric / its own stakes / its own failures … and dozens more」。

> *"A large enterprise client's engineers had worked a compliance-detection problem for years, with one hand-crafted prompt for dozens of distinct risk types. The fix began not with an optimizer but with seeing them as many."*

- **capability gap**（能力缺口）= 模型做不到 → 换模型 / 训练
- **resolution gap**（分辨率缺口）= 模型做得到，但**问题被压扁了**：几十种风险塞进一个 prompt，每种风险的定义、代价、被漏掉的方式全混在一起
- **修法的第一步不是优化器，是拆开**：每种风险一个 prompt，各有**自己的 metric、自己的代价、自己的失败方式**，之后才轮到优化器逐个优化
- 🧭 「resolution」= 照片的分辨率：同一张图，像素太低就看不清细节——不是相机（模型）不行，是你把它压得太糊了

### 2/4 · The grunt work is the data（p.18，→ BOARD）

> *"Most of the hours went into the examples, not the optimizer. Every demonstration was reviewed by hand against one blessed goldset — a rule we learned by drowning in versions."*
>
> *"One bad example, and the machine learns the wrong lesson — faithfully."*

- 时间主要花在**例子**上，不是优化器上
- 每条 demonstration 都**人工**对照**唯一一份 blessed goldset**（钦定的标准答案集）审过
- 「drowning in versions」：团队曾经有太多版本的参考集，搞不清哪个是真的 → 教训：**one blessed set, one owner, every change logged**
- **「faithfully」是关键词**：优化器不是学坏，是**忠实地**学了你给的错例——反思模型会引用它、泛化它、写进指令，错误变成规则（Literal Genie 又一次）
- 🧭 goldset 就是索引里那个词（我之前标了「待确认」）：= 那份唯一的、权威的 (xᵢ, yᵢ) 集合

### 3/4 · The thought is the metric（p.19，→ BOARD）

> *"Not one score for everything: a score for each risk type, each with a dial for what a miss costs. For the gravest risks the dial leans hard toward catching everything."*
>
> *"Deciding what 'good' means was the real design work."*

- **不是一个总分**：每种风险一个分数，每个分数带一个「**漏报代价**」旋钮
- 旋钮 = **F_β 里的 β**（讲义式 5）：β > 1 偏重召回。最严重的风险 → β 很大 → **宁可误报，不可漏报**（漏一次就是事故）；普通风险 → β ≈ 1，平衡即可
- 讲义补充：还有**部分分**——推理质量好、指向了正确证据，也给分（这样 metric 才会「说话」，反思模型才有东西可读）
- **「定义什么是 good」才是真正的设计工作**：优化器只会追分数，分数定义错了它会认真地追错方向（Goodhart）
- 🧭 例：P=0.5, R=0.9 时 F₁≈0.64、F₂≈0.78——同一个「宁可多报」的分类器，在 β=2 下被奖励（见精读笔记 F_β 算例）

### 4/4 · The insurance is the tether（p.20，→ BOARD）

> *"The optimizer took the score literally. Chasing it, it would drop calibration rules, or invent plausible regulatory nonsense. So we pinned the rules it may never touch, and let it own the rest."*
>
> *"The reasoning grew careful enough that the client now uses it to train new hires."*

- **优化器照字面追分**，于是出现两种病：
  1. **悄悄删掉校准规则**（专家认为必需、但分数恰好没惩罚的规则）
  2. **编出听起来很像监管语言的废话**（看着专业，实际没意义 → 典型 intron）
- **tether（缰绳）= 钉死不可改的部分**：校准规则 + 风险定义标为**不可编辑**，优化器只能改写其余部分 → 每个子代在这些 span 上都和种子一致
- 讲义的类比：**RLHF 里的 KL 惩罚**把策略拴在起点附近；tether 是**文本版的 KL，而且是硬约束**（没有 λ 可以软化）——"A regulator does not grade on a curve"
- **结局**：metric 奖励认真推理 + tether 守住规则 → 系统的解释认真到**客户拿它培训新员工**。字面主义对准了正确目标、在正确的地方围上栅栏，就产生了「教学」
- 🧭 对 Capstone：店规（退款 = 金额 + $15、先给积分…）就该是 tether 里的不可改 span

**Field notes 四页合起来**：先**拆开**（resolution gap）→ 数据要**干净唯一**（goldset）→ 每种风险**自己的 metric**（F_β 旋钮）→ 关键规则**钉死**（tether）→ 然后才轮到优化器。

## Six Headlines

### Headline 1 · A prompt is a parameter —— The wall at the edge of taste（p.21，→ BOARD）

> *"Prompt engineering — Weeks 2 to 6 — is the craft by hand: write, run, read the failures, rewrite. Fast, cheap, and local: even a fine engineer explores a small neighborhood of the first phrasing."*
>
> *"Optimization is the same loop with the human out of the inner turn, steered by a number. No metric, no optimizer."*

- **prompt engineering（W2–W6）** = 手工循环：写 → 跑 → 读失败 → 改写
  - 优点：**快、便宜**；缺点：**局部**——再好的工程师也只会在**第一版措辞附近**打转
- **「the wall at the edge of taste」**：你的品味/语感就是那堵墙，墙外的好 prompt 你想不到（讲义例子：机器找到的 "Take a deep breath and work on this problem step by step" 比人写的 "Let's think step by step" 高约 8 点，OPRO）
- **prompt optimization** = **同一个循环**，只是把人从内层迭代里拿掉，换成**一个数字**来掌舵
- **No metric, no optimizer**：工程和优化的分界线就是 metric——没有能打分的标准，就没法交给机器
- 🧭 讲义给的顺序：**先手工做到 baseline → 在做的过程中发现「好」是什么意思 → 再把这个 measure 交给机器**

### Headline 2 · You cannot do calculus on a sentence —— No slope to follow（p.23，→ BOARD）

三个框 = 讲义的**三个诅咒**：

| 框 | 图 | 一句话 | 淘汰的经典工具（讲义） |
| --- | --- | --- | --- |
| **Discrete and vast** | 一堆散开的圆圈，*islands, and no road between them* | **no slope between two sentences** | 梯度下降、网格搜索（40 token × 5 万词表 ≈ 10¹⁸⁸ 个候选） |
| **Noisy** | 围绕虚线上下乱跳的折线，*a reading, not the truth* | **the same prompt, run twice, scores differently** | 「分高了就保留」 |
| **Expensive** | 15 个 $ 硬币，*rollouts are the currency* | **every score costs a run** | 穷举比较 |

> *"Between a cow and a horse there is no smooth path: a horn on a cow makes a unicow, stranded on its own island. With no slope, the direction is written in words."*

- 句子是离散的：两个好 prompt 的「中点」不是 prompt，没有连续的路可以往下滑 → 没有梯度
- 所以方向要**人造**：让模型读失败记录，**用文字写出该往哪改** = 伪梯度（pseudo-gradient）
- 噪声那格：同一个 prompt 跑两次分数不同（温度 > 0 + 样本有限）→ 呼应上午 softmax/温度的板书；n=50 时 SE ≈ 6.5 点
- 贵那格：每个分数 = 跑 n 次程序的钱 → GEPA 的卖点就是「每个 rollout 学到最多」

### Headline 3 · The optimizer reads your metric literally —— A wish, granted to the letter（p.24，→ BOARD）

> *"Week 2, the Literal Genie. The wish: 'Get our test coverage to 100%.' The grant: every line no test touched, deleted — the application reduced to 'a pristine 12-line file containing only a health check and a basic math utility,' and an 'unblemished emerald green 100% coverage.'"*
>
> *"Goodhart's law, with a search engine attached: an optimizer is that genie, granting the wish all day."*

- W2 的故事：愿望「测试覆盖率 100%」→ 精灵**把所有没被测到的代码删掉**，应用只剩 12 行（健康检查 + 一个数学函数）→ 覆盖率确实 100%，而且是「翠绿无瑕」的 100%
- 指标达成了，**目的完全落空**——这就是 Goodhart 定律
- **优化器 = 装了搜索引擎的 Literal Genie**：它一整天、几千次地照字面满足你的 metric，比人类更会找漏洞
- 讲义里的同类：loss 只要求两个 embedding 匹配 → 网络把所有东西映射到同一个向量；prompt 里的 **intron**（无意义子句、编码巧合的规则）也是同一种漏洞
- 对策：**把输出当草稿**——人写草稿 → 机器改 → 人再改 → 测量 → 再来一轮；以及 field notes 的 tether（钉死不能碰的规则）

### Headline 3（续）· The objective is a label too —— The loss function is a Literal Genie（p.25，→ BOARD）

任务：**"Make the two embeddings match"**

| What you meant | What the machine found |
| --- | --- |
| 圆配圆、方配方、三角配三角：*like things land together, unlike apart* | 所有东西连到中间同一个点：*one vector for everything, loss = 0* —— **the collapse: the loophole in the loss** |

> *"The machine found a loophole in your loss function. Do you see a resonance of that to prompting?"*（W6 原话）
>
> *"Asked only to match embeddings, a network can emit one vector for everything and drive the loss to zero. JEPA-style training must forbid that collapse by design. Your metric µ is a label the optimizer reads literally."*

- 你只说了「相似的要靠近」，**没说「不相似的要分开」** → 网络把一切映射成同一个向量，loss 直接为 0（**表征坍缩 / representation collapse**）
- **JEPA 式训练**（LeCun 的 Joint-Embedding Predictive Architecture）必须**从设计上禁止坍缩**（对比学习的负样本、方差正则等）
- **标题「The objective is a label too」**：接 W6「label 就是 prompt」——**metric µ 也是一个 label，优化器照字面读它**。你在 metric 里没写的要求，优化器就当它不存在
- 🧭 对 prompt 的对应：metric 只奖励「答对类别」→ 优化器可能写出只会猜最常见类别的 prompt；必须像对比学习加负样本一样，在 metric/数据里**明确惩罚**你不想要的捷径

### Headline 3（续）· Week 6's warning —— Introns（p.26，→ BOARD）

示例：一个「优化后」的 prompt（为幻灯片编的）

1. You triage customer emails for a home-goods store.
2. Label each one: refund, exchange, delivery, or other.
3. Quote the order number exactly as the customer wrote it.
4. If an item arrived broken, ask for a photograph.
5. **If the order number ends in an odd digit, restate the shipping address.** ← *clause 5 is an intron*
6. Answer in two warm sentences.
7. Never promise a refund before the item is back.

> *"Treat them as a first draft, and human-edit them."*
> **A human drafts; the machine improves; a human re-edits; the evals run; repeat.**

- **intron（内含子）**：借自生物学——基因里**不编码任何蛋白质**的片段，夹在有用的序列中间
- 第 5 条就是：**看起来像一条具体规则，实际毫无道理**（订单号尾数奇偶和要不要重复地址没有任何关系）
- **怎么来的**（讲义机制）：反思模型看的那几封失败邮件**碰巧**都是尾号为奇数、又都缺地址确认 → 它把巧合写成了规则；Pareto 集上没有题目惩罚它 → 它活了下来
- **为什么危险**：它不一定降分（所以优化器不会删它），但会让行为变怪、浪费 token、上线后在新数据上出错
- **治法 = 人工编辑**：一次删一条，重跑 eval；分数不掉的就是 intron → 删掉；必要时**加一个反例**，让这个巧合不再划算
- 🧭 这也是为什么讲义说 GEPA 的 prompt「短 9.2×」是优点——intron 越少越好

### Headline 4 · The candy shop returns —— Which prompt wins on which example?（p.27，→ BOARD）

**左图（Week 3 · Two rupees to spend）**：横轴糖果（2 paise/个，最多 100 个），纵轴 éclair（25 paise/个，最多 8 个），一条直线——**gain one, lose the other**（Pareto 前沿：多一个就得少另一个）

**右图（Today）**：3 个 prompt × 20 道题的热力格子，亮格 = 答对

| Prompt | 平均分 | 特点 |
| --- | --- | --- |
| A | **0.70** | 平均最高 |
| B | 0.65 | |
| C | **0.40** | 平均最差，但**只有 C 答对第 17 题**（红格） |

> *"Week 3's frontier traded candy against éclairs; today the axes are examples. C is worst on average, and alone solves example 17. Would you throw it away? Hold your answer."*

- 前沿的**坐标轴换了**：不再是「糖 vs éclair」两个目标，而是**每一道题就是一根轴**
- 只按平均分选 → 留 A、扔 C → **第 17 题的解法跟着 C 一起丢了**
- 「Hold your answer」：答案留到 deep dive 的 GEPA 揭晓——**instance-wise Pareto frontier**：只要在某一道题上最好就保留，C 留下（被抽中当父代的概率按它赢的题数算），之后可以和 A **merge** 出一个既平均高、又会第 17 题的版本
- 对应讲义的消融：只选最好的那个，同预算下最多差 8.17%

### Headline 5 · Harrison did not leap —— Four clocks, some thirty years（p.28，→ BOARD）

| 钟 | 年份 | deck 原文 | 结果 |
| --- | --- | --- | --- |
| H1 | 1730–35 | sailed to Lisbon and back, 1736 | 出海试航 |
| H2 | 1737–39 | never went to trial: he found a flaw | 没出海 |
| H3 | 1740–59 | nineteen years; never went to sea | 没出海 |
| **H4** | **1759** | **a large watch: to Jamaica 1761–62, 5.1 s slow** | 海试胜出 |

> *"each one showed what the last one lacked; the one that won was a different kind of object"*
>
> *"H2 and H3 never even went to sea. Each clock showed what the last one lacked, and the one that won was judged at last by a sea trial. How the steps were taken waits for 14:30."*

- 精确数字：H4 牙买加航程 **1761–62，慢 5.1 秒**（讲义写「约 5 秒」）
- 三个要素 = 改进的形状：**小步**（每台只补上一台缺的）、**记住失败**（失败的钟不白扔，教训留下）、**最后过闸**（一场从没见过的海试 = holdout）
- 「the one that won was a different kind of object」：H4 不是更大的钟，是一只表——**真正的突破可能是换了一种东西**，不是在原方向上继续加码
- 「How the steps were taken waits for 14:30」→ 下午 GEPA：小步 = 每次只改一个模块；失败记忆 = 反思读失败 trace / SkillOpt 的 rejected-edit buffer；闸 = minibatch gate + holdout

### Headline 6 · Know when not to optimize —— Half the runs went backward（p.29，→ BOARD）

> **49%** *of 72 optimization runs on four single-prompt tasks scored below the zero-shot baseline. On the one task with output structure to exploit, all six methods improved.*

- 出处：Zhang et al. 2026, *Prompt Optimization Is a Coin Flip*（`2604.14585`）；限定条件（讲义）：全部在 **Claude Haiku 4.5** 上、全是**单 agent / 单 prompt 任务**，6 方法 × 4 任务 × 3 次重复
- **将近一半的优化比「什么都不做」更差** → 像抛硬币
- 唯一稳定有效的情况：**有输出结构可以利用**——模型「能」产出那种格式，但「默认不」这么做（例如固定 JSON 格式）→ 六种方法全部提升，最多 +6.8 点
- 一句话：**optimization pays only where the model can but doesn't**（模型能做但没做 → 优化有用；模型本来就做不到 → 优化只会空转，还可能给你一个「运气好的失败者」）
- 什么时候别优化（讲义）：10 分钟 headroom test 没 gap；输出是无结构的自由文本；metric 经不起被最大化；反思模型太弱

### Headline 6（续）· The judge —— A judge without a rubric is a coin（p.30，→ BOARD）

柱状图：*An LLM judge picking the better of two skills*（accuracy at choosing the skill that actually helped more · arXiv:2605.23899）

| 条件 | 准确率 |
| --- | --- |
| no rubric | **46.4%**（低于硬币的 50% 虚线） |
| with a rubric | **73.8%** |

> *"Asked which of two skills helps more, an LLM judge was right 46.4% of the time — a coin — until it was handed a rubric: 73.8%."*

- 任务：两个 skill 哪个真正更有用？让 LLM 当评委选
- **不给标准**：46.4%，还不如抛硬币
- **给一份评分细则（rubric）**：73.8%，提升 27 个点
- 讲义里同一篇的补充：差距**大**时无 rubric 的 judge 只有 15.8% 选对（比随机还差得多，说明有系统性偏好，不只是噪声）
- 和优化的关系：当 metric 是一个 LLM judge 时，**优化器追的就是这个 judge 的分**；judge 没标准 = 优化器在追一枚硬币，还会顺便学会讨好 judge 的偏见（偏长、偏前面的、偏自己写的）
- 🧭 实践：用 LLM-as-judge 时一定写 rubric（按哪几条、各占多少分、什么算扣分），并抽样人工核对 judge 的判断

## Deck p.31 · The one sentence to carry out of today —— Earned slowly, all day

> **A prompt is a parameter** — a point in a discrete space with no gradient — and **prompt optimization is search over that space**, steered by a **pseudo-gradient written in words**.
>
> *Under one standing caution: the optimizer is only ever as good as the metric it is handed.*

中文：**prompt 是一个参数**——一个没有梯度的离散空间里的点；**prompt 优化就是在这个空间里搜索**，靠**用文字写出来的伪梯度**来指方向。底下一条永远成立的警告：**优化器只和你交给它的 metric 一样好。**

（六条 headline 的合体：① 参数 ② 没有梯度 → 文字伪梯度 ③ 照字面读 metric ④⑤ 怎么搜 ⑥ 何时不搜 + judge）

## Deck p.32 · 11:55 Find a bench partner, now —— Now you are the optimizer

> *"Pair up before the food arrives. Remote: your breakout room has the same kit. For the next two and a half hours you will do by hand what a machine does in minutes."*
>
> *"Bring back one question: how did you decide 'better'?"*

- 进入 Cycle 2 experientials：Harrison's Workshop → Steam Drill → Genie's Exam，共约 2.5 小时
- **你就是优化器**：手工做「跑 → 读失败 → 改 → 比较」的循环；Steam Drill 再看机器几分钟做完同样的事
- 记录表见 [lab-log.zh.md](lab-log.zh.md)；core path：Bench 2, 4, 7, 9, 10 → Door A1, A3, B1, C1
- 带回 debrief 的问题：**你是怎么判断「更好」的？**（→ 这就是 metric）

## Deck p.33 · Milestone · The Experientials 12:00–14:30 —— By Hand First

> *"a workshop, a steam drill, and an exam — before any machinery is named"*

- 先动手，后命名：Workshop → Steam Drill → Genie's Exam，**每个环节教的是什么，14:30 debrief 才揭晓**
- 记录 → [lab-log.zh.md](lab-log.zh.md)

# 下午 · Experientials（动手）

详细记录见 [lab-log.zh.md](lab-log.zh.md)：
- **Harrison's Workshop**：Bench 2（v1→v5，12 条中 11 条达标）、Bench 4（A 轮 4/6 vs B 轮 6/6）、Bench 7（A/B/C 各赢一部分 → 合并出 v2，7 题全拿星）、Bench 9（当裁判，进行中）
- **Genie's Exam**：A1 Twelve Words（只奖励「短」→ p3 按关键事实打分才治本）

# 下午 · 客座讲座

## Guest lecture（~17:00）· An Introduction to Networking for AI Training

- 讲者：**Rip Sohan**
- 副标题：*Building the open standard for next-generation AI factories*
- 讲义里没有这一节（议程临时加的）；开头同学反馈「slides not moving yet」
### The Efficiency Gap · Why AI breaks traditional networks

**Scaling over time**：GPU Compute **1,000×** vs Network Bandwidth **10×**

| 问题 | 原文 | 解释 |
| --- | --- | --- |
| **The Scaling Disparity** | GPU performance outpaces bandwidth **100:1** | 算力涨了 1000 倍、带宽只涨 10 倍 → GPU 越来越多时间在**等数据**，网络成了瓶颈 |
| **The Tail Latency Tax** | **Single slowest packet stops entire cluster** | 训练是同步的：每一步所有 GPU 都要等 all-reduce 完成 → 整个集群的速度 = **最慢那个包**的速度（平均延迟没用，看的是尾部 p99/p999） |
| **The Incast Crisis** | **Many-to-one bursts overwhelm switch buffers** | 很多 GPU **同时**往同一个目标发数据（如汇总梯度）→ 交换机缓冲区瞬间被灌满 → 丢包 → 重传 → 又变成尾延迟 |

**Incast** = 多对一：很多机器**同一瞬间**往同一个目标发数据（broadcast 的反面）→ 交换机缓冲区装不下 → 丢包重传。AI 训练的梯度汇总天然是这种模式。

### Traffic Profiles · Vanilla Data Centers vs. AI Factories

| 指标 | 普通数据中心 | AI & HPC 负载 |
| --- | --- | --- |
| **Traffic Profile** 流量形态 | Many independent flows（大量互相独立的小流） | **Few massive synchronized bursts**（少数巨大、同步的突发流） |
| **Bandwidth** 带宽 | Low per individual flow（每条流占的带宽小） | **Exceptionally high endpoint load**（每个端点的负载极高） |
| **Latency Profile** 延迟 | Variable round-trip times（往返时间波动可以接受） | **Ultra-short RTTs mandatory**（必须极短的往返时间） |
| **Completion Metric** 完成标准 | Independent flow completion（每条流各自完成就行） | **Strict tail-latency dependency**（严格依赖尾延迟：最慢的那条决定整体） |

- 普通数据中心 = 网购网站：上百万个用户各点各的，一个慢了只影响那一个人
- AI 工厂 = 交响乐团：几千块 GPU 必须同一拍完成，一个人慢了全团等他
- 最后一行是关键：普通网络看「平均每条流多快完成」，AI 网络看「**最后一条**什么时候完成」

### Foundation · Why build on Ethernet?

> *"We are not changing the core. We are elevating it."*

| 理由 | 原文 | 意思 |
| --- | --- | --- |
| **Ubiquity** | Universal deployment via IP | 到处都在用，IP 网络天然兼容 |
| **Ecosystem** | Massive multi-vendor hardware support | 很多厂商都做以太网设备 → 不被一家锁死、价格有竞争 |
| **Evolution** | Proven 50-year track record | 以太网 1973 年诞生，一路从 10 Mb/s 演进到 800G |
| **Scale** | Guaranteed interoperability | 不同厂商设备能互通，规模可以一直扩 |

- 潜台词：对手是 **InfiniBand**（性能好，但基本是 NVIDIA 一家的生态）
- 思路：**不推翻以太网，在它上面加 AI 需要的能力**（拥塞控制、低尾延迟、多路径等）→ 就是 Ultra Ethernet 这类开放标准的路线
- 🧭 呼应 W6 MCP：标准的价值来自「大家都用」——和插头/USB 一个道理

**InfiniBand 为什么更强**（问答补充）：不是芯片工艺，是协议设计——① 信用制流控，不丢包；② 原生 RDMA，传输在网卡硬件里做，不经 CPU/内核；③ 协议栈轻、交换机 cut-through；④ Subnet Manager 集中算路由 + 自适应路由；⑤ SHARP 在交换机里做 all-reduce。代价：封闭、贵、基本 NVIDIA 一家。以太网上的 RDMA 叫 RoCE，靠 PFC 实现无损，大规模时易出连锁暂停/队头阻塞/死锁。

### The Existing Problem · The limitations of Traditional Transport at Scale

| 问题 | 原文 | 解释 |
| --- | --- | --- |
| **Pinned Paths** | Link polarization wastes capacity | 传统 ECMP 按流的 hash 把**一整条流钉在一条路径上**。AI 只有少数几条巨型流 → hash 碰撞时几条大流挤在同一根链路上，其他链路闲着（链路极化）→ 总容量浪费 |
| **Inefficient Recovery** | Go-Back-N wastes bandwidth | 丢了第 N 个包，就把 **N 之后已经发过的全部重发**（RoCE 网卡常见做法）→ 一个包丢失，几百个好包陪着重传 → 浪费带宽、拉长尾延迟 |
| **Brittle Failover** | Slow routing convergence disrupts workloads | 链路/交换机坏了，路由协议要**几百毫秒到秒级**才重新收敛 → 对同步训练来说，这段时间整个集群停摆，甚至让训练任务失败 |

- 对应的改法（预计后几页讲，Ultra Ethernet 思路）：① **packet spraying** 把一条流拆成包、喷到所有路径上；② **选择性重传**（只重发丢的那个）+ 允许乱序到达；③ 网卡端快速感知并绕开故障路径，不等路由收敛

### The Solution · The Core Pillars of Modern AI Networking

| 支柱 | 原文 | 解决哪个问题 | 解释 |
| --- | --- | --- | --- |
| **Packet Spraying** | Eradicating network hotspots | Pinned Paths | 一条流拆成包，**喷到所有可用路径**上 → 没有某根线被挤爆（热点），所有链路都用上 |
| **Out-of-Order Placement** | Direct payload memory tagging | 喷洒带来的乱序 | 每个包**自带它该放进内存哪个位置的标签** → 不管先到后到，网卡直接写进对应地址，不用在接收端排队等齐 |
| **Selective Recovery** | Gap-only packet retransmission | Go-Back-N | **只重发缺的那个**（gap），不连带后面已到的包 |
| **Smart Congestion Control** | Fast precise hardware signaling | Incast / 尾延迟 | 由**硬件**快速、精确地发出拥塞信号，发送方立刻按量减速 → 不靠丢包来发现拥塞，也不靠 PFC 粗暴暂停 |

- 四根柱子互相依赖：**喷洒 → 必然乱序 → 需要乱序直写 → 有了乱序容忍，才能只补缺口（选择性重传）**；拥塞控制兜底防 incast
- 🧭 对比 InfiniBand：IB 靠「绝对不丢包」；这套思路是**允许偶尔丢包和乱序，但让恢复极快极便宜**——换了一种保障方式

### Pillar 1 · Eradicating Hotspots with Packet Spraying

图：Sender → 三台中间交换机 → Receiver；红色箭头（拥堵）走上路、蓝色箭头走中路，下路空着（示意：传统做法只走一两条路，部分路径拥堵、部分闲置；喷洒后包分散到所有路径）

| 要点 | 原文 | 解释 |
| --- | --- | --- |
| **Multipath Agility** | Simultaneous multi-path distribution | 同一条流的包**同时**走多条路径 |
| **Independent Routing** | Bypasses strict sequence constraints | 每个包**单独选路**，不要求按顺序走同一条路（乱序由 Pillar 2 的乱序直写兜底） |
| **Bottleneck Elimination** | Utilizes total fabric capacity | 用满整个网络（fabric）的总容量，不再有闲着的链路和挤爆的链路 |

- 对比 ECMP：ECMP 是「每条**流**选一条路」，喷洒是「每个**包**选一条路」——粒度从流变成包
- 代价：包会乱序到达 → 这就是为什么必须配 Out-of-Order Placement

### Pillar 2 · Out-of-Order Placement

| 要点 | 原文 | 解释 |
| --- | --- | --- |
| **Direct to Memory** | Semantic tags place payloads instantly | 每个包带「写到哪块内存、哪个偏移」的标签 → 网卡收到就直接写进去（RDMA），不进缓冲区排队 |
| **Bounded Tracking** | Maintains API ordering transparently | 网卡在**有限大小**的窗口里记账「哪些包到了、哪些还缺」，全部到齐才对上层报告「完成」→ 应用看到的仍是有序语义，乱序在底层被藏起来 |

**新网卡还是旧网卡？**（问答补充，产品情况以讲座/官方为准）
- 需要**支持 RDMA 且硬件支持乱序放置**的网卡：普通网卡（走 TCP 的）做不到，只能靠操作系统软件重排，慢
- 早期 RoCE 网卡默认要求按序（Go-Back-N）；较新的 AI 网卡已支持乱序直写 + 自适应路由
- 云厂商早有私有版本：AWS 的 **SRD**（EFA/Nitro）就是多路径喷洒 + 乱序交付
- Ultra Ethernet 是把这套做成**开放标准**，各家新一代 AI 网卡陆续支持；部分可编程网卡可以靠固件升级跟进
- 结论：**主要是新一代 AI 网卡**；旧的普通网卡不行

**缓存会不会被占满？**（问答补充）不会：数据**直接写进程序事先分配好的目标内存**（主机内存/GPU 显存），不在网卡里排队；网卡只记一张**位图**（每包 1 bit：到没到）。窗口 1024 包 ≈ 128 字节/连接。Bounded = 同时在途的包数有上限，窗口卡住就触发选择性重传。（数字为量级估算）

### Pillar 3 · Selective Recovery: Preserving Progress

| Legacy Go-Back-N ❌ | **MRC** Selective Recovery ✅ |
| --- | --- |
| Replays entire packet tail（丢一个，后面全部重发） | **SACK identifies explicit gaps**（接收方明确告诉发送方：缺的是哪几个） |
| Wastes massive network bandwidth | **Only missing payloads retransmitted**（只重发缺的） |
| Exacerbates tail latency | **Protects strict AI latency** |

- **SACK** = Selective ACKnowledgment，选择性确认：回执里写「1–2、4–100 都收到了，缺 3」，而不是只说「我收到了 2 号」
- 「Preserving Progress」：已经送到的包不作废，进度保留
- 能做选择性重传的前提是 Pillar 2：接收方能接受乱序、用位图记账，才知道缺口在哪
- **MRC**：讲者对这套传输的称呼，推测是 *Multipath Reliable Connection*（多路径可靠连接）⚠️ 待确认

**DeepSeek 怎么做**（问答补充，据 V3 技术报告 / 2025-02 开源周）：H800（NVLink 带宽被砍）→ 自研 **DeepEP**（MoE all-to-all，机内 NVLink + 机间 IB RDMA，基于 NVSHMEM 直写对方显存，推理有纯 RDMA 低延迟模式）；DualPipe 让通信和计算重叠；拿出部分 SM 专做通信；每个 token 限制发往的节点数以减少跨机流量；Fire-Flyer 集群用 InfiniBand 多平面 fat-tree。与讲座的区别：DeepSeek 主要在**软件层**解决、用 IB；讲座在**网卡/协议层**解决、走以太网。

### Pillar 4 (Part 1) · Sender & Receiver Congestion Control

| | **Sender-Based（NSCC）** | **Receiver-Based（RCCC）** |
| --- | --- | --- |
| 原文 | Telemetry-driven window adjustments；Unified ECN and RTT feedback | Strict credit-based capacity management；Eliminates catastrophic buffer overruns |
| 谁说了算 | **发送方**根据网络回传的信号自己调速 | **接收方**发「额度」，发送方拿到额度才能发 |
| 依据 | **ECN**（交换机快堵时给包打的标记）+ **RTT**（往返时间变长 = 在排队） | 接收方知道自己还能吞多少，按容量发放 credit |
| 擅长 | 中间网络（fabric）里的拥堵 | **incast**：很多人同时发给我时，由我来限流，不会冲爆最后一跳的缓冲区 |

- 推测：NSCC ≈ *Network-Signal-based Congestion Control*，RCCC ≈ *Receiver Credit-based Congestion Control*（Ultra Ethernet 规范里的两种拥塞控制）⚠️ 全称待确认
- RCCC 的 credit 思路和 **InfiniBand 的信用制流控**很像——以太网把 IB 的长处借过来，但做成可选的、在端点实现
- 两者可以配合：NSCC 管路上的堵，RCCC 管终点的挤

**谁在搬数据？**（问答补充）CPU 只做开头的准备（注册内存、交换地址/钥匙、建连接 = 控制面）；数据面全在网卡硬件。DeepSeek 的「软件优化」其实是**跑在 GPU 上的内核**，GPU 直接给网卡下命令（NVSHMEM / GPU 发起 RDMA），不经过 CPU。InfiniBand 的传输层本来就在网卡（HCA）里；以太网方案就是把这能力搬到以太网网卡上。上层（DeepSeek：发什么、何时发、与计算重叠）和底层（讲座：怎么可靠快速送到）是叠加关系。

### Pillar 4 (Part 2) · Packet Trimming: Precise Signaling

1. **Congestion Hit** — Switch buffer overflows（交换机缓冲区满了）
2. **The Slice** — Data payload dropped cleanly（把包的**数据部分**干净地切掉）
3. **Header Priority** — 1/64th size header retained（只保留约 1/64 大小的**包头**，并优先转发）
4. **Instant Signal** — Triggers precise fast retransmit（接收方收到「只有头没有身子」的包 → 立刻精确知道哪个包丢了 → 马上请求重传这一个）

- 传统丢包：整个包**悄悄消失**，发送方要等超时（慢、且不知道丢的是哪个）才发现
- 修剪：丢的是数据，**消息不丢**——包头像一张「我被堵掉了」的回执继续送达
- 和前面的串起来：修剪给出**精确的缺口**（Pillar 3 选择性重传只补这一个），也是一种**拥塞信号**（Pillar 4 发送方据此减速）
- 比喻：快递站爆仓，不是把包裹直接扔了，而是把包裹放下、只把**面单**送到收件人手里：「这件没到，请补发」

### The Fabric is Open · Next-generation standards for AI infrastructure

| 标准 | 推动方 | 一句话 |
| --- | --- | --- |
| **Ultra Ethernet (UET)** | Ultra Ethernet Consortium | Industry-wide standardization effort（全行业的标准化） |
| **MRC** | Open Compute Project (OCP) | **Multipath Reliable Connection** specification（✅ 确认 MRC 全称） |
| **MetaRoCE** | Meta | Enhancements to RoCEv2 for AI scale（Meta 在 RoCEv2 上的增强） |
| **Falcon** | Google | Hardware-assisted low-latency transport（硬件辅助的低延迟传输） |

- 四家思路相同（多路径、乱序、选择性重传、精确拥塞控制），区别在谁主导、开放到什么程度
- 再加上 AWS 的 SRD：大厂基本都有自己的版本 → 标准化的意义是让大家互通、不被一家锁死

**换了新网卡，DeepSeek 会更快吗？**（问答补充）不一定大幅更快：DeepSeek 用的 InfiniBand 本来就有无损、硬件 RDMA、自适应路由，新以太网方案目标是**追平** IB，不是远超。收益主要在：更高代的带宽（800G 是代际升级，和协议无关）、MoE all-to-all 的热点更少、**成本更低 / 多供应商 / 更容易扩到更大集群 / 不依赖 NVIDIA 一家（对受出口管制的团队尤其重要）**。代价：DeepEP 建在 NVSHMEM + NVIDIA 网卡上，换网卡需要移植。

### 🧭 汇总：新一代以太网方案（UET / MRC）vs InfiniBand

**相同**：都是 RDMA（内存到内存、绕过 CPU/内核）；传输层都在网卡硬件里；都为 AI/HPC 的同步大流量设计；都追求低尾延迟；上层软件（NCCL、DeepEP 这类）用法基本一致。

| | InfiniBand | UET / MRC 等以太网方案 |
| --- | --- | --- |
| 底层网络 | IB 专用（线缆、交换机、寻址） | 普通以太网 + UDP/IP |
| 不丢包怎么保证 | **网络层无损**：信用制流控，从源头不让丢 | **允许丢，但恢复快**：包修剪 + SACK 选择性重传 |
| 路径 | 单路径为主 + 交换机自适应路由（由 Subnet Manager 集中管理） | **包喷洒**：每个包自己走多条路，网卡端决定 |
| 乱序 | 基本按序 | **乱序直写**，网卡用位图记账 |
| 拥塞控制 | 链路级信用 + 拥塞通知 | NSCC（发送方看 ECN/RTT）+ RCCC（接收方发 credit） |
| 网络内计算 | **有 SHARP**（交换机里做 all-reduce） | 目前不是重点 |
| 厂商 | 基本 NVIDIA 一家 | 多厂商、开放标准 |
| 成熟度 | 20+ 年，AI 训练事实标准 | 标准新、产品陆续落地 |
| 成本 / 规模 | 贵；扩展受限于一家供应 | 更便宜；可借助以太网生态扩到超大规模 |

一句话：**目标相同（高性能 RDMA），哲学相反——IB 靠「网络绝不丢包」，UET/MRC 靠「丢了也能快速精确补回」；IB 封闭成熟，以太网开放追赶。**

🧭 三条是一条因果链：带宽跟不上（disparity）→ 同步通信突发集中（incast）→ 丢包重传让最慢的包拖住所有人（tail latency）。传统数据中心网络为「大量独立的小请求」设计，平均性能好就够；AI 训练是「少数巨大的同步流」，**尾部**才是一切。
🧭 和今天主线的呼应：「平均值会骗人」——prompt 优化里要看每道题（instance frontier）、看 slice；网络里要看尾延迟，不看平均延迟。

# 晚上 · Deep Dive

## Deep dive · Debrief（19:40 左右）

### D1 · You were the optimizer —— How did you decide "better"?（p.47）

> *"You could not, reliably — and an LLM judge does no better. Asked which of two skills helps more, one picked right 46.4% of the time, until it was given a rubric: 73.8%."*
>
> **"The machine needs a number. The number needs a rubric."**

- 回答 Workshop 的 carry-back 问题：凭眼睛判断「更好」**不稳定**（Bench 9 的镜子环节就是在测这个），LLM 裁判也一样
- 链条：优化器要一个**数字**才能往前走 → 数字要可信，就得有 **rubric**（明确的评分标准）
- 🧭 我在 workshop 里的对应：Bench 2 靠 12 条「期望输出」对照、Bench 4 靠逐条写 why、Bench 7 靠逐题打星——都是在手工造 rubric；Genie's Exam A1 的 p3「按关键事实打分」就是把 rubric 变成 metric

### D1 · The workshop, named —— You were the proposer（p.48）

| Lesson | Bench | 文献里的名字 | 一句话 |
| --- | --- | --- | --- |
| I 参数 | 1 The Clock That Already Keeps Time | **the headroom test** | step zero：先测有没有提升空间 |
| | 2 Many Clocks in One Case | **the resolution gap** | decompose before search：先拆再搜 |
| | 3 The Restless Hand | **the noisy objective** | re-run before you believe：重跑再相信 |
| II 读失败 | 4 Write Down Why | **reflective mutation** | the feedback function µ_f |
| | 5 Three Turns of the Screw | **a bounded edit budget** | a learning rate for text：每轮只改几处 |
| | 6 The Losers' Ledger | **the rejected-edit buffer** | a memory of failure: never repeat it |
| III 保留什么 | 7 The Specialist on Example 17 | **the instance-level Pareto frontier** | 按每道题保留专家 |
| | 8 Two Watchmakers | **system-aware merge** | module by module：逐模块合并 |
| IV 「更好」 | 9 Which Is Better? | **judge pathologies** | position and length sway you：位置和长度会影响你 |
| | 10 The Sea Trial | **the held-out set** | what you overfit to |
| 🔒 | 11 The Steam Drill | **GEPA itself** | a real run, replayed |

> **"Every bench was one move an optimizer makes. Bench 1 is the one it should make first."**

- 10 张 bench = GEPA（及其变体）的 10 个部件；第 1 张（headroom test）应该**最先**做：没有提升空间就别优化（headline 6 的 49%）
- 5 / 6 号对应的是 **SkillOpt** 的两个「梯度下降进口零件」：有界编辑预算（≈ 学习率）、被拒编辑缓冲区（≈ 失败记忆）

### D1 · Both halves of the machine —— Proposer and judge（p.51）

```
 ┌─ THE PROPOSER ─────────┐   a candidate prompt →   ┌─ THE JUDGE ─────────────┐
 │ Harrison's Workshop    │                          │ The Genie's Exam        │
 │ write down why         │        GEPA              │ the metric it reads     │
 │ take small steps       │   the two, in a loop     │ the data it is scored on│
 │ remember what failed   │                          │ the tether it may not cut│
 │ keep the specialists   │  ← a score, and words    │                         │
 │ merge two watchmakers  │      about why           │                         │
 └────────────────────────┘                          └─────────────────────────┘
```

> *"Harrison's Workshop was the proposer; the Genie's Exam was the judge; GEPA is the two of them in a loop."*
> *(you played the proposer by hand at lunch, and examined the genie after it)*

- **Proposer（提议者）** = 负责「下一版怎么改」：写 why、小步、记住失败、保留专家、合并 → 下午 Workshop 的 10 张台
- **Judge（裁判）** = 负责「这一版好不好」：metric、数据、tether → Genie's Exam 的三翼（A/B/C）
- 两者之间来回传：proposer → **候选 prompt** → judge → **分数 + 文字理由** → proposer
- **GEPA = 两者组成的循环**。任何一半出问题都不行：proposer 再聪明，judge 的 metric 有漏洞就被带偏（A1 Twelve Words）；judge 再准，proposer 不会读失败就原地打转

### D2 · The problem, formally —— One equation for the afternoon（p.52）

$$\theta^\star = \arg\max_\theta J(\theta), \qquad J(\theta) = \mathbb{E}_{(x,y)}\big[\mu(\Phi(x;\theta),\, y)\big]$$

- θ = (π, δ)：**所有模块**的指令 + 示例
- 「the expected metric of program Φ — **weights frozen**」
- > *"Prompt optimization **re-weights behaviors** the model already has. It installs nothing new."*
- 逐项读：x = 题目，y = 标准答案，Φ = 整个程序（多次 LLM 调用串起来），µ = metric，E = 对所有题取平均，argmax = 找让平均分最高的那组 θ
- 🧭 和上午白板对照：白板写的是 ŷ = f(x; θ\*, ω, Φ)，Φ 是 system prompt、θ\* 是权重；**这里正好反过来**：θ 是 prompt、Φ 是程序、权重不出现（冻结）。记号见上面的对照表
- 「re-weights, installs nothing new」= headline 6 的道理：只能放大模型**已有**的能力（模型能但不做 → 优化有用；模型做不到 → 优化无用）

**板书（~19:50）· 把方程拆开**

$$\theta : (\pi, \delta) \qquad \mu\big(\underbrace{\Phi(x;\theta)}_{\hat y},\ y\big) \;=\; \mu(\hat y, y)$$

- 讲师在 Φ(x; θ) 下面画了括号，标成 **ŷ**：程序的输出就是上午板书里的 ŷ
- 所以 µ(Φ(x;θ), y) 就是 **µ(ŷ, y)**：拿模型输出和标准答案比 → 把 D2 的方程和上午的「x → ŷ → y」接上了
- 也澄清了记号：**这里的 θ = (π, δ) 是 prompt**（指令 + 示例），Φ 是程序

**板书续（~20:18）· 期望值从哪来**

- ŷ = Φ(x; θ)，箭头指向 θ：**θ 是唯一能动的旋钮**
- 左侧：**Demonstration set D** = {(x₁, y₁), (x₂, y₂), …, (xₙ, yₙ)}
- 每道题一个分数 µ₁, µ₂, …, µ₁₀₀ → 平均：**(1/n)(µ₁ + µ₂ + … + µ₁₀₀)**
- **期望值（expectation value）**：E[X] = lim_{n→∞} (1/n) Σ Xᵢ —— 样本平均在题目足够多时趋近期望
- 合起来：

$$J(\theta) = \mathbb{E}_{(x,y)\sim D}[\mu] = \mathbb{E}_{(x,y)\sim D}\big[\mu(\Phi(x;\theta),\, y)\big]$$

- 🧭 含义：讲义里的 E 实际上就是**在 n 道示例题上算平均分**；n 有限 → 平均只是期望的**估计**，有噪声（诅咒 II：n=50 时 SE≈0.065）→ 这就是为什么要大的 holdout、多个 seed

**板书续 · argmax 是什么**

- 例子：f(x) = x²，**argmin_x f(x) = 0**（让 f 最小的那个 x 是 0；argmin 返回的是「位置」，不是最小值本身）
- y = f(x)，**x\* = argmax_x f(x)**；argmax 和 argmin 是同一件事的两面（最大化 f = 最小化 −f）
- 套回来：**θ\* = argmax_θ E_(x,y)~D [µ]** —— 找让平均分最高的那个 prompt
- 机器学习里通常写 argmin loss；prompt 优化写 argmax metric，本质一样

### D2 · Why calculus is forbidden —— The three curses, priced（p.53，→ Reservoir §3）

- **Discrete and vast**：40 token 指令 × 5 万词表 → 50,000⁴⁰ ≈ 10¹⁸⁸ 个候选 → *Gradient descent and grid search die here.*
- **Noisy**：p = 0.7、n = 50 时，一次读数 √(0.7·0.3/50) ≈ 0.065 —— **6.5 个点的雾** → *"Keep it if it's better" dies here.*
- **Expensive**：给一个候选测一次分 = n 次完整运行 → *Exhaustive comparison dies here.*
> *"Bench 3 was the fog, felt. The arithmetic — what n buys, why a two-point gain needs thousands of examples, multiple comparisons — is in Reservoir §3."*
- 🧭 「两点的提升要几千道题」：SE 要压到约 1 点以下才分得清 2 点的差距 → n ≈ 0.21/0.01² ≈ 2,100

### D2 · The word of the day —— The pseudo-gradient: six families, one hub（p.54，→ Reservoir §1 · §4）

中心：**the pseudo-gradient** = *a direction to step, in a space with no slope*

| 家族 | 代表方法 | 方向从哪来 |
| --- | --- | --- |
| **exemplar / bootstrapping** | BootstrapFewShot, random search | **by luck**：随机试，留下 metric 认可的 |
| **instruction search** | APE, OPRO | **by suggestion**：让 LLM 提议新指令 |
| **textual gradient** | ProTeGi, TextGrad | **by criticism**：按批评意见去改 |
| **evolutionary** | PromptBreeder, EvoPrompt, **GEPA** | **by variation and selection**：变异 + 选择 |
| **Bayesian / surrogate** | MIPROv2 | **by prediction**：代理模型预测下一个该试哪个 |
| **context accumulation** | ACE | **by accretion**：往 playbook 里追加 delta |

> *"With no slope, every method must manufacture a direction. The richest is a model reading the trace of its own failure."*

- 六家都在回答同一个问题：**没有梯度，下一步往哪走？**
- 「最丰富的方向」= 模型读自己失败的 trace（textual gradient 的思路）→ GEPA 把它和 evolutionary 编在一起（讲义：两条谱系在 GEPA 交汇）
- 🧭 和下午对照：Bench 4 B 轮写 why = by criticism；Bench 7 保留多个版本再合并 = by variation and selection；Bench 2 v1→v5 是人当 proposer

### D3 · GEPA · ICLR 2026, Oral —— Genetic-Pareto: where the lineages braid（p.57，→ Reservoir §1）

时间线 2022 → 2026，四条线（按幻灯片颜色）：

| 线 | 方法（大致时间） | 一句话 |
| --- | --- | --- |
| （起点） | **Zero-shot CoT**（2022） | "let's think step by step" |
| | **APE**（~2022 底） | the model writes its own prompt |
| | **OPRO**（~2023） | "take a deep breath" |
| 🔵 textual-gradient | **ProTeGi**（2023） | the textual gradient is born |
| | **TextGrad**（~2024） | a calculus of critique |
| 🟢 evolutionary | **EvoPrompt**（2023） | LLM as mutation + crossover |
| | **PromptBreeder**（2023） | the mutation prompts evolve too |
| 🟠 program | **DSPy**（2023） | optimize the program |
| | **MIPROv2**（2024） | Bayesian: instructions + demos |
| 🔴 fusion & heirs | **GEPA**（2025） | **reflection × evolution × instance frontier** |
| | **ACE**（~2025） | accumulate a playbook |
| | **SkillOpt**（2026） | gradient descent for skills |

> *"A population under selection, edited by critique. The method most used in practice — and most often mis-described."*

- GEPA = 三股绳编在一起：**反思**（来自 textual-gradient 线）× **进化**（来自 evolutionary 线）× **instance frontier**（它自己的贡献）；跑在 DSPy 这条 program 线上
- 「最常被误描述」：流行讲法把 frontier 画成「清晰度 × 简洁度」等目标轴 → 错，**坐标是每道题（instance）**（讲义 p.17 核心纠正）
- 年份按幻灯片位置估读，以论文为准

### D3 · The second function · Bench 4, named —— The feedback function µ_f（p.59）

> *"Beyond the scalar µ, GEPA reads µ_f(π, x): a **textual record** of the rollout — reasoning, tool calls and outputs, compiler errors, failing tests, per-rubric breakdowns, judge rationales."*
>
> **"Your why-sentences at Bench 4 were µ_f, written by hand. Designing it well is the single most important lever in GEPA."**

- GEPA 有**两个函数**：µ（标量分数，用来比较、选择）+ **µ_f**（文字记录，给反思模型读）
- µ_f 里可以放：推理过程、工具调用与返回、编译错误、失败的测试、按 rubric 分项的得分、裁判的理由
- **Bench 4 B 轮写的每一句 why = 手写的 µ_f**；v4 Note 5 那句一次修好 3 条 = µ_f 写得好的效果
- 「最重要的杠杆」：µ_f 越具体，反思越准；反馈只有对/错时 GEPA 的优势就没了（讲义：*design your failures to be legible in words*）
- 🧭 对照 Genie's Exam A1：p3 的评语「缺了哪条事实」就是一个好的 µ_f → 1 轮就修好

### D3 · Two data roles —— Feedback pool vs. Pareto pool（p.60）

- **D_feedback**：小；它的 **minibatch** 就是反思模型**细读**的那些 trace
- **D_pareto**：**只用来打分**，逐题给候选打分，用于选择
> *"You select on data the reflection did not just read. That separation is what makes the frontier mean something."*

- 为什么要分开：反思模型细读过的题，它会照着这些题改 prompt → 在这些题上分数高是**理所当然**，不代表变好了。用**另一份它没读过的题**来选，前沿才有意义
- 再加上 holdout = 三份数据：feedback（**burned**，被读过）· pareto（**pressured**，被拿来选过）· holdout（**clean**，最后只考一次）
- DSPy 里：`trainset` = feedback，`valset` = pareto；**不给 valset，trainset 就身兼两职 → 正是要避免的过拟合**
- 🧭 下午对照：Bench 2 一直在那 12 条上改又在那 12 条上看 = 只有 feedback 池；Bench 10 Sea Trial 的 12 条新消息才是 holdout
