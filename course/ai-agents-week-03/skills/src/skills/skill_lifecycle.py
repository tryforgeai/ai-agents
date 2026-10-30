# =============================================================================
# Filename: skill_lifecycle.py
#
# Short Description: Scaffold new skills and apply governed procedure deltas.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Skill library lifecycle: scaffold, edit, version, and manifest updates.

Learning overview
--------------------
Instructor theory describes four verbs for skills: **author, retrieve, compose,
improve**. This module implements the first and last at library scale:

1. **scaffold_skill** — Level 1 maturity ("authored"): turn recurring know-how
   into a folder with SKILL.md, changelog, firing tests, and manifest entry.
2. **apply_procedure_delta** — Level 3 maturity ("governed"): apply incremental
   deltas to π (procedure) and β (done-when) only when validation tests pass
   and the validation score does not regress. Full SKILL.md rewrites are
   intentionally unsupported. Firing tests (description / I) are separate.

The governor pattern from instructor theory prevents "silent skill" and "god skill"
anti-patterns from slipping in via careless edits.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from loguru import logger

from skills.governance.evaluator import evaluate_validation
from skills.governance.output_tests import BehaviourRunner
from skills.governance.output_tests import evaluate_behaviour
from skills.paths import manifest_path
from skills.paths import skill_dir
from skills.paths import template_dir_for_pattern

_PROCEDURE_HEADER = "## Procedure"
# Placeholder step written by the lean-core template. Its presence marks a
# scaffolded skill whose procedure has not been authored yet.
_TEMPLATE_PLACEHOLDER = "<common-path step"
_DONE_WHEN_HEADER = "## Done when"


class SkillLifecycleError(Exception):
    """Raised when a lifecycle operation cannot complete."""


@dataclass(frozen=True)
class ScaffoldRequest:
    """Inputs for creating a new skill folder.

    ``description`` + ``trigger_cues`` + ``exclusions`` become the frontmatter
    description — teach students to craft this line before writing procedure.
    """

    name: str
    description: str
    title: str
    trigger_cues: str
    exclusions: str
    pattern: str = "lean-core"


@dataclass(frozen=True)
class TextReplacement:
    """Replace ``old_text`` with ``new_text`` inside a bounded section."""

    old_text: str
    new_text: str


@dataclass(frozen=True)
class ProcedureDelta:
    """Incremental edits to procedure (π) and done-when (β) sections only.

    Frontmatter and ``## When to use`` are never modified by this type.
    """

    procedure_replacements: tuple[TextReplacement, ...] = ()
    remove_procedure_lines: tuple[str, ...] = ()
    append_procedure_lines: tuple[str, ...] = ()
    done_when_replacements: tuple[TextReplacement, ...] = ()
    remove_done_when_lines: tuple[str, ...] = ()
    append_done_when_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class _SkillMdSections:
    """Parsed SKILL.md body split at procedure boundaries."""

    prefix: str
    procedure: str
    done_when: str


@dataclass(frozen=True)
class EditResult:
    """Outcome of a governed procedure delta."""

    skill_name: str
    old_version: str
    new_version: str
    baseline_validation_accuracy: float
    validation_accuracy: float
    accepted: bool
    applied_deltas: tuple[str, ...]
    message: str


_VERSION_PATTERN = re.compile(
    r'^version:\s*["\']?(?P<ver>[\d.]+)["\']?\s*$',
    flags=re.MULTILINE,
)

_WORKFLOW_SUFFIXES = frozenset(
    {"summary", "cleaner", "report", "message", "guardrail", "formatter"}
)
_GENERIC_CATEGORY_PREFIXES = frozenset(
    {
        "scientific",
        "topic",
        "transcript",
        "commit",
        "quarterly",
        "expense",
        "meeting",
        "research",
        "document",
        "email",
        "code",
        "release",
        "pii",
    }
)
_SPECIFIC_TOPIC_MARKERS = re.compile(
    r"\b(riemann|zeta function|proximal policy|ppo)\b",
    flags=re.IGNORECASE,
)


