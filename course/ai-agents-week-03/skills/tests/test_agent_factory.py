# =============================================================================
# Filename: test_agent_factory.py
#
# Short Description: Tests for preload vs lazy skill-loading agents.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for agent factory loading strategies."""

from __future__ import annotations

import re
from unittest.mock import patch

from skills.agent_factory import build_agent
from skills.agent_factory import build_app
from skills.agent_factory import build_skill_toolset

# ADK inject_session_state treats {identifier} as required session keys.
_ADK_STATE_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


@patch("skills.agent_factory.load_all_skills")
def test_preload_toolset_loads_every_skill(mock_load_all) -> None:
    mock_load_all.return_value = []

    toolset = build_skill_toolset(preload=True)

    mock_load_all.assert_called_once()
    assert toolset._registry is not None


@patch("skills.agent_factory.load_all_skills")
def test_lazy_toolset_skips_preload(mock_load_all) -> None:
    toolset = build_skill_toolset(preload=False)

    mock_load_all.assert_not_called()
    assert toolset._registry is not None
    assert toolset.skills == []


def test_lazy_toolset_requires_registry() -> None:
    try:
        build_skill_toolset(preload=False, use_registry=False)
    except ValueError as exc:
        assert "registry" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for lazy without registry")


def test_build_agent_names_reflect_strategy() -> None:
    preload_agent = build_agent(preload=True)
    lazy_agent = build_agent(preload=False)

    assert preload_agent.name == "skillcraft_agent_preload"
    assert lazy_agent.name == "skillcraft_agent_lazy"
    assert "preload" in preload_agent.instruction.lower()
    assert "lazy" in lazy_agent.instruction.lower()


def test_agent_instruction_avoids_adk_session_placeholders() -> None:
    """Brace placeholders must not appear in instructions (ADK session inject)."""
    for preload in (True, False):
        instruction = build_agent(preload=preload).instruction
        match = _ADK_STATE_PLACEHOLDER.search(instruction)
        assert match is None, f"ADK would require session key {match.group()!r}"
        assert "infer" in instruction.lower()


def test_build_agent_includes_lifecycle_tools() -> None:
    agent = build_agent(preload=False)
    tool_names = {tool.name for tool in agent.tools if hasattr(tool, "name")}
    assert "scaffold_new_skill" in tool_names
    assert "author_skill_procedure" in tool_names
    assert "apply_skill_procedure_delta" in tool_names
    assert "refresh_skill_library" in tool_names


def test_build_agent_sanitizes_tool_names_after_model() -> None:
    agent = build_agent(preload=False)
    callback = agent.after_model_callback
    assert callable(callback)
    context, response = object(), object()
    with patch("skills.agent_factory.sanitize_tool_names_after_model") as sanitize:
        sanitize.return_value = None
        assert callback(context, response) is None
        sanitize.assert_called_once_with(
            callback_context=context, llm_response=response
        )


def test_build_app_includes_reflect_and_retry_plugin() -> None:
    app = build_app(preload=False)
    assert app.name == "lazy"
    assert app.root_agent.name == "skillcraft_agent_lazy"
    assert len(app.plugins) == 1
    assert app.plugins[0].__class__.__name__ == "ReflectAndRetryToolPlugin"


def test_build_app_name_matches_agents_folder() -> None:
    assert build_app(preload=True).name == "preload"
    assert build_app(preload=False).name == "lazy"
    assert build_app(preload=False, name="custom").name == "custom"
