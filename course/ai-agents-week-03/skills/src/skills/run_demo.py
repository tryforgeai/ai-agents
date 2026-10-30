# =============================================================================
# Filename: run_demo.py
#
# Short Description: Interactive demo runner for the agent skills ADK agent.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Run the agent skills demo against sample prompts (requires LLM endpoint).

How to use in labs
-----------------
Two modes for instructors:

1. **No LLM** — ``--list-skills`` prints manifest + disk discovery.
   Use this on day 1 to explain library structure before API costs.

2. **With LLM** — pass a prompt to watch ADK tool calls:
   search/list_skills → load_skill → load_skill_resource / run_skill_script.
   Add ``--lazy`` to use registry-only loading (no preload at startup).

Sample prompts in ``_SAMPLE_PROMPTS`` intentionally target different skills
(transcript-cleaner, commit-message) so students see routing in action.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types
from loguru import logger

from skills.agent_factory import build_app as build_app_with_strategy
from skills.skill_loader import snapshot_library

load_dotenv()

_USER_ID = "demo_user"
_SESSION_ID = "demo_session"

# Deliberately diverse prompts — discuss which skill *should* fire for each.
_SAMPLE_PROMPTS = (
    "Clean this noisy transcript: 'So group O optimizes logic for L L M training.'",
    (
        "Draft a commit message for: added filesystem skill registry and "
        "governor validation tests."
    ),
    (
        "Summarize proximal policy optimization in about 100 words with a title, "
        "body, and 3-4 references for further reading."
    ),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run agent skills ADK demo. See docs/LEARNING_GUIDE.md.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="User message (default: run built-in samples).",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Print library snapshot and exit (no LLM required).",
    )
    parser.add_argument(
        "--lazy",
        action="store_true",
        help="Use registry-only lazy loading (no preload at startup).",
    )
    return parser.parse_args()


def _skill_toolset_from_agent(*, agent: LlmAgent) -> SkillToolset:
    """Return the agent's ``SkillToolset`` for startup diagnostics."""
    for tool in agent.tools:
        if isinstance(tool, SkillToolset):
            return tool
    raise TypeError("Expected SkillToolset on agent.tools")


def _format_tool_call(*, tool_name: str, args: dict[str, Any]) -> str:
    """Render a compact tool-call line for CLI tracing."""
    if tool_name == "search_skills":
        query = str(args.get("query", ""))
        if len(query) > 72:
            query = f"{query[:69]}..."
        return f"{tool_name}(query={query!r})"
    if tool_name == "load_skill":
        return f"{tool_name}(skill_name={args.get('skill_name')!r})"
    if tool_name in {"load_skill_resource", "run_skill_script"}:
        return (
            f"{tool_name}(skill_name={args.get('skill_name')!r}, "
            f"file_path={args.get('file_path')!r})"
        )
    if tool_name in {
        "scaffold_new_skill",
        "author_skill_procedure",
        "apply_skill_procedure_delta",
        "refresh_skill_library",
    }:
        return f"{tool_name}({json.dumps(args, sort_keys=True)})"
    if not args:
        return f"{tool_name}()"
    return f"{tool_name}({json.dumps(args, sort_keys=True)})"


def _tool_call_hint(*, tool_name: str, lazy: bool, args: dict[str, Any]) -> str:
    """Explain how the call relates to preload vs lazy loading."""
    if tool_name == "list_skills":
        if lazy:
            return "catalog may be empty in lazy mode"
        return "reads the startup-preloaded catalog"
    if tool_name == "search_skills":
        return "lazy discovery via registry + embeddings"
    if tool_name == "load_skill":
        skill_name = args.get("skill_name", "?")
        if lazy:
            return f"on-demand load of {skill_name!r} from disk"
        return f"procedure for {skill_name!r} (skill preloaded at startup)"
    if tool_name == "load_skill_resource":
        return "L3 resource from skill folder"
    if tool_name == "run_skill_script":
        return "executes bundled script"
    if tool_name == "scaffold_new_skill":
        return "creates a new skill folder from template"
    if tool_name == "author_skill_procedure":
        return "writes Procedure and Done when with validation"
    if tool_name == "apply_skill_procedure_delta":
        return "governed incremental procedure update from follow-up"
    if tool_name == "refresh_skill_library":
        return "rescan library after scaffolding"
    return ""


