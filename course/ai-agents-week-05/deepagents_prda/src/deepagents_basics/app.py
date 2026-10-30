#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

import sys
import uuid
from pathlib import Path

# Add current directory to path for direct module imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Import from local modules
from deepagents_basics.agent import create_prda_agent
from deepagents_basics.utils import message_text, slugify

# ---------------------- Page config ----------------------
st.set_page_config(
    page_title="PRDA - Product R&D Assistant",
    page_icon="🧠",
    layout="wide",
)

# ---------------------- Session state ----------------------
if "store" not in st.session_state:
    from langgraph.store.memory import InMemoryStore
    st.session_state.store = InMemoryStore()

if "agent" not in st.session_state:
    # You can change the default model here if you like
    st.session_state.agent = create_prda_agent(
        model="openai:gpt-5-mini",
        store=st.session_state.store
    )
if "history" not in st.session_state:
    st.session_state.history = []  # store past runs (product_name, slug, summary)


# ---------------------- Helper functions ----------------------
def build_prompt(product_name: str, product_desc: str, target_users: str, constraints: str, slug: str) -> str:
    """Compose the user prompt sent to the Deep Agent - matches exact specification."""
    base = [
        f"I want to build a product called \"{product_name}\".",
        f"Use slug \"{slug}\" for all filesystem paths.",
        "",
        "Details:",
    ]
    if product_desc.strip():
        base.append(f"- Product description: {product_desc}")
    if target_users.strip():
        base.append(f"- Target users: {target_users}")
    if constraints.strip():
        base.append(f"- Constraints: {constraints}")

    base.append("")
    base.append("Please:")
    base.append("1. Analyze the market and competitors.")
    base.append("2. Extract key insights.")
    base.append("3. Propose the technical architecture.")
    base.append(f"4. Generate the PRD and store it at /memories/products/{slug}/prd.md.")
    base.append("5. Also create supporting files:")
    base.append(f"   - /memories/products/{slug}/insights.md")
    base.append(f"   - /memories/products/{slug}/research.md")
    base.append(f"   - /memories/products/{slug}/architecture.md")
    base.append(f"   - /memories/products/{slug}/market_summary.md")
    base.append("")
    base.append("Finally, return ONLY the complete PRD content (no summary, no file paths listing).")
    base.append("The PRD should start directly with '# Product Requirements Document' header.")

    return "\n".join(base)


def _shorten(value, limit: int = 80) -> str:
    """One-line, length-capped rendering of any value for the live log."""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _log_update(log, where: str, update) -> None:
    """Write human-readable lines for one graph-node update to the status log.

    The deep agent is a LangGraph graph, so streaming with
    stream_mode="updates" yields {node: update} dicts; each update may carry
    new messages. AI messages with tool_calls are the interesting ones — they
    are the agent *acting* (planning, delegating, searching, writing files).
    """
    if not isinstance(update, dict):
        return
    for msg in update.get("messages", []) or []:
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                name = tc.get("name", "?")
                args = tc.get("args", {}) or {}
                if name == "task":
                    target = args.get("subagent_type") or _shorten(args.get("description", ""), 50)
                    log.write(f"🤝 {where}: delegating to **{target}**")
                elif name == "write_todos":
                    todos = args.get("todos", []) or []
                    done = sum(1 for td in todos if isinstance(td, dict) and td.get("status") == "completed")
                    log.write(f"📋 {where}: plan updated — {done}/{len(todos)} steps done")
                elif name == "internet_search":
                    log.write(f"🔎 {where}: searching “{_shorten(args.get('query', ''), 60)}”")
                elif name in ("write_file", "edit_file", "read_file", "ls", "glob", "grep"):
                    path = args.get("file_path") or args.get("path") or ""
                    log.write(f"📁 {where}: `{name}` {path}")
                else:
                    log.write(f"🛠️ {where}: `{name}`({_shorten(args, 60)})")
        elif type(msg).__name__ == "ToolMessage" and getattr(msg, "status", None) == "error":
            log.write(f"⚠️ {where}: tool error — {_shorten(getattr(msg, 'content', ''), 90)}")


# ---------------------- Sidebar ----------------------
with st.sidebar:
    st.markdown("## 🧠 PRDA Controls")
    st.markdown(
        "This app uses a **Deep Agent** with planning, filesystem, subagents, "
        "and long-term memory to behave like a small product team."
    )
    st.markdown("---")
    st.markdown("### ℹ️ How to use")
    st.markdown(
        "1. Enter a product idea on the right\n"
        "2. Click **Generate PRD**\n"
        "3. Watch the agent run the full pipeline\n"
        "4. Scroll to see the complete PRD document\n"
    )
    st.markdown("---")
    st.markdown("### ⚙️ Model")
    st.caption("The model is configured in `create_prda_agent()` in `agent.py`.")
    st.markdown("You can change it there to use OpenAI / Anthropic / others.")


