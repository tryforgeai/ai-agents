from google.adk import Event
from adk_patterns import bounded_loop, content_to_text

def increment(node_input):
    return Event(output=int(content_to_text(node_input)) + 1)

root_agent = bounded_loop("loop_demo", increment, lambda value: value >= 3,
                          max_iterations=5)
