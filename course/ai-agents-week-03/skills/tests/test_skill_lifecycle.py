# =============================================================================
# Filename: test_skill_lifecycle.py
#
# Short Description: Tests for skill scaffolding and governed procedure deltas.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for skill lifecycle operations."""

from __future__ import annotations

import shutil

import pytest

from skills.paths import skill_dir
from skills.skill_lifecycle import ProcedureDelta
from skills.skill_lifecycle import ScaffoldRequest
from skills.skill_lifecycle import SkillLifecycleError
from skills.skill_lifecycle import TextReplacement
from skills.skill_lifecycle import apply_procedure_delta
from skills.skill_lifecycle import author_skill_procedure
from skills.skill_lifecycle import remove_skill
from skills.skill_lifecycle import scaffold_skill


@pytest.fixture
def temp_skill_name() -> str:
    return "demo-scaffold-test"


def test_scaffold_creates_folder(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    try:
        path = scaffold_skill(
            request=ScaffoldRequest(
                name=temp_skill_name,
                description="Demo skill for unit tests.",
                title="Demo Scaffold",
                trigger_cues="unit test scaffold",
                exclusions="production use",
            )
        )
        assert path.is_dir()
        assert (path / "SKILL.md").is_file()
        assert (path / "tests" / "firing_cases.yaml").is_file()
        assert (path / "tests" / "validation_cases.yaml").is_file()
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_scaffold_rejects_duplicate(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    request = ScaffoldRequest(
        name=temp_skill_name,
        description="Demo.",
        title="Demo",
        trigger_cues="test",
        exclusions="none",
    )
    scaffold_skill(request=request)
    try:
        with pytest.raises(SkillLifecycleError):
            scaffold_skill(request=request)
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_scaffold_rejects_instance_specific_name(temp_skill_name: str) -> None:
    with pytest.raises(SkillLifecycleError, match="instance-specific"):
        scaffold_skill(
            request=ScaffoldRequest(
                name="riemann-zeta-summary",
                description="Summarizes a scientific topic the user names.",
                title="Bad Name",
                trigger_cues="user asks for a summary",
                exclusions="transcripts",
            )
        )


def test_scaffold_rejects_specific_topic_in_description() -> None:
    with pytest.raises(SkillLifecycleError, match="specific topic"):
        scaffold_skill(
            request=ScaffoldRequest(
                name="scientific-topic-summary",
                description="Summarize the Riemann zeta function.",
                title="Bad Description",
                trigger_cues="user asks for a summary",
                exclusions="transcripts",
            )
        )


def test_author_rejects_summary_without_placeholder() -> None:
    skill_name = "topic-workflow-summary"
    target = skill_dir(name=skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=skill_name,
            description="Summarizes a topic the user names.",
            title="Topic Workflow Summary",
            trigger_cues="user asks for a short summary",
            exclusions="production use",
        )
    )
    try:
        with pytest.raises(SkillLifecycleError, match="placeholders"):
            author_skill_procedure(
                skill_name=skill_name,
                procedure="- [ ] Step 1: Write about Riemann zeta only.\n",
                done_when="Done.\n",
            )
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=skill_name)


def test_scaffold_lean_core_has_no_domain_assets(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    try:
        path = scaffold_skill(
            request=ScaffoldRequest(
                name=temp_skill_name,
                description="Summarizes scientific topics.",
                title="Scientific Summary",
                trigger_cues="user asks for a scientific topic summary",
                exclusions="transcript cleaning or code review",
            )
        )
        skill_md = (path / "SKILL.md").read_text(encoding="utf-8")
        assert "Step 1:" in skill_md
        assert not (path / "references" / "output-format.md").exists()
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_author_skill_procedure_replaces_sections(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=temp_skill_name,
            description="Demo skill for author tests.",
            title="Author Demo",
            trigger_cues="unit test author",
            exclusions="production use",
        )
    )
    procedure = (
        "Copy this checklist into your reply and tick each item as you go:\n\n"
        "- [ ] Step 1: Confirm topic.\n"
        "- [ ] Step 2: Write title and body.\n"
    )
    done_when = "User receives title, body, and references.\n"
    try:
        result = author_skill_procedure(
            skill_name=temp_skill_name,
            procedure=procedure,
            done_when=done_when,
        )
        assert result.accepted
        updated = (target / "SKILL.md").read_text(encoding="utf-8")
        assert "Confirm topic." in updated
        assert "User receives title, body, and references." in updated
        assert "Demo skill for author tests." in updated
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_author_rejects_already_authored_skill(temp_skill_name: str) -> None:
    """author_skill_procedure fills a scaffold once; later edits need deltas."""
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=temp_skill_name,
            description="Demo skill for author guard tests.",
            title="Author Guard Demo",
            trigger_cues="unit test author guard",
            exclusions="production use",
        )
    )
    try:
        first = author_skill_procedure(
            skill_name=temp_skill_name,
            procedure="- [ ] Step 1: Write title and body.\n",
            done_when="User receives a title and body.\n",
        )
        assert first.accepted
        before = (target / "SKILL.md").read_text(encoding="utf-8")
        with pytest.raises(SkillLifecycleError, match="apply_procedure_delta"):
            author_skill_procedure(
                skill_name=temp_skill_name,
                procedure="- [ ] Step 1: Something else entirely.\n",
                done_when="Anything.\n",
            )
        assert (target / "SKILL.md").read_text(encoding="utf-8") == before
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_author_rejects_shipped_skill() -> None:
    """A shipped skill (no template placeholder) cannot be rewritten wholesale."""
    path = skill_dir(name="transcript-cleaner") / "SKILL.md"
    before = path.read_text(encoding="utf-8")
    with pytest.raises(SkillLifecycleError, match="already has an authored"):
        author_skill_procedure(
            skill_name="transcript-cleaner",
            procedure="- [ ] Step 1: Replace everything.\n",
            done_when="Done.\n",
        )
    assert path.read_text(encoding="utf-8") == before


