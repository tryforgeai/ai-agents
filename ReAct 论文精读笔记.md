# ReAct 论文精读笔记

> **ReAct: Synergizing Reasoning and Acting in Language Models**
> Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
> Princeton University + Google Research (Brain team)
> ICLR 2023 · arXiv:2210.03629v3
> 项目页：https://react-lm.github.io/

---

## 0. 一句话总括

**ReAct = Reason + Act。** 让大模型在解题时，把"想一步"（Thought）和"做一步"（Action，如查维基百科）**交错穿插**地生成，而不是只想不做（CoT）或只做不想（Act-only）。这个极其简单的 prompt 改动，同时解决了 CoT 的**幻觉**问题和 Act-only 的**缺乏规划**问题，并让 agent 的行为变得**可解释、可调试、可被人类中途修改**。

> **为什么这篇论文在 AI Agents 课上是必读？**
> 今天你用的几乎所有 agent 框架（LangChain Agent、AutoGPT、OpenAI function calling 的循环、Claude 的 tool use 循环）底层都是 ReAct 这个 Thought→Action→Observation 循环的变体。这是"LLM agent"这个概念工程化的起点论文。

---

## 1. 动机：为什么需要把"推理"和"行动"合起来？

### 1.1 人类的直觉类比（论文开篇就用了这个）

论文用了**做饭**的例子。你在厨房做菜时，脑子里其实在同时干两件事：

| 内心独白（Reasoning） | 外部动作（Acting） |
|---|---|
| "菜都切好了，该烧水了" | 打开火 |
| "没有盐了，那我用酱油加胡椒代替" | 打开冰箱看看有什么 |
| "面团怎么做来着？我得查一下" | 上网搜菜谱 |

关键点：**这两条线不是分开的，而是互相喂养的。**
- 推理告诉你**下一步该做什么动作**（reason to act）
- 动作带回来的信息**修正你的推理**（act to reason）

论文引用了认知科学基础：内语（inner speech, Alderson-Day & Fernyhough 2015）、Vygotsky 的自我调节理论、Baddeley 的工作记忆理论。**上课时这是个很好的开场点：ReAct 的设计灵感是认知科学，不是纯工程 hack。**

### 1.2 当时研究界的两条割裂的路线

**路线 A：只推理（Reasoning-only）**
代表是 Chain-of-Thought（CoT, Wei et al. 2022）。让模型输出"让我们一步步想"，在算术、常识、符号推理上效果很好。

> **致命缺陷**：CoT 是一个 **static black box（静态黑箱）**。模型只用自己脑子里的内部表征生成推理，**没有 grounding（没有接地到外部世界）**。结果就是：
> - **事实幻觉（hallucination）**——编造不存在的事实
> - **错误传播（error propagation）**——第一步错了，后面全错，而且没有任何机制能纠正

**路线 B：只行动（Acting-only）**
代表是 SayCan (Ahn et al. 2022)、WebGPT (Nakano et al. 2021)、Inner Monologue (Huang et al. 2022b) 等。用 LLM 预测下一个动作，在交互环境里执行。

> **致命缺陷**：这些工作**不用语言模型做抽象的高层推理，也不维护工作记忆来支撑行动**。模型只是一个"反应式"的策略函数，不会分解目标、不会跟踪进度、不会处理异常。

**论文的空白点（gap）**：在这两条路线之间，**没人系统研究过把两者协同（synergize）起来会怎样**，以及这种结合能否带来系统性收益。唯一接近的 Inner Monologue，论文在第 4 节专门论证了它"并不是真正的内心思考"（详见本笔记 §4.4）。

---

## 2. 方法：ReAct 到底是什么（第 2 节精读）

### 2.1 形式化定义（一定要理解这个，很可能被考）

标准的 agent-环境交互设定：

- 时刻 $t$，agent 从环境收到观察 $o_t \in \mathcal{O}$
- 按策略 $\pi(a_t | c_t)$ 采取动作 $a_t \in \mathcal{A}$
- 其中**上下文** $c_t = (o_1, a_1, \cdots, o_{t-1}, a_{t-1}, o_t)$ 是到目前为止的全部历史

难点在于：从 $c_t \mapsto a_t$ 这个映射**高度隐式（highly implicit）且需要大量计算**。也就是说，"看完这一大堆历史，直接决定下一步干什么"这一跳太大了，模型跳不过去。

**ReAct 的核心改动，一行就能写完：**

$$\hat{\mathcal{A}} = \mathcal{A} \cup \mathcal{L}$$

**把动作空间扩展为「原动作空间 ∪ 语言空间」。**

- $\mathcal{A}$：真实动作（搜索、点击、拿起物品……）→ 会改变环境，会返回 observation
- $\mathcal{L}$：语言空间里的动作，称为 **thought（思考）/ reasoning trace（推理轨迹）**

**thought 的关键性质：**
> $\hat{a}_t \in \mathcal{L}$ **不影响外部环境，因此也不会带回任何 observation 反馈。**
> 它唯一做的事是：$c_{t+1} = (c_t, \hat{a}_t)$ —— 把自己写进上下文里，去支撑未来的推理或行动。

**这是整篇论文最精妙的一点，务必吃透：**
思考被"伪装"成了一种动作。这样一来，你不需要改模型架构、不需要训练、不需要额外模块——**只要在同一个自回归生成流里，允许模型输出一种"空动作"，agent 就有了工作记忆和规划能力。**

