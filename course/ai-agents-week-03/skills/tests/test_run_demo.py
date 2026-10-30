# =============================================================================
# Filename: test_run_demo.py
#
# Short Description: Tests for skillcraft-demo CLI tracing helpers.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for preload vs lazy demo logging helpers."""

from __future__ import annotations

from skills.run_demo import _format_tool_call
from skills.run_demo import _tool_call_hint


def test_format_tool_call_search_skills() -> None:
    line = _format_tool_call(
        tool_name="search_skills",
        args={"query": "clean transcript"},
    )
    assert line == "search_skills(query='clean transcript')"


def test_format_tool_call_load_skill() -> None:
    line = _format_tool_call(
        tool_name="load_skill",
        args={"skill_name": "transcript-cleaner"},
    )
    assert "transcript-cleaner" in line


def test_tool_call_hint_preload_vs_lazy() -> None:
    args = {"skill_name": "transcript-cleaner"}
    preload_hint = _tool_call_hint(tool_name="load_skill", lazy=False, args=args)
    lazy_hint = _tool_call_hint(tool_name="load_skill", lazy=True, args=args)

    assert "preloaded at startup" in preload_hint
    assert "on-demand" in lazy_hint


def test_tool_call_hint_list_skills_differs_by_mode() -> None:
    preload_hint = _tool_call_hint(tool_name="list_skills", lazy=False, args={})
    lazy_hint = _tool_call_hint(tool_name="list_skills", lazy=True, args={})

    assert "startup-preloaded" in preload_hint
    assert "empty" in lazy_hint
