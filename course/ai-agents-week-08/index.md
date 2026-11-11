# AI Agents Week 08 · The Genie's Bazaar：prompt 优化能做什么、不能做什么

课程：**AI Agents Bootcamp · SupportVectors AI Lab · Fall Cohort**
上课日：2026-11-08（周日，排灯节缩短版 11:15–17:00）
讲师：Asif Qamar · 学生手册 30 页（first draft 2026-11-08）
状态：**上课中**。手册和 kit 已精读，学习笔记已写好。

> **An optimizer can only change what goes into the prompt. It cannot change the weights of the model that reads the prompt.**
> 先判断缺的是信息、知识还是能力，再决定买哪种药。

## 目录

| 文件 | 内容 |
| --- | --- |
| [lesson-plan-精读.zh.md](lesson-plan-精读.zh.md) | **学习笔记**：地图、GEPA/MIPROv2/GRPO、会自我解释的 metric、记分板与噪声、两个 Stall 和两扇 Door（含源码细节和隐藏答案折叠）、四格诊断 |
| [lesson-plan.zh.md](lesson-plan.zh.md) | 听课速览 + 复述题 |
| [lab-log.zh.md](lab-log.zh.md) | 动手记录：worksheet + 每站的预测框和记分板 |
| [notes.zh.md](notes.zh.md) | 课堂笔记（白板 + deck） |
| [learned-so-far.zh.md](learned-so-far.zh.md) | 课中时间线 |
| [学生手册 PDF](Week%208%20-%20The%20Genies%20Bazaar%20student%20manual.pdf) | 原文 |
| `genies-bazaar/` | kit（uv + DSPy） |
| [Week 07](../ai-agents-week-07/index.md) | 上周：Prompt 优化 / GEPA（第一部分） |

## 本周待办

- [ ] 跑 kit：`uv sync` → `.env` → `uv run pytest -q`
- [ ] Stall 1 → Stall 2 → Door A →（Door B）；每站先写预测
- [ ] 填 worksheet 和下课前五问
- [ ] Week 7 尾巴：录播补 p.60 之后 + Owl 五行；Bench 9 / 10
- [ ] 读 GEPA（2507.19457）、MIPRO（2406.11695）、PopQA（2212.10511）

## 课程顺序

Skills（W3–W4）→ Tools + Inference（W5）→ Toolcraft II（W6）→ Prompt 优化 I / GEPA（W7）→ **Prompt 优化 II / 边界（W8）**
