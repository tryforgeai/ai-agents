# =============================================================================
# Filename: test_governance.py
#
# Short Description: Tests for firing, validation, and governor gate.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for skill governance."""

from __future__ import annotations

from skills.governance.evaluator import evaluate_firing
from skills.governance.evaluator import evaluate_library
from skills.governance.evaluator import evaluate_validation
from skills.governance.evaluator import evaluate_validation_library
from skills.governance.governor import run_governor
from skills.skill_loader import snapshot_library


def test_transcript_cleaner_firing_passes() -> None:
    report = evaluate_firing(skill_name="transcript-cleaner")
    assert report.total >= 2
    assert report.accuracy >= 0.75


def test_transcript_cleaner_validation_passes() -> None:
    report = evaluate_validation(skill_name="transcript-cleaner")
    assert report.total >= 3
    assert report.accuracy == 1.0


def test_library_firing_governor_passes() -> None:
    code = run_governor(skill=None, min_accuracy=0.75, test_type="firing")
    assert code == 0


def test_library_validation_governor_passes() -> None:
    code = run_governor(skill=None, min_accuracy=1.0, test_type="validation")
    assert code == 0


def test_evaluate_library_covers_manifest() -> None:
    """Every skill in the manifest gets exactly one report from each gate."""
    manifest_names = {entry.name for entry in snapshot_library().entries}
    firing_reports = evaluate_library()
    validation_reports = evaluate_validation_library()
    assert {r.skill_name for r in firing_reports} == manifest_names
    assert {r.skill_name for r in validation_reports} == manifest_names
