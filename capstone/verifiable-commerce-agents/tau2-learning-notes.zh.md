# tau2-bench 学习笔记：对照 Verifiable Commerce Agents

整理日期：2026-10-28。本文整合 Rosso 提供的 Claude 学习记录、本地 capstone 资料和本次对照分析。**更新：已完成源码核验，优先阅读第 10–17 节；第 1–9 节保留为核验前的学习框架，涉及待核验事项以新章节为准。**

**证据边界：** 首版仅比较笔记；本次进一步克隆并静态阅读上游 commit `122e2432b82d740e8f313f46f0a071729c404f39`，用 Python 标准库统计 JSON 与工具声明。没有安装完整运行环境、调用付费模型、运行对话评测或训练。此前 `PROGRESS.md` 的 commit 与本次不同，不混用结论。源码路径链接固定到本次 commit。

## 1. 我们究竟要学什么

tau2 的价值，是把任务、被测 agent、模拟用户、工具环境和评分器拆开。我们希望借鉴这种结构：固定考场与判分规则，替换 agent，比较不同实现的任务完成能力与过程合规性。

本项目的核心问题是：**agent 是否完成任务、是否违反规则、在哪一步违规，以及违规的影响是什么。** 高终态成功率不能单独回答这些问题。

## 2. 一轮交互如何工作

```text
任务与初始状态
      ↓
模拟用户 ↔ Orchestrator ↔ 被测 Agent
                ↓ 工具调用请求
          Environment / Tools
                ↓
        状态变化 + 交互轨迹
                ↓
             Evaluator
```

在这套接入模式下，agent 提出消息或动作请求，评测环境执行工具并记录结果。评分器评估可观察行为，不需要了解 agent 内部是规则脚本、单模型还是 LangGraph 工作流。

这与你已有架构笔记中的原则相同：模型提出动作，harness 负责执行、记录、验证和停止。

## 3. 如何替换被测 agent

| 替换层级 | 意义 | 需要控制的变量 |
| --- | --- | --- |
| 模型 | 同一 agent 实现换底层模型 | prompt、工具、预算、推理配置 |
| Agent 实现 | 规则脚本、普通 LLM、LangGraph 等互换 | 统一输入输出和动作权限 |
| 外部服务 | 通过适配器接入独立运行的系统 | 协议、状态同步、超时、解析失败 |

提供的笔记使用 `HalfDuplexAgent`、`get_init_state()`、`generate_next_message()` 和工厂注册解释 Python 接入。应将它们作为待核验的实现入口，不把示意代码直接当作当前版本可运行代码。

A2A 服务接入也需要遵守接口契约。它不等于任意现有 agent 无需适配；文本动作协议还可能增加解析失败。两种接入方式使用同一 evaluator，只是可比较的必要条件之一，还需要统一可见信息、工具权限、任务、预算和模拟用户设置。

## 4. 终态评分与过程评分要分开

根据已有调研，DB 评分将参考动作与实际动作分别在环境中重放，比较得到的数据库终态。具体得分由任务的 `reward_basis` 决定；框架还可以包含动作、环境断言和语言相关评分。

因此不能把整个 tau2 概括成“只看数据库”。准确的局限是：**DB 终态一致，本身不能证明过程合规。**

| 场景 | 终态检查能回答什么 | 还需要的证据 |
| --- | --- | --- |
| 正确退款 | 最终金额和订单状态是否正确 | 是否先获得有效确认 |
| 重复请求退款 | 是否造成重复退款 | 请求、重试、幂等键和执行结果 |
| 越权操作 | 对象最终被怎样修改 | 身份、授权范围与操作对象 |
| 正确拒绝 | 数据是否保持不变 | 是否完成必要解释或替代方案 |

本地调研还指出：ActionEvaluator 的参考动作匹配，不自动等价于顺序、次数及额外动作的完整约束。

## 5. pass^k 表达什么

一个任务运行 n 次，成功 c 次，提供的笔记给出的估计量为：

