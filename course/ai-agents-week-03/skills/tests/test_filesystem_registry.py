# =============================================================================
# Filename: test_filesystem_registry.py
#
# Short Description: Tests for FilesystemSkillRegistry search and refresh.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for the ADK filesystem skill registry."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from skills.filesystem_registry import FilesystemSkillRegistry
from skills.semantic_search import SemanticSearchSettings


@patch("skills.filesystem_registry.search_by_cosine_similarity")
def test_search_finds_transcript_skill(mock_search) -> None:
    registry = FilesystemSkillRegistry(
        search_settings=SemanticSearchSettings(
            model_name="test-model",
            similarity_threshold=0.35,
        ),
    )
    names = list(registry._frontmatters.keys())
    transcript_index = names.index("transcript-cleaner")
    mock_search.return_value = [(transcript_index, 0.82)]

    results = asyncio.run(registry.search_skills(query="noisy transcript de-mangle"))
    result_names = [fm.name for fm in results]
    assert "transcript-cleaner" in result_names
    mock_search.assert_called_once()


@patch("skills.filesystem_registry.search_by_cosine_similarity")
def test_search_blank_query_returns_all_skills(mock_search) -> None:
    registry = FilesystemSkillRegistry(
        search_settings=SemanticSearchSettings(
            model_name="test-model",
            similarity_threshold=0.35,
        ),
    )
    expected_names = {fm.name for fm in registry._frontmatters.values()}

    results = asyncio.run(registry.search_skills(query="   "))
    result_names = {fm.name for fm in results}

    assert result_names == expected_names
    mock_search.assert_not_called()


@patch("skills.filesystem_registry.search_by_cosine_similarity")
def test_search_returns_empty_when_below_threshold(mock_search) -> None:
    registry = FilesystemSkillRegistry(
        search_settings=SemanticSearchSettings(
            model_name="test-model",
            similarity_threshold=0.9,
        ),
    )
    mock_search.return_value = []

    results = asyncio.run(registry.search_skills(query="order pizza delivery"))
    assert results == []


def test_get_skill_async() -> None:
    registry = FilesystemSkillRegistry()
    skill = asyncio.run(registry.get_skill(name="commit-message"))
    assert skill.frontmatter.name == "commit-message"
    assert "conventional" in skill.instructions.lower()
