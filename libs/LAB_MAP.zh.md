# Lab → 可复用代码对照

本次阅读了本地 Week 00–03 的笔记、Week 01/02 notebooks、Week 01 glossary 程序和 Week 03 newsletter 的入口/采集/审核/追踪模块。代码库是按这些概念重新组织的通用实现；没有把整套课程应用移进 lib，也没有复制课程密钥、内网地址和业务提示词。

## 分层

```text
llm_patterns：消息、schema、提示、多次调用、工具观察、确定性计算
      ↓ 可在节点中使用
adk_patterns：Agent、图、会话、审批、外部工具、追踪
      ↓
examples：可运行的业务演示；复制后替换业务内容
```

两个库独立安装，不强制相互依赖。通用 LLM 库不强制安装 ADK；ADK 库不强制安装 Instructor。

## 按周对照

| 本地来源 | 提取出的模式 | 新库位置 | 边界 |
|---|---|---|---|
| [Week 00 总结](../course/ai-agents-week-00/summary.zh.md) | 有限循环、明确停止、人工闸门 | adk bounded_loop/reviewed_pipeline；llm run_tool_loop | 本地该周是笔记，未找到独立 Python lab；没有声称提取可运行原程序 |
| [Week 01 API notebook](<../course/ai-agents-week-01/prompts 2/docs/notebooks/01_llm_api.ipynb>) | 统一模型/服务配置、消息调用 | llm client.py | 不猜测供应商，不硬编码模型地址 |
| [Week 01 Instructor notebook](<../course/ai-agents-week-01/prompts 2/docs/notebooks/02_using_instructor.ipynb>) | schema 输出与实际规则校验 | CompletionClient、structured_summary.py | 结构正确不证明事实正确 |
| [Week 01 glossary](<../course/ai-agents-week-01/prompts 2/src/prompts/costar_glossary_builder.py>) | 草稿→改进；结构化提示 | PromptSpec、run_chain、refine | 通用实现，不依赖 svlearn/课程配置 |
| [Week 02 十二种提示](../course/ai-agents-week-02/prompt_engineering/docs/notebooks/01_prompting_techniques.ipynb) | 链、分解、重写、采样、工具循环 | llm pipelines.py、tool_loop.py | 不把一次生成多条路径说成完整树搜索 |
| [Week 02 图片调用](../course/ai-agents-week-02/prompt_engineering/docs/notebooks/02_vl_call.ipynb) / [LiteLLM 版本](../course/ai-agents-week-02/prompt_engineering/docs/notebooks/03_vl_litellm_call.ipynb) | 本地图片→data URL→消息 | llm vision.py | 输出是否正确需人工核对 |
| [Week 02 ADK](../course/ai-agents-week-02/google_adk_basics/docs/notebooks/google_adk_basics.ipynb) | Agent/工具/顺序/分支/并行/状态/审批 | adk_patterns 原有模块 | 2.11.0 上验证 |
| [Week 03 newsletter](../course/ai-agents-week-03/newsletter_adk/README.md) | 嵌套采集→去重→写稿→审核重写→输出 | reviewed_pipeline、reviewed_digest | 演示资料明确标记为模拟；没有真实搜索/发布 |
| [Week 03 lab 实录](../course/ai-agents-week-03/lab-log.zh.md) | Run, don't reason；触发/不触发回归样例 | days_between、sum_amounts、routing_report | 根据记录重写；日志提到的 genies-kitchen 源目录当前未在本地发现 |
| [Phoenix 官方文档](https://adk.dev/integrations/phoenix/) | OTel 导出与 OpenInference | observability.py、phoenix_web.py | 区分官方自动追踪和 native 共存模式 |

## 十二种提示技巧如何落到代码

| 技巧 | 复用方式 | 没有额外承诺的部分 |
|---|---|---|
| Zero-shot | complete(prompt) | 一次调用不保证准确 |
| Few-shot | few_shot_messages | 示例代表性需要业务检验 |
| Role prompting | PromptSpec context / style / audience | 角色不等于专业资格 |
| Chain of Thought | 请求答案及简短可核查说明 | 不依赖或保存模型私有思维过程 |
| Tree of Thought | run_chain 组织候选生成与评估 | 本库没有完整搜索树与回溯引擎 |
| Meta-prompting | Step 生成完整 prompt 字符串→下一步使用 | 不把对象 repr 当指令 |
| Prompt chaining | run_chain | 保留全部命名中间结果 |
| Least-to-most | run_chain 按分解步骤执行 | 步骤需调用方构造，数值可交代码算 |
| Recursive prompting | 输出作为后续 Step 输入 | 和自动重写闭环区分 |
| Reflexion | refine 的评议→修订→再评议 | 不声称完整实现论文的记忆机制 |
| Self-consistency | sample_vote 分开调用后投票 | 没有多数就弃权；多数不证明正确 |
| ReAct | run_tool_loop | 真实工具观察、明确结束和步数上限 |

## 测试与外部依赖

- llm_patterns：11 项测试，含 OpenAI SDK / Instructor 的 mock HTTP 解析。
- adk_patterns：16 项测试，含嵌套工作流、审核重写/拒绝/次数耗尽、Web 接口和 tracing processor 共存。
- API/模型/MCP/新闻源/Phoenix 真实服务未连接；本次不把 mock、示例素材或对象构造等同于线上验证。
- 原课程文件不修改；新模板通过独立 examples 演示，便于日后替换或升级。
