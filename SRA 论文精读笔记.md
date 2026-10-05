# SRA 论文精读笔记

> **Skill Retrieval Augmentation for Agentic AI**
> Weihang Su\*, Jianming Long, Qingyao Ai†, Qiaozhi He, Yichen Tang, Changyue Wang, Yiteng Tu, Yingbo Wang, Yiqun Liu
> 清华大学计算机系 · ByteDance（\* 字节实习期间完成，† 通讯作者）
> `arXiv:2604.24594` · v1 2026-04-27 / v2 2026-05-21 / **v3 2026-06-07**（本笔记据 v3）
> 代码与数据：github.com/oneal2000/SR-Agents · huggingface.co/datasets/WeihangSu/SRA-Bench
> 课程：Week 03 Skillcraft 课堂提及 · 整理于 2026-10-05

> ⚠️ **venue：无。** arXiv 页面没有 journal-ref、没有 Comments，论文本身也未写发表场所。引用时按 preprint 处理。
> ⚠️ **这篇没有 Limitations 一节**，也没有 threats to validity、伦理声明或 broader impact。见 §7。

---

## 0. 一句话总括

**把 RAG 搬到 skill 上：不再把所有 skill 枚举进上下文，而是从一个 26,262 条的语料库里按需检索——然后作者做了一件更重要的事，他们把这条流水线拆成三段分别评测，发现瓶颈根本不在检索。**

核心贡献不是"检索 skill"（Voyager 2023 就在用 embedding 检索技能库），而是：

> **把「检索到了」和「用对了」分开度量，并证明后者才是卡住的地方。**

🔑 和你已读的三篇的关系：

| | 关心什么 |
| --- | --- |
| **Voyager** | 怎么**造**和**存** skill |
| **Generative Agents** | 怎么**写入和检索经历** |
| **ReAct** | 单次任务里怎么交错推理和行动 |
| **SRA** | **库大到放不进上下文时，怎么在正确的时刻取出正确的那一个** |

⚠️ **但摘要对自己的发现做了过度概括**，而正文的表格并不完全支持。见 §7.1——**这是读这篇时最该小心的一处。**

---

## 1. 动机与定位

开篇的论证和 Week 03 讲义完全一致：

> *"In existing agent systems, the dominant strategy for incorporating skills is to explicitly enumerate available skills within the context window. However, this strategy fails to scale: as skill corpora expand, **context budgets are consumed rapidly, and the agent becomes markedly less accurate in identifying the right skill**."*

**两个代价：token 预算和识别准确率。** 正是讲义 `κ` 和 `p` 的那两项。

规模依据（§1）：

> *"as of **April 26, 2026**, platforms such as SkillsMP host **more than one million** distinct skills."*

### 它和 RAG 的区别（§1，值得直接引）

> *"SRA is closely related to Retrieval-Augmented Generation (RAG), but **it is not simply RAG with a different retrieval target**. In classical knowledge-centric RAG, retrieved items are primarily **declarative evidence** used to ground generation. In contrast, SRA retrieves **executable capabilities** that augment the agent's functional competence."*

↔ 这就是今天讲义的 **knowing-that vs knowing-how**，换成了检索系统的语言。

结尾那句对仗写得很好（§8）：

> *"if Retrieval-Augmented Generation made **external knowledge** a central object of study for language models, we believe Skill Retrieval Augmentation can help make **external capabilities** a central object of study for agent systems."*

---

## 2. 方法精读

### 2.1 SRA 的形式化（§2.2）

> *"Given a user query q and a large external skill corpus C, the objective of SRA is to augment an agent with relevant external capabilities retrieved from a large skill corpus **on demand**, rather than relying on a pre-exposed, fixed set of skills enumerated directly in the context. We formalize this process as a **three-stage pipeline**."*

```
skill 单元：   sᵢ = (nᵢ, rᵢ, cᵢ, πᵢ)     名称、描述、内容、可执行载荷
语料库：       C = {s₁, …, s_N}

① Skill Retrieval      L_k = R(q, C) = [s⁽¹⁾,…,s⁽ᵏ⁾],  k ≪ N
② Skill Incorporation  S̃  = G(q, L_k; M)
③ Skill Application    Â  = F(q, S̃; M)
```