def _log_loading_strategy(*, agent: LlmAgent, lazy: bool) -> None:
    """Log how many skills are in memory before the first user prompt."""
    toolset = _skill_toolset_from_agent(agent=agent)
    if lazy:
        logger.info("=== Loading strategy: LAZY (registry-only) ===")
        logger.info("Startup: 0 skills in agent memory")
        logger.info("Skills load from disk when the agent calls load_skill")
        logger.info(
            "Discovery: search_skills (semantic search; list_skills may be empty)"
        )
        return

    names = sorted(toolset._skills.keys())
    logger.info("=== Loading strategy: PRELOAD (eager) ===")
    logger.info("Startup: {} skills loaded into memory", len(names))
    for name in names:
        logger.info("  preloaded: {}", name)
    logger.info("Discovery: list_skills (instant catalog from startup preload)")


def _log_tool_event(*, event: Event, lazy: bool) -> None:
    """Log skill tool calls as they happen during the agent turn."""
    for function_call in event.get_function_calls():
        args = dict(function_call.args) if function_call.args else {}
        hint = _tool_call_hint(tool_name=function_call.name, lazy=lazy, args=args)
        line = _format_tool_call(tool_name=function_call.name, args=args)
        if hint:
            logger.info("Tool → {} — {}", line, hint)
        else:
            logger.info("Tool → {}", line)


async def _run_prompt(*, runner: Runner, prompt: str, lazy: bool) -> None:
    """Send one user message and log tool calls plus the agent's final reply."""
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    logger.info("User: {}", prompt)
    events = runner.run_async(
        user_id=_USER_ID,
        session_id=_SESSION_ID,
        new_message=message,
    )
    async for event in events:
        _log_tool_event(event=event, lazy=lazy)
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text or ""
            logger.info("Agent: {}", text)


async def _main_async(*, prompt: str | None, lazy: bool = False) -> None:
    """Create session, build agent, run one or more prompts."""
    session_service = InMemorySessionService()
    app = build_app_with_strategy(preload=not lazy)
    await session_service.create_session(
        app_name=app.name,
        user_id=_USER_ID,
        session_id=_SESSION_ID,
    )
    _log_loading_strategy(agent=app.root_agent, lazy=lazy)
    runner = Runner(app=app, session_service=session_service)
    prompts = [prompt] if prompt else list(_SAMPLE_PROMPTS)
    for item in prompts:
        await _run_prompt(runner=runner, prompt=item, lazy=lazy)


def main() -> None:
    """CLI entry point."""
    args = _parse_args()
    if args.list_skills:
        snap = snapshot_library()
        logger.info(
            "Manifest v{} maturity L{}", snap.manifest_version, snap.maturity_level
        )
        logger.info("--- Curated (manifest.yaml) ---")
        for entry in snap.entries:
            logger.info(
                "  {} v{} [{}] {}",
                entry.name,
                entry.version,
                entry.pattern,
                entry.status,
            )
        logger.info("--- Discovered on disk (L1 scan) ---")
        for name, fm in snap.discovered.items():
            logger.info("  {} — {}", name, fm.description[:80])
        return

    if not os.getenv("LLM_API_BASE") and not os.getenv("OPENAI_API_KEY"):
        logger.warning("Set OPENAI_API_KEY (hosted default) or LLM_API_BASE for LLM calls.")

    try:
        asyncio.run(_main_async(prompt=args.prompt, lazy=args.lazy))
    except Exception as exc:
        logger.error("Demo failed: {}", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
