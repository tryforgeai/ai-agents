"""Week 03 pattern, synthetic data only; no real news APIs or publication."""
from google.adk import Context, Event
from adk_patterns import parallel, reviewed_pipeline


def source_one(node_input: str):
    return Event(output=[{"id": "a", "title": f"演示资料 A：{node_input}"}])


def source_two(node_input: str):
    return Event(output=[{"id": "a", "title": f"演示资料 A：{node_input}"},
                         {"id": "b", "title": f"演示资料 B：{node_input}"}])


def deduplicate(node_input: dict):
    items = {}
    for source in node_input.values():
        for item in source:
            items.setdefault(item["id"], item)
    return Event(output=list(items.values()))


collection = parallel("collect", source_one, source_two, reducer=deduplicate)


def write(node_input, ctx: Context):
    titles = "\n".join(f"- {item['title']}" for item in ctx.state["source_material"])
    return Event(output=f"# 演示简报\n{titles}\n修改意见：{ctx.state['review_feedback']}")


def publish(node_input: str):
    return Event(output={"status": "approved", "markdown": node_input},
                 state={"final_markdown": node_input})


root_agent = reviewed_pipeline("reviewed_digest", collection, write, publish, max_revisions=2)
