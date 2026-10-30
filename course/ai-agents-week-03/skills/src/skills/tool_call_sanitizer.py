# =============================================================================
# Filename: tool_call_sanitizer.py
#
# Short Description: Strip Harmony / gpt-oss channel tokens from tool call names.
#
# Creation date: 2026-07-10
# Author: SupportVectors AI Training Team
# =============================================================================
"""Sanitize malformed tool names emitted by Harmony-style models.

Models such as ``gpt-oss`` may append control tokens to function names, e.g.
``refresh_skill_library<|channel|>commentary``. ADK looks up tools by exact
name, so those calls fail even when the intended tool is registered.

Attach ``sanitize_tool_names_after_model`` as an ``after_model_callback`` so
names are repaired before tool dispatch — no user retry required.
"""

from __future__ import annotations

import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from loguru import logger

# Harmony / special-token spans: <|channel|>, <|message|>, <|call|>, etc.
_HARMONY_TOKEN = re.compile(r"<\|[^|>]+?\|>")


def sanitize_tool_name(*, name: str) -> str:
    """Return ``name`` with trailing Harmony control tokens removed.

    Args:
        name: Raw function-call name from the model.

    Returns:
        Cleaned tool name. If cleaning would yield an empty string, returns
        the original ``name`` unchanged.
    """
    if not name or "<|" not in name:
        return name

    cleaned = _HARMONY_TOKEN.split(name, maxsplit=1)[0].strip()
    if not cleaned:
        return name
    return cleaned


def sanitize_tool_names_after_model(
    *,
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """``after_model_callback`` that repairs Harmony-polluted tool names in place.

    Args:
        callback_context: ADK callback context (unused; required by ADK).
        llm_response: Model response that may contain function calls.

    Returns:
        Always ``None`` so ADK keeps the (possibly mutated) response object.
    """
    del callback_context  # Required by ADK callback signature.
    content = llm_response.content
    if content is None or not content.parts:
        return None

    for part in content.parts:
        function_call = part.function_call
        if function_call is None or not function_call.name:
            continue
        original = function_call.name
        cleaned = sanitize_tool_name(name=original)
        if cleaned == original:
            continue
        logger.warning(
            "Sanitized tool name {!r} → {!r} (Harmony token leakage)",
            original,
            cleaned,
        )
        function_call.name = cleaned

    return None
