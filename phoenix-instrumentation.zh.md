# 用 Phoenix 监控自己写的 agent loop

> 建立于 2026-09-20 · 来源：bootcamp Week 01 下午 lab 现场（讲师用 Phoenix 追 Hermes Agent）
> 配套：[`team-learning-path.zh.md`](team-learning-path.zh.md) 阶段 0–3

**Phoenix**（Arize，开源）基于 **OpenTelemetry + OpenInference 语义约定**，所以接自己写的 loop 很直接，不需要用它家的框架。

---

## 1. 起 Phoenix

```bash
pip install arize-phoenix arize-phoenix-otel openinference-instrumentation-openai
phoenix serve          # → localhost:6006
```

## 2. 注册 + 自动埋 LLM 调用

```python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer_provider = register(
    protocol="http/protobuf",
    project_name="my-agent",          # ← Phoenix 里的 project 名
)
tracer = tracer_provider.get_tracer(__name__)

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
# Anthropic / LiteLLM / Bedrock 等都有对应 instrumentor
```

> ⭐ **LLM span 不要手写。** 官方文档明说手工只在万不得已时用——messages / tools / token 数 / invocation params 这些结构化字段，手写极易漏。

## 3. 装饰器标出 loop 和工具

```python
@tracer.agent                      # 整个 loop = 一个 AGENT span
def run(task: str):
    messages = [...]
    while True:
        resp = client.chat.completions.create(...)   # ← 自动成 LLM span
        for call in resp.tool_calls:
            result = dispatch(call)
            messages.append(result)
        if verify(state):
            break

@tracer.tool                       # 每个工具 = TOOL span
def get_weather(city: str): ...
```

装饰器同时支持 sync / async / generator。也可以用 context manager 只包一段代码。

---

## ⭐ 4. 七个动词 → span kind 的映射

OpenInference 的 span kind 里，**正好有两个是为课上讲的东西准备的**：`EVALUATOR` 和 `GUARDRAIL`。

| harness 动词 | span kind | 怎么埋 |
| --- | --- | --- |
| （模型推理） | **LLM** | auto-instrumentor |
| **dispatches** | **TOOL** | `@tracer.tool` |
| 整个循环 | **AGENT** | `@tracer.agent` |
| ⭐ **verifies** | **EVALUATOR** | 手动 span，见下 |
| ⭐ **stops / escalates** | **GUARDRAIL** | 手动 span，见下 |
| **enforces / persists** | AGENT span 的 attribute | 见第 5 节 |

*（完整 span kind：LLM / EMBEDDING / CHAIN / RETRIEVER / RERANKER / TOOL / AGENT / GUARDRAIL / EVALUATOR）*

### verifier 埋成 EVALUATOR

```python
from opentelemetry.trace import Status, StatusCode

def verify(state) -> bool:
    with tracer.start_as_current_span(
        "verify.fields_complete",
        openinference_span_kind="EVALUATOR",      # ← 关键
    ) as span:
        ok = all(k in state for k in REQUIRED)
        span.set_input(state)
        span.set_output(ok)
        span.set_status(Status(StatusCode.OK if ok else StatusCode.ERROR))
        return ok
```

### 闸门埋成 GUARDRAIL

```python
def permission_gate(call) -> bool:
    with tracer.start_as_current_span(
        "gate.actuator",
        openinference_span_kind="GUARDRAIL",
    ) as span:
        allowed = call.name in SENSORS or human_approved(call)
        span.set_attribute("tool.name", call.name)
        span.set_attribute("tool.class",
                           "sensor" if call.name in SENSORS else "actuator")
        span.set_attribute("gate.allowed", allowed)
        return allowed
```

> **这么埋的好处**：verifier 和闸门是**独立 span**，不是混在日志里。
> 可以直接数「多少次 verify 失败」「多少次闸门拦截」——**阶段 2 那 50 次的统计不用另写脚本。**

---

## 5. 预算和停止埋成 attribute

```python
span.set_attribute("budget.tokens_used", used)
span.set_attribute("budget.limit", limit)
span.set_attribute("stop.reason", "success" | "insolvency" | "futility" | "deference")
```

> ⭐ **`stop.reason` 一个字段就能看出健康度。**
> 四个出口只有一个是好的。如果 **Futility 和 Deference 常年为 0**，说明你的停止规则根本没生效——不是没触发，是没写对。

**其他值得埋的 attribute**

| 字段 | 为什么 |
| --- | --- |
| `tool.class` = sensor / actuator | 权限设计的可视化 |
| `retry.count` / `retry.reason` | 闭环算术的实测数据 |
| `verify.source` = code / llm / human | 判据来自哪 —— LLM 自评要能被单独筛出来 |
| `session.id` / `task.id` | 跨轮次关联 |

---

## 6. 对应学习路线的用法

| 阶段 | 怎么用 |
| --- | --- |
| **0** 读 trace | 直接看 Hermes / Deep Agents 的 trace（它们本来就接 OpenInference） |
| **1** 裸 loop | 只接 `register()` + auto-instrumentor。**别埋 verifier——因为还没有** |
| **2** 跑坏 50 次 | 在 Phoenix 里按 span 统计失败，归纳分类 |
| **3** 加动词 | ⭐ **每加一个动词，就多一种 span kind** |

> **阶段 3 因此有了一个漂亮的自检**：
> **trace 里 span kind 的种类数，就是"你已经实现了几个动词"的可视化证明。**
> 一开始只有 AGENT / LLM / TOOL；加完 verifier 多出 EVALUATOR；加完闸门多出 GUARDRAIL。
>
> **监控的演进和 harness 的演进是同一条线。**

---

## 7. 现场观察（讲师的 lab 栈）

| | |
| --- | --- |
| tracing | **Phoenix**，本地 `localhost:6006`，project = `hermes-agent` |
| harness | **Hermes Agent** |
| 模型 | **deepseek-v4.1-flash** ← 故意用小模型（*small models used agentically*） |
| 任务 | reliability lab · 蒸汽机，`skill_view(name="reliability-lab:engine-open")` |

**一次 LLM 调用的 token 结构**：prompt **23,434** / completion **206** / total 23,640，延迟 6.4s，整条 trace 50.7s。

> ⭐ **输入是输出的 114 倍。** 十步就是二十多万 token。
> **这就是 agent 的成本结构——贵在 context，不在生成。** 谈 compute economics 要从这里算起。

---

## 相关

- [`team-learning-path.zh.md`](team-learning-path.zh.md)
- [`course/ai-agents-week-01/delta.zh.md`](course/ai-agents-week-01/delta.zh.md)
- [Phoenix — Instrument Python](https://arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/instrument-python)
