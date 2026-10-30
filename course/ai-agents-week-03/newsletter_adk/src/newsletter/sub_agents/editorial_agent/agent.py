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
Editorial writer — long-form Markdown draft from analysis + summaries.

Writes ``editorial_draft``. May re-run after HITL revise with ``{human_feedback?}``.
"""

from google.adk.agents import LlmAgent

from newsletter.settings import llm
from newsletter.sub_agents.editorial_agent.prompt import EDITORIAL_INSTRUCTION

editorial_agent = LlmAgent(
    name="editorial_content_generator",
    model=llm,
    description="Writes an original editorial using validated analysis and article summaries.",
    instruction=EDITORIAL_INSTRUCTION,
    output_key="editorial_draft",
)
