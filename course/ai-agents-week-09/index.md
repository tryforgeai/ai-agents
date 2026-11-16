# AI Agents Week 09 · A Garbage Collector for the Mind（上）：Memory 是什么

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-11-15（周日）
讲师：Asif Qamar · 讲义 37 页（Weeks 9–10 共用，first draft 2026-11-11）
议程：Orientation 11:00 → Experientials 12:00 → Deep dive 14:30 → Owl of Minerva 19:30 → Speakeasy 20:00
状态：**上课中**。上午 Prototype 11 个实验 + 下午 Act I（到 deck p.51）已记；Memory Palace 一楼三个房间已做完（见 lab-log）；Owl、Speakeasy 待补。

> **Memory is not storage; it is policy.**
> **The harness remembers, not the model.**

## 目录

| 文件 | 内容 |
| --- | --- |
| [summary.zh.md](summary.zh.md) | **今天学了什么（课中版）**：实验答案、Act I 要点、课上问题、今天创建的文件、待办 |
| [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md) | **学习笔记（W9 + W10 全本）**：四层分类、四个操作、Smallville 打分与半衰期、heap/GC、compaction amnesia、回收三难、两个时钟、ADK 前缀、写策略、plant–distract–probe、治理、Build/Proof 代码、两个 Postscript、阅读清单、自测 12 题 |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览 + 复述题 |
| [lab-log.zh.md](lab-log.zh.md) | 动手记录：Hundred-Million-Year Prototype 11 个实验 + Palace 一楼 |
| [notes.zh.md](notes.zh.md) | 课堂笔记（白板 + deck） |
| [learned-so-far.zh.md](learned-so-far.zh.md) | 课中时间线 |
| [讲义 PDF](Weeks%209-10%20Lesson%20Plan%20-%20A%20Garbage%20Collector%20for%20the%20Mind.pdf) | 原文 |
| `uploads/` | 实验手册、deck 截图（只留本地，不进 git） |
| `genies-memory-palace/` | Memory Palace kit（只留本地，不进 git） |
| `CURSOR_RULES_FOR_WORKSHOP/` | 讲师给 workshop 用的 Cursor IDE 规则（`.cursor/rules/*.mdc`，14 条：Python 风格、src 布局、文件头、测试、FastAPI、LLM 技术栈等） |
| [memory-storage-guide.zh.md](memory-storage-guide.zh.md) · [English](memory-storage-guide.md) | 课外：向量库 / 关系库怎么选、metadata 为什么需要、chunking 与写入流程、Qdrant vs Postgres、对权限检索的补充 |
| [LoRA 微调入门](../../learning/2026-11-15-fine-tuning-lora/README.md) | 课外：课上问到微调，写的学习代码 + 设计图 |
| [记忆库 metadata 与过滤](../../learning/2026-11-15-memory-store-filters/README.md) | 课外：Qdrant payload vs Postgres 列；写入时填字段、切分时继承、取代不删除、as-of 查询、被遗忘权（Qdrant 版已跑通） |
| [Week 10](../ai-agents-week-10/index.md) | 下周：Act II + Act III |
| [Week 08](../ai-agents-week-08/index.md) | 上周：Genie's Bazaar |

## 课外：权限感知检索、MemGPT 与 System 5

课间问答的产出（源自 LLM and Enterprise RAG Bootcamp 的 Module 5；原件同时存放在那个项目的 `course/ai-agents-week-09/`）。现场问答记录见 [notes.zh.md](notes.zh.md) 末尾「课外问答」一节。

| 文件 | 内容 |
| --- | --- |
| [permission-aware-retrieval.md](permission-aware-retrieval.md) | 权限感知检索完整版（英文，可分享） |
| [permission-aware-retrieval.zh.md](permission-aware-retrieval.zh.md) | 完整版中文翻译 |
| [permission-aware-retrieval-summary.md](permission-aware-retrieval-summary.md) | 8 条精简版：做什么 + 为什么（中英对照） |
| [permission-aware-retrieval-slides.html](permission-aware-retrieval-slides.html) | 11 页 HTML 幻灯片（含 References 页） |
| [memgpt-as-system-5.md](memgpt-as-system-5.md) | 提交稿：MemGPT 能否作为 System 5 的基础（英文） |
| [共享文档（Summary / English / 中文）](https://claude.ai/artifact/Ced6Q82y5Dwfi4YDnQkgD1) | 在线版本 |

相关课程笔记（LLM and Enterprise RAG Bootcamp）：

- [Week 09 · Module 5 Enterprise Entitlement-RAG（§十一）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_09/week-09.zh.md)
- [Week 06 · Guardrails（第 ⑧ 条：ACL at retrieval, not after）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_06/week-06.zh.md)
- [Week 10 · Access control（pre-filter, never post-filter）](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_10/week-10.zh.md)
- [AI Agents Week 00](../ai-agents-week-00/index.md)

待确认：

- [x] p.6「last week's owl」= 上周 Owl of Minerva 的收尾五行 → 新 deck p.7「Week 8, in five lines」
- [x] 「six headlines」= 今天的 Headline 1–6（p.12 边界 → p.19 Memory is not storage; it is policy）
- [ ] 课程里「System 5」的定义是否就是 Beer 的 VSM（今天的 deck 和讲义都没出现，需问讲师）
- [ ] Letta 是否支持只读 memory block（查当前文档）
- [ ] References 里 5 篇论文的出处信息（凭记忆引用，未核对）

## 本周待办

- [x] 下载 Memory Palace kit；一楼 Foyer / Flood / Shoelaces 完成（结果见 lab-log）
- [ ] 下载手册 `fall-agents-week-9-memory-palace-manual.pdf` 放进 `uploads/`
- [ ] 必读：Generative Agents §4（重读）、MemGPT、Memory Survey、Zep、Lost in the Middle
- [ ] W8 尾巴：Taxonomy / Library / Gymnasium 三格 worksheet 还没填
- [ ] 想清楚 capstone 要哪种 compaction 边界机制（阶梯 / flush / 辅助模型）

## 课程顺序

Skills（W3–W4）→ Tools（W5–W6）→ Prompt 优化（W7–W8）→ **Memory（W9–W10）** → Harness → Agentic 架构 → 评测周
