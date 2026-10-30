# ADK 可复用代码库

把课程中的 Agent、工具、图工作流、状态、结构化数据和人工审批整理成可导入的 Python 库。位于 AI Agents 项目的 `libs/adk_patterns`，与课程文件独立。

已在 Python 3.12、Google ADK **2.11.0** 上验证。依赖固定 ADK 版本；升级时先跑测试。API 是薄封装，返回的仍是 ADK Agent / Workflow / Event，可继续使用原生能力。

## 先运行一个不需要模型的例子

在 AI Agents 项目根目录执行：

```bash
bash libs/adk_patterns/run_web.sh calculator 9001
```

打开 http://localhost:9001，选择 calculator（如果界面要求），发送：

```json
{"a": 7, "b": 8}
```

结果包含 `sum: 15`，会话状态保存 `last_sum: 15`。脚本默认复用课程的 `.venv312`，通过 PYTHONPATH 加载本库，不修改现有环境。9001 被占用时改为 9002，或停止原服务。Ctrl+C 结束。

新增：Week 03 的 [reviewed_digest](examples/reviewed_digest/agent.py) 展示嵌套并行采集、去重、人工重写和批准输出。Phoenix 接入见 [详细说明](docs/PHOENIX.zh.md)。

## 示例目录和输入

每个目录包含独立 `agent.py` / `root_agent`，只启动想使用的一个示例。

| 示例 | 输入 | 实际流程 | 需要模型 |
|---|---|---|---|
| calculator | `{"a":7,"b":8}` | 校验→FunctionTool 加法→保存结果 | 否 |
| counter | `继续` | 读取状态→次数加一→输出 | 否 |
| routing | `请总结这段文字` | 关键词分类→选定处理函数；原始输入保留 | 否 |
| parallel | `hello world` | 字符数和大写并行→JoinNode→汇总 | 否 |
| loop | `0` 或 `-10` | 每轮加一→达到3或最多5轮→报告状态 | 否 |
| approval | `增加输入校验` | 固定草稿→暂停→人工选择→返回决定 | 否 |
| reviewed_digest | `AI` | 模拟采集→去重→写稿→审批→有限重写/输出 | 否 |
| phoenix | `请用工具计算7加8` | 模型工具调用与追踪；使用专用启动器 | 是 |
| travel | 下面的旅行 JSON | schema→模型→结构化行程 | 是 |
| agent_tools | `10 英里是多少公里？` | 模型→按需调用函数→回答 | 是 |
| mcp | 根据服务器能力提问 | 模型→MCP 工具→回答 | 是，另需 MCP 服务 |

routing 的处理函数只是演示路由，不会真的生成摘要。approval 不会执行修改，也不会自动重写。loop 只是确定性演示，可以换成 Agent 节点和业务停止判断。

## 运行旅行 Agent

模型配置来自环境变量，没有把课程内网地址或密钥写入库。OpenAI 示例：

```bash
export ADK_MODEL=gpt-4o-mini
# 在自己的终端设置 OPENAI_API_KEY，不要提交到 Git。
bash libs/adk_patterns/run_web.sh travel 9001
```

使用自己的 OpenAI-compatible 服务时，设置 `ADK_MODEL`、`ADK_API_BASE`，以及需要时的 `ADK_API_KEY`。例如 `openai/your-model`；准确标识以服务端为准，不要盲目增删 `openai/` 前缀。Gemini 原生接入可使用 `make_agent(..., model="你的 Gemini 模型名称")`。

在网页发送：

```json
{"city":"上海","start_date":"2026-10-10","days":2,"interests":["美食","博物馆"]}
```

```text
JSON 输入 → TravelRequest 校验 → itinerary_agent → TravelPlan → 网页结果
                                                    ↓
                                           state["last_plan"]
```

这里校验日期、城市非空和天数 1～30。没有自然语言信息提取、实时搜索或审批。`output_key` 记录 Agent 输出，存储形态以 ADK 事件为准；不是承诺保存 Pydantic 实例。

