# =============================================================================
# Filename: skill_loader.py
#
# Short Description: Discover and load Agent Skills from the repo library.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Load skills from the on-disk library using Google ADK helpers.

Learning overview
--------------------
This module demonstrates **two speeds** of reading the library:

1. **Discovery (cheap)** — ``discover_frontmatters()`` reads only YAML
   frontmatter from each ``SKILL.md``. This is Level 1 / initiation set I.
2. **Full load (expensive)** — ``load_skill()`` reads body + all L3 files.
   This is what happens when the agent calls ADK's ``load_skill`` tool.

We also join:

- **Disk scan** — what ADK actually finds on the filesystem.
- **manifest.yaml** — what humans *claim* is in the library (curation).

Comparing them in ``snapshot_library()`` teaches operational observability.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from google.adk.skills import load_skill_from_dir
from google.adk.skills._utils import _read_skill_properties
from google.adk.skills.models import Frontmatter
from google.adk.skills.models import Skill
from loguru import logger

from skills.paths import manifest_path
from skills.paths import skill_dir
from skills.paths import skill_library_dir


@dataclass(frozen=True)
class SkillManifestEntry:
    """One row from ``skills/manifest.yaml``.

    Fields map to library curation concerns from instructor theory:
    - ``pattern`` — which skeleton (lean-core, guardrail, etc.)
    - ``status`` — draft vs active (governance workflow)
  """

    name: str
    version: str
    pattern: str
    status: str


@dataclass(frozen=True)
class SkillLibrarySnapshot:
    """Point-in-time view of the skill library.

    Use in demos/logging to show students:
    - manifest says X
    - disk scan found Y
    Mismatches (e.g. forgot to update manifest) are notes for the instructor.
    """

    manifest_version: str
    maturity_level: int
    entries: tuple[SkillManifestEntry, ...]
    discovered: dict[str, Frontmatter]


class SkillLoadError(Exception):
    """Raised when a skill cannot be loaded from disk."""


def _skip_dir(*, path: Path) -> bool:
    # Underscore prefixes keep templates and hidden dirs out of the library.
    return path.name.startswith("_") or path.name.startswith(".")


def discover_frontmatters(*, base: Path | None = None) -> dict[str, Frontmatter]:
    """List L1 metadata for every skill folder under the library.

    Scans the library like ADK's ``list_skills_in_dir``, but skips scaffold
    folders (``_templates/``, dot dirs) before reading ``SKILL.md`` so ADK
    does not emit spurious "invalid skill" warnings for non-skill paths.

    Args:
        base: Optional override for the library root (used in tests).

    Returns:
        Mapping of skill name to ADK ``Frontmatter``.
    """
    root = base or skill_library_dir()
    if not root.is_dir():
        logger.warning("Skill library missing at {}", root)
        return {}

    skills: dict[str, Frontmatter] = {}
    for skill_folder in sorted(root.iterdir()):
        if not skill_folder.is_dir() or _skip_dir(path=skill_folder):
            continue
        try:
            frontmatter = _read_skill_properties(skill_folder)
            if skill_folder.name != frontmatter.name:
                raise ValueError(
                    f"Skill name '{frontmatter.name}' does not match directory"
                    f" name '{skill_folder.name}'."
                )
            skills[frontmatter.name] = frontmatter
        except (FileNotFoundError, ValueError) as exc:
            logger.warning(
                "Skipping invalid skill '{}' under {}: {}",
                skill_folder.name,
                root,
                exc,
            )
    return skills


def load_manifest() -> tuple[str, int, list[SkillManifestEntry]]:
    """Parse ``skills/manifest.yaml``.

    ``maturity_level`` encodes the organizational adoption model from instructor
    theory (0=ad-hoc … 4=self-improving). This repo targets Level 2–3.

    Returns:
        Tuple of manifest version, maturity level, and skill entries.
    """
    path = manifest_path()
    if not path.is_file():
        return "0.0.0", 0, []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = [
        SkillManifestEntry(
            name=str(row["name"]),
            version=str(row.get("version", "0.0.0")),
            pattern=str(row.get("pattern", "lean-core")),
            status=str(row.get("status", "draft")),
        )
        for row in data.get("skills", [])
    ]
    return (
        str(data.get("version", "0.0.0")),
        int(data.get("maturity_level", 0)),
        entries,
    )


def snapshot_library() -> SkillLibrarySnapshot:
    """Build a manifest + discovery snapshot for observability.

    Called by ``skillcraft-demo --list-skills`` so students can inspect
    the library without invoking an LLM.

    Returns:
        ``SkillLibrarySnapshot`` combining manifest and disk scan.
    """
    manifest_version, maturity, entries = load_manifest()
    discovered = discover_frontmatters()
    return SkillLibrarySnapshot(
        manifest_version=manifest_version,
        maturity_level=maturity,
        entries=tuple(entries),
        discovered=discovered,
    )


def load_skill(*, name: str) -> Skill:
    """Load a single skill by name (L2 body + L3 resources).

    Args:
        name: Skill folder / frontmatter name.

    Returns:
        ADK ``Skill`` with instructions and bundled resources.

    Raises:
        SkillLoadError: If loading fails (missing SKILL.md, name mismatch).
    """
    directory = skill_dir(name=name)
    try:
        return load_skill_from_dir(directory)
    except (FileNotFoundError, ValueError) as exc:
        raise SkillLoadError(str(exc)) from exc


def load_all_skills(*, base: Path | None = None) -> list[Skill]:
    """Load every skill directory under the library.

    Used at agent startup to preload the toolset. Tradeoff to discuss in class:
    - **Preload all** — simpler, faster list_skills, higher memory.
    - **Registry only** — lazy load, better for huge libraries.

    Args:
        base: Optional override for the library root.

    Returns:
        List of ADK ``Skill`` objects (skips ``_templates`` and dot dirs).
    """
    root = base or skill_library_dir()
    frontmatters = discover_frontmatters(base=root)
    skills: list[Skill] = []
    for name in sorted(frontmatters):
        folder = root / name
        if _skip_dir(path=folder):
            continue
        try:
            skills.append(load_skill_from_dir(folder))
        except (FileNotFoundError, ValueError) as exc:
            # Log and continue — one broken skill should not brick the agent.
            logger.error("Skipping skill {}: {}", name, exc)
    return skills
