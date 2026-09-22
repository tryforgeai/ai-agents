# Agent Harness 论文阅读清单（按课程模块排序）

> 建立于 2026-09-20（bootcamp Week 01 当天）
> **所有条目已逐一核查存在性**——包括四篇 2026 预印本，编号 / 标题 / 作者 / 结论均属实。
> 排序原则：**跟着 16 个课程模块走，学到哪读哪**，不要一次性摊开。

---

## 现在就读（两篇）

### ⭐ ReAct: Synergizing Reasoning and Acting in Language Models
`arXiv:2210.03629` · Yao et al. · ICLR 2023

**为什么现在读**：Week 01 p.19 那句 *"The 2023 name for the loop was ReAct"* 的出处。读完今天这页就闭环了。

核心：把"思考轨迹"和"环境行动"交错——Reason → Act → **Observation** → Reason。
关键在 Observation：在此之前主流是 Chain-of-Thought（一路想到底、中途不接触外界，错了没人纠正）。

> ⚠️ 讲师用过去时说 *"**was** ReAct"`——他在降格这个词：**循环是本质，ReAct 只是 2023 年的一种写法**。现在改用结构化 tool calling，但环还是那个环。别把它当"架构"学。

---

### ⭐ SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering
`arXiv:2405.15793` · John Yang et al. · NeurIPS 2024

**为什么现在读**：这是 Week 01 p.22「同一个前沿模型，只换 harness，Terminal-Bench Top-30 → Top-5」的**学术版**。对应课程模块 02。

核心论点（非常 harness-centric）：

> 给模型什么样的电脑接口（**Agent-Computer Interface, ACI**），会显著改变它完成软件工程任务的能力。

数据：SWE-bench 12.5%、HumanEvalFix 87.7% pass@1 —— 而改进**大部分来自 ACI/harness 设计，不是换模型**。

**设计原则（可直接用在 lab 上）**：

- 不要把"万能 Bash"当主要 agent 接口
- 提供**语义化、边界清晰、返回紧凑结构化结果**的工具
- 工具输出是 context 的一部分——终端输出太多会直接吃掉有效推理预算
- 把"找代码→读→改→跑测试→读失败→修复"做成高质量动作原语
- **少量、职责稳定、返回值清晰** > 工具越多越好

---

## 按模块跟进

| 课程模块 | 论文 | 编号 | 备注 |
| --- | --- | --- | --- |
| 03 Context, instructions & personas | Generative Agents: Interactive Simulacra of Human Behavior | `2304.03442` | 长期记忆三件套：**写入 → 压缩反思 → 动态检索** |
| 04 Tools, MCP & security boundaries | OpenHands: An Open Platform for AI Software Developers | `2407.16741` | ICLR 2025。读**架构边界**：agent policy / runtime / tools / sandbox / observability 如何解耦 |
| 05 Skills & procedural knowledge | **Voyager** | `2305.16291` | 可积累的**代码技能库**。见下方专节读法 |
| **多 agent**（课程确认会讲 MARL） | **Why Do Multi-Agent LLM Systems Fail?** | `2503.13657` | UC Berkeley。**结论反直觉**，见下方专节 |
| 06 Evaluation as an engineering discipline | The Scaffold Effect in Coding Agents | `2607.22585` | ⚠️ 2026-07，ICML DL4C workshop 在审 |
| 08 Specs, governance & verification | Natural-Language Agent Harnesses | `2603.25723` | 清华 + 哈工大。选读 |
| 09 **Learning from whole trajectories** | **Agentic Harness Engineering** | `2604.25850` | **与模块 09 精确对应**。三层可观测性：component / experience / decision |
| （补充记忆） | Reflexion: Language Agents with Verbal RL | `2303.11366` | NeurIPS 2023。不训练权重，把失败反馈转成文字反思写入 **episodic memory** |
| （补充记忆） | **MemGPT: Towards LLMs as Operating Systems** | `2310.08560` | ⭐ **原清单漏了这篇**，见下方专节 |
| （综述） | Code as Agent Harness | `2605.18747` | ⚠️ 这是**综述**，42 位作者，不是研究论文。当地图用，不当论文读 |

---

## 📌 记忆专题（三层各对应一篇 + 一篇管注入）

Week 01 补上了 Week 00 缺失的记忆三分法（episodic / semantic / procedural），对应论文：

| 论文 | 管哪层 | 核心 |
| --- | --- | --- |
| **Generative Agents** `2304.03442` | **semantic**（及其生成） | 完整生命周期：写入 → reflection 压缩 → 加权检索。打分公式 `α·relevance + β·recency + γ·importance` 出自这篇 |
| **Reflexion** `2303.11366` | **episodic** | 失败反馈 → 文字反思 → 写入 episodic memory，下次取回 |
| **Voyager** `2305.16291` | **procedural** | 成功做法固化成**可执行 code skill**，不是文字总结 |

### ⭐ MemGPT: Towards LLMs as Operating Systems
`arXiv:2310.08560` · Packer et al. · 2023（后来商业化为 Letta）

**为什么补进来**：上面三篇讲的是「存什么」，MemGPT 讲的是「**每轮塞什么进 context**」—— 也就是 Week 01 那个悬而未决的 injection / 预算分配问题。

把 context 窗口类比成**操作系统的内存分页**：

```
main context   ← RAM（有限、贵）
external store ← 磁盘（无限、慢）
        ↕ agent 自己决定何时换入换出
