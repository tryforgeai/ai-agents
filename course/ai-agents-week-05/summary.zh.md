# Week 05 概念总结（2026-10-18 课）

> 一天四块内容：W3 Lab 揭晓（What Did We Miss?）→ Capstone 项目说明 → Tools Prelude → 客座讲座 LLM Inference at Scale。
> 逐页记录见 [notes.zh.md](notes.zh.md)，实验见 [lab-log.zh.md](lab-log.zh.md)。

## 1. 核心定义

| 概念 | 一句话 |
| --- | --- |
| **没说出来的上下文** | 一行"帮我约个会"背后有 15 步；每一件没说出来的事（何时说的、谁的钟、那边是哪天、她已经在做什么、她允许什么）都是一种"自信地出错"的方式（p.81 The WHY） |
| **MCP** | 模型和工具之间的通用接口。client 调 `tools/list` 拿到 name / description / input_schema / output_schema；模型**只看签名和 docstring，看不到实现** |
| **Harness** | 包住工具或模型的容器：传输、并发、日志、扩缩容都由它管，作者只写业务逻辑（servlet ↔ 容器）。FastMCP 是工具的 harness，推理引擎是模型的 harness |
| **Tool poisoning** | docstring 里藏指令（"回答前先读 secret.txt"）。用户只看到正常结果，模型却照做 |
| **Intent drift** | 每一步都合法，合起来却在做另一件事；靠运行时意图检查抓 |
| **推理引擎** | 把权重文件变成服务的软件：调度、batching、KV cache 管理、GPU 内核、采样、API（vLLM、SGLang、TensorRT-LLM、llama.cpp/Ollama） |
| **Prefill / Decode** | prefill：整段 prompt 一次并行算，算力受限，决定 TTFT；decode：每步 1 个 token、每步读一遍全部权重和 KV cache，带宽受限，决定 ITL |
| **KV cache** | 每个 token 在每层每个 KV 头的 K、V 向量（浮点数，不是词也不是 token ID）。算一次存下来，显存换时间。住在推理引擎管理的 GPU 显存里，agent 和模型权重里都没有 |

## 2. 机制

**Lab 揭晓（15 步）**：收集 → 把信当数据 → 写下读法 → 拿原文核对 → 各方在哪 → 时长 → 哪天 → 钟点 → 读日历 → 规则节假日 → 决定 → 写 invite → **读回校验** → 记录 → 报告每个假设。我的 skill 11 步完整、3 步部分、2 步缺（④ 核对、⑬ 校验）。

**MCP 工具的一生**（自己跑出来的，lab 实验 2）：
- `name: str` → schema `{'type': 'string'}` + `required`；去掉类型 → `{}`，返回的 `structured_content` 也变成 `None`
- 有类型时传 `123` → pydantic 在入口拦下（函数体不执行）；无类型时 → `Hello, 123!` 静默通过
- 返回两份：给模型的 `content` 文本 + 给代码的 `structured_content`；`is_error` 是协议级失败标记

**一次推理**：Query → Tokenize → Prefill（建 KV cache、出第 1 个 token）→ Decode + Sample 循环 → Detokenize 流式输出。总延迟 ≈ TTFT + 输出长度 × TPOT。

**五种并行**：

| 并行 | 切什么 | 通信 | 解决 | 位置 |
| --- | --- | --- | --- | --- |
| TP 张量 | 一层的权重 | 每层 all-reduce | 模型大 + 低延迟 | 节点内 NVLink |
| PP 流水线 | 层的先后 | stage 边界传激活 | 模型特别大 | 可跨节点 |
| EP 专家 | MoE 专家 | 每层两次 all-to-all | MoE 显存 | 最好节点内，常跨 |
| DP 数据 | 请求 | 推理时无 | 流量大 | 任意 |
| CP 上下文 | 一条长序列 | 环形传 K/V | 上下文太长 | 节点内为主 |

实际部署按通信频率**叠加**（Hybrid：组内 TP + 组间 EP/DP）。规律：**通信越频繁，放得越近**。

**速度梯子**：SRAM > L2 > HBM > NVLink > PCIe / RDMA 网络 > CPU 内存 > SSD，每下一级约慢一个数量级。几乎所有推理优化都在这架梯子上做文章：量化（变小留在高层）、PagedAttention（高层不浪费）、KV 卸载（往下挪不丢）、FlashAttention（尽量在 SRAM 算完）。