def _validate_skill_name(*, name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise SkillLifecycleError(
            f"Invalid skill name '{name}': use lowercase letters, digits, hyphens."
        )


def _validate_skill_name_generality(*, name: str) -> None:
    """Reject skill names that bake in one input instance instead of workflow type."""
    parts = name.split("-")
    if len(parts) < 2 or parts[-1] not in _WORKFLOW_SUFFIXES:
        return
    if parts[0] in _GENERIC_CATEGORY_PREFIXES:
        return
    raise SkillLifecycleError(
        f"Skill name '{name}' looks instance-specific (starts with '{parts[0]}'). "
        "Name the workflow, not the input — e.g. 'scientific-topic-summary'. "
        "Take the specific topic from the user message at run time via {topic}."
    )


def _validate_description_generality(*, description: str, trigger_cues: str) -> None:
    """Reject descriptions that name one topic instead of the task pattern."""
    combined = f"{description} {trigger_cues}"
    match = _SPECIFIC_TOPIC_MARKERS.search(combined)
    if match is None:
        return
    raise SkillLifecycleError(
        f"Description/trigger mentions a specific topic ({match.group(0)!r}). "
        "Describe the reusable task (e.g. 'summarize a scientific topic the user "
        "names') — not one instance like Riemann zeta or PPO."
    )


def _validate_parameterized_procedure(
    *,
    skill_name: str,
    procedure: str,
    done_when: str,
) -> None:
    """Require placeholders when authoring summary-style parameterized skills."""
    if not skill_name.endswith("-summary"):
        return
    combined = f"{procedure}\n{done_when}"
    if "{" in combined and "}" in combined:
        return
    raise SkillLifecycleError(
        "Summary skills must use placeholders like {topic} in procedure and "
        "done-when — do not hard-code one subject."
    )


def _render_template(*, request: ScaffoldRequest) -> str:
    """Fill ``SKILL.md.template`` with scaffold parameters."""
    template_path = (
        template_dir_for_pattern(pattern=request.pattern) / "SKILL.md.template"
    )
    if not template_path.is_file():
        raise SkillLifecycleError(f"Template not found: {template_path}")
    text = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{SKILL_NAME}}": request.name,
        "{{SKILL_DESCRIPTION}}": request.description,
        "{{SKILL_TITLE}}": request.title,
        "{{TRIGGER_CUES}}": request.trigger_cues,
        "{{EXCLUSIONS}}": request.exclusions,
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def _default_validation_cases() -> str:
    payload = {
        "cases": [
            {"must_contain": "## Procedure"},
            {"must_contain": "## Done when"},
            {"must_contain": "- [ ]"},
        ]
    }
    return yaml.safe_dump(payload, sort_keys=False)


def _default_firing_cases(*, name: str) -> str:
    payload = {
        "cases": [
            {
                "prompt": f"<prompt that SHOULD fire {name}>",
                "should_fire": True,
            },
            {
                "prompt": f"<related prompt that SHOULD NOT fire {name}>",
                "should_fire": False,
            },
        ]
    }
    return yaml.safe_dump(payload, sort_keys=False)


def _copy_template_assets(*, pattern: str, target: Path) -> None:
    """Copy optional ``references/`` and ``assets/`` from a pattern template."""
    source = template_dir_for_pattern(pattern=pattern)
    for subdir in ("references", "assets"):
        src = source / subdir
        if not src.is_dir():
            continue
        shutil.copytree(src, target / subdir, dirs_exist_ok=True)


def _parse_skill_md(*, text: str) -> _SkillMdSections:
    """Split SKILL.md at ``## Procedure`` and ``## Done when`` headers."""
    procedure_match = re.search(
        rf"^{re.escape(_PROCEDURE_HEADER)}\s*$",
        text,
        flags=re.MULTILINE,
    )
    done_when_match = re.search(
        rf"^{re.escape(_DONE_WHEN_HEADER)}\s*$",
        text,
        flags=re.MULTILINE,
    )
    if procedure_match is None or done_when_match is None:
        raise SkillLifecycleError(
            "SKILL.md must contain ## Procedure and ## Done when sections."
        )
    if procedure_match.start() >= done_when_match.start():
        raise SkillLifecycleError("## Procedure must precede ## Done when.")

    prefix = text[: procedure_match.start()]
    procedure = text[procedure_match.end() : done_when_match.start()]
    done_when = text[done_when_match.end() :]
    return _SkillMdSections(prefix=prefix, procedure=procedure, done_when=done_when)