🔑 **三段拆分本身就是这篇最大的方法贡献。** 以前的评测只看最终任务分数，**检索失败和用错混在一个数字里**。拆开之后才能问："检索明明成功了，为什么最终还是错？"

⚠️ 术语漂移：第三段在摘要和 §1 里叫 **end-task execution**，在 §2.2 和附录里叫 **skill application**。

### 2.2 SRA-Bench 的构造

| | |
| --- | --- |
| 测试实例 | **5,400** |
| 人工构造的 gold skill | **636** |
| 干扰 skill（爬自 GitHub / Skills.sh / Hugging Face Hub） | **25,626** |
| 语料库总量 | **26,262**，其中 gold 占 **2.4%** |

**六个来源数据集：**

| 数据集 | 能力类型 | 实例数 | skill 数 | 映射 | 评测 |
| --- | --- | --- | --- | --- | --- |
| TheoremQA | 定理应用 | **747** | **320** | 单 | 规则 |
| LogicBench | 逻辑推理模式 | **760** | **19** | 单 | 规则 |
| ToolQA | 工具使用流程 | **1,430** | **14** | 单 | 规则 |
| MedCalc-Bench | 医学计算器 | **1,100** | **55** | 单 | 规则 |
| CHAMP | 数学概念 | **223** | **89** | 多 | 规则 |
| BigCodeBench | 软件库 | **1,140** | **139** | 多 | **执行** |
| **合计** | | **5,400** | **636** | | |

**gold skill 怎么来的：** *"LLM drafting followed by expert revision."* 三条原则：*"First, generality… Second, correctness… Third, **leakage control**."*

格式：*"standardized Markdown artifacts with a skill name, a short description, and procedural content that describes **what the capability is, when it applies, how it should be used, and which common pitfalls to avoid**… we additionally attach runnable resources such as Python implementations of medical calculators."*

🔑 **注意那四件事：是什么、何时适用、怎么用、常见坑。** 和今天讲义的三段式 description（做什么 / 何时用 / 何时不用）几乎一一对应，只是把排除项换成了"常见坑"。

⚠️ **起草用的 LLM 没有点名；没有标注者人数、资质，也没有任何标注一致性（IAA）指标。**

### 2.3 五种策略（§4.2）

| 策略 | 做什么 |
| --- | --- |
| **LLM Direct** | 不给任何 skill |
| **Oracle Skill** | 直接给 gold skill（上界） |
| **Full-Skill Injection** | BM25 **top-1** 直接注入 |
| **LLM Selection** | 给 **top-50** 的元数据，让模型挑 **1** 个 |
| **Progressive Disclosure** | 给 top-50 目录，模型用 `LOAD_SKILL` 自取，**最多 10 轮** |

**模型：** Qwen3-4B / 32B / 235B-A22B · Llama-3.1-8B-Instruct / 3.3-70B-Instruct · Mistral-Small-3.1-24B-Instruct-2503；RQ5/RQ6 另加 **GLM-5.1** 和 **GPT-5.4**。
**统一配置：** *"All models are served with a **128K-token** context window and sampling **temperature 0.7**."*

---

## 3. 实验一：端任务性能（Table 2）

各模型的**平均分**：

| 模型 | LLM Direct | Oracle | Full-Inj | LLM Selection | Prog. Disclosure |
| --- | --- | --- | --- | --- | --- |
| Llama-3.1-8B | 29.8 | **44.5** | 32.7 | 37.0 | 36.3 |
| Llama-3.3-70B | 47.8 | **64.4** | 52.7 | 59.2 | 48.5 |
| Mistral-24B | 43.4 | **63.2** | 48.5 | 56.6 | 46.7 |
| Qwen3-235B | 53.3 | **67.5** | 56.2 | 62.8 | 59.9 |
| Qwen3-32B | 50.8 | **67.2** | 54.3 | 62.4 | 55.3 |
| Qwen3-4B | 38.8 | **61.6** | 45.5 | 53.3 | 43.2 |

**Oracle 相对 LLM Direct 的增益：** Llama-8B **+14.7pp** · Llama-70B **+16.6** · Mistral-24B **+19.8** · Qwen3-235B **+14.2** · Qwen3-32B **+16.4** · Qwen3-4B **+22.8**

