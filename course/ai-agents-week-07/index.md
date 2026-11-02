# AI Agents Week 07 · Gradient Descent for Sentences：作坊、前沿与缰绳

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-11-01（周日，11:00–20:30）
实际议程：白板 + Orientation → Experientials 12:00 → Deep dive 14:30 → **Guest lecture 17:00**（讲义里没有）→ Deep dive, continued → Owl of Minerva
状态：**已下课**。精读、课堂笔记（白板 + deck p.2–60）、lab-log、客座讲座、summary 课后版已完成；p.60 之后和 Owl 五行待看录播补。讲义 32 页（Asif Qamar，first draft 2026-10-27）。

> **A prompt is a parameter — a point in a discrete space with no gradient — and prompt optimization is search over that space, steered by a pseudo-gradient written in words.**
> **The optimizer is only ever as good as the metric it is handed.**

## 目录

| 文件 | 内容 |
| --- | --- |
| [summary.zh.md](summary.zh.md) | **今天学了什么（课后版）**：核心概念表、GEPA 循环、field notes 四课、工作台真名、我的练习结果、客座讲座、待办 |
| [notes.zh.md](notes.zh.md) | 逐页课堂笔记：上午白板（ŷ = f(x;θ*,ω,Φ)、softmax 与温度）、Orientation（小测 7 题、field notes、六条 headlines）、客座讲座（AI 网络、UEC/MRC vs InfiniBand、DeepSeek）、Deep dive D1–D3 |
| [lab-log.zh.md](lab-log.zh.md) | 动手记录：Bench 2（v1→v5 + 最终 prompt）、Bench 4（A/B 对比）、Bench 7（frontier + 合并）、Genie's Exam A1 |
| [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md) | 讲义逐节精读：式 (1)–(5)、GEPA 七步、frontier 手算、DSPy 代码、优化器 × artifact；含 **Debrief 揭晓表**（已填）和 Owl 五行（待填） |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览 |
| [reading-list.zh.md](reading-list.zh.md) | 本周四篇必读、选读顺序与核实清单（课前在另一台电脑上整理） |
| [learned-so-far.zh.md](learned-so-far.zh.md) | 课中时间线模板（课前版） |
| [`prep/`](prep/index.md) | **课前版存档**（10/29）：index、速览、概念预习 notes、lab-log 模板、summary 模板；rebase 合并时保留 |
| [GEPA 英文介绍（Claude Doc）](https://claude.ai/artifact/6Ny8LQz754796x1jmM65bT) | 给同学的分享版：准备 → 7 步循环（含图）→ 收尾 → 何时不用 → DSPy；含 Bench 7 手做一轮的例子 |
| `uploads/` | lesson plan PDF、exam card（只留本地，不进 git） |
| `harrisons-workshop/`、`genies-exam/` | 课程 kit（只留本地，不进 git） |
| [Week 06](../ai-agents-week-06/index.md) | 上周：Toolcraft II |
| [勘误核对 W01–W06](../errata-check-W01-W06.zh.md) | 6 份 errata 对照笔记，已全部修正 |
| [全课程阅读清单](../reading-list.zh.md) | 共用阅读索引 |

## 本周待办

- [ ] 看录播补 p.60 之后 + Owl 五行
- [ ] Bench 9 镜子环节；Bench 10 Sea Trial（用 Bench 2 v5）
- [ ] Genie's Exam A3 / B1 / C1（周二 / 周四）
- [ ] workshop notebook、exam field notes 放 `uploads/`
- [ ] Reservoir §1/3/4/5/12；必读 GEPA、DSPy、ACE、SkillOpt
- [ ] 周二 / 周四跑 `dspy.GEPA`
- [ ] Week 6 尾巴：重下 strangers-toolbox（10/26 后），读 *No Castle Without Walls*

## 课程顺序

Skills（W3–W4）→ Tools + Inference（W5）→ Toolcraft II（W6）→ **Prompt 优化 / GEPA（W7）** → Memory（W8）
