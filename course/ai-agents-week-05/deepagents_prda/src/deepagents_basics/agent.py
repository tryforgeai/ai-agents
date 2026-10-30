#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
PRDA Agent Factory

Main entry point for creating and running the PRDA DeepAgent.
"""

import uuid

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents_basics.backend import make_backend
from deepagents_basics.prompts import MAIN_SYSTEM_PROMPT
from deepagents_basics.subagents import build_subagents
from deepagents_basics.tools import internet_search
from deepagents_basics.utils import message_text, slugify


def create_prda_agent(model: str = "openai:gpt-5-mini", store=None):
    """Create the PRDA DeepAgent with streamlined prompts.

    Args:
        model: The model identifier (e.g., "openai:gpt-5-mini"; any
            init_chat_model "provider:model" string works, so a self-hosted
            OpenAI-compatible server is a ChatOpenAI(base_url=...) instance)
            for example:ChatOpenAI(model="openai/gpt-oss-20b", base_url="http://10.0.10.70:8000/v1", api_key="not-needed")
        store: Optional LangGraph store for persistent memory. If None, creates InMemoryStore.

    Returns:
        Configured DeepAgent ready for PRD generation
    """
    if store is None:
        store = InMemoryStore()

    checkpointer = MemorySaver()
    subagents = build_subagents()

    agent = create_deep_agent(
        model=model,
        system_prompt=MAIN_SYSTEM_PROMPT,
        backend=make_backend(store),   # deepagents >= 0.7: an instance, not a factory
        store=store,
        subagents=subagents,
        tools=[internet_search],
        checkpointer=checkpointer,
    )

    return agent


def demo_prda_run():
    """Demo run of PRDA agent."""
    agent = create_prda_agent()
    product_name = "AI Budgeting Assistant for College Students"
    product_slug = slugify(product_name)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_prompt = (
        f"I want to build a product called '{product_name}'.\n"
        f"Use slug '{product_slug}' for all filesystem paths.\n\n"
        "Please:\n"
        "1. Research market and competitors\n"
        "2. Extract key insights and create personas\n"
        "3. Design technical architecture\n"
        "4. Create validation framework and business model\n"
        "5. Design go-to-market strategy\n"
        "6. Write comprehensive PRD\n"
        f"7. Store PRD at /memories/products/{product_slug}/prd.md\n"
        "8. Return summary and complete PRD content"
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_prompt}]},
        config=config,
    )

    content = message_text(result["messages"][-1])

    print("\n=== FINAL RESPONSE ===\n")
    print(content)


if __name__ == "__main__":
    demo_prda_run()
