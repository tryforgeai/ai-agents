# AIDE² 论文精读笔记

> **Recursive self-improvement of AI research agents**
> Dhruv Srikanth, Bingchen Zhao, Dixing Xu, Yuxiang Wu, Zhengyao Jiang
> **Weco AI**（全部作者同属一家公司；baseline AIDE_human 是该公司的生产系统）
> `arXiv:2609.26457v1` · 提交 2026-09-22 · cs.AI / cs.LG / cs.SE
> 课程：课外补读，与 Week 04 之后的「自动提示词优化（DSPy / MIPROv2 / GEPA）」直接相关
> 整理于 2026-10-11（据 v1 PDF 全文 + arXiv HTML 版附录 D/E）

> ⚠️ **venue：无。** arXiv 页面没有 journal-ref，引用时按 preprint 处理。
> ⚠️ **利益相关：** 作者、被改进的 agent（AIDE）、对照基线（AIDE_human）、外层驱动 agent 全部出自 Weco。没有第三方复现。
> ⚠️ **代码未见公开链接**（正文和附录里我没找到 repo）。

---

## 0. 一句话总括

**让一个 AI 研究 agent 改写自己的 harness 代码，在 AI 研发任务上跑分、用隐藏测试集挑出更好的版本，再让新版本成为下一轮被改写的对象——8 天 100 步，接受了 7 次改写，得到的 agent 在 4 个外部 benchmark 上追平或超过人类团队花两年打磨的生产 agent。**

核心贡献不是「agent 改自己的代码」（那是 STOP 2024、Darwin Gödel Machine 2026 已经做过的），而是：

> **把自我改进的目标从"写代码的能力"（DGM 用 SWE-bench 当代理指标）换成"做 AI 研发的效率"本身，并在固定预算下证明增益能迁移到选择阶段从没见过的任务和领域。**

⚠️ **两个硬伤从一开始就限定了论文能主张什么：**

1. **噪声没有被量化到能支撑"7 次改进都是真的"。** 附录 D 承认 Δg ≈ **−0.004 ~ −0.007** "small relative to observed run-to-run variability"，而 7 次接受的平均增量只有 (0.778−0.703)/7 ≈ **0.011**。论文**没有报告 g 的 run-to-run 标准差**，也**没有对 incumbent 重新评估**。→ 能主张"loop 最终找到了更好的 agent"（外部 benchmark 支持），**不能**主张"每一步都是真改进"或"存在持续的上升趋势"。
2. **"ignition"（自我改进能否加速）没有得到证据。** §3.6 作者自己说 inconclusive。→ 论文证明了**一阶的 RSI**（agent 能改进自己当研究员的能力），**没有证明递归**（改进后的 agent 更会改进 agent）。标题里的 "recursive" 比证据走得远。

🔑 和你已读的四篇的关系：

| | 关心什么 | 谁在改 agent |
| --- | --- | --- |
| **ReAct** | 单次任务里推理和行动怎么交错 | 人 |
| **Generative Agents** | 经历怎么写入、检索、反思 | 人 |
| **Voyager** | 技能怎么造、存、复用 | 人（agent 只往技能库里加东西） |
| **SRA** | 库大时怎么取对、用对 skill | 人 |
| **AIDE²** | **harness 本身（搜索策略、上下文管理、选择规则）怎么写** | **agent 自己** |

---

## 1. 动机与定位

摘要里的论证顺序：

1. AI agent 已经在自动化 AI 栈各层的研发（训练效率、推理优化）
2. → 下一步是改进**研究 agent 自身**的研究效率
3. → 被优化的对象就是 agent 自己的代码时，每次被接受的改写成为下一轮的编辑对象 = **recursive self-improvement**
4. → 意义在于对抗「R&D 投入的边际回报递减」（引 **Bloom et al. 2020**, *Are ideas getting harder to find?*）

**第 4 条是这篇被"AI 安全 / 智能爆炸"圈子关注的原因**——它直接把 Good (1965) 的老问题落到可测的实验上。第 1–3 条是给做 agent 工程的人看的。

> *"Such systems improve the efficiency of the artifacts they produce, such as training and inference efficiency, yet the efficiency of the research process producing them remains fixed."* —— §1

🔑 **评测标准要和用途匹配。** 这篇主张的是"研究效率"，而它对研究效率的操作化定义是**固定预算下代码优化任务的得分**。所以它能被公平批评的点是"这个定义够不够代表研究"，而不是"它没发现新科学"。

**目标层：harness。** 模型权重冻结，只改模型外面那层代码（搜索、上下文、验证）。

> *"Our experiments target the harness layer, the code that surrounds a model and controls an agent's search, context, and verification."* —— §1

论文说 appendix C 证明了"agent 的实际能力有相当一部分由 harness 决定"——⭐ 附录 C 的证据是：**gemini 3 flash + AIDE₈₅（1858）> fable 5 + AIDE₀（1796）**（ALE-Bench，同为 **$20** 预算）。**换 harness 的收益超过换一个更强的模型。** 但 MLE-Bench 上 fable 5 的增益在一个标准误之内（**0.823 → 0.828**），所以这个结论**只在 ALE-Bench 上成立**。

---

## 2. 方法精读

### 2.1 双层优化（bi-level）

**内层：** agent `a` 在任务 `t` 上反复改代码，直到花完固定美元预算 `b_t`（token + 执行成本）：

```
x_i = a( x_<i , r_t^pub(x_<i) )        (1)
```

