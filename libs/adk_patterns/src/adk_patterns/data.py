"""用户消息与节点数据的转换。"""
from google.genai import types


def content_to_text(value):
    """支持入口 Content 和后续节点标量；结构化对象请直接用 schema 校验。"""
    if isinstance(value, types.Content):
        return " ".join(p.text for p in value.parts or [] if p.text and not p.thought)
    return str(value)
