# -------------------------------------------------------------------------------------------
#  Copyright (c) 2024.  SupportVectors AI Lab
#
#  This code is part of the training material, and therefore part of the intellectual property.
#  It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#  Use is limited to the duration and purpose of the training at SupportVectors.
#
#  Author: SupportVectors AI Training
# -------------------------------------------------------------------------------------------

"""
This builds an MCP server using the FastMCP library.

The server exposes two tools:
- addition: Add two integers.
- serper_search: Fetch recent search results using the Serper API.

The LangGraph client connects to this server at http://127.0.0.1:9000/mcp using
streamable HTTP via langchain-mcp-adapters.

For more details, refer to the FastMCP documentation: https://gofastmcp.com/clients/client
"""

from fastmcp import FastMCP
from tools.serper_tool import fetch_serper_news
from tools.add_tool import add

mcp = FastMCP(name="newsapi mcp server")

@mcp.tool()
def addition(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The sum of a and b.
    """
    return add(a, b)

@mcp.tool
def serper_search(query: str) -> str:
    """
    Fetch recent news articles using the Serper API for a given query.

    Args:
        query: Search query or topic to fetch news for.

    Returns:
        News articles as a string.
    """
    return fetch_serper_news(query)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=9000)