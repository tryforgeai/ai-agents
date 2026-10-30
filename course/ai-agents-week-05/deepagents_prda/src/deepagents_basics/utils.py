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
PRDA Utility Functions

Helper functions for the PRDA agent.
"""

import re


def slugify(name: str) -> str:
    """Turn a product name into a filesystem-friendly slug.

    Args:
        name: The product name to slugify

    Returns:
        A lowercase, underscore-separated slug

    Examples:
        >>> slugify("AI Budgeting Assistant")
        'ai_budgeting_assistant'
        >>> slugify("My Product 2024!")
        'my_product_2024'
    """
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "product"


def message_text(message) -> str:
    """Return a message's content as plain text.

    LangChain message content is either a string or a list of content
    blocks (e.g. with the OpenAI Responses API that gpt-5 models use by
    default): [{"type": "text", "text": "..."}, ...]. The UI and CLI only
    want the text, whichever shape arrives.
    """
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(block["text"])
        return "\n".join(parts)
    return "" if content is None else str(content)
