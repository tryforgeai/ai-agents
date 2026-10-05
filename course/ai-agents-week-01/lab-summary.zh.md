# Week 01 Lab 学习总结

记录日期：2026-09-29。根据上一周 `prompts 2` 实验材料与本次课堂回顾整理。本文记录学习内容，不代表所有示例都已在本机运行成功。

## 本周主线

从调用模型 API 开始，学习如何组织输入要求，再把模型输出变成程序能读取和校验的数据。三个层次分别是：API 调用、结构化提示词、结构化输出。

## 1 API 基础

材料：[00_primer.ipynb](prompts%202/docs/notebooks/00_primer.ipynb)、[01_llm_api.ipynb](prompts%202/docs/notebooks/01_llm_api.ipynb)。

- Chat 界面和 API 的区别：API 中需要显式组织消息、参数和上下文，程序负责处理返回结果。
- 消息带有角色和内容；模型名称与服务地址共同决定请求发给哪个服务。
- 实验涉及 temperature、top-p、输出长度和重复惩罚等参数。低温度不能当作事实正确的保证。
- OpenAI-compatible 表示接口兼容，不能仅凭客户端名称判断实际服务提供方；运行时应检查配置。

## 2 结构化提示词

对照材料：[普通提示](prompts%202/prompts/00_naive_glossary_prompt.md)、[CO-STAR 风格提示](prompts%202/prompts/01_costar_glossary_prompt.md)、[第二轮改进提示](prompts%202/prompts/02_costar_term_refinement_prompt.md)。

CO-STAR 的六个维度是 Context、Objective、Style、Tone、Audience、Response。项目模板具体采用 Role、Style、Tone、Audience、Goal、Safeguards、Response 等分节，是课程中的实际变体。

普通版本只提出生成术语表的任务；结构化版本进一步明确读者、技术深度、解释组成、例子、用途和格式要求。重点是消除任务中的歧义，而不是记住标题或认为提示越长越好。

提示里要求“不编造”仍然需要内容核验；提示要求 JSON，也应配合解析与校验。

## 3 Instructor 与 Pydantic 结构化输出

核心材料：[02_using_instructor.ipynb](prompts%202/docs/notebooks/02_using_instructor.ipynb)。

本地 notebook 的三个关键步骤：

```python
client = instructor.from_openai(OpenAI())

class ResponseModel(BaseModel):
    summary: str = Field(description="A concise summary of the input text.")
    keywords: list[str] = Field(description="A list of keywords extracted from the input text.")

# 调用 create 时传入：
# response_model=ResponseModel
```

`ResponseModel` 是自己定义的输出类型；调用中的 `response_model` 指定按哪个类型解析。示例用 `summary` 和 `keywords` 表达想获得什么数据，后续程序可以读取相应属性。

notebook 接着增加 `references` 字段，并用 `StrictResponseModel` 的 `field_validator` 检查关键词至少有 3 个。这里要分清三种约束：

| 约束 | 示例 | 含义 |
|---|---|---|
| 字段与类型 | `keywords: list[str]` | 输出需要满足数据结构 |
| 程序校验 | 关键词少于 3 个抛出错误 | 执行明确的验收规则 |
| 自然语言要求 | `Field(description=...)` 中要求内容准确 | 引导生成，但不能单独证明事实正确 |

尤其是 `references: list[str]`，类型通过并不说明文献真的存在。项目模型里的“至少 300 tokens”写在描述中，也不能等同于程序已经计数验证。

## 4 将提示与输出模型连起来

完整程序：[costar_glossary_builder.py](prompts%202/src/prompts/costar_glossary_builder.py)。模型定义：[model.py](prompts%202/src/prompts/model.py)。

```text
选择术语 ImportantTerms
    → 用 CO-STAR 提示生成 GlossaryTerm 草稿
    → 用改进提示再次生成 GlossaryTerm
    → 汇总为 Glossary
```

这是多次调用的流水线：上一阶段的数据成为下一阶段的输入。它也是 Week 02 的 prompt chaining 和自我检查示例的前置基础。

另一份应用材料是 [Old Faithful 提示](prompts%202/docs/notebooks/geyser_prompt.md)，把结构化要求用于数据分析。此处只记录材料入口，具体实验结果以实际运行日志为准。

## 5 本次回顾时发现的配置注意点

Instructor notebook 中标题为“Locally Hosted Ollama”的一节，当前代码实际写的是 OpenAI 官方地址和 `gpt-4o-mini`。标题与当前配置不同，跟课时应看实际请求参数。

同一 notebook 中途把 `client` 重新赋值为普通 `OpenAI()`，用于对比未包装的返回结果。逐格运行时需要注意变量当前指向哪种客户端。

## 复习与待验证

- [ ] 能解释 structured prompt 与 structured output 的区别。
- [ ] 阅读普通提示和 CO-STAR 提示，指出多明确了哪些要求。
- [ ] 运行 Instructor 示例并查看返回对象的字段。
- [ ] 验证关键词数量规则，记录失败时的实际行为。
- [ ] 对照术语表生成的草稿和改进稿，检查事实与格式。

本次已完成：定位并阅读相关文件，整理以上学习总结。未在本次对话中重新运行模型调用。

下一周：[Week 02 Lab 学习总结](../ai-agents-week-02/lab-summary.zh.md)。