### 2.2 Thought 有哪些类型？（论文列举的 5 类）

论文明确指出 thought 不是单一用途，而是有多种功能（对应 Figure 1 里的标注）：

1. **分解任务目标 / 制定计划**（2b Act 1；1d Thought 1）
   - "我需要先搜 x，找到 y，再找 z"
2. **注入常识知识**（2b Act 1）
   - "胡椒瓶更可能出现在柜子(1-6)、台面(1-3)……"
3. **从观察中抽取关键信息**（1d Thought 2, 4）
   - "这段话没提东部区域" / "x 创立于 1844 年"
4. **跟踪进度、转换子目标**（2b Act 8）
   - "现在找到胡椒瓶 1 了。接下来我要把它放进抽屉 1"
5. **处理异常、调整计划**（1d Thought 3）
   - "Front Row 搜不到，那我改搜 Front Row (software)"

另外还有：做常识/算术推理（"1844 < 1989"）、引导搜索重构（"也许我该换个词搜"）、综合最终答案。

### 2.3 一个完整的 ReAct 轨迹长什么样（Figure 1d，HotpotQA）

**问题**：除了 Apple Remote，还有什么设备可以控制 Apple Remote 最初被设计来交互的那个程序？

```
Thought 1: 我需要搜 Apple Remote，找到它最初被设计来交互的程序。
Act 1:     Search[Apple Remote]
Obs 1:     Apple Remote 是 2005 年 10 月推出的遥控器，最初设计用于
           Front Row media center 程序……

Thought 2: Apple Remote 最初设计用于控制 Front Row media center 程序。
           我接下来要搜 Front Row，看还有什么设备能控制它。
Act 2:     Search[Front Row]
Obs 2:     找不到 [Front Row]。相似条目：['Front Row Seat to Earth',
           'Front Row Motorsports', 'Front Row (software)', ...]

Thought 3: 找不到 Front Row，我需要搜 Front Row (software)。
Act 3:     Search[Front Row (software)]
Obs 3:     Front Row 是一个已停止更新的 media center 软件……

Thought 4: Front Row (software) 可以由 Apple Remote 或键盘功能键控制。
           所以答案是键盘功能键。
Act 4:     Finish[keyboard function keys]              ✅
```

**对照三个 baseline 在同一题上的失败：**

| 方法 | 输出 | 结果 |
|---|---|---|
| **Standard**（直接答） | "iPod" | ❌ 纯猜 |
| **CoT**（只推理） | "Apple Remote 最初设计用于与 Apple TV 交互。Apple TV 可以被 iPhone、iPad、iPod Touch 控制。所以答案是 iPhone, iPad, iPod Touch" | ❌ **幻觉**：Apple TV 这个前提就是编的 |
| **Act-only**（只行动） | Search[Apple Remote] → Search[Front Row]（失败）→ Search[Front Row (software)] → Finish[**yes**] | ❌ **有正确信息但不会综合**，因为没有 thought 去把 Obs 3 变成答案 |

> **这张图是整篇论文的精华，上课如果要举一个例子，就举这个。** 它一图说清了：CoT 死于幻觉，Act 死于不会推理，ReAct 两者互补。

### 2.4 关于格式的一个细节（容易被忽略，但很重要）

论文明确区分了两类任务的 prompt 格式：

- **推理为主的任务（HotpotQA / Fever）**：**thought 和 action 严格交替**（dense thought，每个 action 前必有 thought）
- **决策为主的任务（ALFWorld / WebShop）**：动作数量可能很多，**thought 只需要稀疏地出现在最相关的位置**，所以"**让语言模型自己决定 thought 和 action 的异步出现时机**"（asynchronous occurrence）

> 这个设计选择很关键：ReAct 不强制"每步都想"，因为在长动作序列里那样太浪费也太啰嗦。**Sparse reasoning（稀疏推理）**这个概念在第 4 节的实验里是核心卖点。

### 2.5 ReAct 的四个特性（论文自己总结的 A/B/C/D）

**A) 直观且易于设计（Intuitive and easy to design）**
写 ReAct prompt 就是让人类标注者"在自己的动作之上，把心里想的话直接打出来"。**没有 ad-hoc 的格式选择、思考设计、示例挑选。** 这是极低的工程门槛。

**B) 通用且灵活（General and flexible）**
因为 thought 空间是自由文本、出现时机也灵活，同一个范式适用于动作空间完全不同的任务：QA、事实核查、文字游戏、网页导航。

**C) 高性能且鲁棒（Performant and robust）**
只用 **1~6 个** in-context 示例就能泛化到新任务实例，稳定超过只推理或只行动的 baseline。第 4 节还证明了**对 prompt 选择鲁棒**。

**D) 与人对齐、可控（Human aligned and controllable）**
推理轨迹可读 → 人能检查推理和事实正确性。更强的是：**人可以中途编辑 thought 来纠正 agent 行为**（Figure 5，见 §5.4）。

---

## 3. 实验一：知识密集型推理任务（第 3 节精读）

### 3.1 任务设置

| 数据集 | 类型 | 说明 |
|---|---|---|
| **HotpotQA** (Yang et al. 2018) | 多跳问答 | 需要在 2 个或以上维基段落上推理 |
| **FEVER** (Thorne et al. 2018) | 事实核查 | 判定 claim 为 SUPPORTS / REFUTES / NOT ENOUGH INFO |

