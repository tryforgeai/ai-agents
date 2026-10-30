# =============================================================================
# Filename: agent_factory.py
#
# Short Description: Shared builders for preload vs lazy skill-loading agents.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Construct ADK agents that differ only in skill loading strategy.

Two strategies (compare in ``adk web src/skills/agents``):

- **Preload** — ``load_all_skills()`` at startup; ``list_skills`` is instant.
- **Lazy** — registry only; ``search_skills`` + ``load_skill`` fetch from disk.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.tools.skill_toolset import SkillToolset

from skills.filesystem_registry import FilesystemSkillRegistry
from skills.lifecycle_tools import build_skill_lifecycle_tools
from skills.llm_config import make_lite_llm
from skills.skill_loader import load_all_skills
from skills.tool_call_sanitizer import sanitize_tool_names_after_model

_DEFAULT_TOOL_RETRY_ATTEMPTS = 3

_AGENT_INSTRUCTION_COMMON = """You are the agent skills demo assistant.

You accomplish tasks by loading and following packaged skills from the library.

## Required workflow (progressive disclosure)
1. **Discover** — call ``list_skills`` (preload) or ``search_skills`` (lazy).
   Read names + descriptions before deciding no skill fits.
2. **Load** — call load_skill for the best match BEFORE taking action.
3. **Execute** — follow the procedure exactly:
   - tick checklist items if present
   - load references/ or assets/ only when the procedure points you there
   - run scripts/ for deterministic steps (do not re-implement in prose)
4. **Terminate** — confirm the skill's "Done when" criteria in your reply.

## Transparency
Always state which skill you used and why its description matched the task.

## User-provided text
When the user embeds document or transcript text in their message, treat it as
the working input — no separate file is required. Examples:

- ``Clean this transcript: group O and logic errors`` → transcript is
  ``group O and logic errors``
- ``'So group O optimizes logic for L L M training.'`` → quoted text is the input

Do not ask the user to re-upload text they already supplied inline.

## Generalize skills — workflow type, not input instance
Skills name a **reusable workflow**, not one example input.

| Wrong (instance) | Right (workflow) |
|------------------|------------------|
| ``riemann-zeta-summary`` | ``scientific-topic-summary`` |
| ``ppo-summary`` | ``scientific-topic-summary`` |
| ``q3-sales-report`` | ``quarterly-report`` |

Rules when capturing a new skill:

1. **Search first** — before scaffolding, ``search_skills`` using the *task
   type* ("summarize scientific topic"), not the specific input ("Riemann zeta").
   Reuse an existing skill if one matches the workflow.
2. **Name** — verb + object *category* (``scientific-topic-summary``), never the
   user's specific topic in the skill id.
3. **Description / trigger** — describe when the workflow applies in general
   ("user names a scientific topic to summarize"). Do not name one topic.
4. **Procedure** — parameterize per-request inputs with brace placeholders
   (names such as topic, document, or diff). Infer each value from the user's
   natural-language message at run time — the user will not supply them as
   separate named fields. Never bake in content from the first example
   (e.g. zeta zeros, PPO clip objective).
5. **Follow-ups** — refine via ``apply_skill_procedure_delta``, still using
   placeholders — not by creating a second instance-specific skill.

## When no skill fits
Only after discovery tools return no reasonable match:

1. **Execute** — complete the user's task from general knowledge. Include only
   what they asked for in this turn (e.g. a plain summary — not references
   unless they requested them).
2. **Capture** — if the task is reusable, scaffold with the generic lean-core
   template and record the procedure you actually followed:
   - ``scaffold_new_skill`` — always use the default ``lean-core`` pattern.
   - ``author_skill_procedure`` — write the Procedure checklist and Done when
     criteria for *this* turn only (must pass validation tests).
   - ``refresh_skill_library`` — rescan so ``search_skills`` / ``list_skills``
     see the new skill.
3. **Report** — tell the user you had no matching skill, delivered the result
   from scratch, and captured a reusable skill for next time.

## Refining an existing skill (follow-up turns)
When the user returns to the same workflow with new requirements (e.g. first
turn: "summarize PPO"; follow-up: "I need references too"):

1. **Load** the skill you created earlier via ``load_skill``.
2. **Execute** the updated request (add references, change length, etc.).
3. **Delta** — call ``apply_skill_procedure_delta`` to append or adjust
   procedure / done-when lines that encode the new requirement. Use governed
   deltas only — do not rewrite SKILL.md in prose.
4. **Report** what changed in the skill procedure.

### Example: scientific topic summaries
- Turn 1: "Summarize the Riemann zeta function" → ``search_skills`` for
  "summarize scientific topic" first. If ``scientific-topic-summary`` exists,
  load it and infer the topic from the message; else deliver the summary,
  then scaffold ``scientific-topic-summary`` (not ``riemann-zeta-summary``)
  with a topic brace-placeholder in the procedure.
- Turn 2: "I need references" → ``apply_skill_procedure_delta`` on the same
  skill — still parameterized by an inferred topic placeholder.
"""

_AGENT_INSTRUCTION_PRELOAD = (
    f"{_AGENT_INSTRUCTION_COMMON}\n"
    "## Loading strategy (preload)\n"
    "Skills were preloaded at startup. Use ``list_skills`` for discovery, "
    "then ``load_skill`` for the procedure body."
)

