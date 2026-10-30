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
STUDENT ENTRYPOINT — wire the whole app together here.

Two graphs:
1) root_agent (NewsletterApp): chat vs newsletter routing
2) newsletter_pipeline (NewsletterFlow): the multi-step newsletter job

Agents talk through session state via ``output_key`` (e.g. validated_reports).
Later prompts read those keys with ``{validated_reports}`` placeholders.

Run with:
  - MCP tools:  uv run src/newsletter/mcp/fastmcp_server.py
  - ADK web:    cd src && adk web
  - Streamlit:  streamlit run src/newsletter/app.py
  - CLI:        uv run src/newsletter/agent_runner.py
"""

# Phoenix / OTEL must start before google.adk is imported (auto_instrument).
from newsletter.tracing import setup_tracing

setup_tracing()

from google.adk import Workflow
from google.adk.apps import App, ResumabilityConfig
from google.adk.workflow import START

from newsletter.sub_agents.analyst_agent.agent import analyst_agent
from newsletter.sub_agents.editorial_agent.agent import editorial_agent
from newsletter.sub_agents.final_formatter_agent.agent import final_formatter_agent
from newsletter.sub_agents.human_review.agent import (
    ask_human_review_node,
    route_human_review_node,
)
from newsletter.sub_agents.intent_router.agent import (
    chat_agent,
    intent_classifier_agent,
    route_intent_node,
    stash_user_query_node,
)
from newsletter.sub_agents.newsletter_collector.agent import newsletter_collector
from newsletter.sub_agents.validator_agent.agent import validator_agent

# ---------------------------------------------------------------------------
# NewsletterFlow — only runs when intent == "newsletter"
# Steps: collect → validate → analyze → write → HITL → format
# ---------------------------------------------------------------------------

newsletter_pipeline = Workflow(
    name="NewsletterFlow",
    description=(
        "Collect → Validate → Analyze → Write → Human Review → Format"
    ),
    edges=[
        (
            START,
            newsletter_collector,
            validator_agent,
            analyst_agent,
            editorial_agent,
            ask_human_review_node,   # pauses for human approve/revise
            route_human_review_node,
        ),
        # Conditional branch after human review
        (
            route_human_review_node,
            {
                "approve": final_formatter_agent,
                "revise": editorial_agent,  # rewrite with human_feedback in state
            },
        ),
    ],
)

# ---------------------------------------------------------------------------
# NewsletterApp — root graph students hit first
# ---------------------------------------------------------------------------

root_agent = Workflow(
    name="NewsletterApp",
    description=(
        "Routes simple questions to chat; runs NewsletterFlow only for "
        "newsletter / news-digest requests."
    ),
    edges=[
        (
            START,
            stash_user_query_node,      # save user text → state["user_query"]
            intent_classifier_agent,    # outputs "newsletter" or "chat"
            route_intent_node,          # Event(route=...)
        ),
        (
            route_intent_node,
            {
                "newsletter": newsletter_pipeline,
                "chat": chat_agent,
            },
        ),
    ],
)

# App wrapper enables resumable HITL (pause/resume without replaying everything).
# Prefer exporting both root_agent and app — ADK loaders look for either.
app = App(
    name="newsletter",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
