#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""MediaStack news search helper (sync). Called from MCP ``mediastack_search``."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_mediastack_articles(query: str):
    """GET MediaStack /v1/news — needs MEDIASTACK_API_KEY."""
    api_key = os.getenv("MEDIASTACK_API_KEY")
    if not api_key:
        return {"error": "MEDIASTACK_API_KEY not set"}

    params = {
        "access_key": api_key,
        "keywords": query,
        "languages": "en",
        "limit": 8,
        "sort": "published_desc",
    }

    try:
        response = requests.get(
            "http://api.mediastack.com/v1/news",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(fetch_mediastack_articles("Artificial Intelligence"))
