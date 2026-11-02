# 勘误核对：W01–W06 errata × 我的笔记

核对日期：2026-11-01
依据：各周文件夹里的 `agents-fall-week-X-errata.pdf`（讲师 Asif Qamar 课后发布）
范围：各周文件夹里的 .md，根目录的论文精读笔记，并在整个 vault 里按关键词搜了一遍。✅ **2026-11-01 已全部改完**（❌ 14 条 + ⚠️ 12 条）。改动处都标了「✏️ 勘误 W? #?」，在 Obsidian 里搜 `✏️ 勘误` 就能找到。

> Week 1 的勘误针对的是第一天的课，所以命中的大多在 `ai-agents-week-00/`。

## 总览

| 周 | 勘误条数 | ❌ 笔记里确实写错 | ⚠️ 建议补注 |
| --- | --- | --- | --- |
| W1 | 21 | 6 | 2 |
| W2 | 33 | 1 | 1 |
| W3 | 23 | 2 | 3 |
| W4 | 16 | 3 | 2 |
| W5 | 25 | 2 | 3 |
| W6 | 21 | 0 | 2 |

各周勘误的最后一节都列了「听起来不对、其实是对的」说法，**笔记里没有一条被我改错**。

---

## ❌ 必须改（14 条）

### 影响作业或代码的（优先改）

- [x] **W4 #2 · SKILL.md 顶层不能写 `version:`**。规范只允许 6 个字段：必填 `name`、`description`，可选 `license`、`compatibility`、`metadata`、`allowed-tools`。顶层写 `version` 会被 claude.ai 上传、Skills API 和打包器直接拒收（"Unexpected key(s)"），只有 Claude Code 会忽略它。正确写法是 `metadata: { version: "1.0" }`，版本号要加引号。
  - 要改的位置：`ai-agents-week-04/notes.zh.md:330, 338, 345, 375, 386, 391`
  - 一并修正：`ai-agents-week-03/notes.zh.md:637` 说标准只约束两个字段，实际是 6 个字段、其中 2 个必填
  - 已查：`skills/` 下我自己的 skill（paper-deep-read、startup-idea-scout）都没有顶层 `version`
- [x] **W4 #6 · 注意力公式**：`ai-agents-week-04/notes.zh.md:68` 写的是 `A = softmax(⟨K,Q⟩/√d)·V`（照抄板书），应为 **`Attention(Q,K,V) = softmax(QKᵀ/√d_k)·V`**。如果写成 KQᵀ，softmax 就会沿错误的轴归一化。
- [x] **W3 #1 · 已加载的 skill 正文每一轮都要付 token，不是只付一次**：`ai-agents-week-03/survey-notes.zh.md:120` 写「← 只付一次」。正文加载后会一直留在历史里，**之后每轮都要再付**，只有在压缩上下文时才可能被换掉。前缀缓存能让每轮便宜一些，但每轮还是要付。

### 概念错误

- [x] **W1 #8 · 课上讲的是四种记忆（CoALA），不是 Tulving 的三分法**。四种是 working、episodic、semantic、procedural；working memory 出自 Baddeley & Hitch（1974），分类框架出自 CoALA（`2309.02427`）。Tulving 只区分了 episodic 和 semantic。
  - 要改的位置：`ai-agents-week-01/delta.zh.md:24, 26`、`ai-agents-week-01/summary.en.md:12`、`log-2026-09-20.md:23`、`reading-list.zh.md:63`
  - `ai-agents-week-03/notes.zh.md:437` 写对了，可以照着改
- [x] **W5 #12 · Python 是强类型 + 动态类型，不是「弱类型」**。`abracadabra(x)` 的问题是**没有类型标注**。
  - 要改的位置：`ai-agents-week-05/notes.zh.md:395, 398, 548`、`summary.zh.md:65`、`lab-log.zh.md:40`
- [x] **W5 #24 · MCP server 是一个角色，不是 web server**：`ai-agents-week-05/notes.zh.md:949`。MCP server 也可以走 stdio，由 host 以子进程启动；FastMCP 的 `mcp.run()` 默认就是 stdio。
- [x] **W4 #13 · 「consequences」这一栏来自四人帮（GoF，1994），不属于 Alexander 的格式**。Alexander 的模式只有 context / problem / forces / 用 "Therefore:" 引出的 solution。模式目录在 *A Pattern Language*（1977），*The Timeless Way of Building*（1979）讲的是背后的理论。
  - 要改的位置：`ai-agents-week-04/notes.zh.md:451`、`ai-agents-week-03/notes.zh.md:337, 789–791`、`ai-agents-week-03/lesson-plan-精读.zh.md:737`