**关键设置**：两个任务都采用 **question-only setup**——模型**只拿到问题/claim，不给支撑段落**。要么靠自己的内部知识，要么去外部环境检索。（这个设定是为了逼出"是否需要外部工具"这个研究问题。）

### 3.2 动作空间设计（简单到令人惊讶）

作者自己设计了一个**极简的维基百科 API**，只有 3 个动作：

| 动作 | 语义 |
|---|---|
| `search[entity]` | 返回该实体维基页面的**前 5 句话**；若页面不存在，返回维基搜索引擎给的 **top-5 相似实体**建议 |
| `lookup[string]` | 返回页面中**包含该字符串的下一句**（模拟浏览器的 Ctrl+F） |
| `finish[answer]` | 结束任务并给出答案 |

> **论文特意说明这是"故意做弱"的**：这个动作空间"只能基于精确的页面名检索一小部分段落，**显著弱于最先进的词法或神经检索器**"。目的是**模拟人类如何与维基交互，并强迫模型通过显式的语言推理来检索**。
>
> 💡 **这是一个很好的课堂讨论点**：作者用一个故意弱化的工具来隔离变量，证明收益来自"推理+行动的协同"而非"强检索器"。

### 3.3 Baselines（消融设计非常干净，值得学习）

作者的做法是：**从 ReAct 轨迹里系统性地删东西**，得到各个 baseline。

| 方法 | 做法 |
|---|---|
| **Standard** | 删掉 ReAct 轨迹里的所有 thought、action、observation → 只剩 Q→A |
| **CoT** | 删掉 action 和 observation → 只剩推理（reasoning-only baseline） |
| **CoT-SC** | CoT + Self-Consistency：采样 **21 条**轨迹（decoding temperature 0.7），取多数答案 |
| **Act** | 删掉 thought → 只剩 action + observation（近似 WebGPT 的交互方式，但 WebGPT 用的是模仿学习+RL） |

**In-context 示例数量**：HotpotQA 随机取 **6 个**，FEVER 取 **3 个**，人工写成 ReAct 格式。
> 脚注 2 说明：**"我们发现更多示例不会提升性能。"**

**基座模型**：**PaLM-540B**（附录 A.1 还做了 GPT-3 的验证）。

### 3.4 两个混合策略（ReAct ⇄ CoT-SC）—— 论文最实用的工程洞察

作者观察到一个互补性：
> **ReAct 更 factual、更 grounded（事实更准）；CoT 更擅长构造推理结构，但容易幻觉。**

于是设计了两种 backoff（回退）启发式：

**A) ReAct → CoT-SC**
如果 ReAct 在给定步数内没能返回答案，就回退到 CoT-SC。
- HotpotQA 阈值设为 **7 步**，FEVER 设为 **5 步**
- 依据（脚注 3）：**在所有最终答案正确的轨迹中，用满 7 步（HotpotQA）/ 5 步（FEVER）的只占 0.84% 和 1.33%** —— 也就是说，走到这么多步基本就是走不出来了

**B) CoT-SC → ReAct**
如果 $n$ 个 CoT-SC 样本里的多数答案出现次数 **少于 $n/2$**（说明内部知识不足以自信地支撑这个任务），就回退到 ReAct。

> 💡 **这个思想的现代对应**：这本质上是**置信度驱动的工具调用路由**——模型自己有把握就不查，没把握才去查。今天的 agentic RAG、adaptive retrieval 都在做同一件事。

### 3.5 Finetuning（第 3 节末尾）

由于人工标注推理轨迹成本高，作者采用类似 **STaR (Zelikman et al. 2022)** 的 **bootstrapping** 方法：
- 用 ReAct（以及其他 baseline）生成 **3,000 条答案正确的轨迹**
- 用这些轨迹微调更小的模型（**PaLM-8B / 62B**），让它们在给定 question/claim 的条件下解码出完整轨迹（thoughts + actions + observations）
- 训练细节（附录 B.1）：batch size 64；PaLM-8B 上 ReAct/Act 训 4,000 步、Standard/CoT 训 2,000 步；PaLM-62B 上 ReAct/Act 训 4,000 步、Standard/CoT 训 1,000 步
- **观察**：ReAct 和 Act **随训练步数/数据增加持续受益**，而 Standard 和 CoT **微调后很快就退化**

### 3.6 结果（Table 1，PaLM-540B）

| Prompt Method | HotpotQA (EM) | Fever (Acc) |
|---|---|---|
| Standard | 28.7 | 57.1 |
| CoT | 29.4 | 56.3 |
| CoT-SC | 33.4 | 60.4 |
| Act | 25.7 | 58.9 |
| **ReAct** | 27.4 | 60.9 |
| **CoT-SC → ReAct** | 34.2 | **64.6** |
| **ReAct → CoT-SC** | **35.1** | 62.0 |
| *Supervised SoTA* | *67.5* | *89.5* |

**四个必须读懂的结论：**

**① ReAct 稳定优于 Act（27.4 vs 25.7；60.9 vs 58.9）**
→ 证明了**推理对于引导行动的价值**，尤其是在综合最终答案这一步（就是 Figure 1c vs 1d 的差异）。这是全文最核心的消融。

