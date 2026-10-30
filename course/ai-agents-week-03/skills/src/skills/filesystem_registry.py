# =============================================================================
# Filename: filesystem_registry.py
#
# Short Description: ADK SkillRegistry backed by the repo skill library.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Filesystem implementation of the ADK SkillRegistry interface.

Learning overview
--------------------
ADK defines ``SkillRegistry`` as an abstraction for *where skills live*:

- This repo → filesystem (``skills/`` folders)
- Production → GCS, GCP Skill Registry, marketplace zip, etc.

Students implement the same interface; only the backing store changes.

**Why refresh()?** Instructor maturity model Level 1→2 is "write procedures
down." In software terms: add a folder, call ``refresh()``, the agent sees it.
No redeploy of agent code required.

**Why search_skills?** The description (initiation set I) determines whether
a skill loads. ``search_skills`` uses sentence-transformer embeddings with a
cosine-similarity threshold so distant neighbors are not returned. An empty or
whitespace-only query skips embedding and returns the full catalog (same as
``list_skills`` semantics).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from google.adk.skills import load_skill_from_dir
from google.adk.skills.models import Frontmatter
from google.adk.skills.models import Skill
from google.adk.skills.skill_registry import SkillRegistry

from skills.paths import skill_library_dir
from skills.semantic_search import SemanticSearchSettings
from skills.semantic_search import resolve_semantic_search_settings
from skills.semantic_search import search_by_cosine_similarity
from skills.skill_loader import discover_frontmatters


class FilesystemSkillRegistry(SkillRegistry):
    """Load skills from ``<repo>/skills`` with on-demand refresh.

    Implements two ADK registry methods students should memorize:

    - ``get_skill`` — full load by name (L2+L3)
    - ``search_skills`` — discovery by query (L1 frontmatters only); blank
      query returns every skill without embedding

    New skill folders become visible after ``refresh()`` — supporting gradual
    library growth without redeploying agent code.
    """

    def __init__(
        self,
        *,
        base: Path | None = None,
        search_settings: SemanticSearchSettings | None = None,
    ) -> None:
        """Create a registry rooted at the skill library directory.

        Args:
            base: Optional override for the library root path.
            search_settings: Optional embedding model and similarity threshold.
        """
        self._base = (base or skill_library_dir()).resolve()
        self._search_settings = search_settings or resolve_semantic_search_settings()
        self._frontmatters: dict[str, Frontmatter] = {}
        self.refresh()

    def refresh(self) -> dict[str, Frontmatter]:
        """Rescan the library for new or removed skills.

        Call this after ``scaffold_skill`` or manual folder edits so the
        agent's search tool sees the latest catalog.

        Returns:
            Updated name → frontmatter mapping.
        """
        self._frontmatters = discover_frontmatters(base=self._base)
        return dict(self._frontmatters)

    def search_tool_description(self) -> str | None:
        """Guide the model to search before loading unfamiliar tasks.

        ADK injects this into the search tool's description — a hook for
        domain-specific retrieval hints (compare to instructor "pushy trigger").
        """
        return (
            "Search this filesystem skill library when the user's task may match "
            "a packaged procedure (transcripts, QBR, PII, commits, etc.). "
            "Use the returned skill names with load_skill."
        )

    async def get_skill(self, *, name: str) -> Skill:
        """Fetch a skill by name from disk.

        Async wrapper around blocking I/O — ADK registry contract is async.

        Args:
            name: Skill identifier.

        Returns:
            Fully loaded ADK ``Skill``.

        Raises:
            FileNotFoundError: If the skill folder does not exist.
            ValueError: If SKILL.md is invalid.
        """
        skill_path = self._base / name
        if not skill_path.is_dir():
            raise FileNotFoundError(f"Skill '{name}' not found under {self._base}")
        # to_thread: don't block the agent event loop on disk reads.
        return await asyncio.to_thread(load_skill_from_dir, skill_path)

    async def search_skills(self, *, query: str) -> list[Frontmatter]:
        """Semantic search over skill descriptions (L1 discovery).

        Embeds the query and each skill's name + description with a sentence
        transformer, ranks by cosine similarity, and drops results below the
        configured threshold.

        Args:
            query: Free-text task description from the agent. If empty or
                whitespace-only, embedding is skipped and the full catalog is
                returned (unordered), matching ``list_skills`` behavior.

        Returns:
            For a non-empty query: frontmatters ranked by descending cosine
            similarity, including only scores at or above the threshold. For a
            blank query: all frontmatters currently in the library.
        """
        self.refresh()
        if not query.strip():
            return list(self._frontmatters.values())

        names = list(self._frontmatters.keys())
        documents = [
            f"{self._frontmatters[name].name} {self._frontmatters[name].description}"
            for name in names
        ]
        settings = self._search_settings
        ranked = await asyncio.to_thread(
            search_by_cosine_similarity,
            query=query,
            documents=documents,
            model_name=settings.model_name,
            similarity_threshold=settings.similarity_threshold,
        )
        return [self._frontmatters[names[index]] for index, _ in ranked]
