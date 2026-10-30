# =============================================================================
# Filename: shared.py
#
# Short Description: Shared LiteLLM model config and ADK MCP helpers for agents.
#
# Creation date: 2026-07-01
# Author: SupportVectors TA Team
# =============================================================================

"""Shared configuration and helpers for lab agents."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.genai import types

API_BASE_URL = "http://10.0.10.70:8000/v1"
MODEL_NAME = "openai/openai/gpt-oss-20b"

SHADOW_URL = "http://127.0.0.1:9000/mcp"
FS_URL = "http://127.0.0.1:9001/mcp"

INSTRUCTION = (
    "You are a helpful travel assistant. "
    "Always fulfill the user's queries using your tools."
)

_USER_ID = "local-user"
_SESSION_ID = "lab-session"


def lite_llm_model() -> LiteLlm:
    """Return the shared LiteLLM model connector."""
    return LiteLlm(model=MODEL_NAME, api_base=API_BASE_URL, api_key="xo")


def http_toolset(url: str) -> McpToolset:
    """Connect to an MCP server over streamable HTTP."""
    return McpToolset(connection_params=StreamableHTTPConnectionParams(url=url))


async def run_query(agent: LlmAgent, app_name: str, query: str) -> list[dict]:
    """Run one query and return tool calls as ``{"tool": ..., "args": ...}``."""
    session_service = InMemorySessionService()
    runner = Runner(app_name=app_name, agent=agent, session_service=session_service)
    await session_service.create_session(
        app_name=app_name, user_id=_USER_ID, session_id=_SESSION_ID
    )

    message = types.Content(role="user", parts=[types.Part(text=query)])
    tool_calls: list[dict] = []
    try:
        async for event in runner.run_async(
            user_id=_USER_ID, session_id=_SESSION_ID, new_message=message
        ):
            for call in event.get_function_calls():
                tool_calls.append({"tool": call.name, "args": dict(call.args or {})})
    finally:
        await runner.close()
    return tool_calls
