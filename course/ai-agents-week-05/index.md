# AI Agents Week 05 · Lab 揭晓 + Tools + Inference

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-10-18（记录整理于 2026-10-19）
状态：**已上完**。实际讲了四块：**What Did We Miss?**（W3 Lab 揭晓）→ **Capstone Briefs** → **Tools Prelude** → 客座 **The Inference Story**。原计划的 **Toolcraft** 没讲到，顺延到下周。

## 目录

| 文件 | 内容 |
| --- | --- |
| [summary.zh.md](summary.zh.md) | **概念总结**：定义、机制、取舍、和 kit 的接线、新候选技巧 #52–#63、开放问题 |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览：时间线和主线 |
| [notes.zh.md](notes.zh.md) | 逐页速记 + 课堂问答框（KV cache、推理引擎、NVLink、RDMA、all-to-all…） |
| [lab-log.zh.md](lab-log.zh.md) | 实操：W3 skill 复跑；FastMCP quickstart；类型标注对照实验 |
| [../../capstone/fineprint-mcp/](../../capstone/fineprint-mcp/README.md) | 当天做的 FinePrint MCP 原型（4 工具 + 独立校验器） |
| `uploads/` | 讲义、截图 |
| [Week 04](../ai-agents-week-04/index.md) | 上周：Skillcraft（续） |
| [全课程阅读清单](../reading-list.zh.md) | 共用阅读索引 |

## 承接 Week 04 的待办

- [ ] 作业 1：同一个 skill 装进 Hermes 和 Claude Desktop，各跑三个案例
- [x] Lab `when-the-time-is-right` 复跑：100/100（实验 1）
- [ ] 保留 Week 02 最好的 Oracle prompt 及隐藏测试失败

## 本周待办

- [ ] 候选技巧 #52–#63 写进 kit 和 vault 的中英文 4 个文件；kit doctor 加 MCP 检查
- [ ] 日历 skill 补缺口（evidence、`calendar_unreadable`、notes、校验器、触发测试、traps.md、run log）
- [ ] Capstone：确认 BYOP 是否允许、查 Rakuten 条款 → 定 FinePrint 或 Travel → W12 提案（2–3 页）
- [ ] FinePrint：扩任务、接真模型做端到端测试

## 课程顺序

Skills（W3–W4）→ **Lab 揭晓 + Tools + Inference（W5）** → Toolcraft → 自动提示词优化（DSPy / MIPROv2 / GEPA）

## 学习完成清单

- [x] notes 整理完
- [x] summary 写完
- [x] lab 跑完并记录
