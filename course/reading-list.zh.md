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

## Week 02 追加 · 提示词注入与指令层级

> 加入于 2026-09-27（Week 02 当天）。起因：课上讨论 system prompt 与 user prompt 的边界，
> 追问"模型被训练听从 system prompt 是哪里说的"，顺出这一串。

### ⭐⭐ The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions
`arXiv:2404.13208` · Wallace, Xiao, Leike, Weng, Heidecke, Beutel（OpenAI）· 2024-04-19

**为什么读**：Week 02 Act VI（金库）那一幕的**学术底座**。已核查作者与摘要。

摘要核心句：

> *"LLMs often consider **system prompts** (e.g., text from an application developer) to be the **same priority** as text from untrusted users and third parties."*

**关键含义 —— 比课上讲得更狠**：

- system / user 的区分**不是架构隔离**，只是 chat template 里的特殊 token，拼成同一段序列
- 模型"听 system 的话"是**被训练出来的倾向**，强度取决于厂商做了多少功夫
- 正因为默认不够强，OpenAI 才要**专门造合成数据 + SFT + RLHF** 去训一套层级出来：
  **system（开发者）> user（用户）> 工具/网页返回的内容**
- 在 GPT-3.5 上微调后，**对训练时没见过的攻击类型也显著更稳健**，基础能力几乎不退化

> 🔑 **这篇论文本身就是"光靠写 prompt 守不住"的证明。**
> 工程上的解法是改训练和改架构，不是把守卫的话写得更严厉。
> ↔ 幻灯片 p83：*"你没法靠对守卫耳语来守住一个秘密。"*

📌 `hf papers read 2404.13208` 可直接抓取。

---

### Can LLMs Separate Instructions From Data? And What Do We Even Mean By That?
`arXiv:2403.06833` · 2024

标题就是 Act VI 的问题本身。把"指令 / 数据能否分离"当成一个**可定义、可测量**的问题来处理——
而不是当成一个可以靠措辞绕过去的工程细节。

---

### InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents
`arXiv:2403.02691` · 2024

**间接**提示词注入的 benchmark，专门针对**带工具的 agent** —— 正是 lethal trifecta 那条线。
"间接"是关键词：攻击不来自用户，来自 agent 自己去读的网页 / 邮件 / 文档。

> ↔ Willison 的三条腿：私有数据 × **不可信内容** × 对外通信。这篇测的就是中间那条。

---

### 必读（Week 02 讲义指定，非论文）

| 文献 | 用处 |
| --- | --- |
| Sheila Teo · *How I Won Singapore's GPT-4 Prompt Engineering Competition* | COSTAR 出处，Act III 后读 |
| Krakovna et al. · *Specification Gaming: The Flip Side of AI Ingenuity* | reward hacking 案例库（DeepMind） |
| Clark & Amodei · *Faulty Reward Functions in the Wild* | CoastRunners 赛艇 |
| Simon Willison · *The Lethal Trifecta for AI Agents* | Act VI 的框架来源 |

### 通向 Week 03（提示词优化）

- **DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines** `arXiv:2310.03714` · Khattab et al. · ICLR 2024
  → 注意藏在明处的前提：**一个 metric**
- **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning** `arXiv:2507.19457` · Agrawal et al. · ICLR 2026 (Oral)
  → 今天的手工爬山，做成不知疲倦的版本
- **LoRA: Low-Rank Adaptation of Large Language Models** · Hu et al. · ICLR 2022 · `arXiv:2106.09685`
  → 升级阶梯上 prompting 的**上一级**；Civitai 那些标签背后的东西

---

## Week 03 追加 · Skills

> 来源：Week 03 当天的参考资料 deck（自称"约 50 个来源"，按六类组织）。
> 这里记录我截到的那几页；链接和编号照抄屏幕，**未逐条打开核对**。

### 这份清单的组织方式（值得照抄）

| | 内容 | 什么时候用 |
| --- | --- | --- |
| 1 · Docs | 规范、官方 how-to、公告 | 你在构建或配置时 |
| 2 · Examples | 技能库、目录、市场 | 你想看真实的 skill 时 |
| 3 · Security | 扫描器、事故、攻击研究 | **在你安装任何东西之前** |
| 4 · Research | benchmark、市场研究、行业报告 | 你需要证据时 |
| 5 · Scale & future | 检索、上下文、自改进库 | 做进阶或前瞻工作时 |
| 6 · Course | Week 3 的 deck 和演示代码 | 复习和做练习 |

🔑 **按「什么时候用」而不是按主题组织**——这本身就是今天讲的 description 思路：**不是分类，是触发条件。**

### 1 · Docs

| 资源 | 用它来 |
| --- | --- |
| **Agent Skills specification** · agentskills.io/specification | 每个 skill 必须遵守的规则：文件夹布局、必填与选填字段、三层加载 |
| **skills-ref validator** · github.com/agentskills/agentskills | **CI 里做自动格式检查**；`skills-ref validate <folder>` |
| **Skill authoring best practices** · docs.claude.com/…/agent-skills/best-practices | 决定要写多细：简洁度、自由度、evaluation-first |
| **skill-creator** · github.com/anthropics/skills/tree/main/skills/skill-creator | 现成的工作流及其推理依据 |
| **Claude Code: skills** · code.claude.com/docs/en/skills | 列表预算、加载后的持久性、compaction、forked context、allowed-tools、作用域与优先级 |
| **Claude Code: plugins** · code.claude.com/docs/en/plugins | plugin 打包什么、市场、安装作用域、上下文成本、信任 |
| **Steering Claude Code** · claude.com/…claude-code-skills-hooks-rules-subagents-and-more | **何时用 CLAUDE.md / rules / skills / subagents / hooks；哪些是建议性的、哪些是强制的** |
| **Prompt caching** · platform.claude.com/docs/en/build-with-claude/prompt-caching | **让一张大 skill 清单变便宜** |