**② ReAct 在 HotpotQA 上略输给 CoT（27.4 vs 29.4），但在 FEVER 上赢（60.9 vs 56.3）**
> ⚠️ **这是诚实的负面结果，也是最容易被课堂追问的点。** 作者的解释：
> - FEVER 的 SUPPORTS/REFUTES 判定往往只差一点点信息，所以检索准确、最新的知识特别关键 → ReAct 占优
> - HotpotQA 上 ReAct 输在灵活性（见下面 Table 2 的分析）

**③ ReAct + CoT-SC 的组合是最强的 prompting 方法**
- HotpotQA 最好：**ReAct → CoT-SC (35.1)**
- FEVER 最好：**CoT-SC → ReAct (64.6)**
- Figure 2 显示：这两种组合在**任意采样数下都一致大幅超过 CoT-SC**；只用 **3-5 个样本**就能达到 CoT-SC 用 **21 个样本**的水平

**④ 所有 prompting 方法离监督 SoTA 还差很远**（27-35 vs 67.5）
→ 作者自己承认这个 gap，并认为更多人工标注数据 + 微调是出路。

### 3.7 错误分析（Table 2）—— 这一节的含金量最高

作者从 ReAct 和 CoT 各随机抽 **50 条正确 + 50 条错误**轨迹（共 200 条），**人工标注**失败模式：

| | 类型 | 定义 | ReAct | CoT |
|---|---|---|---|---|
| **Success** | True positive | 推理轨迹和事实都正确 | **94%** | 86% |
| | False positive | 幻觉的推理轨迹或事实（但答案蒙对了） | **6%** | 14% |
| **Failure** | Reasoning error | 推理轨迹错误（含陷入重复步骤出不来） | 47% | **16%** |
| | Search result error | 搜索返回空或不含有用信息 | 23% | – |
| | Hallucination | 幻觉的推理轨迹或事实 | **0%** | 56% |
| | Label ambiguity | 预测其实对，但没精确匹配标签 | 29% | 28% |

**三个关键观察（论文原文 A/B/C）：**

**A) 幻觉是 CoT 的严重问题**
CoT 的 false positive 率是 ReAct 的 2 倍多（14% vs 6%），且幻觉占 CoT 失败模式的 **56%**；**ReAct 的幻觉率是 0%**。
→ ReAct 因为接入了外部知识库，轨迹**更接地、更事实驱动、更可信**。

**B) 但结构约束是有代价的：ReAct 的推理错误率更高（47% vs 16%）**
> **交错 thought-action-observation 的结构提升了 grounding 和可信度，但也降低了表达推理步骤的灵活性。**
>
> 一个高频错误模式：**模型反复生成之前已经生成过的 thought 和 action，陷入死循环跳不出来。** 作者把它归类为"推理错误"。
> 脚注 4：怀疑这是**贪心解码（greedy decoding）**的次优所致，未来用 beam search 等更好的解码可能能缓解。

**C) 检索质量是 ReAct 的命门**
非信息性的搜索占了 **23%** 的错误——一旦搜歪了，模型很难恢复和重新组织思路。
→ 这正是"**事实性 vs 灵活性**"的权衡，也是作者提出 ReAct+CoT-SC 组合的动机。

### 3.8 Scaling 与微调（Figure 3）

在 HotpotQA 上对比 Standard/CoT/Act/ReAct × PaLM-8B/62B/540B × prompting/finetuning：

- **Prompting 时**：在 PaLM-8B/62B 上，**ReAct 是四个里最差的**——因为从少量示例里同时学会"推理"和"行动"太难了，小模型学不动
- **Finetuning 时**（仅 3,000 条样本）：**ReAct 变成四个里最好的**
  - 微调后的 **PaLM-8B ReAct 超过所有 PaLM-62B 的 prompting 方法**
  - 微调后的 **PaLM-62B ReAct 超过所有 540B 的 prompting 方法**
- **微调 Standard 或 CoT 显著差于微调 ReAct 或 Act**
  - 作者解释：**前者本质上是教模型去记忆（可能是幻觉的）知识事实，后者是教模型如何（推理并）行动去从维基获取信息——后者是一种更可泛化的知识推理技能**

> 💡 **这个结论在 2026 年回看非常有预见性**：它预告了"**训练 agent 去用工具，比训练它记住知识更划算**"这个现在已经成为共识的路线（也是 tool-use RL、agentic post-training 的理论依据）。

---

## 4. 实验二：决策任务（第 4 节精读）

这一节要回答的问题是：**ReAct 在长程、稀疏奖励的交互环境里也管用吗？**

### 4.1 ALFWorld（文字版具身家务游戏）

**环境**（Shridhar et al. 2020b）：文本版的 ALFRED 具身 benchmark，**6 类任务**（如"用台灯检查纸张"），通过文字动作（`go to coffeetable 1`, `take paper 2`, `use desklamp 1`）导航和交互。

**难度**：
- 一个任务实例可能有 **50+ 个位置**
- 专家策略也要 **50+ 步**才能解决
- 需要**规划和跟踪子目标**，还要**系统性探索**（比如挨个检查所有书桌）
- 特别的挑战：**需要判断常见家居物品可能在哪**（台灯多半在书桌、架子、梳妆台上）——这正好适合考验 LLM 的预训练常识知识