`pass^k = C(c, k) / C(n, k)`，要求 n ≥ k；逐任务计算后再平均。

例如运行 4 次、成功 3 次：pass^1 = 0.75，pass^2 = 0.50，pass^3 = 0.25，pass^4 = 0。

- pass^k：抽取 k 次，全部成功；关注重复成功表现。
- pass@k：k 次中至少一次成功；关注多次尝试是否能找到成功结果。

项目计划的 30 个任务各跑 4 次，可以观察这组任务上的稳定性，不能仅凭 pass^4 证明上线可靠性。仍需同时报告违规类型、成本、延迟、模拟器错误与统计不确定性。

## 6. 如何与我们已有工作衔接

| 已有材料 | 能复用的内容 | 当前边界 |
| --- | --- | --- |
| `PROGRESS.md` | tau2 分层、评分与过程审计调研 | 静态阅读记录，不是实验结果 |
| `SCOPE.md` | 五组对照、Guard 开关、测试集、退化基线 | 项目计划，不代表已实现 |
| `../fineprint-mcp/README.md` | 商店、固定日期、退换货工具、独立 verifier | 本次只读说明，没有重新运行验证 |
| `../../agent-service-architecture.en.md` | harness 执行与验证、解析错误分离 | 架构原则，需要落实到适配器 |
| `../../RLVE 论文精读笔记.md` | 约束式验证、多合法答案、验证器自身验证 | 可借鉴原则，不直接替代 commerce 实验 |

优先评估将 FinePrint 的最小规则和工具接入实验环境，而不是重新写一套商店。新 tau2 domain 是候选方案，尚未作最终选型。

## 7. 需要特别修正的认识

### 不行动获得分数，不一定是漏洞

本来应该拒绝的任务，不修改数据库可以是正确行为。“参考解没有写操作”不能直接推出“随便拒绝就满分”。提供的记录中的 10/114 数量以及实际基线得分尚未复核。

应该分别测试：需要行动时是否完成任务、需要拒绝时是否正确拒绝、是否滥用询问或转人工。低违规率不等于高任务完成率。

### 记录 MCP 调用，不等于已经可以重放

重放还要求一致的工具语义、初始状态、时间与必要的外部响应，并在隔离副本中执行，避免产生第二次外部副作用。回写 ToolCall/ToolMessage 只是适配的一部分。

可以明确一条主验证路径：实际终态 + typed action log + 独立 verifier。只有满足重放条件时，再将重放结果作为交叉核对。

### 没有幂等键，不代表每个工具都会重复生效

工具可能通过状态检查阻止第二次执行。需要逐个验证重试行为，并定义项目自己的幂等契约，不能根据“缺少幂等键”推断所有写工具的结果。

### 决策点需要上下文与环境快照一致

`initial_state.message_history` 是候选入口，但历史中“已经认证”“已经确认”的信息，必须与环境和事件记录一致。单步样本应定义可见上下文、环境快照、合法动作及预期约束。

### 共享规则，也要独立验证规则实现

评测、DSPy metric 和 GRPO reward 应共享明确的业务规则语义，但不能只靠同一段代码互相证明正确。保留手算 seed tasks、边界用例和独立 verifier，检查它们是否共同遗漏或误实现规则。

## 8. 建议的最小实验顺序

以下是建议，尚未执行。

1. **最小环境：** 复用候选 FinePrint 组件，固定“今天”，仅做一条退货规则和三个手算任务，用脚本 agent 跑通状态变化与评分。
2. **过程违规：** 构造最终退款正确但缺少有效确认的轨迹，确认 verifier 能区分终态正确与过程违规。若工具强制拦截，另记录请求违规与实际执行违规。
3. **退化基线：** 跑 do-nothing、always-ask、always-escalate，分别报告任务完成与违规情况，不预设它们必然得零分。
4. **决策点：** 固定同一个上下文与环境快照，在独立副本中比较合法退款、错误退款和询问三个候选动作。
5. **替换 agent：** 接入 LLM 或 LangGraph，固定其余条件，再看多次运行结果；人工区分 agent、模拟用户和协议故障。

