# Week 02 Lab 学习总结

Lab 日期：2026-09-29，按本人所在地 America/Los_Angeles 记录。当前是 Zoom 动手 Lab；所发截图覆盖讲义第 1–3 页和第 5–6 页。周日 2026-09-27 的课程与论文阅读另有笔记。

本文区分课堂已经确认的内容、提前阅读的材料和待完成实验。讲义与 notebook 的已有输出不能视为本人今天的运行结果。

## 1 今天的主题与进度

讲义为 [Prompt engineering walkthrough](prompt_engineering/slides/prompt_engineering_walkthrough.md)，主题是十二种提示技巧与图像提示。

截图确认的内容：

- 第 1 页：今天依次使用三个 notebook。
- 第 2 页：先复习环境、`get_completion`、Instructor，再讲单次调用、流水线、工具循环和视觉语言提示。
- 第 3 页：明确与上周的衔接，以及课程集群所用模型。
- 第 5 页（19:27 截图）：连接课程集群，用 Instructor 包装客户端并选择 JSON 模式。
- 第 6 页（19:34 截图）：共用函数 `get_completion`，通过 `response_model` 选择结构化对象或文本返回。

后续章节已阅读本地材料，但尚无本次课堂逐项完成或实跑结果的记录。

## 2 与 Week 01 的衔接

| Week 01 | Week 02 |
|---|---|
| API 参数与消息 | 用统一函数组织各种实验调用 |
| CO-STAR 组织输入要求 | 按任务选择不同提示与调用方式 |
| Instructor 与 Pydantic 定义输出 | 为解题步骤、候选路径和工具动作分别定义结构 |
| 草稿与改进流水线 | 扩展到分解、反思、投票和工具循环 |

上周解决“怎么调用、怎么描述要求、怎么接收结构化结果”；今天进一步学习“怎么安排多次调用并处理它们之间的数据”。

## 3 文件与运行环境

| 材料 | 课程用途 | 讲义所列模型 |
|---|---|---|
| [01_prompting_techniques.ipynb](prompt_engineering/docs/notebooks/01_prompting_techniques.ipynb) | 十二种提示技巧 | `openai/gpt-oss-20b` |
| [02_vl_call.ipynb](prompt_engineering/docs/notebooks/02_vl_call.ipynb) | 用 OpenAI 客户端发送图片和问题 | `Qwen/Qwen3-VL-8B-Instruct` |
| [03_vl_litellm_call.ipynb](prompt_engineering/docs/notebooks/03_vl_litellm_call.ipynb) | 用 LiteLLM 调用视觉语言模型 | 同上，调用代码另带服务商路由前缀 |

课程材料要求通过 WireGuard 访问 SupportVectors 的 OpenAI-compatible 集群接口。OpenAI 客户端名称不代表请求一定发往官方服务器。具体地址与模型以本地配置和老师现场说明为准；本次尚未验证连通性。

### 第 5 页现场记录：Connecting to the cluster

```python
client = instructor.from_openai(
    OpenAI(
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
    ),
    mode=instructor.Mode.JSON,
)
```

按本页课程说明，`OPENAI_BASE_URL` 指向 `http://10.0.10.70:8000/v1`，请求到课程集群。`OPENAI_API_KEY` 在该集群使用占位值；“不检查真实 key”仅是本页对该服务的说明，不能推广到其他服务。

这里有三个职责：OpenAI 客户端负责接口请求；Instructor 包装客户端，使调用支持 `response_model`；Pydantic 类定义返回字段与校验规则。成功解析校验后，程序得到可访问字段的 Python 对象。

讲义解释选择 `Mode.JSON` 的原因：本实验模型有时一次生成多个 tool calls，而当前默认 tools 模式的处理会拒绝这种结果，因此示例改用 JSON 模式。这是本地实验的兼容性选择，不是说所有模型都应禁用 tools 模式。

`os.environ[...]` 读取当前进程的环境变量，不会自行读取 `.env` 文件；需要前置初始化加载配置。以上是代码阅读记录，尚未验证本人环境是否连接成功。

## 4 十二种技巧的学习地图

下表依据本地讲义与代码整理，不代表今天已经全部讲完。

| 技巧 | 要学的动作 | 本地示例或阅读重点 |
|---|---|---|
| Zero-shot | 不给示例，直接明确任务 | 检查未指定的语气、对象等条件 |
| Few-shot | 用输入输出示例表达规则 | 示例也决定输出粒度与风格 |
| Role prompting | 给出角色及专业视角 | 一次输出不能证明角色提示有效 |
| Chain of Thought | 请求中间解题步骤与答案 | 返回的步骤仍需核查，不能当作正确性证明 |
| Tree of Thought | 探索候选路径 | notebook 是单次多路径提示，没有搜索与回溯 |
| Meta-prompting | 先生成提示再使用 | 检查下次调用拿到的是完整提示还是对象描述 |
| Prompt chaining | 分阶段处理任务 | 中间结果遗漏会传到下游 |
| Least-to-most | 分解后顺序求解 | 当前实现只传上一阶段数字，需留意更早结果丢失 |
| Recursive prompting | 输出再次作为输入深化处理 | 示例是提纲、章节、评议；尚未闭合重写循环 |
| Reflexion | 对答案进行反思与检查 | 本例主要是自检，未实现完整的外部反馈与记忆重试 |
| Self-consistency | 比较多条解答 | 本例一次生成多条路径再评议，不是独立采样后投票 |
| ReAct | 行动、观察、继续决策 | 工具返回预设结果；观察来自工具分支而非模型自述 |

