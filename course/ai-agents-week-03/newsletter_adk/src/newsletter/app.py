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
Streamlit UI (student-friendly front end for the same ``app`` as ADK web).

Shows three ideas from the pipeline:
1) Intent routing — "Generate Newsletter" forces the newsletter path
2) HITL — when RequestInput fires, show approve/revise and resume
3) Chat path — simple questions skip Collect→Format

Requires MCP: uv run src/newsletter/mcp/fastmcp_server.py
"""

from __future__ import annotations

import asyncio
import threading
import uuid
from typing import Any, Coroutine

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from newsletter.agent import app


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_NAME = "newsletter"
USER_ID = "streamlit_user"
REQUEST_INPUT_TOOL = "adk_request_input"


# ---------------------------------------------------------------------------
# Async bridge
# ---------------------------------------------------------------------------

@st.cache_resource
def _background_loop() -> asyncio.AbstractEventLoop:
    """
    One long-lived event loop for the whole Streamlit process.

    The agents (and their MCP connections) are module-level objects shared by
    every rerun and browser tab. MCP sessions are bound to the loop that opened
    them, so calling asyncio.run() per click (a new loop each time) breaks them.
    """
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, name="adk-event-loop", daemon=True).start()
    return loop


def _run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run a coroutine on the shared loop and block until it finishes."""
    return asyncio.run_coroutine_threadsafe(coro, _background_loop()).result()


# ---------------------------------------------------------------------------
# Session / runner helpers
# ---------------------------------------------------------------------------

def _ensure_runtime() -> None:
    """Create (once) an in-memory ADK session + Runner bound to the resumable App."""
    if "session_service" in st.session_state and "runner" in st.session_state:
        return

    session_service = InMemorySessionService()
    session_id = f"st-{uuid.uuid4().hex[:12]}"

    _run_async(
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    )

    st.session_state.session_service = session_service
    st.session_state.session_id = session_id
    st.session_state.runner = Runner(app=app, session_service=session_service)


def _reset_runtime() -> None:
    """Drop the current ADK session so the next run starts clean."""
    for key in (
        "session_service",
        "session_id",
        "runner",
        "pending_request_input",
        "last_chat_reply",
        "final_markdown",
        "run_status",
    ):
        st.session_state.pop(key, None)


def _extract_request_input(event) -> Any | None:
    """Return an adk_request_input function call from an event, if any."""
    if not event.content or not event.content.parts:
        return None
    for part in event.content.parts:
        function_call = getattr(part, "function_call", None)
        if function_call and function_call.name == REQUEST_INPUT_TOOL:
            return function_call
    return None


def _extract_text(event) -> str | None:
    """Best-effort plain text from a final model event."""
    if not event.content or not event.content.parts:
        return None
    return next((p.text for p in event.content.parts if p.text), None)


def _resume_content(function_call, result_text: str) -> types.Content:
    """Build the FunctionResponse message ADK expects to resume HITL."""
    return types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=function_call.id,
                    name=REQUEST_INPUT_TOOL,
                    # Plain text under "result" matches ADK web/CLI resume shape.
                    response={"result": result_text},
                )
            )
        ],
    )


async def _run_until_pause_or_done(
    runner: Runner,
    session_service: InMemorySessionService,
    session_id: str,
    message: types.Content,
) -> dict[str, Any]:
    """
    Drive the agent until it either:
    - pauses for human review (adk_request_input), or
    - finishes the turn.

    Runs on the background loop thread, where st.session_state is not available,
    so everything it needs is passed in.
    """
    request_input_call = None
    last_text = None

    events = runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    )
    async for event in events:
        maybe_request = _extract_request_input(event)
        if maybe_request:
            request_input_call = maybe_request
        if event.is_final_response():
            text = _extract_text(event)
            if text:
                last_text = text

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    state = session.state if session else {}

    return {
        "request_input": request_input_call,
        "chat_text": last_text,
        "final_markdown": state.get("final_markdown_output"),
        "intent": state.get("intent"),
        "state_keys": list(state.keys()),
    }


def run_turn(message: types.Content) -> dict[str, Any]:
    """Sync wrapper for Streamlit button handlers."""
    return _run_async(
        _run_until_pause_or_done(
            st.session_state.runner,
            st.session_state.session_service,
            st.session_state.session_id,
            message,
        )
    )


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Newsletter Generator", page_icon="📰", layout="wide")

st.title("📰 AI Newsletter Generator")
st.caption(
    "Uses intent routing: simple questions get a short chat answer; "
    "newsletter requests run the full Collect → Validate → Analyze → Write pipeline "
    "(with optional human review)."
)

