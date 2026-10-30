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
Intent router — keep the expensive newsletter pipeline off simple questions.

Pattern students should notice:
  FunctionNode (stash) → LlmAgent (classify) → FunctionNode (Event.route)
    ├─ "newsletter" → NewsletterFlow
    └─ "chat"       → chat_agent
"""

from typing import Any

from google.adk import Event
from google.adk.agents import LlmAgent
from google.adk.workflow import FunctionNode
from google.genai import types

from newsletter.settings import llm

INTENT_CLASSIFIER_INSTRUCTION = """
You classify the user's message for a newsletter app.

User message:
{user_query}

Reply with EXACTLY one word:
- newsletter — they are asking you to PRODUCE a newsletter, news digest, or
  news roundup about a specific topic right now
- chat — anything else: greetings, definitions, general questions, and questions
  ABOUT newsletters or how to use this app

Examples:
- "Generate a newsletter about quantum computing" → newsletter
- "Give me this week's AI news digest" → newsletter
- "What's the latest news on EV batteries? Summarize it for me" → newsletter
- "How do I ask you for a newsletter?" → chat
- "What is a newsletter?" → chat
- "What is a neural network?" → chat
- "Hi!" → chat

Do not explain. Output only: newsletter OR chat
"""

CHAT_INSTRUCTION = """
You are a helpful assistant for a newsletter generation app.

User message:
{user_query}

Answer briefly. If they want a full newsletter, tell them to ask e.g.
"Generate a newsletter about Deep Neural Networks".
Do not invent live news headlines.
"""


def _content_to_text(node_input: Any) -> str:
    """Workflow node_input may be str or google.genai Content — normalize to text."""
    if node_input is None:
        return ""
    if isinstance(node_input, str):
        return node_input.strip()
    if isinstance(node_input, types.Content):
        parts = [
            part.text
            for part in (node_input.parts or [])
            if getattr(part, "text", None)
        ]
        return "\n".join(parts).strip()
    return str(node_input).strip()


def stash_user_query(node_input: Any = None) -> Event:
    """Put the original user text in state so later agents can use {user_query}."""
    text = _content_to_text(node_input)
    return Event(state={"user_query": text}, output=text)


def route_intent(node_input: Any = None, user_query: str = "") -> Event:
    """
    Map classifier output → graph route.

    Important: ``output`` must be the *original topic*, not the word "newsletter",
    so the collector still searches for what the user asked about.
    """
    raw = _content_to_text(node_input).lower()
    tokens = raw.replace("`", "").replace('"', "").strip().split()
    intent = tokens[0] if tokens else "chat"

    if intent not in {"newsletter", "chat"}:
        # Soft fallback if the model answers in a full sentence
        if any(k in raw for k in ("newsletter", "news digest", "latest news", "summarize news")):
            intent = "newsletter"
        else:
            intent = "chat"

    original = (user_query or "").strip() or _content_to_text(node_input)
    return Event(route=intent, output=original)


stash_user_query_node = FunctionNode(name="stash_user_query", func=stash_user_query)

intent_classifier_agent = LlmAgent(
    name="intent_classifier_agent",
    model=llm,
    mode="single_turn",  # required when an LlmAgent is a Workflow node
    include_contents="none",  # we pass text via {user_query} instead
    description="Classifies newsletter vs chat intent.",
    instruction=INTENT_CLASSIFIER_INSTRUCTION,
    output_key="intent",
)

route_intent_node = FunctionNode(name="route_intent", func=route_intent)

chat_agent = LlmAgent(
    name="chat_agent",
    model=llm,
    mode="single_turn",
    description="Answers simple questions without running the newsletter pipeline.",
    instruction=CHAT_INSTRUCTION,
)
