# Learning Guide — Agent Skills with Google ADK

This document is the **main learning guide** for the repo. Read it before diving into
the code. It connects **theory covered by the instructor** to the files you will touch.

## 1. The core idea (one paragraph)

A **skill** is packaged *knowing-how*: named procedural knowledge (instructions,
optional scripts and resources) that an agent loads **only when relevant**.
Unlike a one-shot prompt, a skill is **versioned, diffable, and reusable**.
Unlike a hard-coded tool, a skill is **authored in prose** and can evolve.

Google ADK implements this through `SkillToolset`, which exposes tools that map
to **progressive disclosure** — the single most important design principle in
this repo.

## 2. Progressive disclosure (L1 → L2 → L3)

Think of three gates that control **context cost**:

| Level | What loads | Where it lives | ADK tool (typical) |
|-------|------------|----------------|---------------------|
| **L1** | Name + description (triggers) | `SKILL.md` frontmatter | `list_skills` / search |
| **L2** | Procedure body | `SKILL.md` markdown | `load_skill` |
| **L3** | References, templates, scripts | `references/`, `assets/`, `scripts/` | `load_skill_resource`, `run_skill_script` |

**Key idea:** Every token in L2 is paid *every time* the skill loads.
Move rare material to L3 so the common path stays cheap. This is the
*lean-core + appendix* split from instructor theory.

## 3. Skill as an option (formal model)

Instructor theory maps each skill to an RL **option** `⟨I, π, β⟩`:

- **I (initiation set)** → the `description` field in frontmatter. This is the
  *highest-leverage line* in the entire skill. A brilliant procedure behind a
  vague description never fires.
- **π (policy)** → the Procedure section in `SKILL.md`.
- **β (termination)** → the **Done when** section. Without it, the agent does
  not know when to stop.

When reading any `SKILL.md` in this repo, ask: *where is I, π, and β?*

## 4. How this repo is split (on purpose)

```
skills/           ← ARTIFACTS (what the agent reads) — at repo ROOT
src/skills/       ← ORCHESTRATION (Python that loads artifacts into ADK)
```

**Why separate?** Skills are meant to be portable folders. A lawyer or analyst
can edit `skills/pii-guardrail/SKILL.md` without touching Python. The ADK agents
under `src/skills/agents/` are *runtimes* that consume them.

## 5. Code walkthrough (read in this order)

### Step A — `src/skills/paths.py`

Resolves `BOOTCAMP_ROOT_DIR/skills`. Every other module asks paths.py where the
library lives. **Note:** skills are data; Python is plumbing.

### Step B — `src/skills/skill_loader.py`

- `discover_frontmatters()` → L1 only (cheap scan)
- `load_skill()` → full L2+L3 via ADK's `load_skill_from_dir`
- `snapshot_library()` → joins human `manifest.yaml` with disk reality

Open `skills/manifest.yaml` side-by-side. The manifest is **curation** (Level 2
maturity); disk scan is **discovery**.

### Step C — `src/skills/filesystem_registry.py`

Implements ADK's `SkillRegistry` interface. **Note:** when you add a
new folder under `skills/`, call `refresh()` and the registry sees it — no agent
code change. Production systems might back this with GCS or a skill marketplace;
here we use the filesystem for clarity.

### Step D — `src/skills/agent_factory.py` and `src/skills/agents/`

Shared builders wire `SkillToolset` into `LlmAgent`. Two entry points compare
loading strategies:

| Agent folder | Strategy | When skills enter memory | Discovery tool |
|--------------|----------|--------------------------|----------------|
| `agents/preload/` | Eager | At startup (`load_all_skills`) — all skills | `list_skills` |
| `agents/lazy/` | Registry-only | Never at startup; `load_skill` reads the skill from disk when called | `search_skills` (`list_skills` starts empty) |

Read `_AGENT_INSTRUCTION_COMMON` in `agent_factory.py` (plus the short
`_AGENT_INSTRUCTION_PRELOAD` / `_AGENT_INSTRUCTION_LAZY` suffixes) — it teaches
the *model* the same workflow you are learning:

