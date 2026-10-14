---
date: 2026-10-11
type: startup-idea-scout-review
scope: re-review of the 9 candidates from runs 1–3 under skill v4 (company test)
tags: [startup, idea-scout, review]
---

# Company-test review of runs 1–3

> Runs 1–3 sized ideas to a weekend experiment, so most of them are features. This review applies the v4 company test (buyer, size, moat, platform) to all 9 candidates, merges the ones that only make sense together, and kills the rest. Market-size inputs come from search results and are marked; nothing here has been checked against primary sources yet (that is step 8 of the next proper run).

## Bottom line

**Two companies survive, both by merging smaller ideas.**

1. **Japan commerce agent environments and evals** (merges three candidates): sell Japanese e-commerce, travel and merchant-operations environments, rewards and evals to AI labs and to the Japanese platforms building agents. It has the strongest edge and a real, already-paying buyer (labs), but it needs an employment and IP check first because it sits close to your day job.
2. **Independent verification layer for back-office agents in Japan** (merges two candidates): check facts before an agent acts and reconcile what it did afterwards, with an audit trail, for finance and operations teams. Buyer and size are plausible, but the platform test is borderline: invoice SaaS and agent platforms could add parts of it.

Everything else fails at least one test, usually **platform** (a big player will ship it as a feature) or **buyer** (no one pays separately for it).

## Company test, all 9 candidates

| # | Candidate (run) | Buyer | Size | Moat | Platform | Verdict |
|---|---|---|---|---|---|---|
| 1 | AI-drafted claim triage desk (1) | pass | pass | weak | **fail**: Riskified already scores refund claims; Zendesk/Gorgias can add text checks | killed as standalone |
| 2 | Japanese e-commerce operator agent environment (1) | pass | pass | pass | pass | **merged into Company A** |
| 3 | Store testing with simulated AI shoppers (1) | weak | pass | weak | **fail**: Alby, Stellagent; Shopify-style platforms will ship readiness checks | folded into A as a module |
| 4 | MCP / tool-interface regression testing (1) | **fail**: no separate budget | fail | fail | fail | killed: feature |
| 5 | Outcome reconciliation for back-office agents (2) | pass | pass | pass | borderline | **merged into Company B** |
| 6 | Japanese lodging booking-agent eval environment (2) | pass | pass | pass | pass | **merged into Company A** |
| 7 | Freshness/taint checks for agent knowledge (2) | **fail**: free open-source tools | fail | fail | **fail**: coding-agent vendors | killed: feature |
| 8 | Trusted-fact layer for untrusted documents (3) | pass | pass | pass | borderline | **merged into Company B** |
| 9 | Japanese name/address capture for voice agents (3) | weak | fail | fail | **fail**: Amazon Connect, NTT and other voice platforms | killed: feature |

## Company A: Japan commerce agent environments and evals

- **One-liner**: The supplier of Japanese commerce environments for training and testing AI agents. Simulated stores, marketplaces, booking systems and merchant back offices follow Japanese rules (points, campaign calendars, tiered cancellation fees, invoice rules) and score each run by its final state.
- **Company shape**:
  - **Wedge**: a lodging and e-commerce environment pack sold to one AI lab or agent builder.
  - **Expansion**: a catalogue of Japanese enterprise workflows (retail, travel, logistics, accounting), plus an "agent-ready for Japan" certification and evaluation service for Japanese platforms deploying agents.
  - **Moat**: domain fidelity, a growing catalogue of reward hacks and failure cases, and relationships with Japanese platforms.