def _assemble_skill_md(*, sections: _SkillMdSections) -> str:
    """Rebuild SKILL.md from parsed sections."""
    return (
        f"{sections.prefix}{_PROCEDURE_HEADER}\n"
        f"{sections.procedure}"
        f"{_DONE_WHEN_HEADER}\n"
        f"{sections.done_when}"
    )


def _apply_replacements(
    *,
    section: str,
    replacements: tuple[TextReplacement, ...],
    section_name: str,
) -> str:
    """Apply ordered text replacements inside one section."""
    updated = section
    for replacement in replacements:
        count = updated.count(replacement.old_text)
        if count != 1:
            raise SkillLifecycleError(
                f"{section_name}: expected exactly one occurrence of "
                f"{replacement.old_text!r}, found {count}."
            )
        updated = updated.replace(replacement.old_text, replacement.new_text, 1)
    return updated


def _remove_lines(*, section: str, lines: tuple[str, ...], section_name: str) -> str:
    """Remove whole lines that match exactly one line in the section body."""
    if not lines:
        return section
    section_lines = section.splitlines(keepends=True)
    for target in lines:
        target_stripped = target.strip("\n")
        match_indexes = [
            index
            for index, line in enumerate(section_lines)
            if line.rstrip("\n") == target_stripped
        ]
        if len(match_indexes) != 1:
            raise SkillLifecycleError(
                f"{section_name}: expected exactly one line {target_stripped!r}, "
                f"found {len(match_indexes)}."
            )
        section_lines.pop(match_indexes[0])
    return "".join(section_lines)


def _append_lines(*, section: str, lines: tuple[str, ...]) -> str:
    """Append lines to a section body."""
    if not lines:
        return section
    base = section if section.endswith("\n") else f"{section}\n"
    return f"{base}{chr(10).join(lines)}\n"


def _delta_has_operations(*, delta: ProcedureDelta) -> bool:
    return bool(
        delta.procedure_replacements
        or delta.remove_procedure_lines
        or delta.append_procedure_lines
        or delta.done_when_replacements
        or delta.remove_done_when_lines
        or delta.append_done_when_lines
    )


def _describe_delta(*, delta: ProcedureDelta) -> tuple[str, ...]:
    """Human-readable audit lines for CHANGELOG."""
    lines: list[str] = []
    for replacement in delta.procedure_replacements:
        lines.append(
            f"Procedure replace: {replacement.old_text!r} → {replacement.new_text!r}"
        )
    for line in delta.remove_procedure_lines:
        lines.append(f"Procedure remove line: {line!r}")
    for line in delta.append_procedure_lines:
        lines.append(f"Procedure append: {line!r}")
    for replacement in delta.done_when_replacements:
        lines.append(
            f"Done-when replace: {replacement.old_text!r} → {replacement.new_text!r}"
        )
    for line in delta.remove_done_when_lines:
        lines.append(f"Done-when remove line: {line!r}")
    for line in delta.append_done_when_lines:
        lines.append(f"Done-when append: {line!r}")
    return tuple(lines)


def _apply_procedure_delta_to_text(*, text: str, delta: ProcedureDelta) -> str:
    """Apply incremental deltas and return the candidate SKILL.md text."""
    if not _delta_has_operations(delta=delta):
        raise SkillLifecycleError("ProcedureDelta must include at least one operation.")

    sections = _parse_skill_md(text=text)
    procedure = _apply_replacements(
        section=sections.procedure,
        replacements=delta.procedure_replacements,
        section_name="Procedure",
    )
    procedure = _remove_lines(
        section=procedure,
        lines=delta.remove_procedure_lines,
        section_name="Procedure",
    )
    procedure = _append_lines(section=procedure, lines=delta.append_procedure_lines)
    done_when = _apply_replacements(
        section=sections.done_when,
        replacements=delta.done_when_replacements,
        section_name="Done when",
    )
    done_when = _remove_lines(
        section=done_when,
        lines=delta.remove_done_when_lines,
        section_name="Done when",
    )
    done_when = _append_lines(section=done_when, lines=delta.append_done_when_lines)
    return _assemble_skill_md(
        sections=_SkillMdSections(
            prefix=sections.prefix,
            procedure=procedure,
            done_when=done_when,
        )
    )