每次实验保存：版本、任务、初始状态、配置、动作日志、终态、分项评分与错误分类。先证明考场和裁判正确，再比较模型。

## 9. 复习自测

1. 为什么把 agent 与工具执行分开，就更容易替换被测系统？
2. 为什么最终数据库相同，仍可能存在过程违规？
3. 同一个 evaluator 为什么还不足以保证公平比较？
4. 正确拒绝与靠拒绝逃避任务，应该怎样区分？
5. MCP 调用有日志之后，还缺哪些重放条件？
6. 决策点除了聊天历史，还需要保存什么？
7. 如何发现 reward 和 evaluator 共享的实现错误？
8. pass^4 很高能说明什么，又不能说明什么？

## 10. 源码核验后的结论：它适合做什么底座

**tau2 是可扩展的客服 agent 评测框架，不是任意 agent 的零适配评分服务。** 我们可以学习并复用其环境与被测系统分离、任务 schema、可重复初始化、轨迹记录、用户模拟和统计机制。它不能替我们定义 commerce 的正确性，也不能从一个总分推断所有业务风险。

“测试所有 agents”应操作化为：支持满足指定接入契约的多种 agent 实现。任意语言、模型或框架并不妨碍接入；但需要能够重置会话、接受受控工具与政策、输出可执行动作或提供可信执行日志。只能通过网页聊天、无法控制其工具或读取副作用的黑盒产品，只能做较弱的交互评测，不能宣称同等级的数据库验证。

当前仓库还包含多语言、语音全双工、knowledge retrieval、intake 等能力；capstone 第一阶段只需文本 retail/commerce。仓库范围大于我们需要复用的部分。

### 源码导航与职责

以下所有路径均相对上游仓库；固定源码入口见第 17 节。

| 组件 | 源码入口 | 我们要学的设计 |
| --- | --- | --- |
| 任务 | `src/tau2/data_model/tasks.py` | 用户目标、初始状态、评分标准分开；参考答案不交给普通被测 agent |
| Agent | `src/tau2/agent/base_agent.py` | 只依赖统一消息与状态接口 |
| 注册 | `src/tau2/registry.py` | 工厂创建 agent/environment/user，各自可替换 |
| 环境 | `src/tau2/domains/retail/environment.py` | 创建独立 DB 与工具集合，装载 policy |
| 工具 | `src/tau2/domains/retail/tools.py` | 操作前置条件、状态迁移、类型声明 |
| 调度 | `src/tau2/orchestrator/orchestrator.py` | 推进用户、agent、工具；记录终止与错误 |
| 重放 | `src/tau2/environment/environment.py::set_state` | 从初始化数据与已执行变更恢复状态 |
| 评估 | `src/tau2/evaluator/evaluator.py` | 选择评分项、处理异常终止、聚合 reward |
| 稳定性 | `src/tau2/metrics/agent_metrics.py::pass_hat_k` | 按任务统计重复成功，避免只看平均值 |
| 逐步驱动 | `src/tau2/gym/gym_agent.py` | 外部控制 observation/action，不等于内置 dense reward |

## 11. retail 实际能做什么，不能做什么

已读 `data_model.py`、`tools.py`、`policy.md`：原生 retail 是订单售后环境，包括用户与订单查询、商品变体查询、取消、地址/商品/付款修改、退货请求、换货请求和转人工。它不是完整电商平台。

