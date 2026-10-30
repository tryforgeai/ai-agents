# 八周路线图

来源：Proposal v2 第 7 页路线图（含图中三个关卡）。日期待确定；所有执行状态目前待核实。

| 项目周 | 计划交付 | 状态 | 完成证据 |
| --- | --- | --- | --- |
| W1 | Store、rules、verifier；20 seed tasks；模型/GPU smoke test；固定版本 | 待核实 | — |
| W2 | 三个 MCP servers；agents、Guard、审批；冻结测试集 | 待核实 | — |
| W3 | DSPy GEPA/MIPROv2；GRPO pilot；模拟客户 | 待核实 | — |
| W4 | 完整 GRPO；五条件评估；端到端运行与 tracing | 待核实 | — |
| W5 | MCP 攻击集；认证与最小权限；CI 回归门禁 | 待核实 | — |
| W6 | A2A seller；规则库 RAG；跨会话记忆 | 待核实 | — |
| W7 | Docker 部署；成本/延迟预算；最终冻结测试运行 | 待核实 | — |
| W8 | 报告、threat model、demo 彩排；15 分钟 demo + 10 分钟 Q&A | 待核实 | — |

## 三个关卡

| 关卡 | 通过条件 | 未通过时 |
| --- | --- | --- |
| W1 末 | Verifier 与手算 seeds 一致；GPU 能跑训练 | 缩小配置或用课程集群；模型兼容性失败则启用提案 fallback |
| W3 末 | GRPO pilot 显示学习信号 | 改进 reward 和 prompts |
| W4 末 | 课程要求全部满足，结果表填完 | 缩减 W5–7 扩展；提案指定 A2A 优先砍 |

## 排程前需要补齐

- [ ] 项目起始日和最终演示日期
- [ ] 团队成员、owner 和时间投入
- [ ] 小模型课程认可、GPU 环境和额度
- [ ] 现有实现盘点及对应完成证据
