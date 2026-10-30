# LLM Patterns：Week 01–03 通用代码库

与 ADK 无关的基础层：统一文本/结构化调用、CO-STAR、few-shot、提示链、有限重写、真正多次采样投票、工具循环、图片输入、确定性计算和路由评估。模型 API 依赖按需安装，导入库不会读取 .env、联网或调用模型。

## 不用密钥先体验

从 AI Agents 项目根目录执行：

```bash
PYTHONPATH=libs/llm_patterns/src course/ai-agents-week-02/google_adk_basics/.venv312/bin/python libs/llm_patterns/examples/offline_demo.py
```

演示会输出日期差 `497`、精确金额 `0.30`、投票、数据链和路由评估。工具循环的决策是模拟的，计算是真实 Python 函数。

## 安装与模型调用

激活目标虚拟环境后，在项目根目录执行：

```bash
python -m pip install -e "./libs/llm_patterns[api]"
```

配置环境：`LLM_MODEL`、`OPENAI_API_KEY`；兼容服务另设 `OPENAI_BASE_URL`。`INSTRUCTOR_MODE=json` 或 `tools` 显式选择，不根据地址猜测服务能力。使用 OpenAI SDK 时模型值是服务端模型 ID，不需要添加 LiteLLM 专属路由前缀。

```python
from pydantic import BaseModel, Field
from llm_patterns import CompletionClient

class Summary(BaseModel):
    summary: str
    keywords: list[str] = Field(min_length=3)

client = CompletionClient.from_env()
try:
    text = client.complete("简单解释 Agent。")
    data = client.complete("总结 Agent，并提取至少三个关键词。", response_model=Summary)
    print(text)
    print(data.summary, data.keywords)
finally:
    client.close()
```

max_retries 默认 2，timeout 默认 60 秒；SDK 请求重试与 Instructor 解析重试属于两层，不能把它当作总调用次数上限。参数如 temperature/max_tokens 按具体模型支持程度传入。结构校验不验证事实和引用真实性。

## 模式速查与职责

| 入口 | 来自 lab 的概念 | 复用方法 |
|---|---|---|
| CompletionClient | 文本/API/Instructor | 切换 model、base_url、schema |
| PromptSpec | CO-STAR、角色/受众/格式 | render() 后传模型；内容由业务填写 |
| few_shot_messages | Few-shot | 明确的 user/assistant 示例对 |
| run_chain / Step | 草稿改进、分解、元提示、递进处理 | 每一步读原始输入及全部前序结果 |
| refine | 有限反馈重写 | review 返回 bool 和反馈；revise 改稿 |
| sample_vote | Self-consistency | 多次独立调用；无严格多数返回 None |
| run_tool_loop / Tool / Action | Action→Observation | 仅调用注册工具；观察来自真实执行 |
| image_data_url / vision_messages | 图片+文字调用 | 从文件内容识别 MIME，支持多个图片 |
| days_between / sum_amounts | Run, don't reason | 日期运算和 Decimal 金额求和 |
| routing_report | skill 触发评估 | None 表示不应触发；记录错触发/漏触发 |

### 多步骤保留完整上下文

```python
from llm_patterns import Step, run_chain

result = run_chain("原始需求", [
    Step("outline", lambda s: client.complete("列提纲：" + s["input"])),
    Step("draft", lambda s: client.complete("依提纲写稿：" + s["outline"])),
    Step("review", lambda s: client.complete(
        "对照需求评估草稿。需求：" + s["input"] + "；草稿：" + s["draft"])),
])
```

这段放在 client 的生命周期内。Step 接收到上下文副本，避免某一步意外修改前序结果。步骤名不能重复或使用保留名 input。

元提示应先生成完整 prompt 字符串，再交给下一步使用，不能直接把模板对象的 repr 当成完整提示。提纲→正文→评论是链；要实际重写，使用 refine 或增加重写 Step。

### 有限重写

```python
from llm_patterns import refine
result = refine(
    "草稿",
    review=lambda text: (len(text) >= 10, "请补充一个例子"),
    revise=lambda text, feedback: text + "。例如：一个简单示例。",
    max_revisions=2,
)
```

这只是演示验收规则。业务里替换为真实检查或模型评议；模型自评通过不等于事实已证实。最多 review 三次、revise 两次，耗尽后 status=exhausted。

### 工具循环

`decide(request, history)` 返回 Action 或可校验的字典：

```python
{"kind":"tool", "tool":"days_between", "arguments":{"start":"2020-07-22","end":"2021-12-01"}}
{"kind":"finish", "answer":"497 天"}
```

每个 Tool 指定 Pydantic 参数模型和 Python 函数。未知工具或无效参数报错；工具异常作为失败观察传回下一次决策。工具动作模型没有 observation 字段，防止把模型自述当作执行证据。不执行模型给出的 shell/python 字符串，没有 eval。max_steps 限制决策次数，不限制单个外部工具耗时；调用方为网络工具设置 timeout，并只注册当前业务允许执行的工具。

## 视觉输入

`examples/vision_call.py` 展示完整调用。图片签名识别支持 PNG/JPEG/GIF/WebP，签名不是完整图片解码验证；最终由模型服务检查图片是否有效。先转录和检查不确定字符，再解释，避免把误读公式当成事实。

## 范围与验证

课程的“单次要求多个候选”不等于真实树搜索，也不等于多次采样投票。本库提供可执行的多次采样和有限重写，不声称实现完整 Tree-of-Thought 或 Reflexion 论文算法。Zero-shot / Role / CoT 等单次提示无需各造一个 API，可用 PromptSpec 明确目标、答案格式和简短可核查说明。

11 项测试通过，包括实际 OpenAI SDK + Instructor 在本地 mock HTTP 上完成结构化响应解析，随后仍能正确进行文本请求。没有调用真实模型。

```bash
PYTHONPATH=libs/llm_patterns/src course/ai-agents-week-02/google_adk_basics/.venv312/bin/python -m unittest discover -s libs/llm_patterns/tests -v
```

完整来源与覆盖边界见 [lab 对照表](../LAB_MAP.zh.md)。
