# =============================================================================
# Filename: test_lifecycle_tools.py
#
# Short Description: Tests for runtime skill lifecycle ADK tools.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for lifecycle FunctionTools."""

from __future__ import annotations

import shutil

from skills.filesystem_registry import FilesystemSkillRegistry
from skills.lifecycle_tools import build_skill_lifecycle_tools
from skills.paths import skill_dir


def _tool_by_name(*, tools: list, name: str):
    for tool in tools:
        # agent.tools also holds the SkillToolset, which has no ``name``.
        if getattr(tool, "name", None) == name:
            return tool
    raise AssertionError(f"Tool {name!r} not found")


def test_scaffold_new_skill_tool_creates_folder() -> None:
    skill_name = "lifecycle-tool-test"
    target = skill_dir(name=skill_name)
    if target.exists():
        shutil.rmtree(target)
    registry = FilesystemSkillRegistry()
    tools = build_skill_lifecycle_tools(registry=registry, toolset=None)
    scaffold_tool = _tool_by_name(tools=tools, name="scaffold_new_skill")
    try:
        result = scaffold_tool.func(
            name=skill_name,
            description="Summarizes topics for tool tests.",
            title="Tool Test Summary",
            trigger_cues="lifecycle tool test",
            exclusions="production",
        )
        assert result["status"] == "ok"
        assert target.is_dir()
        assert (target / "SKILL.md").is_file()
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=skill_name)


def test_refresh_skill_library_picks_up_new_skill() -> None:
    skill_name = "lifecycle-refresh-test"
    target = skill_dir(name=skill_name)
    if target.exists():
        shutil.rmtree(target)
    registry = FilesystemSkillRegistry()
    tools = build_skill_lifecycle_tools(registry=registry, toolset=None)
    scaffold_tool = _tool_by_name(tools=tools, name="scaffold_new_skill")
    refresh_tool = _tool_by_name(tools=tools, name="refresh_skill_library")
    try:
        scaffold_tool.func(
            name=skill_name,
            description="Refresh test skill.",
            title="Refresh Test",
            trigger_cues="refresh test",
            exclusions="none",
        )
        before = set(registry._frontmatters.keys())
        assert skill_name not in before
        result = refresh_tool.func()
        assert result["status"] == "ok"
        assert skill_name in result["skills"]
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=skill_name)


def test_apply_skill_procedure_delta_tool_appends_lines() -> None:
    skill_name = "lifecycle-delta-test"
    target = skill_dir(name=skill_name)
    if target.exists():
        shutil.rmtree(target)
    registry = FilesystemSkillRegistry()
    tools = build_skill_lifecycle_tools(registry=registry, toolset=None)
    scaffold_tool = _tool_by_name(tools=tools, name="scaffold_new_skill")
    author_tool = _tool_by_name(tools=tools, name="author_skill_procedure")
    delta_tool = _tool_by_name(tools=tools, name="apply_skill_procedure_delta")
    try:
        scaffold_tool.func(
            name=skill_name,
            description="Summary skill for delta tool test.",
            title="Delta Tool Test",
            trigger_cues="delta tool test",
            exclusions="none",
        )
        author_tool.func(
            skill_name=skill_name,
            procedure=(
                "Copy this checklist into your reply and tick each item:\n\n"
                "- [ ] Step 1: Write title and body.\n"
            ),
            done_when="User receives a title and body.\n",
        )
        ref_line = "- [ ] Step 2: List 3-4 references for further reading."
        result = delta_tool.func(
            skill_name=skill_name,
            changelog_note="User requested references in follow-up",
            append_procedure_lines=[ref_line],
            append_done_when_lines=[
                "Output includes 3-4 authoritative references.",
            ],
        )
        assert result["status"] == "ok"
        updated = (target / "SKILL.md").read_text(encoding="utf-8")
        assert ref_line in updated
        assert "3-4 authoritative references" in updated
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=skill_name)


def test_lazy_agent_refresh_keeps_memory_empty() -> None:
    """A lazy agent's refresh must not copy the library into memory.

    Otherwise ADK's search_skills filters out every skill (name conflict) and
    load_skill serves stale copies instead of reading from disk.
    """
    from google.adk.tools.skill_toolset import SkillToolset

    from skills.agent_factory import build_agent

    agent = build_agent(preload=False)
    toolset = next(tool for tool in agent.tools if isinstance(tool, SkillToolset))
    refresh_tool = _tool_by_name(tools=agent.tools, name="refresh_skill_library")

    result = refresh_tool.func()

    assert result["status"] == "ok"
    assert result["skill_count"] > 0
    assert result["newly_preloaded"] == []
    assert toolset._skills == {}


def test_preload_toolset_sees_edits_without_restart() -> None:
    """Deltas and refreshes replace the preload agent's in-memory copy."""
    from google.adk.tools.skill_toolset import SkillToolset

    skill_name = "lifecycle-reload-test"
    target = skill_dir(name=skill_name)
    if target.exists():
        shutil.rmtree(target)
    registry = FilesystemSkillRegistry()
    toolset = SkillToolset(skills=[], registry=registry)
    tools = build_skill_lifecycle_tools(registry=registry, toolset=toolset)
    scaffold_tool = _tool_by_name(tools=tools, name="scaffold_new_skill")
    author_tool = _tool_by_name(tools=tools, name="author_skill_procedure")
    delta_tool = _tool_by_name(tools=tools, name="apply_skill_procedure_delta")
    refresh_tool = _tool_by_name(tools=tools, name="refresh_skill_library")
    try:
        scaffold_tool.func(
            name=skill_name,
            description="Reload test skill.",
            title="Reload Test",
            trigger_cues="reload test",
            exclusions="unrelated tasks",
        )
        author_tool.func(
            skill_name=skill_name,
            procedure="- [ ] Step 1: Write title and body.\n",
            done_when="User receives a title and body.\n",
        )
        assert "Step 1: Write title and body." in toolset._skills[
            skill_name
        ].instructions

        new_line = "- [ ] Step 2: Add a short conclusion."
        result = delta_tool.func(
            skill_name=skill_name,
            changelog_note="Follow-up asked for a conclusion",
            append_procedure_lines=[new_line],
        )
        assert result["status"] == "ok"
        assert new_line in toolset._skills[skill_name].instructions

        skill_md = target / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace(
                "Write title and body.", "Write a title and a body."
            ),
            encoding="utf-8",
        )
        refreshed = refresh_tool.func()
        assert skill_name in refreshed["reloaded"]
        assert "Write a title and a body." in toolset._skills[
            skill_name
        ].instructions
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=skill_name)

    removed = refresh_tool.func()
    assert skill_name in removed["removed"]
    assert skill_name not in toolset._skills


def _remove_manifest_entry(*, name: str) -> None:
    import yaml

    from skills.paths import manifest_path

    path = manifest_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["skills"] = [row for row in data.get("skills", []) if row.get("name") != name]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
