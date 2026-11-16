#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------
"""Language models selected by the ``LLM_PROVIDER`` environment variable.

``LLM_PROVIDER=supportvectors`` sends every call to the SupportVectors
cluster. Any other value, including unset, uses hosted OpenAI.
"""

from __future__ import annotations

import os
from pathlib import Path

import dspy
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Hosted OpenAI. The task model is the one being optimized; the strong model
# is GEPA's reflection teacher and PAPILLON's untrusted external model.
_OPENAI_TASK_MODEL = "openai/gpt-5-mini"
_OPENAI_STRONG_MODEL = "openai/gpt-5"
_OPENAI_MAX_TOKENS = 32000

# SupportVectors cluster. Both models are on the same OpenAI-compatible
# server: gpt-oss-20b is the task model (the gpt-5-mini analog) and
# gpt-oss-120b is the stronger model (the gpt-5 analog).
_SV_TASK_MODEL = "openai/openai/gpt-oss-20b"
_SV_STRONG_MODEL = "openai/openai/gpt-oss-120b"
_SV_API_BASE = "http://10.0.10.70:8000/v1"
_SV_API_KEY = "not-needed"
_SV_MAX_TOKENS = 16000


def _load_env() -> None:
    load_dotenv(_PROJECT_ROOT / ".env")


def llm_provider() -> str:
    """Return the configured provider name, lowercased.

    Missing or blank ``LLM_PROVIDER`` means hosted OpenAI.
    """
    _load_env()
    return os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"


def use_supportvectors() -> bool:
    return llm_provider() == "supportvectors"


def make_lm(*, strong: bool = False) -> dspy.LM:
    """Build a DSPy language model for the provider in ``.env``.

    Args:
        strong: When true, return the stronger model. On OpenAI that is
            ``gpt-5`` (reflection LM / PAPILLON's untrusted model). On the
            SV cluster that is ``gpt-oss-120b``.
    """
    if use_supportvectors():
        model = (
            os.getenv("SV_STRONG_MODEL", _SV_STRONG_MODEL)
            if strong
            else os.getenv("SV_MODEL", _SV_TASK_MODEL)
        )
        return dspy.LM(
            model,
            api_base=os.getenv("SV_API_BASE", _SV_API_BASE),
            api_key=os.getenv("SV_API_KEY", _SV_API_KEY),
            temperature=1.0,
            max_tokens=int(os.getenv("SV_MAX_TOKENS", str(_SV_MAX_TOKENS))),
        )

    model = _OPENAI_STRONG_MODEL if strong else _OPENAI_TASK_MODEL
    return dspy.LM(model, temperature=1.0, max_tokens=_OPENAI_MAX_TOKENS)
