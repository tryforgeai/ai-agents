# AI Agents 方法实验台

本地 Web 应用：浏览两个库的 **32 个公开入口**，编辑 JSON 输入、运行真实库代码、查看 Python 示例/实现，并搜索原始课程和 lab 源码。不是 ADK Web 的替代品；此处聚焦方法教学，ADK Web 仍适合完整 Agent 项目的调试。

## 启动

在 AI Agents 根目录执行：

```bash
bash libs/workbench/run.sh 9010
```

浏览器打开 http://127.0.0.1:9010。脚本默认使用课程的 `.venv312`，默认端口 9010，避免与 ADK Web 的 9001、MCP 的 9000、Phoenix 的 6006 混淆。Ctrl+C 停止。

如果使用自己的 Python 环境，先安装两个库和 Web 依赖：

```bash
python -m pip install -e libs/adk_patterns -e 'libs/llm_patterns[api]' fastapi uvicorn
WORKBENCH_PYTHON="$(command -v python)" bash libs/workbench/run.sh 9010
```

库中 ADK 版本固定为 2.11.0。配置可选依赖应使用启动工作台的同一个 Python 环境。

## 使用

1. 左侧按名称、函数名、概念搜索，或筛选无需外部服务/外部服务。
2. 编辑输入 JSON，点击运行。字符串保留双引号；错误会显示在结果区。
3. 结果支持下载 JSON；图模式显示事件和会话状态。
4. 人工审批会显示专门的批准/修改/拒绝按钮。reviewed_pipeline 的修改意见会传回写稿节点，最多重写两次。
5. LocalSession 示例连续运行会递增计数；“新会话”清空当前方法的会话。
6. 下方切换“运行示例 / 库实现”，复制对应 Python 代码。无状态方法示例包含导入与调用入口；ADK 图示例定义 root_agent，可放入自己的 ADK 应用。
7. “课程与源码”支持按文件名和正文搜索、按 week/库筛选、分页、查看和复制源码。Notebook 展开为代码/Markdown 单元格，**不加载历史输出**。

`/` 快捷键聚焦当前页面的搜索框。页面在窄屏切换为上下布局。

## 外部依赖如何运行

卡片会标注依赖、所需环境变量和“依赖与启动方式”。环境变量只在服务端终端设置，不在网页收集 API key。默认不加载 `.env`。

| 方法 | 配置/要求 | 本次行为 |
|---|---|---|
| CompletionClient | LLM_MODEL、供应商密钥；可选 OPENAI_BASE_URL | 实际文本或 Instructor 结构化调用 |
| make_agent | ADK_MODEL、供应商密钥；可选 ADK_API_BASE / ADK_API_KEY | 实际单轮 Agent 请求 |
| mcp_http | MCP_URL、已运行的 Streamable HTTP 服务 | 发现工具；不执行远端工具 |
| enable_phoenix | PHOENIX_COLLECTOR_ENDPOINT；云端密钥按需配置 | 独立进程尝试导出一个合成 span |
| crewai_tool | crewai / crewai-tools | 实际包装并调用本地大写工具；工作进程关闭遥测并使用临时存储 |

缺少必需的模型/服务地址变量时显示配置提示；配置后重启工作台。实际外部请求需要勾选本次运行选项。Phoenix 的 force_flush 不证明服务端接收成功，请在项目 UI 检查；详见 [Phoenix 接入](../adk_patterns/docs/PHOENIX.zh.md)。

sample_vote 使用你提供的候选值，tool_loop 使用模拟决策和真实计算，reviewed_pipeline 使用模拟新闻资料。界面注明这些边界，不把模拟结果当成真实模型/新闻服务结果。

图片方法支持上传最大 2 MB 的 PNG/JPEG/GIF/WebP，只转换 data URL 和消息格式，不上传到模型。复制图片示例代码时需要替换 your-image.png。

## 搜索范围

启动时索引 `course/` 和 `libs/` 的 `.py`、`.md`、`.ipynb`、`.toml`、`.sh`，跳过隐藏目录、虚拟环境、node_modules、构建结果、符号链接以及大于 2 MB 的文件。不索引 `.env`、Notebook 输出或图片/PDF二进制。新增课程文件后重启工作台刷新目录；已索引文件在打开时读取当前版本。

源码只读，没有运行任意 Python 的编辑器。输入只传给服务器允许的预设示例，不能指定任意文件/函数执行。服务监听 127.0.0.1，拒绝跨源浏览器请求。

## 执行边界

- 非会话示例在独立进程运行，60 秒超时后终止；最多四个并发工作进程。
- 图示例使用真实 ADK Runner。内存会话最多 64 个，30 分钟未使用后在新建会话时回收；同一会话串行执行。
- 页刷新会清空前端会话引用；不要把它当作长期存储。停止服务会关闭所有会话。
- 待审批时先提交决定或重置，不能覆盖当前审批。
- 没有对外部署或修改原始课程文件。

## 文件

| 文件 | 用途 |
|---|---|
| catalog.py | 公开 API → 分类、依赖、默认输入、演示和源码 |
| demos.py | 固定、可审查的执行示例 |
| worker.py | 隔离进程、输出捕获和密钥值过滤 |
| server.py | FastAPI、执行会话、审批和源码端点 |
| sources.py | 只读文件索引与 Notebook 提取 |
| static/ | 无构建依赖的网页 |
| tests/ | 方法覆盖、运行、会话、审批、搜索和边界测试 |

## 验证

从项目根目录运行：

```bash
PYTHONPATH=libs/workbench:libs/adk_patterns/src:libs/llm_patterns/src course/ai-agents-week-02/google_adk_basics/.venv312/bin/python -m unittest discover -s libs/workbench/tests -v
```

接口测试覆盖全部导出方法的目录与源码、可运行离线演示、非法输入、图片转换、计数器、审批重写/批准、源码搜索、Notebook 输出排除、目录穿越和跨源请求拒绝。浏览器中另验证真实界面默认输入、运行、审批重写、源码搜索和打开。外部模型、MCP/Phoenix 服务未在本次发起真实请求。