def scaffold_skill(*, request: ScaffoldRequest) -> Path:
    """Create a new skill folder from the lean-core template."""
    _validate_skill_name(name=request.name)
    _validate_skill_name_generality(name=request.name)
    _validate_description_generality(
        description=request.description,
        trigger_cues=request.trigger_cues,
    )
    target = skill_dir(name=request.name)
    if target.exists():
        raise SkillLifecycleError(f"Skill already exists: {target}")

    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(
        _render_template(request=request),
        encoding="utf-8",
    )
    (target / "CHANGELOG.md").write_text(
        f"# Changelog — {request.name}\n\n"
        f"## 0.1.0 — {date.today().isoformat()}\n\n"
        f"- Scaffolded from lean-core template ({request.pattern}).\n",
        encoding="utf-8",
    )
    tests_dir = target / "tests"
    tests_dir.mkdir()
    (tests_dir / "firing_cases.yaml").write_text(
        _default_firing_cases(name=request.name),
        encoding="utf-8",
    )
    (tests_dir / "validation_cases.yaml").write_text(
        _default_validation_cases(),
        encoding="utf-8",
    )
    for sub in ("references", "assets", "scripts"):
        (target / sub).mkdir(exist_ok=True)
    _copy_template_assets(pattern=request.pattern, target=target)

    _append_manifest_entry(name=request.name, pattern=request.pattern)
    logger.info("Scaffolded skill at {}", target)
    return target


def _append_manifest_entry(*, name: str, pattern: str) -> None:
    """Register new skill in manifest.yaml (status=draft until reviewed)."""
    path = manifest_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {}
    skills = data.get("skills", [])
    if any(row.get("name") == name for row in skills):
        return
    skills.append(
        {
            "name": name,
            "version": "0.1.0",
            "pattern": pattern,
            "status": "draft",
        }
    )
    data["skills"] = skills
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def remove_skill(*, name: str) -> Path:
    """Retire a skill: delete its folder and drop its manifest entry.

    The inverse of ``scaffold_skill`` — the end of the lifecycle that
    scaffolding begins. Intended for retiring skills added during
    experiments or walkthroughs, so the library returns to a known state
    and add→author→evaluate→retire leaves no trace (idempotent demos).

    Raises:
        SkillLifecycleError: if no folder *and* no manifest entry exist
            for ``name`` (nothing to remove).
    """
    _validate_skill_name(name=name)
    target = skill_dir(name=name)
    removed_folder = target.is_dir()
    if removed_folder:
        shutil.rmtree(target)
    removed_entry = _remove_manifest_entry(name=name)
    if not (removed_folder or removed_entry):
        raise SkillLifecycleError(f"No skill named '{name}' to remove.")
    logger.info(
        "Removed skill '{}' (folder deleted: {}, manifest entry dropped: {})",
        name, removed_folder, removed_entry,
    )
    return target


def _remove_manifest_entry(*, name: str) -> bool:
    """Drop ``name`` from manifest.yaml. Returns True if an entry was removed."""
    path = manifest_path()
    if not path.is_file():
        return False
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    skills = data.get("skills", [])
    kept = [row for row in skills if row.get("name") != name]
    if len(kept) == len(skills):
        return False
    data["skills"] = kept
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return True


def _bump_patch_version(*, version: str) -> str:
    """Semantic-ish patch bump for procedure edits (teach versioning early)."""
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return "0.1.1"
    major, minor, patch = (int(p) for p in parts)
    return f"{major}.{minor}.{patch + 1}"


