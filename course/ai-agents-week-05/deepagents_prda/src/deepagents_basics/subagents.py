#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
PRDA Subagent Definitions

Specialized subagents for research, insights, architecture, validation, GTM, and writing.
"""

from deepagents import SubAgent

from deepagents_basics.prompts import (
    ARCHITECTURE_AGENT_PROMPT,
    GTM_AGENT_PROMPT,
    INSIGHTS_AGENT_PROMPT,
    RESEARCH_AGENT_PROMPT,
    VALIDATION_AGENT_PROMPT,
    WRITER_AGENT_PROMPT,
)
from deepagents_basics.tools import internet_search


def build_subagents() -> list[SubAgent]:
    """Build the 6 specialized subagents of the PRDA pipeline."""

    return [
        {
            "name": "research-agent",
            "description": "Deep market research and competitive intelligence",
            "system_prompt": RESEARCH_AGENT_PROMPT,
            "tools": [internet_search],
        },
        {
            "name": "insights-agent",
            "description": "Detailed user personas, pain points, feature prioritization",
            "system_prompt": INSIGHTS_AGENT_PROMPT,
            "tools": [],
        },
        {
            "name": "architecture-agent",
            "description": "Technical architecture with ASCII diagrams and cost estimates",
            "system_prompt": ARCHITECTURE_AGENT_PROMPT,
            "tools": [],
        },
        {
            "name": "validation-agent",
            "description": "Validation framework, SWOT, business model, unit economics",
            "system_prompt": VALIDATION_AGENT_PROMPT,
            "tools": [],
        },
        {
            "name": "gtm-agent",
            "description": "Go-to-market strategy, pricing, launch plan",
            "system_prompt": GTM_AGENT_PROMPT,
            "tools": [],
        },
        {
            "name": "writer-agent",
            "description": "Comprehensive PRD synthesis (all 14 sections)",
            "system_prompt": WRITER_AGENT_PROMPT,
            "tools": [],
        },
    ]