🔑 **Oracle 这一列证明了「给对 skill 确实有用」——而且模型越小增益越大**（Qwen3-4B +22.8pp vs Qwen3-235B +14.2pp）。这正是今天讲义 `g` 的含义：**模型自己越不会，skill 的能力增益越大。**

### 🔥 ⚠️ 但 Progressive Disclosure 输了，而且是全输

| | LLM Selection | Progressive Disclosure | 差 |
| --- | --- | --- | --- |
| Llama-3.1-8B | **37.0** | 36.3 | −0.7 |
| Llama-3.3-70B | **59.2** | 48.5 | **−10.7** |
| Mistral-24B | **56.6** | 46.7 | **−9.9** |
| Qwen3-235B | **62.8** | 59.9 | −2.9 |
| Qwen3-32B | **62.4** | 55.3 | **−7.1** |
| Qwen3-4B | **53.3** | 43.2 | **−10.1** |

**六个模型，LLM Selection 六比零全胜。** 而且 Llama-3.3-70B 上 Progressive Disclosure（48.5）**只比完全不给 skill（47.8）好 0.7pp**。

论文自己的判词（§5.1）：

> *"Progressive Disclosure **exhibits a much less stable pattern**… its gains are **inconsistent**, and it **rarely matches** the strongest selection-based configurations."*

↔ **这和 Week 03 讲义直接冲突。** 讲义把渐进披露称为 *"the load-bearing idea of the day"*（p.19），而这篇的实测说：**在 26,262 条的真实规模上，一次性让模型从 50 条元数据里挑一个，比让它多轮自取更好。**

🔑 我的解读（论文没说）：**渐进披露省的是 κ，但多轮自取把"该不该再取一个"这个判断交给了模型——而这篇后面证明的恰恰是模型做不好这个判断。** 省下的 κ 被糟糕的决策吃掉了。

⚠️ 不过别推论过头：这测的是**一次性检索场景**（给定 query 取 skill），不是今晚那种**边做边按需读 L3 文件**的场景。两者形态不同。

---

## 4. 实验二：检索（Table 3 / 4）

**Recall@1 的跨数据集差异极大：**

| 方法 | TheoremQA | LogicBench | ToolQA | CHAMP | MedCalc | BigCode |
| --- | --- | --- | --- | --- | --- | --- |
| BM25 | 57.2 | **12.0** | **7.0** | 13.2 | 29.3 | 23.6 |
| BGE | 66.8 | 4.1 | 32.2 | 9.8 | 41.4 | 20.7 |
| Qwen3-32B 重排 | **77.4** | **31.4** | 43.7 | 22.3 | **91.2** | **28.2** |
| Qwen3-235B 重排 | 75.4 | 30.9 | **56.4** | 22.1 | **92.3** | 27.2 |

🔑 **两个极端值得记：**

- **MedCalc 上 LLM 重排把 Recall@1 从 29.3 拉到 92.3** —— 因为医学计算器的名字高度可辨识，一经重排几乎不会错。
- **CHAMP 上谁都不行**（最好 22.5）——数学概念是多标签、抽象、且概念名和题面词汇重叠少。

**检索难度不是均匀的，而且和领域强相关。** 做自己的技能库时，这意味着**同一套检索配置在不同领域会给出完全不同的表现**。

> **"reranking quality is not strictly monotonic with model scale."**（§5.3）—— Qwen3-32B 在四个数据集上超过 235B。

---

## 5. 🔥 实验三：加载行为（这篇真正的发现）

### 5.1 加载率本身就离谱（Table 6）

**skill loading rate 的定义（Table 6 caption，全文唯一定义）：**

> *"Skill loading rate measures whether the agent **successfully incorporates at least one valid skill** before producing the final answer. Overall is computed over all 5,400 instances, rather than by averaging dataset-level rates."*