结束时 agent **自己挑一个**解 `x̂_t` 交出去。「下一步编辑哪个节点、交哪个、记忆怎么组织」全都是 agent 代码的一部分，**外层可以改**。

**打分：** 交出的解在**私有 held-out 数据**上算 `r_t^priv`，跨 T 个任务取平均：

```
g(a) = (1/T) Σ_t r_t^priv( x̂_t )        (2)
```

实际上每个任务独立跑几次再平均（⚠️ **几次没说**；T 是多少**也没说**）。

**外层：** 做替换 `(a, x, r^pub) ↦ (a^out, a, g)`，同一个公式上提一层：

```
a_k = a^out( a_<k , g(a_<k) )          (3)
a*_k = argmax_{a ∈ a_≤k} g(a)          (4)
```

外层 agent 总是**编辑当前 incumbent**（目前 g 最高的），被接受的改写就成为下一步的底稿。

🔑 **两层的选择机制不对称**：内层的选择策略是可编辑的（后来真被改成了 bandit），**外层的 argmax 是写死的**。这意味着外层没法学会"对噪声做稳健选择"——而这恰恰是 §5 Discussion 承认的最大问题。

### 2.2 两条设计约束（论文明说的）

1. **public / private 分离**：内层看 `r^pub`，外层按 `r^priv` 选。内层 agent **无法直接优化外层的选择标准**。
   ⭐ 附录 D：被拒的改写里，**约四分之一**在 agent 可见的 public 信号上比 incumbent 高、在 private grade 上更低而被拒。**这是 public/private 分离在起作用的直接证据**——没有它，这四分之一会被接受。
2. **固定预算 `b_t`**：所有 agent 同预算，增益只能来自更好的算法而不是更多算力。

> *"evaluating all agents under the same per-task budget b_t constrains improvements to arise from a better algorithm rather than from spending additional compute."* —— §2.1

🔑 **但"同预算"不等于"同步数"。** 预算按美元算时，更短的 prompt = 更便宜的调用 = 更多搜索步。§3.5 的上下文压缩（最多 **~50×**）有一部分增益就是这样"买"来的。这仍然是"更好的算法"，但读者应该知道增益的来源之一是**省 token 换步数**。

### 2.3 AIDE₀：被改进的起点

- 从 **AIDE**（Jiang et al. 2025，MLE-Bench 上表现好）精简而来：去掉 ML 专用部件，保留树搜索
- 三个算子：**draft**（探索新想法）/ **debug**（修 bug）/ **improve**（精修有希望的方向）
- 搜索策略：**贪心**——分数最高的解做下一次操作的父节点
- 有一个 **reviewer**：读执行输出，抽取分数和反馈
- **完整历史拼接**：每个 draft / improve prompt 都带上所有先前候选的代码和执行输出 → prompt 随运行增长

### 2.4 外层 agent 与模型配置

| 角色 | agent | 模型 |
| --- | --- | --- |
| 外层（改写者） | **AIDE_human**（Weco 生产系统，两年人工迭代） | **claude opus 4.7** |
| 内层（被评估者） | AIDE₀ → AIDE_k | **gemini 3 flash** |

- 为什么内层用便宜模型：在任务预算 `b_t` 下，**gemini 3 flash 追平或略超**更贵的模型
- 为什么外层用强模型：**评估一个候选的成本远大于提出它的成本**，所以提案质量值得花钱
- 同理：内层 reviewer **单次 LLM 调用**读执行输出；外层 reviewer **多步探索**评估产物

🔑 **AIDE_human 身兼三职**：外层驱动者、对照基线、ignition test 的参照臂。它既是"老师"又是"考官"又是"对手"——这在 §8 批判里展开。

### 2.5 选择基准（selection benchmark）：三个任务族

1. **ML engineering**：训练模型达到目标指标
2. **Heuristic algorithm engineering**：竞赛编程式组合优化
3. **Harness engineering**：改进 agent 的 prompt、上下文管理、反馈回路

> *"We construct the task set to be diverse in order to induce evolutionary pressure on the types of improvements that are made to the inner-loop agent, namely general mechanisms over task-specific tricks."* —— §2.1

🔑 第 3 族很微妙：**agent 在练习改 harness，而外层又在改它的 harness。** 这让"自我改进"和"在任务上表现好"之间有了一条额外的通路——但论文没有分族报告 g，看不出哪一族贡献了多少。

---

## 3. 实验一：持续改进的轨迹（§3.2，Fig. 2）

**设置：** **8 天**墙钟，**100 节点**轨迹（初始 agent + **99** 个改写提案）。

**结果：** **7 次接受**，分别在第 **2、6、28、39、47、63、85** 步；incumbent grade **0.703 → 0.778**；AIDE_human 在同一 grade 下为 **0.749**。

| 步 | 改写内容（Fig. 2 标注） |
| --- | --- |
| **2** | 在策略上做 bandit 搜索 |
| **6** | 要求先做根因诊断再修 bug |
| **28** | 通过 fork 冠军节点逃离平台期 |
| **39** | 一次 robustness 修复崩溃后自我修复 |
| **47** | 修补一个导致评估崩溃的错误 |
| **63** | 读日志前先压缩刷屏输出 |
| **85** | 降级一个容易失败的 draft 策略 |

另外**两次完整重复**同一协议，分别接受了 **2** 次和 **4** 次改写。

### 作者没报的部分