`.env.example` 仅作模板，库不会自动扫描或加载 .env。避免导入库时覆盖使用方环境。

## 在其他项目中导入

激活目标 Python 虚拟环境后，在项目根目录执行：

```bash
python -m pip install -e "./libs/adk_patterns"
```

然后可以直接使用：

```python
from adk_patterns import make_agent, sequence

writer = make_agent("writer", "将用户需求整理成三个实施步骤。")
root_agent = sequence("planning", writer)
```

需要设置模型环境变量。安装会解析 pyproject 中的依赖；建议为新项目使用独立虚拟环境。无需安装的方式是把本库 `src` 目录加入 PYTHONPATH，启动脚本已经这样做。

## 模式速查

| 复用入口 | 用途 | 关键约定 |
|---|---|---|
| `ModelConfig` / `make_agent` | 模型配置、单轮 Agent、工具和 schema | 不传 model 时读取 ADK_MODEL |
| `sequence(name, *nodes)` | 顺序处理 | 上一步 output 传入下一步 |
| `branching(name, router, routes)` | 条件路由 | router 返回 output 和 route；所有可能路由需映射 |
| `parallel(name, *workers, reducer=...)` | 并行后汇总 | JoinNode 等待全部；reducer 按节点名取结果 |
| `bounded_loop(name, worker, is_done, max_iterations=5)` | 有上限的循环 | 同步 is_done；每次调用重置计数；输出 completed/exhausted |
| `approval_workflow(name, draft_node)` | 人工审批 | RequestInput 暂停；原会话恢复；返回结构化决定 |
| `function_tool(function)` | 函数作为图节点工具 | 函数提供类型注解和 docstring |
| `mcp_http(url, headers=...)` | 外部 MCP 工具 | Streamable HTTP；调用方负责服务可达和资源清理 |
| `crewai_tool(...)` | 包装第三方工具 | 可选依赖，按需导入 |
| `LocalSession` | Notebook / Python 运行 | 同一对象和 session_id 才复用状态 |
| `print_event` / `event_text` | 查看事件和响应 | 不打印 thought；原始事件仍可自行检查 |
| `enable_phoenix(project_name, endpoint=...)` | 显式开启追踪 | 先配置接收端并安装 tracing extra |

`Context`、`Event`、`Workflow` 等直接从 `google.adk` 导入，不再重复封装。需要模型多轮工具行为等更深定制时，直接使用原生 Agent 参数。

### 顺序和数据传递

```python
from google.adk import Event
from adk_patterns import sequence

def normalize(node_input: str):
    return Event(output=" ".join(node_input.split()))

def finish(node_input: str):
    return Event(output={"text": node_input}, state={"last_text": node_input})

root_agent = sequence("normalize_text", normalize, finish)
```

入口消息通常是 Content；`node_input: str` 让 ADK 提取文本。若同一节点在循环里接收不同类型，使用无类型 node_input 加 `content_to_text`，或设计统一 schema，避免把后续整数硬校验为字符串。

### 分支必须传递数据

```python
return Event(output=node_input, route="support")
```

只写 route 不代表你已经明确传递了业务数据。路由函数可以基于规则，也可以由模型生成分类结果后再路由。

### 状态与输出分开

```python
from google.adk import Context, Event

def count(node_input, ctx: Context):
    attempts = ctx.state.get("attempts", 0) + 1
    return Event(output={"attempts": attempts}, state={"attempts": attempts})
```

output 是后续节点数据；state 是会话中的共享小数据；message 是用户进度提示。内存服务不是磁盘持久化，进程退出就丢失。

### Notebook 中运行和查看结果

完成安装（或设置 PYTHONPATH），先定义 root_agent，再运行：

```python
from adk_patterns import LocalSession, print_event

client = LocalSession(root_agent)
session_id = await client.create()

async for event in client.stream(session_id, "你的输入"):
    print_event(event)

print(await client.state(session_id))
# 想继续同一会话：复用 client 和 session_id 再调用 stream。
# 全部运行结束后再关闭：
await client.close()
```

