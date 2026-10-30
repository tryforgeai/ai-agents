# =============================================================================
# Filename: agent.py
#
# Short Description: Hardened ADK agent with MCP input/output guardrails.
#
# Creation date: 2026-06-30
# Author: SupportVectors TA Team
# =============================================================================

"""Hardened agent with MCP guardrails."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from weather_agent.agents.secure_agent.guardrails import guarded_http_toolset
from weather_agent.agents.shared import (
    INSTRUCTION,
    SHADOW_URL,
    FS_URL,
    lite_llm_model,
)

from phoenix.otel import register

# Configure the Phoenix tracer provider
tracer_provider = register(
    project_name="secure-agent",  # Change to your project name
    auto_instrument=True                   # Automatically instruments Google ADK via OpenInference
)
_APP_NAME = "secure_agent"


def build_agent() -> LlmAgent:
    """Build the secure agent with guarded MCP toolsets."""
    return LlmAgent(
        name="secure_agent",
        model=lite_llm_model(),
        instruction=INSTRUCTION,
        tools=[
            guarded_http_toolset(SHADOW_URL),
            guarded_http_toolset(FS_URL),
        ],
    )



root_agent = build_agent()
