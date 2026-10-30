from google.adk import Event
from adk_patterns import branching

def classify(node_input: str):
    text = node_input.lower()
    route = "summary" if "总结" in text or "summary" in text else "support"
    return Event(output=node_input, route=route)

def summarize(node_input: str):
    return Event(output={"handler": "summary", "request": node_input})

def support(node_input: str):
    return Event(output={"handler": "support", "request": node_input})

# 演示确定性路由；可把 summarize/support 替换为模型 Agent。
root_agent = branching("routing", classify, {"summary": summarize, "support": support})
