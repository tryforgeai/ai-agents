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
Human-in-the-loop (HITL) after the editorial draft.

ADK pattern:
1) ask_human_review yields RequestInput → workflow pauses
2) UI/CLI sends FunctionResponse for adk_request_input
3) That reply becomes ask_human_review's output → route_human_review
4) Event(route="approve"|"revise") picks the next edge
"""

from typing import Any

from google.adk import Event
from google.adk.events import RequestInput
from google.adk.workflow import FunctionNode


def _parse_review_response(response: Any) -> tuple[str, str]:
    """Normalize web/CLI/Streamlit payloads into (decision, feedback)."""
    if response is None:
        return "approve", ""

    if isinstance(response, str):
        text = response.strip()
        lower = text.lower()
        if lower in {"approve", "a", "yes", "y", "ok"}:
            return "approve", ""
        if lower.startswith("revise"):
            _, _, rest = text.partition(":")
            feedback = rest.strip() or text
            if feedback.lower() in {"revise", "r"}:
                feedback = "Please improve clarity, flow, and structure."
            return "revise", feedback
        if lower in {"revise", "r", "no", "n"}:
            return "revise", "Please improve clarity, flow, and structure."
        return "revise", text  # free text = revision notes

    if isinstance(response, dict):
        # ADK often wraps plain chat as {"result": "approve"}
        if "result" in response and len(response) == 1:
            return _parse_review_response(response["result"])

        decision_raw = str(response.get("decision", "")).strip().lower()
        feedback = str(response.get("feedback", "") or "").strip()
        if decision_raw in {"approve", "a", "yes", "y", "ok"}:
            return "approve", ""
        if decision_raw in {"revise", "r", "no", "n"}:
            return "revise", feedback or "Please improve clarity, flow, and structure."
        if feedback:
            return "revise", feedback
        return "approve", ""

    return "approve", ""


def ask_human_review(
    node_input: Any = None,
    editorial_draft: str = "",
    review_count: int = 0,
):
    """Pause the graph and show the full draft to the human."""
    draft = (editorial_draft or str(node_input or "")).strip()

    # Unique interrupt_id per review round (needed if revise loops back)
    return RequestInput(
        interrupt_id=f"editorial_review_{review_count}",
        message=(
            "Review the editorial draft below.\n\n"
            "Reply with exactly one of:\n"
            "  • approve\n"
            "  • revise: <your feedback>\n\n"
            f"{draft}"
        ),
        payload={"editorial_draft": editorial_draft or draft},
    )


def route_human_review(
    node_input: Any = None,
    review_count: int = 0,
) -> Event:
    """Turn the human reply into a route + optional human_feedback in state."""
    decision, feedback = _parse_review_response(node_input)
    route = "approve" if decision == "approve" else "revise"
    state_update: dict[str, Any] = {
        "review_count": review_count + 1,
        "human_feedback": feedback if route == "revise" else "",
    }
    return Event(
        output={"decision": decision, "feedback": feedback},
        route=route,
        state=state_update,
    )


# Default: do not re-run ask_human_review on resume; reply becomes its output.
ask_human_review_node = FunctionNode(name="ask_human_review", func=ask_human_review)
route_human_review_node = FunctionNode(name="route_human_review", func=route_human_review)

human_review_agent = ask_human_review_node  # alias for older imports