- ⚠️ **另外两次 run 的最终 grade 没报。** 只说"also produced sustained improvements"。如果它们停在 0.72 附近，那主 run 的 0.778 就是三次里最好的一次——**选最好的 run 来展示**。
- ⚠️ **g 的噪声水平没报。** 附录 D 只给了一句定性的"small relative to observed run-to-run variability"（针对 −0.004 ~ −0.007）。
- ⚠️ **没有对 incumbent 重评。** argmax 在噪声上选 = **winner's curse**：被选中的分数系统性偏高。0.778 很可能高估了 AIDE₈₅ 的真实 g。
- ⭐ **Fig. 2 的轴从 0.644 截断**，且有一个早期候选得分 **0.565** 落在图外。buggy 候选画在底部一行、不给分——**buggy 率没报**（数图上的叉可以估，但论文没给数字）。
- ⭐ **7 次改写里有 3 次（39、47、85）本质是修 bug / 降级坏策略**，不是新能力。第 47 步"修补导致评估崩溃的错误"——见 §5 的 ⚠️，这一步可能部分改变了**度量**而不是**能力**。

> *"Because candidates were selected on g, the recursive self-improvement trace is not meant to demonstrate generalization beyond the selection benchmark."* —— §3.2

作者诚实之处：明确说 Fig. 2 **不证明泛化**，只证明"在选择基准上超过了 AIDE_human"（他们叫 **first-order generalization**：从 public 信号泛化到同任务的 private 数据）。

---

## 4. 实验二：外部 benchmark 上的迁移（§3.3，Fig. 3 / Table 1）

**设置：** 四个从未参与选择的 benchmark（**second-order generalization**），对比 AIDE₀ / AIDE₄₇（前 50 步内的 incumbent）/ AIDE₈₅（最终 incumbent）/ AIDE_human。

| Benchmark | 分布 | 任务 × 种子 | 主约束 | 模型 | 指标 |
| --- | --- | --- | --- | --- | --- |
| **ALE-Bench lite** | in（任务族级） | **10 × 10** | **$5** / 200 步 / 12h | gemini 3 flash | 竞赛表现分 |
| **MLE-Bench lite** | in | **22 × 3** | **$5** / 500 步 / 24h | gemini 3 flash | private percentile |
| **FML-Bench** | in | **18 × 3** | **100 步** | **gpt-5.4** | 平均归一化测试提升 % |
| **WeatherBench 2** | **out** | **1 × 3** | **$15** / 200 步 | **gemini 3.1 pro** | forecast-skill gain |

| Agent | ALE | MLE | WB2 | FML (%) |
| --- | --- | --- | --- | --- |
| AIDE₀ | 1536 ± 33 | 0.678 ± 0.006 | 0.262 ± 0.205 | 15.0 ± 0.9 |
| AIDE₄₇ | 1713 ± 26 | **0.730 ± 0.005** | **0.798 ± 0.003** | 19.7 ± 1.2 |
| AIDE₈₅ | **1790 ± 9** | 0.722 ± 0.011 | 0.793 ± 0.005 | **19.9 ± 1.1** |
| AIDE_human | 1511 ± 35 | 0.708 ± 0.007 | 0.404 ± 0.193 | 19.6 ± 1.0 |

（± 为 benchmark 均值的 1 个标准误）

**论文结论：** 两个进化 checkpoint 都优于 AIDE₀；AIDE₈₅ 在四个上都**追平或超过** AIDE_human。增益非单调：AIDE₈₅ 在 ALE / FML 最好，AIDE₄₇ 在 MLE / WB2 最好。

### WeatherBench 2：最惊人的那个数字

起点是一个**动力学核心（dynamical core）**，评估四个场（**500 hPa 位势高度、2 m 温度、海平面气压、10 m 纬向风**），预报时效 **1–15 天**，与 **ERA5** 对比，相对 **persistence 预报**换算成 skill。报告的是**相对未修改核心的提升**，不是 leaderboard 绝对分。

> *"On every seed, both evolved checkpoints independently converged on the same family of changes to the forecasting model's numerics, reaching nearly identical gains with almost no variation across runs. AIDE0 and AIDEhuman reach a comparable solution on at most one seed and vary widely across the rest."* —— §3.3

### 作者没报的 / 需要小心的

- ⚠️ **"追平或超过"四个里有两个是统计上的平手。** FML：**19.9 ± 1.1 vs 19.6 ± 1.0**；MLE：AIDE₈₅ **0.722 ± 0.011 vs 0.708 ± 0.007**。真正拉开差距的是 **ALE（1790 vs 1511）** 和 **WB2（0.793 vs 0.404）**。
- ⚠️ **WB2 是 1 个任务 × 3 个种子。** AIDE₀ 和 AIDE_human 的标准误（**0.205 / 0.193**）几乎和均值一样大——它们是"有时找到、有时没找到"的双峰分布。"OOD 上增益最大"这句话建立在 **n = 3** 上。🔑 更准确的说法是：**进化后的 agent 每次都找到了那个数值改动，旧 agent 大约三次里找到一次**——这是**可靠性**的提升，不一定是能力上限的提升。
- ⚠️ **"那个数值改动"具体是什么，论文没说。** 对一个 OOD 主张来说，这是最该公开的细节。
- ⭐ **FML-Bench 用步数而不是美元做约束**（**100 步**）。所以在 FML 上，上下文压缩**不能**通过"省钱换步数"贡献增益。FML 上 AIDE₀ → AIDE₈₅ 的 **+4.9pp** 是纯粹每步质量的提升——**这是全文最干净的一个对照**，但论文没指出这一点。
- ⭐ **FML 用 gpt-5.4、WB2 用 gemini 3.1 pro**——与选择时的 gemini 3 flash 不同。所以 Fig. 3 本身就已经是**跨模型**迁移，不只是跨任务。论文在附录 C 才专门讲跨模型，没在正文点出 Fig. 3 已经包含了这一层。
- ⭐ 附录 A：AIDE₀ 有 **5 个 FML-Bench run** 因上下文窗口溢出提前终止（按终止时最好的候选打分）。所以 AIDE₀ 的 **15.0** 部分是被**崩溃**拖低的，而不全是搜索质量差。附录 E 明确说 AIDE₄₇、AIDE₈₅、AIDE_human **都没有**遇到这个问题。

