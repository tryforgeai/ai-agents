#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
One place for knobs every agent shares.

In ``.env``, uncomment **exactly one** ``NEWSLETTER_LLM_PROVIDER=...`` line
(and the matching model / key lines for that provider). Commented lines are
ignored. If the same key appears more than once uncommented, the **last**
one wins — so you can leave older options commented above the active one.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from google.adk.models.lite_llm import LiteLlm

_ENV_ASSIGN = re.compile(
    r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$"""
)


def _strip_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    # inline comment: KEY=value # note  (only when unquoted)
    if " #" in value and not (raw.strip().startswith('"') or raw.strip().startswith("'")):
        value = value.split(" #", 1)[0].rstrip()
    return value


def _load_dotenv_last_wins() -> Path | None:
    """
    Load project ``.env`` with last-uncommented-assignment wins.

    Standard python-dotenv is first-wins and skips keys already in the
    process environment, which fights the "uncomment to select" workflow.
    """
    # Prefer workspace .env (two levels up from this file: src/newsletter/settings.py)
    candidates = [
        Path(__file__).resolve().parents[2] / ".env",
        Path.cwd() / ".env",
    ]
    env_path = next((p for p in candidates if p.is_file()), None)
    if env_path is None:
        return None

    parsed: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ENV_ASSIGN.match(stripped)
        if not match:
            continue
        key, raw_val = match.group(1), match.group(2)
        parsed[key] = _strip_value(raw_val)

    for key, value in parsed.items():
        os.environ[key] = value
    return env_path


_load_dotenv_last_wins()

# "local" | "openai" | "openrouter" — set by uncommenting one line in .env
LLM_PROVIDER = os.getenv("NEWSLETTER_LLM_PROVIDER", "local").strip().lower()


def _build_llm() -> tuple[str, LiteLlm]:
    """Return (model_name, shared LiteLlm client) for the selected provider."""
    model_override = os.getenv("NEWSLETTER_MODEL")  # optional force-override

    if LLM_PROVIDER == "openai":
        model = model_override or os.getenv("NEWSLETTER_OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("NEWSLETTER_API_KEY")
        kwargs: dict = {"model": model}
        if api_key:
            kwargs["api_key"] = api_key
        return model, LiteLlm(**kwargs)

    if LLM_PROVIDER == "openrouter":
        model = model_override or os.getenv(
            "NEWSLETTER_OPENROUTER_MODEL", "openrouter/openai/gpt-4o-mini"
        )
        if not model.startswith("openrouter/"):
            model = f"openrouter/{model}"
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("NEWSLETTER_API_KEY")
        kwargs = {"model": model}
        if api_key:
            kwargs["api_key"] = api_key
        api_base = os.getenv("OPENROUTER_API_BASE")
        if api_base:
            kwargs["api_base"] = api_base
        return model, LiteLlm(**kwargs)

    if LLM_PROVIDER != "local":
        raise ValueError(
            f"Unknown NEWSLETTER_LLM_PROVIDER={LLM_PROVIDER!r}. "
            "Uncomment one of: local | openai | openrouter in .env"
        )

    model = model_override or os.getenv(
        "NEWSLETTER_LOCAL_MODEL", "openai/openai/gpt-oss-20b"
    )
    api_base = os.getenv("NEWSLETTER_API_BASE", "http://10.0.10.70:8000/v1")
    api_key = os.getenv("NEWSLETTER_API_KEY", "dummy")
    return model, LiteLlm(model=model, api_base=api_base, api_key=api_key)


MODEL, llm = _build_llm()

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "9000"))
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", f"http://{MCP_HOST}:{MCP_PORT}/mcp")

PHOENIX_PROJECT_NAME = os.getenv("PHOENIX_PROJECT_NAME", "adk-agent-new-2")
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() in {"1", "true", "yes"}