1. **Discover** — `list_skills` (preload) or `search_skills` (lazy)
2. **Load** — `load_skill` for the best match, before acting
3. **Execute** — follow the procedure; open `references/` / `assets/` only when
   pointed to; run `scripts/` instead of re-doing their work in prose
4. **Terminate** — confirm the "Done when" criteria

It also covers what to do when **no skill fits** (do the task, then capture it
with the lifecycle tools in Step E) and how to **refine** a skill on a follow-up
turn (a procedure delta, not a rewrite).

ADK `SkillToolset` behaviours worth knowing before Exercise 4:

- In **preload** mode, `search_skills` filters out every skill that is already
  in memory, so it returns `[]` for the preloaded library. Use `list_skills`.
- `load_skill` serves the **in-memory copy** when there is one. So the
  preload agent's lifecycle tools reload a skill after each accepted edit, and
  `refresh_skill_library` reloads every skill (and drops retired ones); a hand
  edit on disk needs that refresh or a restart.
- The lazy agent keeps **nothing** in memory: `build_agent` does not give its
  lifecycle tools the toolset, so its `refresh_skill_library` only rescans
  disk, and `load_skill` reads the current file every time.

`UnsafeLocalCodeExecutor` runs `scripts/*.py` locally, inside your Python
process, with your permissions. Scripts receive their input as command-line
arguments (`sys.argv`), never on stdin. **Never use in production** without
sandboxing — instructor theory treats scripts as privileged code.

`tool_call_sanitizer.py` repairs tool names that `gpt-oss` sometimes emits with
Harmony control tokens (e.g. `refresh_skill_library<|channel|>commentary`), and
`ReflectAndRetryToolPlugin` (in `build_app`) lets the model recover from other
tool errors within the same turn.

### Step E — `src/skills/skill_lifecycle.py`

Learning flows to trace in code:

1. **`scaffold_skill`** — a recurring task gets a folder (`SKILL.md`,
   `CHANGELOG.md`, placeholder tests) and a `status: draft` manifest entry.
   It rejects instance-specific names such as `riemann-zeta-summary`.
2. **`author_skill_procedure`** — replaces the Procedure and Done when sections
   in one go, right after scaffolding; validated like a delta. It is refused
   once the template's placeholder steps are gone, so an authored skill can
   only change through deltas.
3. **`apply_procedure_delta`** — governed incremental deltas to π / β with
   rollback if validation tests fail or the validation score regresses. An
   accepted delta bumps the patch version and appends to `CHANGELOG.md`.
4. **`remove_skill`** — retires a skill: deletes its folder and manifest entry.

`src/skills/lifecycle_tools.py` wraps flows 1–3 (plus `refresh_skill_library`)
as tools the **agent itself** can call when no skill fits a task.

### Step F — `src/skills/governance/`

- `evaluator.py` — **firing tests** (description / I) and **validation tests**
  (procedure / π)
- `output_tests.py` — **script tests** (run a bundled script on a sample
  input, compare stdout; no LLM) and **behaviour tests** (the LLM applies the
  skill to a sample input; the reply is checked). See Exercise 6.
- `governor.py` — CLI gate: ``--test-type firing`` (the default),
  ``validation``, ``script``, ``behaviour``, or ``all`` (firing + validation +
  script; add ``--with-behaviour`` for behaviour too). ``--min-accuracy``
  defaults to **1.0**; the
  process exits with code 1 if any evaluated skill is below it.

How a firing test decides (`semantic_search.matches_skill_description`): the
description is split at "Do NOT use" into a positive zone and an exclusion zone,
each prefixed with the **skill name**. A prompt is blocked if it shares an
exclusion keyword (e.g. `summar`, `translat`) with the exclusion zone, or if it
is closer to the exclusion zone by more than 0.03 (while scoring at least 0.175
on the positive zone); it fires if its cosine similarity to
the positive zone is ≥ 0.35; otherwise a **keyword fallback** fires it when
≥ 15% of its words (4+ letters) appear in the positive zone, or it shares a
skill-name part or a domain word (`transcript`, `qbr`, `pii`, `commit`, …).

