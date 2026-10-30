"""模型配置：不硬编码课程内网地址，不读取或打印密钥。"""
import os
from dataclasses import dataclass, field

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm


@dataclass(frozen=True)
class ModelConfig:
    model: str
    api_base: str | None = None
    api_key: str | None = field(default=None, repr=False)

    def __post_init__(self):
        if not self.model.strip():
            raise ValueError("model must not be empty")

    @classmethod
    def from_env(cls):
        """ADK_MODEL 必填；OpenAI 等供应商密钥也可以由 LiteLLM 原生读取。"""
        model = os.getenv("ADK_MODEL", "").strip()
        if not model:
            raise ValueError("请设置 ADK_MODEL，例如 gpt-4o-mini 或服务支持的模型标识")
        return cls(model, os.getenv("ADK_API_BASE") or None,
                   os.getenv("ADK_API_KEY") or None)

    def build(self):
        options = {}
        if self.api_base:
            options["api_base"] = self.api_base
        if self.api_key:
            options["api_key"] = self.api_key
        return LiteLlm(model=self.model, **options)


def make_agent(name, instruction, *, model=None, tools=None,
               input_schema=None, output_schema=None, output_key=None):
    """创建单轮 Agent。model 可传 ModelConfig、ADK 模型对象或原生 Gemini 名称。"""
    if model is None:
        model = ModelConfig.from_env()
    if isinstance(model, ModelConfig):
        model = model.build()
    return Agent(name=name, instruction=instruction, model=model,
                 mode="single_turn", tools=list(tools or []),
                 input_schema=input_schema, output_schema=output_schema,
                 output_key=output_key)