**ReAct prompt 构造**：每类任务随机标注 **3 条**轨迹，每条包含稀疏的 thought，用于 (1) 分解目标 (2) 跟踪子目标完成情况 (3) 决定下一个子目标 (4) 用常识推理物品在哪。
**鲁棒性设计**：从 3 条标注中取 2 条的排列组合，为每类任务构造 **6 套 prompt**。Act prompt 用完全相同的轨迹、只是去掉 thought → **完全公平的受控对比**。
**评测**：**134 个未见过的评测游戏**，task-specific 设置。
**Baseline**：**BUTLER**，一个用每类任务 **10⁵ 条专家轨迹**训练的模仿学习 agent。

### 4.2 WebShop（真实网购环境）

**环境**（Yao et al. 2022）：**1.18M 真实商品 + 12k 条人类指令**的在线购物网站环境。（ReAct 原文写的是 "12k"，精确值 12,087 来自 WebShop 原论文。）
- 包含大量结构化和非结构化文本（商品标题、描述、选项，从 Amazon 爬取）
- 任务：按用户指令买到对的商品（例："我想要一个带抽屉的床头柜，要镍质饰面，价格低于 $140"）
- 交互方式：搜索（`search[nightstand drawers]`）、点按钮（`color: modern-nickel-white`、`back to search`）
- 评测：**500 条测试指令**上的 average score（所选商品覆盖目标属性的百分比）和 success rate（所选商品满足全部要求的比例）

**Baselines**：IL（用 **1,012 条**人类标注轨迹训练）、IL+RL（额外用 **10,587 条**训练指令）。

### 4.3 结果

**Table 3 — ALFWorld 各任务成功率（%）**

| Method | Pick | Clean | Heat | Cool | Look | Pick 2 | **All** |
|---|---|---|---|---|---|---|---|
| Act (best of 6) | 88 | 42 | 74 | 67 | 72 | **41** | 45 |
| ReAct (avg) | 65 | 39 | 83 | 76 | 55 | 24 | 57 |
| **ReAct (best of 6)** | **92** | 58 | **96** | 86 | **78** | **41** | **71** |
| ReAct-IM (avg) | 55 | 59 | 60 | 55 | 23 | 24 | 48 |
| ReAct-IM (best of 6) | 62 | **68** | 87 | 57 | 39 | 33 | 53 |
| BUTLER_g (best of 8) | 33 | 26 | 70 | 76 | 17 | 12 | 22 |
| BUTLER (best of 8) | 46 | 39 | 74 | **100** | 22 | 24 | 37 |

- **ReAct 最佳 71% ≫ Act 最佳 45% ≫ BUTLER 37%**
- **即使是 ReAct 最差的一次试验（48%）也超过了两种方法的最佳试验**
- ReAct 对 Act 的优势在**全部 6 次受控试验中都成立**，相对增益 **33%~90%，平均 62%**
- 定性观察：**没有 thought，Act 无法正确分解目标，或者会丢失对环境当前状态的跟踪**

**Table 4 — WebShop**

| Method | Score | SR |
|---|---|---|
| Act | 62.3 | 30.1 |
| **ReAct** | **66.6** | **40.0** |
| IL | 59.9 | 29.1 |
| IL+RL | 62.4 | 28.7 |
| *Human Expert* | *82.1* | *59.6* |

- **one-shot 的 Act 就已经和 IL / IL+RL 打平**（对比一下：IL+RL 用了 10,587 条训练指令）
- **加上稀疏推理后，ReAct 绝对成功率提升 10%**
- 机制：ReAct 更容易识别和指令相关的商品与选项，**用推理去弥合"嘈杂的观察"和"动作"之间的鸿沟**（例："对于'省空间的客厅搁脚凳'，这个商品有 '39x18x18inch' 和 'blue' 选项，看起来不错"）
- ⚠️ **但离人类专家（59.6% SR）还差很远**——人类会做更多商品探索和查询重构，这对 prompting 方法仍是挑战

### 4.4 最重要的消融：ReAct vs ReAct-IM（内部推理 vs 外部反馈）

这一小节是论文对 **Inner Monologue (IM, Huang et al. 2022b)** 的直接回应，**很可能是课堂讨论重点**。

**论文的论点**：
> Inner Monologue 是第一个展示 LLM 闭环系统的工作，ReAct 建立在它之上。**但 IM 的"内心独白"仅限于对环境状态的观察，以及为了满足目标 agent 还需要完成什么。** 它不是真正的内心思考。
>
> 相比之下，**ReAct 的推理轨迹是灵活且稀疏的，允许针对不同任务诱导出多样的推理类型。**

**消融实验设计（ReAct-IM）**：用 IM 风格的**密集外部反馈**重新标注同一批专家轨迹，限制 thought 只能表达 (1) 分解当前目标 (2) 当前需要完成的子目标。
**ReAct-IM 因此缺少的能力**：(1) 判断子目标何时完成 (2) 决定下一个子目标是什么 (3) 引导 LLM 调用内部预训练知识来判断物品可能在哪。

**结果**：ReAct **71%** vs ReAct-IM **53%**（overall），**6 类任务中有 5 类 ReAct 占优**。
定性观察：ReAct-IM 经常搞不清子目标有没有完成、下一个子目标是什么（缺乏高层目标分解），也经常判断不出物品在 ALFWorld 环境中的位置（缺乏常识）。

> 💡 **这个消融的方法论值得学**：它不是和别人的系统比（那会混入无数无关变量），而是**在自己的框架内，把对方的核心限制复现出来**，从而干净地隔离出"自由灵活的内部推理"这一个变量的贡献。

