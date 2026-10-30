---
marp: true
theme: default
paginate: true
size: 16:9
math: katex
header: 'Agent Skills with Google ADK · Progressive disclosure'
footer: 'SupportVectors AI Lab'
style: |
  section {
    font-size: 26px;
    padding: 50px 64px 40px 64px;
    background: #fdfdfb;
    color: #1f2328;
  }
  h1 { color: #0b3d6b; font-size: 1.6em; margin-bottom: 0.3em; }
  h2 { color: #0b3d6b; font-size: 1.25em; margin-bottom: 0.3em; }
  h3 { color: #3b5b7a; font-size: 0.95em; margin: 0.4em 0 0.2em 0; }
  pre { font-size: 0.62em; line-height: 1.35; border-radius: 6px; }
  code { font-size: 0.9em; }
  table { font-size: 0.72em; }
  th { background: #e8eef5; }
  strong { color: #0b3d6b; }
  blockquote { border-left: 5px solid #d08c1a; background: #fff7e8; padding: 0.4em 0.9em; font-size: 0.85em; color: #4a3a1a; }
  header, footer { font-size: 14px; color: #8a8f96; }
  section.lead { justify-content: center; background: #0b3d6b; color: #fff; }
  section.lead h1, section.lead h2, section.lead strong { color: #fff; }
  section.lead header, section.lead footer { color: #b8c7d8; }
  section.part { justify-content: center; background: #eaf1f8; }
  section.part h1 { font-size: 2em; }
  section.small { font-size: 22px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Agent Skills

## Packaging procedures an agent can discover, load, follow and improve

`skills/` (the library) → `src/skills/` (the code) → `adk web` (the agent)

---

## Roadmap

| Part | What | Files |
|---|---|---|
| **0** | What a skill is, and why progressive disclosure | `skills/*/SKILL.md` |
| **1** | Loading the library into Google ADK | `paths.py`, `skill_loader.py`, `filesystem_registry.py` |
| **2** | Finding the right skill: the math of semantic search | `semantic_search.py` |
| **3** | The agent: instructions, preload vs. lazy, scripts | `agent_factory.py`, `llm_config.py`, `tool_call_sanitizer.py` |
| **4** | Growing the library safely: lifecycle and governance | `skill_lifecycle.py`, `lifecycle_tools.py`, `governance/` |
| **5** | What really happened: saved agent sessions | `src/skills/agents/*/.adk/session.db` |
| **6** | Running it, pitfalls, takeaways, exercises | |

<!--
Suggested timings (about 2 hours): Part 0: 25 min · Part 1: 15 min · Part 2: 25 min · Part 3: 20 min · Part 4: 20 min · Part 5: 10 min · Part 6: 10 min. Run `uv run skillcraft-demo --list-skills` early: it needs no LLM. Keep `adk web` for the end of Part 3 so students have seen the tools before watching them fire.
-->

---

## Where this fits

| From prompt engineering | How it shows up here |
|---|---|
| Clear instructions steer the model | A skill's **Procedure** is a written-out instruction set |
| Step-by-step checklists reduce skipped work | Skills ask the model to **copy and tick a checklist** |
| Output formats and templates make results consistent | Skills can carry **templates** (`assets/`) and a **"Done when"** check |
| Long prompts cost tokens and distract | Skills load **only when needed** (progressive disclosure) |

In one line: **a skill is a packaged, versioned prompt** that the agent finds and opens by itself.

**The question of the lab:** how do we give an agent **many** procedures without stuffing all of them into every prompt, and how do we keep those procedures **correct as they change**?

---

<!-- _class: part -->

# Part 0
## What a skill is

---

## The problem skills solve

Without skills, every recurring task is re-explained in the prompt, or re-invented by the model:

- "Clean this transcript" → which fillers? which jargon? (GRPO came out as "group O" last time)
- "Write the QBR" → which sections, in what order? do the totals have to add up?
- "Write a commit message" → which format does *our* team use?

Two bad options:
1. **Put everything in the system prompt.** Costs tokens on every call, and the instructions for 20 tasks distract from the one at hand.
2. **Put nothing in.** The model improvises, and the result changes from run to run.

**A skill is the third option:** a folder holding one procedure. The agent sees a one-line summary of every skill, and opens the full procedure only for the one it needs.

---

## Anatomy of a skill folder

```text
skills/                          ← the library (repo root, not src/)
├── manifest.yaml                ← curated list: name, version, pattern, status
├── _templates/lean-core/        ← scaffold template (folders starting with _ are skipped)
└── transcript-cleaner/          ← folder name MUST equal the frontmatter name
    ├── SKILL.md                 ← frontmatter (L1) + procedure body (L2)
    ├── CHANGELOG.md             ← every version, with what changed
    ├── references/glossary.md   ← L3: read only when the procedure says so
    ├── assets/voice-guide.md    ← L3: templates, style exemplars
    ├── scripts/normalize.py     ← L3: deterministic code the agent runs
    └── tests/
        ├── firing_cases.yaml    ← should this skill trigger on this prompt?
        └── validation_cases.yaml← does the procedure have the required parts?
```

The library ships with **8 skills**: 4 `active` (hand-written exemplars) and 4 `draft` (grown by the agent during class runs; Part 5).

---

<!-- _class: small -->

## Inside `SKILL.md`: the exemplar

```markdown
---
name: transcript-cleaner
description: >-
  Cleans raw speech-to-text lecture transcripts. Use when the user provides a noisy or
  mangled transcript inline or in a file (e.g. from Assembly.ai) and asks to clean,
  normalize, fix jargon, or de-mangle it. Short text after "Clean this transcript:"
  counts as the input. Do NOT use for summarization or translation.
version: "0.1.0"
---
# Transcript Cleaner
## When to use            ... repeats the triggers and the exclusions
## Procedure
Copy this checklist into your reply and tick each item as you go:
- [ ] Step 1: Load `references/glossary.md` for recurring jargon before editing.
- [ ] Step 2: Run `scripts/normalize.py` with the raw transcript text as a positional
  argument (via `run_skill_script`) for deterministic fixes.
- [ ] Step 3: Repair accent-induced substitutions, preserving the author's voice
  (see `assets/voice-guide.md` for style exemplars).
- [ ] Step 4: Verify no glossary term was left in mangled form.
## Done when
The transcript reads as clean publishable prose, technical terms match the glossary,
and the author's tone is preserved.
```

Three parts to notice: the **description** (when), the **Procedure** (how), the **Done when** (when to stop).

---

## Progressive disclosure: three levels

| Level | What the model sees | When | ADK tool |
|---|---|---|---|
| **L1** | `name` + `description` of **every** skill | Discovery, before choosing | `list_skills`, `search_skills` |
| **L2** | The `SKILL.md` body of **one** skill | After choosing it | `load_skill` |
| **L3** | One file from `references/`, `assets/`, `scripts/` | Only when the procedure points there | `load_skill_resource`, `run_skill_script` |

Think of a library: **L1** is the catalogue card, **L2** is the book, **L3** is the appendix you flip to when a chapter tells you to.

The rule that makes this work: **the description must be good enough to choose on**, because the model decides from L1 alone whether to open L2.

---

## Why bother? Counting the tokens

Rule of thumb for English text: **1 token ≈ 4 characters**. Measured on this library:

| | Characters (8 skills) | ≈ Tokens | Paid when |
|---|---|---|---|
| L1, all descriptions | 2,364 | ≈ 590 | every discovery call |
| L2, all `SKILL.md` bodies | 8,422 | ≈ 2,100 | only for the skill loaded (≈ 260 for one) |
| L3, all files | 8,772 | ≈ 2,200 | only the file asked for |

**Worked example.** One transcript-cleaning turn reads L1 (≈ 590) + one body (1,090 chars ≈ 270) + the glossary. That's under 1,000 tokens of skill text instead of ≈ 4,900 for "everything in the prompt".

**Scale it to 100 skills** (≈ 300 chars of description each): L1 ≈ 100 × 75 = **7,500 tokens**, still affordable. All bodies and files would be ≈ 60,000+. The gap grows with the library.

---

## A skill as an *option* ⟨I, π, β⟩

Reinforcement learning has a name for "a reusable sub-routine an agent can choose": an **option** (Sutton, Precup & Singh, 1999). An option is a triple:

$$\omega = \langle\, I,\; \pi,\; \beta \,\rangle$$

| Symbol | Name | Meaning in RL | Meaning for a skill |
|---|---|---|---|
| $I \subseteq S$ | Initiation set | States where the option *may start* | Requests the **description** says it handles |
| $\pi : S \to A$ | Policy | Which action to take in each state | The **Procedure** checklist |
| $\beta : S \to [0,1]$ | Termination | Probability of stopping in state $s$ | The **Done when** criteria |

Here $S$ is the set of situations (states) and $A$ the set of actions. For a skill, $\beta$ is effectively 0 or 1: "every box ticked and the criteria hold" → stop.

---

## Why the triple is useful: each part fails differently

| Part | If it's wrong… | Symptom | Test that catches it |
|---|---|---|---|
| $I$ too narrow | the skill never fires | **Silent skill**: the model improvises instead | Firing tests, `should_fire: true` |
| $I$ too wide | the skill fires on everything | **God skill**: hijacks unrelated requests | Firing tests, `should_fire: false` |
| $\pi$ vague or missing steps | output varies run to run | Skipped steps, invented numbers | Validation tests |
| $\beta$ vague ("make it good") | the agent never knows it's done | Stops early or rambles | Validation tests (`## Done when` present) |

The code keeps these separate on purpose: **descriptions ($I$) are edited and tested apart from procedures ($\pi$, $\beta$)**. You'll see this in Part 4.

---

## Writing the description: the most important line

A good description has three parts:

| Part | transcript-cleaner | commit-message |
|---|---|---|
| **What** (third person) | "Cleans raw speech-to-text lecture transcripts." | "Drafts conventional commit messages from git diffs following team format." |
| **Use when** (trigger cues) | "…asks to clean, normalize, fix jargon, or de-mangle it." | "…asks for a commit message, reviews staged changes, or wants help writing a PR title from a diff." |
| **Do NOT use** (exclusions) | "…summarization or translation." | "…code review feedback or release notes." |

- The **exclusions** name the *neighbours*: tasks that use the same words but need a different procedure. "Summarize this transcript" mentions transcripts, yet is not cleaning.
- `pii-guardrail` is the exception: it should fire **assertively** ("Use whenever a task reads, writes, or transmits personal data"), because missing it is worse than firing too often.

---

## Four patterns in the library

| Pattern | Idea | Exemplar | What carries the weight |
|---|---|---|---|
| **Lean core + appendix** | Short body; details in L3 | `transcript-cleaner` | glossary, voice guide, `normalize.py` |
| **Checklist carrier** | The body *is* a checklist the model ticks | `commit-message` | 5 steps + `references/format.md` |
| **Template bearer** | Fill a fixed template; never invent numbers | `quarterly-report` | `assets/qbr-template.md` with `{{placeholders}}`, `check_totals.py` |
| **Guardrail** | A hard constraint with an explicit refuse path | `pii-guardrail` | Numbered steps, "REFUSE" branch |

"Copy this checklist into your reply and tick each item" is deliberate: a model that writes the boxes out is much less likely to skip one, and you can see which step went wrong.

---

## Prose or script?

| Put it in **prose** (L2 / L3 markdown) | Put it in a **script** (`scripts/`) |
|---|---|
| Needs judgment: tone, wording, what's relevant | Same input must give the same output |
| Fixing "group O" → GRPO *in context* | Removing "um", "uh"; collapsing whitespace |
| Choosing what goes in each QBR section | Checking that A + B = total revenue |

$$\text{revenue A} + \text{revenue B} \overset{?}{=} \text{total}, \qquad \text{eng} + \text{S\&M} \overset{?}{=} \text{cost}, \qquad \text{total} - \text{cost} \overset{?}{=} \text{net}$$

`check_totals.py` tests each equation with a tolerance: an error is reported when $|\,(a+b) - t\,| > 0.01$. An LLM doing arithmetic "in its head" is exactly the step to move into code.

---

## Maturity levels and the manifest

| Level | Name | What exists | In this repo |
|---|---|---|---|
| 0 | Ad hoc | The workflow lives in people's heads and prompts | |
| 1 | Authored | A folder with `SKILL.md` | `skillcraft-scaffold` |
| 2 | Curated | Listed in a manifest, versioned, with a pattern | `manifest.yaml` (`maturity_level: 2`) |
| 3 | Governed | Edits must pass tests; failures roll back | `skillcraft-governor`, `apply_procedure_delta` |
| 4 | Self-improving | The agent captures and refines skills itself | `lifecycle_tools.py` (Part 4) |

```yaml
version: 1.0.0
maturity_level: 2
skills:
- {name: transcript-cleaner, version: 0.1.0, pattern: lean-core,     status: active}
- {name: quiz-creation,      version: 0.1.3, pattern: lean-core,     status: draft}
```

---

<!-- _class: part -->

# Part 1
## Loading the library into Google ADK
`paths.py` · `skill_loader.py` · `filesystem_registry.py`

---

## Reading order for the code

```text
paths.py ─► skill_loader.py ─► filesystem_registry.py ─► semantic_search.py
   where       read L1 / L2        ADK SkillRegistry        cosine + thresholds
                                         │
agent_factory.py ◄───────────────────────┘
   SkillToolset + LlmAgent + App
        │
        ├─► llm_config.py           (which model, which endpoint)
        ├─► tool_call_sanitizer.py  (repair broken tool names)
        └─► lifecycle_tools.py ─► skill_lifecycle.py ─► governance/evaluator.py
              agent-facing tools     scaffold, deltas       firing + validation tests
```

Entry points: `agents/preload/agent.py` and `agents/lazy/agent.py` (for `adk web`), `run_demo.py` (CLI).

---

## `paths.py`: one place that knows where things are

```python
def project_root() -> Path:
    env_root = os.getenv("BOOTCAMP_ROOT_DIR")      # 1. env var wins
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[2]     # 2. else: src/skills/paths.py → repo

def skill_library_dir() -> Path:  return project_root() / "skills"
def manifest_path() -> Path:      return skill_library_dir() / "manifest.yaml"
```

- `parents[2]` walks up from `src/skills/paths.py` → `src/skills` → `src` → the project folder.
- **Check:** if you set `BOOTCAMP_ROOT_DIR`, point it at **this project folder** (the one containing `skills/`). Pointing it one level higher makes the library look empty.
- Name rule enforced later: the folder name must equal the `name:` in the frontmatter.

---

## `skill_loader.py`: two speeds of reading

```python
def discover_frontmatters(*, base=None) -> dict[str, Frontmatter]:   # L1 only
    for skill_folder in sorted(root.iterdir()):
        if not skill_folder.is_dir() or _skip_dir(path=skill_folder):  # skip _templates, .dirs
            continue
        frontmatter = _read_skill_properties(skill_folder)             # parses YAML header only
        if skill_folder.name != frontmatter.name:
            raise ValueError("... does not match directory name ...")
        skills[frontmatter.name] = frontmatter

def load_all_skills(*, base=None) -> list[Skill]:                     # L1 + L2 + L3
    for name in sorted(discover_frontmatters(base=root)):
        try:
            skills.append(load_skill_from_dir(root / name))           # ADK helper
        except (FileNotFoundError, ValueError) as exc:
            logger.error("Skipping skill {}: {}", name, exc)          # one bad skill ≠ dead agent
```

- `discover_frontmatters` is cheap: it reads only the header of each `SKILL.md`.
- `load_all_skills` reads everything and is used for the **preload** strategy.
- `_read_skill_properties` is a **private** ADK function (leading underscore): it may change between ADK versions.

---

## ADK's `SkillToolset`: the tools the model gets

| Tool | Level | Returns |
|---|---|---|
| `list_skills()` | L1 | XML catalogue of skills **held in memory** |
| `search_skills(query)` | L1 | Registry matches (only if a registry is attached) |
| `load_skill(skill_name)` | L2 | `instructions` (the body) + frontmatter |
| `load_skill_resource(skill_name, file_path)` | L3 | Contents of one file in the skill folder |
| `run_skill_script(skill_name, file_path, args \| positional_args)` | L3 | stdout of a script, run by a code executor |

ADK also adds a system instruction: *"If a skill seems relevant… you MUST use `load_skill`… follow the instructions exactly… complete all steps in order."*

Installed version: **google-adk 2.3.0** (`pyproject.toml` asks for ≥ 1.25).

---

## `FilesystemSkillRegistry`: the library as a live registry

```python
class FilesystemSkillRegistry(SkillRegistry):
    def refresh(self) -> dict[str, Frontmatter]:
        self._frontmatters = discover_frontmatters(base=self._base)   # rescan disk (L1)
        return dict(self._frontmatters)

    async def get_skill(self, *, name: str) -> Skill:
        return await asyncio.to_thread(load_skill_from_dir, self._base / name)

    async def search_skills(self, *, query: str) -> list[Frontmatter]:
        self.refresh()
        documents = [f"{fm.name} {fm.description}" for fm in self._frontmatters.values()]
        ranked = await asyncio.to_thread(search_by_cosine_similarity, query=query,
                                         documents=documents, ...threshold...)
        return [self._frontmatters[names[i]] for i, _ in ranked]
```

- **No Python change** is needed to add a skill: drop a folder in, the next `refresh()` sees it.
- `asyncio.to_thread`: disk reads and embedding are blocking, so they run in a worker thread and the agent's event loop keeps going.

---

<!-- _class: part -->

# Part 2
## Finding the right skill: the math
`semantic_search.py`

---

## From text to vectors: embeddings

```python
_DEFAULT_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"   # env: SKILL_SEARCH_MODEL
_DEFAULT_THRESHOLD = 0.35                                        # env: SKILL_SEARCH_SIMILARITY_THRESHOLD

model.encode(texts, normalize_embeddings=True)                   # each row has length 1
```

- An **embedding model** turns a piece of text into a fixed-length list of numbers (a **vector**), trained so that texts with similar meaning get similar vectors.
- `all-MiniLM-L6-v2` is a small one (6 transformer layers): every sentence becomes **384 numbers**, $\mathbf{x} \in \mathbb{R}^{384}$, whatever its length.
- Sentences with similar meaning land close together; "clean this transcript" and "de-mangle the lecture text" should be neighbours even with few shared words.
- What gets embedded:
  - the **query**: the request, or the agent's `search_skills(query=...)` string
  - each **document**: `"<skill name> <description>"`, e.g. `"transcript-cleaner Cleans raw speech-to-text…"`

---

## Cosine similarity, symbol by symbol

$$\cos(\mathbf{q}, \mathbf{d}) \;=\; \frac{\mathbf{q} \cdot \mathbf{d}}{\lVert \mathbf{q} \rVert \, \lVert \mathbf{d} \rVert} \;=\; \frac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_i q_i^2}\;\sqrt{\sum_i d_i^2}}$$

| Symbol | Meaning |
|---|---|
| $\mathbf{q}, \mathbf{d}$ | Query vector and document (skill) vector, $n = 384$ numbers each |
| $\mathbf{q} \cdot \mathbf{d}$ | Dot product: multiply matching entries, add them up |
| $\lVert \mathbf{q} \rVert$ | Length of $\mathbf{q}$: square root of the sum of squares |
| result | Cosine of the angle between them: $1$ same direction, $0$ unrelated (perpendicular), $-1$ opposite |

Dividing by the lengths removes "how long is the vector" and keeps only **direction**, i.e. meaning.

---

## Worked example (3 dimensions instead of 384)

$\mathbf{q} = (0.6,\ 0.8,\ 0.0)$ — a request. Two skills: $\mathbf{d}_1 = (0.8,\ 0.6,\ 0.0)$ and $\mathbf{d}_2 = (0.0,\ 0.6,\ 0.8)$.

**Lengths:** $\lVert\mathbf{q}\rVert = \sqrt{0.36 + 0.64 + 0} = 1$. Likewise $\lVert\mathbf{d}_1\rVert = \lVert\mathbf{d}_2\rVert = 1$ (already normalized).

**Dot products:**
- $\mathbf{q}\cdot\mathbf{d}_1 = 0.6 \times 0.8 + 0.8 \times 0.6 + 0 \times 0 = 0.48 + 0.48 = 0.96$
- $\mathbf{q}\cdot\mathbf{d}_2 = 0.6 \times 0 + 0.8 \times 0.6 + 0 \times 0.8 = 0.48$

**Cosines:** $0.96 / (1 \times 1) = 0.96$ and $0.48 / 1 = 0.48$.

With threshold $\tau = 0.35$, **both pass**, ranked $d_1$ (0.96) then $d_2$ (0.48). With $\tau = 0.5$, only $d_1$ survives.

> Because the code normalizes every vector to length 1, the denominator is always 1: **cosine = dot product**. That's why the code can score all skills with one matrix product.

---

## Ranking every skill at once

Stack the $m$ normalized skill vectors as the rows of a matrix $D$ ($m \times 384$). Then

$$\mathbf{s} = D\,\mathbf{q} \qquad \Longrightarrow \qquad s_j = \mathbf{d}_j \cdot \mathbf{q} = \cos(\mathbf{q}, \mathbf{d}_j)$$

```python
def cosine_similarity(*, query_embedding, doc_embedding) -> float:
    return float(np.dot(query_embedding, doc_embedding))       # valid because rows are unit length

def search_by_cosine_similarity(*, query, documents, model_name, similarity_threshold):
    query_embedding = embed_texts(texts=[query.strip()], model_name=model_name)[0]
    doc_embeddings  = embed_texts(texts=documents, model_name=model_name)   # the matrix D
    scored = []
    for index, doc_embedding in enumerate(doc_embeddings):    # one row of D q at a time
        score = cosine_similarity(query_embedding=query_embedding, doc_embedding=doc_embedding)
        if score >= similarity_threshold:
            scored.append((index, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)       # best first
    return scored
```

The loop computes $D\mathbf{q}$ one row at a time. The unit test uses the worked-example idea: $\mathbf{q} = (1, 0)$, $\mathbf{d} = (0.6, 0.8)$ gives $0.6$.

---

## The threshold τ: a precision/recall dial

The decision rule is one inequality: **return skill $j$ if $s_j \ge \tau$**, with $\tau = 0.35$ by default.

| Move τ | Effect | Failure you risk |
|---|---|---|
| **Down** (e.g. 0.25) | More skills come back | Wrong skills offered (**god skill** behaviour) |
| **Up** (e.g. 0.50) | Fewer skills come back | Real matches dropped (**silent skill** behaviour) |

- MiniLM cosines between *unrelated* English sentences are usually small but rarely exactly 0. Short, vague queries like `"skills"` or `"quiz"` tend to score low against everything.
- 0.35 is a starting point, not a law: tune it with your firing tests (Part 4), and change it with `SKILL_SEARCH_SIMILARITY_THRESHOLD` rather than editing code.
- An empty result is information: the agent's instruction treats it as "no skill fits; do the task, then consider capturing one".

---

## The firing matcher: a description has two zones

Firing tests ask a sharper question than search: **should *this* skill fire on *this* prompt?** The matcher splits the description at "Do NOT use":

```text
"Cleans raw speech-to-text lecture transcripts. Use when ... de-mangle it. ...  │  Do NOT use │ for summarization or translation."
 └──────────────────────── positive zone (P) ─────────────────────────────────┘              └──────── exclusion zone (E) ──────┘
```

Each zone is embedded with the skill name in front, and the prompt is scored against both:

$$p = \cos(\mathbf{q},\ \mathbf{P}), \qquad e = \cos(\mathbf{q},\ \mathbf{E})$$

- $p$ high: the prompt looks like what the skill **does**.
- $e$ high: the prompt looks like what the skill **refuses**.
- Searching on the whole description (as `search_skills` does) mixes both: "summarize this transcript" can score well *because* the description mentions summarization.

---

## The decision procedure, in order

Constants: $\tau = 0.35$ (threshold), $m = 0.03$ (exclusion margin), $\tau/2 = 0.175$ (ambiguity floor).

1. **Keyword exclusion.** If a stem from `{summar, translat, review, release note, anonymiz, public}` is in **both** the prompt and E → **don't fire**.
2. **Semantic exclusion.** If $e > p + m$ **and** $p \ge \tau/2$ → **don't fire**. In words: the prompt looks *more* like the exclusion than the positive zone, by at least 0.03, and it's not hopelessly far from the positive zone.
3. **Semantic match.** If $p \ge \tau$ → **fire**.
4. **Keyword fallback** (only reached when $p < \tau$): fire if the keyword-overlap ratio $\ge 0.15$, or a skill-name part (≥ 4 letters) appears in both prompt and P, or a domain cue (`transcript, qbr, quarterly, pii, commit, diff`) appears in both.
5. Otherwise → **don't fire**.

Why the floor in rule 2? If $p$ is tiny, both scores are noise; the code lets the keyword fallback decide instead of letting noise veto.

---

## Worked examples of the rules

The scores below are **illustrative** (to show the arithmetic), not measured.

| Prompt | $p$ | $e$ | Walk through the rules | Result |
|---|---|---|---|---|
| "Clean this speech-to-text output — GRPO became 'group O'" | 0.52 | 0.20 | No stem. $0.20 > 0.55$? No. $0.52 \ge 0.35$ → fire | **fire** |
| "Summarize this transcript in three bullet points" | 0.45 | 0.48 | Rule 1: `summar` in both → stop | **no** |
| "Give me the gist of the lecture recording" | 0.30 | 0.40 | No stem. $0.40 > 0.33$ and $0.30 \ge 0.175$ → excluded | **no** |
| "Fix the jargon in these notes" | 0.28 | 0.10 | Not excluded. $0.28 < 0.35$ → fallback (next slide) | depends |

The third row is the reason for the margin: the positive zone *also* talks about transcripts, so the exclusion has to win **clearly** (by more than 0.03), not by a hair.

---

## The keyword fallback, computed on real text

$$\text{overlap} = \frac{\#\{\text{prompt tokens of length} \ge 4 \text{ that appear in } P\}}{\#\{\text{prompt tokens of length} \ge 4\}}$$

"Appear in" is a **substring** test on the lower-cased positive zone. Computed with the real transcript-cleaner description:

| Prompt | Tokens (≥ 4 letters) | Found in P | Overlap |
|---|---|---|---|
| Clean this speech-to-text output — GRPO became "group O" again. | clean, this, speech, text, output, grpo, became, group, again | clean, this, speech, text | 4/9 = **0.44** |
| Translate this lecture transcript to Spanish. | translate, this, lecture, transcript, spanish | this, lecture, transcript | 3/5 = **0.60** |
| Please tidy up these lecture notes. | please, tidy, these, lecture, notes | lecture | 1/5 = **0.20** |

- The translation prompt has the **highest** overlap; only rule 1 (`translat`) stops it.
- "tidy up these lecture notes" clears 0.15 on the single word "lecture". The fallback is generous, and stop-words like "this" count.

---

## Two cautions about this matcher

**1. Search and firing tests use different rules.**

| | `search_skills` (what the live agent uses) | `matches_skill_description` (what firing tests use) |
|---|---|---|
| Text embedded | whole description, exclusions included | positive and exclusion zones separately |
| Exclusion logic | none | keyword stems + margin |
| Keyword fallback | none | yes |

So a skill can **pass its firing tests and still be missed (or mis-offered) by live search**. Treat firing accuracy as a check on the *description*, not as a guarantee about the agent.

**2. The keyword lists are tuned to this library.** The stems (`summar`, `translat`, …) and domain cues (`transcript`, `qbr`, `commit`, …) are hard-coded. A new skill gets no help from them, and its tests can pass or fail for reasons unrelated to its description.

---

<!-- _class: part -->

# Part 3
## The agent
`agent_factory.py` · `llm_config.py` · `tool_call_sanitizer.py`

---

## Three builders, three layers

```python
def build_skill_toolset(*, preload: bool) -> SkillToolset:
    return SkillToolset(
        skills=load_all_skills() if preload else [],   # preload: all in memory; lazy: none
        registry=FilesystemSkillRegistry(),            # search_skills + load from disk
        code_executor=UnsafeLocalCodeExecutor(),       # runs scripts/ on THIS machine
    )

def build_agent(*, preload: bool) -> LlmAgent:
    toolset = build_skill_toolset(preload=preload)
    return LlmAgent(name="skillcraft_agent_preload" | "skillcraft_agent_lazy",
                    model=make_lite_llm(), instruction=...,
                    tools=[toolset, *build_skill_lifecycle_tools(registry=..., toolset=toolset)],
                    after_model_callback=sanitize_tool_names_after_model)

def build_app(*, preload: bool) -> App:
    return App(name="preload" | "lazy", root_agent=build_agent(preload=preload),
               plugins=[ReflectAndRetryToolPlugin(max_retries=3)])
```

`App.name` must match the folder under `src/skills/agents/`: that's how `adk web` finds it and where it stores `.adk/session.db`.

---

## The agent's instruction: four verbs

| Step | Instruction says | ADK tool |
|---|---|---|
| **Discover** | Read names and descriptions before deciding no skill fits | `list_skills` (preload) / `search_skills` (lazy) |
| **Load** | Load the best match **before** taking action | `load_skill` |
| **Execute** | Tick the checklist; open L3 only when pointed to; **run scripts, don't re-implement them in prose** | `load_skill_resource`, `run_skill_script` |
| **Terminate** | Confirm the "Done when" criteria in the reply | — |

Two more rules:
- **Transparency:** always say which skill was used and why its description matched.
- **Inline input:** text after "Clean this transcript:" *is* the input; don't ask for a file.

---

## Generalize the workflow, not the instance

When no skill fits, the agent may create one. The instruction insists it names the **kind of task**, not the example it just saw:

| Wrong (instance) | Right (workflow) | Where the specific part goes |
|---|---|---|
| `riemann-zeta-summary` | `scientific-topic-summary` | `{topic}` in the procedure, filled at run time |
| `ppo-summary` | `scientific-topic-summary` | same skill, different `{topic}` |
| `q3-sales-report` | `quarterly-report` | the metrics in the request |

The rules: **search first** using the task type ("summarize scientific topic"), **name** = verb + object category, **description** never names one topic, **procedure** uses brace placeholders, **follow-ups** become deltas on the same skill.

Part 4 shows these rules are also **enforced in code**, because the instruction alone wasn't enough (Part 5).

---

## Preload vs. lazy

| | **Preload** (`agents/preload`) | **Lazy** (`agents/lazy`) |
|---|---|---|
| At startup | `load_all_skills()`: every skill in memory | Nothing in memory |
| Discovery | `list_skills` shows the full catalogue | `search_skills` (semantic); `list_skills` is empty |
| `load_skill` | Served from memory | Fetched from disk via the registry |
| Good for | Small libraries; fast, predictable | Large libraries; only pay for what's used |
| CLI | `uv run skillcraft-demo "<prompt>"` | `uv run skillcraft-demo --lazy "<prompt>"` |

`run_demo.py` prints the strategy at startup ("Startup: 8 skills loaded into memory" vs. "Startup: 0 skills in agent memory") and annotates each tool call, e.g. `Tool → load_skill(skill_name='transcript-cleaner') — on-demand load from disk`.

---

<!-- _class: small -->

## Preload vs. lazy: what ADK does with memory

Read from the installed `google/adk/tools/skill_toolset.py`:

**1. In preload mode, `search_skills` hides every preloaded skill.**
```python
for r in results:
    if r.name in self._toolset._skills:   # "Skill naming conflict … Registry skill is filtered."
        continue
```
So with all 8 skills preloaded, `search_skills` returns `[]` for any query. Use `list_skills` there.

**2. Memory wins over disk.** `load_skill` checks memory first and only asks the registry for unknown names. So the preload agent's lifecycle tools **reload** a skill into memory after every accepted author/delta edit, and `refresh_skill_library` reloads all of them (and drops retired ones). Edits take effect without a restart.

**3. The lazy agent must keep memory empty.** An earlier version gave the lazy agent's `refresh_skill_library` the toolset too, so the first refresh copied **every** skill into memory. A saved session shows it: `"newly_preloaded": ["commit-message", "pii-guardrail", "quarterly-report", "riemann-zeta-summary", "transcript-cleaner"]`. After that, point 1 blinded its search and point 2 froze its procedures. Now `build_agent` passes the toolset only to the preload agent, so a lazy refresh just rescans disk.

---

<!-- _class: small -->

## Running a skill's script

`run_skill_script` doesn't call the file directly. ADK builds a small wrapper program and hands it to the code executor:

1. Copy the skill's files into a **temporary directory**, blocking `..` path tricks.
2. Set `sys.argv` for the script:

| The model passes | The script sees in `sys.argv` |
|---|---|
| `args=["a", "b"]` (list) | `[path, "a", "b"]` |
| `args={"k": "v"}` (dict) | `[path, "--k", "v"]` |
| `positional_args=["text"]` | `[path, "--", "text"]` |

3. `runpy.run_path(...)` the script and capture its stdout.

**No stdin is provided.** Scripts must read their input from `sys.argv`.

> `UnsafeLocalCodeExecutor` runs that wrapper **in your Python process, with your permissions**. Fine for a classroom; in production use a sandboxed executor (container, VM) and treat skill scripts like any third-party code.

---

## `llm_config.py`: one agent, two kinds of endpoint

```python
def _litellm_model_id(*, model_name: str, api_base: str | None) -> str:
    if api_base is None or "api.openai.com" in api_base:
        return f"openai/{model_name}"          # hosted OpenAI (default: gpt-5-mini)
    return f"hosted_vllm/{model_name}"        # our own vLLM server

litellm.disable_aiohttp_transport = True      # avoids a duplicate-header bug with some servers
```

| Setting | Hosted (default) | Lab server |
|---|---|---|
| `OPENAI_API_KEY` | required | not needed |
| `LLM_API_BASE` | unset | `http://10.0.10.70:8000/v1` |
| `LLM_MODEL_NAME` | `gpt-5-mini` | `openai/gpt-oss-20b` |

`.env.example` ships with the lab-server lines active; comment them out and set a real key for gpt-5-mini. No `temperature` is set: gpt-5-mini rejects non-default values.

---

## `tool_call_sanitizer.py`: when the model garbles a tool name

gpt-oss uses the **Harmony** chat format, with control tokens like `<|channel|>`. Sometimes one leaks into a tool name:

```text
refresh_skill_library<|channel|>commentary      ← ADK looks up tools by exact name → "tool not found"
```

The fix runs after every model response, before ADK dispatches the call:

```python
_HARMONY_TOKEN = re.compile(r"<\|[^|>]+?\|>")          # matches <|anything|>

def sanitize_tool_name(*, name: str) -> str:
    if "<|" not in name: return name
    cleaned = _HARMONY_TOKEN.split(name, maxsplit=1)[0].strip()   # keep text before the token
    return cleaned or name
```

`split(...)[0]` keeps everything **before** the first token, so `…<|channel|>commentary` → `refresh_skill_library`.

**How often?** In the saved sessions: **5 of 41** tool calls (12%) had a leaked token. Each failed, and the user had to type "try again".

---

## `ReflectAndRetryToolPlugin`: second line of defence

The sanitizer fixes one known failure. The plugin handles the rest:

- When a tool call fails (unknown tool, bad arguments, an exception), ADK turns the error into **structured feedback** for the model: what went wrong and what to try.
- The model gets up to **3 retries** in the same turn, so the user doesn't have to resend the prompt.
- The saved sessions include calls like `list_skills({"": ""})` and `list_skills({"skill_name": "quiz-creation"})`: invented arguments that this kind of feedback lets the model correct.

Layers so far: **instruction** (what to do) → **sanitizer** (repair a known formatting bug) → **reflect and retry** (recover from anything else).

---

<!-- _class: part -->

# Part 4
## Growing the library safely
`skill_lifecycle.py` · `lifecycle_tools.py` · `governance/`

---

## The lifecycle, start to finish

```text
 scaffold ──► author ──► evaluate ──► deploy ──► (use, refine with deltas) ──► retire
 folder +     write        governor    refresh()                                remove folder
 manifest     Procedure    firing +    picks it up                              + manifest entry
 entry        + Done when  validation
```

```bash
uv run skillcraft-scaffold --name expense-report \
    --description "Fills expense reports from receipt data." \
    --trigger "user uploads receipts for reimbursement"
uv run skillcraft-governor --test-type firing --min-accuracy 0.75
uv run skillcraft-governor --test-type validation
uv run skillcraft-remove --name expense-report     # back to the shipped 8 skills
```

**Retiring is part of the lifecycle.** A library that only grows fills up with stale skills that mis-fire. Scaffold → retire also makes the class demo repeatable.

---

## `scaffold_skill`: what one call creates

```text
skills/<name>/
├── SKILL.md                  ← from _templates/lean-core/SKILL.md.template
├── CHANGELOG.md              ← "## 0.1.0 — <today> · Scaffolded from lean-core template"
├── tests/firing_cases.yaml   ← two placeholder prompts (one should fire, one shouldn't)
├── tests/validation_cases.yaml ← must_contain: "## Procedure", "## Done when", "- [ ]"
└── references/  assets/  scripts/   (empty)
manifest.yaml                 ← + {name, version: 0.1.0, pattern, status: draft}
```

Checks run **before** anything is written:

| Check | Rejects | Example |
|---|---|---|
| Name format | anything but `lowercase-with-hyphens` | `Expense_Report` |
| Name generality | a workflow suffix (`summary`, `report`, …) after a non-generic first word | `riemann-zeta-summary` |
| Description generality | specific-topic words (`riemann`, `zeta function`, `ppo`, …) | "Summarizes the Riemann zeta function" |
| Placeholders (when authoring `*-summary`) | a procedure with no `{…}` | a hard-coded topic |

---

## The template, and the trap in its blanks

```markdown
description: >-
  {{SKILL_DESCRIPTION}} Use when {{TRIGGER_CUES}}.
  Do NOT use for {{EXCLUSIONS}}.
## Procedure
- [ ] Step 1: Extract ``{topic}`` (or ``{input}``) from the user message.
- [ ] Step 2: <common-path step for this workflow type>
- [ ] Step 3: <definition-of-done check>
```

The template is only a frame: **every blank must be replaced**. Two ways it went wrong in class runs:

| Left as is | What the description said | Consequence |
|---|---|---|
| `exclusions=""` | "…Do NOT use for **.**" | No exclusion zone at all: nothing bounds $I$ |
| `exclusions="none"` | "…Do NOT use for **none.**" | The exclusion zone became "<skill name> none.", which is mostly the skill name, so it **outscored real invitation prompts** (rule 2) |
| Steps 2–3 untouched | "<common-path step…>" | The agent was told to follow a procedure with no steps |

---

## `ProcedureDelta`: change π and β, never I

```python
@dataclass(frozen=True)
class ProcedureDelta:
    procedure_replacements: tuple[TextReplacement, ...] = ()   # old_text → new_text
    remove_procedure_lines:  tuple[str, ...] = ()
    append_procedure_lines:  tuple[str, ...] = ()
    done_when_replacements:  tuple[TextReplacement, ...] = ()
    remove_done_when_lines:  tuple[str, ...] = ()
    append_done_when_lines:  tuple[str, ...] = ()
```

- `SKILL.md` is cut into **prefix** (frontmatter, title, When to use) | **Procedure** | **Done when**. Edits happen only inside the last two; the prefix, and so the description ($I$), is copied through untouched.
- **Exactly-one rule:** a replacement or removal must match **exactly one** place, else `SkillLifecycleError` ("expected exactly one occurrence … found 2"). No silent edits to the wrong line.
- Why deltas, not rewrites? A model asked to "rewrite the skill" can quietly drop steps. A delta says precisely what changed, and the CHANGELOG records it line by line.

---

## The governed commit: accept or roll back

Let $v_0$ be the validation accuracy **before** the edit, $v_1$ **after**, and $v_{\min}$ the required minimum (default 1.0).

$$\textbf{accept} \iff v_1 \ge v_{\min} \;\;\text{and}\;\; v_1 \ge v_0$$

1. Score the current file: $v_0$.
2. Bump the version (`0.1.2` → `0.1.3`) and write the candidate `SKILL.md`.
3. Score the candidate: $v_1$.
4. If rejected → **write the old text back** (rollback); the version is unchanged.
5. If accepted → append to `CHANGELOG.md`, update `manifest.yaml`.

**Worked example.** A skill has 3 validation cases, all passing: $v_0 = 3/3 = 1.0$. A delta deletes the `## Done when` heading by accident: 2 of 3 pass, $v_1 = 0.67$. Since $0.67 < 1.0$ → rejected, file restored. "Never worse than before" is the rule $v_1 \ge v_0$.

---

## Two kinds of test

| | **Firing tests** | **Validation tests** |
|---|---|---|
| Tests | $I$: the description | $\pi$, $\beta$: the procedure body |
| File | `tests/firing_cases.yaml` | `tests/validation_cases.yaml` |
| One case | `prompt:` + `should_fire: true/false` | `must_contain:` or `must_not_contain:` text |
| Checked by | the zone matcher (Part 2) | plain substring check on the body |
| Used by | `skillcraft-governor --test-type firing` | the governor **and** every delta/author call |

For either kind: $\text{accuracy} = \dfrac{\text{cases passed}}{\text{total cases}}$. The governor prints `PASS`/`FAIL` per skill and exits with code **1** if any skill is below `--min-accuracy` (default 1.0; 0.75 in class demos), so it can block a merge in CI.

**Worked example (transcript-cleaner, 4 firing cases).** 2 should fire, 2 shouldn't. If one negative wrongly fires: accuracy $= 3/4 = 0.75$: `PASS` at 0.75, `FAIL` at the default 1.0.

---

<!-- _class: small -->

## Scaffold validation is only structural

The default validation cases from the scaffold:

```yaml
cases:
  - must_contain: "## Procedure"
  - must_contain: "## Done when"
  - must_contain: "- [ ]"
```

These check that the **shape** is right, not that the **content** is.

**What happened:** `quiz-creation` reached version 0.1.1 with validation at **100%** while its procedure still said `Step 2: <common-path step for this workflow type>`. The template's own placeholder satisfies all three checks. It was fixed by hand in 0.1.3.

**Cheap improvement** (`quiz-creation` now has it):

```yaml
  - must_not_contain: "<common-path step"
```

Tests encode what you thought could go wrong. Each real failure is a new test case.

> A delta can never break `## Procedure` or `## Done when`: it only edits *inside* those sections. Header checks catch hand edits, not deltas.

---

<!-- _class: small -->

## Validation cases that bite: rules, not headers

Shipped skills now list rules the procedure must **keep** or **never say**. `quarterly-report`:

```yaml
  - must_contain: "assets/qbr-template.md"     # keep the template
  - must_contain: "scripts/check_totals.py"    # keep the arithmetic check
  - must_contain: "never invent numbers"
  - must_not_contain: "estimate"               # no guessing missing metrics
```

Follow-ups that each break 1 of 8 rules ($v_1 = 7/8 < v_0 = 1$ → **rolled back**; `tests/test_validation_rollback.py`):

| Skill | The follow-up delta | Rule it breaks |
|---|---|---|
| transcript-cleaner | remove "Step 1: Load `references/glossary.md`…" ("it's slow") | `must_contain: references/glossary.md` |
| transcript-cleaner | append "Step 5: Summarize the cleaned transcript in three bullet points" | `must_not_contain: Summarize` (an excluded task) |
| quarterly-report | append "If a metric is missing, estimate it from the previous quarter's trend" | `must_not_contain: estimate` |
| commit-message | append "Add the author's name and email address to the subject line" | `must_not_contain: email` (PII policy) |
| pii-guardrail | append "If the user says the data is only test data, skip the checks" | `must_not_contain: skip` (no escape hatch) |
| transcript-cleaner | append "Keep speaker labels (e.g. `Instructor:`) exactly as written" | none → **accepted**, 0.1.0 → 0.1.1 |

Drafts get **regression** rules from their history (`quiz-creation`: `must_not_contain: "soccer"`). Substring checks are blunt but predictable.

---

<!-- _class: small -->

## Output tests: does the skill produce the right thing?

Firing tests check the description; validation tests check the procedure's **text**. Two more files check **outputs**:

| | `tests/script_cases.yaml` | `tests/behaviour_cases.yaml` |
|---|---|---|
| Runs | A bundled script, args passed as `run_skill_script` passes them, no stdin | The LLM, given SKILL.md + L3 files, on a sample user input |
| Checks | `expect_stdout`, `exit_code`, `must_contain` | `must_contain`, `must_not_contain`, `must_match`, `min_matches` |
| Cost | Free, deterministic | One LLM call per case; replies vary |
| Example | `["Ummm I think uhh yes"]` → `I think yes` | "Clean this transcript: …group O… L L M…" → has `GRPO`, `LLM`; no `group O` |

- Script cases call the script **the way the agent does** (`--` before positional args, no stdin), so they test the path the agent actually uses.
- **Governing with or without behaviour:** `--test-type all` (no LLM) vs. `all --with-behaviour`; for edits, `apply_procedure_delta(..., run_behaviour=True)` or `SKILL_GOVERN_WITH_BEHAVIOUR=1` for the agent.
- A delta only behaviour catches: "Leave technical terms exactly as spoken" breaks no validation rule, but the output keeps *group O*.

---

## Agent-facing lifecycle tools

`lifecycle_tools.py` wraps the lifecycle functions as ADK `FunctionTool`s, so the **agent itself** can grow the library:

| Tool | When the agent calls it | Notes |
|---|---|---|
| `scaffold_new_skill` | No skill fit, task looks reusable | Only `lean-core` accepted |
| `author_skill_procedure` | Right after scaffolding | Replaces Procedure + Done when; validated; refused once authored |
| `refresh_skill_library` | After scaffolding | Rescans disk; for the preload agent, also reloads its in-memory skills |
| `apply_skill_procedure_delta` | User adds a requirement on a later turn | Append/remove lines only; validated |

Every tool returns a status dict (`ok` / `rejected` / `error` + message) rather than raising, so a failure becomes something the model can read and react to.

This is maturity **level 4**: the library improves from use, with the governor as the brake.

---

<!-- _class: part -->

# Part 5
## What really happened
Saved sessions in `src/skills/agents/{lazy,preload}/.adk/session.db`

---

## Session: "Summarize the Riemann Zeta function" (lazy)

```text
search_skills("Riemann Zeta function summary")  → []
search_skills("math topic summary")             → []
search_skills("scientific topic summary")       → []
list_skills()                                   → <available_skills></available_skills>
scaffold_new_skill(name="riemann-zeta-summary",
    description="Provides a concise summary of the Riemann Zeta function, ...")    → ok
author_skill_procedure(...)  → ok, 0.1.0 → 0.1.1, validation 100%
refresh_skill_library()      → 5 skills, all "newly_preloaded" (since fixed)
```

User: *"I also need references … I should be able to reuse the skill … for other scientific topics."*

```text
apply_skill_procedure_delta(append_procedure_lines=["- [ ] Include 3–4 scholarly references ..."])
  → ok, 0.1.1 → 0.1.2
```

**Lessons:** the delta mechanism worked, but the skill was **named after the instance**. This run is why the generality checks now exist; today `scaffold_skill` rejects that name. The library's `scientific-topic-summary` (with `{topic}`) is the generalized version.

---

## Session: cricket → football → diabetes (lazy)

1. "Write a Wikipedia style article on the game of cricket": 3 empty searches → scaffold `wikipedia-article-writing` with **exclusions "None"**. The authored procedure read:
   > *Identify the standard Wikipedia structure: lead, history, **rules/format, notable events**, cultural impact…*

   "Rules/format" is cricket talking. The first example leaked into the general procedure.
2. "…the game of football": the skill was reused (good).
3. "Generate a wikipedia style article on diabetes": found via search, loaded, followed. A disease has no "rules/format".

**Also in the current procedure:** filler steps such as "Save the final article text" and "End the procedure". A step should be something the model can **do and check**.

The description has since been rewritten with real exclusions (quizzes, study summaries, news blurbs, promotional biographies): version 0.1.2.

---

<!-- _class: small -->

## Sessions: wedding invitation and quiz (lazy)

**Wedding.** Scaffolded with `exclusions="none"` → description ended "Do NOT use for none." The authored procedure kept growing, and the agent itself remarked *"The procedure is extremely long with many repeated steps."* The CHANGELOG for 0.1.3: *"removed runaway generated checklist (repeated steps through 177)"*. Today: 6 steps and a checkable "Done when".

**Quiz.**
- "Create a quiz on soccer" → 5 questions. User: *"I want 10 of them at least."* → `apply_skill_procedure_delta(append "Ensure the quiz contains at least 10 questions")` → 0.1.0 → 0.1.1. A textbook delta.
- But the template's `<common-path step…>` placeholders stayed in the body; the model said *"The procedure is incomplete … we need to interpret."* Validation was 100% throughout (previous part).

**Pattern across sessions:** the mechanics (scaffold, delta, version, changelog) worked every time. What failed was **content quality**: instance-baking, empty exclusions, runaway or placeholder steps. That's what review and better tests are for.

---

## Session: "Give me a summary of skills as used in agents" (preload)

```text
search_skills("summary of skills used in agents")  → []
search_skills("skills")                             → []
list_skills<|channel|>commentary()                  → tool not found
   user: "what are the skills available"
list_skills()                                       → 6 skills
```

- Both searches came back empty **by design**: in preload mode ADK filters out every preloaded skill (Part 3, surprise 1). The agent concluded *"Maybe the skill library is empty?"*
- Then a Harmony token broke the tool name, and the user had to re-ask. The sanitizer now repairs this automatically.
- Later in the same session the user asked for "a bibliography section with at least 3 books" on a Wikipedia article. The agent added it to the answer but did **not** record it in the skill. Compare the quiz session, where the same kind of follow-up did produce a delta. The instruction is a request, not a guarantee.

---

<!-- _class: part -->

# Part 6
## Running it, pitfalls, takeaways

---

## Commands

```bash
uv sync                                                      # install
uv run skillcraft-demo --list-skills                         # no LLM: manifest + disk scan
uv run skillcraft-governor --test-type firing --min-accuracy 0.75
uv run skillcraft-governor --test-type validation
uv run skillcraft-governor --test-type all                   # firing + validation + script, no LLM
uv run skillcraft-governor --test-type all --with-behaviour  # + LLM behaviour tests
uv run skillcraft-demo "Clean this transcript: group O and logic errors"          # preload
uv run skillcraft-demo --lazy "Clean this transcript: group O and logic errors"   # lazy
uv run adk web src/skills/agents                             # pick "preload" or "lazy"
uv run pytest tests/ -v
```

**Expected tool sequence** for the transcript prompt (preload):
`list_skills` → `load_skill('transcript-cleaner')` → `load_skill_resource('references/glossary.md')` → `run_skill_script('scripts/normalize.py', …)` → `load_skill_resource('assets/voice-guide.md')` → reply with ticked checklist and "Done when" confirmed.

None of the saved sessions exercised `run_skill_script`, so watch this one live.

---

<!-- _class: small -->

## What `normalize.py` does

```python
FILLER_PATTERN = re.compile(r"(?:,\s*)?\b(?:um+|uh+|you know)\b,?|\blike,(?=\s)", flags=re.IGNORECASE)
cleaned = FILLER_PATTERN.sub("", text)   # then tidy spaces before punctuation, trim
```

| Input | Output |
|---|---|
| `Ummm I think uhh yes` | `I think yes` |
| `So um the model, you know, converges` | `So the model converges` (the filler's commas go too) |
| `It's like, really fast and I like this approach` | `It's really fast and I like this approach` ("like," as a pause only) |
| `So group O optimizes the logic` | unchanged: fixing jargon needs judgment, so Step 3 leaves it to the model |

**How the agent calls it.** The procedure says to pass the transcript as a positional argument, so ADK runs `normalize.py -- "<text>"`. The script drops a leading `--` before joining its arguments; otherwise `--` would end up in the cleaned text. `check_totals.py` does the same, and reads its JSON from the arguments, because the agent gives scripts no stdin.

These are exactly the cases in `tests/script_cases.yaml`, run the same way the agent runs the script.

---

<!-- _class: small -->

## Pitfalls (1/2): loading and running skills

| Pitfall | Where | Effect | Fix |
|---|---|---|---|
| Script tested differently from how the agent calls it | `scripts/` | Passes by hand, fails through `run_skill_script` (no stdin; `--` before positional args) | Read input from `sys.argv`, drop a leading `--`, test with `script_cases.yaml` |
| Preload hides skills from `search_skills` | ADK `SearchSkillsTool` | Empty searches in preload mode | Use `list_skills` when preloaded |
| `UnsafeLocalCodeExecutor` | `agent_factory.py` | Scripts run with your permissions | Sandbox in production |

---

<!-- _class: small -->

## Pitfalls (2/2): search, tests and governance

| Pitfall | Where | Effect | Fix |
|---|---|---|---|
| Firing tests ≠ live search | `semantic_search.py` | Tests pass, agent still misses | Also check `search_skills` scores for each test prompt |
| Hard-coded stems and cues | `semantic_search.py` | Tuned to these 8 skills | Move them into each skill's tests or metadata |
| Validation is structural | scaffold defaults | Template placeholders pass at 100% | Add `must_not_contain` cases for template text |
| `status: draft` isn't enforced | `skill_loader.py` | Draft skills are loaded and offered like active ones | Filter on manifest status |
| Private ADK APIs | `_read_skill_properties`, `toolset._registry`, `toolset._skills` | May break on an ADK upgrade | Pin the version; wrap access in one place |

---

## Takeaways

1. **A skill = a description, a procedure, and a stop condition** (⟨I, π, β⟩). Each fails in its own way and gets its own tests.
2. **Progressive disclosure** keeps the always-on cost to one line per skill; bodies and files load only on demand.
3. **The description is a classifier.** It's scored by cosine similarity against the request, so write it with trigger words *and* named exclusions.
4. **Move arithmetic and string fixing into scripts.** Then test the scripts the way they're actually called.
5. **Edit by deltas, gate by tests, roll back on regression.** "Never worse than before": $v_1 \ge v_0$.
6. **Tests check what you thought of.** Structural validation let template placeholders through; each real failure should become a new case.
7. **Agents can grow their own library.** The mechanics worked in every saved session; the content needed human review every time.

---

<!-- _class: small -->

## Exercises (1/3): break a description

Full steps and expected output: `docs/LEARNING_GUIDE.md`, section 6.

No LLM needed.

1. `uv run skillcraft-governor --skill transcript-cleaner`. **Expect** `PASS — 4/4 (100%)`.
2. Set transcript-cleaner's description to `Helps with text.` and rerun. **Expect** `FAIL — 2/4`: the *summarize* and *translate* prompts now fire. Which rules let them through? (No exclusion zone any more; the skill **name** still says "transcript".) This is the **god skill** direction.
3. Add a should-fire case without the words *transcript*, *clean*, *text*: "De-mangle this Assembly.ai lecture output: GRPO came out as group O." **Expect** `3/5`: a real request is missed, the **silent skill**.
4. Restore the description (**expect** `5/5`), then remove the extra case.

---

## Exercises (2/3): scaffold, test, retire `meeting-notes`

No LLM needed.

1. Scaffold it and run the firing governor before editing. **Expect** `1/2`: the two placeholder prompts are nearly identical, so one is always wrong.
2. Run `--test-type validation`. **Expect** `3/3` even with `<common-path step…>` still in the procedure. Add `must_not_contain: "<common-path step"` (**expect** `3/4`), then write real steps.
3. Write real firing cases and exclusions until both gates pass; `--list-skills` shows 9. Retire it with `skillcraft-remove`; back to 8.

---

## Exercises (3/3): agent and scripts

1. **Trace disclosure.** Run the transcript prompt with and without `--lazy`. List the tool calls and mark each L1, L2 or L3. **Expect** `Startup: 8 skills loaded into memory` vs. `Startup: 0 skills in agent memory`, and `list_skills` vs. `search_skills` for discovery.
2. **Add a script case.** Give `quarterly-report` a case where engineering + S&M ≠ total cost, expecting exit code 1 and `Cost mismatch`. Run `--test-type script`.
3. **Memory vs. disk.** Run `uv run pytest tests/test_lifecycle_tools.py -v`. Read the two tests on the preload and lazy agents' memory, and explain with Part 3 what would break in each agent if they failed.
4. **Tune τ.** Set `SKILL_SEARCH_SIMILARITY_THRESHOLD` to 0.25 and 0.50 and rerun the firing governor. Which skills change, and in which direction (silent or god)?
