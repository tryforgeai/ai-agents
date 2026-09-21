# 参考阅读：Agent Harness Engineering（Addy Osmani，2026-04-19）

来源：<https://addyosmani.com/blog/agent-harness-engineering/>
关联：Week 00 [`notes.zh.md`](notes.zh.md) → ACT II p.21「Model plus harness」

> **为什么读这篇**：课上 p.21 那句 *"a decent model with a great harness beats a great model with a bad harness"* **一字不差出现在这篇文里**。讲师用的是这个圈子的现成说法，不是自创。这篇是该说法的完整展开。

---

## 一、核心等式

> **Agent = Model + Harness.**
> **If you're not the model, you're the harness.**（Viv Trivedy）

harness = **除模型之外的一切代码、配置、执行逻辑**。裸模型不是 agent；harness 给了它**状态、工具执行、反馈回路、可强制的约束**之后，它才成为 agent。

具体包含：

- system prompt、`CLAUDE.md` / `AGENTS.md`、skill 文件、子 agent 提示词
- 工具、skills、MCP server 及其**描述**
- 自带基础设施（文件系统、沙箱、浏览器）
- 编排逻辑（派生子 agent、交接、模型路由）
- hooks / 中间件（压缩、续跑、lint 检查）
- **可观测性（日志、trace、成本与延迟计量）** ← 这就是课上的 **ledger**

> Simon Willison 的极简版：agent 就是*"在循环里运行工具以达成目标"*的系统。**功夫在工具和循环的设计上。**

**关键提醒**：Claude Code、Cursor、Codex、Aider、Cline —— **这些全都是 harness**。底下的模型有时是同一个，**但你体验到的行为由 harness 主导**。

---

## 二、"Skill issue" 重构 ⭐

工程师的默认反应是：agent 干了蠢事 → 怪模型 → "等下一代吧"。

**harness 思维拒绝这个默认值**。失败通常是**可读的**：

| agent 的问题 | harness 的修法 |
| --- | --- |
| 不知道某个约定 | 写进 `AGENTS.md` |
| 跑了破坏性命令 | 加 hook 拦掉 |
| 40 步的任务跑丢了 | 拆成 planner + executor |
| 老是"完成"了坏代码 | 把 typecheck 的失败信号**回灌进循环** |

> HumanLayer：*"不是模型问题，是配置问题。"*

**⭐ 硬数据**：Terminal Bench 2.0 上，**同一个 Claude Opus 4.6**，跑在 Claude Code 里的分数**远低于**跑在定制 harness 里。Viv 的团队**只改 harness**，把一个 coding agent 从 Top 30 推到 Top 5。

> 原因：模型的 post-training 和它训练时所用的 harness **是耦合的**。换个 harness、配上更适合你代码库的工具和更紧的反压信号，能**解锁原 harness 浪费掉的能力**。

> **结论**：*"今天模型能做的，和你看到它做的，之间那道差距，主要是 harness 的差距。"*

---

## 三、⭐ 棘轮（The Ratchet）：每个错误都变成一条规则

**这是全文最可操作的一条习惯。**

> 只要发现 agent 犯了个错，就花时间做一个工程上的解法，**让它再也犯不了这个错**。

把 agent 的错误当作**永久信号**——不是笑话，不是"这次手气不好，重跑一次"。

作者的例子：agent 提交了一个注释掉测试的 PR，被误合并 →
1. `AGENTS.md` 加一条"永远不要注释掉测试；要么删要么修"
2. pre-commit hook 加一条：在 diff 里 grep `.skip(` 和 `xit(`
3. reviewer 子 agent 把"注释掉的测试"标为阻断项

**两条纪律：**

- **只在见到真实失败后才加约束**
- **只在更强的模型让它变得多余时才移除**

> **⭐ `AGENTS.md` 的每一行都应该能追溯到一件具体出过的事。**

> **所以 harness engineering 是一门手艺而不是一个框架**：适合你代码库的 harness 由**你自己的失败史**塑形。**下载不来。**