| 模型 | TheoremQA | LogicBench | ToolQA | CHAMP | MedCalc | BigCode | **Overall** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-4B | 15.5 | 55.0 | 2.4 | 13.5 | 33.4 | 14.8 | **21.0** |
| Llama-8B | 97.9 | **99.7** | 2.9 | 86.5 | 97.8 | 96.0 | **72.1** |
| Mistral-24B | 45.1 | 38.0 | 29.6 | 22.9 | 32.1 | 6.4 | **28.3** |
| Qwen3-32B | 24.9 | 45.9 | 0.6 | 1.8 | 41.3 | 7.2 | **20.1** |
| Llama-70B | 31.7 | 32.6 | 6.9 | 1.8 | 0.9 | **0.0** | **11.1** |
| Qwen3-235B | 77.2 | 87.5 | 1.5 | 15.7 | 56.4 | 88.2 | **54.1** |
| GLM-5.1 | 55.3 | 25.7 | 7.8 | 25.6 | 86.5 | 27.5 | **37.8** |
| GPT-5.4 | 6.8 | 0.4 | 38.7 | 15.7 | 74.7 | 19.5 | **31.2** |

**同一个语料库、同一个检索器，整体加载率从 11.1% 到 72.1%。** 单格最低 **0.0%**（Llama-70B / BigCodeBench），最高 **99.7%**（Llama-8B / LogicBench）。

> *"with **no monotonic trend that larger models behave more rationally or robustly**."*（§1）

🔑 **这不是"大模型更会判断"的问题，是根本没有一致策略。** Llama-8B 几乎见什么加载什么（72.1%），Llama-70B 几乎不加载（11.1%）——**同一个家族，差 61 个百分点。**

### 5.2 相关性意识（Table 7）：检索到 gold 会不会更倾向加载？

| 模型 | gold 在 top-50 | gold **不在** | 差 |
| --- | --- | --- | --- |
| Qwen3-4B | 21.8 | 16.9 | +4.9 |
| Llama-8B | 73.7 | 64.1 | +9.6 |
| Mistral-24B | 30.4 | 17.3 | +13.1 |
| Qwen3-32B | 21.2 | 14.3 | +6.9 |
| **Llama-70B** | 10.4 | 14.5 | **−4.2** |
| Qwen3-235B | 57.8 | 35.3 | **+22.4** |
| **GLM-5.1** | 43.5 | 8.2 | **+35.4** |
| **GPT-5.4** | 36.6 | 3.6 | **+33.0** |

论文给这个现象起了名字：

> **"This reveals a clear form of *skill-loading hallucination*: rather than first determining whether the retrieved candidates contain a genuinely relevant capability, the model often proceeds to load some retrieved skill anyway."**（§5.5）

但它同时承认前沿模型是例外：

> *"frontier models such as GLM-5.1 and GPT-5.4 show **much sharper separation**… their advantage does not come from indiscriminately loading more skills overall, but from being **more selective**: they are more willing to load when a relevant skill is available, and much less willing to do so when it is not."*

⭐ **我从表里读出来的（论文没明说）：** 推导可得 **4,520 / 5,400 = 83.7%** 的实例 gold 在 BM25 top-50 内，**880 条（16.3%）不在**。

### 5.3 ⭐⭐ 需求意识（Table 8）：这才是全篇最硬的发现

**做法很聪明：** 按同一个模型**不给 skill 时能不能做对**把实例分两组，然后比加载率。而且——

> *"To isolate the effect of need awareness from retrieval availability, this analysis is **restricted to instances where a gold skill appears among the top-50**."*（§5.6）

**也就是说：两组都确保"有相关 skill 可用"，唯一的差别是「这题我自己会不会」。**

| 模型 | 自己会 · 加载率 | 自己不会 · 加载率 | **Δ** |
| --- | --- | --- | --- |
| Qwen3-4B | 23.6 | 20.8 | **−2.8** |
| Llama-8B | 84.5 | 69.4 | **−15.1** |
| Mistral-24B | 28.0 | 32.1 | +4.1 |
| Qwen3-32B | 21.4 | 21.0 | −0.4 |
| Llama-70B | 10.7 | 10.1 | −0.6 |
| Qwen3-235B | 59.5 | 56.0 | −3.5 |
| GLM-5.1 | 45.0 | 41.5 | −3.4 |
| GPT-5.4 | 34.4 | 40.2 | +5.8 |
| **合计** | **36.9** | **36.9** | **+0.1** |