| 需求 | 当前原生 retail | 对 capstone 的影响 |
| --- | --- | --- |
| 查询与售后订单状态迁移 | 有 | 可学任务与工具建模 |
| 30 天退货 / 45 天换货 | Order 没有送达日期等时间字段 | 增加日期与任务时钟，编写边界用例 |
| 优惠券、叠券 | 当前 schema/tools 未建模 | 需自建促销规则与工具 |
| 购物车、创建 checkout 订单 | 当前工具未提供完整流程 | 不能直接把原生 retail 当三类 MCP server 的实现 |
| 明确确认后写操作 | policy/docstring 要求；写函数没有确认凭证参数 | 需要可信确认事件与过程检查 |
| 重试不会重复退款 | 部分操作由状态检查挡住重复请求 | 与幂等键返回相同结果不是同一保证 |
| 退货后的实际付款结算 | return 工具主要记录 return requested 与相关字段 | 不可把“接受退货请求”误称为“已完成退款到账” |
| 跨会话记忆、卖家审批 | 当前 retail 没有项目所需的完整模型 | 需要额外会话/审批状态和场景 |

重要细节：`Tool` 是包装 Python callable 的对象，不是安全沙箱。标准运行路径让 orchestrator 执行工具，并不保证不可信的进程内 agent 无法绕过它。自研可信 agent 可以用进程内适配；第三方不可信 agent 应隔离进程与存储权限，通过受控工具网关访问考场。

## 12. 评分：源码与数据比概括更重要

### 12.1 DB 与 ACTION 是不同问题

`EnvironmentEvaluator` 为 predicted 与 gold 创建独立环境，两边应用初始化数据/动作；predicted 使用实际完整轨迹，gold 使用初始历史加参考动作；最后比较 agent DB 和 user DB hash。环境断言也在 predicted 环境执行。

`ActionEvaluator._check_actions()` 对每个参考动作，查找实际调用中是否存在匹配项。它不是完整轨迹等价：不检查全局顺序，不自动禁止额外调用，也没有一对一消耗匹配来约束次数。因此即使启用 ACTION，也不能替代事件级合规规则。

`evaluate_simulation()` 在非 AGENT_STOP/USER_STOP 终止时直接给 0。缺失评判标准可能返回中性 1。这说明自建任务需要 schema lint：预期检查不能为空，不能让遗漏评分项表现成通过。

### 12.2 本次实际统计

使用相邻 `tau2_source_audit.py`，输出保存于 `tau2-source-audit.json`。这是静态统计，不是模型得分。

- 基础 `data/tau2/domains/retail/tasks.json`：114 题；112 题 basis 为 DB + NL_ASSERTION，2 题为 DB。
- 英文语言包 `data/tau2/multilingual/en/retail_tasks_en.json`：50 题，全部 basis 为 DB + NL_ASSERTION。
- 发布 manifest `data/tau2/benchmarks/text.json` 绑定 `text-v1` 和各语言×领域的 revision，并使用 retail_50。不能把基础 114 题的统计直接当成发布 benchmark 的统计。
- 基础 114 题中，10 题没有参考 WRITE 调用，ID 为 10、12、24、25、50、57、62、65、67、68。
- 其中 24、62、67、68 有非空 NL assertions，要求告知具体商品/金额信息；其余 6 题的 NL assertions 为空。正常终止、无 DB 改动时，这 6 题具备退化策略得分的静态条件；实际终止与得分仍需实验。

这修正了“10/114 都可礼貌拒绝得满分”的说法，也修正了把 COMMUNICATE 当作所有 retail 任务实际评分项的误读。**schema 默认、文档示例和数据中实际 basis 是三回事。**

### 12.3 重放的精确行为

当前 `set_state()` 会核对 ToolCall/ToolMessage 对应关系，跳过 execution_status=rejected、未知工具和不改变状态的工具；重新执行 mutates_state=True 的工具，严格模式还比较重放输出与记录输出。

因此“把所有调用重放一遍”不够精确。工具的变更标记、拒绝状态、输出稳定性都影响评估。被执行但返回错误的工具仍可能产生副作用，不能简单把 error 当作未执行。

## 13. 与 Claude 笔记和我之前总结逐条对比

