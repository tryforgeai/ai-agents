"""Enable tracing explicitly with the dedicated launcher (see docs)."""
from adk_patterns import make_agent


def add(a: int, b: int) -> int:
    """Add two integers exactly."""
    return a + b


root_agent = make_agent("traced_calculator", "调用 add 工具计算用户提供的两个整数。", tools=[add])
