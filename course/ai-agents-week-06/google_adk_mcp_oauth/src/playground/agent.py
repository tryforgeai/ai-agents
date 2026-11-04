"""Playground agent that invokes OAuth-protected MCP tools via Google ADK.

This module provides an interactive agent built with Google ADK (Agent Development Kit)
that connects to an MCP (Model Context Protocol) server with OAuth2 authentication.
The agent can call protected tools like purchase_item, view_my_orders, and refund_purchase through FastMCP.
"""

import asyncio
import os
from dotenv import load_dotenv

import httpx

from fastmcp import Client as McpClient
from fastmcp.client.auth import OAuth as McpOAuth

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "adk_mcp_app")
USER_ID = os.getenv("USER_ID", "user1")
SESSION_ID = os.getenv("SESSION_ID", "session1")

MCP_URL = os.getenv("MCP_URL", "http://localhost:8026/mcp")

# -----------------------------------------------------------------------------
# FastMCP OAuth helper
# -----------------------------------------------------------------------------
# Scopes come from the server's 401 WWW-Authenticate challenge. The MCP client
# uses that scope list, then protected-resource metadata, during authorization.
mcp_oauth = McpOAuth(
    mcp_url=MCP_URL,
    
)

def _calltool_result_to_json(result):
    """Extract JSON data from an MCP CallToolResult.

    Searches result content for json or text parts and returns parsed JSON.
    Returns None if no parseable JSON is found.

    Args:
        result: MCP CallToolResult object with a content attribute.

    Returns:
        Parsed JSON dict/list, or None.
    """
    for c in getattr(result, "content", []) or []:
        if getattr(c, "type", None) == "json":
            return getattr(c, "data", None)
        if getattr(c, "type", None) == "text":
            import json
            try:
                return json.loads(getattr(c, "text", ""))
            except Exception:
                pass
    return None

async def _mcp_call(tool_name: str, args: dict | None = None) -> dict:
    """Call an MCP tool via OAuth-authenticated FastMCP client.

    Args:
        tool_name: Name of the MCP tool to invoke.
        args: Optional dict of arguments to pass to the tool.

    Returns:
        Dict with tool result. Wraps non-dict results in {"result": ...}.
    """
    async with McpClient(MCP_URL, auth=mcp_oauth) as c:
        res = await c.call_tool(tool_name, args or {})
        data = _calltool_result_to_json(res)
        return data if isinstance(data, dict) else {"result": data}

# -----------------------------------------------------------------------------
# Public HTTP tool (no OAuth)
# -----------------------------------------------------------------------------

async def http_list_products() -> dict:
    """
    Call public HTTP endpoint /products.
    """
    base_url = MCP_URL.replace("/mcp", "")
    url = f"{base_url}/products"

    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=5)
        r.raise_for_status()
        return r.json()

# -----------------------------------------------------------------------------
# ADK tools (functions become tools)
# -----------------------------------------------------------------------------


async def mcp_purchase_item(item_id: str) -> dict:
    """Call protected MCP tool purchase_item."""
    return await _mcp_call("purchase_item", {"item_id": item_id})


async def mcp_view_my_orders() -> dict:
    """Call protected MCP tool view_my_orders."""
    return await _mcp_call("view_my_orders")


async def mcp_refund_purchase(transaction_id: str) -> dict:
    """Call protected MCP tool refund_purchase."""
    return await _mcp_call("refund_purchase", {"transaction_id": transaction_id})


# -----------------------------------------------------------------------------
# Agent + Runner
# -----------------------------------------------------------------------------
agent = LlmAgent(
    name="mcp_store_agent",
    model=LiteLlm(model="openai/openai/gpt-oss-20b", api_base="http://10.0.10.70:8000/v1",api_key="dummy"),
    tools=[
        http_list_products,      # public HTTP
        mcp_purchase_item,       # protected MCP
        mcp_view_my_orders,      # protected MCP
        mcp_refund_purchase,     # protected MCP
    ],
    instruction=(
        "You are a storefront assistant connected to an OAuth-protected backend.\n"
        "If user wants to see available products, call http_list_products.\n"
        "If user wants to buy something, call mcp_purchase_item with item_id.\n"
        "If user wants to see their purchases, call mcp_view_my_orders.\n"
        "If user wants to refund a purchase, call mcp_refund_purchase with transaction_id.\n"
        "Otherwise respond normally."
    ),
)



session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

def _content_from_text(text: str) -> types.Content:
    """Build a user Content message for the ADK runner.

    Args:
        text: Raw user input string.

    Returns:
        types.Content instance with role="user" and a single text part.
    """
    return types.Content(role="user", parts=[types.Part(text=text)])

async def run_turn(user_text: str) -> str:
    """Run one ADK conversation turn and return the assistant's reply.

    Consumes the async generator from the runner until the final response event,
    then extracts the assistant text.

    Args:
        user_text: The user's input message.

    Returns:
        The assistant's final text reply, or "(no response)" if empty.
    """
    final_text = ""

    # ADK runner is async generator; consume events until final response
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=_content_from_text(user_text),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = getattr(event.content.parts[0], "text", "") or ""

    return final_text or "(no response)"

async def main():
    """Interactive REPL for the MCP OAuth agent.

    Creates a session, then loops reading user input and printing agent replies.
    Exits on 'exit' or 'quit'.
    """
    # IMPORTANT: create the session *before* the first run
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print(f"ADK agent ready. MCP_URL={MCP_URL}")
    print("Try: 'list products', 'buy p1', 'view my orders', or 'refund <transaction_id>'. Type 'exit' to quit.\n")

    while True:
        user_text = input("> ").strip()
        if user_text.lower() in {"exit", "quit"}:
            break

        try:
            reply = await run_turn(user_text)
            print(reply)
            print()
        except Exception as e:
            print(f"[error] {type(e).__name__}: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