Validation tests are plain substring checks (`must_contain` /
`must_not_contain`) on the procedure body. ``apply_procedure_delta`` rolls back
when validation fails or regresses.

> **Note:** the live agent's `search_skills` uses plain cosine similarity on the
> whole description (no zones, no keyword fallback), so a skill can pass its
> firing tests and still be ranked differently by the agent.

The first governor run downloads the `all-MiniLM-L6-v2` embedding model.

## 6. Hands-on exercises

Run every command from the project root. Exercises 1–3, 5 and the
first two steps of 6 need **no LLM**; Exercise 4 and the rest of 6 do.

### Exercise 1 — Trace progressive disclosure

1. Run `uv run skillcraft-demo --list-skills`.

   **Expect** (log lines, abbreviated):

   ```text
   Manifest v1.0.0 maturity L2
   --- Curated (manifest.yaml) ---
     transcript-cleaner v0.1.0 [lean-core] active
     ...                                  (8 entries: 4 active, 4 draft)
   --- Discovered on disk (L1 scan) ---
     commit-message — Drafts conventional commit messages from git diffs ...
     ...                                  (8 skills, first 80 characters of each description)
   ```

   Only L1 (name + description) is read here; no procedure bodies are loaded.
2. Open `skills/transcript-cleaner/SKILL.md` and identify I (the `description`),
   π (`## Procedure`) and β (`## Done when`).
3. Note what is deferred to L3: `references/glossary.md`, `assets/voice-guide.md`
   and `scripts/normalize.py`. The procedure names each one at the step that
   needs it.

### Exercise 2 — Break and fix a description

1. **Baseline.** Run `uv run skillcraft-governor --skill transcript-cleaner`.

   **Expect:** `PASS [firing] transcript-cleaner — 4/4 correct (100%)`. The two
   should-fire prompts match; the summarize and translate prompts are blocked
   by the `Do NOT use for summarization or translation` clause.
2. **Weaken the description.** In `skills/transcript-cleaner/SKILL.md`, replace
   the whole multi-line `description:` value so the line reads
   `description: Helps with text.`
3. **Run the governor again** (same command).

   **Expect** (exit code 1):

   ```text
   FAIL [firing] transcript-cleaner — 2/4 correct (50%)
     prompt='Summarize this transcript in three bullet points.' expected=False got=True
     prompt='Translate this lecture transcript to Spanish.' expected=False got=True
   ```

   The failures are on the prompts that should **not** fire. With the
   `Do NOT use` clause gone, nothing excludes summarizing or translating, and
   the word `transcript` still matches because the **skill name** is always
   part of the text being matched. This is the *overlap / god skill* direction:
   a vague description fires on neighbouring tasks. The two should-fire prompts
   still pass, and would pass even with low cosine scores, through the keyword
   fallback (`transcript` from the name; `clean` and `text`), not because the
   description describes the task.
4. **Now see the *Silent Skill*.** Add this case to the end of
   `skills/transcript-cleaner/tests/firing_cases.yaml`. It is a genuine
   cleaning request that avoids the words *transcript*, *clean* and *text*:

   ```yaml
     - prompt: >-
         De-mangle this Assembly.ai lecture output: GRPO came out as group O.
       should_fire: true
   ```

   Run the governor again. **Expect:** `3/5`, with the new prompt listed as
   `expected=True got=False`. Against `Helps with text.` it shares no keywords,
   so it can fire only if its cosine similarity reaches 0.35, which is unlikely
   against a three-word description. A real request the skill should handle is
   silently missed. (If it does fire on your machine, compare its score with
   the threshold — that is worth discussing too.)
5. **Revert the description** and run the governor once more. **Expect:**
   `5/5 (100%)`. The restored description mentions *Assembly.ai*, *de-mangle*
   and *lecture*, so the new prompt fires again.
6. **Clean up:** remove the case you added in step 4 (or keep it as a
   permanent regression test), so the skill is back to its shipped state.

**Takeaway:** a vague description fails both ways — it misses real requests
(silent skill) and fires on the wrong ones (god skill). Firing tests need
should-fire *and* should-not-fire cases to catch both.

### Exercise 3 — Add a skill gradually

