# =============================================================================
# Filename: semantic_search.py
#
# Short Description: Sentence-transformer embeddings and cosine-similarity search.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Semantic skill discovery via sentence-transformer embeddings.

Uses L2-normalized vectors so dot product equals cosine similarity. Results
below ``similarity_threshold`` are dropped so unrelated nearest neighbors are
not returned.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

_DEFAULT_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
_DEFAULT_THRESHOLD: Final[float] = 0.35
_ENV_MODEL: Final[str] = "SKILL_SEARCH_MODEL"
_ENV_THRESHOLD: Final[str] = "SKILL_SEARCH_SIMILARITY_THRESHOLD"
_EXCLUSION_MARGIN: Final[float] = 0.03
_MIN_TOKEN_LENGTH: Final[int] = 4
_KEYWORD_OVERLAP_THRESHOLD: Final[float] = 0.15
_KEYWORD_EXCLUSION_STEMS: Final[tuple[str, ...]] = (
    "summar",
    "translat",
    "review",
    "release note",
    "anonymiz",
    "public",
)

_sentence_transformer: SentenceTransformer | None = None
_loaded_model_name: str | None = None


@dataclass(frozen=True)
class SemanticSearchSettings:
    """Configuration for embedding-based skill search."""

    model_name: str
    similarity_threshold: float


def resolve_semantic_search_settings() -> SemanticSearchSettings:
    """Read semantic search settings from environment variables.

    Returns:
        Resolved model name and minimum cosine-similarity score.
    """
    raw_threshold = os.getenv(_ENV_THRESHOLD, str(_DEFAULT_THRESHOLD))
    return SemanticSearchSettings(
        model_name=os.getenv(_ENV_MODEL, _DEFAULT_MODEL),
        similarity_threshold=float(raw_threshold),
    )


def _get_sentence_transformer(*, model_name: str) -> SentenceTransformer:
    """Lazy-load and cache the sentence transformer model."""
    global _sentence_transformer, _loaded_model_name
    if _sentence_transformer is None or _loaded_model_name != model_name:
        from sentence_transformers import SentenceTransformer

        _sentence_transformer = SentenceTransformer(model_name)
        _loaded_model_name = model_name
    return _sentence_transformer


def embed_texts(*, texts: list[str], model_name: str) -> np.ndarray:
    """Compute L2-normalized embeddings for a list of texts.

    Args:
        texts: Strings to embed.
        model_name: Hugging Face sentence-transformer model id.

    Returns:
        Float32 array of shape ``(len(texts), embedding_dim)``.
    """
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    model = _get_sentence_transformer(model_name=model_name)
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(embeddings, dtype=np.float32)


def cosine_similarity(
    *, query_embedding: np.ndarray, doc_embedding: np.ndarray
) -> float:
    """Cosine similarity for unit-length embedding vectors."""
    return float(np.dot(query_embedding, doc_embedding))


