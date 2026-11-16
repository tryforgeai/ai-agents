# AI Agents Week 10 · A Garbage Collector for the Mind（下）：Context 生命周期与治理

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-11-22（周日，⚠️ 待确认）
讲义：和 W9 共用，[PDF 在 Week 09](../ai-agents-week-09/Weeks%209-10%20Lesson%20Plan%20-%20A%20Garbage%20Collector%20for%20the%20Mind.pdf)
状态：**课前**。学习笔记已在 W9 写全本。

> **A memory system's read policy and its forget policy are one function, read in two directions.**
> Compaction 是剩余项，不是反射。

## 目录

| 文件 | 内容 |
| --- | --- |
| [W9 学习笔记 §3 Act II](../ai-agents-week-09/lesson-plan-精读.zh.md#3-act-iiw10--context-生命周期全剧中心) | managed heap、compaction amnesia、GC、驱逐分数、回收三难、两个海拔、缓存账、Hermes |
| [W9 学习笔记 §4 Act III](../ai-agents-week-09/lesson-plan-精读.zh.md#4-act-iiiw10--构建和治理-memory) | 谱系、两个时钟、ADK 前缀、写策略、plant–distract–probe、治理、sleep-time、Project Vend |
| [W9 学习笔记 §5–7](../ai-agents-week-09/lesson-plan-精读.zh.md#5-practice-i--the-buildcapstone) | Build / Proof 代码、两个 Postscript（Speakeasy） |
| `uploads/` | 只留本地，不进 git |
| [Week 09](../ai-agents-week-09/index.md) | 上周：Act I |

## 本周待办

- [ ] 课前在 W9 笔记里复习 Act II / III，做自测题 5–12
- [ ] Palace 二楼 + 大厅（Overflowing Desk / Two Clocks / Diary Decision / Long Visit，⚠️ 待手册核实）
- [ ] Speakeasy：两个 Postscript
- [ ] 课上再建 notes / lab-log / learned-so-far
