# =============================================================================
# Filename: agent.py
#
# Short Description: Exposed ADK agent without MCP guardrails.
#
# Creation date: 2026-06-29
# Author: SupportVectors TA Team
# =============================================================================

"""Exposed agent for the tool-poisoning lab."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from weather_agent.agents.shared import (
    INSTRUCTION,
    SHADOW_URL,
    FS_URL,
    http_toolset,
    lite_llm_model
)

from phoenix.otel import register

# Configure the Phoenix tracer provider
tracer_provider = register(
    project_name="exposed-agent",  # Change to your project name
    auto_instrument=True                   # Automatically instruments Google ADK via OpenInference
)

_APP_NAME = "exposed_agent"


def build_agent() -> LlmAgent:
    """Build the exposed agent connected to shadow and victim filesystem servers."""
    return LlmAgent(
        name="exposed_agent",
        model=lite_llm_model(),
        instruction=INSTRUCTION,
        tools=[http_toolset(SHADOW_URL), http_toolset(FS_URL)],
    )


root_agent = build_agent()