---

## 5. 关键洞察补充（附录里的宝藏）

### 5.1 ReAct 能拿到**比数据集标签更新**的知识（附录 A.2, Figure 4）

作者在检查轨迹时发现：**有时 ReAct 和数据集标签不一致，是因为标签本身过时了。**

例子：问题问某酒店有多少房间，HotpotQA 标签是 **2,664**（数据集构建时的数据）。
- Standard：3,000 ❌（幻觉）
- CoT：2,885 ❌（幻觉了"Treasure Island has 2,885 rooms"）
- Act：搜到了正确页面但**没有答案就结束了** ❌（缺乏推理去引导如何交互）
- **ReAct：3,104 ✅**（**唯一拿到最新答案的**——通过真实的网页交互 + 推理）

> 这提示了一个至今仍成立的点：**benchmark 的静态标签会过时，而接入实时信息的 agent 反而会被"判错"。** 这是评估 agent 的一个根本性难题。

### 5.2 跨模型验证：GPT-3 也行（附录 A.1, Table 5）

**都是 ReAct prompting，只是换基座模型：**

| ReAct prompting | PaLM-540B | GPT-3 (text-davinci-002) |
|---|---|---|
| HotpotQA (EM，随机 500 题子集) | 29.4 | **30.8** |
| ALFWorld (SR %，134 个未见实例) | 70.9 | **78.4** |

> ⚠️ 别和 Table 1 混淆：这里的 29.4 是 **ReAct 在 500 题子集上**的成绩，恰好和 Table 1 里 **CoT 在全集上**的 29.4 数值相同，但含义完全不同。

GPT-3 **一致地超过** PaLM-540B，作者推测是因为 **GPT-3 做过人类指令跟随的微调**。
→ 结论：**ReAct prompting 在不同大模型、不同任务上都有效**，不是 PaLM 特有的现象。
（HotpotQA 上随机采样 500 个验证问题；ALFWorld 用全部 134 个未见实例，greedy decoding。）

### 5.3 人在回路的行为纠正（附录 A.3, Figure 5）—— 我最喜欢的部分

在 ALFWorld 里，一条 ReAct 轨迹因为 **Act 17 的一个幻觉 thought** 而失败。
人类**只是编辑了两个 thought**（Act 17 和 Act 23，删掉一句幻觉的话 + 加了点提示），ReAct 的行为就**彻底改变并成功完成任务**。

作者的评论非常有洞察力：
> 从人的角度看，解决这个任务**从"敲几十个动作"变成了"只改两句思考"**，开启了人机协作的新形式。
>
> **这种"即时策略编辑"对 Act 和之前的 RL 方法来说是极难做到的**——人类无法改变模型参数，而改几个动作并不会改变模型其余的行为。
>
> 这个范式也**超越了单纯的人机对话去更新目标或子目标**（指 Inner Monologue）——**编辑 ReAct 的 thought 可以修改模型的内部信念、推理风格，或者任何灵活的思考空间所支持的东西。**

> 💡 **这是 ReAct 被低估的贡献**：它把 agent 的"内部状态"变成了**人类可读、可写的自然语言**。今天所有关于 agent 可解释性、可干预性、可审计的讨论，源头都在这里。

---

## 6. 与其他方法的对比地图（第 5 节 + 课外补充）

### 6.1 论文自己的 Related Work 定位

**推理这条线：**

| 方法 | 做法 | 与 ReAct 的差别 |
|---|---|---|
| CoT (Wei+ 2022) | 输出中间推理步骤 | 孤立、固定的推理，不接外部 |
| Least-to-most (Zhou+ 2022) | 分解复杂任务 | 同上 |
| Zero-shot CoT (Kojima+ 2022) | "Let's think step by step" | 同上 |
| Self-Consistency (Wang+ 2022a) | 采样多条推理取多数 | 同上 |
| Selection-Inference (Creswell+ 2022) | 把推理拆成"选择"和"推断"两步 | 更复杂的推理架构，但仍不接外部 |
| STaR (Zelikman+ 2022) | 用模型自己生成的 rationale 微调 | ReAct 借用了这个 bootstrapping 思想做微调 |
| Faithful reasoning (Creswell & Shanahan 2022) | 三步分解，每步一个专用 LM | 同上 |
| Scratchpad (Nye+ 2021) | 微调 LM 输出中间计算步骤 | 同上 |

> **ReAct 的定位**："与这些方法相比，ReAct 做的**不只是孤立、固定的推理**，它把**模型动作和对应的观察整合进一条连贯的输入流**，使模型能更准确地推理，并处理推理之外的任务（如交互式决策）。"

**决策这条线：**

| 方法 | 做法 | 与 ReAct 的差别 |
|---|---|---|
| WebGPT (Nakano+ 2021) | LM 与浏览器交互回答 ELI5 问题 | **不显式建模思考和推理过程**，依赖昂贵的人类反馈做 RL |
| BlenderBot / Sparrow / SimpleTOD | 训练 LM 决定 API 调用 | 同样不显式建模推理，依赖昂贵数据集和人类反馈 |
| SayCan (Ahn+ 2022) | LM 预测动作，再用 affordance 模型重排 | 不做抽象推理 |
| Inner Monologue (Huang+ 2022b) | 注入环境反馈作为"内心独白" | **"内心独白"只是环境状态的复述，不是真正的内在思考**（见 §4.4） |