- **Who pays**: AI labs and agent companies that need non-US, non-English domains; Japanese platforms (marketplaces, OTAs, payment companies) shipping agents that need pre-launch evaluation.
- **Business model**: per-environment and per-task contracts with labs; annual evaluation subscriptions for platforms.
- **Market size (estimate)**:
  - **Lab pricing**: environment tasks sell for roughly $200–2,000 each, with contracts often six to seven figures per quarter (Epoch AI, [via search](https://www.cxodigitalpulse.com/?p=42733)).
  - **Lab spend**: Wing VC estimates one large lab spends tens of millions a year on environment vendors and expects aggregate spend to grow 3–5× into 2026 ([via search](https://www.wing.vc/content/rl-environments-for-agentic-ai-who-will-win-the-training-verification-layer-by-2030)).
  - **Path to ¥1B (estimate)**: three lab contracts at $1M a year, plus 20 Japanese platform subscriptions at ¥10M a year.
- **Platform risk**: labs build environments in-house, and generalist vendors (Mercor, which bought Deeptune; Mechanize) could add Japanese domains. Defense: Japanese commerce rules are niche, constantly changing and expensive to learn without local operators; generalists prioritise coding and computer use.
- **Your edge**: the strongest of any candidate. You have Rakuten commerce and travel knowledge, speak Japanese, and the course pointed you at "environment + reward + eval" as the layer worth building.
- **First validation**: build one lodging scenario on τ³-bench plus one marketplace-operations scenario on StoreBench's public tasks, then show them to two environment vendors and two Japanese agent teams. **Pass criteria**: at least one says it would pay for a pilot, or a vendor offers to resell it.
- **Biggest unknown**: whether labs want Japanese commerce specifically, or only "more diverse domains" at a lower price.
- **Must decide first**: this is close to Rakuten's business. Check your employment contract and conflict-of-interest rules before building or talking to anyone, and never use internal data.

## Company B: Independent verification layer for back-office agents in Japan

- **One-liner**: An independent "assurance layer" for finance and operations agents. Before an agent acts, it checks the facts the decision relies on (rates, tax, dates, registration numbers, bank details). After the agent acts, it reconciles what the agent claimed against the systems of record. Both steps produce an audit trail that finance and compliance teams can sign off on.
- **Company shape**:
  - **Wedge**: supplier-invoice and refund agents at mid-sized Japanese e-commerce companies.
  - **Expansion**: every back-office agent (procurement, accounts payable, order operations, CRM), across vendors, as the independent check that auditors accept.
  - **Moat**: connectors to Japanese accounting, ERP and EC systems; a growing library of false-fact attacks and agent failure cases; audit-standard status once accounting firms rely on it.
- **Who pays**: CFOs and heads of operations at mid-sized companies already paying for back-office SaaS; later, auditors and insurers.
- **Business model**: subscription per connected agent or workflow, plus per-document volume.
- **Market size (estimate)**:
  - **Spend benchmark**: Japanese companies already pay heavily for back-office SaaS. Sansan's group ARR was about ¥50B for FY2026, with Bill One ARR growing about 35% (secondary summary, [via search](https://quartr.com/events/sansan-inc-4443-q4-2026_FVWnUuyW)).
  - **Path to ¥1B (estimate)**: 800 mid-sized customers × ¥1.2M a year. The buyer count is an estimate and is unverified.
- **Platform risk (borderline)**: Bill One and other invoice SaaS already check invoice fields, and agent platforms are adding testing (OpenAI is acquiring Promptfoo). Defense: platforms verify their own agents, while a company running agents from several vendors needs one independent check. This is the course's lesson that a verifier must be independent of the generator. If interviews show buyers trust the platform's own checks, this fails.
- **Your edge**: verifier and ledger concepts from the course, the data-fix agent use case, and e-commerce back-office knowledge.
- **First validation**: interview 10 finance or operations leads at Japanese EC companies about which agents touch their books and how they verify them today; demo the false-fact checker and a reconciliation report on synthetic data. **Pass criteria**: at least 3 describe a real incident or audit question, and at least 2 agree to a paid pilot.
- **Biggest unknown**: whether mid-sized Japanese companies deploy enough back-office agents in the next 12–18 months for an independent layer to matter.

## Killed, and why

- **Claim triage desk (standalone)**: platform fail. Riskified already scores refund claims, and customer-service platforms can add text checks. Its Japan-specific evidence was also never confirmed.
- **Simulated AI shopper testing (standalone)**: Alby and Stellagent already do it, and commerce platforms will ship readiness checks. It survives only as a module of Company A.
- **MCP regression testing, knowledge freshness checks, voice name/address capture**: features. Either free tools or the platforms themselves cover them, and no buyer has a separate budget.

## What changed in the scores

Old scores (/30) measured "good weekend experiment". None of them carry over. Companies A and B have not been scored on the new /35 scale because their market-size inputs are still unverified search results; the next proper run should score them after step 8.

## Sources

- https://www.cxodigitalpulse.com/?p=42733
- https://www.wing.vc/content/rl-environments-for-agentic-ai-who-will-win-the-training-verification-layer-by-2030
- https://quartr.com/events/sansan-inc-4443-q4-2026_FVWnUuyW
- https://fortune.com/2026/03/19/andreessen-horowitz-ai-startups-deeptune-series-a
- https://www.mechanize.work/blog/cheap-rl-tasks-will-waste-compute/
