# RLVE 论文精读笔记

> **RLVE: Scaling Up Reinforcement Learning for Language Models with Adaptive Verifiable Environments**
> Zhiyuan Zeng\*, Hamish Ivison\*, Yiping Wang\*, Lifan Yuan\*, Shuyue Stella Li, Zhuorui Ye, Siting Li, Jacqueline He, Runlong Zhou, Tong Chen, Chenyang Zhao, Yulia Tsvetkov, Simon Shaolei Du, Natasha Jaques, Hao Peng, Pang Wei Koh, Hannaneh Hajishirzi（\* 共同一作）
> University of Washington · **Ai2** · UIUC · Princeton · LMSYS
> **ICML 2026**（PMLR 306）· `arXiv:2511.07317` · v1 2025-11-10 / **v2 2026-06-06**（本笔记据 v2 HTML 全文 + 附录 A–E + 全部 9 张图）
> 代码：github.com/Zhiyuan-Zeng/RLVE
> 课程：课外补读。和 Week 03 Voyager 的「自动课程」、Week 02 的「verifier 阶梯」直接对照
> 整理于 2026-10-12

> ⚠️ **这篇没有 Limitations 一节。** 只有 §7「Discussion on Future Work」和一段模板式 Impact Statement（*"none which we feel must be specifically highlighted here"*）。§6 失败模式一节因此大部分是我从图里挖的。
> ⚠️ **图里的具体数值（各 benchmark 分数、直方图计数）都是我读图估计的**，精度约 ±0.3pp，标「读图」。论文正文只给了 **3.37%**、**0.49%**、「约 2%」这几个数。我用读图值反算平均，和正文对得上（见 §5），所以读数大体可信。

---

## 0. 一句话总括

**手写 400 个能无限出题、程序判分、难度可调的「题目生成器」，训练时每个生成器各自跟踪模型在当前最高难度上的正确率，到 90% 就把难度往上推一级。在一个已经用 20,000 H100 小时练到饱和的 1.5B 模型上，再练约 1,100 小时，6 个推理 benchmark 平均涨 3.37 个点。**

核心贡献不是「程序生成的可验证数据」（那是 Reasoning Gym、InternBootcamp、SynLogic、Enigmata 已经做过的），也不是「自适应课程」（RL 里 POET、PLR 早就有，LM 上 SATURN 在单个 SAT 环境里做过），而是：

> **把两者在 400 个环境的规模上合起来，并用一个严格的 held-out 环境测试集（50 个训练时从未见过的环境）证明：扩充环境的数量，而不是在同一个环境里堆数据量，才是泛化推理能力的来源。**

🔑 它有 verifier，也有 ground truth（程序算出来的）。所以它能主张 **correctness**，这一点比 Generative Agents 强得多。但它的「泛化」主张要拆两层看：
- **对外**（6 个公开 benchmark）：证据扎实，但只有 **1.5B** 模型、一个 seed。
- **对内**（50 个 held-out 环境）：这些环境和训练环境是**同一批作者、同一种风格、同一个 gym** 写的。所以「OOD」更准确的说法是**「没见过的同族任务」**，不是分布外。

---

## 1. 动机与定位

引言把 RL 数据扩展的困难列成两条，**顺序有讲究**：

1. 收集带 ground-truth 答案的题目**很贵**（后文用 DeepMath-103K 的 **$138,000 / 127,000 GPU 小时**来具体化）
2. 题目**太易或太难**时 RL 会完全停滞：太易没有学习信号，太难则奖励一直很低（引 Razin et al. 的 vanishing gradients）

第 1 条是 procedural generation 解决的，第 2 条是 adaptive difficulty 解决的。🔑 **让这篇被 RL scaling 圈子重视的是第 2 条加上「data saturation」这个场景**：拿 ProRL-1.5B-v2 这个「在 136K 题上训到饱和」的模型当起点，再往上推。这回应的是当时的一个担忧：*"models' improvement increasingly saturates on finite training data"*（§1）。

两个设计原则（§3）：

> *"the environments are designed as pedagogical tools for developing reasoning capabilities"*（§1）

就像教小学生手算乘法，虽然计算器更快更可靠。**环境可以跑程序，模型不能。**

↔ 🔑 **这和 Week 03 的口号正好相反。** Week 03 说 *"let a program do what a program does better"*，这是 harness 视角：能交给程序的就交给程序。RLVE 是训练视角：**故意不让模型用程序**，逼它把算法内化成推理。两者不矛盾，但读这篇时要记住：**RLVE-Gym 的任务不是 agent 的真实任务**，它们是练习题。

🔑 评测标准要和用途匹配：不要批评「为什么要让 LM 手动排序」，这些任务本来就是体操，目标是迁移到 AIME、LiveCodeBench。

---

## 2. 方法精读

### 2.1 Verifiable Environment 的定义（§2.1）

$$E = (I, \mathcal{P}, R)$$

- $I$：输入模板（prompt 模板）
- $\mathcal{P}_d$：问题生成器（程序），按难度 $d \in [0, +\infty)$ 采样参数 $p$
- $R_p$：verifier（程序），对输出 $o$ 给出标量奖励 $R_p(o) \in \mathbb{R}$

关键扩展：**verifier 不必和标准答案比对。** Sudoku 检查是否满足所有约束，而不是和某个预存解比较（多解时后者会误判）。

附录 B.1：**所有 400 个环境的奖励范围都是 [−1.0, +1.0]**。格式错误统一给 **−1.0**。

🔑 这是 Week 02 verifier 阶梯的**最上面一级**（确定性检查，「十行代码，每次给出同样的答案」），而且被推到了极致：400 个环境，每一个都只靠这一级。

### 2.2 自适应难度（§2.2 + Algorithm 1 + 附录 A）🔥

每个环境 $i$ 各自维护：
- 难度区间 $[\ell_\pi^{(i)}, h_\pi^{(i)}]$，初始 **$\ell = h = 0$**
- 统计量 $(a^{(i)}, b^{(i)})$：**只统计 $d = h$ 的题**上的正确 rollout 数 / 总 rollout 数