# ---------------------- Main layout ----------------------
st.markdown(
    "<h1 style='margin-bottom:0.2rem;'>🧠 Product Research & Development Assistant</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:gray; margin-top:0;'>Powered by DeepAgents – planning, memory, subagents, and HITL.</p>",
    unsafe_allow_html=True,
)

# ---------------------- Main content ----------------------
col_input, col_output = st.columns([1.1, 1.4], gap="large")

# ---------------------- Left column: Input form ----------------------
with col_input:
    st.markdown("### ✍️ Define your product")

    with st.container():
        product_name = st.text_input(
            "Product name",
            placeholder="e.g. AI Budgeting Assistant for College Students",
        )

        product_desc = st.text_area(
            "Short product description",
            placeholder="What does this product do? What problem does it solve?",
            height=120,
        )

        target_users = st.text_area(
            "Target users / segments",
            placeholder="e.g. college students in India, first-time budgeters, etc.",
            height=80,
        )

        constraints = st.text_area(
            "Constraints / notes (optional)",
            placeholder="e.g. must be mobile-first, low-cost, offline-friendly, etc.",
            height=80,
        )

        st.markdown("---")
        run_button = st.button("🚀 Generate PRD", type="primary", use_container_width=True)

    if st.session_state.history:
        st.markdown("### 📜 Previous runs")
        for i, h in enumerate(reversed(st.session_state.history), start=1):
            with st.expander(f"{i}. {h['product_name']}  (slug: {h['slug']})", expanded=False):
                st.markdown(h["summary"])


# ---------------------- Right column: Output / Run view ----------------------
with col_output:
    st.markdown("### 📡 Run status & results")

    if run_button:
        if not product_name.strip():
            st.warning("Please enter a product name before running.")
        else:
            slug = slugify(product_name)

            agent = st.session_state.agent
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}

            user_prompt = build_prompt(
                product_name=product_name,
                product_desc=product_desc,
                target_users=target_users,
                constraints=constraints,
                slug=slug,
            )

            # Stream the run instead of one blocking invoke, so the UI shows
            # what the agent is doing while it works. subgraphs=True also
            # surfaces events from INSIDE subagent runs (e.g. the research
            # agent's searches), not just the orchestrator's own moves.
            final_content = "(No content returned)"
            with st.status("Running the Deep Agent pipeline…", expanded=True) as status_log:
                try:
                    for item in agent.stream(
                        {"messages": [{"role": "user", "content": user_prompt}]},
                        config=config,
                        stream_mode="updates",
                        subgraphs=True,
                    ):
                        namespace, update = item if isinstance(item, tuple) else ((), item)
                        where = "orchestrator" if not namespace else "subagent"
                        for _node, node_update in (update or {}).items():
                            _log_update(status_log, where, node_update)

                    # The checkpointer holds the final state for this thread.
                    # message_text() flattens block-list content (gpt-5 models
                    # answer via the Responses API, whose messages carry
                    # [{"type": "text", ...}] blocks rather than a plain str).
                    messages = agent.get_state(config).values.get("messages", [])
                    if messages:
                        final_content = message_text(messages[-1]) or final_content
                    status_log.update(label="✅ Pipeline complete", state="complete", expanded=False)
                except Exception as exc:
                    status_log.update(label=f"Pipeline failed: {_shorten(exc, 120)}", state="error")
                    raise

            # Store in history
            st.session_state.history.append(
                {
                    "product_name": product_name.strip(),
                    "slug": slug,
                    "summary": final_content,
                }
            )

            # Display the PRD directly - clean output
            st.success("✅ PRD Generation Complete!")

            st.markdown("---")

            # Display the PRD content directly (the agent should return only the PRD)
            # Clean the content - remove any preamble if present
            prd_content = final_content.strip()

            # If the content starts with common preambles, try to find the actual PRD start
            prd_start_markers = [
                "# Product Requirements Document",
                "## 1. Executive Summary",
                "# PRD:",
            ]

            for marker in prd_start_markers:
                if marker in prd_content:
                    idx = prd_content.find(marker)
                    if idx > 0:
                        # There's content before the PRD, extract just the PRD
                        prd_content = prd_content[idx:]
                    break

            # Durability: the agent's /memories/ store is in-memory and dies
            # with this process, so also persist the PRD to disk and offer a
            # download -- a 15-minute artifact should survive a restart.
            out_dir = Path(__file__).resolve().parents[2] / "outputs"
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / f"{slug}_prd.md"
            out_path.write_text(prd_content, encoding="utf-8")
            st.caption(f"Saved a copy to `outputs/{out_path.name}`")
            st.download_button(
                "⬇️ Download PRD (markdown)",
                prd_content,
                file_name=out_path.name,
                mime="text/markdown",
            )

            # Display the PRD with nice formatting
            st.markdown(prd_content)

    else:
        st.info("Fill in the product details on the left and click **Generate PRD** to get started.")
