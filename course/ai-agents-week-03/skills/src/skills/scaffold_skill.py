# =============================================================================
# Filename: scaffold_skill.py
#
# Short Description: CLI to scaffold a new skill folder from the lean-core template.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Scaffold a new skill when a recurring task has no packaged procedure yet.

Typical learning scenario
--------------------
A team notices the agent reinvents the same workflow every sprint (e.g. expense
reports, release checklists). That is instructor theory **Level 0** (ad-hoc).

This CLI promotes the workflow to **Level 1** (authored): a folder with
SKILL.md, changelog, firing-test stub, and manifest entry.

After scaffolding, students should:
1. Replace placeholder firing cases in ``tests/firing_cases.yaml``
2. Replace placeholder validation cases in ``tests/validation_cases.yaml``
2. Flesh out procedure + L3 files
3. Run ``uv run skillcraft-governor``
4. Call ``FilesystemSkillRegistry.refresh()`` or restart the agent
"""

from __future__ import annotations

import argparse
import sys

from loguru import logger

from skills.skill_lifecycle import ScaffoldRequest
from skills.skill_lifecycle import SkillLifecycleError
from skills.skill_lifecycle import remove_skill
from skills.skill_lifecycle import scaffold_skill


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold a new lean-core skill under skills/<name>/. "
            "See skills/_templates/lean-core/SKILL.md.template."
        ),
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Skill id (lowercase-hyphens). Must match folder name.",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Third-person description (initiation set I — most important line).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Human title in SKILL.md body (defaults to title-cased name).",
    )
    parser.add_argument(
        "--trigger",
        default="the user requests this specific workflow",
        help="Literal trigger cues embedded in description.",
    )
    parser.add_argument(
        "--exclude",
        default="unrelated tasks",
        help="Explicit exclusions — prevents god-skill anti-pattern.",
    )
    parser.add_argument(
        "--pattern",
        default="lean-core",
        help="Pattern label recorded in manifest.yaml (for teaching catalog).",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = _parse_args()
    title = args.title or args.name.replace("-", " ").title()
    request = ScaffoldRequest(
        name=args.name,
        description=args.description,
        title=title,
        trigger_cues=args.trigger,
        exclusions=args.exclude,
        pattern=args.pattern,
    )
    try:
        path = scaffold_skill(request=request)
    except SkillLifecycleError as exc:
        logger.error("{}", exc)
        sys.exit(1)
    logger.info("Created skill at {}", path)
    logger.info("Next steps:")
    logger.info("  1. Edit {}/SKILL.md procedure", path)
    logger.info("  2. Replace {}/tests/firing_cases.yaml placeholders", path)
    logger.info("  3. Replace {}/tests/validation_cases.yaml placeholders", path)
    logger.info(
        "  4. uv run skillcraft-governor --test-type firing --skill {}",
        args.name,
    )
    logger.info("  5. uv run skillcraft-demo --list-skills")


def remove_main() -> None:
    """CLI entry point for retiring a skill (inverse of scaffolding).

    Removes the skill folder and its manifest entry, returning the library
    to its prior state — run it at the end of the lifecycle walkthrough so
    scaffold → author → evaluate → retire is idempotent.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Retire a skill: delete skills/<name>/ and its manifest entry.")
    parser.add_argument("--name", required=True, help="Skill folder name to remove")
    args = parser.parse_args()
    try:
        path = remove_skill(name=args.name)
    except SkillLifecycleError as exc:
        logger.error("{}", exc)
        sys.exit(1)
    logger.info("Retired skill '{}' — removed {} and its manifest entry.", args.name, path)
    logger.info("Verify with: uv run skillcraft-demo --list-skills")


if __name__ == "__main__":
    main()
