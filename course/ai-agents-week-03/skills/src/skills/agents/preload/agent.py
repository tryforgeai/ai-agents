# =============================================================================
# Filename: agent.py
#
# Short Description: ADK agent that preloads all skills at startup.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Preload strategy agent for side-by-side comparison in ADK web.

Run both agents::

    adk web src/skills/agents
"""

from __future__ import annotations

from skills.agent_factory import build_app

app = build_app(preload=True)
root_agent = app.root_agent
