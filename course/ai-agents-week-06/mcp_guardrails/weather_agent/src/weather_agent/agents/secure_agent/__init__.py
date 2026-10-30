# =============================================================================
# Filename: __init__.py
#
# Short Description: Hardened agent package exports.
#
# Creation date: 2026-06-30
# Author: SupportVectors TA Team
# =============================================================================

"""Hardened agent package."""

from weather_agent.agents.secure_agent.agent import build_agent, root_agent
from weather_agent.agents.secure_agent.guardrails import (
    sanitize_tool_description,
    sanitize_tool_output,
)

__all__ = [
    "build_agent",
    "root_agent",
    "sanitize_tool_description",
    "sanitize_tool_output",
]
