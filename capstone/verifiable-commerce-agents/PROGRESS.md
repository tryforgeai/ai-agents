# 当前进度

最后更新：2026-10-28（America/Los_Angeles）

## 当前状态

**跟踪目录已建立；proposal v2 已归档；实际开发与实验进度待核实。**

| 项目 | 状态 | 证据 |
| --- | --- | --- |
| Proposal v2 归档 | 已完成 | proposal/Verifiable_Commerce_Agents_Capstone_Proposal_v2.pdf |
| 范围、八周路线图、决策日志初始化 | 已完成 | SCOPE.md、ROADMAP.md、DECISIONS.md |
| 已有代码/实验与提案逐项核对 | 未开始 | — |
| 核心开发、DSPy、GRPO、评估 | 待核实 | 未提供本项目实现或运行证据 |

## 下一步（建议顺序）

- [ ] 盘点已有项目代码与实验，包括 FinePrint 可复用部分，建立完成证据。
- [ ] 确认起止日期、团队分工、小模型课程认可和 GPU 环境。
- [ ] 确定 W1 最小闭环：一条政策 → 一个 typed action → 数据库变更 → verifier 判定。
- [ ] 补齐 20 个手算 seed tasks，并跑模型/GPU smoke test。

## 待确认与风险

| 项目 | 当前情况 | 后续动作 |
| --- | --- | --- |
| 小模型是否符合课程要求 | 提案待确认 | Office hours 确认并记录答复 |
| RTX 5090 测试配置/集群 | 提案待确认 | 核实环境后做最小训练运行 |
| API 预算 | 提案要求 spending cap，未给金额 | 确定金额并记录各实验支出 |
| 计划对应实际日期 | 尚未提供 | 补齐后映射项目 W1–8 |
| 模型与依赖版本 | 提案拟选，未验证 | W1 核实、smoke test、锁版本 |

## 推进日志

### 2026-10-26 · 建档

- 用户确认此提案是要做的 capstone，要求创建文件夹跟踪进度。
- 保存原 PDF 副本，阅读全文并查看第 7 页路线图。
- 建立范围、路线图、当前状态和决策记录。
- 本次没有开展实现或训练；不推断已完成任何项目周里程碑。

### 后续记录模板

- 日期：
- 本次目标：
- 完成内容与证据（代码 / 测试 / trace / 报告）：
- 实验条件与结果（如适用）：
- 阻塞或决定：
- 下一步：

### 2026-10-26 · τ-bench 源码调研

- 核对上游 commit `0c69df456a96aa76a1162591574dad9c427a34d7` 的任务 schema、retail policy/tools、环境、评分器、pass^k 与 Gym 接口；本次为静态阅读，未运行模型评测。
- 来源：[评分说明](https://github.com/sierra-research/tau2-bench/blob/0c69df456a96aa76a1162591574dad9c427a34d7/docs/evaluation.md)、[环境评分器](https://github.com/sierra-research/tau2-bench/blob/0c69df456a96aa76a1162591574dad9c427a34d7/src/tau2/evaluator/evaluator_env.py)、[动作评分器](https://github.com/sierra-research/tau2-bench/blob/0c69df456a96aa76a1162591574dad9c427a34d7/src/tau2/evaluator/evaluator_action.py)。
- 关键事实：参考动作在 gold 环境重放产生目标终态；实际轨迹重放得到 predicted 终态，比较 DB hash。是否计入最终分数由 reward_basis 决定；评分可包括 LLM judge，并非全部确定性。
- ActionEvaluator 检查参考动作是否出现在调用集合中，不直接约束顺序、重复次数或所有额外动作。
- 建议（未定案）：借鉴 Task/Environment/Agent/Simulator/Evaluator 分层；本项目增加事件级 policy invariants、审批与幂等审计、规则级诊断、独立 seed 验证。
- 下一步候选：先实现 3 个可手算任务和脚本 agent，验证环境与评分器，再接 LLM；选型尚未定案。

### 2026-10-28 · tau2 学习笔记与源码核验

- 静态核验 commit `122e2432b82d740e8f313f46f0a071729c404f39` 的 agent、retail、重放、评分、Gym 与 A2A 实验桥接。
- 更新 `tau2-learning-notes.zh.md` 第 10–17 节，加入与用户提供的 Claude 笔记逐项比较及 capstone 设计建议。
- 用标准库脚本 `tau2_source_audit.py` 统计基础 114 题与英文 50 题，结果保存 `tau2-source-audit.json`；不代表运行得分。
- 修正关键概括：基础 retail 多数 basis 为 DB + NL_ASSERTION；10 个无参考写任务中 4 个有非空 NL 要求；部分工具有状态级重复调用防护；Gym 不自动提供单步 dense reward。
- 局部阅读 FinePrint verify.py；没有运行模型、训练、工具重放实验或全面验证原型，不变更实现完成状态。
- 建议下一步：三个手算任务 + 脚本 agent，验证终态与确认过程分开判分；新 commerce domain 仍为建议选型。
