from google.adk import Event
from adk_patterns import approval_workflow

def draft(node_input: str):
    return Event(output=f"需求：{node_input}。计划：确认输入、实现修改、运行验证。")

# 固定草稿方便离线体验；可替换为 make_agent(...)。
root_agent = approval_workflow("approval_demo", draft)