1. **Scaffold** a new skill:

   ```bash
   uv run skillcraft-scaffold \
     --name meeting-notes \
     --description "Formats raw meeting notes into action items and decisions." \
     --trigger "user pastes meeting notes and asks for action items"
   ```

   **Expect:** `Created skill at .../skills/meeting-notes` followed by a list of
   next steps. The new folder holds `SKILL.md` (template steps), `CHANGELOG.md`,
   `tests/firing_cases.yaml`, `tests/validation_cases.yaml` and empty
   `references/`, `assets/`, `scripts/`; `manifest.yaml` gains
   `meeting-notes` with `status: draft`. Because `--exclude` was not given, the
   description ends with `Do NOT use for unrelated tasks.`
2. **Run the governor before editing anything:**
   `uv run skillcraft-governor --skill meeting-notes`.

   **Expect:** `FAIL [firing] meeting-notes — 1/2 correct (50%)`. The two placeholder
   prompts (`<prompt that SHOULD fire meeting-notes>` and
   `<related prompt that SHOULD NOT fire meeting-notes>`) are almost the same
   text, so the matcher gives them the same answer, and one of them is wrong.
   Placeholder tests prove nothing.
3. **Write real firing cases** in `skills/meeting-notes/tests/firing_cases.yaml`
   (at least two that should fire and two related ones that should not, e.g.
   summarizing a meeting recording or writing a meeting invite), sharpen the
   description with a real `Do NOT use for ...` clause, and rerun until it
   passes.
4. **Run the validation tests:**
   `uv run skillcraft-governor --skill meeting-notes --test-type validation`.

   **Expect:** `PASS [validation] meeting-notes — 3/3 correct (100%)` — even though the
   procedure still contains the template's `<common-path step ...>`
   placeholders. The default checks only look for `## Procedure`,
   `## Done when` and `- [ ]`. Add a case such as
   `- must_not_contain: "<common-path step"` to `validation_cases.yaml`, rerun
   (**expect** `3/4`, `FAIL`), then write real procedure steps and a checkable
   Done-when until it passes again.
5. Run `uv run skillcraft-demo --list-skills`. **Expect:** 9 skills, including
   `meeting-notes v0.1.0 [lean-core] draft`.
6. **Retire** the skill so the library returns to its shipped state:

   ```bash
   uv run skillcraft-remove --name meeting-notes
   uv run skillcraft-demo --list-skills   # back to 8 skills
   ```

### Exercise 4 — Watch the agent use a skill

Needs `OPENAI_API_KEY` (hosted default, `gpt-5-mini`) or `LLM_API_BASE` +
`LLM_MODEL_NAME` (lab vLLM server) in `.env`.

1. **Preload agent:**

   ```bash
   uv run skillcraft-demo "Clean this transcript: group O optimizes logic"
   ```

   **Expect** first `=== Loading strategy: PRELOAD (eager) ===` and
   `Startup: 8 skills loaded into memory`, then one `Tool → ...` line per tool
   call. A typical sequence (the model may vary it):
   `list_skills` → `load_skill('transcript-cleaner')` →
   `load_skill_resource('references/glossary.md')` →
   `run_skill_script('scripts/normalize.py')` →
   `load_skill_resource('assets/voice-guide.md')` → a final reply that names
   the skill, ticks the checklist and fixes *group O* → GRPO and *logic* →
   logits.
2. **Lazy agent:** add `--lazy` to the same command. **Expect**
   `Startup: 0 skills in agent memory`, and discovery through `search_skills`
   instead of `list_skills`.
3. **ADK web UI:** `uv run adk web src/skills/agents`, pick **preload** or
   **lazy**, and inspect each tool call and its response in the event view.

Things you may notice:

- In preload mode, `search_skills` returns `[]` even for an obvious match: ADK
  hides skills that are already in memory (see Step D). `list_skills` is the
  right tool there.
- `normalize.py` is called with the text as a positional argument. ADK puts
  `--` before positional arguments; the script drops it before cleaning.
- Without a prompt, `skillcraft-demo` runs three built-in sample prompts
  (transcript, commit message, scientific summary) to show routing.

### Exercise 5 — Watch a procedure delta roll back

