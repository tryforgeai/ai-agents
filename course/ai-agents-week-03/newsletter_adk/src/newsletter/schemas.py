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
Data contracts between agents.

Passing one of these models as ``output_schema`` makes the LLM return JSON that
ADK validates and stores in state as a dict (under the agent's ``output_key``).

OpenAI strict mode treats every field as required, so these models avoid
defaults — use "" or [] when a value is unknown.
"""

from typing import Literal

from pydantic import BaseModel, Field

# --- validator_agent → state["validated_reports"] ---------------------------

class Claim(BaseModel):
    claim: str = Field(description="One factual claim taken from the article.")
    confidence: float = Field(
        description="0.0–1.0, based on how consistently other sources agree."
    )
    notes: str = Field(description="Why this confidence was given; '' if nothing to add.")


class ValidatedArticle(BaseModel):
    source_name: str
    article_title: str
    url: str
    url_format_ok: bool = Field(
        description=(
            "Heuristic only: the URL is complete and well-formed. "
            "It does NOT mean the page was opened."
        )
    )
    reputation_flag: Literal["ok", "low", "blacklisted"]
    claims: list[Claim]


class ValidatedReports(BaseModel):
    validated_articles: list[ValidatedArticle]


# --- analyst_agent → state["analysis_report"] -------------------------------

class TimelineEvent(BaseModel):
    date: str
    event: str


class Conflict(BaseModel):
    claim: str
    disagreement_sources: list[str]


class AnalysisReport(BaseModel):
    themes: list[str]
    timeline: list[TimelineEvent]
    conflicts: list[Conflict]
    summary: str = Field(description="Concise paragraph of patterns and takeaways.")
