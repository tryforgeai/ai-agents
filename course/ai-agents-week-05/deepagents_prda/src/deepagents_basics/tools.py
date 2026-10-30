#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
PRDA Custom Tools

Internet search for market research (Tavily when a key is set; a mock
result otherwise, so the pipeline runs end to end without any search key).
"""

import os
from typing import Literal

from langchain.tools import tool

# ---------------------------------------------------------------------------
# Optional: Tavily integration for internet search
# ---------------------------------------------------------------------------

try:
    from tavily import TavilyClient
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if api_key:
        tavily_client = TavilyClient(api_key=api_key)
    else:
        tavily_client = None
except (ImportError, Exception):
    tavily_client = None


# ---------------------------------------------------------------------------
# Internet Search Tool
# ---------------------------------------------------------------------------

@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> str:
    """Run a web search for product / market / competitor research."""
    if tavily_client is None or not getattr(tavily_client, "api_key", None):
        return (
            f"[MOCK SEARCH RESULT]\n"
            f"Query: {query}\n"
            f"- Result 1: Example competitor A with features.\n"
            f"- Result 2: Example competitor B with pricing.\n"
            f"- Trend: Growing market interest.\n"
        )

    res = tavily_client.search(
        query=query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return str(res)
