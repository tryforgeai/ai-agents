# =============================================================================
# Filename: governor.py
#
# Short Description: CLI gate for firing and validation skill tests.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Governor gate for skill library quality (instructor maturity Level 3).

Two test types
--------------
- **firing** — description / initiation set I: does the skill trigger on the
  right prompts (not too few, not too many)?
- **validation** — procedure / policy π: does SKILL.md include required
  sections, checklists, and references?
- **script** — run bundled scripts on sample inputs and check their output
  (deterministic, no LLM).
- **behaviour** — apply the skill to sample inputs with the LLM and check the
  reply (costs API calls; results can vary between runs).
- **all** — firing + validation + script; add ``--with-behaviour`` to include
  behaviour tests too.

``apply_procedure_delta`` uses validation tests programmatically and rolls back
on failure. Run this CLI before merging description or procedure edits:

    uv run skillcraft-governor --test-type firing --min-accuracy 0.75
    uv run skillcraft-governor --test-type validation
    uv run skillcraft-governor --test-type script
    uv run skillcraft-governor --test-type behaviour --skill transcript-cleaner
    uv run skillcraft-governor --test-type all --with-behaviour
"""

from __future__ import annotations

import argparse
import sys
from typing import Literal

from loguru import logger

from skills.governance.evaluator import evaluate_firing
from skills.governance.evaluator import evaluate_library
from skills.governance.evaluator import evaluate_validation
from skills.governance.evaluator import evaluate_validation_library
from skills.governance.output_tests import evaluate_behaviour
from skills.governance.output_tests import evaluate_behaviour_library
from skills.governance.output_tests import evaluate_scripts
from skills.governance.output_tests import evaluate_scripts_library

TestType = Literal["firing", "validation", "script", "behaviour", "all"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run skill firing or validation tests (governor gate). "
            "See docs/LEARNING_GUIDE.md."
        ),
    )
    parser.add_argument(
        "--skill",
        help="Evaluate a single skill (default: all manifest skills).",
    )
    parser.add_argument(
        "--test-type",
        choices=("firing", "validation", "script", "behaviour", "all"),
        default="firing",
        help=(
            "firing = description triggers; validation = procedure rules; "
            "script = bundled scripts on sample inputs (no LLM); behaviour = "
            "skill applied by the LLM to sample inputs; all = firing + "
            "validation + script (+ behaviour with --with-behaviour)."
        ),
    )
    parser.add_argument(
        "--with-behaviour",
        action="store_true",
        help="With --test-type all, also run the LLM behaviour tests.",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=1.0,
        help="Minimum required accuracy (0.0–1.0). Use 0.75 in class demos.",
    )
    return parser.parse_args()


def _reports_for(*, test_type: str, skill: str | None) -> list:
    """Run one test type for one skill or the whole library."""
    if test_type == "firing":
        return [evaluate_firing(skill_name=skill)] if skill else evaluate_library()
    if test_type == "validation":
        return (
            [evaluate_validation(skill_name=skill)]
            if skill
            else evaluate_validation_library()
        )
    if test_type == "script":
        return [evaluate_scripts(skill_name=skill)] if skill else evaluate_scripts_library()
    if test_type == "behaviour":
        return (
            [evaluate_behaviour(skill_name=skill)]
            if skill
            else evaluate_behaviour_library()
        )
    raise ValueError(f"Unknown test type: {test_type}")


def run_governor(
    *,
    skill: str | None,
    min_accuracy: float,
    test_type: TestType = "firing",
    with_behaviour: bool = False,
) -> int:
    """Execute governor tests and return a process exit code.

    Args:
        skill: Optional single skill name.
        min_accuracy: Fail if any report is below this threshold.
        test_type: ``firing``, ``validation``, ``script``, ``behaviour`` or
            ``all`` (firing + validation + script).
        with_behaviour: With ``all``, also run the LLM behaviour tests.

    Returns:
        0 on success, 1 if any skill fails the gate.
    """
    if test_type == "all":
        types = ["firing", "validation", "script"]
        if with_behaviour:
            types.append("behaviour")
    else:
        types = [test_type]

    failed = False
    for current in types:
        for report in _reports_for(test_type=current, skill=skill):
            status = "PASS" if report.accuracy >= min_accuracy else "FAIL"
            logger.info(
                "{} [{}] {} — {}/{} correct ({:.0%})",
                status,
                current,
                report.skill_name,
                report.correct,
                report.total,
                report.accuracy,
            )
            for failure in report.failures:
                logger.warning("  {}", failure)
            if report.accuracy < min_accuracy:
                failed = True
    return 1 if failed else 0


def main() -> None:
    """CLI entry point."""
    args = _parse_args()
    sys.exit(
        run_governor(
            skill=args.skill,
            min_accuracy=args.min_accuracy,
            test_type=args.test_type,
            with_behaviour=args.with_behaviour,
        )
    )


if __name__ == "__main__":
    main()
