# =============================================================================
# Filename: llm_config.py
#
# Short Description: LiteLLM / OpenAI-compatible model settings for ADK.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Shared LLM configuration for the agent skills demo.

Note for learners
----------------
Skills change **what the agent does** (procedure in context).
The model endpoint changes **who reasons** about that procedure.

This bootcamp uses ``LiteLlm`` to point ADK at an OpenAI-compatible server
(e.g. local vLLM). Students can swap models without touching skill folders.

Environment variables (set in ``.env`` or shell):

- ``LLM_API_BASE`` — OpenAI-compatible base URL
- ``LLM_MODEL_NAME`` — model id (provider prefix added automatically)
- ``OPENAI_API_KEY`` — API key (may be dummy for local servers)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

import litellm
from google.adk.models.lite_llm import LiteLlm

# Bootcamp lab defaults — override via environment for your deployment.
# LLM endpoint options (defaults target hosted OpenAI):
#  (a) OpenAI hosted (default): model gpt-5-mini, base URL https://api.openai.com/v1 (or omit it), OPENAI_API_KEY required
#  (b) self-hosted OpenAI-compatible server (vLLM / Ollama): set the base URL to your local server (e.g. http://localhost:8000/v1) and a served model, e.g. openai/gpt-oss-20b
_DEFAULT_BASE_URL: Final[str] = "https://api.openai.com/v1"
_DEFAULT_API_KEY: Final[str] = "not-needed"
_DEFAULT_MODEL: Final[str] = "gpt-5-mini"


def _litellm_model_id(model_name: str, base_url: str) -> str:
    """Pick the LiteLLM provider by destination (same rule as the ch08-01 lab).

    - Hosted OpenAI: ``openai/<name>`` so LiteLLM's gpt-5 parameter handling
      applies (e.g. max_tokens → max_completion_tokens).
    - Self-hosted router: ``hosted_vllm/<served-id>`` so the router receives
      the full id (e.g. ``openai/gpt-oss-20b``) unchanged.
    """
    name = model_name.strip()
    if name.startswith(("hosted_vllm/", "openai/openai/")):
        return name
    if "api.openai.com" in base_url:
        return f"openai/{name.removeprefix('openai/')}"
    return f"hosted_vllm/{name}"


@dataclass(frozen=True)
class LlmSettings:
    """OpenAI-compatible endpoint configuration."""

    base_url: str
    api_key: str
    model: str


def resolve_llm_settings() -> LlmSettings:
    """Read LLM settings from environment variables.

    Returns:
        Resolved ``LlmSettings`` with defaults for local bootcamp endpoints.
    """
    base_url = os.getenv("LLM_API_BASE", _DEFAULT_BASE_URL)
    return LlmSettings(
        base_url=base_url,
        api_key=os.getenv("OPENAI_API_KEY", _DEFAULT_API_KEY),
        model=_litellm_model_id(os.getenv("LLM_MODEL_NAME", _DEFAULT_MODEL), base_url),
    )


def _ensure_litellm_httpx_transport() -> None:
    """Prefer httpx over aiohttp for OpenAI-compatible lab endpoints.

    Some bootcamp vLLM proxies emit duplicate ``Server`` response headers.
    LiteLLM's default aiohttp transport rejects those; httpx tolerates them.
    """
    litellm.disable_aiohttp_transport = True


def make_lite_llm() -> LiteLlm:
    """Build the ADK LiteLLM model wrapper.

    Requires ``google-adk[extensions]`` — LiteLLM is optional in base ADK.

    Returns:
        Configured ``LiteLlm`` instance for ``LlmAgent``.
    """
    _ensure_litellm_httpx_transport()
    settings = resolve_llm_settings()
    return LiteLlm(
        model=settings.model,
        api_base=settings.base_url,
        api_key=settings.api_key,
    )
