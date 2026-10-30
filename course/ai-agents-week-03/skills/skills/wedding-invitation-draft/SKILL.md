---
name: wedding-invitation-draft
description: >-
  Drafts a formal wedding invitation from couple names, date, time, venue,
  dress code, and RSVP details. Use when the user asks to draft a wedding
  invitation, create a wedding invite, or fill a wedding invitation template.
  Do NOT use for birthday party cards, thank-you notes, save-the-date emails,
  or wedding speeches.
version: "0.1.3"
---

# Wedding Invitation Drafting

## When to use

Reinforce the trigger and name explicit negatives (teach students: bound I):

- Use when: the user asks to draft a wedding invitation, create a wedding invite, or fill a wedding invitation template.
- Do NOT use for: birthday party cards, thank-you notes, save-the-date emails, or wedding speeches.

## Procedure

Checklist-carrier pattern — use ``{placeholder}`` for per-request inputs:

- [ ] Step 1: Extract ``{couple_names}``, ``{date}``, ``{time}``, and ``{venue}`` from the user message.
- [ ] Step 2: Extract optional ``{dress_code}`` and ``{rsvp}`` details if given.
- [ ] Step 3: If any mandatory field (``{couple_names}``, ``{date}``, ``{time}``, ``{venue}``) is missing, ask the user for it before drafting.
- [ ] Step 4: Draft the invitation in a formal register, incorporating any requested tone (formal, casual, whimsical).
- [ ] Step 5: Verify every mandatory field appears in the draft; include dress code and RSVP lines only when provided.
- [ ] Step 6: Present the final invitation, formatted for printing or digital sharing.

Do not bake one example couple or venue into the procedure. Do not report
"done" until every box is ticked.

## Done when

The invitation names the couple, date, time, and venue; includes dress code
and RSVP lines when the user supplied them; and matches the requested tone.