> 🔥 **总体加载率 36.9% vs 36.9%。差 0.1 个百分点。**
> **八个模型里五个是负的**——也就是说，**它们在自己已经会做的题上反而更爱加载 skill。**

> *"**The results reveal a striking absence of need awareness.** … Even when a task demonstrably exceeds the model's native competence, the agent is generally **no more likely** to load a skill than when the task is already within reach of its parametric knowledge. This pattern indicates that skill loading is **not functioning as a targeted compensatory mechanism** for missing capability, but is instead triggered in a **largely indiscriminate** manner."*（§5.6）

### ↔ 这对今天学的加载规则意味着什么

讲义给的是：

```
VoL(s) = p_s · g_s − κ(c_s)
```

**这篇测出来的是：模型几乎不看 g。** 需不需要、能不能自己做，对加载决策的影响是 **0.1pp**。

🔑 所以准确的说法是：

> **加载规则是一个规范性模型——它描述的是「应该怎么加载」，不是「模型实际怎么加载」。**

讲义自己其实说了（*"a teaching model"*），但这篇给了它一个实证的下界：**在真实规模的库上，当前模型离这个规范有多远。**

**而这反过来提高了 description 的重要性**，不是降低——因为如果模型自己判断不了"需不需要"，**那个判断就必须被你写进那一行字里**。排除项不是锦上添花，是在补模型缺的那块。

---

## 6. ⭐ 读表发现的三条（论文没说）

**① Oracle 和最佳实用方案之间还有 4–7pp 的缺口。**

```
Qwen3-32B：   Oracle 67.2  vs  最佳实用（LLM Selection）62.4   →  差 4.8pp
Qwen3-4B：    Oracle 61.6  vs  53.3                          →  差 8.3pp
Llama-3.3-70B：Oracle 64.4  vs  59.2                          →  差 5.2pp
```

**检索+选择拿到了大部分增益，但没拿满。** 而按 §5 的分析，剩下那几个点主要卡在「加载决策」上，不在检索。

**② 模型越小，Oracle 增益越大，但实用方案的损失也越大。**

```
Qwen3-4B：   Oracle +22.8pp，实用方案只拿到 +14.5pp   →  兑现率 64%
Qwen3-235B： Oracle +14.2pp，实用方案拿到 +9.5pp      →  兑现率 67%
```

小模型最需要 skill，**也最不会用 skill**。

**③ 加载率和最终成绩不相关。** Llama-8B 加载率 **72.1%**（最高），平均分 **37.0**（最低档）；Llama-70B 加载率 **11.1%**（最低），平均分 **59.2**。**加载多少和做得好不好是两回事。**

---

## 7. ⚠️ 论文内部的不一致

**1. 🔥 摘要对「相关性意识」做了过度概括，而 Table 7 不支持。**

摘要说：*"agents tend to load skills at similar rates, **regardless of whether a gold skill is retrieved** or whether the task actually requires external capabilities."*

但 Table 7 里 **GLM-5.1 +35.4pp、GPT-5.4 +33.0pp、Qwen3-235B +22.4pp** —— 这三个明显有相关性意识，而且 §5.5 自己写了 *"much sharper separation"*。

> 🔑 **真正站得住的是后半句（need-awareness，Δ=+0.1pp），前半句对前沿模型不成立。**
> 摘要把两个强度完全不同的发现并列了。**引用这篇时该只引后半句。**

**2. Oracle 上界被突破了一次。** Table 2，Qwen3-235B / TheoremQA：**Oracle 65.9 < Progressive Disclosure 68.1**（而且 68.1 被加粗成最佳）。全表唯一一处，**论文从未提及**。§5.1 的措辞留了余地：*"Oracle Skill consistently outperforms LLM Direct across **essentially** all model-benchmark combinations."*

**3. 对 Progressive Disclosure 的评价自相矛盾。** §5.1 说它 *"gains are inconsistent, and it rarely matches the strongest selection-based configurations"*；但 Figure 2 caption 和 §5.2.1 说它 *"remains **more robust** across models"*。

**4. Table 8 的 Overall「36.9 vs 36.9, Δ=+0.1」是四舍五入产物**（真值约 36.90 vs 36.94，Δ≈+0.04）。结论不受影响，但那个 +0.1 不该被当精确值引。

