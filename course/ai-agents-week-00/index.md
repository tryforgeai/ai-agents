# AI Agents Week 00 — The loop, the governor, and the lamp（2026-09-12）

主题：*AI Agents — The loop, the governor, and the lamp*
形式：**Public Meetup** · SupportVectors AI Lab
定位：不在编号周次序列内，单独成册（Week 00 = agent 线的起点）

> 标题页副文案：
> *Morning: the ideas. Afternoon: an engine on your own laptop — and a newsletter it cannot be trusted to write alone.*

上午讲思想，下午在自己的笔记本上跑一个 engine；产出物是一份 newsletter——而**它不能被单独信任去写完**（这句是全天的题眼：agent 能跑，但必须有人/有闸在中间）。

## 目录

| 文件 | 内容 |
| --- | --- |
| ⭐⭐ [`summary.zh.md`](summary.zh.md) | **总结**（先看这个）：按概念组织 —— 四个定义 / 两个方向的算术 / 四条 pipeline / 四条停止规则 / 失败模式图鉴 / 可用检查表 / 金句速查 |
| 📤 [`summary.en.md`](summary.en.md) | **英文版 · 给团队分享用** —— 内部备忘录形式，知识分享取向，不含个人待办 |
| [`notes.zh.md`](notes.zh.md) | **现场笔记**：按 ACT I–VII 七幕、逐页记录（2900 行） |
| ⭐ [`ref-harness-engineering.zh.md`](ref-harness-engineering.zh.md) | **参考阅读**：Addy Osmani《Agent Harness Engineering》精读 —— p.21 那句话的出处与完整展开 |
| [`avaloka-mapping.zh.md`](avaloka-mapping.zh.md) | Avaloka 映射占位：Agent Capability / Evidence·Memory·Tool·Eval / 落地清单 |
| [`uploads/slide-01-title.png`](uploads/slide-01-title.png) | p.1 标题页截图 |
| [`uploads/slide-02-journey.png`](uploads/slide-02-journey.png) | p.2 七幕路线图 |

## 全天七幕（p.2）

| | 幕 | 标题 |
| --- | --- | --- |
| 谷 | ACT I | Myth to Machine |
| 峰 | ACT II | What an Agent Is |
| 谷 | ACT III | Why Now |
| 峰 | **ACT IV** | **The Loop & the Governor** |
| 谷 | ACT V | The Engine Room |
| | *lunch* | （落在 ACT V 与 VI 之间） |
| 峰 | ACT VI | The Newsletter |
| 谷→出口 | ACT VII | Anatomy & Landscape |

## 三个词（开场先记，含义待现场校准）

| 词 | 初步猜测 | 现场确认 |
| --- | --- | --- |
| **The loop** | agent 的基本循环：perceive → decide → act → observe，以及它何时该停 | ACT IV |
| **The governor** | 调速器——限制 loop 的东西：预算、步数、置信阈值、人类审批闸 | ACT IV |
| **The lamp** | 疑似阿拉丁神灯 | ✅ **ACT I, p.9 — Aladdin's lamp**。精灵 = 委托（delegation）的最古老形态：说出目标，一个你不理解的力量照**字面**执行 |

> 「调速器」这个词在 Week 12（语义缓存，ACT II）出现过一次，指用 γ/τ 控制决策的松紧。今天若同名，注意是否同一套直觉在 agent 层面的复用。

## 相关

- 前置：[`../week_12/index.md`](../week_12/index.md)（语义缓存 · 决策门槛 σ/γ/τ）
- 前置：[`../week-09.zh.md`](../week-09.zh.md)（OKF + Secure Retrieval，agent 读什么）
- 模板：[`../../templates/weekly-note.md`](../../templates/weekly-note.md)