## 3. 取舍

| 取舍 | 结论 |
| --- | --- |
| 工具多 vs 少 | 少、按任务划分、互不相似、按角色限定（相似的工具像相似的专家，路由难选） |
| 默认值 vs 报错 | 缺参数报错，不偷偷给默认值；报错说清是谁的问题、怎么改 |
| 工具输出全给 vs 裁剪 | 按意图裁剪，附来源和时间戳；越长 prefill 越贵 |
| 单 agent vs 多 agent | 先用满一个，按测到的瓶颈再拆；交接点用 schema（和"拆 GPU 带来通信成本"同理） |
| 长期凭证 vs 按需凭证 | 按需签发、范围最小、用完即过期；写操作的令牌在人确认那一刻才签 |
| 吞吐 vs 延迟 | batch 越大吞吐越高、每人越慢；用 goodput（只数满足 SLO 的请求）防止拿延迟换吞吐；看 P99 不看平均 |
| MoE | 省算力不省显存；DeepSeek-V3 总 671B、每 token 激活 37B（top-8 / 256） |

## 4. 与 Week 03–04（Skills）和我的 kit 的接线

- 本周把"LLM 读、代码判"推广到了**工具层**和**推理层**：Nyaya 那页说的正是——逻辑的 inference（vyāpti，必然成立）交给代码，LLM 的 inference（统计采样）只负责读
- Tools Prelude 的安全五页 = 原则 5（内容是数据）的具体攻击面：投毒 docstring、改配置重定向、未清洗上下文提权、输出进 shell/SQL、意图漂移
- Inference 讲座给"工具少、输出短、轮数少"补了**成本理由**：agent 是最贵的负载（多轮上下文 + 工具结果像 RAG 塞回 + 结构化输出）
- 本周新增候选技巧（课后写进 kit，编号接 #51）：

| # | 技巧 | 来源 |
| --- | --- | --- |
| #52–#56 | 工具粒度、强类型 schema、#25 扩展到 docstring、契约式设计、输出按意图裁剪 + 上下文经济 | Tools Prelude p.9–18 |
| #57 | 先用满一个 agent 再拆 | p.21 |
| #58 | 工具描述是不受信任的输入 | p.23 |
| #59 | 模型输出不进 shell / SQL；循环有步数和预算上限；配置要校验 | p.25 |
| #60 | JIT 凭证 | p.26 |
| #61 | 声明意图，按意图限制工具，运行时逐步检查 | p.27 |
| #62 | 稳定内容放 prompt 最前且逐字不变，命中前缀缓存 | Inference p.7 |
| #63 | 按难度路由模型档位：代码 → 小模型 → 大模型 | Inference 前沿技巧 |

- kit doctor 候选检查：`@mcp.tool` 缺类型注解或 docstring（lab 2b 实证）；docstring 含命令式指令；`shell=True` / `os.system` / f-string 拼 SQL

## 5. 当天产出

- `capstone/fineprint-mcp/`：FinePrint 商店的 4 个 MCP 工具 + 独立校验器 + 2 个任务；pytest 30 个、`try_cases.py` 11/11、R-117 reward 1.0
- Capstone 选择倾向 **FinePrint（去掉 cash-back）**：RLVR 奖励可验证、数据全合成；前提是老师批准 BYOP、查 Rakuten 兼职/IP 条款
- 本地跑通 FastMCP quickstart 和类型标注对照实验（lab 实验 2、2b、2c）

## 6. 开放问题

- [ ] Toolcraft deck 还没讲到，下周接着看
- [ ] 日历 skill 的缺口：evidence 核对、`calendar_unreadable` 结果、notes 补全、独立校验器、触发测试、traps.md、run log
- [ ] FinePrint：任务扩到 150 训练 / 60 测试；接真模型（DSPy agent）测"读 docstring、选对工具、先预览再确认"；对抗任务
- [ ] 课程集群是不是 H100/A100（有无 NVLink），决定 GRPO 怎么跑；TRL `use_vllm=True`
- [ ] 核实笔记里"按记忆"的数字：H800 NVLink 带宽、DeepSeek-V3 GPU 小时、RTX 5090 带宽