**5. 做了配对 t 检验（Table 2 的 ∗），却没说跑了几次、什么种子、方差多少**——而且温度是 **0.7**，不是 0。

**6. 「Gold Load Rate」（Table 8 的列）全文没有定义。**

**7. 附录 A.3.3 有「Example 2」却没有「Example 1」**（v1 和 v3 都是）。

**8. 动机和证据之间有缺口。** 整篇以"上下文预算被迅速耗尽"立论，**却从未测过 token 数、延迟或成本**——而且所有实验都在 128K 窗口内跑得下。

---

## 8. 在 agent 谱系里的位置

| 论文 | 管哪一层 | 核心问题 | 有无 verifier / ground truth |
| --- | --- | --- | --- |
| **ReAct** | 单 episode 内 | 推理和行动怎么交错 | 任务成败 ✅ |
| **Generative Agents** | episodic → semantic | 积累的经历怎么写入和检索 | ❌ 只能主张 believability |
| **Voyager** | procedural | 怎么**造**和**存**技能 | 环境说了算 ✅ |
| **SRA** | procedural 的**取用侧** | **库大到放不下时怎么取对、用对** | 规则匹配 + 单元测试 ✅ |

### 它自己怎么划界（§6.2，直接引用）

> *"Pioneering systems like **Voyager [54]** demonstrate the value of maintaining an ever-growing skill corpus of executable programs for embodied lifelong learning… While these works underscore the utility of reusable skill abstractions, **their primary focus remains on skill acquisition, code synthesis, or ecosystem analysis**. SRA departs from this focus by addressing the critical bottleneck of **scalability**: rather than investigating how to create or store skills, we tackle the challenge of **retrieval-time access**."*

🔑 **Voyager 的库规模论文没给；SRA 直接在 26,262 条上测。** 这是两篇最实质的差别——Voyager 证明了"库能让 agent 变强"，SRA 问的是"库变成一百万条之后还成立吗"。

> 对照：Voyager 的 top-5 检索准确率是 **96.5%**（309 样本），而 SRA 在 26,262 条上，BM25 的 Recall@1 在 LogicBench 上只有 **12.0%**。**规模变了，问题也变了。**

### ↔ 与 Week 03 的对照

| 讲义 | SRA 的实测 |
| --- | --- |
| 小库把所有描述放进上下文让模型选；大库用 embedding | **交叉点在哪，讲义没说；SRA 测的是大库那一侧** |
| `VoL = p·g − κ`，加载规则 | **规范性的；模型实际不看 g（Δ=+0.1pp）** |
| 渐进披露是"the load-bearing idea" | **六个模型上全不如一次性 LLM Selection** |
| description 是最高杠杆的一行 | **更重要了**——模型自己判断不了需求，判断必须写进描述 |
| 市场 46% 重名、36.8% 有缺陷 | **SRA 的干扰集就是从同样的市场爬的**（GitHub / Skills.sh / HF） |

---

## 9. 批判性分析

### 9.1 论文自己承认的

**没有 Limitations 一节。** "limitation" 全文出现两次，都不是在说自己：

- §5.6 *"this points to a deeper limitation of **today's SR-Agents**"*
- §6.1 *"SRA operates at their intersection while systematically addressing **their respective limitations**"*

§7 的《Toward a Research Agenda》是替代品，四个方向：**结构化技能库** · **技能质量控制与演化** · **从语义匹配到效用感知的检索** · **参数化技能增强**。

其中第二条说得很准：

> *"the retrieved unit in SRA is **not merely textual evidence but an actionable capability package** whose errors may directly mislead downstream reasoning and execution."*

### 9.2 我自己补的

**① 🔥 最该做的那个实验没做：从来没告诉模型「你可以不加载」。**

全篇的发现是"模型判断不了该不该加载"，但**没有任何 prompt 层的干预实验**——没有"以上都不相关"选项、没有明确允许拒绝、没有对加载决策做任何提示工程消融。

**这是一个单变量、成本极低、而且直接检验核心主张的实验。** 如果加一句 *"If none of the retrieved skills is relevant, answer without loading any"* 就能把 Δ 从 +0.1pp 拉上去，那结论就从"模型缺乏这个能力"变成"没人要求它这么做"——**两个结论的工程含义天差地别。**

