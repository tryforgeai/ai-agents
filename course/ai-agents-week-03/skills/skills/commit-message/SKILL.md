---
name: commit-message
description: >-
  Drafts conventional commit messages from git diffs following team format.
  Use when the user asks for a commit message, reviews staged changes, or
  wants help writing a PR title from a diff. Do NOT use for code review
  feedback or release notes.
version: "0.1.0"
---

# Commit Message

## When to use

- Use when: the user shares a diff or asks for a commit / PR title.
- Do NOT use for: full code review, architecture critique, or changelog entries.

## Procedure

Copy this checklist into your reply and tick each item as you go:

- [ ] Step 1: Read `references/format.md` for the team's conventional format.
- [ ] Step 2: Identify change type (feat, fix, docs, refactor, test, chore).
- [ ] Step 3: Write subject line ≤ 72 chars: `<type>(<scope>): <summary>`.
- [ ] Step 4: Add body explaining **why**, not just what changed.
- [ ] Step 5: List breaking changes or migration notes if any.

Do not report "done" until every box is ticked.

## Done when

A complete conventional commit message (subject + optional body) is ready to paste.
