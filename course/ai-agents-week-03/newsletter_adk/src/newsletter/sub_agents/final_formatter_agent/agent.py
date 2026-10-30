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
Final formatter — polish Markdown for publication.

Reads ``{editorial_draft}``, writes ``final_markdown_output`` (what UIs display).
"""

from google.adk.agents import LlmAgent

from newsletter.settings import llm
from newsletter.sub_agents.final_formatter_agent.prompt import FORMATTING_INSTRUCTION

final_formatter_agent = LlmAgent(
    name="FinalMarkdownFormatterAgent",
    model=llm,
    description="Formats the refined editorial into clean publication-ready Markdown.",
    instruction=FORMATTING_INSTRUCTION,
    output_key="final_markdown_output",
)