def _commit_governed_skill_md(
    *,
    skill_name: str,
    old_text: str,
    candidate_text: str,
    changelog_lines: tuple[str, ...],
    min_validation_accuracy: float,
    run_behaviour: bool = False,
    min_behaviour_accuracy: float = 1.0,
    behaviour_runner: BehaviourRunner | None = None,
) -> EditResult:
    """Write candidate SKILL.md, validate, and rollback on failure.

    With ``run_behaviour=True`` the skill's behaviour tests (LLM applied to
    sample inputs) are run before and after the edit as a second gate, with
    the same rule: at least ``min_behaviour_accuracy`` and no regression.
    """
    path = skill_dir(name=skill_name) / "SKILL.md"
    baseline_report = evaluate_validation(skill_name=skill_name)
    baseline_score = baseline_report.accuracy
    baseline_behaviour = (
        evaluate_behaviour(skill_name=skill_name, runner=behaviour_runner).accuracy
        if run_behaviour
        else None
    )

    old_match = _VERSION_PATTERN.search(old_text)
    old_version = old_match.group("ver") if old_match else "0.1.0"
    new_version = _bump_patch_version(version=old_version)
    updated = _VERSION_PATTERN.sub(f'version: "{new_version}"', candidate_text, count=1)

    path.write_text(updated, encoding="utf-8")
    try:
        candidate_report = evaluate_validation(skill_name=skill_name)
    except Exception:
        path.write_text(old_text, encoding="utf-8")
        raise
    validation_score = candidate_report.accuracy

    if validation_score < min_validation_accuracy:
        path.write_text(old_text, encoding="utf-8")
        return EditResult(
            skill_name=skill_name,
            old_version=old_version,
            new_version=old_version,
            baseline_validation_accuracy=baseline_score,
            validation_accuracy=validation_score,
            accepted=False,
            applied_deltas=changelog_lines,
            message=(
                f"Edit rejected: validation accuracy {validation_score:.0%} "
                f"< required {min_validation_accuracy:.0%}"
            ),
        )

    if validation_score < baseline_score:
        path.write_text(old_text, encoding="utf-8")
        return EditResult(
            skill_name=skill_name,
            old_version=old_version,
            new_version=old_version,
            baseline_validation_accuracy=baseline_score,
            validation_accuracy=validation_score,
            accepted=False,
            applied_deltas=changelog_lines,
            message=(
                f"Edit rejected: validation accuracy {validation_score:.0%} "
                f"< baseline {baseline_score:.0%}"
            ),
        )

    if run_behaviour:
        try:
            behaviour_score = evaluate_behaviour(
                skill_name=skill_name, runner=behaviour_runner
            ).accuracy
        except Exception:
            path.write_text(old_text, encoding="utf-8")
            raise
        if behaviour_score < min_behaviour_accuracy or (
            baseline_behaviour is not None and behaviour_score < baseline_behaviour
        ):
            path.write_text(old_text, encoding="utf-8")
            return EditResult(
                skill_name=skill_name,
                old_version=old_version,
                new_version=old_version,
                baseline_validation_accuracy=baseline_score,
                validation_accuracy=validation_score,
                accepted=False,
                applied_deltas=changelog_lines,
                message=(
                    f"Edit rejected: behaviour accuracy {behaviour_score:.0%} "
                    f"(baseline {baseline_behaviour:.0%}, required "
                    f"{min_behaviour_accuracy:.0%})"
                ),
            )

    changelog = skill_dir(name=skill_name) / "CHANGELOG.md"
    delta_notes = "\n".join(f"- {line}" for line in changelog_lines)
    note = f"\n## {new_version} — {date.today().isoformat()}\n\n{delta_notes}\n"
    with changelog.open("a", encoding="utf-8") as handle:
        handle.write(note)

    _update_manifest_version(name=skill_name, version=new_version)
    return EditResult(
        skill_name=skill_name,
        old_version=old_version,
        new_version=new_version,
        baseline_validation_accuracy=baseline_score,
        validation_accuracy=validation_score,
        accepted=True,
        applied_deltas=changelog_lines,
        message="Delta accepted and version bumped.",
    )