No LLM needed. Each shipped skill's `tests/validation_cases.yaml` now holds
rules the procedure must keep (`must_contain`) or must never say
(`must_not_contain`), not just the section headers. Read
`skills/quarterly-report/tests/validation_cases.yaml`. Back up the library
first (`cp -R skills /tmp/skills-backup`), then try a delta that a user might
plausibly ask for — "if a metric is missing, estimate it from last
quarter":

```bash
uv run python -c "
from skills.skill_lifecycle import ProcedureDelta, apply_procedure_delta
r = apply_procedure_delta(
    skill_name='quarterly-report',
    delta=ProcedureDelta(append_procedure_lines=(
        '- [ ] Step 5: If a metric is missing, estimate it from the previous quarter.',)),
    changelog_note='demo: should be rejected')
print(r.accepted, r.baseline_validation_accuracy, r.validation_accuracy)
print(r.message)
"
```

**Expect:**

```text
False 1.0 0.875
Edit rejected: validation accuracy 88% < required 100%
```

The delta broke one of 8 rules (`must_not_contain: "estimate"`), so the
candidate scored 7/8 and `SKILL.md` was written back unchanged: same
version, no new `CHANGELOG.md` entry. Now try a delta that keeps every rule,
e.g. `'- [ ] Step 5: Round currency values to two decimals.'`. It is accepted:
the version goes to 0.1.1 and `CHANGELOG.md` gains an entry. Restore the
library afterwards: `rm -rf skills && cp -R /tmp/skills-backup skills`.

`tests/test_validation_rollback.py` runs five such rejections (dropping the
glossary step, adding a summarize step, inventing numbers, an email address in
commit messages, a "skip the checks" escape hatch in the PII guardrail) plus
one accepted delta.

### Exercise 6 — Test what a skill produces

Firing tests check the description and validation tests check the text of the
procedure. Neither checks the **output** of the skill on a real input. Two
more test files do:

| File | What runs | Checks | Cost |
|------|-----------|--------|------|
| `tests/script_cases.yaml` | A bundled script, with arguments passed the way `run_skill_script` passes them and no stdin | `expect_stdout`, `exit_code`, `must_contain` / `must_not_contain` | Free, deterministic |
| `tests/behaviour_cases.yaml` | The LLM, given the SKILL.md body and its L3 files, on a sample user input | `must_contain`, `must_not_contain`, `must_match` (regex), `min_matches` (regex + count) | One LLM call per case; replies vary |

1. **Script tests** (no LLM): `uv run skillcraft-governor --test-type script`.

   **Expect** `PASS [script] transcript-cleaner — 6/6 correct (100%)` and
   `PASS [script] quarterly-report — 4/4 correct (100%)`. Read the cases: one
   passes the text as `positional_args`, which the runner sends as
   `-- "<text>"` exactly like `run_skill_script`, so the script is tested the
   way the agent calls it.
2. **Add a case.** In `skills/quarterly-report/tests/script_cases.yaml`, add a
   case where `eng_cost + sm_cost` does not equal `total_cost`, expecting
   `exit_code: 1` and `must_contain: ["Cost mismatch"]`. Rerun: **expect**
   `5/5`. Then break it on purpose (expect `exit_code: 0`) to see a failure
   message.
3. **Behaviour tests** (needs the LLM):
   `uv run skillcraft-governor --test-type behaviour --skill transcript-cleaner`.
   **Expect** `2/2` most of the time: the replies should contain *GRPO*,
   *logits* and *LLM* and no *group O* or *you know*. If a case fails, read the
   reported problem and rerun once: model output varies.
4. **Govern with or without behaviour.**
   - `uv run skillcraft-governor --test-type all` runs firing, validation and
     script tests (no LLM calls).
   - Add `--with-behaviour` to include the behaviour tests.
   - For edits, `apply_procedure_delta(..., run_behaviour=True)` also runs
     the skill's behaviour tests before and after the edit and rolls back if
     the score drops. The agent's lifecycle tools do the same when
     `SKILL_GOVERN_WITH_BEHAVIOUR=1` is set.
