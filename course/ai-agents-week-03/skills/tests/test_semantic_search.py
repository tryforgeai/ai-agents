# =============================================================================
# Filename: test_semantic_search.py
#
# Short Description: Tests for embedding-based cosine similarity search.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Tests for semantic skill search helpers."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from skills.semantic_search import cosine_similarity
from skills.semantic_search import keyword_exclusion_blocks
from skills.semantic_search import keyword_overlap_ratio
from skills.semantic_search import matches_by_cosine_similarity
from skills.semantic_search import matches_skill_description
from skills.semantic_search import search_by_cosine_similarity
from skills.semantic_search import split_description_zones


def test_cosine_similarity_for_unit_vectors() -> None:
    query = np.array([1.0, 0.0], dtype=np.float32)
    doc = np.array([0.6, 0.8], dtype=np.float32)
    assert cosine_similarity(query_embedding=query, doc_embedding=doc) == pytest.approx(
        0.6
    )


@patch("skills.semantic_search.embed_texts")
def test_search_filters_below_threshold(mock_embed_texts) -> None:
    mock_embed_texts.side_effect = [
        np.array([[1.0, 0.0]], dtype=np.float32),
        np.array(
            [
                [0.9, 0.1],
                [0.2, 0.8],
                [0.1, 0.1],
            ],
            dtype=np.float32,
        ),
    ]
    results = search_by_cosine_similarity(
        query="transcript cleanup",
        documents=["transcript skill", "quarterly report", "unrelated topic"],
        model_name="test-model",
        similarity_threshold=0.5,
    )
    assert len(results) == 1
    assert results[0][0] == 0
    assert results[0][1] == pytest.approx(0.9)


@patch("skills.semantic_search.embed_texts")
def test_search_returns_empty_for_blank_query(mock_embed_texts) -> None:
    results = search_by_cosine_similarity(
        query="   ",
        documents=["transcript skill"],
        model_name="test-model",
        similarity_threshold=0.5,
    )
    assert results == []
    mock_embed_texts.assert_not_called()


def test_split_description_zones() -> None:
    positive, exclusion = split_description_zones(
        description="Clean transcripts. Do NOT use for summarization."
    )
    assert positive == "Clean transcripts."
    assert exclusion == "for summarization."


def test_keyword_overlap_ratio() -> None:
    ratio = keyword_overlap_ratio(
        prompt="Clean this speech-to-text transcript output",
        document="transcript-cleaner Cleans raw speech-to-text lecture transcripts",
    )
    assert ratio >= 0.15


def test_keyword_exclusion_blocks_summarization() -> None:
    assert keyword_exclusion_blocks(
        prompt="Summarize this transcript in three bullet points",
        exclusion="for summarization or translation.",
    )


@patch("skills.semantic_search.embed_texts")
def test_matches_skill_description_keyword_fallback(mock_embed_texts) -> None:
    mock_embed_texts.side_effect = [
        np.array([[1.0, 0.0]], dtype=np.float32),
        np.array([[0.2, 0.8]], dtype=np.float32),
    ]
    assert matches_skill_description(
        skill_name="transcript-cleaner",
        description="Cleans raw speech-to-text lecture transcripts.",
        prompt="Clean this speech-to-text transcript output",
        model_name="test-model",
        similarity_threshold=0.35,
    )


@patch("skills.semantic_search.embed_texts")
def test_matches_skill_description_rejects_exclusion_zone(mock_embed_texts) -> None:
    mock_embed_texts.side_effect = [
        np.array([[1.0, 0.0]], dtype=np.float32),
        np.array([[0.9, 0.1]], dtype=np.float32),
        np.array([[0.95, 0.05]], dtype=np.float32),
    ]
    assert not matches_skill_description(
        skill_name="transcript-cleaner",
        description="Clean transcripts. Do NOT use for summarization.",
        prompt="Summarize this transcript",
        model_name="test-model",
        similarity_threshold=0.35,
        exclusion_margin=0.03,
    )


@patch("skills.semantic_search.embed_texts")
def test_matches_by_cosine_similarity(mock_embed_texts) -> None:
    mock_embed_texts.side_effect = [
        np.array([[1.0, 0.0]], dtype=np.float32),
        np.array([[0.9, 0.1]], dtype=np.float32),
    ]
    assert matches_by_cosine_similarity(
        query="transcript cleanup",
        document="transcript-cleaner Cleans lecture transcripts",
        model_name="test-model",
        similarity_threshold=0.5,
    )
    mock_embed_texts.side_effect = [
        np.array([[1.0, 0.0]], dtype=np.float32),
        np.array([[0.1, 0.1]], dtype=np.float32),
    ]
    assert not matches_by_cosine_similarity(
        query="transcript cleanup",
        document="unrelated topic",
        model_name="test-model",
        similarity_threshold=0.5,
    )
