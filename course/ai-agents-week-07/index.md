# Week 07 · Gradient Descent for Sentences

**主题：自动提示词优化——Workshop、Frontier、Tether。**

准备于 2026-10-29；计划学习日 **2026-11-01（周日）**，按用户所说的本周日推定，课程安排仍以 portal 为准。状态：**课前准备，尚未上课或运行本周 lab**。

来源：[lesson plan 原文](uploads/fall-agents-week-7-lesson-plan.pdf)，Asif Qamar，first draft 2026-10-27。物理 PDF 共 34 页，正文印刷页码 1–32；笔记统一引用印刷页码（物理页码 = 印刷页码 + 2）。原文只在本地保留；原始 `course/fall-agents-week-7-lesson-plan.pdf` 也保留。

## 从这里开始

| 文件 | 用途 |
| --- | --- |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 周日速览、时间安排、课前清单、不提前开实验的规则 |
| [notes.zh.md](notes.zh.md) | 中文概念预习；下午内容折叠，便于先做体验再读机制 |
| [lab-log.zh.md](lab-log.zh.md) | Workshop / Exam 实操记录模板；不预填结果或答案 |
| [learned-so-far.zh.md](learned-so-far.zh.md) | 上课时按时间补充，区分课堂事实和自己的推断 |
| [summary.zh.md](summary.zh.md) | 课前主线与课后总结模板；Owl 五句话等待课堂揭晓 |
| [reading-list.zh.md](reading-list.zh.md) | 讲义的四篇必读、选读顺序与核实清单 |
| `kits/` | 两套实验各放独立目录；未下载，不猜启动命令 |
| `exports/` | 保存实验导出的 Markdown 和记录；只在本地保留 |
| `uploads/` | 讲义、Reservoir、卡片、课堂截图，只在本地保留 |
| `papers/` | 后续论文原文，只在本地保留 |

## 周日前必须完成

- [ ] portal 下载 `harrisons-workshop.zip` 和 `genies-exam.zip`，分别解压到 `kits/`。
- [ ] 按各 README 启动到首页；可用无 key 的 recorded replay。不要提前打开 bench / door。
- [ ] 下载 Reservoir、workshop card、exam card；目前本地只找到 lesson plan。
- [ ] Week06 的 Stranger’s Toolbox 若早于 10 月 26 日，按讲义要求更新；确认 No Castle Without Walls 材料。
- [ ] 复述工具 label 五问：何时用、怎么调、失败后怎么办、能否重试、谁强制边界。
- [ ] 先读 [速览](lesson-plan.zh.md)，配对后再做核心路径。

**两条时间底线：14:30 Deep Dive；19:30 Owl。** Workshop 核心 Bench 2→4→7→9→10；Exam 核心 A1→A3→B1→C1。Bench 10 依赖 Bench 2 的最终 prompt，需老师解锁；Bench 11 集体演示。

衔接：[Week06](../ai-agents-week-06/index.md) 的手工工具说明优化与安全执行边界 → 本周对文本参数做自动搜索和评估 → 讲义预告 Week08 Memory。
