# =============================================================================
# Filename: paths.py
#
# Short Description: Resolve project root and on-disk skill library paths.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Filesystem paths for the skill library and manifest.

Why this layout matters
-----------------
Skills live at the **repository root** (``skills/``), not under ``src/``.
That separation is deliberate:

- Skill folders are **portable artifacts** (zip, git, marketplace).
- Python under ``src/skills/`` is **runtime plumbing**.

Every module that needs the library should call functions here instead of
hard-coding paths — one place to explain the layout to students.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# Bootcamp projects set this in .env — keeps paths correct in notebooks/IDEs.
_ENV_ROOT: Final[str] = "BOOTCAMP_ROOT_DIR"
_MANIFEST_NAME: Final[str] = "manifest.yaml"
_LIBRARY_DIR_NAME: Final[str] = "skills"
_TEMPLATE_DIR_NAME: Final[str] = "_templates"


def project_root() -> Path:
    """Return the repository root directory.

    Resolution order (teach explicit configuration first):
    1. ``BOOTCAMP_ROOT_DIR`` environment variable (bootcamp standard)
    2. Infer from this file: ``src/skills/paths.py`` → three parents up

    Returns:
        Path to the project root (parent of the ``skills/`` library folder).
    """
    env_root = os.environ.get(_ENV_ROOT)
    if env_root:
        return Path(env_root).resolve()
    # paths.py is at src/skills/paths.py → parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def skill_library_dir() -> Path:
    """Return the root-level skill library directory.

    This is the folder ADK's ``load_skill_from_dir`` expects to contain
    one subfolder per skill (e.g. ``transcript-cleaner/SKILL.md``).

    Returns:
        Path to ``<project_root>/skills``.
    """
    return project_root() / _LIBRARY_DIR_NAME


def manifest_path() -> Path:
    """Return the skill library manifest file path.

    ``manifest.yaml`` is *curation* (human registry), not required by ADK.
    It tracks versions, patterns, and maturity — see instructor theory Level 2.
    """
    return skill_library_dir() / _MANIFEST_NAME


def template_dir() -> Path:
    """Return the lean-core scaffold template directory.

    ``_templates/`` is prefixed with underscore so our library scan
    skips it (scaffold-only, not a real skill).
    """
    return template_dir_for_pattern(pattern="lean-core")


def template_dir_for_pattern(*, pattern: str) -> Path:
    """Return the scaffold template directory for a named pattern.

    Args:
        pattern: Pattern label (e.g. ``lean-core``).

    Returns:
        Path to ``skills/_templates/<pattern>/``.
    """
    return skill_library_dir() / _TEMPLATE_DIR_NAME / pattern


def skill_dir(*, name: str) -> Path:
    """Return the directory for a named skill.

    ADK enforces: folder name == frontmatter ``name`` in SKILL.md.
    Teach students this invariant early — mismatches cause load errors.

    Args:
        name: Skill identifier (must match folder and frontmatter name).

    Returns:
        Path to ``skills/<name>/``.
    """
    return skill_library_dir() / name
