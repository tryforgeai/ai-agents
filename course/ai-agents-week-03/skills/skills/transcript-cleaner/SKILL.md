---
name: transcript-cleaner
description: >-
  Cleans raw speech-to-text lecture transcripts. Use when the user provides a
  noisy or mangled transcript inline or in a file (e.g. from Assembly.ai) and
  asks to clean, normalize, fix jargon, or de-mangle it. Short text after
  "Clean this transcript:" counts as the input. Do NOT use for summarization or
  translation.
version: "0.1.0"
---

# Transcript Cleaner

## When to use

- Use when: the user supplies a noisy lecture or meeting transcript and wants
  jargon restored, accent-induced substitutions fixed, or readable prose.
- The transcript may appear inline in the user message (quoted or after a colon);
  a separate file is not required.
- Do NOT use for: summarization, translation, or generating new content from
  scratch.

## Procedure

Copy this checklist into your reply and tick each item as you go:

- [ ] Step 1: Load `references/glossary.md` for recurring jargon before editing.
- [ ] Step 2: Run `scripts/normalize.py` with the raw transcript text as a
  positional argument (via `run_skill_script`) for deterministic fixes.
- [ ] Step 3: Repair accent-induced substitutions, preserving the author's voice
  (see `assets/voice-guide.md` for style exemplars).
- [ ] Step 4: Verify no glossary term was left in mangled form.

Do not report "done" until every box is ticked.

## Done when

The transcript reads as clean publishable prose, technical terms match the
glossary, and the author's tone is preserved.