---

## 四、从行为倒推（Working backwards from behaviour）

设计方法：**想要的行为 → 倒推出交付该行为的 harness 部件**。

> **如果你说不出某个组件是为了交付哪个行为而存在的，它多半就不该在那儿。**

| 想要的行为 | harness 部件 |
| --- | --- |
| 持久地处理真实数据 | **文件系统 + Git** |
| 写代码并执行 | **bash + 代码执行** |
| 安全执行、良好默认 | **沙箱 + 自带工具** |
| 记住新知识 | 记忆文件、web search、MCP |
| 长 context 下不掉链子 | **压缩、工具输出卸载、skills** |
| 长周期任务 | Ralph loop、规划、验证 |

### 4.1 文件系统 + Git：**持久状态**

最基础也最被低估的原语。模型只能操作 context 里装得下的东西——**没有文件系统，你就只是在往聊天框里粘贴**。

有了它，agent 得到：工作区、**把中间产物卸载出 context 的地方**、以及多个 agent 和人**通过共享文件协同**的接口。加上 Git 就白得了版本控制：追踪进度、回滚错误、分支做实验。

> 其余大多数 harness 原语最后都指向文件系统。

### 4.2 bash + 代码执行：**通用工具**

harness 只能执行它写了逻辑的工具。两条路：给每个可能的动作预造一个工具，**或者给它 bash，让它自己现造**。

> *"这是'教人用一个厨房小家电'和'把整个厨房交给他'的区别。"*

### 4.3 沙箱与默认工具

bash 只有跑在安全的地方才有用。在自己笔记本上跑 agent 生成的代码有风险，而且单个本地环境**扩展不到多个并行 agent**。

沙箱应自带：预装运行时和包、Git 和测试 CLI、**无头浏览器**。

> **浏览器、日志、截图、测试运行器 —— 这些正是让 agent 能观察自己工作、闭合自我验证回路的东西。**

> **模型不配置自己的执行环境。** 在哪儿跑、有什么可用、怎么验证输出，**全是 harness 层的决定**。

### 4.4 记忆与搜索：持续学习

模型除了权重和当前 context 之外没有额外知识。**不能改权重，就只能靠 context 注入。**

`AGENTS.md` 这类记忆文件每次启动都注入；agent 改它 → harness 重载 → **一次会话的知识带进下一次**。粗糙但有效的持续学习。

### 4.5 ⭐ 对抗 context rot

> **context rot**：context 窗口越满，模型推理和完成任务的能力**越差**。

三种反复出现的技术：

| 技术 | 做法 |
| --- | --- |
| **Compaction（压缩）** | 快满时智能摘要并卸载旧 context。**生产 harness 不能让 API 直接报错** |
| **Tool-call offloading（工具输出卸载）** | 2000 行日志塞进 context 只有噪音。**只留头尾**，全文卸到文件系统，需要时再读 |
| **Skills + progressive disclosure** | 启动时加载全部工具和 MCP，**在 agent 行动之前就已经拉低了性能**。skills 让 harness **只在任务真的需要时才展开**指令和工具 |

**Anthropic 补充的一招（超长任务用）：完整 context 重置** —— 拆掉整个会话，**从一份紧凑的交接文件重建**。他们明确说：*对长任务而言，光靠压缩不够。*

> 这更像**给新工程师做 onboarding**，而不是我们通常说的"记忆"。

### 4.6 长周期执行

今天的模型有三个毛病：**过早停止**、**复杂问题分解得差**、**跨多个 context 窗口时前后不一致**。

**Ralph Loop**：一个 hook **拦截模型退出的意图**，把原始 prompt 重新注入一个**全新的 context 窗口**，逼它对着完成条件继续干。每轮从干净状态开始，**通过文件系统读取上一轮的状态**。

> 一个极简的技巧，把单会话 agent 变成多会话 agent —— **而这种原语你从"用个更聪明的模型"里永远推导不出来**。

