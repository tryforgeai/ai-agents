# Idea Scout · Run log

> Append one entry per run. "Suggestions for the skill" are only recorded; you approve them before the skill changes. Uncurated self-modification measured negative in practice (SkillsBench: self-generated skills −1.3 points, curated +16.2).

## 2026-10-11 · Run 1 (skill v1, Chinese report)

- Time: about 30 minutes; about 25 fetch + search calls
- Where it got stuck: two requests failed on the web_fetch URL length limit; the Hugging Face papers page was a stale cache; vendor pages were very long
- Checking found 3 errors in the draft: Riskified's capability overstated, Alby also runs simulated shopping tests, and a CFPB number with no traceable source
- Suggestions for the skill (adopted in v2): verify against primary sources; add checkpoints; add a signal ledger and retraction; compute timestamps with code

## 2026-10-11 · Skill v3

- Skill and data files switched to English; reports are now written in English. The 2026-10-11 report stays in Chinese and in v1 format as history.

## 2026-10-11 · Run 2 (skill v3, English report)

- Time: about 30 minutes; 19 fetch + search calls (budget 40)
- Result: 3 ideas, all 22/30; check_report.py exit 0 on first run
- Independent check (step 8): reopened TestMu, VerifiedX, Cinchor, Conscium and the dots launch post for Idea 1's competitor claims; checked numbers against primary sources (TravelPlanner 0.6%, arXiv 2610.11188 29.5 points, τ-bench 0.460, HN 169/677). Correction caught: a search summary said nobody verifies real-world effects, but TestMu Agent Assurance does (pre-deployment), so Idea 1's competition score dropped from 3 to 2
- Where it got stuck: the Japanese travel search returned general cancellation-policy pages; HN comment dates were not retrieved, so ledger dates are approximate
- Suggestions for the skill (not applied; waiting for approval):
  1. Add `created_at` to the HN `attributesToRetrieve` so ledger dates are exact
  2. When three ideas tie on total score, state the tie-break rule (suggest: pain + edge)
  3. Add a ledger convention for signals seen only in search summaries (e.g. mark "via search, unverified") and let the script WARN on them

## 2026-10-11 · Skill v3.1 (approved by user)

- Run 2 showed the checklist only at the start and fully ticked at the end. Fixed: live progress via the Cowork task list, with re-posting the checklist after every item as the fallback; evidence note per item; partial completion stated.

## 2026-10-11 · Run 3 (skill v3.1)

