from google.adk import Context, Event
from adk_patterns import sequence

def count(node_input, ctx: Context):
    attempts = ctx.state.get("attempts", 0) + 1
    return Event(output={"attempts": attempts}, state={"attempts": attempts},
                 message=f"本会话已执行 {attempts} 次")

root_agent = sequence("counter", count)