> **ReAct 的成本优势**："ReAct 以**便宜得多**的方式学到一个策略，因为决策过程**只需要对推理过程的语言描述**。"

### 6.2 课外补充：ReAct 在 Agent 谱系中的位置（上课可能会问）

```
          【 只推理 】                    【 只行动 】
         CoT (2022.01)                 SayCan (2022.04)
      Self-Consistency (2022.03)       WebGPT (2021.12)
              │                              │
              └──────────┬───────────────────┘
                         ▼
                 【 ReAct (2022.10) 】
              Thought → Action → Observation 循环
                         │
        ┌────────────────┼──────────────────┬─────────────────┐
        ▼                ▼                  ▼                 ▼
   Reflexion         Tree of Thoughts    Toolformer      现代 Agent 框架
   (2023.03)         (2023.05, 同作者)    (2023.02)      LangChain / AutoGPT
   加"自我反思"       把推理变成树搜索      学会何时调工具    OpenAI function calling
   的长期记忆        （不只是链）          （训练而非prompt）  Claude tool use / MCP
```

**几个重要的后继关系，值得记住：**

| 后继工作 | 它补上了 ReAct 的什么短板 |
|---|---|
| **Reflexion** (Shinn+ 2023) | ReAct 失败了就失败了，**没有跨 episode 的学习**。Reflexion 加了一个"反思"步骤，把失败经验写进长期记忆，下次重试时读取 |
| **Tree of Thoughts** (Yao+ 2023，同一作者 Shunyu Yao) | ReAct 是**贪心的单线程链**，走错路就出不来（正好对应 Table 2 里 47% 的推理错误）。ToT 引入**搜索和回溯** |
| **Toolformer** (Schick+ 2023) | ReAct 靠 prompt 教模型用工具；Toolformer 用**自监督训练**把工具调用能力烧进模型权重 |
| **Function calling / Tool use API** | 把 ReAct 的 `Action: Search[x]` 从**自由文本解析**变成**结构化 JSON 输出**，大幅提升可靠性——这是把 ReAct 从研究 prompt 变成生产系统的关键工程化一步 |
| **MCP (Model Context Protocol)** | 标准化了"环境/工具"这一侧，让 ReAct 循环里的 Action 空间可以即插即用 |

> **一个很好的课堂总结句**：ReAct 定义了 agent 的**基本循环（loop）**；后续所有工作要么在**优化循环内部的推理**（ToT、self-consistency），要么在**加记忆**（Reflexion），要么在**标准化动作接口**（function calling、MCP），要么在**把能力从 prompt 移到权重里**（Toolformer、agentic RL）。

---

## 7. 局限性与批判性分析（准备被老师追问）

### 7.1 论文自己承认的（第 6 节 Conclusion + Ethics）

1. **动作空间大的复杂任务需要更多示例，容易超出 in-context learning 的输入长度限制**
2. **prompting 效果离监督 SoTA 差很远**（27-35 vs 67.5 EM）
3. **需要更多高质量人类标注**才能进一步提升
4. **伦理风险**：把 LLM 接上外部环境的动作空间有危险（查看不当或私密信息、执行有害动作）。作者的缓解措施是**把交互限制在特定网站**（维基、WebShop），且**动作空间里不含危险动作**（模型在 WebShop 上不能真买东西，也不能编辑维基）

### 7.2 我自己补充的批判点（课堂可以主动提出，加分项）

**① 推理错误率 47% 是个大问题，而且论文的解释不够充分**
作者把它归因于贪心解码，但"反复生成相同 thought 陷入死循环"更可能是**缺乏状态去重机制和回溯机制**的结构性问题。ToT 和 Reflexion 后来正是从这里切入的。

**② HotpotQA 上 ReAct 输给 CoT，这个负面结果被组合方法"掩盖"了**
论文很快转向 ReAct+CoT-SC 的组合，但一个更诚实的读法是：**在检索器很弱、且问题在模型参数知识覆盖范围内时，去检索反而是负担。** 什么时候该用工具，本身是个未解决的问题。

**③ 评测的静态标签问题（§5.1）会系统性低估 ReAct**
如果 HotpotQA 里有相当比例的题标签已过时，那么 27.4 这个 EM 是被低估的。论文只给了定性例子，**没有量化有多少题受影响**——这是一个可以追问的实验空白。

**④ Best-of-6 / Best-of-8 的报告方式值得警惕**
ALFWorld 的 71% 是 **best of 6**，而 average 只有 **57%**。虽然作者很诚实地两个都报了，且 avg 也超过 Act 的 best，但**引言和摘要里的"34% 绝对提升"用的是 best vs best**。看 agent 论文时要养成看方差的习惯。

**⑤ 成本没有讨论**
ReAct 的轨迹比 CoT 长得多（多轮 thought + action + observation），**token 成本和延迟显著更高**，论文完全没有分析。在 2026 年的实际部署里，这是选型的头等考量。

**⑥ Thought 是否真的"因果地"影响了行动？**
这是个更深的认识论问题：模型输出的 thought 可能只是**事后合理化（post-hoc rationalization）**，而非真正的决策依据。后来关于 CoT faithfulness 的研究（Turpin et al. 2023 等）表明推理轨迹常常不忠实于模型的真实计算过程。**ReAct 的可解释性主张，在这个意义上需要打折扣。**