5. **A delta only behaviour can catch.** "Leave technical terms exactly as
   spoken" breaks no validation rule, yet a model following it stops fixing
   *group O*. `tests/test_output_tests.py` shows the behaviour gate rejecting
   it (with a stand-in for the LLM) and the same delta being accepted when the
   gate is off.

## 7. Pattern catalog (maps to `skills/` folders)

| Pattern | Skill example | When to use |
|---------|---------------|-------------|
| Lean core + appendix | `transcript-cleaner` | Common path in SKILL.md; rare tables in references/ |
| Checklist carrier | `commit-message` | Long procedures that lose coherence |
| Template bearer | `quarterly-report` | Exact output shape; template in assets/ |
| Guardrail / policy | `pii-guardrail` | Hard constraints; refuse path required |

### How the four draft skills were made

The four `active` skills above were written by hand as exemplars, one per
pattern. The four `draft` skills were **grown by the agent** during class runs
(Part 5 of the slides replays the sessions), and all four use **lean core**:

- **Why lean core:** the agent's `scaffold_new_skill` tool accepts only
  `lean-core` (`skills/_templates/` holds no other template), and the agent's
  instruction says to always scaffold with it. Lean core is the safe default
  for a first capture: a short `SKILL.md` that can grow by deltas later.
- **What they look like:** the template's procedure is a checklist with
  `{placeholder}` inputs (its own heading says "Checklist-carrier pattern"),
  so each draft is a lean-core folder with a checklist-style procedure. None
  has L3 files yet: no `references/`, `assets/` or `scripts/` content. Their
  appendix is still empty.

| Draft skill | How it came about | What went wrong, and the fix |
|---|---|---|
| `scientific-topic-summary` | The agent was asked to summarize the Riemann zeta function, found no skill, and scaffolded `riemann-zeta-summary`. A follow-up asked for references and reuse on other topics. | Named after the instance. Generalized to `{topic}` (0.1.0); this run is why `scaffold_skill` now rejects instance names. |
| `wikipedia-article-writing` | Scaffolded after "write a Wikipedia-style article on cricket"; later reused for football and diabetes. | Exclusion "None"; the procedure kept cricket's "rules/format, notable events". Exclusions fixed in 0.1.2; the procedure still has that leak and two filler steps. |
| `quiz-creation` | Scaffolded for "a quiz on soccer with at least 10 questions"; a follow-up ("only 5 were created, I want 10") became a delta (0.1.1). | Empty exclusion; the template's placeholder steps survived because authoring failed on a garbled tool name. Fixed in 0.1.2 and 0.1.3. |
| `wedding-invitation-draft` | Scaffolded for "draft an invite for a wedding", then filled with the couple, date, time and venue. | Exclusion "none" outscored real prompts; the authored checklist ran away to 177 repeated steps. Fixed in 0.1.2 and 0.1.3. |

**If they were written by hand today**, a different pattern would often fit
better: `wedding-invitation-draft` as a **template bearer** (the invitation
layout in `assets/`), `quiz-creation` as a **checklist carrier** with the
answer-key format in `references/`, and `wikipedia-article-writing` as
**lean core + appendix** with the section structure moved to `references/`.
Promoting a draft is a human step: pick the pattern, add the L3 files, and
change `status` to `active` in `manifest.yaml`.

## 8. Maturity model (where this repo sits)

| Level | Meaning | This repo |
|-------|---------|-----------|
| 0 | Ad-hoc prompts | — |
| 1 | Authored skills as folders | ✓ eight skills (4 active hand-written exemplars, 4 drafts that grew out of agent runs) |
| 2 | Curated library + manifest | ✓ `manifest.yaml` |
| 3 | Evaluated + governed | ✓ governor + firing and validation tests |
| 4 | Self-improving under governor | partial: the agent can scaffold, author and apply deltas (`lifecycle_tools.py`); results still need human review |

## 9. Further reading

- [anthropics/skills](https://github.com/anthropics/skills) — reference implementations
- [ADK Skills](https://adk.dev/skills/) — `SkillToolset` API
- [agentskills.io](https://agentskills.io/) — portable folder spec
- Instructor sessions — skeleton patterns, governor, anti-patterns
