import asyncio
import os
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# =========================
# 1) State + Config
# =========================
MODEL_NAME = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://10.0.10.70:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "not-needed"
MCP_SERVERS = {
    "mcp_server": {
        "url": "http://localhost:9000/mcp/",
        "transport": "streamable_http",
    }
}

class NewsletterState(TypedDict):
    topic: str
    messages_mcp: Annotated[List[AnyMessage], add_messages]
    raw_results: str
    newsletter: str

# Globals set in initialize_components()
llm = None
tools = None
tool_node = None
model_with_tools = None

# =========================
# 2) Initialize Components
# =========================
async def initialize_components():
    global llm, tools, tool_node, model_with_tools
    llm = ChatOpenAI(model=MODEL_NAME, base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    tool_node = ToolNode(tools, messages_key="messages_mcp")
    model_with_tools = llm.bind_tools(tools)

# =========================
# 3) Nodes
# =========================
async def research_node(state: NewsletterState) -> NewsletterState:
    """
    Ask the LLM (with tools bound) to find sources.
    First pass: it will likely emit a tool call.
    Second pass (after tool output is in the thread): it should write results without calling tools.
    """
    topic = state["topic"]
    msgs = state.get("messages_mcp", [])

    prompt = (
        "You can use the available MCP tools if (and only if) you have not already fetched results.\n"
        f"Task: Search for solid, recent sources on: '{topic}'.\n"
        "Return 5–8 concise items (title, url, 1–2 line summary).\n"
        "If you already see tool output with search results in this conversation, DO NOT call tools again; "
        "instead, summarize those items directly."
    )
    # IMPORTANT: include the running thread so the model sees ToolMessage content
    ai: AIMessage = await model_with_tools.ainvoke(msgs + [HumanMessage(content=prompt)])
    return {"messages_mcp": msgs + [HumanMessage(content=prompt), ai]}

async def collect_tool_results(state: NewsletterState) -> NewsletterState:
    """
    Collect ToolNode outputs into raw text for newsletter generation.
    """
    msgs = state.get("messages_mcp", [])

    raw_chunks = []
    for m in msgs:
        if isinstance(m, ToolMessage):
            if isinstance(m.content, str):
                chunk = m.content
            else:
                chunk = str(m.content)
            chunk = (chunk or "").strip()
            if chunk:
                raw_chunks.append(chunk)

    raw_results = "\n\n".join(raw_chunks).strip()
    if not raw_results:
        raw_results = state.get("raw_results", "")

    return {"raw_results": raw_results}

async def generate_newsletter(state: NewsletterState) -> NewsletterState:
    """
    Produce ~300 words newsletter from tool output (or fallback to last AI content).
    """
    topic = state["topic"]
    raw = (state.get("raw_results") or "").strip()
    if not raw:
        # Fallback: use last AI content from the search node
        ai_contents = [m.content for m in state.get("messages_mcp", []) if isinstance(m, AIMessage)]
        raw = (ai_contents[-1] if ai_contents else "").strip()

    prompt = (
        "You are a succinct newsletter writer.\n"
        f"Topic: {topic}\n"
        "Using ONLY the material below (do not invent links, names, or numbers), "
        "write a clean, single-voice newsletter (~300 words). Include:\n"
        "- a clear headline (H1 markdown)\n"
        "- a short lead (1–2 sentences)\n"
        "- 2–3 compact paragraphs weaving the key points\n"
        "- a 'Further reading' list with the exact URLs you were given (omit if none)\n"
        "Material:\n"
        "-----\n"
        f"{raw}\n"
        "-----\n"
        "Constraints: factual, readable, neutral."
    )
    final_ai: AIMessage = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"newsletter": final_ai.content.strip()}

# =========================
# 4) Router
# =========================
def route_after_research(state: NewsletterState):
    """
    After research_node, if the last AI message has tool_calls -> 'execute_tools'
    otherwise go straight to 'generate_newsletter'.
    """
    msgs = state.get("messages_mcp", [])
    ai = msgs[-1] if msgs else None
    if isinstance(ai, AIMessage) and getattr(ai, "tool_calls", None):
        return "execute_tools"
    return "generate_newsletter"

# =========================
# 5) Build Graph
# =========================
async def build_graph():
    await initialize_components()

    g = StateGraph(NewsletterState)
    g.add_node("research", research_node)
    g.add_node("execute_tools", tool_node)
    g.add_node("collect_tool_results", collect_tool_results)
    g.add_node("generate_newsletter", generate_newsletter)

    g.add_edge(START, "research")
    g.add_conditional_edges(
        "research",
        route_after_research,
        {
            "execute_tools": "execute_tools",
            "generate_newsletter": "generate_newsletter",
        },
    )
    # Loop back to research after tools have been executed and collected
    g.add_edge("execute_tools", "collect_tool_results")
    g.add_edge("collect_tool_results", "research")
    g.add_edge("generate_newsletter", END)

    graph = g.compile()
    graph.get_graph().draw_mermaid_png(output_file_path="newsletter.png")
    return graph

# =========================
# 6) Main
# =========================
async def main():
    topic = "the role of energy models in deep neural networks"  # change as needed
    graph = await build_graph()

    init_state: NewsletterState = {
        "topic": topic,
        "messages_mcp": [],
        "raw_results": "",
        "newsletter": "",
    }
    out: NewsletterState = await graph.ainvoke(init_state)
    print(out["newsletter"])

if __name__ == "__main__":
    asyncio.run(main())
