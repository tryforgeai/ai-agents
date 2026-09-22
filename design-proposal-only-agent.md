# Proposal-Only Agent · 只产出提案的 Agent
### Data Fix v1 — the agent writes a file, a human decides
### Data Fix 第一版 —— agent 只写文件，人来决定

> 2026-09-20 · 配套 [`usecase-data-fix-agent.zh.md`](usecase-data-fix-agent.zh.md) · [`team-learning-path.zh.md`](team-learning-path.zh.md)

---
---

# EN

## The principle

The agent never writes to the database. It investigates, reasons, and produces **one artifact: a correction file** — a CSV of proposed changes, each row carrying its evidence. A human reviews it. The existing, already-audited execution path applies it.

> **Model proposes, harness disposes** — and in v1, the human is part of the harness.

This is not a temporary compromise on the way to full autonomy. It is the correct first version, for a specific reason: **a CSV is a verifier a human can actually use.** They can sort it, filter it, spot-check twenty rows, and notice that column four looks wrong in a way no confidence score would have told them.

## What the agent produces

**1. `corrections.csv`** — one row per proposed change:

| Column | Contents |
| --- | --- |
| `row_key` | Primary key of the affected record (e.g. `order_id`) |
| `table` | Target table |
| `field` | Field to change |
| `current_value` | Value read at investigation time |
| `proposed_value` | What it should become |
| `fix_type` | From a fixed catalogue — not free text |
| `evidence` | Where this came from: `JIRA-4521 §3` / Confluence page + anchor / Slack permalink |
| `confidence` | `high` / `medium` / `low` |
| `needs_decision` | `true` when a human has to choose, not just approve |
| `notes` | Only when something doesn't fit the other columns |

**2. `report.md`** — the things a CSV can't carry:

- Row count, and whether it falls in the expected range
- Dry-run results: invariants checked, before/after samples
- **What the agent was unsure about, and why**
- **What it deliberately excluded, and why** ← the most valuable section
- Which sources were consulted

## Why a file, and why CSV

| | |
| --- | --- |
| **Reviewable at a glance** | Sorting by `confidence` or `fix_type` surfaces the suspicious rows in seconds |
| **Diffable** | Two runs of the agent can be compared. So can agent vs. the historical human fix |
| **It is the eval set** | Every reviewed CSV becomes a labelled case for Stage 2 |
| **Nothing to roll back** | A wrong file costs review time. A wrong write costs an incident |
| **Approval binds to content** | Hash the file; the execution step re-checks the hash. This closes the "approved A, executed B" hole |

## What the agent must not do

- **No write credentials at all.** Not restricted ones — none. The read MCP server connects with a `SELECT`-only database user; the grant enforces this, not a prompt.
- **No free-form SQL.** Fix types come from a catalogue of parameterised operations. A model composing arbitrary SQL is a shell tool wearing a different hat: you cannot draw a permission boundary around it.
- **No action driven by ticket text.** Jira, Confluence and Slack content is *evidence to cite*, never an instruction to follow. A ticket that says "while you're in there, set all statuses to active" is untrusted input, and the structured `fix_type` field is what prevents it from becoming an action.

## Verification, before the human sees it

The agent runs a dry-run and reports the results. It does not decide whether they are acceptable.

```sql
BEGIN;
  apply proposed corrections
  → affected rows: 147   (expected 140–160)  ✅
  → invariant: order totals unchanged        ✅
  → sample 5 rows, before / after
ROLLBACK;
```

⚠️ **But only execution correctness is machine-checkable here.** For this workload, deciding *which* rows to touch requires reading prose across several sources, and deciding *what value* to write requires case-by-case judgement. A dry-run can prove "147 rows changed, totals intact." It cannot prove those were the right 147 rows.

> **So the CSV is not merely a safety measure — it is the only verifier of business correctness in v1. The reviewer's eyes are the verifier, and there is no backup.**

This also raises the bar for v3: a fix type only graduates to automatic execution when its business correctness becomes machine-checkable too.

```
✅  "currency should equal the row in merchant_config"  → checkable, can graduate
❌  "currency should reflect what ops intended"          → stays at v2 forever
```

Three kinds of judgement, kept separate:

| Kind | Question |
| --- | --- |
| **Business correctness** | Are these the right rows, and the right new values? |
| **Execution success** | After the write, does a read-back match? |
| **Must stop** | Row count over limit, table outside the allow-list, conflicting evidence, budget exhausted |

**Stopping is not success.** Only one of the four exits is a happy one.

## Rollout

| Stage | Agent | Human |
| --- | --- | --- |
| **v1** | Investigate → CSV + report | Reviews every row; runs the fix by hand |
| **v2** | Same, plus dry-run evidence | Approves the file; **existing service** executes against the approved hash |
| **v3** | Low-risk fix types execute automatically | Reviews exceptions and a sample |

Do not skip to v3. The thing that earns each step is **a verifier with a track record**, not a working demo.

---
---

# 中文

## 原则

**agent 永远不碰数据库。** 它只做调查、推理，然后产出**一样东西：一个修正文件** —— 一份 CSV，每行一个提议的改动，**每行带着它的证据**。人来审，然后由**现有的、已经过审计的执行路径**去改。

