---
name: pii-guardrail
description: >-
  Enforces the PII-handling policy. Use whenever a task reads, writes, or
  transmits personal data (names, emails, phone numbers, government IDs).
  Fires assertively; this is a hard constraint. Do NOT use for purely public
  or anonymized aggregate data.
version: "0.1.0"
---

# PII Guardrail

## When to use

- Use when: any step would read, write, log, or transmit personal data.
- Do NOT use for: fully anonymized aggregates with no re-identification risk.

## Procedure

1. Detect whether the task touches personal data.
2. If yes, verify all policy checks:
   - Data minimization: only fields strictly required are used.
   - No PII in logs, commit messages, or skill outputs sent externally.
   - Redact before displaying examples (show `***` for emails/phones).
3. If any check fails, **REFUSE** and explain which policy was violated.
4. Otherwise proceed and log the allow/refuse decision in the reply.

## Done when

A clear allow or refuse decision has been issued and logged with the checks
performed.
