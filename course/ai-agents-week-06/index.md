# AI Agents Week 06 · Toolcraft II：插头、门与协议

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-10-25（周日，11:00–19:45）
状态：**已下课**。课前笔记、deck 精读、两篇论文精读、课堂补充（截至 19:58，Act I–XI + Coda + 三星推理分享）、summary 课后版都已完成；p.123–130 和作业待看录播补。讲义 27 页（Asif Qamar，first draft 2026-10-25）。

> **The protocol carries capability; the architecture around it carries trust.**
> **Labels request. Boxes enforce.**

## 目录

| 文件 | 内容 |
| --- | --- |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览：时间线、11:15 复述题、课前检查、三句主线 |
| [notes.zh.md](notes.zh.md) | 按 Act 的详细笔记（Preface → 13 扇门 → 协议传记 → 盒子 fail open → 五问），每节留「课堂补充」；**§14 = 三星推理分享**（KV cache、vLLM / SGLang / Dynamo、内存金字塔、AI Memory Node 实测） |
| [summary.zh.md](summary.zh.md) | **今天学了什么（课后版）**：label 四站、门的揭晓、门 1–4 结果、三星推理分享、Act IV–XI 与 Coda、两段课的接线、候选技巧 #64–#85、项目落地、待办 |
| [learned-so-far.zh.md](learned-so-far.zh.md) | **课中时间线**（11:15–19:58，逐条带时间）：学到的概念、门 1–4 结果、自己串起来的几条、课后待办 |
| [lab-log.zh.md](lab-log.zh.md) | **Field notebook**：环境命令、Hermes 配置、13 扇门的预测表 + 记录模板；课后 FinePrint 五问自查 |
| [toolcraft-details.pdf](toolcraft-details.pdf) | **课堂 deck**（130 页）；页码索引、小测预答、deck 精读（讲义没有的数字、讲义与 deck 的 10 处差异、🔒 折叠的门揭晓）在 notes 末尾。⚠️ p.28–50 是门的揭晓，开门前别看 |
| [../../Landscape of AI Agent Architectures 论文精读笔记.md](<../../Landscape of AI Agent Architectures 论文精读笔记.md>) | **本周论文 ①**：`arXiv:2404.11584`（Masterman et al. 2024）LLM 单 / 多 agent 架构综述；原文 [2404.11584v1.pdf](papers/2404.11584v1.pdf) |
| [../../Multi-Agent Deep RL Survey 论文精读笔记.md](<../../Multi-Agent Deep RL Survey 论文精读笔记.md>) | **本周论文 ②**：Gronauer & Diepold 2022，MARL 综述；原文 [s10462-021-09996-w.pdf](papers/s10462-021-09996-w.pdf) |
| `uploads/` | lesson plan PDF、板书照片、课上 deck 截图（按 `HHMM-主题.png` 命名；课程材料，只留本地不进 git） |
| [Week 05](../ai-agents-week-05/index.md) | 上周：Lab 揭晓 + Tools Prelude + Inference |
| [全课程阅读清单](../reading-list.zh.md) | 共用阅读索引 |

## 承接 Week 05 的待办

- [ ] 候选技巧 #52–#63 写进 kit；kit doctor 加 MCP 检查
- [ ] 日历 skill 补缺口（evidence、`calendar_unreadable`、校验器、触发测试…）
- [ ] FinePrint：扩任务、接真模型做端到端
- [x] Toolcraft deck 没讲到 → 本周就是 Toolcraft Part II

## 课前（今天上午）

- [ ] 默写 label 的四个决定（lesson-plan 里有答案，先别看）
- [ ] Hermes 0.22.2 确认，**不要 update**；下载并 `uv sync` strangers-toolbox；配 Hermes stanza
- [ ] Node ≥22.19 + MCP Inspector 2.11.0
- [ ] 扫一眼 notes §1（Decision Ledger）和 §2（门的规则）
- [ ] 记住店规（notes 附录）：先给积分；退款 = 金额 + $15；手续费不对顾客提

## 本周待办（课后）

- [ ] lab-log：13 扇门全部记录，Verify 分数填齐
- [x] Act III 揭晓后更新 summary（课后版已完成）
- [ ] 必读 5 篇（notes 末尾清单）
- [x] 本周论文精读 ×2（Landscape、MARL 综述）——两篇配对读：LLM 多 agent 的每个坑在 MARL 里都有名字
- [ ] 精读笔记里 ⚠️ 待核：Guo et al.（`2403.12482`）里「轮换领导通信成本最低」和 Figure 5「选举 leader 成本最高」是否同一条件
- [ ] FinePrint 按五问改：idempotency key、工具注解、钉版本、stateless + kill-a-replica
- [ ] 候选技巧 #64–#85 写进 kit
- [ ] 作业（19:15 公布）：

## 课程顺序

Skills（W3–W4）→ Lab 揭晓 + Tools + Inference（W5）→ **Toolcraft II（W6）** → 自动提示词优化：PromptCraft / GEPA（W7）

## 学习完成清单

- [x] 课前笔记（lesson-plan / notes / summary / lab-log 框架）
- [x] 课堂补充填完（p.123–130 除外）
- [ ] 门全部跑完并记录
- [x] summary 课后版


## 10 月 27 日追加 Lab（10 月 29 日补记）

[MCP Guardrails 实操记录](lab-log.zh.md#2026-10-27--mcp-guardrails-lab2026-10-29-补记)：A 假密钥外传成功、B 敏感读取拦截已确认；C 观察到模型拒绝，描述清洗与输出脱敏仍需独立验证。包含三个终端的启动命令、排错、服务端检查与脱敏代码讲解、实现局限和待测清单。此次追加不代表门 5–13、讲义末页及作业已补齐。


下一周：[Week07 · 自动提示词优化预习与实验记录](../ai-agents-week-07/index.md)（11 月 1 日课前准备）。
