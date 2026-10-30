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
NewsData.io tool (async) — attached directly to newsdata_agent (not via MCP).
"""

import os
from typing import Any, Dict

import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def fetch_newsdata_articles(query: str) -> Dict[str, Any]:
    """GET NewsData /api/1/news — needs NEWSDATA_API_KEY."""
    api_key = os.getenv("NEWSDATA_API_KEY")
    if not api_key:
        return {"error": "NEWSDATA_API_KEY not set"}

    params = {
        "apikey": api_key,
        "q": query,
        "language": "en",
        "size": 8,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://newsdata.io/api/1/news", params=params
        ) as resp:
            if resp.status != 200:
                return {"error": f"{resp.status}: {await resp.text()}"}

            data = await resp.json()
            if data.get("status") != "success":
                return {"error": data.get("message", "Unknown error from NewsData.io")}

            # Map NewsData field names → shared article shape
            articles = [
                {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "date": item.get("pubDate"),
                    "snippet": item.get("description") or "No summary available.",
                }
                for item in data.get("results", [])
            ]
            return {"articles": articles}
