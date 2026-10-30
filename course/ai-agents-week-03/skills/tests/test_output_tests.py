# =============================================================================
# Filename: test_output_tests.py
#
# Short Description: Tests for script and behaviour (input → output) tests and
#                    the optional behaviour gate on procedure deltas.
#
# Creation date: 2026-10-07
# Author: SupportVectors AI Training Team
# =============================================================================
"""Script tests run for real; behaviour tests use a fake runner (no LLM)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from skills.governance.governor import run_governor
from skills.governance.output_tests import build_skill_prompt
from skills.governance.output_tests import evaluate_behaviour
from skills.governance.output_tests import evaluate_scripts
from skills.paths import manifest_path
from skills.paths import skill_dir
from skills.skill_lifecycle import ProcedureDelta
from skills.skill_lifecycle import apply_procedure_delta

_GOOD_TRANSCRIPT_REPLY = (
    "Today we look at how GRPO updates the logits of an LLM during training. "
    "Attention Is All You Need showed that you don't need recurrence at all."
)
_BAD_TRANSCRIPT_REPLY = (
    "So, today we look at how group O updates the logic of an L L M, you know."
)
_LITERAL_STEP = (
    "- [ ] Step 5: Leave technical terms exactly as spoken, so the speaker's "
    "words are preserved."
)


def _fake_runner(skill_name: str, user_input: str) -> str:
    """Stand-in for the LLM: obeys the procedure currently on disk.

    If the procedure says to keep terms "exactly as spoken", it leaves the
    mangled jargon in place, as a model following that step would.
    """
    del user_input
    body = (skill_dir(name=skill_name) / "SKILL.md").read_text(encoding="utf-8")
    return _BAD_TRANSCRIPT_REPLY if "exactly as spoken" in body else _GOOD_TRANSCRIPT_REPLY


@pytest.fixture
def restore_transcript_cleaner() -> Iterator[None]:
    paths: list[Path] = [
        manifest_path(),
        skill_dir(name="transcript-cleaner") / "SKILL.md",
        skill_dir(name="transcript-cleaner") / "CHANGELOG.md",
    ]
    saved = {path: path.read_bytes() for path in paths}
    yield
    for path, content in saved.items():
        path.write_bytes(content)


def test_transcript_cleaner_scripts_pass() -> None:
    report = evaluate_scripts(skill_name="transcript-cleaner")
    assert report.total == 6
    assert report.accuracy == 1.0, report.failures


def test_quarterly_report_scripts_pass() -> None:
    report = evaluate_scripts(skill_name="quarterly-report")
    assert report.total == 4
    assert report.accuracy == 1.0, report.failures


def test_script_case_failure_is_reported() -> None:
    from skills.governance.output_tests import run_script_case

    problems = run_script_case(
        skill_name="transcript-cleaner",
        case={
            "script": "scripts/normalize.py",
            "args": ["um hello"],
            "expect_stdout": "goodbye",
        },
    )
    assert problems == ["stdout 'hello', expected 'goodbye'"]


def test_behaviour_checks_pass_on_good_reply() -> None:
    report = evaluate_behaviour(
        skill_name="transcript-cleaner",
        runner=lambda _name, _input: _GOOD_TRANSCRIPT_REPLY,
    )
    assert report.total == 2
    assert report.accuracy == 1.0


def test_behaviour_checks_fail_on_bad_reply() -> None:
    report = evaluate_behaviour(
        skill_name="transcript-cleaner",
        runner=lambda _name, _input: _BAD_TRANSCRIPT_REPLY,
    )
    assert report.accuracy == 0.0
    assert any("missing 'GRPO'" in failure for failure in report.failures)
    assert any("forbidden 'group O'" in failure for failure in report.failures)


def test_skill_prompt_inlines_l3_files() -> None:
    prompt = build_skill_prompt(skill_name="transcript-cleaner")
    assert "## Procedure" in prompt
    assert "# references/glossary.md" in prompt
    assert "| group O | GRPO |" in prompt


def test_delta_passing_validation_but_breaking_behaviour(
    restore_transcript_cleaner: None,
) -> None:
    """The delta keeps every validation rule, so only the behaviour gate stops it."""
    skill_md = skill_dir(name="transcript-cleaner") / "SKILL.md"
    before = skill_md.read_text(encoding="utf-8")

    gated = apply_procedure_delta(
        skill_name="transcript-cleaner",
        delta=ProcedureDelta(append_procedure_lines=(_LITERAL_STEP,)),
        changelog_note="Follow-up: keep the speaker's exact words",
        run_behaviour=True,
        behaviour_runner=_fake_runner,
    )
    assert not gated.accepted
    assert gated.validation_accuracy == 1.0
    assert "behaviour accuracy 0%" in gated.message
    assert skill_md.read_text(encoding="utf-8") == before

    ungated = apply_procedure_delta(
        skill_name="transcript-cleaner",
        delta=ProcedureDelta(append_procedure_lines=(_LITERAL_STEP,)),
        changelog_note="Follow-up: keep the speaker's exact words",
    )
    assert ungated.accepted
    assert "exactly as spoken" in skill_md.read_text(encoding="utf-8")


def test_governor_all_skips_behaviour_unless_asked() -> None:
    with patch(
        "skills.governance.governor.evaluate_behaviour_library",
        side_effect=AssertionError("behaviour tests must not run"),
    ):
        code = run_governor(skill=None, min_accuracy=0.75, test_type="all")
    assert code == 0