---

## 8. 复习自测题（自己先答，再回去翻）

**基础层**
1. 用一个公式写出 ReAct 对 agent 动作空间的改动，并解释 thought 这种动作的特殊之处。
2. ReAct 在 HotpotQA 上用的三个动作是什么？作者为什么故意设计一个"弱"的检索接口？
3. Standard / CoT / CoT-SC / Act 这四个 baseline 分别是从 ReAct 轨迹里删掉了什么？

**理解层**
4. Figure 1 的 Apple Remote 例子里，CoT 和 Act 分别是怎么失败的？失败的根因有什么本质不同？
5. Table 2 显示 ReAct 的幻觉率是 0% 但推理错误率是 47%（CoT 是 56% 和 16%）。用一句话概括这个 trade-off 的来源。
6. 为什么 prompting 时 ReAct 在小模型上最差，但 finetuning 后在小模型上最好？作者给的解释是什么？
7. ReAct-IM 消融想证明什么？它相比 ReAct 缺了哪三种 thought？

**应用/批判层**
8. 如果让你改进 ReAct 来降低那 47% 的推理错误，你会怎么做？（提示：往 ToT / Reflexion 方向想）
9. ReAct → CoT-SC 和 CoT-SC → ReAct 两种回退策略的触发条件分别是什么？这背后共同的思想是什么？
10. Figure 5 的"人类编辑 thought"为什么是 ReAct 独有的能力，而 RL agent 做不到？
11. 举出至少三个现代 agent 系统/技术，说明它们分别继承或改进了 ReAct 的哪一部分。

---

## 9. 5 分钟口头汇报提纲（如果需要在课上讲）

1. **问题**（30 秒）：LLM 的推理（CoT）和行动（tool use）当时是两条平行线。只推理 → 幻觉、错误传播；只行动 → 不会规划、不会跟踪状态。
2. **洞察**（30 秒）：人类做复杂任务时两者是交织的（做饭例子）。所以——把"思考"当成一种**不改变环境的动作**，塞进同一个动作空间。
3. **方法**（1 分钟）：$\hat{\mathcal{A}} = \mathcal{A} \cup \mathcal{L}$。Thought→Action→Observation 循环。Few-shot prompt，1-6 个示例，不改模型。走一遍 Apple Remote 的例子。
4. **实验**（1.5 分钟）：4 个 benchmark。知识任务上 ReAct 稳超 Act，和 CoT 互补（组合最优 35.1 / 64.6）；决策任务上碾压——ALFWorld 71% vs BUTLER 37%（后者用了 10⁵ 条专家轨迹），WebShop 绝对 +10% SR（vs 用了上万条训练数据的 IL+RL）。核心卖点：**one/two-shot 打赢用海量数据训练的模仿学习和 RL**。
5. **最有意思的发现**（1 分钟）：ReAct 幻觉率 0% vs CoT 56%；ReAct 能拿到比数据集标签更新的答案；**人类改两句 thought 就能救回失败的轨迹**。
6. **局限与影响**（30 秒）：推理错误率高（易死循环）、离监督 SoTA 远、成本高。但它定义了今天所有 agent 框架的基本循环，是 Reflexion / ToT / function calling / MCP 的共同起点。

---

## 10. 核心数字速查表（考前扫一眼）

| 项目 | 数值 |
|---|---|
| 会议 / 年份 | ICLR 2023 |
| 基座模型 | PaLM-540B（另验证 GPT-3 text-davinci-002） |
| In-context 示例数 | HotpotQA 6 / FEVER 3 / ALFWorld 2（从 3 条里排列）/ WebShop 1 |
| HotpotQA EM：CoT / ReAct / 最优组合 / 监督 SoTA | 29.4 / 27.4 / **35.1** / 67.5 |
| FEVER Acc：CoT / ReAct / 最优组合 / 监督 SoTA | 56.3 / 60.9 / **64.6** / 89.5 |
| CoT-SC 采样数 / 温度 | 21 / 0.7 |
| 回退阈值 | HotpotQA 7 步，FEVER 5 步 |
| 微调数据量 / 模型 | 3,000 条 bootstrap 轨迹 / PaLM-8B、62B |
| ALFWorld：ReAct best / avg，Act best，BUTLER | 71% / 57%，45%，37% |
| ALFWorld ReAct 对 Act 相对增益 | 33%~90%，平均 62% |
| ALFWorld 评测实例数 / BUTLER 训练量 | 134 个未见实例 / 每类任务 10⁵ 条专家轨迹 |
| WebShop：ReAct Score/SR，Act，IL+RL，人类专家 | 66.6/40.0，62.3/30.1，62.4/28.7，82.1/59.6 |
| 摘要里的两个"绝对提升" | ALFWorld +34%，WebShop +10% |
| 幻觉率：ReAct vs CoT（失败模式占比） | 0% vs 56% |
| 推理错误率：ReAct vs CoT | 47% vs 16% |
| GPT-3 vs PaLM-540B（均为 ReAct）：HotpotQA / ALFWorld | 30.8 vs 29.4 / 78.4 vs 70.9 |

---

*笔记基于 arXiv:2210.03629v3（2023-03-10 版）全文正文 + 附录 A、B 整理。第 6.2 节的谱系图和第 7.2 节的批判分析为笔记作者补充，非论文原文内容。*
