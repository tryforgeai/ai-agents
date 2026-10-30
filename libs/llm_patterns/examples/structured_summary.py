"""Requires pip install -e '.[api]' and LLM_MODEL / OPENAI_API_KEY."""
from pydantic import BaseModel, Field
from llm_patterns import CompletionClient, PromptSpec, Step, run_chain

class Summary(BaseModel):
    summary: str
    keywords: list[str] = Field(min_length=3)

if __name__ == "__main__":
    client = CompletionClient.from_env()
    try:
        instruction = PromptSpec("帮助初学者学习 ADK", "总结输入材料", response="摘要与至少三个关键词").render()
        result = run_chain("ADK 可以组织模型、工具、状态和工作流。", [
            Step("draft", lambda s: client.complete(instruction+"\n"+s["input"], response_model=Summary)),
            Step("revised", lambda s: client.complete(
                "根据原文检查并改进草稿，保留有依据的内容。\n原文："+s["input"]+
                "\n草稿："+s["draft"].model_dump_json(), response_model=Summary)),
        ])
        print(result["revised"].model_dump_json(indent=2))
    finally:
        client.close()