---

## 5. 实验三：reward hacking 下降（§3.4，Fig. 4）

**设置：** KernelBench 子集——agent 把 PyTorch 模块替换成自定义 GPU kernel，在**孤立计时**（proxy）上优化。然后把 kernel 插进 **GPT-2 / ViT / CNN** 训练循环，看 proxy 增益留下多少。共 **38 个 (kernel, 训练上下文) 对**，**3 个种子**，**20 步**，gemini 3 flash。

**判定规则（附录 A）：** 孤立加速 **> 1.02×**，且训练中保留的加速**不到一半**、或者**运行时崩溃** → 记为 reward hacking。

**结果：** AIDE₀ **55%** → AIDE₄₇ **39%** → AIDE₈₅ **32%**；AIDE_human **39%**。

> *"These reward hacking rates establish a held-out behavioral change, though they do not identify which rewrites produced it."* —— §3.4

### 作者没报的部分

- ⭐ **换算成计数**（我按 38 推算，论文没给）：55% ≈ **21/38**，39% ≈ **15/38**，32% ≈ **12/38**。AIDE₀ → AIDE₈₅ 差 **9 对**。
- ⚠️ **没有显著性检验。** 我用 Fisher 精确检验（双侧）粗算：**AIDE₀ vs AIDE₈₅ p ≈ 0.063**；**AIDE₈₅ vs AIDE_human p ≈ 0.63**。而且 38 个对**不独立**（同一个 kernel 出现在多个训练上下文里），真实有效样本更少。→ "下降"在 0.05 水平上**不显著**；"比人类基线低 7pp"**完全在噪声内**。
- ⚠️ **"emergent"这个词用得过头。** §3.5 披露 AIDE₈₅ 里加了一条**固定指令**：每个代码生成 prompt 都提醒模型"解会在一个看不到的私有划分上评分，应偏好稳健、可泛化的做法"。**这条指令几乎就是在叫它别 reward hack。** 下降可能有相当部分直接来自这句 prompt，而不是从搜索策略里"涌现"。论文说 robustness 机制 *"may account for"* 这个下降——这已经削弱了"loop 从未优化过它"的叙事：loop 优化的是 private grade，而"别过拟合 public 信号"和"别 reward hack proxy"是**同一种压力**。
- 🔑 所以更准确的表述：**public/private 分离在选择阶段施加了"别骗 proxy"的压力，这个压力迁移到了一个新的 proxy（孤立计时）上。** 这不是意外，是设计的直接后果——而这本身就是一个有价值的结论，比"emergent"更有用。

---

## 6. 解剖 AIDE₈₅：进化出了什么（§3.5）🔥

### 6.1 搜索策略：bandit over 策略臂 + 定期 fork

- 五个固定 draft 策略：**conservative / aggressive_rewrite / ensemble / tuned_specialist / robust_simple**
- 每个新节点**继承父节点的策略标签**
- 每步用 **UCB1** 选一个策略臂；**30%** 的步改为按各臂最好分数做 **softmax** 采样
- 选中臂后，扩展该臂下**分数最高**的节点
- **每 5 步** fork 一次全局最优节点，在**另一个策略臂**下继续改进

> *"Selecting over strategy arms rather than individual nodes gives the agent a lever on the diversity of approach, not just on which local optimum to polish."* —— §3.5

🔑 **在"策略"而不是"节点"上做 bandit** 是这里最聪明的一点：臂的数量固定为 5，UCB 统计量能很快稳定；而在节点上做 bandit，臂数随树增长，永远估不准。Fork 解决的是"平台期继续精修收益递减、但重新 draft 又会丢掉已有的好解"——**在冠军身上换策略**两头都避开。⭐ Fig. 5（ALE 一个任务前 60 节点）直观显示：AIDE₀ 几乎全部节点都来自一个 draft，AIDE₈₅ 同时维持多条谱系。

### 6.2 上下文管理：有界 prompt + 按 bug 率触发的失败记忆

- draft / improve 算子不再读完整历史，改读**根节点和近期候选的紧凑摘要**
- **失败记忆**：当候选 bug 率 **≥ 15%** 时，向 draft / improve prompt 注入**最多 3 条**反复出现的错误签名（近期 buggy 候选的最后几行错误，去重）
- **15%** 阈值是 AIDE² 自己选的；bug 少时机制休眠

**效果（median task-level 每次调用 prompt 缩小倍数，运行结束时）：**

| | vs AIDE₀ | vs AIDE_human |
| --- | --- | --- |
| MLE-Bench | **7×** | 2.6–5.7×（与 ALE、FML 合并报告的区间） |
| ALE-Bench | **~50×** | 同上 |
| FML-Bench | **~50×** | 同上 |
| WeatherBench 2 | **>40×** | **13–14×** |

附录 E 还说 AIDE₀ 的 prompt 比 AIDE_human **大 3–14×**。

