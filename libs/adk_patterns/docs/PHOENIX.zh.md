# Phoenix 与 ADK 的集成

阅读依据：[Google ADK 官方 Phoenix 集成](https://adk.dev/integrations/phoenix/)。官方核心做法是安装 `arize-phoenix-otel` 和 `openinference-instrumentation-google-adk`，配置 collector endpoint / cloud key，然后调用 `register(project_name=..., auto_instrument=True)`。

数据链：ADK 执行 → instrumentation 生成 span → OpenTelemetry processor/exporter → Phoenix collector → Phoenix UI。ADK Web 是运行和调试入口，Phoenix 是跨请求的追踪查看端；启用 tracing 不等于启动 Phoenix 服务，也不会自动执行评估。

## 端口和角色

| 地址 | 用途 |
|---|---|
| http://localhost:9001 | ADK Web：发请求、审批、看执行事件 |
| http://localhost:6006 | 本地 Phoenix：查看项目和 traces |
| http://localhost:6006/v1/traces | Phoenix HTTP OTLP 接收地址，本库使用此协议 |
| http://localhost:4317 | 常见的 Phoenix gRPC collector；不要给本库的 HTTP 配置使用 |
| http://localhost:9000/mcp | 课程 MCP 服务，与 tracing 无关 |

## 两种模式

| 模式 | 用途 | 行为 |
|---|---|---|
| openinference | 官方推荐的 Phoenix 语义追踪 | register(auto_instrument=True)，自动接入已安装的 OpenInference 集成 |
| native | 想保留 ADK Web 原生 Trace，并把同一原生 span 导出到 Phoenix | 使用原生 OTel provider/exporter，不安装 OpenInference 补丁 |

默认函数模式是 openinference。Web 专用启动器默认 native。

本地核对版本：ADK 2.11.0、arize-phoenix-otel 0.17.2、openinference-instrumentation-google-adk 1.0.2。当前 OpenInference 的 `_instrument()` 会关闭已有 ADK tracers；Phoenix provider 的 add_span_processor 默认又会替换默认 processor。这是这组安装版本的源码观察，不是所有未来版本的通用结论。

native 实现使用标准 OTel provider，添加 exporter 时保留已有 processors，不复制课程中的 monkey-patch 方法。两种模式不能在同一进程混用；切换模式/项目需要重启。native spans 可能没有 OpenInference 增补的 LLM 语义字段；能看到追踪不代表每个 token/工具字段都齐全。

## 安装和启动

激活计划运行的虚拟环境后，在项目根目录执行：

```bash
python -m pip install -e "./libs/adk_patterns[tracing]"
```

本地 Phoenix 服务另需安装 `arize-phoenix`，也可以使用已运行的 Phoenix 或云端。示意命令（安装服务端之后）：

```bash
phoenix serve
```

再开终端，从 AI Agents 根目录运行（先配置自己的模型）：

```bash
export ADK_MODEL=gpt-4o-mini
# 自行设置 OPENAI_API_KEY，或配置自己的 ADK_API_BASE / ADK_API_KEY。
export PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/v1/traces
export PHOENIX_PROJECT_NAME=ai-agents-labs
export ADK_PHOENIX_MODE=native
course/ai-agents-week-02/google_adk_basics/.venv312/bin/python libs/adk_patterns/phoenix_web.py
```

这要求依赖安装在所用的 `.venv312` 中；也可换成你新建的虚拟环境的 python。

打开 9001，选择 phoenix，输入“请用工具计算 7 加 8”。再打开 Phoenix 6006，选择 ai-agents-labs 项目，查看新 trace。批量导出有短暂延迟，脚本关闭时会 force_flush。不要将启动成功或测试中的内存 span 当成已经在 Phoenix 收到真实数据。

## 在自己的 Python 程序接入

```python
from adk_patterns import enable_phoenix

provider = enable_phoenix(
    "my-project",
    endpoint="http://127.0.0.1:6006/v1/traces",
    mode="openinference",
)
# 创建并运行 Agent / Runner …
provider.force_flush()
```

配置应在开始请求、启动 ADK Web 之前执行。ADK Web 模式使用 phoenix_web.py，确保项目 resource 和导出器先初始化。native 模式发现已存在但项目不匹配的 provider 会报错，而不是悄悄把数据放进错误项目。

云端：使用服务页面给出的 collector endpoint 和 PHOENIX_API_KEY。native 要求完整 `/v1/traces` HTTP 地址，具体空间路径以 Phoenix 页面为准。密钥由 Phoenix exporter 从环境读取，本库不打印密钥。

`enabled=False` 直接返回 None，不进行注册；不要调用它的 force_flush。库默认不会自动开启追踪。公开模式 API 幂等：同一配置重复调用复用 provider，不重复添加 exporter；更换配置要求重启。

## 查看和排错

- ADK Web 有回复、Phoenix 没 trace：检查 collector 地址/协议、项目选择、服务是否运行，等待 batch 导出或 force_flush。
- 启用后出现延迟：检查 collector 是否不可达；batch=True 减少请求线程上的导出等待，但不修复连接问题。
- Phoenix 有 trace，ADK Web Trace 不见：核对模式，当前安装版本的自动 instrumentation 会影响原生 tracers；用 native 启动器并重启进程。
- import 出现 OpenTelemetry 内部名称缺失：先重启 Notebook kernel；若新进程也失败，再检查依赖一致性，不能一律归因于代码拼写。
- trace 可能包含提示词、响应和工具参数；使用自己的本地/授权 collector，并按数据需求配置脱敏。

已验证：官方 register 的调用参数/幂等性；native 真实 ADK 执行产生的 OTel span 到两个内存 exporter 同时导出，证明不会覆盖另一 processor。尚未连接真实 Phoenix collector 或调用模型；不能保证当前环境的 collector/云密钥可用。