- Time: about 25 minutes; 17 fetch + search calls (budget 40)
- Result: 2 ideas (23/30 and 19/30 weak), 4 killed; bottom line says "insufficient signal" for a third. check_report.py exit 0
- Progress tracking: 10 Cowork tasks updated one at a time. The user did not see them at first, so the checklist was also posted in chat after each step from step 5 on; the user then confirmed the Progress panel was visible
- Independent check: reopened Bill One, the NTA WooCommerce plugin and the Promptfoo acquisition post; 3 corrections (Bill One's check is stronger than first written; plugin claim verified; an unverified "50+ types" figure removed). Idea 2 not re-verified
- Where it got stuck: one scripted edit failed on a stale string and had to be redone; e-commerce-specific pain signals on HN were thin
- Suggestions for the skill (not applied; waiting for approval):
  1. In Cowork, also post the checklist in chat at the start and after each step by default (the task panel alone was easy to miss), instead of only as a fallback
  2. Clear or archive tasks from earlier runs before creating the 10 new ones, so the Progress panel shows only this run
  3. The three suggestions from run 2 are still open

## 2026-10-11 · Skill v4.0 (approved by user) + company-test review

- User feedback: runs 1–3 produced features and skills, not startup ideas. Root cause: the rubric rewarded weekend-testability and never asked about buyer budget, market size, moat or platform absorption.
- Skill v4: company test gate (buyer, size, moat, platform), company-scope candidates (wedge → expansion → moat), 7-dimension /35 scoring; script and fixtures updated.
- Review of the 9 candidates: 2 companies survive by merging (A: Japan commerce agent environments and evals; B: independent verification layer for back-office agents); 7 killed or merged. 3 searches; market-size inputs are unverified search results.

## 2026-10-11 · Profile correction

- The profile said "knows the Japanese market". That was my inference from the employer, never stated by the user. The user works on Rakuten's US cash-back business and has no Japan-market content experience.
- Impact: Japan-specific wedges in runs 1–3 and both Companies A and B in the review were scored with an edge the user does not have. Both companies are now "needs re-review".
- Fixed profile.md (US cash-back; added a rule: only write what the user said; mark inferences).
- Suggestion for the skill (not applied; waiting for approval): step 1 should flag any profile line marked "(inferred, unconfirmed)" and ask the user before scoring edge on it.

## 2026-10-11 · Skill v4.1 (approved by user)

- Why: every run looked like a red ocean because pain came from Hacker News, i.e. developers' own problems in the most crowded AI layer.
- Changes: industry-first signal sources (SEC full-text search and Federal Register API tested and working; reddit.com is blocked for fetch, so only via search results); at least half of pain signals from industry sources, with a script warning; theme is an industry, not AI tooling; inferred profile lines are asked about instead of scored.
- Still open from earlier runs: HN created_at (now in the source templates), tie-break rule, "via search" ledger marking, default chat checklist in Cowork, clearing old tasks.

## 2026-10-11 · Run 4 (skill v4.1)

- Theme: US e-commerce import, tariff and customs compliance. Result: insufficient signal, 0 ideas; 9 candidates killed (mostly platform/competition: Altana, Tarifflo, Amari, Intertek and others). Report: `2026-10-11 idea-scout-us-ecommerce-customs.md`. check_report.py exit 0, 0 warnings.
- Time: about 15 minutes; 36 fetch + search calls (budget 40). 6 pain signals, all from industry sources (Federal Register, 10-K, job post, trade press, law-firm alert, CPSC rule).
- Independent check: reopened Altana (Fortune), Altana-Cervo (SaasRise), Amari (VCBacked), Intertek, RH 10-K, CBP rule, Bradley, CPSC rule, arXiv ATLAS. Corrections: removed an unsupported claim that Altana already did customs filing (then added it back with a source as S15), removed a "free calculator" claim, downgraded "30+ brokerages" to unverified, softened the CPSC registry claim. Not reopened: Eurofins, Comply PRO+, Lightsource, Zonos and Flexport headlines.
- Where it got stuck: the data folder (`Projects/AI-agents`) was not mounted, so step 1 needed a folder request; the SEC full-text search result was too large and not useful; large fetches are saved to a host path that bash cannot read (use Grep/Read on that path); the CPSC page returned empty (client-rendered); no operator-forum voice (reddit blocked, search returned none).
- Suggestions for the skill (not applied; waiting for approval):
  1. After picking the theme, run 2 crowding searches ("<theme> AI startup raises 2026", "<theme> software") before collecting signals, so a saturated theme is caught in about 5 calls instead of 30
  2. Add to Known pitfalls: large web_fetch results are saved to a file; read them with Grep/Read on the saved path, not bash
  3. Replace the SEC full-text fetch with "WebSearch for 10-K risk-factor phrases, then fetch the specific filing and Grep it" (this worked for RH)
  4. Add non-reddit operator-voice sources (Shopify Community, Amazon seller forums, trade-association pages)
  5. Step 1 should say what to do when the data folder is not mounted (request the folder), and SKILL.md paths should match the vault (the project folder copy still shows an old description and old paths)
  6. Open from earlier runs: tie-break rule, "via search" marking, default chat checklist in Cowork, clearing old tasks

## 2026-10-11 · Run 5 (skill v4.1)

- Theme: US shopping cash-back, rewards and affiliate loyalty (user asked for a theme closer to cash-back and said conflict of interest is not a concern; recorded in profile.md). Result: 1 idea at 25/35 (independent attribution-integrity auditor for multi-network affiliate advertisers), 5 killed. Report: `2026-10-11 idea-scout-us-cashback-rewards.md`. check_report.py exit 0, 0 warnings.
- Time: about 30 minutes; 29 fetch + search calls (budget 40). 7 pain signals, all from industry sources (Ibotta 10-K, trade press on the Honey case, two job posts, Adweek via ATDb, PMA summary).
- Independent check: reopened the Ibotta 10-K, PPC Land (Honey, Rakuten SDK), Impact.com help page, Bluepear, both job posts and the Everflow/PMA summary. Corrections: exact SDK quote, spend noted as $13.62B on the PMA page vs $13.63B in coverage, added Impact.com monitoring evidence. Not verified: Marcode (fetch timed out), Phia funding, Wildfire, Minty, Bureau vendor list, PartnerCentric.
- Where it got stuck: Reddit still unreachable for operator voice; the SEC route was replaced by fetching the Ibotta filing from its investor site and Grep-ing the saved file, which worked; one fetch timed out at 180 seconds; PMA primary page was not opened (only via search).
- Weak points of the idea: platform test is borderline; the advertiser count and price are estimates; competitor Marcode's scope is unverified.
- Suggestions for the skill (not applied; waiting for approval):
  1. Add a rule for a borderline test: a candidate that passes only on one stated argument should carry that argument in its kill criteria and be listed first under "For you to decide" (done by hand this run)
  2. Add "fetch the company's own investor-site filing, then Grep" as the preferred 10-K route in signal-sources.md (worked for Ibotta and RH)
  3. Add a ledger type "market" for sizing inputs so they are not counted as pain (done by hand this run)
  4. Ledger IDs added late (S19) break the numeric order; either allow re-numbering before the final check or note it as acceptable
  5. Open from earlier runs: tie-break rule, default chat checklist in Cowork, clearing old tasks (task list now has 20 items from two runs)

## 2026-10-11 · Run 6 (skill v4.2)

- Theme: US e-commerce and subscription consumer-protection compliance (auto-renewal, pricing and fees, reviews, endorsements). Chosen by the skill at the user's request; the last two runs were customs and cash-back. Result: 1 idea at 25/35 (continuous consumer-protection flow auditor for subscription/DTC brands), 5 killed. Report: `2026-10-11 idea-scout-us-ecommerce-consumer-protection.md`. check_report.py exit 0, 0 warnings.
- Time: about 35 minutes; 21 fetch + search calls (budget 40), plus a verification subagent (about 17 tool calls of its own). 9 pain signals, all from industry sources (2 Federal Register ANPRMs, 2 10-Ks, law-firm alerts, a job post, an insurer blog).
- Crowding check first (run-4 suggestion, applied by hand): 2 searches showed financial-services marketing compliance is crowded (Blee, Haast), so the theme was steered to e-commerce flows.
- Independent check (subagent with only the report path): S10, S11, S12, S15, S9 verified; S1/S2 relabelled from "proposed rule" to ANPRM; S14 corrected (date, $105M price unverified); removed the claim that Stripe disclaims legal advice. The subagent could not re-fetch Benesch (duplicate-fetch block); its figures were verified from the main run's full fetch.
- Where it got stuck: the data folder was not mounted again (folder request needed); no first-hand operator voice (forums); the 10-K route via site:sec.gov search + fetch + Grep worked (Bark); the 10-K page was 122k characters, Grep with short windows was needed because matches sit on one huge line.
- Suggestions for the skill (not applied; waiting for approval):
  1. Make the 2-search crowding check after picking the theme a formal step (it saved a crowded sub-theme this run)
  2. Tell the verification subagent that pages fetched in the main run may be blocked from re-fetch for an hour, and pass it the main run's quotes for those sources
  3. Add "site:sec.gov 10-K <phrase>" search → fetch → Grep with ≤ 250-character windows to signal-sources.md section A
  4. SKILL.md still names `Projects/AI-agents/skills/startup-idea-scout/` as the skill folder, but the skill files live in `Projects/startup-idea-scout/`; align the paths
  5. Open from earlier runs: tie-break rule, default chat checklist in Cowork, ledger renumbering
