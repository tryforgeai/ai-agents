# =============================================================================
# Filename: agent.py
#
# Short Description: ADK agent that loads skills from the registry on demand.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Lazy / registry-only agent for side-by-side comparison in ADK web.

Run both agents::

    adk web src/skills/agents
"""

from __future__ import annotations

from skills.agent_factory import build_app

app = build_app(preload=False)
root_agent = app.root_agent