🔑 **"按 bug 率门控的失败记忆"是一个可以直接搬走的模式。** 它解决的是 Generative Agents 式记忆流的老问题：**大部分记录是噪声**。这里的做法是"平时不记，出问题频繁时才注入，且只注入去重后的最多三条"——**记忆的写入由一个运行时统计量门控**，而不是每步都写。

↔ 和 [[Generative Agents 论文精读笔记]] 的 importance 打分门控 reflection 是同一类设计：**用一个便宜的标量决定何时启用昂贵的记忆机制。**

### 6.3 稳健性：三个机制

1. **两条 prompt 级保护**：
   - 固定指令：提醒"私有划分上评分，偏好稳健可泛化方案"（见 §5 的 ⚠️）
   - 生成代码几乎为空（**< 40 个字符**，如 stub / 占位符）时重新 prompt
2. **选择规则**：按"与 top 候选中位数的距离"惩罚每个候选，防止选中偶然的高分
   - ⚠️ **但论文自己说：这个惩罚保序，回放所有 held-out run，它从未改变过选中的候选。** → **这是一个死机制。** 它被保留下来，说明外层 argmax 无法剔除"无害但无用"的代码——正是 §5 Discussion 承认的"unused artifacts"。
3. **修复评估脚本**：某个任务的 held-out 评分脚本只要任一测试用例失败，就会在**所有**用例上崩溃；AIDE₈₅ 加了一个补丁让单个失败不再拖垮整个评估。

> *"a narrow, low-risk intervention targeting a verified failure mode . . . without altering search dynamics"* —— agent 对自己补丁的描述，§3.5 引用

> *"Interestingly, rather than exploiting the broken evaluation, AIDE2 repaired it."* —— §3.5

⚠️ **这一条论文写成了亮点，但我认为它是全文最需要追问的地方。** 如果被修复的是**选择基准**里某个任务的 held-out 评分，那么第 47 步（"patches an error that crashed evaluations"）的 g 增益中，有一部分来自**度量被修好了**，而不是 agent 变强了。**"修复评估"和"篡改评估"在机制上是同一种能力**——区别只在意图，而意图恰恰是我们不能从分数里读出来的。论文没有说：

- 这个补丁改的是 agent 自己的代码（绕开崩溃）还是评分脚本本身
- 第 47 步的增益里有多少来自这个修复
- 为什么 harness 的改写能够触达 held-out 评分路径（这本身就是一个隔离漏洞）

### 6.4 被拒绝的提案（附录 D）⭐

外层提了很多经典方法，**全部被拒**：

| 提案 | 对应经典方法 | g · Δg |
| --- | --- | --- |
| 岛屿种群 + 周期迁移和交叉 | island-model GA | 0.685 · **−0.021** |
| LLM 裁判两两锦标赛做选择 | tournament selection + pairwise LLM judging | 0.654 · **−0.090** |
| 停滞触发的探索升级 | reactive search / adaptive restarts | 0.704 · **−0.040** |
| 继续精修 vs 重启的决策 | Luby restart policies | 0.666 · **−0.078** |
| 提交时多数投票集成 | bagging / self-consistency | 最高 0.723 · **−0.031**（3 个变体） |
| 探索率调参与衰减 | decaying ε-greedy | 0.748 · −0.006（噪声内） |
| 方差自适应探索 | UCB-V | 0.674 · **−0.080** |
| 祖先-后代趋势回传 | MCTS value backup | 0.7497 · −0.004（噪声内） |
| 提升第二名 / 近似平局覆盖 | optimizer's curse 下的选择 | 5+ 变体 · 最好 −0.007（噪声内） |
| 把对单节点的大量重访视为过拟合嫌疑 | 无直接对应 | 0.7498 · −0.004（噪声内） |

> *"Ensembling methods were explored during the recursive self-improvement run but were never retained, with the agent's analyses consistently noting that ensembling LLM calls consumes budget that could otherwise fund additional search steps."* —— 附录 D

🔑 三条读表发现：

1. **LLM-as-judge 选择是最差的提案（−0.090）。** 在有可执行指标的场景里，用 LLM 判断替代数字只会更糟——和课上"有 verifier 就别用 judge"的经验一致。
2. **集成在固定预算下是负收益。** 这是"固定预算"约束最直接的体现：在算力不限的论文里集成几乎总有效，这里每次都被拒。
3. **"optimizer's curse 下的稳健选择"被提了 5 次以上、全都在噪声内被拒**——而外层自己就在 optimizer's curse 下工作（§2.1 的 🔑）。**loop 反复想修的正是它自己的病，但外层的 argmax 是写死的，它改不到那一层。**

---

## 7. 实验四：Ignition test（§3.6，Fig. 7）

**问题：** 进化后的 agent 当外层驱动者，是否比产生它的 agent 更擅长驱动 RSI？如果不是，就不会从递减回报变成加速回报。

**设置：** 两臂，各 **3 个种子 × 50 步**，内层都从 **AIDE₄₇** 起步。
- 处理臂：外层 = **AIDE₄₇**
- 参照臂：外层 = **AIDE_human**

**结果：** 平均终点 **0.780**（AIDE₄₇）vs **0.782**（AIDE_human）。处理臂约 **20 步**到达最终区域，参照臂约 **40 步**。

> *"with only three seeds per outer-loop agent, we find these results to be inconclusive; they do not establish that AIDE47 is more sample-efficient as a self-improver than AIDEhuman."* —— §3.6

作者只主张：**没有明显退化。**

### ⭐ 作者没并排看的一点

