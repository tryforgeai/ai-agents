# =============================================================================
# Filename: test_skill_loader.py
#
# Short Description: Tests for skill discovery and loading.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for the on-disk skill library loader.

These tests run **without an LLM** — use them to verify skill folder structure
before running ``skillcraft-demo``. They teach:

- ``snapshot_library()`` joins manifest (curation) with disk scan (reality)
- ADK requires folder name == frontmatter ``name``
- L3 resources land in ``references/``, ``assets/``, ``scripts/`` per ADK spec
"""

from __future__ import annotations

from skills.skill_loader import load_all_skills
from skills.skill_loader import load_skill
from skills.skill_loader import snapshot_library


def test_snapshot_matches_manifest() -> None:
    """Disk scan should find every skill the manifest lists (and no templates)."""
    snap = snapshot_library()
    manifest_names = {entry.name for entry in snap.entries}
    assert manifest_names <= set(snap.discovered)
    assert len(snap.entries) >= 5  # library only grows
    assert "_templates" not in snap.discovered


def test_load_transcript_cleaner_has_resources() -> None:
    """Exemplar skill bundles L3 glossary (references) and script."""
    skill = load_skill(name="transcript-cleaner")
    assert skill.frontmatter.name == "transcript-cleaner"
    assert "glossary.md" in skill.resources.references
    assert "normalize.py" in skill.resources.scripts


def test_load_all_skills_non_empty() -> None:
    """Preload path used by the preload agent should return the curated library."""
    skills = load_all_skills()
    names = {s.frontmatter.name for s in skills}
    assert "transcript-cleaner" in names
    assert "pii-guardrail" in names