**Planning**：把目标分解成步骤，**写进磁盘上的 plan 文件**。每步之后自我验证：hook 跑测试套件，**把失败的错误文本回灌给模型**。

**⭐ Planner / Generator / Evaluator 分离**：

> Anthropic 明确指出：**把生成和评估分成不同的 agent，效果优于自我评估——因为 agent 给自己打分时可靠地偏乐观。**
>
> *"It's GANs for prose."*

**Sprint contract**：generator 和 evaluator 在写代码之前**先谈妥"完成"的定义**。

> 作者自述：**先写下 done-condition**，比他改过的任何 prompt 都更能防止范围漂移。

### 4.7 ⭐ Hooks：强制层

> **hook 是"我告诉了 agent 要 X"和"系统强制执行 X"之间的分界。**

hook = 在特定生命周期点运行的脚本：工具调用前、文件编辑后、提交前、会话开始时。

典型用途：
- 每次编辑后跑 typecheck / lint / 测试，暴露失败
- **拦截破坏性 bash**（`rm -rf`、`git push --force`、`DROP TABLE`）
- **推 `main` 或开 PR 前要求批准**
- 写入时自动格式化，省得 agent 浪费 token 调空格

> **⭐ 原则：success is silent, failures are verbose（成功无声，失败聒噪）。**
>
> typecheck 过了，agent 什么都听不到；失败了，**错误文本被注入循环**，agent 自我纠正。→ 常态下反馈回路**几乎免费**，出问题时**直接可操作**。

### 4.8 `AGENTS.md` 与工具选择

仓库根目录那个扁平的 markdown 规则手册，仍是**杠杆最高的单个配置点**——因为它**每一轮都落进 system prompt**。

**两条血的教训：**

1. **要短。** HumanLayer 把自己的控制在 **60 行以内**。每一行都在抢注意力，**规则越多，每条规则越不值钱**。
   > **是飞行员检查单，不是风格指南。**
2. **每一行都要挣来。** 规则要能追溯到具体的过往失败或硬性外部约束。否则就是噪音。**用棘轮，别头脑风暴。**

**工具同理**：每个工具的名字、描述、schema **每次请求都被印进 prompt**。
> **十个聚焦的工具胜过五十个互相重叠的**，因为模型能把菜单记在脑子里。

**⚠️ 安全警告**：工具描述会进 prompt，**所以你装的任何 MCP server 都是模型会读的可信文本**。一个草率或恶意的 MCP **可以在你打字之前就对你的 agent 完成提示词注入**。

---

## 五、harness 不会缩小，只会**移动**

天真的说法：模型变强 → harness 就没用了。

**确实有部分成立**：Opus 4.6 基本消灭了"context 焦虑"这个失败模式（Sonnet 4.5 曾在接近它以为的 context 上限时**过早收尾**），于是半年前为此写的一整类缓解脚手架**变成了死代码**。

**但天花板跟着模型一起移动了**：原来够不着的任务进入射程，**而它们有自己的失败模式**。焦虑脚手架没了，取而代之你需要多日记忆策略、协调三个专职 agent 的 harness、或者给生成的 UI 做设计质量的 evaluator。

> **⭐ Anthropic 的说法最干净：*"harness 里的每个组件，都编码了一条关于'模型自己做不到什么'的假设。"***
>
> 模型在某件事上变强了 → 那个组件**不再承重，应该拆掉**。模型解锁了新东西 → **需要新脚手架去够新天花板**。

### 模型–harness 训练回路

今天的 agent 产品是**带着 harness 做 post-training 的**。模型会**专门变得更擅长 harness 设计者认为它该擅长的动作**：文件操作、bash、规划、子 agent 派发。

> 这就是为什么 Opus 4.6 在 Claude Code 里和在别人的 harness 里**手感不同**，也是为什么**改一个工具的逻辑有时会引发奇怪的回归**。
>
> 真正通用的模型不该在乎你用 `apply_patch` 还是 `str_replace`——**但协同训练制造了过拟合**。