⚠️ **主 run 走了 85 步才从 0.703 到 0.778；ignition test 两臂都只用 50 步就从 AIDE₄₇ 出发到达 0.780 / 0.782。** 也就是说，从同一个 AIDE₄₇ 出发，**另外 6 个独立的 50 步 run 平均都追上或超过了主 run 第 47–85 步的全部成果**。两种解读：

- (a) 0.78 附近是这个 harness 空间在该基准上的一个**天花板**，谁来驱动都会撞上去
- (b) 主 run 第 47 步之后的 incumbent 分数（0.778）本身就受 winner's curse 影响，真实值更低

两种都说明：**主 run 后半段的"持续上升"不应被当作 RSI 特有的现象。** 论文没有做这个比较。

---

## 8. 失败模式与局限（§5 Discussion）

### 8.1 噪声在两层之间复合

> *"If the noise is high enough, a falsely accepted rewrite becomes the new incumbent (eq. (4)), so a single noisy comparison can derail the outer loop's subsequent search."* —— §5

**具体表现：** 内层轨迹随种子变化 + 单个解的评估本身有噪声 → g 同时包含两种噪声 → 一次假阳性接受会改变后续所有编辑的底稿。

🔑 这属于**进化计算里的 noisy fitness + elitism** 问题：精英保留 + 噪声适应度 = 被幸运个体劫持。经典解法（重评精英、统计门控如 Wu et al. 2025、co-evolving evaluator 如 Red Queen Gödel Machine）论文在相关工作里都引了，**但自己一个都没用**。

### 8.2 成本让结论无法变强

> *"a definitive comparison would be prohibitively costly, requiring additional seeds of recursive self-improvement and a full held-out evaluation of each seed's final agent."* —— §5

🔑 这是**所有 RSI 研究的结构性问题**：评估一个"改进者"需要跑完整个改进过程，而改进过程本身就要多天。**元层级每上一层，统计功效需要的算力乘一个大常数。** 这意味着"ignition"这种问题可能**在可负担的算力下原则上测不出来**。

### 8.3 进化出来的 agent 难以理解

> *"It is unclear which components drive performance and which, if any, are unused artifacts of earlier recursive self-improvement steps."* —— §5

**具体表现：** §6.3 那个从未改变选择结果的惩罚规则就是现成的例子。

🔑 属于 **bloat**（遗传编程里的代码膨胀）。GP 文献里 bloat 是公认的、几乎不可避免的现象；**这里没有任何简约性压力**（没有对代码长度或复杂度的惩罚），所以 bloat 只会随步数累积。

### 8.4 部署摩擦

进化出的 agent 需要兼容现有产品功能和部署基础设施。🔑 **研究原型和生产系统之间的差距**——论文提到但没展开。

---

## 9. 在 agent 谱系里的位置

| 论文 | 管哪一层 | 核心问题 | 谁改 agent | 有无 verifier / ground truth |
| --- | --- | --- | --- | --- |
| **ReAct** | 单 episode | 推理与行动怎么交错 | 人 | 任务成败 ✅ |
| **Generative Agents** | episodic → semantic 记忆 | 经历怎么写入、检索、反思 | 人 | ❌ 只能主张 believability |
| **Voyager** | procedural（技能库） | 技能怎么造、存 | 人；agent 只扩充技能库 | 环境 ✅ |
| **SRA** | procedural 的取用侧 | 库大时怎么取对、用对 | 人 | 规则匹配 + 单元测试 ✅ |
| **AIDE²** | **harness（搜索 / 上下文 / 选择 / 验证）** | **agent 能否改进自己做研发的效率** | **agent 自己** | **双层：内层 public 指标 ✅，外层 private held-out ✅** |

论文里提到、你还没精读的近亲（只记定位，**未读原文，以下不作为可引用结论**）：

| 系统 | 和 AIDE² 的区别（据 AIDE² 的相关工作一节） |
| --- | --- |
| **STOP**（Zelikman 2024） | 改进的是"改进器"脚手架 |
| **Darwin Gödel Machine**（Zhang 2026a） | 维护自改写编码 agent 的**档案库**；用 SWE-bench 作为"能改好自己"的代理指标 |
| **ADAS**（Hu 2025）/ **Meta-Harness**（Lee 2026） | 优化整个 harness，但**优化者和被优化者是分开的** |
| **GEPA**（Agrawal 2026b）/ **DSPy** | 优化 prompt / pipeline，不涉及自指 |
| **AlphaEvolve / OpenEvolve / ShinkaEvolve** | 种群式程序进化，优化的是**产物**，驱动过程仍是人写的 |

🔑 **AIDE² 不是 Voyager 或 GEPA 的替代，是它们之上的一层。** Voyager 让 agent 积累**技能**（agent 的"知识"），GEPA 让外部优化器改进 **prompt**，AIDE² 让 agent 改写**决定自己如何搜索和记忆的代码**。它和 DGM 的根本区别在于**目标函数**：DGM 优化"编码能力"并假设这能迁移到"自我改进能力"，AIDE² 直接优化"研究效率"——但正如 ignition test 所示，**直接优化研究效率并没有自动带来更好的自我改进能力**。

### ↔ 与课程的对照

