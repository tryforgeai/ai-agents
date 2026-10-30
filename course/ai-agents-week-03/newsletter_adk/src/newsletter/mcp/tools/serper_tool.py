#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""Serper Google News helper (sync). Called from the MCP ``serper_search`` tool."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_serper_news(query: str) -> dict:
    """POST https://google.serper.dev/news — needs SERPER_API_KEY."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY environment variable is not set"}

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": 8}

    try:
        response = requests.post(
            "https://google.serper.dev/news",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(fetch_serper_news("AI news"))