def test_apply_delta_rejects_bad_procedure() -> None:
    skill = skill_dir(name="transcript-cleaner")
    original = (skill / "SKILL.md").read_text(encoding="utf-8")
    result = apply_procedure_delta(
        skill_name="transcript-cleaner",
        delta=ProcedureDelta(
            procedure_replacements=(
                TextReplacement(
                    old_text="Load `references/glossary.md` for recurring jargon before editing.",
                    new_text="Skip glossary loading.",
                ),
            ),
        ),
        changelog_note="test bad procedure delta",
        min_validation_accuracy=1.0,
    )
    assert not result.accepted
    assert result.validation_accuracy < result.baseline_validation_accuracy
    restored = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert restored == original


def test_apply_delta_accepts_incremental_append(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=temp_skill_name,
            description="Demo skill for delta tests.",
            title="Delta Demo",
            trigger_cues="unit test delta",
            exclusions="production use",
        )
    )
    try:
        result = apply_procedure_delta(
            skill_name=temp_skill_name,
            delta=ProcedureDelta(
                append_procedure_lines=("- [ ] Step 4: Confirm output formatting.",),
            ),
            changelog_note="Add formatting checklist step",
        )
        assert result.accepted
        updated = (target / "SKILL.md").read_text(encoding="utf-8")
        assert "Confirm output formatting." in updated
        assert "Demo skill for delta tests." in updated
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_apply_delta_removes_procedure_line(temp_skill_name: str) -> None:
    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=temp_skill_name,
            description="Demo skill for line removal.",
            title="Remove Demo",
            trigger_cues="unit test remove",
            exclusions="production use",
        )
    )
    extra_line = "- [ ] Step 4: Optional formatting check."
    try:
        apply_procedure_delta(
            skill_name=temp_skill_name,
            delta=ProcedureDelta(append_procedure_lines=(extra_line,)),
            changelog_note="Add optional step",
        )
        result = apply_procedure_delta(
            skill_name=temp_skill_name,
            delta=ProcedureDelta(remove_procedure_lines=(extra_line,)),
            changelog_note="Remove optional step",
        )
        assert result.accepted
        updated = (target / "SKILL.md").read_text(encoding="utf-8")
        assert extra_line not in updated
    finally:
        if target.exists():
            shutil.rmtree(target)
        _remove_manifest_entry(name=temp_skill_name)


def test_apply_delta_rejects_empty_delta() -> None:
    with pytest.raises(SkillLifecycleError, match="at least one operation"):
        apply_procedure_delta(
            skill_name="transcript-cleaner",
            delta=ProcedureDelta(),
            changelog_note="empty delta",
        )


def test_apply_delta_rejects_missing_anchor() -> None:
    with pytest.raises(SkillLifecycleError, match="exactly one occurrence"):
        apply_procedure_delta(
            skill_name="transcript-cleaner",
            delta=ProcedureDelta(
                procedure_replacements=(
                    TextReplacement(
                        old_text="THIS TEXT DOES NOT EXIST",
                        new_text="replacement",
                    ),
                ),
            ),
            changelog_note="missing anchor",
        )


def _remove_manifest_entry(*, name: str) -> None:
    import yaml

    from skills.paths import manifest_path

    path = manifest_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["skills"] = [row for row in data.get("skills", []) if row.get("name") != name]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_remove_skill_round_trips_scaffold(temp_skill_name: str) -> None:
    """scaffold → remove leaves no folder and no manifest entry (idempotent demo)."""
    import yaml

    from skills.paths import manifest_path

    target = skill_dir(name=temp_skill_name)
    if target.exists():
        shutil.rmtree(target)
    scaffold_skill(
        request=ScaffoldRequest(
            name=temp_skill_name,
            description="Demo skill for unit tests.",
            title="Demo Scaffold",
            trigger_cues="unit test scaffold",
            exclusions="production use",
        )
    )
    removed_path = remove_skill(name=temp_skill_name)
    assert removed_path == target
    assert not target.exists()
    manifest = yaml.safe_load(manifest_path().read_text(encoding="utf-8"))
    assert all(row["name"] != temp_skill_name for row in manifest["skills"])


def test_remove_missing_skill_raises() -> None:
    with pytest.raises(SkillLifecycleError):
        remove_skill(name="never-existed-skill")
