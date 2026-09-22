# AI Agents Week 01 — What makes a system an agent?（2026-09-20）

课程：**AI Agents Bootcamp** · SupportVectors AI Lab（正式开课日 = 2026-09-20）
大纲位置：`01 / 16 areas of study` · 分类 **Foundations**
一句话问题：*When does a sequence of instructions become a system that can pursue a goal?*

> **⚠️ 已确认：本周用的是同一套 deck。**
> p.1 标题页与 Week 00 **逐字相同**，副标题栏甚至仍写着 `PUBLIC MEETUP · SUPPORTVECTORS AI LAB`
> —— 说明讲师直接复用了 9/12 那场的幻灯片，没有为正式课重做。
> 见 [`uploads/slide-01-title.png`](uploads/slide-01-title.png) ↔ [`../ai-agents-week-00/uploads/slide-01-title.png`](../ai-agents-week-00/uploads/slide-01-title.png)
>
> **推论**：增量不会在幻灯片里，只会在**口头讲法、现场 Q&A、和下午的 lab** 里。
> 所以 —— **别再逐页截图了**，只在讲师说出 deck 上没有的东西时才记。
> 主体内容请看 👉 [`../ai-agents-week-00/summary.zh.md`](../ai-agents-week-00/summary.zh.md)

## 目录

| 文件 | 内容 |
| --- | --- |
| ⭐ [`delta.zh.md`](delta.zh.md) | **本周增量**（主文件）：新增 / 讲法不同 / 被修正 / 被砍掉 四类 |
| [`notes.zh.md`](notes.zh.md) | 现场笔记（只在出现 Week 00 没有的内容时才记） |
| 📤 [`summary.en.md`](summary.en.md) | **英文版 · 给团队分享用** —— 本周主题：agent 记忆的三分法（episodic / semantic / procedural） |
| [`uploads/`](uploads/) | 幻灯片截图，命名沿用 `slide-NN-xxx.png` |
| 📚 [`../reading-list.zh.md`](../reading-list.zh.md) | **论文清单**（全课程共用）：按 16 个模块排序，已逐篇核查。现在只需读 ReAct + SWE-agent |

## 与 Week 00 的对应关系

大纲 01 的三条 bullet，对照 Week 00 的七幕：

| 大纲 01 要点 | Week 00 出处 | 覆盖度 |
| --- | --- | --- |
| Agency, delegation, and the model–tool–environment relationship | ACT I（Aladdin's lamp = delegation 的最古老形态）+ ACT II（What an Agent Is） | 待确认 |
| ReAct loops; decomposing goals into actions whose results can be checked | **ACT IV（The Loop & the Governor）** | 待确认 |
| Choosing between deterministic software and model-mediated decisions | ACT IV（四条停止规则 / verifier 算术）+ ACT VII | 待确认 |

**In practice（本周动手）**：Set up the Python and lab environment; inspect a first agent loop and its execution trace.
**Working with**：Python · n8n · Ray

> 注意：Week 00 下午已经在笔记本上跑过 engine + newsletter。本周的 lab 若只是环境搭建，重点放在 **execution trace 怎么读**——这是 Week 00 没细讲的部分。

## 待确认清单（听课时对照）

- [x] ~~"ReAct" 这个词 Week 00 有没有正式出现过？~~ **有，p.19**：*"The 2023 name for the loop was ReAct."* 他把 ReAct 降格成"那一年对循环的叫法"——循环是本质，ReAct 只是写法。所以大纲 01 的 "ReAct loops" 不是新内容。
- [ ] governor / 停止规则 在正式课里是不是同一套讲法？
- [ ] deterministic vs model-mediated 的判据，有没有比 Week 00 更具体的决策表？
- [ ] execution trace 的字段结构（Week 00 没有）

## 相关

- 前置（主体内容）：[`../ai-agents-week-00/index.md`](../ai-agents-week-00/index.md)
- 参考阅读：[`../ai-agents-week-00/ref-harness-engineering.zh.md`](../ai-agents-week-00/ref-harness-engineering.zh.md)
- 课程大纲截图：[`../ai-agents-week-00/uploads/bootcamp-curriculum.png`](../ai-agents-week-00/uploads/bootcamp-curriculum.png)