def author_skill_procedure(
    *,
    skill_name: str,
    procedure: str,
    done_when: str,
    changelog_note: str = "Authored procedure from first successful execution.",
    min_validation_accuracy: float = 1.0,
    run_behaviour: bool = False,
    min_behaviour_accuracy: float = 1.0,
    behaviour_runner: BehaviourRunner | None = None,
) -> EditResult:
    """Replace procedure and done-when sections after a novel task succeeds.

    Use when the agent completes a task without a matching skill, then captures
    the workflow as a reusable procedure. Frontmatter (description / I) is
    preserved — edit descriptions separately with firing tests.

    Only allowed while the procedure is still the scaffold template (it
    contains ``<common-path step``). Once a procedure has been authored, every
    later change must go through ``apply_procedure_delta``, so an existing
    skill can never be rewritten wholesale.

    Args:
        skill_name: Target skill folder name.
        procedure: Markdown body for ``## Procedure`` (include checklist lines).
        done_when: Markdown body for ``## Done when``.
        changelog_note: Summary recorded in CHANGELOG.
        min_validation_accuracy: Minimum validation accuracy to accept the edit.

    Returns:
        ``EditResult`` describing acceptance or rejection.

    Raises:
        SkillLifecycleError: If SKILL.md structure is invalid, or if the
            procedure has already been authored.
    """
    path = skill_dir(name=skill_name) / "SKILL.md"
    if not path.is_file():
        raise SkillLifecycleError(f"SKILL.md not found for {skill_name}")

    if not procedure.strip():
        raise SkillLifecycleError("Procedure body must not be empty.")
    if not done_when.strip():
        raise SkillLifecycleError("Done-when body must not be empty.")

    _validate_parameterized_procedure(
        skill_name=skill_name,
        procedure=procedure,
        done_when=done_when,
    )

    old_text = path.read_text(encoding="utf-8")
    sections = _parse_skill_md(text=old_text)
    if _TEMPLATE_PLACEHOLDER not in sections.procedure:
        raise SkillLifecycleError(
            f"Skill '{skill_name}' already has an authored procedure. "
            "author_skill_procedure only fills a freshly scaffolded skill; "
            "use apply_procedure_delta to change an existing one."
        )
    procedure_body = procedure if procedure.endswith("\n") else f"{procedure}\n"
    done_when_body = done_when if done_when.endswith("\n") else f"{done_when}\n"
    candidate_text = _assemble_skill_md(
        sections=_SkillMdSections(
            prefix=sections.prefix,
            procedure=f"\n{procedure_body}",
            done_when=f"\n{done_when_body}",
        )
    )
    if candidate_text == old_text:
        raise SkillLifecycleError("author_skill_procedure made no changes.")

    return _commit_governed_skill_md(
        skill_name=skill_name,
        old_text=old_text,
        candidate_text=candidate_text,
        changelog_lines=(changelog_note,),
        min_validation_accuracy=min_validation_accuracy,
        run_behaviour=run_behaviour,
        min_behaviour_accuracy=min_behaviour_accuracy,
        behaviour_runner=behaviour_runner,
    )


def apply_procedure_delta(
    *,
    skill_name: str,
    delta: ProcedureDelta,
    changelog_note: str,
    min_validation_accuracy: float = 1.0,
    run_behaviour: bool = False,
    min_behaviour_accuracy: float = 1.0,
    behaviour_runner: BehaviourRunner | None = None,
) -> EditResult:
    """Apply incremental procedure deltas with validation and rollback.

    Instructor rule: change π and β through **deltas**, not full SKILL.md
    rewrites. Frontmatter / description (I) is untouched — use firing tests
    when editing descriptions separately.

    Workflow:

    1. Parse SKILL.md into prefix, procedure, done-when
    2. Apply delta operations inside bounded sections
    3. Score baseline validation, write candidate, re-score
    4. Rollback if validation fails or regresses
    5. Append structured delta lines to CHANGELOG

    Args:
        skill_name: Target skill folder name.
        delta: Incremental replacements, line removals, and append operations.
        changelog_note: Summary line recorded before per-delta audit lines.
        min_validation_accuracy: Minimum validation accuracy to accept the edit.
        run_behaviour: Also gate on the skill's behaviour tests (LLM calls).
        min_behaviour_accuracy: Minimum behaviour accuracy when enabled.
        behaviour_runner: Optional replacement for the LLM runner (tests).

    Returns:
        ``EditResult`` describing acceptance or rejection.

    Raises:
        SkillLifecycleError: If delta is empty or anchors are ambiguous.
    """
    path = skill_dir(name=skill_name) / "SKILL.md"
    if not path.is_file():
        raise SkillLifecycleError(f"SKILL.md not found for {skill_name}")

    old_text = path.read_text(encoding="utf-8")
    candidate_text = _apply_procedure_delta_to_text(text=old_text, delta=delta)
    if candidate_text == old_text:
        raise SkillLifecycleError("ProcedureDelta made no changes.")

    changelog_lines = (changelog_note, *_describe_delta(delta=delta))
    return _commit_governed_skill_md(
        skill_name=skill_name,
        old_text=old_text,
        candidate_text=candidate_text,
        changelog_lines=changelog_lines,
        min_validation_accuracy=min_validation_accuracy,
        run_behaviour=run_behaviour,
        min_behaviour_accuracy=min_behaviour_accuracy,
        behaviour_runner=behaviour_runner,
    )


def _update_manifest_version(*, name: str, version: str) -> None:
    path = manifest_path()
    if not path.is_file():
        return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for row in data.get("skills", []):
        if row.get("name") == name:
            row["version"] = version
            break
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