流程：

```
每生成一道题：
  i ~ Uniform(1..n)              # 均匀选环境
  d ~ UniformInt(ℓ_i, h_i)       # 区间内均匀选难度
  p ~ P_d^(i)                    # 生成题
  rollouts, rewards
  if d == h_i: 累加 a_i, b_i

每次参数更新后，对每个环境：
  if b_i ≥ τ_num:
      if a_i / b_i ≥ τ_acc:  h_i += 1
          if h_i − ℓ_i + 1 > d_Δ:  ℓ_i = h_i − d_Δ + 1    # 滑动窗口
      a_i, b_i ← 0                # 无论升没升都清零
```

**附录 A 的默认参数：**

| 超参 | 值 |
| --- | --- |
| 准确率阈值 $\tau_{acc}$ | **0.9** |
| 最小样本阈值 $\tau_{num}$ | **8 × 每题 rollout 数** = 8 × 16 = **128 个 rollout** |
| 滑动窗口 $d_\Delta$ | **4** |
| $h$ 的上限 | **无** |

几个细节：

- **只升不降。** $h$ 没有回退机制，$\ell$ 随 $h$ 上移，低难度题会彻底退出采样。
- **统计只看最高一级。** 窗口里 $h-1, h-2, \ldots$ 的表现不被监控。
- **`IsCorrect(r_o)` 没有定义。** 很多环境用部分得分（见 §2.4，如 $(x/N)^{10}$），什么奖励算「正确」，论文没说。我推测是 $r = 1$，但这是**推测**。

🔑 这个机制的真实作用是**把「题目难度刚好在能力边界」这件事从数据集层面下放到每个环境自己**。脆弱处在于它是一个**阈值触发的单向棘轮**：没有遗忘检测，没有降级，而且推进速度和环境总数成反比（见 §8 第 2 条）。

### 2.3 RL 算法和 effective prompt ratio（§2.3 + 附录 C）

- 算法：**DAPO**（GRPO 变体），用 dynamic sampling：过采样后，**丢掉所有 rollout 奖励都相同的 prompt**，反复采直到填满 batch。
- **Effective prompt ratio** = 没被 dynamic sampling 丢掉的 prompt 比例。比例越高，浪费的 inference 越少（inference 是 RL 训练的算力瓶颈）。

🔑 这个指标是全篇的「温度计」：**RLVE 的整个论证就是「自适应让这个比例保持在高位」**。它也说明 RLVE 和 DAPO 的 dynamic filtering 是**互补的**：DAPO 在 rollout **之后**丢题，RLVE 在 rollout **之前**选题（§6 相关工作里也是这么定位的）。

**训练配置（附录 C）：**

| 项 | 值 |
| --- | --- |
| 框架 | **slime**（THUDM） |
| 训练 batch / 过采样 batch | **128 / 384** |
| 每 prompt rollout 数 | **16**，temperature **1.0** |
| KL / entropy loss | **都不用** |
| clip range | **[0.2, 0.28]** |
| 其他 | partial rollout、off-policy importance sampling、每个 rollout step 一次更新 |
| 优化器 | Adam，常数 LR，weight decay **0.01** |
| LR（1.5B 系列 / Qwen2.5-7B-Base） | **2×10⁻⁶ / 1×10⁻⁶** |
| 最大 rollout 长度（1.5B / 7B） | **24,576 / 8,192** tokens |
| 硬件 | 单节点 **8×H100 80GB** |
| 单次 run | **2–8 天 ≈ 350–1,500 H100 小时** |

Qwen2.5-7B-Base 用的 prompt（照抄）：

```
A conversation between User and Assistant. The user asks a question, and the assistant solves it. The assistant first thinks about the reasoning process in the mind and then provides the user with the answer. Show your work in <think> </think> tags, and return the final answer in <answer> </answer> tags.
User: {input}
Assistant: Let me solve this step by step.
<think>
```

### 2.4 RLVE-Gym：400 个环境（§3 + 附录 B）

六类来源（Table 1）：**编程竞赛 · 数学运算 · 优化问题 · 经典算法 · 逻辑谜题 · NP 完全问题**。

**附录 B.1 的六个样例，各自的难度映射和奖励函数**（这是正文没有的硬细节）：