_AGENT_INSTRUCTION_LAZY = (
    f"{_AGENT_INSTRUCTION_COMMON}\n"
    "## Loading strategy (lazy / registry-only)\n"
    "No skills were preloaded. ``list_skills`` may be empty — use "
    "``search_skills`` to discover candidates, then ``load_skill`` to fetch "
    "the procedure from disk on demand."
)


def build_skill_toolset(
    *, preload: bool, use_registry: bool | None = None
) -> SkillToolset:
    """Construct the ADK SkillToolset wired to this repo's library.

    Args:
        preload: When True, read every skill folder at construction time.
            When False, start with an empty in-memory catalog and rely on the
            registry for ``search_skills`` and ``load_skill``.
        use_registry: When True, attach ``FilesystemSkillRegistry`` for search,
            on-demand loading, and post-scaffold refresh. Defaults to True for
            both strategies so the library can grow at runtime.

    Returns:
        Configured ``SkillToolset`` with local script execution enabled.

    Raises:
        ValueError: If ``preload`` is False and ``use_registry`` is False.
    """
    attach_registry = True if use_registry is None else use_registry
    if not preload and not attach_registry:
        raise ValueError("Lazy loading requires a skill registry.")

    registry = FilesystemSkillRegistry() if attach_registry else None
    skills = load_all_skills() if preload else []

    # WARNING: UnsafeLocalCodeExecutor runs scripts on your machine with your
    # user permissions. Fine for bootcamp demos; use a sandbox in production.
    return SkillToolset(
        skills=skills,
        registry=registry,
        code_executor=UnsafeLocalCodeExecutor(),
    )


def _filesystem_registry(*, toolset: SkillToolset) -> FilesystemSkillRegistry | None:
    """Narrow the toolset registry to the filesystem implementation.

    ADK types ``SkillToolset._registry`` as ``SkillRegistry | None``.
    Lifecycle tools call ``FilesystemSkillRegistry.refresh()``.

    Args:
        toolset: Toolset whose registry was attached by ``build_skill_toolset``.

    Returns:
        The filesystem registry, or None when the toolset has no registry.

    Raises:
        TypeError: If the attached registry is not a ``FilesystemSkillRegistry``.
    """
    registry = toolset._registry
    if registry is None:
        return None
    if isinstance(registry, FilesystemSkillRegistry):
        return registry
    kind = type(registry).__name__
    message = f"Skill lifecycle tools require a FilesystemSkillRegistry, got {kind}."
    raise TypeError(message)


def build_agent(*, preload: bool) -> LlmAgent:
    """Create an LLM agent with the chosen skill-loading strategy.

    Args:
        preload: When True, preload all skills at startup; when False, use
            registry-only lazy loading.

    Returns:
        ADK ``LlmAgent`` configured for progressive disclosure. Tool names are
        sanitized after each model turn so Harmony/gpt-oss channel tokens do
        not break dispatch.
    """
    if preload:
        name = "skillcraft_agent_preload"
        description = (
            "Preloads the full skill library at startup, then uses "
            "list/search and load_skill at run time."
        )
        instruction = _AGENT_INSTRUCTION_PRELOAD
    else:
        name = "skillcraft_agent_lazy"
        description = (
            "Starts with no preloaded skills; discovers via search_skills "
            "and loads procedures from disk on demand."
        )
        instruction = _AGENT_INSTRUCTION_LAZY

    toolset = build_skill_toolset(preload=preload)
    # Only the preload agent keeps skills in memory, so only it needs the
    # lifecycle tools to sync that memory. A lazy agent reads from disk via the
    # registry; handing it the toolset would copy every skill into memory on
    # the first refresh, which also hides them from ADK's search_skills.
    lifecycle_tools = build_skill_lifecycle_tools(
        registry=_filesystem_registry(toolset=toolset),
        toolset=toolset if preload else None,
    )

    return LlmAgent(
        name=name,
        model=make_lite_llm(),
        description=description,
        instruction=instruction,
        tools=[toolset, *lifecycle_tools],
        # No temperature override: the default model (gpt-5-mini) rejects
        # non-default temperature; model defaults are fine for this demo.
        after_model_callback=lambda callback_context, llm_response: (
            sanitize_tool_names_after_model(
                callback_context=callback_context,
                llm_response=llm_response,
            )
        ),
    )


def build_app(*, preload: bool, name: str | None = None) -> App:
    """Wrap ``build_agent`` in an ADK ``App`` with automatic tool-error recovery.

    ``ReflectAndRetryToolPlugin`` turns tool-not-found and other tool failures
    into structured guidance so the model can correct itself in-loop — the
    user does not need to resend the prompt. Prefer exporting this ``App``
    from agent modules (ADK loads ``app`` before ``root_agent``).

    ``App.name`` must match the agents-dir folder (``lazy`` / ``preload``).
    ADK web stores sessions under ``{agents_dir}/{app.name}/.adk/``; using the
    LlmAgent id here would create a spurious third entry in the agent picker.

    Args:
        preload: Forwarded to ``build_agent``.
        name: ADK app / folder id. Defaults to ``preload`` or ``lazy``.

    Returns:
        Configured ``App`` with sanitizer (on the agent) and reflect/retry.
    """
    agent = build_agent(preload=preload)
    app_name = name if name is not None else ("preload" if preload else "lazy")
    return App(
        name=app_name,
        root_agent=agent,
        plugins=[
            ReflectAndRetryToolPlugin(max_retries=_DEFAULT_TOOL_RETRY_ATTEMPTS),
        ],
    )
