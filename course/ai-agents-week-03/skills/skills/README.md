# Skill Library — Instructor Notes

Human-readable guide to the **artifact layer** (`skills/`). For Python/orchestration,
see `docs/LEARNING_GUIDE.md` and `src/skills/`.

## Why a folder of plain text?

Instructor theory emphasizes four properties of skill-as-folder:

1. **Inspectable** — you read exactly what the agent will be told
2. **Diffable** — git review like any other code
3. **Portable** — zip, share, [agentskills.io](https://agentskills.io/) standard
4. **Authorable** — domain experts write prose; engineers write scripts

## Layout (maps to progressive disclosure)

```
skills/
  manifest.yaml              # Level 2 curation: versions, patterns, status
  <skill-name>/
    SKILL.md                   # L1 frontmatter + L2 procedure (required)
    references/                # L3: read on demand (glossaries, API notes)
    assets/                    # L3: templates, style guides, schemas
    scripts/                   # L3: run on demand (deterministic steps)
    CHANGELOG.md               # audit trail for procedure edits
    tests/
      firing_cases.yaml        # governor: test description triggers (I)
      validation_cases.yaml    # governor: test procedure structure (π)
```

### Reading any SKILL.md — find ⟨I, π, β⟩

| Symbol | Meaning from instructor theory | In SKILL.md |
|--------|-------------------------------|-------------|
| **I** | Initiation set (trigger) | `description` in frontmatter |
| **π** | Policy (procedure) | `## Procedure` section |
| **β** | Termination | `## Done when` section |

## Exemplar walkthrough

Open `transcript-cleaner/` alongside `references/STUDY_GUIDE.md` for a line-by-line
annotated tour of the lean-core pattern.

## Included skills (pattern catalog)

| Skill | Pattern | What to notice |
|-------|---------|----------------|
| `transcript-cleaner` | Lean core + appendix | Glossary in `references/`, not SKILL.md |
| `quarterly-report` | Template bearer | Template in `assets/`, validator in `scripts/` |
| `pii-guardrail` | Guardrail | Explicit **REFUSE** path — no checklist needed |
| `commit-message` | Checklist carrier | Copy-paste checklist in Procedure |

## Adding a skill gradually (student lab)

```bash
# 1. Scaffold lean-core skeleton from instructor theory
uv run skillcraft-scaffold \
  --name my-new-skill \
  --description "Does X for Y. Use when ... Do NOT use for ..."

# 2. Author — keep SKILL.md scannable; defer rare cases
# 3. Write real firing + validation cases (replace placeholders!)
# 4. Gate before merge
uv run skillcraft-governor --test-type firing --skill my-new-skill
uv run skillcraft-governor --test-type validation --skill my-new-skill

# 5. Verify discovery (no agent code change)
uv run skillcraft-demo --list-skills
```

## Editing existing procedures

Use **incremental deltas** — not full SKILL.md rewrites (instructor theory):

```python
from skills.skill_lifecycle import ProcedureDelta, TextReplacement, apply_procedure_delta

apply_procedure_delta(
    skill_name="transcript-cleaner",
    delta=ProcedureDelta(
        append_procedure_lines=("- [ ] Step 5: Verify formatting.",),
    ),
    changelog_note="Add formatting verification step",
)
```

1. Change only π / β via ``ProcedureDelta`` — never bloat the description (I)
2. Version bump and ``CHANGELOG.md`` entries are applied automatically on accept
3. Run ``skillcraft-governor --test-type validation`` — rejected deltas roll back

To **remove** a checklist line, pass its exact text (without depending on
``TextReplacement`` with an empty string):

```python
apply_procedure_delta(
    skill_name="transcript-cleaner",
    delta=ProcedureDelta(
        remove_procedure_lines=("- [ ] Step 4: Verify no glossary term was left in mangled form.",),
    ),
    changelog_note="Drop redundant glossary verification step",
)
```

## Code vs prose boundary (teach this explicitly)

| Write as **script** | Write as **prose** |
|---------------------|-------------------|
| Deterministic string fixes | Judgment / voice preservation |
| Arithmetic validation | Policy interpretation |
| Schema checks | When to refuse vs proceed |

Scripts run **outside** the context window — cheaper and more exact per instructor
theory on the code/prose decision rule.
