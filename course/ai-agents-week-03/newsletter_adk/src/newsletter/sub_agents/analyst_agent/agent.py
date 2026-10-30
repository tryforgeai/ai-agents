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
Analyst — themes / timeline / conflicts.

Uses ``validated_reports`` for substance and source metadata.
Writes ``analysis_report`` (shape: ``AnalysisReport``).
"""

from google.adk.agents import LlmAgent

from newsletter.schemas import AnalysisReport
from newsletter.settings import llm
from newsletter.sub_agents.analyst_agent.prompt import ANALYST_INSTRUCTION

analyst_agent = LlmAgent(
    name="analyst_agent",
    model=llm,
    description="Analyzes validated content for themes and conflicts.",
    instruction=ANALYST_INSTRUCTION,
    output_schema=AnalysisReport,
    output_key="analysis_report",
)
