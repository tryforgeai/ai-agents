# =============================================================================
# Filename: test_tool_call_sanitizer.py
#
# Short Description: Tests for Harmony tool-name sanitization.
#
# Creation date: 2026-07-10
# Author: SupportVectors AI Training Team
# =============================================================================
"""Regression tests for gpt-oss channel-token leakage in tool names."""

from __future__ import annotations

from unittest.mock import MagicMock

from google.adk.models.llm_response import LlmResponse
from google.genai import types

from skills.tool_call_sanitizer import sanitize_tool_name
from skills.tool_call_sanitizer import sanitize_tool_names_after_model


def test_sanitize_strips_channel_commentary_suffix() -> None:
    raw = "refresh_skill_library<|channel|>commentary"
    assert sanitize_tool_name(name=raw) == "refresh_skill_library"


def test_sanitize_leaves_clean_names_unchanged() -> None:
    assert sanitize_tool_name(name="load_skill") == "load_skill"


def test_sanitize_empty_after_tokens_keeps_original() -> None:
    raw = "<|channel|>commentary"
    assert sanitize_tool_name(name=raw) == raw


def test_after_model_callback_mutates_function_call_name() -> None:
    response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        name="refresh_skill_library<|channel|>commentary",
                        args={},
                    )
                )
            ],
        )
    )

    result = sanitize_tool_names_after_model(
        callback_context=MagicMock(),
        llm_response=response,
    )

    assert result is None
    assert response.content is not None
    assert response.content.parts is not None
    assert response.content.parts[0].function_call.name == "refresh_skill_library"
