# 项目范围与验收依据

来源：Proposal v2，2026-10-24。以下均为计划目标，不是实现结果。

## 核心（项目 Week 1–4）

1. **商店与确定性验证器**：生成商店、客户、订单、政策；30 天退货、45 天换货、优惠券叠加规则。用 20 个手算 seed tasks 验证规则本身。
2. **Tools / MCP**：catalog、cart and checkout、orders 三个 MCP servers；最小权限、typed errors、写操作幂等。
3. **编排**：supervisor + checkout/promotions 与 orders/returns 两个 specialists；Policy Guard 检查每次写操作，大额退款转人工审批。
4. **DSPy**：同一个 next-action signature；冻结手写 baseline，比较 GEPA 与 MIPROv2，和 GRPO 使用相同小模型、相同决策任务。
5. **RLVR / GRPO**：单步决策（工具调用、询问、升级人工）；约 400 个候选筛到约 150 个有学习信号的训练样本；LoRA，G=8。对数据库副本应用动作并计算 reward：违规 -1、不可用输出 -0.5，正确动作最高 1，按 action/tool/arguments 给部分分；多个合法答案取最佳匹配。

## 评估与证据

- 在优化前冻结测试集，按规则组合划分：150 个 held-out decision points；30 个端到端任务，每个跑 4 次。
- 五个条件：小模型 + 手写 prompt / GEPA / MIPROv2 / GRPO，以及 frontier model ceiling。
- 指标：step accuracy、policy violation rate、pass^1–pass^4、每个解决对话的成本、两档 effort 的延迟、Guard 拦截率；Guard 开/关均报告违规率。
- 配对 95% bootstrap interval 排除零才宣称提升；报告测试集可检测的最小差异。
- 六类场景：窗口内退货、窗口外退货、叠券、用换货替代退款、升级人工、商品描述中的提示注入。
- 防虚假高分：do-nothing / always-ask / always-escalate 基线；模拟客户用不同模型家族；人工检查 30 段模拟对话。

## 扩展（项目 Week 5–7）

| 故事 | 计划与验收重点 |
| --- | --- |
| Don't fall for tricks | MCP 攻击集、认证、最小权限、审批；比较防御开关下攻击成功率及正常任务通过率 |
| Remember me next time | 2–3 次跨会话记忆、地址变更、承诺积分、删除请求；错误记忆不能导致违规；经验记忆开关对照 |
| Ask the seller first | 独立 seller agent 经 A2A 服务交互；核对双方记录、seller 批准、仅退款一次、拒绝伪造批准 |
| Find the right rule | 40–80 页规则库、冲突优先级与检索；比较完整上下文、oracle 规则、搜索的正确率与成本 |

生产能力：prompt caching、structured outputs、两档 effort、固定版本的 OpenTelemetry GenAI tracing、违规回归 CI、Docker Compose 一条命令复现 demo、代码外管理 secrets。

## 资源和边界

- 数据全部合成，不使用真实客户个人数据。
- 拟用 Qwen3.5-4B（non-thinking），fallback Qwen3-4B-Instruct-2507；课程认可待确认。
- 提案拟用 Sonnet 5.5 作为对话与 reflection 模型，Opus 5.5 作为子集 ceiling；实际可用性、价格、版本待核实。
- 单 RTX 5090 或课程集群；预计约 6 GPU-hours，课程额度 8 小时；API 支出上限数值待定。
- 拟用 LangGraph、Python、MCP/A2A SDK、TRL + LoRA、vLLM 或 Unsloth、DSPy、OpenTelemetry；Week 1 验证并固定版本。
- 时间不足优先砍 A2A；可选扩展是 single-agent 对照和训练小模型接管决策并回退 frontier。
- 不新增 policy rule families，不做 multi-turn GRPO。
