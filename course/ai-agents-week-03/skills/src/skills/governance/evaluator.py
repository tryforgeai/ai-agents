# =============================================================================
# Filename: evaluator.py
#
# Short Description: Firing-test evaluator for skill descriptions (instructor theory).
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Evaluate skill descriptions (firing) and procedures (validation).

Learning overview
--------------------
Instructor theory separates two test types:

**Firing tests** (``firing_cases.yaml``) — test initiation set **I** (description).
Do prompts trigger the right skill? Catches silent skills (too few fires) and
overlap / god-skills (too many fires). Does *not* judge procedure quality.

**Validation tests** (``validation_cases.yaml``) — test policy **π** (procedure).
Does SKILL.md body include required sections, checklists, and references?
``apply_procedure_delta`` accepts an edit only when validation score does not
regress and meets the minimum threshold.

**Production vs classroom:** firing uses sentence-transformer cosine similarity
(same as ``FilesystemSkillRegistry.search_skills``) with a keyword-overlap
fallback when embeddings score below threshold.
"""

from __future__ import annotations

from dataclasses import dataclass

import yaml

from skills.paths import skill_dir
from skills.semantic_search import matches_skill_description
from skills.semantic_search import resolve_semantic_search_settings
from skills.skill_loader import load_skill


@dataclass(frozen=True)
class FiringCase:
    """One positive or negative firing test.

    ``should_fire=True``  → prompt must match description (recall).
    ``should_fire=False`` → prompt must NOT match (precision).
    """

    prompt: str
    should_fire: bool


@dataclass(frozen=True)
class FiringReport:
    """Aggregate firing-test results for a skill."""

    skill_name: str
    total: int
    correct: int
    accuracy: float
    failures: tuple[str, ...]


def _load_cases(*, skill_name: str) -> list[FiringCase]:
    """Read ``skills/<name>/tests/firing_cases.yaml``."""
    path = skill_dir(name=skill_name) / "tests" / "firing_cases.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [
        FiringCase(
            prompt=str(row["prompt"]),
            should_fire=bool(row["should_fire"]),
        )
        for row in data.get("cases", [])
    ]


def _would_fire(*, skill_name: str, description: str, prompt: str) -> bool:
    """Hybrid matcher: semantic similarity with keyword fallback.

    Uses cosine similarity on ``"{skill_name} {description}"`` (same as
    ``search_skills``). When the score is below threshold, token overlap and
    domain cues provide a secondary signal. Exclusion zones are checked both
    semantically and by keyword stems.
    """
    settings = resolve_semantic_search_settings()
    return matches_skill_description(
        skill_name=skill_name,
        description=description,
        prompt=prompt,
        model_name=settings.model_name,
        similarity_threshold=settings.similarity_threshold,
    )


@dataclass(frozen=True)
class ValidationCase:
    """One structural check against the procedure body (SKILL.md markdown)."""

    must_contain: str | None = None
    must_not_contain: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    """Aggregate validation-test results for a skill procedure."""

    skill_name: str
    total: int
    correct: int
    accuracy: float
    failures: tuple[str, ...]


def _load_validation_cases(*, skill_name: str) -> list[ValidationCase]:
    """Read ``skills/<name>/tests/validation_cases.yaml``."""
    path = skill_dir(name=skill_name) / "tests" / "validation_cases.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases: list[ValidationCase] = []
    for row in data.get("cases", []):
        cases.append(
            ValidationCase(
                must_contain=(
                    str(row["must_contain"]) if row.get("must_contain") else None
                ),
                must_not_contain=(
                    str(row["must_not_contain"])
                    if row.get("must_not_contain")
                    else None
                ),
            )
        )
    return cases


def _passes_validation_case(*, instructions: str, case: ValidationCase) -> bool:
    """Return whether the procedure body satisfies one validation case."""
    if case.must_contain is not None and case.must_contain not in instructions:
        return False
    if case.must_not_contain is not None and case.must_not_contain in instructions:
        return False
    return True


def evaluate_validation(*, skill_name: str) -> ValidationReport:
    """Run validation cases against the current procedure body.

    Args:
        skill_name: Skill to evaluate.

    Returns:
        ``ValidationReport`` with accuracy and failure messages.
    """
    cases = _load_validation_cases(skill_name=skill_name)
    if not cases:
        return ValidationReport(
            skill_name=skill_name,
            total=0,
            correct=0,
            accuracy=1.0,
            failures=(),
        )

    skill = load_skill(name=skill_name)
    instructions = skill.instructions
    failures: list[str] = []
    correct = 0
    for case in cases:
        if _passes_validation_case(instructions=instructions, case=case):
            correct += 1
            continue
        if case.must_contain is not None:
            failures.append(f"missing required text: {case.must_contain!r}")
        elif case.must_not_contain is not None:
            failures.append(f"forbidden text present: {case.must_not_contain!r}")
    total = len(cases)
    accuracy = correct / total if total else 1.0
    return ValidationReport(
        skill_name=skill_name,
        total=total,
        correct=correct,
        accuracy=accuracy,
        failures=tuple(failures),
    )


def evaluate_validation_library(
    *, names: list[str] | None = None
) -> list[ValidationReport]:
    """Evaluate validation tests for multiple skills.

    Args:
        names: Optional explicit skill list; defaults to manifest skills.

    Returns:
        One report per skill.
    """
    if names is None:
        from skills.skill_loader import load_manifest

        _, _, entries = load_manifest()
        names = [entry.name for entry in entries]
    return [evaluate_validation(skill_name=name) for name in names]


def evaluate_firing(*, skill_name: str) -> FiringReport:
    """Run firing cases for a skill against its current description.

    Firing tests judge initiation set **I** only: should this skill load for
    each prompt? They do not validate procedure quality.

    Args:
        skill_name: Skill to evaluate.

    Returns:
        ``FiringReport`` with accuracy and failure messages.
    """
    cases = _load_cases(skill_name=skill_name)
    if not cases:
        # No tests → pass by default (but teach: empty tests are a smell).
        return FiringReport(
            skill_name=skill_name,
            total=0,
            correct=0,
            accuracy=1.0,
            failures=(),
        )

    skill = load_skill(name=skill_name)
    description = skill.frontmatter.description
    failures: list[str] = []
    correct = 0
    for case in cases:
        predicted = _would_fire(
            skill_name=skill_name,
            description=description,
            prompt=case.prompt,
        )
        if predicted == case.should_fire:
            correct += 1
        else:
            failures.append(
                f"prompt={case.prompt!r} expected={case.should_fire} got={predicted}"
            )
    total = len(cases)
    accuracy = correct / total if total else 1.0
    return FiringReport(
        skill_name=skill_name,
        total=total,
        correct=correct,
        accuracy=accuracy,
        failures=tuple(failures),
    )


def evaluate_library(*, names: list[str] | None = None) -> list[FiringReport]:
    """Evaluate firing tests for multiple skills.

    Args:
        names: Optional explicit skill list; defaults to manifest skills.

    Returns:
        One report per skill.
    """
    if names is None:
        from skills.skill_loader import load_manifest

        _, _, entries = load_manifest()
        names = [entry.name for entry in entries]
    return [evaluate_firing(skill_name=name) for name in names]