### 2 · Examples · 精选库

| 库 | 内容 | 实测数据（截图当时） |
| --- | --- | --- |
| **anthropics/skills** | 文档类（docx/pptx/xlsx/pdf）、设计、企业、meta skill；多为 Apache 2.0 | 参考实现 |
| **obra/superpowers** | 一整套工程方法做成互链的 skill：头脑风暴、规划、TDD、调试、评审 | **295k ⭐ / 26.4k fork / 683 commits / v6.4.2**；带 claude / codex / cursor / devin / hermes / kimi / muse / opencode / pi 九套 plugin |
| **trailofbits/skills** | 约四十个**窄**安全 skill：差异评审、Semgrep 规则、供应链审计 | **窄触发 + 自带 verifier 的范本** |
| **VoltAgent/awesome-agent-skills** | 厂商官方 skill 的精选索引：Sentry、Stripe、Cloudflare、Microsoft… | **35.2k ⭐ / 3.8k fork / 711 commits**；自称 **1000+**，README 写着 *"Hand-picked, not AI-slop generated"* |

> ⭐ **obra/superpowers 的 295k star** 值得单独注意——这是"把一整套工程方法做成互链 skill"的最大规模案例，而且它**为九个不同客户端各维护一套 plugin**。
> ⭐ **trailofbits 的"约四十个窄 skill"**是 Router 模式的实物：不做一个大的安全审计 skill，做四十个各管一件事的。

### 3 · Security

见 Week 02 的注入专题，外加：**Snyk Security Labs · ToxicSkills**（2026-02，审计 3,984 个公开 skill：**36.8%** 至少一个缺陷，**13.4%** 严重）。

### 4 · Research 🔥

| 论文 | 编号 | 核心数字 |
| --- | --- | --- |
| **SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks** | `arXiv:2602.12670` (2026-02-13) | **84 个任务、11 个领域**；**精选 skill +16.2 分**；**自生成 skill −1.3**；**2–3 个 skill 胜过 4+ 个** |
| **Agent Skill Evaluation and Evolution** | `arXiv:2606.11435` | 综述六个 benchmark 家族和四种 skill 演化方式；点名缺口 |
| **SkillCorpus** | `arXiv:2607.15557` | **821K 原始 skill 精选到 96,401**，**19 个质量标记**；增益温和 |
| **Inside the Skill Market** | `arXiv:2607.09065` | **11,497 个软件工程 skill**：结构、生命周期阶段、token 大小 |
| **Skill Retrieval Augmentation for Agentic AI** | `arXiv:2604.24594` | **26,262 条语料库**；**need-awareness Δ = +0.1pp** → [[SRA 论文精读笔记]] ✅ 已精读 |

> 🔥 **SkillsBench 那三个数字是今天最该记的实证：**
>
> - **自生成 skill 是负收益（−1.3）** —— 让 agent 自己写 skill 不等于变强
> - **2–3 个胜过 4+ 个** —— **这是 κ 的直接实测**，而且拐点低得惊人
> - 精选 skill **+16.2** vs 自生成 **−1.3** —— **差的不是数量，是策展**
>
> ↔ 和 SRA 合起来看：**SkillsBench 说"少而精"，SRA 说"大库里模型不会挑"。两篇指向同一个结论——瓶颈在选择，不在拥有。**

⚠️ **SkillsBench 作者单位很分散**（BenchFlow / Amazon / Ohio State / Dartmouth / Stanford / UC Davis / CMU / UC Berkeley / Independent），引用时留意这是个松散协作，不是单一实验室。

### 5 · Foundations（讲义引用的六篇）

| 论文 | 编号 | 用它来 |
| --- | --- | --- |
| **Voyager** | `2305.16291` | 正典的技能库 agent → [[Voyager 论文精读笔记]] ✅ |
| **Reflexion** | `2303.11366` | 不用梯度的学习 |
| **PAL: Program-aided Language Models** | `2211.10435` | **`scripts/` 存在的理由** |
| **Toolformer** | `2302.04761` | 工具使用的起点 |
| **Gorilla** | `2305.15334` | 早期的大规模工具调用 |
| **Options framework** · Sutton, Precup & Singh | *Artificial Intelligence* 112, 1999 | **skill 的理论**：initiation set / policy / termination |

---

## 相关

- [`ai-agents-week-00/ref-harness-engineering.zh.md`](ai-agents-week-00/ref-harness-engineering.zh.md) —— Addy Osmani《Agent Harness Engineering》精读（p.22 那句的出处）
- [`ai-agents-week-01/delta.zh.md`](ai-agents-week-01/delta.zh.md)
- [`ai-agents-week-02/index.md`](ai-agents-week-02/index.md) —— 提示词周
- [`ai-agents-week-03/index.md`](ai-agents-week-03/index.md) —— Skillcraft
- [[Voyager 论文精读笔记]] · [[SRA 论文精读笔记]] · [[Generative Agents 论文精读笔记]] · [[ReAct 论文精读笔记]]