| 原说法 | 核验结果 | 应采用的表述 |
| --- | --- | --- |
| agent 可通过小接口替换 | 基本正确 | 支持 UserMessage、ToolMessage、MultiToolMessage；输出 AssistantMessage，并管理 state |
| 注册后就能另起 CLI 使用 | 有条件 | 注册是进程内的；CLI 启动必须导入注册代码。示例在同一脚本注册并调用 runner |
| A2A 不需改被测代码 | 原对话后来已纠正 | 实验桥接需要 A2A 服务及其 `<json>` 动作协议，不是通用免适配接口 |
| 只看 DB / 不看过程 | 过度概括 | 框架支持多种评分；具体过程规则是否覆盖取决于任务与 evaluator |
| 10/114 不行动就满分 | 不成立为整体结论 | 10 个无参考写操作，其中 4 个有非空 NL 要求；仍需实跑 |
| 所有写工具执行两次会重复生效 | 错误 | cancel 首次变 cancelled，第二次被 pending 检查拒绝；return 类似 |
| 没有日期/优惠券 | 当前原生 retail 确认 | 扩展 schema 与业务规则，不是 tau2 框架不可表达 |
| Gym 可以作为训练入口 | 正确但不完整 | `_get_reward()` 在运行结束前返回 0；单步 commerce reward 需要自己实现 |
| retail 可直接 solo_mode | Gym README 有误导性示例 | retail `get_environment()` 明确拒绝 solo_mode=True |
| 最小示例不需要 API key | 示例顶部文字不可靠 | 示例实际调用 generate 与 LLM runner，不能当离线例子 |
| 只需替换 Evaluator 与 initial_state | 不完整 | 还需要领域 schema/tools、适配器、可信日志、状态隔离、数据集与评分接线 |
| 判分器相同所以公平 | 不充分 | 还要固定信息、工具、用户分布、预算、模型设置与重置语义 |

我此前“要检查实际 reward_basis”“重复工具可能被状态检查挡住”的质疑得到源码支持。但原先只给出泛化提醒不够：现在应该用上述具体数据与函数行为替代。

## 14. 我们建议采用的系统设计

这是基于源码与 proposal 的建议，不是已经实现或已决定的技术选型。

```text
版本化任务集 / 初始快照 / 固定时钟
                  ↓
       Runner + User Simulator
                  ↕
            Agent Adapter
       ┌──────────┼────────────┐
     脚本       LLM/DSPy     LangGraph/外部服务
                  ↓ 动作请求
      Tool Gateway / Policy Guard（可开关）
                  ↓
        Commerce Environment / MCP
                  ↓
      请求、拦截、执行结果、状态变化日志
                  ↓
        独立 Verifier → 分项报告
```

### 三种接入契约

1. **下一步动作接口：** agent 只返回动作请求，环境执行。最容易比较决策能力。LangGraph 需要在工具执行边界暂停并交回请求，不能内部执行后又让 tau2 再执行。
2. **受控工具服务接口：** 完整 agent 系统调用我们提供的隔离 MCP/tools。网关记录与校验，verifier 读取真实测试终态。适合完整产品系统评测，但需要另做 runner/trajectory 适配。
3. **纯黑盒交互：** 只有输入输出、没有可信副作用。可以测沟通和任务声明，无法提供同等强度的数据库与过程验证。报告必须标明证据等级。

不要将这三类直接混成一张“所有 agents”的总榜。先按工具控制和可观察程度分组，同组内公平比较。

### 输出维度与训练 reward 分开

报告至少保留：任务完成率、规则级违规率、尝试违规率、实际执行违规率、Guard 拦截率、不必要转人工/拒绝率、成本、延迟、pass^k。

违规事件建议包含 rule_id、step_id、entity_id、evidence、attempted/executed、金额影响。金额能确定时记录 amount_cents；隐私等非货币风险不能凭空折算成美元。

训练时才将这些信号映射成 proposal 的标量 reward（违规 -1、不可用输出 -0.5、正确动作最高 1 与部分分）。完成任务和不违规必须同时考虑，防止“永远不行动”成为高 reward 策略。

### 确认事件如何可信