**两个实际含义：**

1. **harness 是活的系统，不是一次配好的配置文件。**
2. **"最好的"harness 未必是模型训练时所在的那个**，而是为你的任务设计的那个。

---

## 六、Harness-as-a-Service（HaaS）

从**建立在 LLM API 上**（给你一个 completion）转向**建立在 harness API 上**（给你一个 **runtime**）。Claude Agent SDK、Codex SDK、OpenAI Agents SDK 都指向同一方向。

| | 过去的默认路径 | 现在的默认路径 |
| --- | --- | --- |
| 你要做的 | 自己搭循环、接工具调用、管会话状态、发明审批流 | **选一个 harness 框架**，沿四根支柱配置（system prompt / 工具 / context / 子 agent） |
| 精力放在 | 重造 agent | **领域特定的 prompt 与工具设计** |

> Viv 的话，也是"先乱着开始"的最佳论据：
> ***"好的 agent 构建是一场迭代练习。没有 v0.1，你就没法迭代。"***

---

## 七、走向何方

> **把顶级 coding agent 并排放（Claude Code、Cursor、Codex、Aider、Cline）——它们彼此之间的相似度，高于它们底层模型之间的相似度。**

模型不同，**harness 模式在收敛**。这是行业在慢慢找出"把生成模型变成能交付东西的系统"所需的**承重脚手架**。

**三个开放问题：**

1. 编排**多个 agent 并行**在同一个代码库上工作
2. agent **分析自己的 trace**，识别并修复 harness 层的失败模式
3. harness **为给定任务即时组装**正确的工具和 context，而不是启动时预配置

> **最后一条尤其有意思——那是 harness 从静态配置变成某种更接近编译器的东西的时刻。**

---

## 八、与 Week 00 课程的对照

| 课上的点 | 这篇文里的对应 |
| --- | --- |
| p.21 *"decent model + great harness beats..."* | **原句出处**（Viv / HumanLayer 圈子的说法） |
| p.21 harness 四件事（shown / may do / checks / stops） | 对应：context 注入、工具与权限、验证与 evaluator、**hooks 与 permission gate** |
| p.21 *"unit of engineering moved from prompt to loop"* | 全文主旨 |
| p.13 **ledger**（运行时在场的账） | **observability 层**：日志、trace、成本计量 |
| p.10 泥人的 **kill switch** | **hooks**：拦截破坏性命令、要求批准 |
| p.9 神灯 *delegation without verification* | **planner/generator/evaluator 分离** + sprint contract |
| p.12 猴面包树（多 agent 是祝福还是不得已） | 开放问题①：并行多 agent 编排；子 agent 的 **context 防火墙** |
| p.11 Ifá 分布式 | 同上 |
| 我问的 **progressive disclosure** | §4.5 对抗 context rot 的第三招 |
| 我问的 **token efficiency** | §4.5 context rot 整节 |
| 我说的 **"谋事在模型，成事在 harness"** | *"If you're not the model, you're the harness."* |
| 下午 newsletter *"cannot be trusted to write alone"* | **⭐ *"agents reliably skew positive when grading their own work"*** —— 自评偏乐观，所以必须有独立 evaluator |

### ⭐ 本文补上的、课上还没讲的东西

1. **棘轮纪律** —— 每个错误变成一条规则；`AGENTS.md` 每行都要能追溯到一次具体失败
2. **success is silent, failures are verbose** —— 反馈回路的设计原则
3. **同模型换 harness = Top 30 → Top 5** —— 硬数据，证明杠杆在 harness
4. **"每个组件编码了一条关于模型做不到什么的假设"** —— 判断该拆哪个组件的标准
5. **MCP 描述 = 提示词注入面** —— 安全
6. **少而聚焦的工具 > 多而重叠的工具** —— 十个 > 五十个
7. **模型–harness 协同训练导致过拟合** —— 换 harness 会有奇怪回归