def search_by_cosine_similarity(
    *,
    query: str,
    documents: list[str],
    model_name: str,
    similarity_threshold: float,
) -> list[tuple[int, float]]:
    """Rank document indices by cosine similarity to the query.

    Args:
        query: Free-text search string. Empty or whitespace-only queries
            return an empty list (no embedding). Callers such as
            ``FilesystemSkillRegistry.search_skills`` may treat a blank query
            differently before invoking this helper.
        documents: Candidate texts (e.g. skill name + description).
        model_name: Sentence-transformer model id.
        similarity_threshold: Minimum cosine similarity to include a hit.

    Returns:
        ``(index, score)`` pairs sorted by descending score, threshold-filtered.
        Returns ``[]`` when ``query`` is blank or ``documents`` is empty.
    """
    query_stripped = query.strip()
    if not query_stripped or not documents:
        return []

    query_embedding = embed_texts(texts=[query_stripped], model_name=model_name)[0]
    doc_embeddings = embed_texts(texts=documents, model_name=model_name)

    scored: list[tuple[int, float]] = []
    for index, doc_embedding in enumerate(doc_embeddings):
        score = cosine_similarity(
            query_embedding=query_embedding,
            doc_embedding=doc_embedding,
        )
        if score >= similarity_threshold:
            scored.append((index, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def matches_by_cosine_similarity(
    *,
    query: str,
    document: str,
    model_name: str,
    similarity_threshold: float,
) -> bool:
    """Return whether ``document`` is semantically similar enough to ``query``.

    Args:
        query: Free-text prompt or search string.
        document: Candidate text (e.g. skill name + description).
        model_name: Sentence-transformer model id.
        similarity_threshold: Minimum cosine similarity to count as a match.

    Returns:
        ``True`` when cosine similarity meets or exceeds the threshold.
    """
    results = search_by_cosine_similarity(
        query=query,
        documents=[document],
        model_name=model_name,
        similarity_threshold=similarity_threshold,
    )
    return len(results) > 0


def split_description_zones(*, description: str) -> tuple[str, str]:
    """Split a skill description into positive and exclusion zones.

    Args:
        description: Full skill description from frontmatter.

    Returns:
        ``(positive_zone, exclusion_zone)``. ``exclusion_zone`` is empty when no
        ``Do NOT use`` clause is present.
    """
    parts = re.split(r"(?i)do not use", description, maxsplit=1)
    positive = parts[0].strip()
    exclusion = parts[1].strip() if len(parts) > 1 else ""
    return positive, exclusion


def _tokenize_for_overlap(*, text: str) -> list[str]:
    """Extract lowercase alphanumeric tokens for keyword overlap."""
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= _MIN_TOKEN_LENGTH
    ]


def keyword_overlap_ratio(*, prompt: str, document: str) -> float:
    """Fraction of prompt tokens (length >= 4) found in ``document``.

    Args:
        prompt: User or test prompt.
        document: Skill name + description text to match against.

    Returns:
        Overlap ratio in ``[0.0, 1.0]``. Returns ``0.0`` when there are no
        qualifying prompt tokens.
    """
    tokens = _tokenize_for_overlap(text=prompt)
    if not tokens:
        return 0.0
    document_lower = document.lower()
    hits = sum(1 for token in tokens if token in document_lower)
    return hits / len(tokens)


def keyword_exclusion_blocks(*, prompt: str, exclusion: str) -> bool:
    """Return whether prompt keywords align with the exclusion zone.

    Args:
        prompt: User or test prompt.
        exclusion: Text after the ``Do NOT use`` clause.

    Returns:
        ``True`` when a shared exclusion stem appears in both prompt and zone.
    """
    if not exclusion.strip():
        return False
    prompt_lower = prompt.lower()
    exclusion_lower = exclusion.lower()
    return any(
        stem in prompt_lower and stem in exclusion_lower
        for stem in _KEYWORD_EXCLUSION_STEMS
    )


def _keyword_match_positive_zone(
    *,
    skill_name: str,
    positive_document: str,
    prompt: str,
) -> bool:
    """Keyword fallback when cosine similarity is below threshold."""
    overlap = keyword_overlap_ratio(prompt=prompt, document=positive_document)
    if overlap >= _KEYWORD_OVERLAP_THRESHOLD:
        return True

    prompt_lower = prompt.lower()
    document_lower = positive_document.lower()
    name_cues = [
        part for part in skill_name.split("-") if len(part) >= _MIN_TOKEN_LENGTH
    ]
    if any(cue in prompt_lower and cue in document_lower for cue in name_cues):
        return True

    return any(
        cue in prompt_lower and cue in document_lower
        for cue in ("transcript", "qbr", "quarterly", "pii", "commit", "diff")
    )


def matches_skill_description(
    *,
    skill_name: str,
    description: str,
    prompt: str,
    model_name: str,
    similarity_threshold: float,
    exclusion_margin: float = _EXCLUSION_MARGIN,
) -> bool:
    """Return whether a prompt matches a skill description.

    Primary signal is cosine similarity on the positive description zone.
    When that is below ``similarity_threshold``, a keyword-overlap fallback
    is tried (token overlap, skill-name cues, and shared domain terms).
    Exclusion zones are checked by keyword stems always. Semantic exclusion
    (exclusion cosine score beating positive by ``exclusion_margin``) applies
    only when the positive score is already in the ambiguous band
    (>= ``similarity_threshold * 0.5``), so low-scoring prompts can still use
    the keyword fallback.

    Args:
        skill_name: Skill folder name (prepended to each zone, like search).
        description: Full initiation-set text from frontmatter.
        prompt: User or test prompt to evaluate.
        model_name: Sentence-transformer model id.
        similarity_threshold: Minimum cosine similarity for a positive match.
        exclusion_margin: Required positive-zone lead over the exclusion zone.

    Returns:
        ``True`` when the prompt matches the description under these rules.
    """
    prompt_stripped = prompt.strip()
    if not prompt_stripped:
        return False

    positive, exclusion = split_description_zones(description=description)
    positive_document = f"{skill_name} {positive}"
    query_embedding = embed_texts(texts=[prompt_stripped], model_name=model_name)[0]
    positive_embedding = embed_texts(
        texts=[positive_document],
        model_name=model_name,
    )[0]
    positive_score = cosine_similarity(
        query_embedding=query_embedding,
        doc_embedding=positive_embedding,
    )

    if exclusion:
        exclusion_document = f"{skill_name} {exclusion}"
        exclusion_embedding = embed_texts(
            texts=[exclusion_document],
            model_name=model_name,
        )[0]
        exclusion_score = cosine_similarity(
            query_embedding=query_embedding,
            doc_embedding=exclusion_embedding,
        )
        if keyword_exclusion_blocks(prompt=prompt_stripped, exclusion=exclusion):
            return False
        semantic_ambiguity_floor = similarity_threshold * 0.5
        semantically_excluded = exclusion_score > positive_score + exclusion_margin
        if semantically_excluded and positive_score >= semantic_ambiguity_floor:
            return False

    if positive_score >= similarity_threshold:
        return True

    return _keyword_match_positive_zone(
        skill_name=skill_name,
        positive_document=positive_document,
        prompt=prompt_stripped,
    )
