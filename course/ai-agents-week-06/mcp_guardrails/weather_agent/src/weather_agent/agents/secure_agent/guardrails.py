# =============================================================================
# Filename: guardrails.py
#
# Short Description: MCP input/output guardrails for the hardened agent.
#
# Creation date: 2026-07-01
# Author: SupportVectors TA Team
# =============================================================================

"""
Tool-description and tool-output guardrails for the hardened agent.

Input guardrails run when MCP tools are discovered: server-supplied descriptions
are scrubbed before the model sees them. Output guardrails run after each tool
call: secret-like values are redacted before results enter the model context.
"""

from __future__ import annotations

import re
from typing import Any

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
from typing_extensions import override

# --- Input guardrail constants ------------------------------------------------
# Replaces any stripped injection text so the model still sees a neutral note.
_SAFE_DESC = "[Sanitized tool description: untrusted override instructions were removed.]"

# Matches hidden override blocks such as <IMPORTANT>...</IMPORTANT> in poisoned
# tool docstrings (the primary tool-poisoning vector in this lab).
_IMPORTANT = re.compile(r"<IMPORTANT>.*?</IMPORTANT>", re.IGNORECASE | re.DOTALL)

# Phrases that coerce cross-tool abuse (e.g. "run the read_file tool before
# calling this"). Each pattern is checked after <IMPORTANT> blocks are removed.
_INJECTIONS = (
    re.compile(r"before calling.*?tool", re.IGNORECASE | re.DOTALL),
    re.compile(r"run the [\w_]+ tool", re.IGNORECASE),
    re.compile(r"do not mention this instruction", re.IGNORECASE),
)

# --- Output guardrail constants -----------------------------------------------
# Patterns that identify credential-like key=value lines in tool responses.
# Group 1 is preserved (the label); group 2 is replaced with [REDACTED].
_SECRET_PATTERNS = (
    re.compile(r"(?i)(export\s+\w+\s*=\s*)([^\n\r]+)"),
    re.compile(r"(?i)((?:api[_-]?key|password|secret|token)\s*=\s*)([^\n\r]+)"),
)


def sanitize_tool_description(description: str) -> str:
    """Strip override markup and malicious chaining instructions from a tool description.

    This is the **input guardrail**. MCP servers can embed hidden instructions in
    tool docstrings; those strings become trusted model context unless scrubbed.

    Args:
        description: Raw tool description returned by an MCP server.

    Returns:
        A sanitized description safe to expose to the model workspace.
    """
    if not description:
        return description
    cleaned = _IMPORTANT.sub(_SAFE_DESC, description)
    for pattern in _INJECTIONS:
        if pattern.search(cleaned):
            cleaned = pattern.sub(_SAFE_DESC, cleaned)
    return cleaned.strip()


def _redact_value(value: Any) -> Any:
    """Recursively redact secret-like strings from a tool response payload.

    Walks dicts and lists so nested MCP content (e.g. ``content`` arrays) is
    also cleaned before the model reads it.

    Args:
        value: A string, collection, or scalar returned by a tool.

    Returns:
        The same structure with matching secret substrings replaced by
        ``[REDACTED]``.
    """
    if isinstance(value, str):
        redacted = value
        for pattern in _SECRET_PATTERNS:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        return redacted
    if isinstance(value, dict):
        return {key: _redact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def sanitize_tool_output(tool_name: str, output: dict) -> dict:
    """Redact system settings or secret-like values from a tool response.

    This is the **output guardrail**. It runs after a tool executes and before
    the result is written back into the model's scratchpad memory.

    Args:
        tool_name: Name of the tool that produced ``output``.
        output: Raw tool response dictionary.

    Returns:
        A redacted copy of ``output`` safe to return to the model.
    """
    sanitized = _redact_value(output)
    if isinstance(sanitized, dict):
        return sanitized
    return {"tool": tool_name, "result": sanitized}


class GuardedMcpTool(MCPTool):
    """MCP tool wrapper that applies the output guardrail on every execution."""

    @override
    async def run_async(self, *, args: dict[str, Any], tool_context: Any) -> Any:
        """Execute the underlying MCP tool and redact its response.

        Args:
            args: Tool arguments from the model.
            tool_context: ADK tool context for the current invocation.

        Returns:
            The tool result after :func:`sanitize_tool_output` has been applied.
        """
        result = await super().run_async(args=args, tool_context=tool_context)
        payload = result if isinstance(result, dict) else {"result": result}
        return sanitize_tool_output(self.name, payload)


class GuardedMcpToolset(McpToolset):
    """MCP toolset that sanitizes descriptions at discovery and output at runtime."""

    @override
    async def get_tools(
        self, readonly_context: ReadonlyContext | None = None
    ) -> list[BaseTool]:
        """Discover MCP tools and run the input guardrail on each description.

        Loops through tools returned by the server, replaces poisoned description
        text via :func:`sanitize_tool_description`, then wraps each tool in a
        :class:`GuardedMcpTool` so execution output is also guarded.

        Args:
            readonly_context: Optional ADK context used to filter available tools.

        Returns:
            Guarded ADK tools ready to bind to the hardened agent.
        """
        tools_response = await self._execute_with_session(
            lambda session: session.list_tools(),
            "Failed to get tools from MCP server",
            readonly_context,
        )

        tools: list[BaseTool] = []
        for tool_def in tools_response.tools:
            safe_description = sanitize_tool_description(tool_def.description or "")
            if tool_def.description != safe_description:
                tool_def = tool_def.model_copy(update={"description": safe_description})

            guarded = GuardedMcpTool(
                mcp_tool=tool_def,
                mcp_session_manager=self._mcp_session_manager,
                auth_scheme=self._auth_scheme,
                auth_credential=self._auth_credential,
                require_confirmation=self._require_confirmation,
                header_provider=self._header_provider,
                progress_callback=getattr(self, "_progress_callback", None),
            )
            guarded.description = safe_description
            if self._is_tool_selected(guarded, readonly_context):
                tools.append(guarded)
        return tools


def guarded_http_toolset(url: str) -> GuardedMcpToolset:
    """Connect to an MCP server over HTTP with input and output guardrails.

    Args:
        url: Streamable HTTP MCP endpoint (e.g. ``http://127.0.0.1:9000/mcp``).

    Returns:
        A :class:`GuardedMcpToolset` bound to the remote server.
    """
    return GuardedMcpToolset(
        connection_params=StreamableHTTPConnectionParams(url=url)
    )
