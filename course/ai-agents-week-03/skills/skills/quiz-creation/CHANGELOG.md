# Changelog — quiz-creation

## 0.1.0 — 2026-07-10

- Scaffolded from lean-core template (lean-core).

## 0.1.1 — 2026-07-10

- Added requirement for minimum 10 questions.
- Procedure append: '- [ ] Step 4: Ensure the quiz contains at least 10 questions.'
- Done-when append: '- Quiz contains at least 10 questions.'

## 0.1.2 — 2026-10-04

- Replaced the empty exclusion with encyclopedia articles, study summaries, and exam grading.
- Replaced placeholder firing cases with real should-fire and should-not-fire prompts.

- 0.1.3: Procedure placeholders (<common-path step>, <definition-of-done check>) replaced with real steps; scaffold Done-when boilerplate replaced with a checkable termination.

## 0.1.4 — 2026-10-08

- Added generalized checks for output precision, single‑choice enforcement, loop‑count clarity, and type/value distinction.
- Procedure append: '[ ] Step 9: Verify that each option string exactly matches the actual runtime output (e.g., include full class names, quotes, and type distinctions).'
- Procedure append: '[ ] Step 10: Confirm that a single‑choice question has exactly one correct option; flag the question if multiple options match the expected output.'
- Procedure append: '[ ] Step 11: For loop‑count questions, explicitly state the required initial variable value and loop exit condition required for correct iteration.'
- Procedure append: '[ ] Step 12: Distinguish between value and type in options, ensuring no ambiguity (e.g., integer vs. string labels).'
- Done-when append: '- The quiz verifies that each option string is exactly the same as the runtime output.'
- Done-when append: '- Single‑choice questions are validated to have only one correct option; duplicates are rejected.'
- Done-when append: '- Loop‑count questions must specify initial value and exit condition to avoid ambiguity.'
- Done-when append: '- Options that merely state a type or value without clear distinction are flagged.'

## 0.1.5 — 2026-10-08

- Corrected exact-output checks to require only the correct option to match; distractors must be incorrect.
- Distinguished printed output from value representations and type labels.
- Moved all checks before delivery, normalized checklist formatting, and removed redundant checks.
- Required sufficient loop context and correction of ambiguous options before delivery.
