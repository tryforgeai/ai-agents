# AI Agents 可复用代码库

| 库 | 用途 | 入口 |
|---|---|---|
| llm_patterns | API、Instructor、提示链、视觉输入、受限工具循环、精确计算、路由评估 | [中文使用说明](llm_patterns/README.md) |
| adk_patterns | Agent、图工作流、状态、审批、MCP、会话、Phoenix | [中文使用说明](adk_patterns/README.md) |

- [按 week 的 Lab → 代码对照表](LAB_MAP.zh.md)
- [Phoenix 与 ADK 的集成及启动](adk_patterns/docs/PHOENIX.zh.md)

从项目根目录先体验无需模型的流程：

```bash
bash libs/adk_patterns/run_web.sh reviewed_digest 9001
```

输入一个主题，查看模拟资料汇总，尝试 revise 并提供意见，再 approve。拒绝会结束，重写最多两次。这个示例不会抓取新闻或对外发布。

## Web 方法实验台

[workbench 使用说明](workbench/README.md)：交互运行全部 32 个公开方法入口、查看示例/实现、搜索课程与 lab 源码。

```bash
bash libs/workbench/run.sh 9010
```

打开 http://127.0.0.1:9010。需要模型或服务的方法会显示依赖和配置方式。