| 环境 | 难度 $d$ → 参数 | 奖励 |
| --- | --- | --- |
| BubbleSwapLowerBound_PermutationCounting（改编自 **CNOI 2018**） | 排列长度 **N = d + 3** | 格式错 −1；否则 $(\min(x,y)/\max(x,y))^{10}$ |
| Integral | 表达式树节点数 **= d + 2** | 解析失败 −1；导数相等 +1；否则 0 |
| PolynomialMinimum | 多项式次数 **2(d + 1)** | 解析失败 −1；否则 $\left(\frac{f(x_{triv}) - f(x_0)}{f(x_{triv}) - f(x_0')}\right)^5$ |
| Sorting | 长度 **N ≈ 3 × 1.1^d** | 解析失败 −1；长度错 −0.5；否则 $(x/N)^{10}$ |
| Sudoku | **max(N, M) ≤ d + 2** | 解析失败 −1；全满足 +1；否则 0 |
| HamiltonianPathExistence | 顶点数 **N = d + 3** | 解析失败 −1；非合法排列 −0.5；否则 $(x/(N-1))^5$ |

**「利用解与验的不对称」的三个手法**（§3.2）：

1. **反向生成**：Integral 先随机生成 $F$，求导得到 $F'$ 作为题目，验证时只需对模型答案求导。**从来不需要算积分**，而随机的 $f$ 可能根本没有初等原函数。
2. **埋解生成**：Sudoku 从一个标准解出发做等价变换再挖空；Hamiltonian path 先随机排列顶点、连上相邻边**埋一条路径**，再加随机边。
3. **只验不解**：NP 完全问题的验证是多项式时间的。

> *"Exploiting this advantage provides supervision signals that are otherwise infeasible to obtain through imitation learning"*（§3.2）

**难度设计原则**（§3.3）：低难度题必须能**归约**到高难度题，或是它的子问题。例：能排 N+1 长的数组就能排 N 长的（在前面插一个最小元）；能做 $\int(f+1)$ 就能做 $\int f$。

⭐ **Sorting 的难度在低端是「假台阶」**（附录 B.1 推算）。N ≈ 3 × 1.1^d：d=0 → 3，d=1 → 3.3，d=2 → 3.63，d=3 → 3.99，d=4 → 4.39。如果取整，**d=0 到 d=2（甚至 d=3）生成的都是长度 3 的数组**。也就是说「难度 +1」在前几级可能**根本不改变题目分布**，只是让棘轮多走几轮 128 rollout 的检查。论文没说用的是哪种取整（「roughly proportional」），所以这条是**推测**，但指数映射在低端分辨率不足是确定的。

🔑 「难度是整数、每升一级 +1」这个统一接口，掩盖了**每个环境里 d 的含义完全不同**：有的线性（N = d+3），有的指数（1.1^d），有的翻倍（次数 2(d+1)）。论文 §4.1 自己也用这一点论证「静态难度无法跨环境统一调参」。但反过来看，**同一个 $\tau_{acc}$、同一个 $d_\Delta$ 套在 400 种完全不同的难度尺度上**，本身也是一个没检验过的假设。

---

## 3. 实验一：自适应 vs 静态难度（§4.1，Fig. 3 / Fig. 4）

### 3.1 单环境案例（Fig. 3）

**设置**：Qwen2.5-7B-Base，分别在 **Sorting** 和 **Multiplication**（难度 = 操作数位数）上单独训练。对照三种静态难度：**d ~ [0,1]、[0,20]、[0,100]**。
**评测**：ID 是同环境 **4,000** 道题，难度在 **[0, 20)** 均匀；OOD 是 $\mathcal{D}_{ood}$（**50 个环境 × 50 题 = 2,500 题**）。

**读图结果**（Fig. 3，横轴约 **25 H100 小时**）：

| | Sorting ID | Sorting OOD | Mult. ID | Mult. OOD |
| --- | --- | --- | --- | --- |
| 起点 | ~52 | ~13 | ~4 | ~13 |
| **Adaptive** | **~97** | **~22.5** | **~27** | **~32** |
| Static [0,1] | ~70（提前停） | ~14 | ~13 | ~30 |
| Static [0,20] | ~96 | ~21 | ~24 | ~31 |
| Static [0,100] | ~79 | ~17 | ~13 | ~16.5 |

Effective prompt ratio（Fig. 3a，横轴 **100 step**）：
- Static [0,1]：Sorting 在约 **step 20** 降到 **0**，曲线就此**终止**（训练无法继续填满 batch）
- Static [0,20]：Sorting 峰值约 **80%**，在约 **step 93** 降到接近 **0**
- Adaptive：稳定在 Sorting 约 **25%**、Multiplication 约 **30%**

论文的结论：静态难度上限太低，学习**停滞**；上限太高，**效率低**。static [0,20] 和 ID 分布重合，有 **oracle 优势**，但 adaptive 仍然打平甚至超过它。

**作者没报的部分：**

⭐ **adaptive 的 effective prompt ratio 也只有 25–30%**（Fig. 3a）。也就是说，即使有自适应难度，**70% 以上的 prompt 仍被 dynamic sampling 丢掉了**。论文强调「最高」，但没讨论为什么绝对值这么低。我的猜测：窗口里低于 $h$ 的那几级正确率已经 ≥ 90%，16 个 rollout 全对的概率很高。

⭐ **在 Sorting 上，effective ratio 不能解释 ID 差距。** static [0,100] 的 ratio（~20%）和 adaptive（~24%）很接近，但 ID 准确率差了约 **18 个点**（79 vs 97）。🔑 「有多少题是有效的」不等于「有效的是**哪些**题」：[0,100] 的有效题大多集中在 ID 测试范围之外。

⭐ **Multiplication 的 ID 只到 ~27%。** 7B base 模型在 25 GPU 小时内基本没学会多位乘法，但 OOD 却从 ~13 涨到 ~32。🔑 **这么大的 OOD 增益，很可能主要来自格式和输出习惯的学习**（base 模型第一次学会 `<answer>` 格式），而不是乘法能力的迁移。论文没有把格式效应和推理效应拆开。

### 3.2 多环境：静态无法逐个调参（Fig. 4）

**设置**：四个模型（Qwen2.5-7B-Base、R1-Distill-Qwen-1.5B、DeepScaleR-1.5B、ProRL-1.5B-v2）在 $\mathcal{C}_{256}$ 上联合训练 **400 步**。
**Fig. 4a**：step 400 时各环境的 $h^{(i)}$ 分布，正文说 *"a broad range from 0 to 12"*。
**Fig. 4b**：对照组用统一的静态 **[0, 20]**（覆盖了所有环境实际达到的难度）。

结果：adaptive 在四个模型上**始终高于**静态，差距读图约 **1–3 个点**。ProRL-1.5B-v2 上两条线有交叉（终点约 **55.5 vs 53.5**）。

⭐ **Fig. 4a 的分布是严重右偏的，「broad range」说得太宽了。** 读图：
- Qwen2.5-7B-Base：约 **93** 个环境停在 **h = 0**，约 **81** 个在 h = 1，约 **41** 个在 h = 2。也就是 **256 个里约 215 个（~84%）没走过第 2 级**。最高 **10**。
- R1-Distill：约 **90** 个在 h = 0，最高约 **10**
- DeepScaleR：约 **75** 个在 h = 0，最高 **11**
- ProRL-1.5B-v2：分布最平，h = 0/1/2 各约 **47 / 45 / 45**，最高 **12**

🔑 **400 步之后，大部分环境实际上只用了最简单的一两级。** 换句话说，主实验里「自适应」真正推起来的只是少数环境。这让人想问：多环境实验里的增益，有多少来自「难度自适应」，有多少只是「环境多样性」本身？Fig. 4b 的对照恰好**混淆了这两件事**（见 §8）。

⚠️ **「oracle」对照其实不是 oracle。** 正文说用 Fig. 4a 的分布 *"as oracle information"*，但实际做法只是取一个**统一的 [0, 20]** 来覆盖所有环境。对 84% 停在 h ≤ 1 的环境来说，[0, 20] 里 **90% 以上的题都太难**，这几乎注定输。真正的 oracle 应该是**逐环境用 $[0, h^{(i)}_{final}]$**。论文的论点（「必须逐环境调」）是对的，但这个对照证明不了「adaptive 胜过最优静态」。

⭐ **OOD 的统计噪声和差距同量级**（我算）。$\mathcal{D}_{ood}$ 每题只采 **1** 个样本（附录 D），n = 2,500，准确率 ~30% 时标准误 ≈ $\sqrt{0.3 \times 0.7 / 2500}$ ≈ **0.9pp**。Fig. 4b 的 1–3 个点差距大约是 **1–3 个标准误**，单 seed，也没有误差棒。

---

## 4. 实验二：环境数量 scaling（§4.2，Fig. 5）🔥

**设置**：在 $\mathcal{C}_{256}$ 里取嵌套子集 $\mathcal{C}_1 \subset \mathcal{C}_4 \subset \mathcal{C}_{16} \subset \mathcal{C}_{256}$，四个模型各自训练 **400 步**，在 $\mathcal{D}_{ood}$ 上评测。

**各集合的构成（附录 E）**：
- $\mathcal{C}_1$：**Multiplication**
- $\mathcal{C}_4$：+ **Division、EuclidGame、Sorting**
- $\mathcal{C}_{16}$：+ 12 个（GCDOne_Counting、HamiltonianPath、LampChanging、LargestConvexPolygon、PCPPermutation、Path_NoGoingBack_Counting、**SAT**、ShortestPath、SpiralMatrix、SubsequenceReversalLNDS、UndamagedSubmatrixCounting、WYRLevelingGround）
- $\mathcal{C}_{256}$：再 + **240** 个

**读图结果**（step 400 的 OOD 准确率）：

| 模型 | 起点 | C₁ | C₄ | C₁₆ | C₂₅₆ |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-7B-Base | ~13 | ~22.5 | ~22 | ~25 | **~30** |
| R1-Distill-Qwen-1.5B | ~22 | ~24 | ~31 | ~35 | **~42** |
| DeepScaleR-1.5B | ~26 | ~30 | ~36 | ~44 | **~50** |
| ProRL-1.5B-v2 | ~45 | ~45 | ~45 | ~51.5 | **~55.5** |

论文结论：
> *"merely increasing the volume of RL training data remains insufficient for improving generalizable reasoning capabilities, given that a single environment can already generate an unbounded amount of data."*（§4.2）

和 Procgen（Cobbe 2020）、Super-NaturalInstructions（Wang 2022）、INSTRUCTOR（Su 2023）的结论同构：**任务种类比数据量重要。**

🔑 这个实验设计是全篇**最干净的一处**：步数固定、每个环境都能无限出题，所以「数据量」被控制住了，变的只有「环境数」。

**作者没报的部分：**

⭐ **在 Qwen2.5-7B-Base 和 ProRL-1.5B-v2 上，C₁ ≈ C₄。** 从 1 个环境加到 4 个，**几乎没有增益**。🔑 C₄ 加的是 Division、EuclidGame、Sorting，和 Multiplication **同属「算术/简单算法」**。真正的跳跃出现在 C₁₆，它第一次引入了图、SAT、几何、计数。所以 Fig. 5 测的「环境数」和「**类别多样性**」是**混在一起的**。

⭐ **只有一条嵌套链、一个随机抽样。** 没有「换一组 16 个环境」的重复，看不出 16 个环境里换不同成员时方差有多大。

⭐ **ProRL-1.5B-v2 上 C₁ 和 C₄ 基本是平的**（~45 → ~45）。对一个已经饱和的 RL 模型，**窄环境的 RL 等于没训**。这其实是 §5.1 的一个预告：必须用**大量**环境，才能推动已经饱和的模型。

⚠️ **Fig. 3 和 Fig. 5 对同一个设置给出的数字对不上。** Qwen2.5-7B-Base 只在 Multiplication 上训练：Fig. 3c 的 OOD 到了约 **32%**，Fig. 5 的 C₁（也就是只有 Multiplication）在 400 步时只有约 **22.5%**。可能的解释是两者的**窗口大小不同**（见 §7 第 1 条：Fig. 3 用 $d_\Delta = 2$，Fig. 5 应该是默认的 4）和横轴不同（GPU 小时 vs 步数）。但论文没有并排讨论这一点。如果窗口大小能让单环境 OOD 差 **~10 个点**，那 $d_\Delta$ 就不是一个可以随手设的超参。

---

## 5. 实验三：在真实 benchmark 上 scaling（§5，Fig. 6–9）

**六个 benchmark 和指标**（附录 D）：

| Benchmark | 领域 | 指标 |
| --- | --- | --- |
| AIME 2024 / 2025 | 数学 | **Avg@64** |
| OMEGA-500 | 数学 | **Avg@4** |
| OlympiadBench | 数学 | **Avg@4** |
| LiveCodeBench **v6** | 代码 | 16 个样本里算 **Pass@8** |
| BBEH | 逻辑 | **Avg@4** |

评测用 SGLang，temperature **0.6**、top-p **0.95**，最大长度 **32,768**（1.5B 系列）/ **16,384**（7B）。

### 5.1 数据饱和场景（§5.1，Fig. 6 / Fig. 8）

**起点 ProRL-1.5B-v2**：从 R1-Distill-Qwen-1.5B 出发，用 **20,000+ H100 小时**、约 **136,000** 道题（数学、代码、逻辑、STEM、指令遵循）训到饱和。
**对照**：在同一个 ProRL 数据集上继续原 RLVR 训练的 checkpoint，**由 Hu et al. (2025b) 提供**。

| | 算力 | 平均增益 |
| --- | --- | --- |
| **RLVE（400 环境）** | **~1,100 H100 小时** | **+3.37** |
| 继续原 RLVR | **3,600 H100 小时** | **+0.49** |

**逐 benchmark（读图，Fig. 8，取各自最后一个点）：**

| | 起点 | RLVE 终点 | 继续 RLVR |
| --- | --- | --- | --- |
| AIME 2024 | ~52.0 | ~56.5（+4.5） | ~52.3（+0.3） |
| AIME 2025 | ~33.8 | ~39.8（+6.0） | ~34.4（+0.6） |
| OMEGA-500 | ~24.1 | ~27.8（+3.7） | ~23.9（**−0.2**） |
| OlympiadBench | ~57.9 | ~60.6（+2.7） | ~58.1（+0.2） |
| BBEH | ~7.4 | ~9.1（+1.7） | ~7.6（+0.2） |
| LiveCodeBench | ~26.0 | ~27.5（+1.5） | ~27.5（**+1.5**） |
| **平均（我算）** | **~33.5** | **~36.9（+3.4）** | **~34.0（+0.5）** |

反算的平均和正文的 **3.37 / 0.49** 吻合，说明 **3.37 是最后一个 checkpoint 的值，不是挑出来的峰值**。这一点值得肯定。

⭐ **LiveCodeBench 上两者打平。** RLVE 在代码上的终点增益（~+1.5）和继续 RLVR 一样。RLVE 的优势**几乎全在数学和逻辑**。考虑到 RLVE-Gym 有「相当一部分」环境改编自编程竞赛题，这个结果有点出人意料。🔑 可能的解释：RLVE 训练的是「手动模拟程序得出答案」，而 LCB 考的是「写程序」，两种能力的迁移比想象中弱。

⭐ **对照组只有一个点。** Fig. 6/8 里「继续原 RLVR」那条线**只有起点和终点两个 checkpoint**，中间的虚线是插值。所以看不出它在 1,100 小时时是多少，也看不出它是否一开始就平了。

⚠️ **Fig. 8 的「最高点水平线」不对称。** 图注说 *"each curve has a corresponding horizontal line indicating its highest point"*。RLVE 有**几十个** checkpoint，对照组只有**一个**。在噪声大的 benchmark 上（BBEH 在 7.3 到 10.7 之间来回跳），**在几十个点上取 max 天然占便宜**。正文的 3.37 用的是终点值，没受影响；但读图时如果看水平线，会高估 RLVE（例如 BBEH 峰值 ~10.8，终点只有 ~9.1）。

⚠️ **算力对比跨了不同的训练栈。** RLVE 用 slime + DAPO，对照 checkpoint 来自另一个团队（Hu et al. 2025b，即 BroRL 那篇），训练框架、rollout 设置都可能不同。**「3× 算力」是 GPU 小时之比，不是同等条件下的效率对比。**

### 5.2 算力受限场景（§5.2，Fig. 7 / Fig. 9）

**起点 OpenThinker3-1.5B**（当时最强的开源 1.5B SFT 模型，没做过推理 RL）。
**对照**：在 **DeepMath-103K**（约 **103K** 道高难数学题）上用**完全相同的设置**训练。两者都训练 **400 步**。

**读图（Fig. 9，step 400）：**

| | 起点 | RLVE | DeepMath-103K |
| --- | --- | --- | --- |
| AIME 2024 | ~54.3 | ~58.2 | ~56.4（峰值 ~57.5） |
| AIME 2025 | ~42.0 | ~49.9 | ~48.3（峰值 ~48.7） |
| OMEGA-500 | ~25.2 | ~29.4（峰值 ~29.8） | ~28.5 |
| OlympiadBench | ~56.8 | ~62.7 | ~60.3 |
| BBEH | ~4.0 | ~7.1（峰值 ~8.7） | ~5.4（峰值 ~6.1） |
| LiveCodeBench | ~28.2 | ~34.1（峰值 ~34.4） | ~31.8（峰值 ~32.0） |
| **平均（Fig. 7）** | **~35.1** | **~40.2（+5.1）** | **~38.4（+3.3）** |

正文：「about 2%」的优势；AIME 上 *"comparable"*，峰值高约 **1 个点**。和读图一致。

🔑 **最反直觉的一点**：一个**纯数学**数据集，在数学 benchmark（OMEGA、OlympiadBench）上**输给了**一堆排序、数独、图论题。

⚠️ **「相同步数」不等于「相同算力」。** §5.1 用 GPU 小时做横轴，§5.2 换成了 step。两种数据的 rollout 长度分布很可能不同（DeepMath 的高难题往往推理很长），每步的实际算力也不同。论文没报 §5.2 两条 run 各用了多少 GPU 小时。

⚠️ **成本对比不对称。** DeepMath-103K 的构建成本给了具体数字（**$138,000、127,000 GPU 小时**），RLVE-Gym 的成本只说 *"substantially more cost-efficient"*。**400 个环境的人工工程投入**（17 位作者中有多少人、花了多少小时）一个字没报。§7 自己也承认这是 *"substantial human effort"*。

⭐ **两条 run 在 step 400 都没收敛**（Fig. 7 里 RLVE 的最后一个点就是最高点，DeepMath 在最后一步还跳了 ~0.8）。所以「谁更好」只在 400 步这个预算下成立，**长期上限未知**。

---

## 6. 失败模式与局限

⚠️ 论文**没有**专门的 Limitations 一节。下面分两类：论文自己在 §7 承认的，和我从图里读出来的。

### 6.1 论文承认的：自动环境工程失败（§7）

作者试过用前沿 LM 自动写环境，但没有人工干预时**质量保不住**，具体卡在三处：

1. 输入模板的**无歧义性**
2. 问题生成器能否**可靠、高效地**生成**合法且多样**的题
3. verifier 面对各种模型输出时是否**稳健**

> *"LMs often struggle to design environments that exploit the asymmetry between solving and verification in computational complexity, as such designs typically requires expert knowledge and deliberate engineering."*（§7）

🔑 **这属于「verifier 本身需要被验证」这一类更一般的问题**（↔ Week 03 notes 里 Harrison 那条：*裁判本身也需要被裁判*）。RLVE 的扩展瓶颈不在算力，而在**写对 verifier 的人力**。这也意味着「400」这个数字很难再往上加一个数量级。

### 6.2 论文承认的：非可验证环境（§7）

创意写作、deep research 这类奖励无法写成算法的任务，**难度如何定义和控制**是开放问题。

### 6.3 我从图里读出来的

1. **自适应的覆盖面很窄**（Fig. 4a）：400 步后约 **84%** 的环境（Qwen 7B）还在 h ≤ 1。🔑 属于**课程推进速度 vs 环境数量**的矛盾（见 §8 第 2 条）。
2. **有效 prompt 比例上限只有 25–30%**（Fig. 3a）。🔑 属于**阈值课程和 GRPO 组内方差需求之间的错配**：$\tau_{acc} = 0.9$ 意味着窗口里大部分题已经「全对」。
3. **代码能力没有额外迁移**（Fig. 8 LCB）。🔑 属于**「手动模拟」和「写程序」是不同能力**。
4. **格式学习可能混进 OOD 增益**（Fig. 3c Multiplication）。🔑 属于**base 模型 RL 的通用混淆**。

---

## 7. ⚠️ 论文内部的不一致

| # | 一处说 | 另一处说 | 差别在哪 |
| --- | --- | --- | --- |
| 1 | 附录 A：默认滑动窗口 **$d_\Delta = 4$**；Fig. 4b 图例 $d \sim [h-3, h]$ 吻合 | Fig. 3 图例：*"Adaptive Difficulty: $d \sim [h_\pi - 1, h_\pi]$"*，即 **$d_\Delta = 2$** | §4.1 的单环境实验**没用默认超参**，正文也没说明 |
| 2 | Fig. 3c：Qwen 7B 只训 Multiplication，OOD 约 **32%** | Fig. 5：Qwen 7B 的 C₁（= Multiplication）OOD 约 **22.5%** | 窗口（2 vs 4）和横轴（25 GPU 小时 vs 400 步）都不同；论文未对照。见 §4 |
| 3 | 附录 C：*"Every training run"* 都是 **2–8 天、350–1,500 H100 小时** | Fig. 3 的单环境 run 横轴只到约 **25 H100 小时** | 附录 C 的「每一次」显然不包括 §4.1 的案例研究 |
| 4 | 正文：Fig. 4a 的 $h$ *"a broad range from 0 to 12"* | 图：四个模型的最大值分别约 **10 / 10 / 11 / 12**，且质量集中在 **0–2** | 「0 到 12」是**四个模型合并的极值**；说法没错，但「broad」会误导 |
| 5 | §4.1 称 [0, 20] 静态对照用了 *"oracle information"* | 实际是**统一区间**，不是逐环境区间 | 见 §3.2 |
| 6 | §5.1 的横轴是 **H100 小时** | §5.2 的横轴是 **step** | 两个场景的「效率」不能放在一起比 |

---

## 8. 在 agent 谱系里的位置

| 论文 | 管哪一层 | 什么在变 | 课程/难度怎么来 | 有无 verifier / ground truth |
| --- | --- | --- | --- | --- |
| **ReAct** | 推理时，单 episode | 不变（prompt） | 无 | 任务成败 ✅ |
| **Generative Agents** | 推理时，记忆 | 记忆流 | 无 | ❌ 只能主张 believability |
| **Voyager** | 推理时，procedural 技能库 | 技能库（代码） | **GPT-4 自动课程**：*尽可能新，同时仍在够得着的范围内* | GPT-4 critic ⚠️ + 环境状态 ✅ |
| **SRA** | 推理时，技能取用 | 不变 | 无 | 规则匹配 + 单元测试 ✅ |
| **AIDE²** | 推理时，harness 代码 | agent 自己的 harness | 无（固定任务集） | 双层 held-out ✅ |
| **RLVE** | **训练时，模型权重** | **权重** | **每个环境一个阈值棘轮**：$\tau_{acc} = 0.9$ 就 $h{+}{+}$ | **程序 verifier ✅，程序算出的 ground truth ✅** |

论文里提到、你还没精读的近亲（**据 RLVE §6 的相关工作，未读原文，不作为可引用结论**）：

| 系统 | 和 RLVE 的区别 |
| --- | --- |
| Reasoning Gym / SynLogic / Enigmata / InternBootcamp | 程序生成的可验证数据，但**难度静态**；InternBootcamp 观察到早期饱和，也发现更多环境有帮助，但**测试题不保证来自没见过的环境** |
| SATURN（Liu 2025c） | 自适应难度，但**只有 SAT 一个环境** |
| Absolute Zero / SPIRAL / SPICE | **self-play**：模型自己出题。RLVE 刻意避开，因为 LM 生成的题和 verifier 可能是错的 |
| PRIME（Cui 2025）/ DAPO | 在 rollout **之后**过滤；RLVE 在 rollout **之前**选题，二者互补 |
| POET / PLR / Procgen | 经典 RL 里的环境生成和课程，RLVE 的思想来源 |

🔑 **RLVE 和 Voyager 是同一个想法，放在两层。** 两者都在回答「下一道题出什么」，答案都是「刚好够得着的」。区别在于：
- **Voyager** 用 **LLM 判断**出题，结果存进**技能库**（推理时，外置）
- **RLVE** 用**正确率阈值**出题，结果写进**权重**（训练时，内化）

Voyager 的课程是语义的、开放的，但出题者和裁判都是 GPT-4，可能出错。RLVE 的课程是数值的、封闭的（只能沿着人设计的 d 轴走），但**每一步都可验证**。

🔑 **它不是 Voyager 或 harness 工程的替代，而是它们之下的一层**：RLVE 改进的是 harness 里那个「模型」本身的推理底子。你在 Week 03 写的 skill 跑在什么模型上，这篇决定的是那个模型的推理能力怎么练出来。

### ↔ 与课程的对照

| 课程内容 | RLVE 的对应 |
| --- | --- |
| Week 02：verifier 阶梯，最上一级是「十行代码，每次给出同样的答案」 | RLVE-Gym 的 400 个 verifier **全在最上一级**；§7 说明连这一级**也很难自动写对** |
| Week 03：*"let a program do what a program does better"* | RLVE 的原则正好相反：**训练时不让模型用程序**。harness 视角和训练视角的分工 |
| Week 03：Voyager 自动课程 *「尽可能新，同时仍在够得着的范围内」* | $\tau_{acc} = 0.9$ + 滑动窗口就是这句话的**数值化版本** |
| Week 03 notes：*裁判本身也需要被裁判* | §7 自动环境工程失败的三条原因，全部是「verifier/generator 质量谁来保证」 |

---

## 9. 批判性分析

### 论文自己承认的

见 §6.1–6.2：自动环境工程的三个质量问题，以及非可验证环境的难度控制尚无办法。论文**没有**承认任何关于实验设计本身的局限。

### 我自己补的

1. **「Scaling Up」只在 1.5B 上验证过。** 标题说 scaling，但 §5 的两个主实验都是 **1.5B**，§4 的分析最大到 **7B base**。在更大的模型上，RLVE-Gym 里的大部分环境可能在 d = 0–2 就被秒杀，阈值棘轮要推很多级才有信号；也可能大模型本来就会，迁移消失。**这不是一个参数问题，是外推问题**：RLVE 最有吸引力的主张（「环境比数据重要」）恰恰是在最小的模型上证明的。

2. **课程推进速度和环境数量成反比，这不 scale。** 每个环境要攒够 **128** 个 $d = h$ 的 rollout 才检查一次。环境是均匀采样的，所以环境数从 256 增加到 4,000 时，每个环境的推进速度**慢约 16 倍**。Fig. 4a 已经显示 256 个环境、400 步后多数环境停在 h ≤ 1。**「环境越多越好」（§4.2）和「每个环境都要推到能力边界」（§4.1）在固定算力下是互相拉扯的**，论文把两者分开论证，从来没让它们正面碰过。可能的改进：按学习进度加权采样环境（PLR 式），而不是均匀采样。

3. **「环境数」和「类别多样性」混在了一起。** Fig. 5 的 C₁ → C₄ 几乎没有增益（同属算术），C₄ → C₁₆ 才开始跳（引入图论/SAT/几何）。所以 §4.2 的结论更准确的说法可能是「**类别**多样性驱动泛化」，而不是「环境**数量**」。这决定了社区下一步该做什么：如果是数量，就该写更多同类环境；如果是类别，就该找新的**任务族**。

4. **OOD 测试集和训练集同源，泛化主张偏强。** 50 个 held-out 环境出自同一批作者、同一个模板风格、同一个奖励格式（[−1, 1]、格式错 −1）。模型学会「RLVE-Gym 风格的题怎么答」，就能在这 50 个上涨分。§5 的公开 benchmark 是更可信的证据，但它们只有一个 seed，而且部分 benchmark（BBEH 在 7–11 之间跳）噪声和增益同量级。

5. **棘轮只升不降，没有遗忘监控。** $\ell$ 上移后，低难度题彻底退出采样，也没有对它们的回测。在 400 个环境、长训练里，**低级技能会不会退化**完全没有被测量。

6. **没有 verifier 被 hack 的分析。** 论文自己在 §7 说 LM 很难写出「对各种模型输出都稳健」的 verifier，但对**人写的** 400 个 verifier，同样的风险一个字没测。部分得分函数（如 Sorting 的 $(x/N)^{10}$、长度错只扣到 −0.5）给了模型一些「部分正确就有奖励」的捷径。

**值得做的复现实验：**
> 固定 **400 步**、Qwen2.5-7B-Base（或 R1-Distill-1.5B），在 $\mathcal{D}_{ood}$ 和 6 个 benchmark 上比较四个条件：
> (a) $\mathcal{C}_{16}$ 原版；
> (b) 16 个环境**全部来自同一类**（如 16 个算术/计数环境）；
> (c) 16 个环境**各来自不同类**（6 类各取 2–3 个）；
> (d) $\mathcal{C}_{256}$ 但**关闭自适应**、改用**逐环境** $[0, h^{(i)}_{final}]$ 的真 oracle 静态区间。
> (b) vs (c) 拆开「数量」和「多样性」；(d) vs 原版 $\mathcal{C}_{256}$ 回答「多环境实验里，自适应本身到底贡献多少」。每个条件 **3 个 seed**。按附录 C 的 7B 配置，一次 run 约 350 H100 小时，总共约 **12 次 run、~4,000 H100 小时**。

---

## 10. 复习自测题

1. 一个 verifiable environment 是哪三元组？哪两个部分是程序实现的？
2. RLVE 的 $a, b$ 统计的是哪些题的 rollout？升级判断发生在每道题之后还是每次参数更新之后？
3. $\tau_{acc}$、$\tau_{num}$、$d_\Delta$ 的默认值分别是多少？$\tau_{num}$ 按 16 个 rollout 换算是多少个 rollout？
4. 滑动窗口在什么条件下更新 $\ell$？更新后 $\ell$ 等于什么？$h$ 会不会下降？
5. Fig. 3 的 adaptive 曲线用的窗口是多少？和附录 A 的默认值一致吗？
6. Effective prompt ratio 的定义是什么？为什么它直接关系到训练效率？Fig. 3 里 adaptive 稳定在大约多少？
7. Sorting 环境的数组长度和难度 d 是什么关系？奖励函数是什么？长度错扣多少？
8. Integral 环境怎么做到「从来不需要算积分」？表达式树的节点数和 d 是什么关系？
9. Hamiltonian path 环境如何保证路径存在？奖励的指数是几？
10. $\mathcal{C}_1$ 是哪个环境？$\mathcal{C}_4$ 加了哪三个？为什么 C₁ → C₄ 在两个模型上几乎没有增益？
11. $\mathcal{D}_{ood}$ 有多少个环境、每个环境多少题、难度范围是多少？每题采几个样本？
12. ProRL-1.5B-v2 原本训练了多少 H100 小时、多少道题？RLVE 再训多少小时涨了多少？继续 RLVR 用了多少小时涨了多少？
13. 在 Fig. 8 里，哪个 benchmark 上 RLVE 和继续 RLVR 的终点增益打平？
14. DeepMath-103K 的构建成本是多少？§5.2 的对比为什么不能直接说成「同等算力下更好」？
15. §7 说自动环境工程卡在哪三点？

---

## 11. 核心数字速查表

| 项 | 数字 |
| --- | --- |
| 环境总数 | **400** |
| 环境来源类别 | **6**（编程竞赛 / 数学运算 / 优化 / 经典算法 / 逻辑谜题 / NP 完全） |
| 奖励范围 | **[−1.0, +1.0]**，格式错 **−1.0** |
| $\tau_{acc}$ | **0.9** |
| $\tau_{num}$ | **8 × rollout 数 = 128** |
| $d_\Delta$（默认 / Fig. 3） | **4 / 2** |
| 初始 $\ell, h$ | **0, 0** |
| held-out 环境 / 题 / 难度 | **50** 个 × **50** 题 = **2,500**，d ∈ **[0, 4]**，每题 **1** 个样本 |
| $\mathcal{D}_{ood}$ 标准误（我算，p≈0.3） | **≈ 0.9pp** |
| 训练集合 | **C₁ ⊂ C₄ ⊂ C₁₆ ⊂ C₂₅₆**（从剩余 **350** 个里取） |
| C₁ | **Multiplication** |
| C₄ 增量 | **Division、EuclidGame、Sorting** |
| §4.1 ID 测试 | **4,000** 题，d ∈ **[0, 20)** |
| 静态对照 | **[0,1] / [0,20] / [0,100]** |
| Fig. 3 横轴 | **~25 H100 小时** / **100 step** |
| Fig. 3 adaptive effective ratio | Sorting **~25%** · Mult **~30%** |
| Fig. 3 Sorting ID（adapt / [0,20] / [0,100] / [0,1]） | **~97 / ~96 / ~79 / ~70** |
| Fig. 3 Mult OOD（adapt / [0,20] / [0,1] / [0,100]） | **~32 / ~31 / ~30 / ~16.5** |
| Fig. 4a h 范围（Qwen7B / R1 / DSR / ProRL） | 最大 **10 / 10 / 11 / 12** |
| Fig. 4a Qwen7B h=0/1/2 计数 | **~93 / ~81 / ~41**（h ≤ 1 约 **84%**） |
| Fig. 4b 差距 | **~1–3pp**；ProRL 终点 **~55.5 vs ~53.5** |
| Fig. 5 C₂₅₆ OOD（Qwen7B / R1 / DSR / ProRL） | **~30 / ~42 / ~50 / ~55.5** |
| Fig. 5 C₁ OOD（同序） | **~22.5 / ~24 / ~30 / ~45** |
| 训练步数（§4、§5.2） | **400** |
| ProRL-1.5B-v2 原始训练 | **20,000+ H100 小时**，**~136,000** 题 |
| §5.1 RLVE | **~1,100 H100 小时**，**+3.37** |
| §5.1 继续 RLVR | **3,600 H100 小时**，**+0.49**（小 **7×**） |
| §5.1 平均（起点 / RLVE / RLVR，读图） | **~33.5 / ~36.9 / ~34.0** |
| §5.1 LCB 增益（RLVE / RLVR） | **~+1.5 / ~+1.5** |
| §5.2 平均（起点 / RLVE / DeepMath） | **~35.1 / ~40.2 / ~38.4** |
| §5.2 RLVE 优势 | **约 2pp** |
| DeepMath-103K 构建成本 | **$138,000**，**127,000 GPU 小时** |
| 评测指标 | AIME **Avg@64** · OMEGA/Olympiad/BBEH **Avg@4** · LCB **v6 Pass@8（16 样本）** |
| 评测采样 | temp **0.6**，top-p **0.95**，最大 **32,768 / 16,384** |
| 训练 batch / 过采样 | **128 / 384** |
| 每题 rollout / temp | **16 / 1.0** |
| clip | **[0.2, 0.28]**，无 KL、无 entropy loss |
| LR（1.5B / 7B） | **2×10⁻⁶ / 1×10⁻⁶** |
| weight decay | **0.01** |
| 最大 rollout 长度（1.5B / 7B） | **24,576 / 8,192** |
| 硬件 / 单 run | **8×H100**；**2–8 天 ≈ 350–1,500 H100 小时** |
| BubbleSwap | 改编自 **CNOI 2018**，N = **d+3**，奖励指数 **10** |
| Integral | 节点 **d+2**，奖励 **+1 / 0 / −1** |
| PolynomialMinimum | 次数 **2(d+1)**，奖励指数 **5** |
| Sorting | N ≈ **3 × 1.1^d**，长度错 **−0.5**，指数 **10** |
| Sudoku | max(N,M) ≤ **d+2** |
| HamiltonianPathExistence | N = **d+3**，非法排列 **−0.5**，指数 **5** |

⚠️ 「~」开头的都是读图估计，引用时注明「据 Fig. X 读图」。论文正文给出的精确数字只有：**3.37 / 0.49 / 3× / 7× / 1,100 / 3,600 / 20,000 / 136,000 / 103K / $138,000 / 127,000** 和附录里的超参。

---

## 相关

- [[Voyager 论文精读笔记]] —— 同一个「刚好够得着」的自动课程，Voyager 放在推理时 + 技能库，RLVE 放在训练时 + 权重
- [[AIDE2 论文精读笔记]] —— 同样依赖 held-out 来防过拟合；AIDE² 的 held-out 是任务的隐藏测试集，RLVE 的是 50 个没见过的环境
- [[SRA 论文精读笔记]] —— 都把「规则匹配 / 单元测试」当 verifier；SRA 测的是取用，RLVE 用它来训练
- [[Generative Agents 论文精读笔记]] —— 谱系里唯一没有 verifier 的一篇，可以拿来和 RLVE 对比「有无 ground truth 决定能主张什么」
- [[ReAct 论文精读笔记]]
- [[course/reading-list.zh.md]]