| 课程内容 | AIDE² 的对应 |
| --- | --- |
| Week 02：保留 Oracle prompt 的**隐藏测试**失败 | 外层只看 **private grade**；附录 D 里约 1/4 被拒提案是"public 涨、private 跌"——**隐藏测试防过拟合**的大规模实证 |
| Week 04 Lab：*"Tonight's skill becomes the baseline the optimizer must beat."* | 外层 `argmax` + incumbent 机制就是这句话的自动化版本；注意本文的教训——**没有重评的 baseline 会被噪声抬高** |
| Week 04 之后：DSPy / MIPROv2 / GEPA | 这几个都在 AIDE² 的"automated harness search"相关工作里；区别是它们的**优化器是固定的**，AIDE² 让优化器本身也可被优化 |
| Week 00：把记忆决定交给 harness（`persists`） | AIDE₈₅ 的 bug 率门控失败记忆是 harness 决定"何时写记忆"的一个**被搜出来**的实例 |

---

## 10. 批判性分析

### 论文自己承认的

见 §8：噪声复合、ignition test 不确定、成本限制统计功效、进化出的 agent 难以解释且可能含无用代码、部署摩擦。§3.4 也承认 reward hacking 下降**无法归因到具体改写**。

### 我自己补的

1. **"Recursive"在证据上只走了一步。** 论文证明了 agent 能改进自己作为**研究员**的能力（一阶），但"递归"的核心主张——改进后的 agent 作为**改进者**也更强——被 ignition test 判为不确定。标题和摘要都在暗示递归已被演示。更准确的标题是 *Self-improvement of AI research agents at the harness layer*。

2. **外层选择没有噪声控制，但整篇的定量叙事依赖它。** argmax + 不重评 + 噪声与增量同量级 = 经典的 winner's curse。"7 次接受、持续上升"可能部分是在噪声上挑最大值的产物。**这不是参数问题，是结构问题**：只要外层选择规则写死且不可编辑，loop 就无法修复它——附录 D 显示 loop **反复尝试**修这类问题（optimizer's curse 相关提案 5+ 次）却只能改内层。

3. **"修复评估"揭示了隔离边界不清。** harness 的改写能触达 held-out 评分路径，本身就是安全上的红旗。论文把它当正面例子讲，但在一个以"分离信号防 hacking"为核心设计原则的系统里，**被评估者能修改评估者是这个原则的直接失效**——无论这次的修改是善意的。

4. **baseline 的独立性不够。** AIDE_human 同时是外层驱动者、对照基线和 ignition 参照臂，且是作者公司自己的产品。它"强"的唯一外部证据是 FML-Bench 上领先 AI Scientist v2 **0.3pp**（19.6 vs 19.3），论文自己承认 *"The margins separating the leading agents are small relative to the seed-level standard error."* 用一个和第二名统计平手的系统去宣称"追平人类两年 R&D"，分量要打折扣。

5. **"研究效率"的操作化很窄。** 所有任务都是"给定代码库 + 给定标量指标 → 优化"。真正的研究里最难的部分——**选问题、定指标、判断结果是否有意义**——全部在 loop 之外。这篇证明的是"自动化的代码优化器能自我改进"，这对 R&D 的哪一部分有多大推动，论文没有论证。Bloom et al. 的"想法越来越难找"恰恰主要是**找对问题**难。

6. **关键统计量缺席，无法独立估计效应大小。** 选择基准的任务数 T、每任务重复次数、每任务预算 b_t、8 天 run 的总成本、g 的 run-to-run 标准差、另两次 run 的最终 grade、buggy 率、reward hacking 的显著性——**全都没报**。对一篇以"RSI 有效"为核心主张的论文，这些是判断主张强度的必要信息。

**值得做的复现实验：**
> 用**同一个外层 agent**、**同样 100 步**，但每次接受前对 incumbent 和候选**各重评 5 次**（或用 Wu et al. 2025 的统计门控），跑 3 个种子。比较：(a) 接受次数，(b) 最终 incumbent 在 Fig. 3 四个 benchmark 上的表现。如果 (a) 显著减少而 (b) 基本不变，说明原 run 的"7 次改进"里有相当部分是噪声；如果 (b) 也提升，说明噪声控制本身就是 RSI 最值得加的一个机制。成本约为原 run 的 **5×**——贵，但比论文自己说"prohibitively costly"的 ignition test 便宜。

---

## 11. 复习自测题

1. 外层 agent 和内层 agent 分别用什么模型？为什么内层选更便宜的那个？
2. 公式 (2) 里的 g(a) 用的是 public 还是 private 分数？为什么这个选择是防 reward hacking 的核心？
3. 主 run 走了多少步、多少天？接受了几次改写？incumbent grade 从多少到多少？AIDE_human 在同一 grade 下是多少？
4. 另外两次重复 run 各接受了几次改写？论文报告了它们的最终 grade 吗？
5. AIDE₈₅ 的 bandit 用什么算法选策略臂？有百分之多少的步改用 softmax？fork 的周期是几步？
6. 五个 draft 策略分别叫什么？新节点的策略标签从哪里来？
7. 失败记忆在什么条件下激活？最多注入几条错误签名？签名是怎么构成的？
8. 在 FML-Bench 上，上下文压缩为什么**不能**通过"省钱换步数"贡献增益？（提示：看约束类型）
9. reward hacking 的判定阈值是什么？共多少个 (kernel, 训练上下文) 对？三个训练上下文是哪三个模型？
10. AIDE₀ → AIDE₈₅ 的 reward hacking 率从多少降到多少？按 38 对换算差几对？这个差异在 0.05 水平上显著吗？
11. 附录 D 里哪个被拒提案的 Δg 最差？为什么集成方法从未被保留？
12. Ignition test 两臂的终点分别是多少？各自大约多少步到达最终区域？作者的结论是什么？
13. 附录 C 里，gemini 3 flash + AIDE₈₅ 在 ALE-Bench 上的分数和 fable 5 + AIDE₀ 相比如何？这个结论在 MLE-Bench 上成立吗？
14. AIDE₈₅ 里有一个"从未改变过选中候选"的机制，是哪个？它说明了什么？