↔ 今天讲义说 description 要写"何时**不**用"。**这篇测的全是没有排除项的世界。**

**② Progressive Disclosure 的实现可能不公平，而论文没讨论这个混淆。**

它的提示词里有一句劝说性的话：*"these often contain critical details that general knowledge may miss."* ——**这是在推模型去加载**。而 Progressive Disclosure 恰好是加载决策最多的那个策略（最多 10 轮，每轮都要决定）。

**一个劝人多加载的提示词 × 一个本来就不会判断该不该加载的模型 = 它表现最差，可能有一部分是实现造成的。**

**③ 温度 0.7 + 配对 t 检验 + 不报运行次数，是一个统计上的硬伤。**

在随机解码下做显著性检验，却不说跑几次、不给方差，**读者无法判断 Table 2 里那些 ∗ 有多少是真的**。而这不是小问题——很多格子的差距只有 1–3 个百分点。

**④ gold skill 由 LLM 起草，而评测对象也是 LLM，存在风格同源的风险。**

*"LLM drafting followed by expert revision"*，但**起草模型没点名**，也没有标注一致性。如果 gold skill 的写法恰好贴近某个模型家族的偏好，Oracle 那一列就不是纯粹的上界。论文的"leakage control"原则只防内容泄漏，**不防风格同源**。

**⑤ 值得做的复现实验：把加载决策和应用解耦来测。**

当前的 loading rate 把"决定加载"和"成功纳入"混在一起（定义是 *successfully incorporates at least one valid skill*）。
**分开测：给模型 top-50，只问一个是非题「这里面有你需要的吗」，不让它执行任务。** 对照它实际的加载行为。
如果判断题答得好而实际行为不一致，**那瓶颈在流程设计；如果判断题本身就答不好，那才是能力问题。** 这篇把两者混着测，所以它的结论比它能支持的要强一点。

---

## 10. 复习自测题

1. SRA 的三段流水线分别叫什么？第三段有两个名字，分别出现在哪里？
2. SRA-Bench 的三个规模数字是多少？gold 占语料库的百分之几？
3. 干扰 skill 是从哪三个平台爬的？
4. skill loading rate 的定义是什么？它出现在论文的哪个位置（正文还是表注）？
5. Table 6 里整体加载率最高和最低的模型分别是谁，各是多少？单格的极值呢？
6. Table 8 的分组依据是什么？为什么要限制在"gold 在 top-50"的实例上？
7. Table 8 的总体 Δ 是多少？八个模型里几个是负的？负得最多的是谁？
8. 摘要那句关于 relevance-awareness 的话，被哪三个模型的数据推翻了？各是多少 pp？
9. Progressive Disclosure 和 LLM Selection 在六个模型上的胜负是几比几？差距最大的是哪个模型？
10. MedCalc 上 LLM 重排把 Recall@1 从多少拉到了多少？为什么这个数据集特别吃重排？
11. Oracle 上界在哪一格被突破了？论文提过这件事吗？
12. 这篇用的温度是多少？做了什么统计检验？报了几次运行？
13. 它怎么区分自己和 RAG？原文那句对比的两个关键词是什么？
14. 它引用 Voyager 时，说 Voyager 的关注点是什么、自己的是什么？

---

## 11. 核心数字速查表

