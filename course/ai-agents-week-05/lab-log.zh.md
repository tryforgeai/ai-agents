# Week 05 实操记录

> 现场跑出来的结果，不是讲义内容。
> 模型 / 温度：
> 记于 2026-10-18

## 环境

```bash
# 命令待填
```

## 实验 1 · 复跑 W3 Lab `when-the-time-is-right`（课前自检）

```bash
cd ../ai-agents-week-03/when-the-time-is-right-kit
python3 dev/run_given.py                     # 100 个 given case 全跑
python3 pack.py when-the-time-is-right       # 打包 .skill
python3 check.py g-001 --invite <ics>        # 单例官方判分
```

- 结果：**100 / 100 通过**（72 book · 17 propose · 9 ask · 1 no_slot · 1 already），约 1 秒；`pack.py` 通过，打出来的包跟文件夹里现有的 `.skill` 一模一样
- 注意：`run_given.py` 喂的是**手工抽好的 request JSON**，测的只是 `schedule.py`。LLM 把邮件读成 JSON 那一步没测到，隐藏的 100 个扣分 case 主要考的就是这一步
- 待对照：今天 "What Did We Miss?" 揭晓的陷阱，跟 SKILL.md 的读信规则逐条对一遍

## 今晚可执行清单

- [ ]

## 实验 2 · FastMCP quickstart（2026-10-18 19:40）

- 环境：`~/mcp-quickstart`，`.venv`，fastmcp 4.1.1 / mcp 2.3.0（全局安装时 rich 升到 15，与 instructor 冲突 → 改用项目 venv）
- server：`greet(name: str) -> str`，HTTP transport，`127.0.0.1:8000/mcp`
- client `list_tools()` 输出（= LLM 能看到的全部）：
  - name `greet`
  - description = docstring 原文
  - input_schema：`{'type': 'object', 'additionalProperties': False, 'properties': {'name': {'type': 'string'}}, 'required': ['name']}`
- `call_tool` 结果：`content=[TextContent('Hello, Ford!')]`，`structured_content={'result': 'Hello, Ford!'}`，`is_error=False`
- 观察：
  - `name: str` → `type: string`，没有默认值 → `required`；`additionalProperties: False` 拒绝多余参数（白板 3、Tools Prelude p.14 强类型）
  - 返回值有两份：给模型读的文本 `content` + 给代码用的 `structured_content`（p.17 输出）
  - `is_error` 是协议级的错误标记（p.16 契约：失败要显式报错）
  - SDK v2 把 `inputSchema` 改名为 `input_schema`（弃用警告）

### 实验 2b · 去掉类型标注（19:40）

- 改动：`def greet(name: str) -> str:` → `def greet(name):`
- input_schema：`'name': {'type': 'string'}` → **`'name': {}`**（模型只知道"有个必填参数叫 name"，不知道类型）
- 返回：`structured_content` 和 `data` 从 `{'result': 'Hello, Ford!'}` → **`None`**。去掉 `-> str` 后 FastMCP 不知道输出类型，只剩给模型读的文本，代码拿不到结构化结果
- 结论：类型标注同时决定**输入 schema**（模型怎么传、server 怎么校验）和**输出 schema**（代码能否直接用结果）。少了它，两头都丢信息 → doctor 候选检查"`@mcp.tool` 缺类型注解"有实证

### 实验 2c · 传错误类型 `{'name': 123}`（19:4x）

- 有类型版本（`name: str`）：**被拦下**
  `ToolError - 1 validation error for call[greet] / name / Input should be a valid string [type=string_type, input_value=123, input_type=int]`
- 拦截发生在 FastMCP（pydantic v2 校验）层，函数体根本没执行；pydantic v2 默认**不会**把 int 偷偷转成 str
- 错误信息写明了哪个参数、期望什么、实际收到什么 → 模型拿到这条 ToolError 可以自己改正重试（#48：说清楚是谁的问题、怎么改）
- 无类型版本（`def greet(name):`）：**悄悄通过** → `Hello, 123! | is_error = False`。错误的值进了函数体，没有任何报错
- 对照结论：同一个错误输入，有类型 = 入口拦下并说明原因；无类型 = 静默接受、产出看似正常的结果。后者更危险，因为下游看不出问题
- 踩坑（记入陷阱登记）：第一次重跑时旧 server 还占着 8000 端口（`Errno 48 address already in use`），新 server 没起来，请求被旧的有类型版本应答 → 差点得出"无类型也会被拦"的错误结论。教训：**确认测的是你以为的那个版本**——看启动日志有无 ERROR，或让 server 启动时打印版本标识；清端口用 `lsof -ti :8000 | xargs kill`
