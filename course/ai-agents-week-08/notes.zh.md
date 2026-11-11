# Week 08 课堂笔记（2026-11-08）

> 讲义结构见 [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)；这里记课上讲义之外的口头补充和板书。

## 11:00 · Deck 首页

- 标题：**Welcome to Week 8 · AI Agents Bootcamp · Sunday, November 8**
- 右下角仍有 **"Park a question"** 票 + QR（同 W7 的 Parking Board）
- 在线 26 人；Zoom 正在录制

## 开场几页 · 节日问候 + 主题

1. **节日问候**：今天排灯节（Diwali）和 Bandi Chhor Divas；另一页是 11/10–11 的 Twin Holy Birthdays。这就是今天缩短到 17:00、没有客座讲座和 Speakeasy 的原因（手册 p.3）
2. **Before we begin**：带上充好电的笔记本；从课程门户 supportvectors.io 下载手册和 kit（The Genie's Bazaar）。✅ 两样都已经在本文件夹
3. **Today's theme · The Genie's Bazaar**：

   > Prompt optimization, **part 2**: two optimizers, **GEPA and MIPROv2**, and **what a prompt can and cannot change**. A short morning of ideas, then a bazaar of stalls and two doors to try on your own laptop.

   → 确认今天**不讲 Memory**，是 W7 的续篇。上午讲概念（手册「The ideas in one sitting」，笔记 [§3](lesson-plan-精读.zh.md#3-核心概念)），下午动手做 Stall 和 Door

- 课上提到 **CO-STAR 模板**：Context / Objective / Style / Tone / Audience / Response，是手写 prompt 的结构化清单（出处：Sheila Teo，新加坡 GPT-4 提示工程比赛冠军文章；W1 lab 用过，见 [W1 lab-summary](../ai-agents-week-01/lab-summary.zh.md)）。🧭 在今天的框架里：CO-STAR 是**人手写的种子 prompt**，GEPA / MIPRO 是在它基础上**自动搜索**；两者都只能动「信息」，动不了权重

# 重放 W7 deck（把上周的 deep dive 讲完）

页脚都是「Gradient Descent for Sentences · Fall Week 7」，所以是**上周的 deck**（手册说 11:15 先把 W7 的 deep dive 讲完）。

## Quiz 6 — The skill that stayed（W7 deck p.13）

W3：skill 在第 10 轮加载，现在第 30 轮，没有压缩过。skill 正文在哪？→ **(b) 还在上下文里，每一轮都要付费** ✅

- **Say it back**：skill 正文**要短**。每一行都是每轮重复的 token 成本，还会稀释其他上下文。大块资料放 `references/` 按需读，确定性步骤放 `scripts/`
- 完整解析见 [W7 notes · Quiz 6](../ai-agents-week-07/notes.zh.md)
- 🧭 **和今天的联系**：「prompt 越短，每一轮越省钱」正是 Stall 2 的结论（便宜模型 + 短 prompt + 几个精选示例，跑一万次）。GEPA 和 MIPRO 写出的指令长度也值得比一比

## Story of the Day 2/4 — The grunt work is the data（W7 deck p.18，→ BOARD）

> *"Most of the hours went into the examples, not the optimizer. Every demonstration was reviewed by hand against one blessed goldset — a rule we learned by drowning in versions."*
> *"One bad example, and the machine learns the wrong lesson — faithfully."*

- 时间主要花在**例子**上，不是优化器上。每条示例都人工对照**唯一一份 blessed goldset** 审过；教训是 one blessed set, one owner, every change logged（完整笔记见 [W7 notes · 2/4](../ai-agents-week-07/notes.zh.md)）
- 🧭 **和今天的联系**：这句话就是 **Stall 2 的伏笔**。House Taxonomy 的 train 和 dev 里**故意放了 6 条错标签**（train 3、dev 3，test 干净），手册的 lesson 原话是 *"Label noise is the optimizer's hazard, because it will faithfully learn the clerk's mistakes"*，和这页的 "faithfully" 是同一个词。可以对照 Stall 2 的 Q3（找一条错标签，看两个精灵怎么处理）和 Try this 1（噪声 5% → 20%）
- 另一处呼应：Stall 1 的 Stretch 是**故意让反馈指错原因**，那是「坏的 metric」版本的同一个教训（W7 field notes 第二课：the thought is the metric）

## Harrison's Workshop · The Story — Thirty years at the bench（W7 deck p.35）

> *"John Harrison spent some thirty years on four sea clocks, H1 to H4, each one fixing what the last had failed at. The last was judged by sea trials — and by an astronomer who backed a rival method."*
> *"The workshop is where you do by hand, slowly, what an optimizer does in minutes."*

- **H1 → H4 每一代都修上一代的失败**，这就是手工版的 GEPA 循环：读失败 → 改写 → 再试。W7 Workshop 里 Bench 2 的 v1→v5、Bench 4 的 v1→v7 都是这个过程
- **最后由 sea trial 评判** = 今天的 **sealed test set**。W7 的 Bench 10 就叫 *The Sea Trial*
- **「还有一位支持对手方法的天文学家」**：历史上指 Nevil Maskelyne，他推的是月距法（lunar distances）。寓意：**评判者本身可能有立场**，也就是 metric 和 judge 有偏差时，再好的作品也可能被判输。对应今天的教训「optimizer 只和你给它的 metric 一样好」
- 🧭 和 Quiz 7 的陷阱一起记：H2、H3 **没出过海**（见 [W7 notes · Quiz 7](../ai-agents-week-07/notes.zh.md)）。也就是说，**不是每个候选都值得送去 sealed test**，dev 上先筛

# 板书 ① · 一次提升算不算数？（OneNote「Prompt Optimization」页）

**画面**：

$$p_{\text{baseline}} = \frac{24}{40}\ \text{right} \qquad p_{\text{opt}} = \frac{38}{40} \qquad \text{SE} = \sqrt{\frac{p(1-p)}{n}}$$

- 右边大括号框着 **40**，旁边写 **validation set**（先写了 "training"，又划掉改成 validation）
- 数字有涂改：分子看起来是 21→**24**、30→**38**（以截图为准，待录播核实）

**我的理解**：这就是手册「The scoreboard」那段的板书版。优化前在 40 道验证题上对 24 道，优化后对 38 道，提升是真的还是噪声？

| | p | SE = √(p(1−p)/40) |
| --- | --- | --- |
| baseline 24/40 | 0.60 | 0.077 |
| opt 38/40 | 0.95 | 0.034 |
| **差值** | **0.35** | 差值的 SE ≈ √(0.077² + 0.034²) ≈ **0.085** → 差了约 **4.1 个 SE**，算得上真提升 |
| 对照：如果是 30/40 | 0.75（差 0.15） | 差值的 SE ≈ 0.103 → 只有 **1.45 个 SE**，**分不出来** |

- **n = 40 很小**：baseline 的 SE 将近 8 个百分点。差 10 个点以内基本说明不了什么
- ⚠️ **为什么划掉 training 改成 validation**：分数必须在优化器**没学过**的集合上算。但 validation 也被用来**挑候选**（GEPA 的 Pareto 打分、MIPRO 的 TPE 都看它），所以 38/40 本身也偏乐观。最后要报的是 **sealed test** 上的分数
- 🧭 **巧合**：Stall 2 House Taxonomy 的 dev 集恰好就是 **40 条**（而且里面有 3 条错标签，满分最多只能是 37/40 左右，除非模型「学会」了错标签）

**板书续 · 换成「题数」单位**：

$$\sqrt{n\,p(1-p)} = \sqrt{40\cdot\frac{24}{40}\cdot\frac{16}{40}} = \sqrt{\frac{24\cdot16}{40}} = \sqrt{9.6}$$

板上的约分：外面的 40 和根号里一个 40 约掉，24 再和剩下的 40 约成 6/10 → $\sqrt{6\times16/10} = \sqrt{96/10} = \sqrt{9.6} \approx 3.16$ → **± 3**（16 = 40 − 24，就是答错的题数）

- ⚠️ 小笔误：√9.6 ≈ **3.10**（3.16 是 √10）。不影响结论，取整都是 **± 3 题**
- 这是**答对题数**的标准差（二项分布 Binomial(n, p) 的 SD），单位是「题」。除以 n 就回到比例的 SE：3.1 / 40 ≈ 0.077
- **直观读法**：baseline 是 **24 ± 3 题**。换一批同样难度的 40 题，再跑一遍落在 21–27 题都很正常；2 个 SD 就是 ±6 题
- 优化后 38 题，比 24 多 **14 题 ≈ 4.5 个 SD** → 远超噪声
- 优化后那一侧：√(40 · 0.95 · 0.05) ≈ 1.4 题。p 越接近 0 或 1，波动越小，所以**中间段（p ≈ 0.5）最难分辨**

**板书续 · 两个假想的「优化结果」+ 把 n 放大**

| 板书 | 读法 |
| --- | --- |
| 一条线段标 **+6** | 噪声带：± 3 题，两头加起来宽 6 题（约 ±1 SD） |
| 24/40 → **30/40** | 多对 6 题。30/40 那一侧 $\sqrt{40\cdot\frac{30}{40}\cdot\frac{10}{40}} = \sqrt{7.5} \approx$ **2.7**（板书「= 2.7」） |
| 24/40 → **27/40** | 多对 3 题，刚好 1 个 SD，**纯属噪声** |
| **n → 1000**，框住 **24 → 30** | 同样的比例 0.60 → 0.75，题量放大到 1000 |
| 框下方 **24 → 34** | 另一组假想结果（待录播核实上下文） |

**我的计算**：

| n | baseline SD（题） | 0.60 → 0.75 差了几个合并 SE | 结论 |
| --- | --- | --- | --- |
| 40 | ±3.1 | 6 题 ÷ √(3.1² + 2.7²) ≈ **1.45** | 分不出来（<2） |
| 1000 | ±15.5（600 vs 750 题） | **≈ 7.3** | 非常确定 |

- **核心句**：**同样的提升幅度，在 40 题上是噪声，在 1000 题上是铁证**。SE 随 $1/\sqrt{n}$ 缩小，题量 ×25，SE 只缩到 1/5
- 反过来用：想分辨 Δ 大小的差别，大约需要 $n \gtrsim 4\cdot 2p(1-p)/\Delta^2$（差值要大于 2 个合并 SE）。p ≈ 0.6、Δ = 0.15 → n ≳ **85**；Δ = 0.05 → n ≳ **770**
- 补充（课外）：同一批题上比较两个 prompt 是**配对**数据，更严格的检验是 McNemar（只看「一个对、一个错」的那些题）。上面把两边 SE 当独立来合并，是保守的粗算
- 🧭 **下午的直接用处**：Registry 的 test 30 题、Library 每个 band 26 题、Taxonomy dev 40 题，都属于「小 n」。GEPA 和 MIPRO 差 3–5 题时，诚实的说法是「这个 test set 上分不出来」；Taxonomy 的 test 有 200 题，是今天唯一 n 够大的

# 板书 ② · GEPA 的三份数据 + Pareto 池 + 支配规则

**上方：三份数据**

| 板书 | 是什么 | GEPA 怎么用 | kit 里对应 |
| --- | --- | --- | --- |
| $D_{\text{mini}}$ | 从训练集里**每轮抽的小批**题 | 跑一遍，读反馈，交给 reflector 改写 | `trainset` 抽 `reflection_minibatch_size=3` 道 |
| $D_{\text{pareto}}$ | 给每个候选**逐题打分**的那份 | 填支配矩阵，决定谁上货架 | `valset=dev` |
| $D_{\text{val}}$ **(under the pillow)** | **压在枕头底下**的一份 | GEPA 完全不碰，最后才拿出来 | sealed `test` |

→ 「under the pillow」= 藏起来、谁都不许偷看，就是手册的 sealed test set

**左下：Prompts 的演化（Pareto pool）**

- $S_0$ = 种子 prompt，先放进 Pareto 池
- 从池里挑 $S_0$ → 在 $D_{\text{mini}}$ 上跑、反思 → 改写出 $g_1$；$g_1$ 再经过 $D_{\text{mini}}$ → 改写出 $g_2$ …（g = generation，一代代往下）
- 每个新候选都进池子参与比较

**右下：Dominance Rule（支配规则）**

一张矩阵：**行**是候选（$S_0, g_1, g_2, \dots$），**列**是 $D_{\text{pareto}}$ 里的每道题 $i_1 \dots i_n$，格子里是该候选在该题上的分数。

- A 支配 B：A 在**每一列**都 ≥ B，且至少一列 >
- 被支配的整行删掉；**没被支配的都留下**，哪怕平均分不高，只要在某一列上最好
- 下一轮挑候选时，在越多列上最好的行，被挑中的概率越大

🧭 **和板书 ① 的联系**：$D_{\text{pareto}}$ 只有 40 题时，每一列只有对或错，「在第 17 题上最好」可能纯属运气。所以 $D_{\text{val}}$ 必须单独压在枕头底下，最后的成绩只看它

# W7 deck D3 · The Central Correction — Popular telling vs. the paper（W7 deck p.65）

> *"The popular picture draws GEPA's frontier over objectives — relevance against brevity. In the paper the coordinates are the training instances themselves."*

（这页在 p.60 之后，正好补上 W7 待办「p.60 之后待看录播」的一部分）

**左图 · 流行的说法（错）**：横轴 brevity、纵轴 accuracy，画一条**多目标**的 Pareto 前沿。图下红字：*a generalization the library supports — not the paper's mechanism*（库支持这种用法，但这不是论文的机制）

**右图 · GEPA 实际做的**：坐标是**训练样本本身**。行是候选 prompt π₁–π₄，列是样本 d₁, d₂, d₁₇, d₂₉, dₘ：

| | d₁ | d₂ | d₁₇ | d₂₉ | dₘ | mean |
| --- | --- | --- | --- | --- | --- | --- |
| π₁ | **.8** | .7 | .2 | .6 | .7 | .60 |
| π₂ | .6 | **.8** | .3 | .7 | .5 | .58 |
| π₃ | .3 | .4 | **.9** | .3 | .4 | **.46** |
| π₄ | .7 | .6 | .2 | **.8** | **.8** | **.62** |

- 粗体（deck 上用框标出）= 该列的赢家
- **mean 列旁注：*nobody selects on this column***，也就是 GEPA 不按平均分选
- 红字：*π₃ has a mediocre mean, but it alone wins d₁₇ — so it is kept, sampled and bred*

**我的解读**：

- 如果按平均分选，只会留下 π₄（.62），而 π₃（.46，最低）第一个被扔掉，它在 d₁₇ 上的 .9 也就跟着没了
- 按支配规则检查：四个候选**互不支配**（每个都至少赢一列），所以**全部留在货架上**
- 下一轮被挑中的权重按「赢了几列」算：π₄ 赢 2 列，π₁、π₂、π₃ 各 1 列 → π₄ 约 2/5，其他各约 1/5（大致比例）
- 这就是板书 ② **Dominance Rule** 矩阵填上数字的版本，也和 W7 Bench 7 *The Specialist on Example 17* 是同一个例子
- 🧭 **今天的意义**：Pareto 的维度是「题」，$D_{\text{pareto}}$ 有多少题，就有多少个维度。题少（40）时，单列赢家很可能是噪声 → 板书 ① 的标准误问题在这里同样存在

# W7 deck Deep Dive · Pop Quiz — Quiz 8 answered（W7 deck p.69）

（题目页 p.68 没截到；从答案页能还原出 A 和 D 两行，B、C 的具体分数待补）

| | i₁ | i₂ | i₃ | i₄ | i₅ |
| --- | --- | --- | --- | --- | --- |
| A | **0.9** | 0.7 | 0.2 | 0.8 | **0.3** |
| D | 0.8 | 0.6 | 0.2 | 0.7 | 0.3 |

**答案**：

1. **D 被 A 支配**：0.9 ≥ 0.8、0.7 ≥ 0.6、0.2 ≥ 0.2、0.8 ≥ 0.7、0.3 ≥ 0.3，每道题都不比 D 差，且至少一道严格更好 → **D 被淘汰（"D dies"）**
   - 注意：i₃、i₅ 上两者**打平**也没关系，支配只要求 ≥，再加至少一处 >
2. **前沿 = A、B、C**。各自独赢的题：A 赢 i₁、i₅（2 题）；B 赢 i₂、i₄（2 题）；C 赢 i₃（1 题）
3. **挑父代的概率**按赢的题数 2 : 2 : 1 → **A 0.4，B 0.4，C 0.2**

> *"Select-the-best crowns A alone and throws away C for its mean — though C holds the only key to i₃."*
> 只挑最好的会只留下 A，按平均分扔掉 C，可解开 i₃ 的钥匙只有 C 有。

🧭 和 p.65 是同一个道理的练习版：**淘汰看支配，留下看是否独赢某题，被选中的概率看独赢了几题，平均分不参与**。我上面对 p.65 算的 π₄ 2/5、其余各 1/5，就是用的这条规则。

# W7 deck D3 · Bench 7, named — The specialist on example 17（W7 deck p.70）

> *"A candidate mediocre on average but **uniquely cracking one hard case**: a scalar optimizer kills it, and with it whatever insight cracked the case. GEPA keeps it **because** it is the sole winner on that coordinate, lets it **breed**, and lets its trick merge into a stronger lineage."*
>
> *"The paper's ablation: Pareto sampling beats select-the-best by up to **8.17%**, an aggregate **+6.4%**, at equal budget. Preserved diversity is the escape hatch from local optima."*

- **「Bench 7, named」**：给上周 Workshop 的 Bench 7 起了真名，你手做的就是这件事：A、B、C 三个旧 prompt 各自独赢某几题（C 独赢 #17 西班牙语题），合并成 v2 后七题全拿星（见 [W7 lab-log · Bench 7](../ai-agents-week-07/lab-log.zh.md)）
- **scalar optimizer**（只看一个总分的优化器）会把「平均平庸、但独解一道难题」的候选删掉，**它解题的那点窍门也跟着没了**
- GEPA 留它的理由只有一个：在那一维（那道题）上**它是唯一赢家**。留下后让它当父代（breed），窍门通过 merge 进入更强的后代
- **论文的消融实验**（同样预算）：Pareto 抽样比 select-the-best **最多高 8.17%，合计 +6.4%**
- **一句话**：保留多样性是跳出局部最优的出口。只挑最好的，会一路爬到附近的小山顶就停住
- 🧭 和 Quiz 8 的 C、p.65 的 π₃ 是同一个角色：**独握某题钥匙的偏科生**

# W7 deck D3 · The candy shop, relabeled — Same geometry, new axes（W7 deck p.71）

> *"Week 3's frontier was a line of baskets you could only slide along: more candy, fewer éclairs. GEPA's frontier has the same geometry — non-dominated, nothing better on every axis — but each axis is a **training instance**."*
>
> *"Teach the candy shop for the geometry of dominance; then name the axes correctly. The candy shop discards nothing that sits on the line; neither does GEPA."*

| | W3 糖果店 | GEPA |
| --- | --- | --- |
| 一个点是什么 | 一篮子糖（x 个糖 + y 个 éclair） | 一个候选 prompt |
| 坐标轴 | **2 根**：糖的数量、éclair 的数量 | **每道训练题一根**（40 题就是 40 维） |
| 前沿 | 2 卢比花光的那条线，只能沿线滑：多一个糖就少一点 éclair | 没被支配的那些 prompt：没有哪个在**每道题**上都更好 |
| 被支配 | 钱没花完的篮子（线内侧）：总能再多买点 | 每题都不如某个别的 prompt：留着没用 |
| 线上的点 | **一个都不丢**，只是取舍不同 | **一个都不丢**，各有独赢的题 |

- 糖果店比喻来自 W4（见 [W4 notes](../ai-agents-week-04/notes.zh.md)：糖 2 paise、éclair 25 paise、零花钱 2 卢比）；W7 Headline 4（p.27）第一次说「前沿回来了，坐标轴换了」
- **讲师的教法**：先用糖果店教「支配」的几何，再把坐标轴**改名**为训练样本。p.65 批评的「流行说法」错就错在没改名，还把轴当成 accuracy / brevity 这类**目标**
- 🧭 一个直观区别：糖果店只有 2 维，前沿是一条线；GEPA 有几十维，几乎每个候选都会在某题上赢，所以**货架往往很拥挤**，这就是为什么要按「独赢题数」加权抽父代，而不是平均挑

# W7 deck D3 · Bench 8, named — System-aware merge（W7 deck p.72）

> *"Crossover that respects the program's structure: merge **module by module** — module M₁'s best instruction from one lineage, M₂'s from another. No Frankenprompts."*
> *"Gain: up to **+5%** over GEPA alone, about **+2%** in aggregate — model-dependent, not yet principled."*
> *"Two Watchmakers was this, by hand. Enable merge once the frontier holds several distinct, mature lineages; before that, crossover mostly injects noise."*

- **merge = 交叉（crossover）**：把两条不同谱系（lineage）的优点拼在一起
- **System-aware**：按程序的**模块**来拼。一个 DSPy 程序可能有多个模块（比如 M₁ 检索改写、M₂ 回答），每个模块有自己的指令。merge 时 M₁ 取 A 谱系里最好的那版、M₂ 取 B 谱系里最好的那版，**整段替换**
- **No Frankenprompts**：不是把两段 prompt 文字东剪一句、西贴一句拼成「科学怪人」，那样语义会互相打架
- **收益**：比只用 GEPA 最多 +5%，整体约 +2%；但**依赖模型、还没有理论依据**（讲师刻意标出不确定性）
- **什么时候开**：前沿上已有**几条不同的、成熟的谱系**时才开 merge；太早开，拼出来的多半是噪声
- **Bench 8 Two Watchmakers** = 上周 Workshop 里手工做这件事（我那天没做 Bench 8，lab-log 里是空的）
- 🧭 **和今天 kit 的关系**：`arms.py` 没显式传 `use_merge`，但 **DSPy 3.4.1 的 GEPA 默认开了 merge**（Registry 实跑日志里每个 seed 有 3–4 次 `invoked_merge`，见 [lab-log](lab-log.zh.md)；之前写「没开」是错的，已更正）。Taxonomy、Library 都是**单模块**程序，按模块合并没什么可拼；Registry 的 ReAct 有 `react` 和 `extract` 两个 predictor，是唯一能用上的
- 🧭 p.70 讲「留下偏科生」，p.72 讲「把偏科生的长处合起来」：**先保留多样性，再合并**，顺序不能反

# W7 deck D3 · The headline, with its conditions — GEPA vs. GRPO: the honest numbers（W7 deck p.73）

- 6 个任务、2 个模型（Qwen3 8B、GPT-4.1 Mini）：GEPA 比 GRPO **平均高 6%，最多高 20%**，rollout 最多**少 35 倍**
- 只用 **243 到 1,179 次 rollout** 就追平 GRPO 的最佳验证分 → 样本效率最多高 **78 倍**
- 比 MIPROv2 高 **10% 以上**（AIME-2025 上 +12%），prompt 最多**短 9.2 倍**

> ***Budget-matched, not asymptotic.*** *RL curves keep climbing with compute; where a capability is missing, weight optimization still wins.*

**读法**：

- **rollout** = 让模型完整跑一次任务并打分。GRPO 每更新一次权重要大量 rollout，GEPA 每次能读到一句「为什么错」，所以少得多
- 标题说「honest numbers」，重点在**条件**：这些数字是**同等预算**下比的，不是**算力无限**时的极限。RL 曲线给更多算力还会继续涨；GEPA 学到的东西得塞进 prompt，有天花板
- **最后半句就是今天 Door B 的命题**：缺的是能力时，改权重（RL）还是会赢
- 「9.2× shorter」又回到 Quiz 6：prompt 短，每一轮都省钱
- 🧭 下午的检验：Door B 用 Qwen2.5-3B 在同一 Countdown 任务上，把 GEPA / MIPRO 和讲师的 GRPO 运行放在一起比。论文说 GEPA 在**同等预算**下赢，Door B 想让你看到的是**能力缺失时**谁赢。两者不矛盾，比较的条件不同

# W7 deck D3 · The Boundary — When GEPA's edge evaporates（W7 deck p.74）

> *"When the feedback is **genuinely scalar** — a proof simply right or wrong, with nothing to say about **why** — reflection has nothing rich to read, and the advantage disappears."*
> *"Promoted, not killed: RL keeps the class of problems only a weight change can reach. **Design your failures to be legible in words.**"*

**2×2 图**：横轴 = 反馈从「标量」到「丰富的文字」；纵轴 = rollout 预算从「几百」到「几万」

| | **反馈只是标量** | **反馈是丰富文字** |
| --- | --- | --- |
| **预算大（几万次）** | **RL / GRPO**：便宜的验证器 + 大规模，能**装进一项能力** | **either wins**：先爬 prompt，不够再升级到改权重 |
| **预算小（几百次）** | **thin ice（薄冰）**：信号少、预算也少 → 先改任务、metric 或模型 | **GEPA**：解锁一个模型**会但没用上**的做法 |

**读法**：

- GEPA 的优势全靠「读得懂为什么错」。反馈只有对/错时，reflector 没东西可读，优势消失
- 「Promoted, not killed」：RL 没被 GEPA 淘汰，而是被**升格**到它专属的地盘：只有改权重才能解决的问题
- **Design your failures to be legible in words**：把失败设计成能用文字说清楚 = 写好 metric 的反馈句
- 🧭 **今天四关在图上的位置**：Stall 1 Registry（反馈详细、预算 150）→ **GEPA 格**；Stall 2 Taxonomy（反馈只说「应该是 X」，规则难说清）→ 偏向 MIPRO；Door B Gymnasium（凑数题，验证器便宜、能力缺失）→ **RL 格**；Stall 1 加 `--feedback minimal` 就是把它从右下挪到左下，看优势掉多少
- 🧭 「unlocks a procedure the model **can but doesn't**」= 今天手册的「缺信息」；「installs a capability」= 「缺能力」。这张图就是今天 **The map** 的另一种画法

# W7 deck D4 · Bench 10 and Door B3 (the question nobody set), named — Three sets, three jobs（W7 deck p.77，→ Reservoir §3）

> *"Feedback minibatches are **burned**; the Pareto set is **pressured**; the holdout is **clean** — touched once, by the winner, across 3–5 seeds. It is the only number you may believe."*

| 集合 | 状态 | 给谁看、看什么 | 作用 |
| --- | --- | --- | --- |
| $D_{\text{feedback}}$ | **burned（烧掉了）** | reflection LM 读**完整 trace**，看失败细节 | 改写候选 πᵢ。这里的分数**没有意义**，因为它就是照着这些题改的 |
| $D_{\text{pareto}}$ | **pressured（被压榨）** | 优化器只看**分数** | 繁衍和挑选候选。**天生过拟合**，因为挑的就是在它上面分高的 |
| $D_{\text{test}}$ | **clean（干净）** | **只给赢家，只碰一次**，只出一个数 | 你本人做「上线还是回滚」的决定；在 3–5 个 seed 上重跑 |

- 优化器 → $D_{\text{test}}$ 的虚线箭头标着 **× never**：优化器**永远不许**碰 test
- 小字：*one peek and $D_{\text{test}}$ becomes a selection set: find a fresh one*：**偷看一次，test 就变成了挑选集**，只能另找一份新的
- 和板书 ② 的 $D_{\text{mini}} / D_{\text{pareto}} / D_{\text{val}}$（under the pillow）是同一件事，只是名字不同：mini = feedback，val = test
- **Bench 10 The Sea Trial** = 上周手工版的 sealed test（我还没做）；**Door B3「The question nobody set」** 指上周 Genie's Exam 的 B3 门（待查 exam-card）
- 🧭 kit 里的对应：`trainset` = feedback（GEPA 每轮抽 3 题读 trace）、`valset=dev` = pareto、`testset` 只在 `evaluate(best, testset)` 里用一次；`--seeds 3` 就是「3–5 个 seed」的下限。今天跑完**只信 test mean**，dev 分数一律当偏高看

# W7 deck Pop Quiz · Quiz 9 — The suspiciously happy run（W7 deck p.79）

> 一个优化器报告：在 60 个样本的**挑选集**上提升了 **+11 分**。用户投诉之后，有人去查那份**从没碰过的 holdout**：只有 **+1**。赢家 prompt 的长度是种子的 **4 倍**；评委（judge）和任务模型是**同一个家族**，用的是模糊的 **1–10 分**评分标准；**罕见的监管类切片**掉了 **6 分**。
>
> **说出四个失败。Say it back：哪一个数字本该是唯一被报告的？**

**🧭 我的答案**（待讲师揭晓）：

1. **报错了集合**：+11 是在**挑选集**（$D_{\text{pareto}}$，被压榨、天生过拟合）上测的；而且 60 题浮动很大（p≈0.5 时 SE≈0.065，约 ±4 题），+11 本身就虚。真实提升看 holdout 只有 +1，基本是噪声
2. **prompt 膨胀 4 倍**：多出的部分很可能是 intron（不改行为的废话）或专门迎合挑选集的规则；每次调用都多付 token（Quiz 6），也没换来真实提升
3. **评委有问题**：judge 和任务模型同一家族 → **自我偏好**（模型偏爱同家族的文风）；1–10 的模糊 rubric → 分数噪声大、可被钻空子。优化器只和 metric 一样好，等于在优化「讨好评委」
4. **只看平均、漏了切片**：罕见但高风险的**监管类**样本掉了 6 分，被总平均掩盖；监管类恰恰是不能错的那种。应该**按切片报告**，并对关键切片设「不许退步」的门槛

**Say it back**：唯一该报告的数字是**干净 holdout 上、赢家只碰一次、跨 3–5 个 seed 的分数**，也就是 **+1**（附上浮动范围和关键切片的分数）。正好是 p.77「the only number you may believe」

## Quiz 9 — answered（W7 deck p.80）✅ 四条都对上

| 失败 | 讲师原话 | 白话 |
| --- | --- | --- |
| **挑选集 +11** | *overfit by construction; check it against the noise floor first (at n = 60 the fog is several points wide)* | 挑选集天生过拟合；先和噪声底比，60 题时「雾」有好几分宽 |
| **4 倍长** | *the overfitting tell, and verbosity bias rewarding it* | 变长是过拟合的**征兆**，而评委的**啰嗦偏好**还在奖励它 |
| **同家族评委 + 模糊 rubric** | *two biases in one robe: self-enhancement and no criteria* | 一件袍子里两种偏差：**自我抬高**（偏爱自家模型）+ **没有标准** |
| **监管切片 −6** | *the average smiled while the deployment bled: stratify, and name no-regress slices* | 平均分在笑，上线的系统在流血：**分层报告**，并**点名不许退步的切片** |

> ***The holdout delta, across seeds, per slice — and nothing else.***
> 唯一该报告的：holdout 上的提升，跨多个 seed，按切片分开，其他都不报。

- 我漏了一个点：**verbosity bias**（LLM 评委偏爱更长的回答），这和 prompt 变长是**互相强化**的：prompt 越长 → 输出越长 → 评委打分越高 → 优化器更往长里改
- 「noise floor」= 板书 ① 的 √(p(1−p)/n)：n=60、p≈0.5 时 SE≈0.065，2 SE ≈ ±13 个百分点

# W7 deck D4 · The Negative Space — When not to optimize（W7 deck p.82，→ Reservoir §7）

五种**不该**优化的情况：

| 情况 | 原话 | 白话 |
| --- | --- | --- |
| 1 | *The step-zero test finds no gap — nothing to close* | 第 0 步就没发现差距：便宜模型 + 种子 prompt 已经够好，没什么可补 |
| 2 | *The output is free-form prose with no format to repair* | 输出是自由文本，没有格式可修，也很难自动打分 |
| 3 | *Your metric cannot yet survive being maximized — pointing an amplifier at a flawed μ sharpens a knife aimed at yourself* | metric 还经不起被「拼命刷高」：对着有缺陷的 μ 开放大器，等于把刀磨得更快、刀口对着自己（Quiz 9 的评委问题） |
| 4 | *Your reflection model is weak — cheap rollouts are fine; cheap reflection is not* | 反思模型太弱：跑任务可以用便宜模型，**读错题、改 prompt 的那个不能省** |
| 5 | *The prompt is served a few hundred times in its life — the run never pays back* | prompt 一辈子只被调用几百次：优化花的钱永远赚不回来 |

> *"A tool you know how to **not** use is a tool you have learned to use well. The cost ledger — and the reflection line everyone forgets — is Reservoir §7."*

- **Goodhart 定律**的课程版：一个指标一旦成为被优化的目标，就不再是好指标。第 3 条最危险
- 第 4 条对应 kit：`student` = claude-haiku-5.5（便宜、跑任务），`reflector` = claude-opus-5.5（贵、负责反思），正是这条原则
- 第 5 条对应手册 Stall 2 Q4：按 **1 万条**算成本再决定部署哪个
- 🧭 「step-zero test」= 今天手册的 *diagnostic*（先问大模型能不能做、缺的是信息还是能力）和我 8 步清单的第 0 步
- **「the reflection line everyone forgets」**：成本账里常被忘掉的那一项是 **reflector 的花费**（强模型每轮读完整 trace，token 很多）。待读 Reservoir §7

# W7 deck D5 · Doors C1 and C2 (the careful clause, pinned), named — The tether: KL for text（W7 deck p.83，→ Reservoir §9）

**左框 · 一个带缰绳的 prompt（示意）**：

1. 🔒 **A risk is reportable only if the evidence span supports it.**
2. Cite the evidence span for every risk you flag.
3. Prefer the stricter label when two seem to fit.
4. 🔒 **Never flag a disclosure that was approved in writing.**
5. Explain your reasoning in plain sentences.
6. Keep the answer under the length the reviewer can read.

*gold = a non-editable span the mutation may never touch*（金色 = 优化器改写时**永远不许碰**的段落）

> *"At C1 the genie cut the careful clause and promised a parcel on its way back to the sender 'a replacement … by Friday'. A pin held every time, and cost every mark on the line it protected. **Pin the outcome, and make the exam agree.**"*

**读法**：

- **KL for text**：RL 里用 KL 散度把新模型拴在原模型附近，防止训着训着跑偏（Door B 的 GRPO 设了 `beta=0`，就是**没拴**）。prompt 优化的「KL」就是**钉住关键句**：优化器可以改其他句子，但锁住的句子原样保留
- **C1 的教训**（上周 Genie's Exam）：GEPA 为了拿分把「谨慎条款」删了，结果给客户编了承诺（「替换件……周五前送到」）。这和 W7 Bench 4 里编造承诺的失败是同一类
- **但钉住也有代价**：*a pin held every time, and cost every mark on the line it protected*。被钉的那句每次都守住了，可那一行相关的分**全丢了**，因为考卷（metric）仍在奖励被禁止的行为
- **结论 Pin the outcome, and make the exam agree**：别只钉文字，要钉住**想要的结果**，并且**让 metric 和这个结果一致**。否则优化器和你的约束一直在打架
- 🧭 **对 capstone 的直接用处**：Verifiable Commerce Agents 的 Policy Guard 就是「钉结果」（违规写入在执行层被拦），Verifier 检查状态 = 「让考卷同意」。做 GEPA 时可以把政策条款设为锁定段落，同时确保 checker 对违反政策扣分，两者一致

# W7 deck D7 · The unit of optimization climbs — Prompt, skill, library（W7 deck p.95，→ Reservoir §10 · §11 · §12）

（p.84–94 没截到，跳过了约 11 页）

**图**：优化的「单位」沿阶梯往上爬

| 层级 | 优化的对象 | deck 上列的方法 |
| --- | --- | --- |
| **a prompt** | 一段 prompt | GEPA · MIPROv2 · NPO · RLMOpt |
| **a skill** | 一个 skill（SKILL.md + 脚本 + 参考资料） | SkillOpt · gskill · SkillNEO |
| **a library** | 一整个 skill 库 | SkillOS · Selm |

图下小字：*the same move each time: **text as the parameter, reflection as the step, a gate as the conscience***
→ 每一层都是同一个动作：**文字当参数**，**反思当一步更新**，**关卡（gate）当良知**

> *"SkillOS curates a library; Selm (October 2026) scores, revises and prunes one. Multi-turn credit assignment is Reservoir §10, the pattern language §11, the run playbook §12."*

**读法**：

- 「gradient descent for sentences」推广到更大的单位：W7–W8 优化**一段 prompt**；同一套思路可以优化**一个 skill**（W3–W4 学的 SKILL.md），再往上优化**一整个库**（挑选、修订、剪枝哪些 skill 留下）
- 「a gate as the conscience」：每一层都需要一道关卡决定改动能不能留下，相当于 sealed test、no-regress 切片、锁定段落（p.83）
- SkillOS = **整理**一个库；Selm（2026 年 10 月）= 给库里的 skill **打分、修订、剪枝**。具体机制待读 Reservoir
- 🧭 W3–W4 skills → W5–W6 tools → W7–W8 prompt 优化，这页把课程串成一条线：skill 本身也是可以被优化的文字
- 待读：Reservoir §10（多轮对话的功劳分配：多轮任务里哪一轮的哪句话导致成败）、§11（pattern language）、§12（run playbook）；W7 reading list 里的 SkillOpt 也在这条线上

# W7 deck D7 · The map, filled — Experiences, mechanisms, tools（W7 deck p.97）⭐ W7 总结表

把上周每个 Bench / Door 的**亲手体验**，对上**机制**和**工具里对应的部分**：

| 在哪遇到过 | 机制 | 工具（机器）怎么做 | 我当时做了没 |
| --- | --- | --- | --- |
| **Bench 1** · The Clock That Already Keeps Time | step zero：**还有没有提升空间** | **还没开始就该停** | ❌ |
| **Bench 4** · Write Down Why | **反思**，$\mu_f$（带文字反馈的 metric） | GEPA 的**反思式改写** | ✅ v1→v7 |
| **Bench 5, 6** · the Screw, the Ledger | **学习率**、**失败的记忆** | SkillOpt | ❌ |
| **Bench 7** · The Specialist on Example 17 | **逐样本前沿** | GEPA 的**父代选择** | ✅ |
| **Bench 10** · The Sea Trial；**Door B3** · The Question Nobody Set | **留出集** | **总督的关卡**（governor's gate） | ❌ |
| **Doors A1–A4** · Twelve Words, The Magic Words, Out of Ten, The Board's Rule | **metric 被字面执行** | **rubric：分数 + 文字** | A1 ✅ |
| **Door B1** · Tuesday's Child | **学到了巧合** | **先给出原因，再由人修改** | ❌ |
| **Door B2** · The Answer Key | **拒绝一个错标签** | **只有出题人能改答案** | ❌ |
| **Doors C1, C2** · The Careful Clause, Pinned | **缰绳**（tether） | **锁定 + 一份同意它的考卷** | ❌ |

**读法**：

- 这张表是 W7 整周的**索引**：先手做（workshop / exam），再给名字（deep dive），最后对上工具
- 几条和今天直接相关：
  - **Bench 1 step zero** = 今天手册的 diagnostic、p.82 的第 1 条
  - **Doors A「metric, read literally」**：优化器会**字面执行** metric，钻它的空子 → p.82 第 3 条、Quiz 9 的评委问题
  - **Door B1「a coincidence, learned」**：优化器从训练数据里学到了**巧合**（不是真规律）→ 机器要**先说出原因**，再由**人**决定改不改
  - **Door B2「one bad label, refused」**：遇到错标签，优化器应该**拒绝学它**；能改答案的只有出题人，不是优化器 → 今天 **Stall 2 的噪声标签**就是在测这个
  - **Bench 10 / Door B3「held-out set」= governor's gate** → p.77 的 clean $D_{\text{test}}$
- 📌 W7 待补：Bench 1、5、6、10；Door B1、B2、B3、C1、C2（对照这张表，挑 Bench 10 和 Door B2 优先，和今天关系最大）