| 项 | 数字 |
| --- | --- |
| 测试实例 | **5,400** |
| gold skill | **636** |
| 干扰 skill | **25,626** |
| 语料库总量 | **26,262**（gold 占 **2.4%**） |
| 六个数据集实例数 | 747 / 760 / 1,430 / 1,100 / 223 / 1,140 |
| 六个数据集 skill 数 | 320 / 19 / 14 / 55 / 89 / 139 |
| 上下文窗口 | **128K** |
| 采样温度 | **0.7** |
| 候选池 | top-**50** |
| 注入 top-k 扫描 | k ∈ {**1, 2, 4, 8**} |
| 干扰数扫描 | N ∈ {**0, 2, 4, 8**} |
| Progressive Disclosure 最大轮数 | **10** |
| gold 在 BM25 top-50 的实例 | **4,520 / 5,400 = 83.7%**（推导值） |
| Oracle 增益（平均分） | 8B **+14.7** · 70B **+16.6** · 24B **+19.8** · 235B **+14.2** · 32B **+16.4** · 4B **+22.8** |
| Oracle vs 最佳实用方案的缺口 | **4.8–8.3pp**（32B 4.8 · 70B 5.2 · 4B 8.3） |
| Oracle 增益的兑现率 | 4B **64%** · 235B **67%** |
| 平均分 · Oracle | 8B **44.5** · 70B **64.4** · 24B **63.2** · 235B **67.5** · 32B **67.2** · 4B **61.6** |
| 平均分 · LLM Selection | 8B **37.0** · 70B **59.2** · 24B **56.6** · 235B **62.8** · 32B **62.4** · 4B **53.3** |
| 平均分 · Prog. Disclosure | 8B **36.3** · 70B **48.5** · 24B **46.7** · 235B **59.9** · 32B **55.3** · 4B **43.2** |
| **PD vs LLM Selection** | **六个模型 0 : 6 全负**：8B **−0.7** · 70B **−10.7** · 24B **−9.9** · 235B **−2.9** · 32B **−7.1** · 4B **−10.1** |
| 加载率的跨模型落差 | **61 个百分点**（Llama-8B 72.1 − Llama-70B 11.1，同一家族） |
| Recall@1 · BM25 基线 | ThmQA **57.2** · Logic **12.0** · ToolQA **7.0** · CHAMP **13.2** · MedCalc **29.3** · BigCode **23.6** |
| Recall@1 · 最佳重排 | ThmQA **77.4** · Logic **31.4** · ToolQA **56.4** · CHAMP **22.5** · MedCalc **92.3** · BigCode **28.2** |
| 整体加载率（Table 6） | 4B **21.0** · 8B **72.1** · 24B **28.3** · 32B **20.1** · 70B **11.1** · 235B **54.1** · GLM **37.8** · GPT **31.2** |
| gold 不在 top-50 的实例 | **880 条（16.3%）** |
| 对照 · Voyager 的 top-5 检索准确率 | **96.5%**（309 样本，库规模未公布） |

> `scripts/check_numbers.py` 仍会标出两项：**91.2**（Qwen3-32B 的 MedCalc Recall@1）和 **−2.8**（Qwen3-4B 的 Δ Load）。
> **判断结果：不补。** 两者都是表格单元格而非结论性数字——速查表已收了各自维度的极值（MedCalc 最佳 92.3、Δ 最负 −15.1 及负值模型数 5/8）。**此条为已判断，勿重复讨论。**
| 整体加载率范围 | **11.1% – 72.1%** |
| 单格加载率极值 | **0.0%**（Llama-70B/BigCode）– **99.7%**（Llama-8B/Logic） |
| Table 7 最大正差 | GLM-5.1 **+35.4pp** · GPT-5.4 **+33.0pp** · Qwen3-235B **+22.4pp** |
| Table 7 唯一负差 | Llama-70B **−4.2pp** |
| **Table 8 总体 Δ** | **+0.1pp（36.9 vs 36.9）** |
| Table 8 负 Δ 的模型数 | **5 / 8**，最负 Llama-8B **−15.1pp** |
| MedCalc Recall@1 | BM25 **29.3** → Qwen3-235B 重排 **92.3** |
| CHAMP Recall@1 最好 | **22.5**（Llama-70B） |
| SkillsMP 规模（§1，截至 2026-04-26） | **超过一百万** |
| 版本 | v1 2026-04-27 / v2 2026-05-21 / **v3 2026-06-07** |
| v1→v3 作者变化 | **7 → 9 人**（新增两位 ByteDance） |

---

## 相关

- [[Voyager 论文精读笔记]] —— 管「造和存」，SRA 管「取和用」
- [[Generative Agents 论文精读笔记]] —— 没有 verifier，正好对照
- [[ReAct 论文精读笔记]] —— 内层循环的原型
- [[course/ai-agents-week-03/notes.zh.md]] —— 加载规则、渐进披露、selection geometry
- [[agent-service-architecture.en.md]] —— Router / Loader 那一层的工程对应