# Sidebar: session controls
with st.sidebar:
    st.header("Session")
    if st.button("Reset session", use_container_width=True):
        _reset_runtime()
        st.success("Session cleared. Next run starts fresh.")
    st.markdown(
        "Make sure MCP is running:\n\n"
        "`uv run src/newsletter/mcp/fastmcp_server.py`"
    )

# Primary: newsletter generation (forces newsletter wording so the router starts the pipeline)
st.subheader("Generate a newsletter")
topic = st.text_input(
    "Topic",
    placeholder="e.g. Deep Neural Networks",
    key="topic_input",
)

col_gen, _ = st.columns([1, 3])
with col_gen:
    generate_clicked = st.button("Generate Newsletter", type="primary")

if generate_clicked:
    if not topic.strip():
        st.warning("Please enter a topic before generating.")
    else:
        _ensure_runtime()
        # Phrase the request so the intent classifier routes to the newsletter pipeline.
        user_text = f"Generate a newsletter about {topic.strip()}"
        with st.spinner("Running newsletter pipeline… this can take a few minutes"):
            result = run_turn(
                types.Content(role="user", parts=[types.Part(text=user_text)])
            )

        if result["request_input"]:
            st.session_state.pending_request_input = result["request_input"]
            st.session_state.run_status = "awaiting_review"
            st.info("Editorial draft is ready for human review below.")
        elif result["final_markdown"]:
            st.session_state.final_markdown = result["final_markdown"]
            st.session_state.run_status = "done"
            st.session_state.pending_request_input = None
        else:
            # Chat path or incomplete pipeline
            st.session_state.last_chat_reply = result["chat_text"] or (
                "No newsletter markdown was produced. "
                "Try a clearer topic, or check MCP / API keys."
            )
            st.session_state.run_status = "chat"
            st.session_state.pending_request_input = None

# Human-in-the-loop review panel (shown when the pipeline pauses)
if st.session_state.get("run_status") == "awaiting_review" and st.session_state.get(
    "pending_request_input"
):
    st.markdown("---")
    st.subheader("🧑 Human review")
    fc = st.session_state.pending_request_input
    args = getattr(fc, "args", None) or {}
    st.markdown(args.get("message") or "Review the editorial draft.")

    decision = st.radio(
        "Decision",
        options=["approve", "revise"],
        horizontal=True,
        key="review_decision",
    )
    feedback = ""
    if decision == "revise":
        feedback = st.text_area(
            "Revision feedback",
            placeholder="e.g. Shorten the intro and keep a neutral tone",
            key="review_feedback",
        )

    if st.button("Submit review", type="primary"):
        if decision == "revise" and not feedback.strip():
            st.warning("Please provide revision feedback, or choose approve.")
        else:
            result_text = "approve" if decision == "approve" else f"revise: {feedback.strip()}"
            with st.spinner("Resuming pipeline…"):
                result = run_turn(_resume_content(fc, result_text))

            if result["request_input"]:
                # Another revision cycle asked for review again
                st.session_state.pending_request_input = result["request_input"]
                st.session_state.run_status = "awaiting_review"
                st.info("Updated draft ready — review again.")
            else:
                st.session_state.pending_request_input = None
                st.session_state.final_markdown = result["final_markdown"]
                st.session_state.run_status = "done" if result["final_markdown"] else "chat"
                if not result["final_markdown"]:
                    st.session_state.last_chat_reply = result["chat_text"] or (
                        "Pipeline finished without final_markdown_output."
                    )
                st.rerun()

# Optional: ask a simple question without forcing the newsletter pipeline
st.markdown("---")
st.subheader("Ask a simple question")
st.caption("Uses the same intent router — greetings / definitions stay on the chat path.")
question = st.text_input("Question", placeholder="e.g. What is a neural network?", key="chat_input")
if st.button("Ask"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        _ensure_runtime()
        with st.spinner("Thinking…"):
            result = run_turn(
                types.Content(role="user", parts=[types.Part(text=question.strip())])
            )
        if result["request_input"]:
            st.session_state.pending_request_input = result["request_input"]
            st.session_state.run_status = "awaiting_review"
            st.info("Unexpected review pause — use the Human review section above.")
        elif result["final_markdown"]:
            st.session_state.final_markdown = result["final_markdown"]
            st.session_state.run_status = "done"
        else:
            st.session_state.last_chat_reply = result["chat_text"] or "No reply."
            st.session_state.run_status = "chat"

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

status = st.session_state.get("run_status")
if status == "done" and st.session_state.get("final_markdown"):
    st.markdown("---")
    st.subheader("Final Markdown")
    st.markdown(st.session_state.final_markdown, unsafe_allow_html=False)
elif status == "chat" and st.session_state.get("last_chat_reply"):
    st.markdown("---")
    st.subheader("Assistant reply")
    st.write(st.session_state.last_chat_reply)