```

关键设计：**让 agent 调用函数管理自己的记忆** —— 需要旧信息时主动 `search`，context 将满时主动 `evict` 到外部存储。

> ⚠️ **和课程框架的张力，值得对照着看**：
> MemGPT 把记忆管理**交给模型**；而 Week 00 的框架倾向把这类决定交给 **harness**（七动词里的 `persists`）。
> 按 p.53 的 Deference 规则——**有些决定它没资格做**——「自己决定忘掉什么」算不算其中之一？

### 检索 ≠ rerank

Rerank 只解决候选排序。记忆检索多两个轴、多一道工序：

| | 标准 RAG | 记忆 |
| --- | --- | --- |
| 打分 | 相关性 | 相关性 + **新近性** + **重要性** |
| 时间 | 文档基本静态 | **会过期、会被推翻** |
| 出处 | 无所谓 | **必须带 provenance**（客户说的 vs 模型猜的） |

```
召回 → 打分（含时间衰减）→ rerank → 【预算分配】→ 注入
                                      ↑ 记忆独有，是打包问题不是排序问题
```

---

## 📌 Voyager 读法（procedural memory 的原型）

`2305.16291` · Wang et al.（NVIDIA / Caltech）· 2023 · **没训练任何权重**

**三个组件**：自动课程 / **skill library** / 迭代提示。

⭐ **skill library 的关键设计**：skill 是**可执行 JavaScript**，但**用描述的 embedding 建索引**——
检索靠的是 **contract（描述）**，不是 procedure（代码）。所以 **contract 写得烂比没写还糟**。

**结果**：独特物品 3.3×、行进距离 2.3×、科技树里程碑快 15.3×，**技能可迁移到新世界**。

### ⚠️ 读时必带的三个保留

**1. Minecraft 是异常友好的环境**

| Minecraft | 真实场景 |
| --- | --- |
| 动作**可逆** | 发出去的邮件收不回 |
| 反馈**即时且程序化** | 「这个推荐好不好」没有返回码 |
| 成功信号**明确** | 模糊 |
| 试错**免费** | 每次调用都花钱 |

→ 它验证的是**机制可行**，不是这套东西在高风险环境里安全。

**2. 它的 self-verification 用 LLM 当裁判** —— 直接撞上 Week 00 p.27 的**镜子问题**（*agents reliably skew positive when grading their own work*）。Voyager 过关是因为**环境信号足够强**兜住了乐观。**换到没有强环境信号的场景，这套会塌。**

**3. 2023 年的论文**，读思想别抄代码。

### 怎么读（两小时）

| 读 | 跳 |
| --- | --- |
| §Skill Library —— 代码化 + 描述索引 | Minecraft 环境和 API 细节 |
| §Iterative Prompting —— 三种反馈怎么回灌 | 科技树 / 物品统计 benchmark |
| §Self-Verification —— 及它为什么能成立 | 自动课程 |

**带走三条**：

1. **procedural memory 的正确形态是可执行物**，因为它自带验证
2. **检索靠 contract，不靠 procedure**
3. **verify 通过才入库** —— 防止"把侥幸成功固化成标准做法"的唯一闸门

### ↔ 和 Generative Agents 的区别

| | Generative Agents | Voyager |
| --- | --- | --- |
| 存什么 | **我经历了什么** | **我会做什么** |
| 记忆层 | episodic → semantic | **procedural** |
| 形态 | 自然语言 | **可执行代码** |
| "反思" | reflection：合成高层推断 | 改代码直到跑通 |
| 目标 | **believability** | **competence** |
| **有无 ground truth** | ❌ **没有** | ✅ **环境说了算** |

> 最深的区别是**验证**。Voyager 有 verifier，Generative Agents 没有——
> 这解释了主张强度：一个只能说"看起来可信"，一个能说"快 15.3×"。
>
> **两边互补**：GA 管 episodic/semantic 的写入与检索，Voyager 管 procedural。
> 空缺也互补：GA 缺验证，Voyager 缺"记住发生过什么"。

---

## 📌 多 agent：Why Do Multi-Agent LLM Systems Fail?

`arXiv:2503.13657` · Cemri et al., UC Berkeley（Matei Zaharia、Ion Stoica 等）

> ✅ **课程确认会讲 MARL**，到时带着这篇去对照。

- **1,600+ 条执行轨迹**标注，跨 **7 个主流多 agent 框架**
- **14 种失败模式**，三类：**系统设计 / agent 间错位 / 任务验证**
- Cohen's κ = 0.88

**核心结论（反直觉）**：

> 失败大多源于**系统设计和交互问题**，不是 LLM 能力不足；**需要结构性重新设计，不是修修补补。**

**失败模式对照 Week 00**：

| MAST | 课上对应 |
| --- | --- |
| **Step Repetition**（重复步骤、无进展） | **hunting** / Futility 出口 |
| **Task verification** 整一类 | **verifier** |
| Disobey Task/Role Specification | specification gap（神灯） |

> **答案方向**：多 agent 常不如单 agent，因为它**把 harness 问题乘了 N 倍**——每多一个 agent，多一份 context、多一道交接、多一处静默失败。
>
> **← 补上了猴面包树判据的反面**：
> - p.27 给了什么时候**该**用：*when information demands*
> - MAST 给了什么时候**会出事**：交接和验证撑不住的时候

⚠️ **MARL ≠ LLM 多 agent**，别混：

| | MARL | LLM 多 agent |
| --- | --- | --- |
| agent 是 | 被**训练**出的策略（权重） | 被 **prompt** 出的 LLM 实例 |
| 怎么变好 | 训练，reward 更新参数 | 不训练，改 prompt / 改编排 |
| 怎么协作 | 环境里的动作和奖励 | **文字互相说话** |

讲师提 MARL 借的是它的**问题**（团队何时胜过独奏者），**不是方法**。

---

## ⚠️ 两条提醒

**1. 别先读那四篇 2026 的。**
都是三到六个月内的预印本，还没被时间筛过。搜索时同主题一大批正在涌现——HarnessX、*What makes a harness a harness*、*Stop Comparing LLM Agents Without Disclosing the Harness*、*Rethinking the Evaluation of Harness Evolution*……**这个方向正在喷发，大部分会沉下去。新 ≠ 重要。**

**2. 这份清单原本的框架假设「你要造一个 harness runtime」。**
但最初的问题是 DSH vs Hermes **选哪个用**。选型 ≠ 自建，差一个数量级的工作量。读的时候注意别被带偏。

---

## 落地框架（比论文清单本身更有用的部分）

自建 harness 的六层：

```
1. Task layer        任务状态、验收标准、风险级别
2. Context layer     Repo map、AGENTS.md、RAG、记忆检索、上下文压缩
3. Policy layer      plan → act → observe → verify → reflect；子 agent、模型路由、预算与终止
4. Tool layer        搜索、读写、Git、测试、构建、浏览器、MCP
5. Environment layer workspace、容器、依赖缓存、网络/密钥/生产权限隔离
6. Evidence layer    trajectory、diff、命令输出、测试证据、评测、成本、失败分类
```

**六条实践原则**（前两条最要紧）：

> 🔑 **policy 可以是 prompt；invariant 必须是 code。**
> 🔑 **"任务完成"必须有可检查的 evidence。**

- 把不可违反的事做成**系统约束**，不是提示词建议
- 工具要做成**高信息密度的领域接口**，不是无限制 shell
- 重复失败转成**最小、可回滚、可评测**的 harness 改动
- 长期记忆要有 **provenance、置信度、时效、删除机制**

> **↔ 与课程的对应**：第二条就是 Week 00 p.53 的 **Success 出口 + verifier**——
> *"You may run your loop only as far as your verifier deserves to be trusted."*（p.48）

---

## 相关

- [`ai-agents-week-00/ref-harness-engineering.zh.md`](ai-agents-week-00/ref-harness-engineering.zh.md) —— Addy Osmani《Agent Harness Engineering》精读（p.22 那句的出处）
- [`ai-agents-week-01/delta.zh.md`](ai-agents-week-01/delta.zh.md)
