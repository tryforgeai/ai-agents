from adk_patterns import make_agent

def miles_to_kilometers(miles: float) -> float:
    """Convert a distance in miles to kilometers."""
    return miles * 1.60934

root_agent = make_agent("converter", "请调用工具完成英里到公里的换算。",
                        tools=[miles_to_kilometers])
