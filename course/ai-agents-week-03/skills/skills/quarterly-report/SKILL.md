---
name: quarterly-report
description: >-
  Fills a quarterly business review (QBR) from supplied metrics using the
  canonical template. Use when a full QBR is requested and numeric metrics are
  available. Do NOT use when metrics are missing or when only a narrative
  summary is needed.
version: "0.1.0"
---

# Quarterly Report

## When to use

- Use when: the user requests a QBR / quarterly report and provides metrics.
- Do NOT use for: executive summaries without metrics, or ad-hoc slide decks.

## Procedure

Copy this checklist into your reply and tick each item as you go:

- [ ] Step 1: Load `assets/qbr-template.md` — the canonical section order.
- [ ] Step 2: For each section, fill from supplied metrics; never invent numbers.
- [ ] Step 3: Run `scripts/check_totals.py` with the metrics JSON to validate
  subtotals reconcile.
- [ ] Step 4: Confirm no placeholder tokens remain.

Do not report "done" until every box is ticked.

## Done when

Every template section is filled, totals reconcile, and no placeholder remains.
