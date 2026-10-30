from google.adk import Event
from adk_patterns import parallel

def length(node_input: str):
    return Event(output=len(node_input))

def uppercase(node_input: str):
    return Event(output=node_input.upper())

def report(node_input: dict):
    return Event(output={"length": node_input["length"], "uppercase": node_input["uppercase"]})

root_agent = parallel("parallel_demo", length, uppercase, reducer=report)
