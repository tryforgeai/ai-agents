---
name: scientific-topic-summary
description: >-
  Produces a concise summary of a scientific or technical topic named by the
  user. Use when the user asks to summarize, explain briefly, or give an
  overview of a scientific concept, theorem, algorithm, or function — the
  specific topic comes from the request, not from this skill's name. Do NOT use
  for transcript cleaning, code review, or detailed proofs.
version: "0.1.0"
---

# Scientific Topic Summary

## When to use

- Use when: the user names a scientific or technical topic and wants a short
  summary or overview (e.g. "summarize proximal policy optimization",
  "explain the Riemann zeta function").
- The **topic** is always taken from the user's message — never hard-code one
  topic in the procedure.
- Do NOT use for: transcript cleaning, commit messages, or full derivations.

## Procedure

Copy this checklist into your reply and tick each item as you go:

- [ ] Step 1: Extract `{topic}` from the user request (the subject to summarize).
- [ ] Step 2: Write a concise, accurate **title** for `{topic}`.
- [ ] Step 3: Write a **body** of about 100 words (90–110) explaining what
  `{topic}` is, why it matters, and one key idea.
- [ ] Step 4: List **3–4 references** for further reading on `{topic}` (title +
  URL or citation each).

Do not report "done" until every box is ticked.

## Done when

The user receives a title, a ~100-word body about `{topic}`, and 3–4
authoritative references for further reading.