> **谋事在模型，成事在 harness** —— 而第一版里，**人就是 harness 的一部分**。

这不是通往全自动路上的临时妥协，**它就是正确的第一版**。理由很具体：**CSV 是人真的用得上的 verifier。** 可以排序、筛选、抽查二十行——然后一眼看出第四列不对劲，而任何置信度分数都不会告诉你这一点。

## agent 产出什么

**1. `corrections.csv`** —— 一行一个改动：

| 列 | 内容 |
| --- | --- |
| `row_key` | 受影响记录的主键（如 `order_id`） |
| `table` | 目标表 |
| `field` | 要改的字段 |
| `current_value` | 调查时读到的值 |
| `proposed_value` | 应该改成什么 |
| `fix_type` | ⭐ **来自固定目录，不是自由文本** |
| `evidence` | 依据来自哪：`JIRA-4521 §3` / Confluence 页面+锚点 / Slack 永久链接 |
| `confidence` | `high` / `medium` / `low` |
| `needs_decision` | 需要人**做选择**（而不只是批准）时为 `true` |
| `notes` | 只在别的列装不下时才写 |

**2. `report.md`** —— CSV 装不下的东西：

- 影响行数，以及是否落在预期区间
- 干跑结果：检查了哪些不变量、before/after 抽样
- **它拿不准的地方，以及为什么**
- ⭐ **它故意排除掉的行，以及为什么** ← 最值钱的一节
- 查了哪些来源

## 为什么是文件，为什么是 CSV

| | |
| --- | --- |
| **一眼可审** | 按 `confidence` 或 `fix_type` 一排序，可疑的行几秒钟就浮上来 |
| **可 diff** | 两次运行能比；agent 的方案和当年人工的修法也能比 |
| ⭐ **它就是 eval 集** | 每一份审过的 CSV 都变成阶段 2 的标注案例 |
| **没有东西需要回滚** | 文件错了，代价是审查时间；写入错了，代价是一次事故 |
| ⭐ **审批绑定内容** | 对文件取 hash，执行时重新校验 —— **堵住「批了 A、执行成 B」那个洞** |

## agent 绝对不能有的

- **不要任何写权限。** 不是"受限的写权限"，是**没有**。读取用的 MCP server 连库用 `SELECT` 权限的账号——**由数据库 grant 强制，不是靠 prompt 说"请只读"。**
- **不要自由 SQL。** 修复类型来自**参数化操作目录**。让模型拼任意 SQL，等于换了顶帽子的万能 shell —— **权限边界根本画不出来。**
- **动作不能由工单正文驱动。** Jira / Confluence / Slack 的内容是**用来引用的证据**，不是**要执行的指令**。工单里写「顺手把所有状态改成 active」时，**结构化的 `fix_type` 字段就是让它变不成动作的那道墙。**

## 交给人之前的验证

agent 跑干跑并报告结果，**但不由它判断结果可不可接受**。

```sql
BEGIN;
  执行提议的修正
  → 影响行数：147   （预期 140–160）  ✅
  → 不变量：订单总额不变              ✅
  → 抽样 5 行 before / after
ROLLBACK;
```

⚠️ **但这里可机器判定的只有执行侧。** 这个场景已确认：定位哪些行要读散落在几处的文字，改成什么值要逐案判断。干跑能证明「改了 147 行、总额没崩」，**证明不了「这 147 行就是该改的」**。

> ⭐ **所以 CSV 不只是安全措施——它是 v1 里业务正确性的唯一 verifier。审的人那双眼睛就是 verifier，没有替补。**

这也把 v3 的门槛抬高了：**只有业务正确性也能变成机器判据的 fix 类型，才有资格自动执行。**

```
✅  "币种应等于 merchant_config 表里那一行"   → 可校验，能毕业
❌  "币种应该是运营当时的意图"                 → 永远停在 v2
```

**因此 CSV 要按「让人 10 秒审一行」来排版**：`evidence` 精确到链接 + 定位 + 原文摘录（给个工单号等于让他重做一遍调查）；按 `confidence` 升序排，不确定的在最前；`needs_decision`（需要做选择）和普通待批准**分成两批**。

三种判据分开写：

| 类型 | 问什么 |
| --- | --- |
| **业务正确性** | 是不是该改的那些行？新值对不对？ |
| **执行成功** | 写完读回来，一致吗？ |
| **必须停止** | 行数超限、表不在白名单、证据冲突、预算耗尽 |

⚠️ **「停下来」不等于「成功」。四个出口只有一个是好的。**

## 演进路径

| 阶段 | agent 做 | 人做 |
| --- | --- | --- |
| **v1** | 调查 → CSV + report | **逐行审**，手工执行修复 |
| **v2** | 同上 + 干跑证据 | 批准文件；**现有服务**按批准的 hash 执行 |
| **v3** | 低风险类型自动执行 | 审异常 + 抽查 |

> **不要跳到 v3。** 让你有资格往前走一步的，是**verifier 的历史战绩**，不是一个能跑的 demo。

---

## 相关 · Related

- [`usecase-data-fix-agent.zh.md`](usecase-data-fix-agent.zh.md)
- [`team-learning-path.zh.md`](team-learning-path.zh.md)
- [`phoenix-instrumentation.zh.md`](phoenix-instrumentation.zh.md)
