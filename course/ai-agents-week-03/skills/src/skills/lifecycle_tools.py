# =============================================================================
# Filename: lifecycle_tools.py
#
# Short Description: ADK tools for scaffolding and authoring skills at runtime.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Function tools that let the agent grow the skill library after novel tasks.

When no packaged skill matches, the agent can:

1. Complete the task from general knowledge.
2. Call ``scaffold_new_skill`` to create a folder + manifest entry.
3. Call ``author_skill_procedure`` to record the workflow that worked.
4. Call ``refresh_skill_library`` so discovery tools see the new skill.

Follow-up turns refine an existing skill via ``apply_skill_procedure_delta``.
"""

from __future__ import annotations

import os
from typing import Any

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.skill_toolset import SkillToolset
from loguru import logger

from skills.filesystem_registry import FilesystemSkillRegistry
from skills.skill_lifecycle import ProcedureDelta
from skills.skill_lifecycle import ScaffoldRequest
from skills.skill_lifecycle import SkillLifecycleError
from skills.skill_lifecycle import apply_procedure_delta
from skills.skill_lifecycle import author_skill_procedure as commit_skill_procedure
from skills.skill_lifecycle import scaffold_skill
from skills.skill_loader import load_skill


def _behaviour_gate_enabled() -> bool:
    """Whether agent edits are also gated on behaviour tests (LLM calls).

    Off by default. Set ``SKILL_GOVERN_WITH_BEHAVIOUR=1`` to turn it on.
    """
    return os.getenv("SKILL_GOVERN_WITH_BEHAVIOUR", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def build_skill_lifecycle_tools(
    *,
    registry: FilesystemSkillRegistry | None,
    toolset: SkillToolset | None = None,
) -> list[FunctionTool]:
    """Create lifecycle tools wired to the agent's registry and toolset.

    Args:
        registry: Filesystem registry shared with ``SkillToolset`` (may be None).
        toolset: The **preload** agent's ``SkillToolset``, kept in sync with
            disk after scaffolding, authoring, deltas and refreshes. Pass None
            for a lazy agent: it reads skills from disk through the registry
            on every ``load_skill``, so it needs no in-memory copy.

    Returns:
        List of ``FunctionTool`` instances for the agent.
    """

    def _reload_into_toolset(skill_name: str) -> None:
        """Preload agents only: replace the in-memory copy of an edited skill.

        ADK's ``load_skill`` serves skills held in ``toolset._skills`` before it
        asks the registry, so without this a preload agent would keep following
        the old procedure until restart.
        """
        if toolset is None:
            return
        try:
            toolset._skills[skill_name] = load_skill(name=skill_name)
        except Exception as exc:
            logger.warning("Could not reload skill {}: {}", skill_name, exc)

    def scaffold_new_skill(
        *,
        name: str,
        description: str,
        title: str,
        trigger_cues: str,
        exclusions: str,
        pattern: str = "lean-core",
    ) -> dict[str, Any]:
        """Create a new skill folder under skills/<name>/ from the lean-core template.

        Call this after completing a novel task when no existing skill matched.
        Search for the task *type* first — do not scaffold one skill per input.

        Name workflows, not instances: ``scientific-topic-summary`` not
        ``riemann-zeta-summary``. Use ``{topic}`` (or similar) in the procedure
        via ``author_skill_procedure``.

        Args:
            name: Workflow id (category + task), e.g. scientific-topic-summary.
            description: Third-person description of the reusable task pattern.
            title: Human-readable title in SKILL.md.
            trigger_cues: General when-to-use cues (no specific topic names).
            exclusions: Tasks this skill must NOT handle.
            pattern: Template pattern (default ``lean-core`` only).

        Returns:
            Status dict with ``path`` on success or ``error`` on failure.
        """
        if pattern != "lean-core":
            return {
                "status": "error",
                "message": (
                    f"Unknown pattern {pattern!r}. Use lean-core; refine the "
                    "skill later with apply_skill_procedure_delta."
                ),
            }
        request = ScaffoldRequest(
            name=name,
            description=description,
            title=title,
            trigger_cues=trigger_cues,
            exclusions=exclusions,
            pattern=pattern,
        )
        try:
            path = scaffold_skill(request=request)
        except SkillLifecycleError as exc:
            return {"status": "error", "message": str(exc)}
        logger.info("Agent scaffolded skill at {}", path)
        return {
            "status": "ok",
            "path": str(path),
            "message": (
                "Skill folder created. Call author_skill_procedure next, then "
                "refresh_skill_library."
            ),
        }

    def author_skill_procedure(
        *,
        skill_name: str,
        procedure: str,
        done_when: str,
        changelog_note: str = "Authored procedure from first successful execution.",
    ) -> dict[str, Any]:
        """Replace the Procedure and Done when sections in an existing skill.

        Use only right after scaffold_new_skill, to capture the checklist
        workflow that succeeded on the first novel task. It is rejected for a
        skill whose procedure was already authored: use
        apply_skill_procedure_delta for any later change. For parameterized tasks, use placeholders
        like ``{topic}`` — never hard-code the first example's subject.

        Args:
            skill_name: Target skill folder name.
            procedure: Markdown body for ## Procedure (include ``- [ ]`` steps).
            done_when: Markdown body for ## Done when.
            changelog_note: Short note appended to CHANGELOG.

        Returns:
            Status dict with version and validation scores.
        """
        try:
            result = commit_skill_procedure(
                skill_name=skill_name,
                procedure=procedure,
                done_when=done_when,
                changelog_note=changelog_note,
                run_behaviour=_behaviour_gate_enabled(),
            )
        except SkillLifecycleError as exc:
            return {"status": "error", "message": str(exc)}
        if result.accepted:
            _reload_into_toolset(skill_name)
        payload: dict[str, Any] = {
            "status": "ok" if result.accepted else "rejected",
            "skill_name": result.skill_name,
            "old_version": result.old_version,
            "new_version": result.new_version,
            "validation_accuracy": result.validation_accuracy,
            "message": result.message,
        }
        return payload

    def apply_skill_procedure_delta(
        *,
        skill_name: str,
        changelog_note: str,
        append_procedure_lines: list[str] | None = None,
        append_done_when_lines: list[str] | None = None,
        remove_procedure_lines: list[str] | None = None,
        remove_done_when_lines: list[str] | None = None,
    ) -> dict[str, Any]:
        """Apply incremental procedure changes after a follow-up user request.

        Use when the user refines requirements on a skill you already created
        (e.g. "add references" after an initial summary-only workflow). Runs
        validation tests and rolls back on failure.

        Args:
            skill_name: Target skill folder name.
            changelog_note: Why this delta was applied (e.g. user follow-up).
            append_procedure_lines: New checklist lines to add under Procedure.
            append_done_when_lines: New criteria to add under Done when.
            remove_procedure_lines: Exact procedure lines to remove.
            remove_done_when_lines: Exact done-when lines to remove.

        Returns:
            Status dict with version and validation scores.
        """
        delta = ProcedureDelta(
            append_procedure_lines=tuple(append_procedure_lines or ()),
            append_done_when_lines=tuple(append_done_when_lines or ()),
            remove_procedure_lines=tuple(remove_procedure_lines or ()),
            remove_done_when_lines=tuple(remove_done_when_lines or ()),
        )
        try:
            result = apply_procedure_delta(
                skill_name=skill_name,
                delta=delta,
                changelog_note=changelog_note,
                run_behaviour=_behaviour_gate_enabled(),
            )
        except SkillLifecycleError as exc:
            return {"status": "error", "message": str(exc)}
        if result.accepted:
            _reload_into_toolset(skill_name)
        return {
            "status": "ok" if result.accepted else "rejected",
            "skill_name": result.skill_name,
            "old_version": result.old_version,
            "new_version": result.new_version,
            "validation_accuracy": result.validation_accuracy,
            "message": result.message,
        }

    def refresh_skill_library() -> dict[str, Any]:
        """Rescan the skill library so discovery tools see new or edited skills.

        Call after scaffold_new_skill or manual folder edits. For a preload
        agent, also reloads every skill on disk into its in-memory catalog
        (new, edited and unchanged alike) and drops skills that were retired.
        A lazy agent only rescans: it loads skills from disk when it needs them.
        """
        if registry is None:
            return {
                "status": "error",
                "message": "No skill registry attached to this agent.",
            }

        frontmatters = registry.refresh()
        loaded: list[str] = []
        reloaded: list[str] = []
        removed: list[str] = []
        if toolset is not None:
            for skill_name in frontmatters:
                is_new = skill_name not in toolset._skills
                try:
                    toolset._skills[skill_name] = load_skill(name=skill_name)
                except Exception as exc:
                    logger.warning("Could not load skill {}: {}", skill_name, exc)
                    continue
                (loaded if is_new else reloaded).append(skill_name)
            for skill_name in list(toolset._skills):
                if skill_name not in frontmatters:
                    del toolset._skills[skill_name]
                    removed.append(skill_name)

        return {
            "status": "ok",
            "skill_count": len(frontmatters),
            "skills": sorted(frontmatters.keys()),
            "newly_preloaded": loaded,
            "reloaded": reloaded,
            "removed": removed,
        }

    return [
        FunctionTool(scaffold_new_skill),
        FunctionTool(author_skill_procedure),
        FunctionTool(apply_skill_procedure_delta),
        FunctionTool(refresh_skill_library),
    ]
