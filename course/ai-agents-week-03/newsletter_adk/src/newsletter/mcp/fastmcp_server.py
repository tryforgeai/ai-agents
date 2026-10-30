#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
FastMCP tool server for this project.

Agents connect with McpToolset → http://127.0.0.1:9000/mcp
Each ``@mcp.tool()`` function becomes a callable tool for LlmAgents.

Start with: uv run src/newsletter/mcp/fastmcp_server.py
"""

from typing import Any

from fastmcp import FastMCP

from newsletter.mcp.tools.mediastack_tool import fetch_mediastack_articles
from newsletter.mcp.tools.serper_tool import fetch_serper_news
from newsletter.settings import MCP_HOST, MCP_PORT

mcp = FastMCP(name="newsletter-mcp-server")


@mcp.tool()
def serper_search(query: str) -> dict[str, Any]:
    """Google News via Serper — used by serper_agent in the collector."""
    return fetch_serper_news(query)


@mcp.tool()
def mediastack_search(query: str) -> dict[str, Any]:
    """News search via MediaStack — used by mediastack_agent."""
    return fetch_mediastack_articles(query)


def main():
    """HTTP MCP server (defaults to 127.0.0.1:9000; see settings.py)."""
    mcp.run(transport="http", host=MCP_HOST, port=MCP_PORT)


if __name__ == "__main__":
    main()
