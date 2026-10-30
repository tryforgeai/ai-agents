from google.adk import Event
from pydantic import BaseModel
from adk_patterns import sequence, function_tool

class Numbers(BaseModel):
    a: int
    b: int

def prepare(node_input: str):
    # 与课程固定 2+3 不同：真正读取用户 JSON。
    return Event(output=Numbers.model_validate_json(node_input).model_dump())

def add(a: int, b: int) -> dict:
    """Add two integers."""
    return {"a": a, "b": b, "sum": a + b}

def finish(node_input: dict):
    return Event(output=node_input, state={"last_sum": node_input["sum"]})

root_agent = sequence("calculator", prepare, function_tool(add), finish)
