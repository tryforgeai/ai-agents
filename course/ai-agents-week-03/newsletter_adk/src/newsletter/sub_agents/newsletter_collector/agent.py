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
Parallel news collection (fan-out / fan-in).

Four LlmAgents run at once; each writes its own output_key.
JoinNode waits for all four before the parent Workflow continues.

Tools:
- Serper / MediaStack → via MCP (local FastMCP server, see settings.MCP_SERVER_URL)
- NewsAPI / NewsData → direct Python function tools
"""

from google.adk import Workflow
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.workflow import START, JoinNode

from newsletter.settings import MCP_SERVER_URL, llm
from newsletter.sub_agents.newsletter_collector.prompt import (
    MEDIASTACK_INSTRUCTION,
    NEWSAPI_INSTRUCTION,
    NEWSDATA_INSTRUCTION,
    SERPER_INSTRUCTION,
)
from newsletter.tools.newsapi_tool import fetch_newsapi_articles
from newsletter.tools.newsdata_tool import fetch_newsdata_articles


def get_mcp_toolset(tool_filter: list[str] | None = None) -> McpToolset:
    """Connect to FastMCP; tool_filter limits which remote tools this agent sees."""
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
        tool_filter=tool_filter,
    )


# --- Source agents (each stores results under a different state key) ---------

serper_agent = LlmAgent(
    name="serper_agent",
    model=llm,
    description="Fetches articles using the Serper API for real-time search results.",
    instruction=SERPER_INSTRUCTION,
    tools=[get_mcp_toolset(tool_filter=["serper_search"])],
    output_key="serper_articles",
)

mediastack_agent = LlmAgent(
    name="mediastack_agent",
    model=llm,
    description="Fetches articles using the MediaStack API for media monitoring.",
    instruction=MEDIASTACK_INSTRUCTION,
    tools=[get_mcp_toolset(tool_filter=["mediastack_search"])],
    output_key="mediastack_articles",
)

newsapi_agent = LlmAgent(
    name="newsapi_agent",
    model=llm,
    description="Fetches articles using NewsAPI.org for comprehensive news coverage.",
    instruction=NEWSAPI_INSTRUCTION,
    tools=[fetch_newsapi_articles],  # in-process tool (no MCP)
    output_key="newsapi_articles",
)

newsdata_agent = LlmAgent(
    name="newsdata_agent",
    model=llm,
    description="Fetches articles using NewsData.io for global news aggregation.",
    instruction=NEWSDATA_INSTRUCTION,
    tools=[fetch_newsdata_articles],
    output_key="newsdata_articles",
)

# Nested tuple after START = run these agents in parallel, then join.
collection_join = JoinNode(name="collection_join")

newsletter_collector = Workflow(
    name="newsletter_collector",
    description="Orchestrates parallel execution of news collection agents.",
    edges=[
        (
            START,
            (serper_agent, newsapi_agent, newsdata_agent, mediastack_agent),
            collection_join,
        ),
    ],
)