若要求主评分完全确定性，不能让 agent 自己传 `confirmed=True` 就算证明获得同意。可以由受控用户模拟器/交互层产生绑定 action 参数的 confirmation event 或 token，再由验证器检查它发生在写操作之前。自由文本“yes”若靠 LLM 解释，则该部分并非完全确定性；需明确选择并单独报告。

### 与已有 FinePrint 的关系

本次还读了 `../fineprint-mcp/verify.py`：它确实独立读取 SQLite 和 rules.json，检查退货期限、超过实付的退款、换货产品一致性等，并生成 reward；没有依赖 fineprint 判定模块。但这是现有终态 verifier，不等于已经具备所有事件级确认、身份和审批验证。复用前要补规则覆盖表及独立手算用例。

## 15. 学习与动手路线：每一步都有要回答的问题

| 顺序 | 阅读/实验 | 必须能回答的问题 | 产出 |
| --- | --- | --- | --- |
| 1 | retail policy、data_model、tools；手读任务 0、10、24 | 规则写在 prompt、工具还是评分里？ | 每条规则的执行位置表 |
| 2 | tasks.py、evaluator_env、evaluator_action、evaluator.py | 正确终态和正确过程有什么差别？ | 两条相同终态、不同合规性的轨迹 |
| 3 | base_agent、minimal_text_agent、registry、orchestrator | 如何让自己的 agent 只提出动作？ | 脚本 adapter，确认工具仅执行一次 |
| 4 | set_state、toolkit、DB | 什么条件下重放可重复？ | 初始快照、重放结果、输出一致性检查 |
| 5 | mock domain、FinePrint 最小规则 | 能否迁入一个 30 天规则？ | 期限内/期限外/边界日三个手算任务 |
| 6 | Gym、InitialState | 如何冻结单步决策点？ | 同状态的多个候选动作及 reward |
| 7 | 小规模 LLM 与用户模拟 | 错误来自 agent、用户还是协议？ | 人工审阅轨迹和分类报告 |
| 8 | 冻结 held-out 集，再接 DSPy/GRPO | 优化是否在未见组合上提升？ | 五组对照与配对不确定性报告 |

最小反例实验：正常终态+无确认、重复取消、合法拒绝、无理由拒绝、伪造确认、相同幂等键重试。区分工具防御效果与 agent 本身行为，分别报告 Guard 开/关。

不建议第一周同时实现优惠券全流程、跨会话记忆、A2A 卖家与检索。按 proposal 的核心/扩展分阶段，先确认一个规则与一个动作的可验证闭环。

## 16. 本次完成与未完成

- 已完成：固定 commit 源码阅读、基础/英文任务集静态统计、核心接口和评分路径核验、Claude 记录逐条比较、FinePrint verifier 局部阅读。
- 已保存：本学习笔记、`tau2_source_audit.py`、`tau2-source-audit.json`。
- 未完成：tau2 依赖安装、模型 benchmark、do-nothing 实跑、重放运行测试、commerce domain 实现、训练、FinePrint 全面审计。
- 版本化建议：保留上游原始任务与得分做参考；我们新增 domain 的结果单独报告，不冒称 tau2 官方可比分数。冻结代码、任务集合、语言包、模型与 judge 配置，而不只固定随机种子。

## 17. 固定版本源码引用

本次 commit：`122e2432b82d740e8f313f46f0a071729c404f39`。

- [评分文档](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/docs/evaluation.md)
- [环境评分器](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/evaluator/evaluator_env.py)
- [动作评分器](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/evaluator/evaluator_action.py)
- [环境重放](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/environment/environment.py)
- [Agent 接口](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/agent/base_agent.py)
- [retail 工具](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/domains/retail/tools.py)
- [retail 基础任务](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/data/tau2/domains/retail/tasks.json)
- [英文 retail 任务](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/data/tau2/multilingual/en/retail_tasks_en.json)
- [Gym 实现](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/tau2/gym/gym_agent.py)
- [A2A 实验桥接](https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/src/experiments/agentify_tau_bench/src/agentify_tau_bench/green_agent/agent.py)
