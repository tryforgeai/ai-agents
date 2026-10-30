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
CLI runner — same HITL resume pattern as Streamlit, but in the terminal.

Study this file to see the ADK resume handshake:
  1) run until you see function_call name == adk_request_input
  2) reply with FunctionResponse(id=..., name=adk_request_input, response={...})
  3) call runner.run_async again with that message

Usage: uv run src/newsletter/agent_runner.py
"""

from __future__ import annotations

import asyncio
import json

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from newsletter.agent import app

APP_NAME = "newsletter"
USER_ID = "12345"
SESSION_ID = "123344"
REQUEST_INPUT_TOOL = "adk_request_input"


async def setup_session_and_runner():
    """Create an in-memory session and a Runner bound to the resumable App."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(app=app, session_service=session_service)
    return session_service, session, runner


def _extract_request_input(event):
    """Return the adk_request_input function call from an event, if present."""
    if not event.content or not event.content.parts:
        return None
    for part in event.content.parts:
        function_call = getattr(part, "function_call", None)
        if function_call and function_call.name == REQUEST_INPUT_TOOL:
            return function_call
    return None


def _prompt_human_review(function_call) -> dict:
    """
    Collect approve / revise from the terminal.

    Payload shape ``{"result": "..."}`` matches ADK web/CLI resume handling.
    """
    args = function_call.args or {}
    message = args.get("message") or "Please review the editorial draft."
    print("\n" + "=" * 72)
    print("HUMAN REVIEW REQUIRED")
    print("=" * 72)
    print(message)
    print("=" * 72)

    while True:
        decision = input("Decision [approve / revise: feedback]: ").strip()
        lower = decision.lower()
        if lower in {"approve", "a", "yes", "y", "ok"}:
            return {"result": "approve"}
        if lower.startswith("revise") or lower in {"r", "no", "n"}:
            if ":" in decision:
                return {"result": decision}
            feedback = input("Revision feedback: ").strip()
            if feedback:
                return {"result": f"revise: {feedback}"}
            return {"result": "revise: Please improve clarity, flow, and structure."}
        print("Please enter 'approve' or 'revise: <feedback>'.")


def _resume_message(function_call, response_payload: dict) -> types.Content:
    """Build the FunctionResponse Content that resumes a RequestInput pause."""
    return types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=function_call.id,
                    name=REQUEST_INPUT_TOOL,
                    response=response_payload,
                )
            )
        ],
    )


async def call_agent_async(query: str) -> None:
    """Run until complete, prompting at each human-review pause."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    session_service, session, runner = await setup_session_and_runner()

    print(f"Initial session state: {session.state}")
    pending_message = content

    while True:
        request_input_call = None
        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=pending_message,
        )

        async for event in events:
            maybe_request = _extract_request_input(event)
            if maybe_request:
                request_input_call = maybe_request

            if event.is_final_response():
                if event.content and event.content.parts:
                    text_part = next(
                        (p.text for p in event.content.parts if p.text), None
                    )
                    print("Agent Response:", text_part or "[No textual response]")
                else:
                    print("Agent Response: [Empty or non-text response]")

        if not request_input_call:
            break

        human_payload = _prompt_human_review(request_input_call)
        print(f"Resuming with: {json.dumps(human_payload)}")
        pending_message = _resume_message(request_input_call, human_payload)

    updated_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print(f"Updated session state keys: {list(updated_session.state.keys())}")

    final_markdown = updated_session.state.get("final_markdown_output")
    if final_markdown:
        print("\n=== FINAL NEWSLETTER (Markdown) ===\n")
        print(final_markdown)
    else:
        print("No final_markdown_output found (chat path or incomplete run).")


if __name__ == "__main__":
    # Prefixed so the intent router chooses the newsletter pipeline.
    asyncio.run(call_agent_async("Generate a newsletter about Deep Neural Networks"))