---

## 12. 核心数字速查表

| 项 | 数字 |
| --- | --- |
| 主 run 墙钟 | **8 天** |
| 轨迹长度 | **100 节点**（1 初始 + **99** 提案） |
| 接受次数 | **7** |
| 接受步 | **2, 6, 28, 39, 47, 63, 85** |
| incumbent grade | **0.703 → 0.778** |
| AIDE_human grade | **0.749** |
| Fig. 2 轴截断 / 图外点 | **0.644** / **0.565** |
| 另两次 run 接受次数 | **2** / **4** |
| 平均每次接受增量（我算） | **≈ 0.011** |
| 噪声内 Δg | **−0.004 ~ −0.007** |
| 被拒中 public 更高的比例 | **约 1/4** |
| 外层模型 | **claude opus 4.7** |
| 内层模型 | **gemini 3 flash** |
| ALE-Bench lite | **10 / 40** 题 × **10** 种子，**$5**，200 步，12h |
| MLE-Bench lite | **22 / 75** 赛题 × **3** 种子，**$5**，500 步，24h |
| FML-Bench | **18** 任务 × **3** 种子，**100 步**，**gpt-5.4** |
| WeatherBench 2 | **1** 任务 × **3** 种子，**$15**，200 步，**gemini 3.1 pro** |
| KernelBench | **38 对** × **3** 种子，**20 步** |
| ALE（0 / 47 / 85 / human） | **1536 / 1713 / 1790 / 1511** |
| MLE（0 / 47 / 85 / human） | **0.678 / 0.730 / 0.722 / 0.708** |
| FML %（0 / 47 / 85 / human） | **15.0 / 19.7 / 19.9 / 19.6** |
| WB2（0 / 47 / 85 / human） | **0.262 / 0.798 / 0.793 / 0.404** |
| WB2 标准误 AIDE₀ / human | **0.205 / 0.193** |
| reward hacking（0 / 47 / 85 / human） | **55% / 39% / 32% / 39%** |
| 推算计数 | **21 / 15 / 12 / 15**（/38） |
| Fisher p：AIDE₀ vs AIDE₈₅ / AIDE₈₅ vs human（我算） | **≈ 0.063 / ≈ 0.63** |
| hacking 判定 | 孤立加速 **> 1.02×** 且训练中保留 **< 一半** 或崩溃 |
| UCB1 外的 softmax 比例 | **30%** |
| fork 周期 | **每 5 步** |
| draft 策略数 | **5** |
| 失败记忆阈值 / 条数 | bug 率 **≥ 15%** / 最多 **3** 条 |
| 空代码保护阈值 | **< 40 字符** |
| prompt 缩小 vs AIDE₀ | MLE **7×** · WB2 **>40×** · ALE / FML **~50×** |
| prompt 缩小 vs AIDE_human | ALE/MLE/FML **2.6–5.7×** · WB2 **13–14×** |
| AIDE₀ prompt vs AIDE_human | 大 **3–14×** |
| AIDE₀ 上下文溢出终止 | FML **5** 个 run · ALE（$20）**48** 个 run |
| Ignition test | **3** 种子 × **50** 步 × 2 臂；终点 **0.780**（AIDE₄₇）/ **0.782**（human） |
| Ignition 到达终点区域 | **~20 步** / **~40 步** |
| 附录 C 预算 | **$20**，ALE 时限 **36h** |
| ALE 跨模型（AIDE₀ → AIDE₈₅） | gemini 3 flash **1577 → 1858** · fable 5 **1796 → 1944** · gpt-5.6-sol **2025 → 2121** |
| MLE 跨模型（AIDE₀ → AIDE₈₅） | gemini 3 flash **0.701 → 0.747** · gpt-5.6-sol **0.767 → 0.794** · fable 5 **0.823 → 0.828** |
| FML 排名 | AIDE_human **19.6** · AI Scientist v2 **19.3** · Autoresearch **19.2** · AIDE **17.8** · OpenEvolve **15.1** · AI Scientist v1 **13.2** · AIRA **13.2** |
| 最差被拒提案 | LLM 裁判锦标赛 **−0.090** |

⚠️ 同一个 agent 在不同预算下的分数不同，别混用：ALE 上 gemini 3 flash + AIDE₀ 在 **$5** 下是 **1536**（Fig. 3），在 **$20** 下是 **1577**（Fig. 9）；AIDE₈₅ 对应 **1790 / 1858**。MLE 上 AIDE₀ 是 **0.678 / 0.701**。

---

## 相关

- [[Voyager 论文精读笔记]] —— agent 积累技能但不改自己的循环；AIDE² 改的正是那个循环
- [[Generative Agents 论文精读笔记]] —— importance 门控 reflection ↔ bug 率门控失败记忆
- [[ReAct 论文精读笔记]] —— AIDE 的 draft / debug / improve 是 ReAct 循环在代码搜索上的特化
- [[SRA 论文精读笔记]] —— 同样是"上下文放不下时怎么办"，SRA 靠检索，AIDE₈₅ 靠有界摘要
- [[course/reading-list.zh.md]] —— DSPy 已在清单中；GEPA 是 Week 04 之后的内容
- [[course/ai-agents-week-04/index.md]] —— "skill becomes the baseline the optimizer must beat"
