# Study guide — transcript-cleaner walkthrough

**For instructors and students.** This file is L3 material — the agent loads it
only when pointed here; it does not bloat the lean core.

## Map of the skill folder

```
transcript-cleaner/
  SKILL.md              ← L1 + L2 (always loaded together via load_skill)
  references/
    glossary.md         ← L3 (loaded when procedure says so)
    STUDY_GUIDE.md      ← L3 (this file — human study guide)
  assets/
    voice-guide.md      ← L3 (style exemplars)
  scripts/
    normalize.py        ← L3 (run, don't read into context)
  tests/
    firing_cases.yaml   ← governor: description triggers (I)
    validation_cases.yaml ← governor: procedure structure (π)
```

## SKILL.md annotated

### Frontmatter — initiation set **I**

```yaml
name: transcript-cleaner          # MUST match folder name (ADK enforces)
description: >-                   # HIGHEST-LEVERAGE LINE in the skill
  Cleans raw speech-to-text ...
  Use when ... noisy ... de-mangle ...
  Do NOT use for summarization or translation.
version: "0.1.0"
```

**Class questions:**
- Why third person? (Router reads it, not the end user.)
- Why literal triggers ("Assembly.ai", "de-mangle")?
- Why exclusions? (Prevents god-skill / trigger collision.)

### Procedure — policy **π**

The checklist pattern from instructor theory keeps long tasks coherent:

1. Load glossary (L3 deferral — not in core)
2. Run script (deterministic — zero reasoning tokens)
3. Repair by meaning (judgment — model reasoning)
4. Verify glossary coverage (termination check)

### Done when — termination **β**

Without this section, the agent does not know when to stop. Compare to RL
options framework termination condition.

## Anti-patterns to demo in class

| Anti-pattern | Demo |
|--------------|------|
| Vague description (god skill + silent skill) | Change description to "Helps with text." → governor fails 2/4: the summarize and translate prompts now fire. A cleaning request without the words transcript / clean / text is then missed. See `docs/LEARNING_GUIDE.md`, Exercise 2 |
| Kitchen-sink | Paste entire glossary into SKILL.md → context cost |
| Leaky script | Script that writes outside skill dir → discuss sandboxing |

## Exercise

Add a new glossary row for a term your STT model mangles. Run
``skillcraft-governor --test-type validation`` — procedure edits must pass
validation tests. Firing tests (``--test-type firing``) only change if you
edit the frontmatter description.
