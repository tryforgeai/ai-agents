# AI Agents Week 03 · Skillcraft — A Prompt That Waits in the Pantry

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**  
讲义作者：Asif Qamar · 初稿日期：2026-10-03  
全天安排：11:00–20:00；18:15 checkpoint，18:30 后为可选进阶实验。

> **本周主线：把团队反复使用的做法写成可检索、按需加载、能验证完成的 Skill。**
> Week 02 学会把愿望说清楚；Week 03 把做法保存下来，让 agent 在正确的时候找到它。

## 目录

| 文件 | 内容 |
| --- | --- |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览：准备、时间表、六幕重点、Kitchen 六个实验、晚间 Lab 与作业 |
| [summary.zh.md](summary.zh.md) | 概念总结：渐进加载、触发边界、加载收益、Options、代码与判断、测试和设计模式 |
| [notes.zh.md](notes.zh.md) | 学习笔记：按 `skillcraft-slides.pdf`（113 页）逐幕走一遍，含原文金句、六道 Pop Quiz 与自进化附录 |
| [skillcraft-slides.pdf](skillcraft-slides.pdf) | 本周主讲幻灯片原件 |
| [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md) | 精读笔记：按原文逐节精读，补齐公式算例、Snyk 审计数字、两个 agent 的运行差异表、排错表、field notebook 模板与完整文献 |
| [fall-agents-week-3-lesson-plan.pdf](fall-agents-week-3-lesson-plan.pdf) | 原始 lesson plan PDF，共 43 页，正文使用独立页码 |
| ⭐ [survey-notes.zh.md](survey-notes.zh.md) | **第二场 · Agent Skills 田野调查**：harness 邻居图（hooks / subagent / plugin）、市场数据、两套分类、63.8% 纯文字、2.2% 需求类、厂商上手、runbook 十三行范例、范围判定表、五段工作流、听众问题清单、**以及和主讲冲突的六处** |
| ⭐ [lab-log.zh.md](lab-log.zh.md) | **Kitchen 实操记录**：Literal Cook 三张卡的逐轮结果、Honest Sous-Chef 对比、Which Scroll Wakes、Run Don't Reason 的三个失败样本（466 / 496 / 17791.11，均经复核）、Forge、今晚可执行清单 |
| [genies-kitchen/](genies-kitchen/) | 已解压的实验 app（`.venv` 已建，Python 3.12）；走 OpenRouter |
| [Week 02](../ai-agents-week-02/index.md) | 前置：部分规格说明、COSTAR、规格博弈、lethal trifecta |
| [全课程阅读清单](../reading-list.zh.md) | 共用阅读索引；**Week 03 追加一节已并入**（参考资料 deck 的六类清单 + SkillsBench 等五篇） |

### 本周产出的 skill 与论文笔记

| 文件 | 内容 |
| --- | --- |
| [`../../skills/paper-deep-read/`](../../skills/paper-deep-read/) | 当天写的论文精读 skill（含触发测试集）；已保存到 Claude |
| [[Voyager 论文精读笔记]] | ACT III 的正典案例 |
| [[SRA 论文精读笔记]] | 课堂提及；**need-awareness Δ=+0.1pp，对加载规则是实证打击** |
| [[agent-service-architecture.en.md]] | 多租户 agent 服务的架构笔记（英文），Router/Loader 那一层的工程对应 |

## 课程安排变化

**以本周讲义为准：Skills → Tools → 自动提示词优化。** Week 02 曾预告下一周讲 DSPy / MIPROv2 / GEPA；本周讲义明确将优化器内容顺延两周。保留上周最好的 Oracle prompt 及隐藏测试失败，后续仍会用到。

## 学习完成清单

- [ ] 区分 tool、skill、agent，以及 MCP、RAG 各自提供什么。
- [ ] 解释三层渐进加载：metadata / body / files & scripts。
- [ ] 写清 description 的触发词和排除条件，允许“不用任何 skill”。
- [ ] 写出 procedure 和可检查的 Done when。
- [ ] 把确定性计算交给脚本，并验证输入和输出。
- [ ] 分开测试“是否触发”和“触发后是否正确”。
- [ ] 审查外来 skill 的正文与脚本，理解权限和 sandbox 的作用。
- [ ] 完成日历实验 Tier 1；超出能力时明确说明或提问。
- [ ] 在 Hermes 与 Claude Desktop 中运行相同的三个案例。
- [ ] 带步骤清单、失败假设和检查方法参加 TA 复盘。

## ⚠️ 读之前先知道：讲义被实测打到的六处

当天第二场和两篇论文给主讲 deck 带来几处修订，**复习前先看** [`notes.zh.md` 的「课后修订」一节](notes.zh.md) 或 [`survey-notes.zh.md` 第六节](survey-notes.zh.md)。最要紧的三条：

- **"绝对不能发生"的事该是 hook，不是 skill 里的 Guardrail 文字**
- **渐进披露**在 SRA 的实测里**六个模型上全不如一次性 LLM Selection**（最大落后 10.7pp）
- **SkillsBench：2–3 个 skill 胜过 4+ 个；自生成 skill −1.3 分**，而精选 +16.2 分 → **差别不在数量，在策展**

## 当前资料状态

- ✅ `genies-kitchen` 已解压并跑通（见 `lab-log.zh.md`）
- ⬜ `when-the-time-is-right-kit.zip` —— 晚间 16:40 发放，尚未取得
- ⬜ 晚间 Lab 的 field notebook（步骤表 / 陷阱表 / 七问）待填
- ⬜ 作业 1：同一个 skill 装进 Hermes 和 Claude Desktop，各跑三个案例

论文编号、市场数字、GitHub star 数等**照抄屏幕，未逐条打开原始来源核对**；厂商自报数字（如 Rakuten 的「一天 → 一小时」）已在正文标明证据形态。
