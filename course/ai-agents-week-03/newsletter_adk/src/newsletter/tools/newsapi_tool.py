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
NewsAPI.org tool (async) — attached directly to newsapi_agent (not via MCP).

ADK can call async Python functions as tools the same way as sync ones.
"""

import os
from typing import Any, Dict

import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def fetch_newsapi_articles(query: str) -> Dict[str, Any]:
    """GET NewsAPI /v2/everything — needs NEWSAPI_API_KEY."""
    api_key = os.getenv("NEWSAPI_API_KEY")
    if not api_key:
        return {"error": "NEWSAPI_API_KEY not set"}

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 8,
        "apiKey": api_key,
    }

    async with aiohttp.ClientSession() as session, session.get(
        "https://newsapi.org/v2/everything", params=params
    ) as resp:
        if resp.status != 200:
            return {"error": f"{resp.status}: {await resp.text()}"}

        data = await resp.json()
        # Normalize fields so all collectors look similar downstream
        articles = [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "date": item.get("publishedAt"),
                "snippet": item.get("description") or "No summary available.",
            }
            for item in data.get("articles", [])
        ]
        return {"articles": articles}