- [x] **W3 #14 · Terminal-Bench 从约第 30 名升到前五，是 LangChain 的 agent 跑出来的，模型一直是 GPT-5.2-Codex**。分数从 52.8% 到 66.5%，只改了 harness；这次和「离开 Claude Code」没有关系。
  - 要改的位置：`ai-agents-week-00/notes.zh.md:579`
- [x] **W1 #20 · 「重试五次」对应 0.65⁶，不是 0.65⁵**：`log-2026-09-20.md:107`。0.65⁵ 是 1 次尝试加 4 次重试（88.4%）；重试五次是 1 − 0.65⁶ ≈ **92.4%**，正是这个数超过了供应商的 90%。

### 史实、出处错误

- [x] **W1 #10 · 百万步零错误是 2025 年 11 月的结果，不是 2026 年**：MAKER，Meyerson et al.，`2511.09030`，任务是 20 盘汉诺塔，共 1,048,575 步。
  - 要改的位置：`ai-agents-week-00/summary.zh.md:334`、`notes.zh.md:1395, 2897`。这两处原本是待查项，现在可以关掉
- [x] **W1 #4 · harness 的词源**：harness 来自古法语 *harneis*（「装备、军需」），本义是「装备好」，不是「驯服动物」；拉牲口的意思是后来才有的。
  - 要改的位置：`ai-agents-week-00/summary.zh.md:89`、`notes.zh.md:1286, 1326`
- [x] **W1 #14 · Orunmila 是 orisha（智慧与占卜之神），不是「使者」**；至高神是 Olodumare。
  - 要改的位置：`ai-agents-week-00/notes.zh.md:156, 250, 378`
- [x] **W1 #15 · 猴面包树那句谚语出自 Akan / Ewe，不是约鲁巴谚语**。
  - 要改的位置：`ai-agents-week-00/notes.zh.md:20, 272`、`summary.en.md:204`
- [x] **W2 #25 · 情人节派对是事先设定的，不是自发产生的**：`Generative Agents 论文精读笔记.md:14`。Isabella 被设定要办派对，Maria 被设定喜欢 Klaus；邀请、消息传播和到场才是涌现出来的。同一文件第 257–259 行写对了，只有开头这句和后文矛盾。

---

## ⚠️ 建议补注（不算错）

- **W1 #5** `ai-agents-week-00/summary.en.md:204`、`notes.zh.md:767`：「有新信息」只是多 agent 能多出价值的**必要条件，不是充分条件**（Ao, Gao, Simchi-Levi `2603.26993` Prop. 6）
- **W1 #6** `ai-agents-week-00/notes.zh.md:60`、`index.md:19`、`reading-list.zh.md:407`：Top-30 → Top-5 的数据来自 LangChain 2026-02-17 的博客，Osmani 只是评论者
- **W2 #1** `ai-agents-week-02/notes.zh.md:25`：小标题「LLM = 编码器–解码器」不准确。语言模型 = 给 token 序列分配概率的模型，GPT 是只有解码器的结构
- **W3** SkillsBench 的数字和勘误版本不一致：勘误写精选 skill 让成功率从 33.9% 升到 50.5%，自生成 skill 降 8–12 分，1–3 个 skill 涨 18–19 分。笔记写的是 +16.2 / −1.3，散在 W3 notes、survey-notes、W4 notes、reading-list 几处
- **W3** `ai-agents-week-00/ref-harness-engineering.zh.md:47`：容易读成 Terminal-Bench 那次用的是 Opus 4.6
- **W3** `ai-agents-week-03/notes.zh.md:430, 436`：补一句「正文加载后一直留在历史里」
- **W4 #14** `ai-agents-week-03/notes.zh.md:807`：说 89.5% 的 skill 没有脚本，但按勘误口径（脚本、库、应用合计）约 86% 不含可执行代码
- **W5 #13** `ai-agents-week-03/survey-notes.zh.md:421`：scripts/ 默认是拿来执行的，但不禁止读
- **W5 #3** `ai-agents-week-01/delta.zh.md:92`：笔记说「脚本自己实现 MCP client 不该这么做」，勘误认为这是正当做法，可以省掉每轮的上下文开销
- **W5 #12** `ai-agents-week-05/lab-log.zh.md:56`：FastMCP 默认会把兼容的值强制转换（如 `"10"` → `10`），要设 `strict_input_validation=True` 才会拒收
- **W6 #7** `ai-agents-week-06/notes.zh.md:1865`：Gorilla 论文还做了 retrieval-aware training，「新工具就得重新微调」这个限制已经部分解决
- **W6 #11** `ai-agents-week-06/notes.zh.md:1141`：Beck 的地铁图 1931 年设计、**1933 年发布**
