# Agent Skills Demo — Google ADK

A **teaching repo** for the Agent Skills pattern: packaged procedural knowledge
that agents load on demand. Conceptual framing comes from **theory covered by the
instructor**; implementation from [Google ADK `SkillToolset`](https://adk.dev/skills/)
and the [Agent Skills spec](https://agentskills.io/).

> **Start here:** [`docs/LEARNING_GUIDE.md`](docs/LEARNING_GUIDE.md) — concepts,
> code walkthrough, and hands-on exercises.

## What you will learn

1. **Progressive disclosure** — load metadata first (L1), procedure second (L2),
   resources only when needed (L3).
2. **Skills as options** — description = trigger, procedure = policy,
   "done when" = termination.
3. **Library growth** — scaffold new skills without changing agent code.
4. **Governed edits** — validation tests reject procedure changes that fail or
   regress; firing tests separately judge description triggers.

## Architecture (two layers on purpose)

```
skills/                    # ARTIFACTS — portable skill folders (repo ROOT)
  manifest.yaml            # human-curated registry (maturity Level 2)
  transcript-cleaner/      # example: lean core + references + scripts
  ...

src/skills/                # ORCHESTRATION — Python that feeds ADK
  paths.py                 # where the library lives (BOOTCAMP_ROOT_DIR or repo root)
  skill_loader.py          # discover (L1) vs load (L2+L3)
  filesystem_registry.py   # ADK SkillRegistry over the skills/ folder
  semantic_search.py       # embeddings + cosine similarity for search and firing tests
  agent_factory.py         # shared preload vs lazy SkillToolset / LlmAgent / App builders
  agents/
    preload/agent.py       # eager: load all skills at startup
    lazy/agent.py          # registry-only: load on demand
  llm_config.py            # hosted OpenAI vs self-hosted vLLM model
  tool_call_sanitizer.py   # repairs gpt-oss tool names with Harmony tokens
  skill_lifecycle.py       # scaffold, author, governed deltas, retire
  lifecycle_tools.py       # the same lifecycle as tools the agent can call
  governance/              # firing + validation tests and governor gate
  run_demo.py              # skillcraft-demo CLI
  scaffold_skill.py        # skillcraft-scaffold / skillcraft-remove CLIs
```

**Intentional split:** non-programmers can edit `skills/*/SKILL.md`; engineers
wire the runtime in `src/skills/`.

## Progressive disclosure in ADK

When the agent handles a task, ADK's `SkillToolset` typically:

```
list_skills / search     →  L1 frontmatter only (cheap)
load_skill               →  L2 SKILL.md body
load_skill_resource      →  L3 references/ or assets/
run_skill_script         →  L3 scripts/ (executed, not pasted into context)
```

Only relevant tokens enter the model context — the economic reason skills beat
giant system prompts.

## Skill patterns in this library

The examples follow the **skeleton skill repository** patterns from instructor
theory (lean core, checklist carrier, guardrail, template bearer):

| Skill | Pattern | Instructor pattern | Teaching focus |
|-------|---------|-------------------|----------------|
| `transcript-cleaner` | Lean core + appendix | Lean-core skeleton | Defer glossary to `references/` |
| `commit-message` | Checklist carrier | Checklist carrier | Tick boxes; don't lose steps |
| `pii-guardrail` | Guardrail / policy | Guardrail / policy | Explicit refuse path |
| `quarterly-report` | Template bearer | Template bearer | Template in `assets/`, not prose |

The library also holds four `draft` skills that grew out of class runs where
the agent created and refined skills (`scientific-topic-summary`, `wikipedia-article-writing`,
`quiz-creation`, `wedding-invitation-draft`) — eight skills in all. Their
`CHANGELOG.md` files show how agent-written skills went wrong and were fixed.
Note that `status: draft` is informational: draft skills are loaded and offered
to the agent like active ones.

Each skill folder includes `tests/firing_cases.yaml` (description triggers),
`tests/validation_cases.yaml` (rules the procedure text must keep or avoid) and
`tests/behaviour_cases.yaml` (sample inputs and checks on the LLM's reply when
it applies the skill). Skills with scripts also have `tests/script_cases.yaml`
(script input → expected output, no LLM).

## Quick start

```bash
cp .env.example .env
# .env.example ships with option (b) active: the lab vLLM server
# (LLM_API_BASE=http://10.0.10.70:8000/v1, LLM_MODEL_NAME=openai/gpt-oss-20b).
# For hosted OpenAI gpt-5-mini (the code default) instead: comment out the
# option (b) lines and set a real OPENAI_API_KEY under option (a).
export BOOTCAMP_ROOT_DIR="$(pwd)"   # this project folder (the one containing skills/)
export PYTHONPATH="$(pwd)/src"

# No LLM needed — inspect the library
uv run skillcraft-demo --list-skills

# Run firing tests on descriptions (governor gate; first run downloads the
# all-MiniLM-L6-v2 embedding model). --min-accuracy defaults to 1.0.
uv run skillcraft-governor --test-type firing --min-accuracy 0.75

# Run validation tests on procedures
uv run skillcraft-governor --test-type validation

# Run bundled scripts on sample inputs (no LLM)
uv run skillcraft-governor --test-type script

# Apply skills to sample inputs with the LLM and check the replies
uv run skillcraft-governor --test-type behaviour

# Everything without LLM calls; add --with-behaviour to include behaviour tests
uv run skillcraft-governor --test-type all

# Run agent against a prompt (needs LLM; default preload strategy)
uv run skillcraft-demo "Clean this transcript: group O and logic errors"

# Same demo with lazy/registry-only loading
uv run skillcraft-demo --lazy "Clean this transcript: group O and logic errors"

# ADK web UI — pick preload or lazy agent; watch tool calls live
uv run adk web src/skills/agents
```

## Gradual skill growth (lifecycle)

This mirrors the instructor's maturity model (Levels 1 → 2 → 3):

1. **Scaffold** when a task recurs without a procedure:

   ```bash
   uv run skillcraft-scaffold \
     --name expense-report \
     --description "Fills expense reports from receipt data." \
     --trigger "user uploads receipts for reimbursement"
   ```

2. **Author** — edit `SKILL.md` (lean core), add `references/` / `assets/` /
   `scripts/` as needed. See `skills/README.md`.
3. **Evaluate** — replace the placeholder cases in `tests/firing_cases.yaml`
   and `tests/validation_cases.yaml` (the placeholders do not test anything:
   the scaffold's firing test scores 1/2 and its validation test passes even
   with the template's placeholder steps), then run both gates:

   ```bash
   uv run skillcraft-governor --skill expense-report                        # firing
   uv run skillcraft-governor --skill expense-report --test-type validation
   ```

4. **Deploy** — `FilesystemSkillRegistry.refresh()` picks up new folders; no
   Python change required. A lazy agent reads skills from disk, so it sees
   new and edited skills on its next turn. A running preload agent sees them
   after `refresh_skill_library` (edits made through the lifecycle tools are
   reloaded automatically); otherwise restart it.

5. **Retire** — when the experiment is over, remove the scaffolded skill so the
   library returns to its shipped eight-skill state. The whole walkthrough is
   **idempotent**: scaffold → author → evaluate → retire leaves no trace, and
   you can run it again from the top.

   ```bash
   uv run skillcraft-remove --name expense-report
   uv run skillcraft-demo --list-skills   # verify: back to the shipped library
   ```

   (Retiring is part of the lifecycle, not an afterthought: a library that can
   only grow fills with stale procedures that mis-fire — the governor can gate
   *edits*, but only removal keeps the *catalog* honest.)

**Governed edits:** `apply_procedure_delta()` in `skill_lifecycle.py` applies
incremental procedure deltas, bumps version, runs **validation** tests, and
**rolls back** if validation fails or the score regresses. With
`run_behaviour=True` it also runs the skill's **behaviour** tests before and
after the edit (LLM calls) and rolls back if they drop; the agent's lifecycle
tools do this when `SKILL_GOVERN_WITH_BEHAVIOUR=1` is set. Use firing tests
when editing descriptions.

**Agent-driven growth:** `lifecycle_tools.py` gives the agent the same lifecycle
as tools (`scaffold_new_skill`, `author_skill_procedure`,
`apply_skill_procedure_delta`, `refresh_skill_library`). When no skill fits a
task, the agent does the task and then captures it as a new skill; follow-up
requirements become procedure deltas. `scaffold_skill` rejects
instance-specific names such as `riemann-zeta-summary`.

## Things to know before running the agent

- **Preload mode:** ADK's `search_skills` hides skills that are already in
  memory, so it returns `[]` for the preloaded library; the agent should use
  `list_skills`. In lazy mode, `list_skills` starts empty and `search_skills`
  is the discovery tool.
- **Memory vs. disk:** the preload agent serves skills from memory. Its
  lifecycle tools reload a skill after each accepted edit, and
  `refresh_skill_library` reloads them all; a hand edit on disk needs that
  refresh (or a restart). The lazy agent keeps nothing in memory and reads
  from disk on every `load_skill`.
- **Scripts get arguments, not stdin:** `run_skill_script` passes input in
  `sys.argv`, with a `--` before positional arguments. The bundled scripts read
  their input from the arguments and drop a leading `--`; `script_cases.yaml`
  tests them called exactly this way.
- **Firing tests vs live search:** firing tests use description zones and a
  keyword fallback; the agent's `search_skills` uses plain cosine similarity on
  the whole description. Passing firing tests does not guarantee the agent
  finds the skill.
- `UnsafeLocalCodeExecutor` runs skill scripts in your own Python process —
  fine for class, not for production.

## Tests (run without an LLM)

```bash
uv sync --group dev
uv run pytest tests/ -v
```

Tests cover loading, registry search, scaffolding, and the governor — so
students can verify structure before spending tokens on the agent.

## File reading order (for instructors)

1. `docs/LEARNING_GUIDE.md`
2. `skills/transcript-cleaner/references/STUDY_GUIDE.md` + `SKILL.md` (annotated exemplar)
3. `src/skills/paths.py` → `skill_loader.py` → `filesystem_registry.py` →
   `semantic_search.py`
4. `src/skills/agent_factory.py` → `agents/preload/` and `agents/lazy/` →
   `llm_config.py`, `tool_call_sanitizer.py`
5. `src/skills/skill_lifecycle.py` → `lifecycle_tools.py`
6. `src/skills/governance/evaluator.py` → `governor.py`
7. `slides/skills_walkthrough.pdf` — the lab slide deck

## References

- [anthropics/skills](https://github.com/anthropics/skills)
- [ADK Skills documentation](https://adk.dev/skills/)
- [agentskills.io specification](https://agentskills.io/)
- Instructor sessions — lean core, governor, maturity model, anti-patterns


## Dependencies and quickstart

`uv sync` installs everything (`uv sync --group dev` for the test suite). Hosted
OpenAI `gpt-5-mini` needs a real `OPENAI_API_KEY` in `.env` (and the lab-server
lines commented out); the
pytest suite and `--list-skills` need no LLM at all. Run order: `pytest tests/ -v`
→ `uv run skillcraft-demo --list-skills` → the governor → `uv run skillcraft-demo
"<prompt>"` → `uv run adk web src/skills/agents`.