结构化输入可传 dict 或 Pydantic 对象，stream 会转换为 JSON。普通脚本用 `asyncio.run(main())`，Notebook 用顶层 await。

### 人工审批恢复

ADK Web 会处理交互。Python 客户端需要从事件中的 `adk_request_input` function_call 获取 id，携带相同 id 返回结构化回复；只发字符串 "approve" 不等同于恢复请求。

```python
from google.genai import types

# call 是暂停事件 part.function_call，保持同一 client / session_id。
reply = types.Content(role="user", parts=[types.Part(
    function_response=types.FunctionResponse(
        id=call.id, name=call.name,
        response={"decision": "approve", "notes": ""},
    )
)])
async for event in client.stream(session_id, reply):
    print_event(event)
```

approve/revise/reject 当前只记录决定。如需执行、重写或拒绝分支，在返回结果后追加显式路由；不要把“已批准”文案当作已经执行操作。

### MCP、第三方工具与追踪

```python
from adk_patterns import mcp_http

toolset = mcp_http("http://127.0.0.1:9000/mcp")
# 传给 make_agent(..., tools=[toolset])。
# 自己管理生命周期时，在同一异步生命周期结束处执行：
# await toolset.close()
```

Google Search 可直接作为原生工具传入兼容的 Gemini Agent；不能假设所有工具都支持所有模型。

`enable_phoenix` 现在要求显式 endpoint 或 PHOENIX_COLLECTOR_ENDPOINT，支持 enabled、mode、batch；返回 provider 可 force_flush。旧的单参数调用需要先配置 endpoint。

可选安装：`python -m pip install -e '.[crewai]'` 或 `'.[tracing]'`（在本库目录执行）。追踪可能发送提示词、输出和工具内容，只有显式调用 `enable_phoenix` 才启用本库的追踪配置。

## 验证

从 AI Agents 根目录运行，不需要模型密钥：

```bash
PYTHONPATH=libs/adk_patterns/src course/ai-agents-week-02/google_adk_basics/.venv312/bin/python -m unittest discover -s libs/adk_patterns/tests -v
```

测试实际驱动 ADK Runner：用户数字而非固定值、无效输入、会话连续性/隔离、分支数据保留、并行汇总、循环成功/耗尽/重新计数、审批暂停及三种决定恢复、MCP 对象构造，以及 ADK Web 应用发现和 `/run` 接口。共 16 项测试。

Web 验证使用进程内 TestClient，无需绑定端口；当前执行环境禁止监听端口，因此未进行真实浏览器端口访问验证。

没有替你调用收费模型或连接外部 MCP/CrewAI/Phoenix 服务；这些集成需要各自配置后做端到端验证。

## 参考与扩展

图语法采用本地 ADK 2.11.0，并对照 [Google ADK 官方图工作流文档](https://github.com/google/adk-python/blob/main/docs/guides/workflow/graph/index.md)。并行必须显式汇总，循环必须有退出路径，详见 [官方 Workflow 文档](https://github.com/google/adk-python/blob/main/docs/guides/workflow/workflow/index.md)。

新业务建议复制一个 examples 子目录，替换 schema、指令和工具；原始 edge 图仍然可用。暂未封装部署、长期记忆、自动审批执行和自然语言表单提取。

## Week 03：嵌套工作流与有上限的人工重写

`reviewed_pipeline(name, prepare, writer, publish, max_revisions=2)` 将采集/分析子图、写稿节点、审批和输出节点连接起来。writer 使用 state 中的 source_material、review_draft、review_feedback；approve 进入 publish，reject 结束，超过修订上限返回 exhausted。prepare 可直接传 parallel(...) 返回的 Workflow。

字段约定是共享 state 契约，单一会话不要并发运行多个同名审核流程。每次开始会清空审核计数和反馈。参考 examples/reviewed_digest。
