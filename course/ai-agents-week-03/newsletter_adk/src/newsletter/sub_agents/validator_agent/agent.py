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
Validator — credibility filter after collection.

No tools: reads the four collector output keys from state and writes
``validated_reports`` (shape: ``ValidatedReports``) for the article reader / analyst.
"""

from google.adk.agents import LlmAgent

from newsletter.schemas import ValidatedReports
from newsletter.settings import llm
from newsletter.sub_agents.validator_agent.prompt import VALIDATOR_INSTRUCTION

validator_agent = LlmAgent(
    name="validator_agent",
    model=llm,
    description="Cross-checks collected articles for credibility and URL quality.",
    instruction=VALIDATOR_INSTRUCTION,
    output_schema=ValidatedReports,  # forces JSON matching the Pydantic model
    output_key="validated_reports",
)