记忆方式：先看是单次调用、调用流水线，还是带工具的循环，再看方法名称。不要把教学简化版误认为完整研究实现。

## 5 Instructor 在今天的作用

`get_completion` 接收提示、模型、温度和可选的 `response_model`。模型类把输出拆成程序需要的字段，例如步骤与最终答案；工具动作还可以使用 `Literal` 限定候选名称。

学习时分开检查：输出能否解析、字段能否通过校验、内容是否有依据。字段描述是生成提示的一部分；类型验证只覆盖明确写入的规则。

### 第 6 页现场记录：get_completion

课堂确认：`get_completion` 是课程提供的通用调用模板（template），不是需要从头编写的练习，也不是 SDK 自带的方法。实验中复用这个模板，重点调整传入的 prompt、Pydantic 输出模型和采样参数；多次调用的流程由外层代码组织。

函数参数是 `prompt`、`model`、`temperature` 和 `response_model`，默认模型为 `openai/gpt-oss-20b`，默认温度 0.7。

- 传入 Pydantic 类：调用 Instructor，成功解析校验后直接返回对应对象，例如通过 `result.summary` 读取字段。
- `response_model=None`：从响应的 `choices[0].message.content` 提取内容，供文本场景使用。
- 函数自身只构造一条 user 消息，没有显式 system 消息，也没有自动保存对话历史。流水线或 ReAct 要继续使用先前结果，需由外部代码把它们放入下一次 prompt。
- “没有 system 消息”描述的是此函数构造的消息；Instructor 仍可能根据模式补充 schema 或格式要求，不能据此断言底层最终请求只有原始提示。
- 讲义示例用 0.3 偏向稳定输出、0.7 偏向多样输出；这是本实验的设置，不保证低温度下答案正确。

这层 helper 统一调用方式，具体提示技巧来自传入的提示、输出 schema，以及外层是否安排多次调用或工具循环。

## 6 视觉语言提示


notebook 02–03 将文字问题与图片一起放进消息。图片通过 base64 data URL 传输，两个 notebook 用不同客户端完成相似调用。

讲义中的三个练习是：解释物理笔记、解释优化器更新公式并给代码、识别故意写错的公式。讲义报告模型曾误读平方的位置，并产生基于错误转录的分析。这是课程已有示例，尚未在今天重跑。

适合本次实验的步骤：先逐符号转录并标明不清楚的部分，人工对照图片，再要求解释或纠错。代码运行成功、文档格式漂亮与物理或数学结论正确，是不同的验收项。

## 7 本地代码中值得动手检查的地方

- ReAct 通过 `thought` 中是否出现 `final answer` 或 `solution` 停止。练习可改成明确的结束字段或动作，同时保留步数上限。
- Self-consistency 的多条路径不是独立请求。练习可改成多次独立调用，由程序归一化答案并投票。
- Meta-prompting 当前把 Pydantic 对象的字符串表示传给下一次调用。练习可增加 `prompt_text` 字段，明确传递生成的提示正文。
- Least-to-most 只保存 `current_result`，练习可传递完整的已解子问题与结果。
- 视觉调用没有显式设置 temperature。比较客户端时还应核对请求参数，并重复运行；不能从两次不同答案直接归因于客户端。

以上为待做练习，本次没有修改或运行这些 notebook。

## 8 周日课程与 Generative Agents 阅读

周日课程的提示词规格、指标博弈、留出评测与金库实验，见 [复习总纲](复习总纲.zh.md) 和 [原实验记录](lab-log.zh.md)。这些是周日内容，不混入今天 Zoom Lab 的完成记录。

周日还讲了 *Generative Agents: Interactive Simulacra of Human Behavior*，本次已补充 [论文学习总结与复现路线](generative-agents-summary.zh.md)。它将记忆检索、反思、计划和环境反馈接成持续运行的系统，与今天的调用流水线和工具循环形成联系。

## 9 后续实验记录

### 9 月 29 日环境排错

19:39 截图显示 `%run supportvectors-common.ipynb` 缺少 `nbformat`；补装后，19:40 截图进一步暴露缺少 `numpy`。检查发现原 `.venv` 使用 Python 3.14.6，而项目要求 Python 3.12，且依赖未装齐。

本次保留原环境，通过 `UV_PROJECT_ENVIRONMENT=.venv312 uv sync --python 3.12 --locked` 创建独立 Python 3.12 环境并安装锁定依赖。使用 notebook 时需切换内核至本项目 `.venv312/bin/python`，再从初始化单元格开始运行。这是环境准备完成，不代表课程集群或模型调用已验证。

每完成一个实验，追加：时间、notebook 与单元格、模型及参数、输入、实际输出、预期、差异、修改与复测结果。对比实验保留原始输出，避免只记最终成功版本。

- [x] 确认今日主题与上周内容的关系。
- [x] 定位上周 Instructor 与结构化提示材料。
- [x] 阅读本地讲义及关键代码，整理学习地图。
- [ ] 验证 WireGuard 与课程接口连通性。
- [ ] 跑通 notebook 01，并记录实际输出。
- [ ] 完成至少一个流水线或停止条件改进实验。
- [ ] 跑通 notebook 02–03，核对图片转录与分析。

前置：[Week 01 Lab 学习总结](../ai-agents-week-01/lab-summary.zh.md)。
