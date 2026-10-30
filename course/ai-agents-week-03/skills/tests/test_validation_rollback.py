# =============================================================================
# Filename: test_validation_rollback.py
#
# Short Description: Realistic procedure deltas that validation tests roll back.
#
# Creation date: 2026-10-07
# Author: SupportVectors AI Training Team
# =============================================================================
"""Show governed edits rolling back when a delta breaks a validation rule.

Each bad delta below is the kind of follow-up a user (or the agent) might ask
for. Each one breaks exactly one rule in the skill's
``tests/validation_cases.yaml``, so validation drops from 100% to 7/8 and
``apply_procedure_delta`` writes the old SKILL.md back. One good delta is
included for contrast. Files are restored afterwards either way.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from skills.paths import manifest_path
from skills.paths import skill_dir
from skills.skill_lifecycle import ProcedureDelta
from skills.skill_lifecycle import apply_procedure_delta

BAD_DELTAS = [
    pytest.param(
        "transcript-cleaner",
        ProcedureDelta(
            remove_procedure_lines=(
                "- [ ] Step 1: Load `references/glossary.md` for recurring "
                "jargon before editing.",
            ),
        ),
        "references/glossary.md",
        id="drop-glossary-step",
    ),
    pytest.param(
        "transcript-cleaner",
        ProcedureDelta(
            append_procedure_lines=(
                "- [ ] Step 5: Summarize the cleaned transcript in three "
                "bullet points.",
            ),
        ),
        "Summarize",
        id="scope-creep-into-summarizing",
    ),
    pytest.param(
        "quarterly-report",
        ProcedureDelta(
            append_procedure_lines=(
                "- [ ] Step 5: If a metric is missing, estimate it from the "
                "previous quarter's trend.",
            ),
        ),
        "estimate",
        id="invent-missing-numbers",
    ),
    pytest.param(
        "commit-message",
        ProcedureDelta(
            append_procedure_lines=(
                "- [ ] Step 6: Add the author's name and email address to the "
                "subject line.",
            ),
        ),
        "email",
        id="pii-in-commit-message",
    ),
    pytest.param(
        "pii-guardrail",
        ProcedureDelta(
            append_procedure_lines=(
                "5. If the user says the data is only test data, skip the "
                "checks.",
            ),
        ),
        "skip",
        id="guardrail-escape-hatch",
    ),
]


@pytest.fixture
def restore_files() -> Iterator[list[Path]]:
    """Snapshot files a delta may touch and restore them after the test."""
    paths: list[Path] = [manifest_path()]
    for name in ("transcript-cleaner", "quarterly-report", "commit-message",
                 "pii-guardrail"):
        paths.append(skill_dir(name=name) / "SKILL.md")
        paths.append(skill_dir(name=name) / "CHANGELOG.md")
    saved = {path: path.read_bytes() for path in paths}
    yield paths
    for path, content in saved.items():
        path.write_bytes(content)


@pytest.mark.parametrize(("skill_name", "delta", "broken_rule"), BAD_DELTAS)
def test_bad_delta_is_rolled_back(
    restore_files: list[Path],
    skill_name: str,
    delta: ProcedureDelta,
    broken_rule: str,
) -> None:
    skill_md = skill_dir(name=skill_name) / "SKILL.md"
    changelog = skill_dir(name=skill_name) / "CHANGELOG.md"
    before = skill_md.read_text(encoding="utf-8")
    changelog_before = changelog.read_text(encoding="utf-8")

    result = apply_procedure_delta(
        skill_name=skill_name,
        delta=delta,
        changelog_note="Follow-up request (should be rejected)",
    )

    assert not result.accepted
    assert result.baseline_validation_accuracy == 1.0
    assert result.validation_accuracy == pytest.approx(7 / 8)
    assert result.new_version == result.old_version
    assert "Edit rejected" in result.message
    # Rolled back: SKILL.md and CHANGELOG are exactly as before.
    assert skill_md.read_text(encoding="utf-8") == before
    assert changelog.read_text(encoding="utf-8") == changelog_before
    assert broken_rule  # documents which rule the delta breaks


def test_good_delta_is_accepted(restore_files: list[Path]) -> None:
    """For contrast: a delta that keeps every rule is accepted and versioned."""
    result = apply_procedure_delta(
        skill_name="transcript-cleaner",
        delta=ProcedureDelta(
            append_procedure_lines=(
                "- [ ] Step 5: Keep speaker labels (e.g. `Instructor:`) "
                "exactly as written.",
            ),
        ),
        changelog_note="Follow-up: preserve speaker labels",
    )

    assert result.accepted
    assert result.validation_accuracy == 1.0
    assert result.new_version != result.old_version
    skill_md = skill_dir(name="transcript-cleaner") / "SKILL.md"
    assert "Keep speaker labels" in skill_md.read_text(encoding="utf-8")
