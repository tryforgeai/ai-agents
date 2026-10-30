# Verifiable Commerce Agents

Rosso 的 AI Agents Bootcamp capstone 项目跟踪目录。

- 建档日期：2026-10-26（America/Los_Angeles）
- 当前阶段：proposal v2 已归档，执行进度待核实。
- 计划来源：[Proposal v2](proposal/Verifiable_Commerce_Agents_Capstone_Proposal_v2.pdf)，文档日期 2026-10-24。
- 项目起始日、截止日、团队分工：待确认。项目 Week 1–8 不等于 Bootcamp 课程周次。

## 从这里继续

| 文件 | 用途 |
| --- | --- |
| [PROGRESS.md](PROGRESS.md) | 当前状态、下一步、问题和每次推进的日志 |
| [ROADMAP.md](ROADMAP.md) | Proposal 的八周计划、验收关卡和降级方案 |
| [SCOPE.md](SCOPE.md) | 项目范围、实验设计和交付标准 |
| [DECISIONS.md](DECISIONS.md) | 已确认决定与待确认选择 |
| [tau2-learning-notes.zh.md](tau2-learning-notes.zh.md) | tau2 源码学习、Claude 笔记核验、capstone 接入设计；优先读第 10–17 节 |
| [tau2-source-audit.json](tau2-source-audit.json) | 固定 commit 的任务评分项与无参考写操作任务统计 |
| [proposal/](proposal/) | 原始提案的本地副本 |

## 项目目标

构建模拟在线商店，让 agent 处理优惠券、退货和换货。以数据库最终状态与 typed action log 验证行为，不依赖 agent 的自然语言自述。共享 policy rules 同时服务于整段对话评估、DSPy metric 和单步 GRPO reward。

## 跟踪约定

- 每次推进更新 PROGRESS 的当前状态、下一步和日志；完成项附代码、测试、trace 或报告证据。
- 状态使用：待核实 / 未开始 / 进行中 / 阻塞 / 已完成；不把提案中的计划记为已实现。
- 需求或技术选择发生变化时写入 DECISIONS，并同步范围与路线图。
- 既有 `../fineprint-mcp/` 可作为复用候选；尚未审计它与本项目的关系，不计为本项目已完成工作。
- 提案中的模型名、软件版本和协议版本是拟选配置，实施前需验证兼容性与可用性。
