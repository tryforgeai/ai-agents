# Idea status table

> Cross-run idea ledger. `startup-idea-scout` reads it in step 1 to avoid repeats and appends new ideas as "candidate" in step 10.
> You fill in "passed / killed" after running a weekend experiment or interviews. That is the only verification signal from the real world, and it is more reliable than any score.

| Idea | First seen | Status | Evidence / notes |
|---|---|---|---|
| AI-drafted claim triage desk | 2026-10-11 | killed | 24/30; run 2 added hotel evidence (HN 50048713) |
| Training and eval environment for Japanese e-commerce operator agents | 2026-10-11 | merged | 23/30 |
| End-to-end store testing with simulated AI shoppers | 2026-10-11 | merged | 23/30; study Stellagent and Alby first |
| Agent-experience regression testing for MCP and tool interfaces | 2026-10-11 | killed | 20/30, weak |
| LLM judge calibration service | 2026-10-11 | killed | Galileo, Patronus, FutureAGI already do it |
| AI phone reception for Japanese restaurants and shops | 2026-10-11 | killed | NTT docomo, LINE AiCall, もしもしAI |
| GEO / AI search visibility | 2026-10-11 | killed | Profound and others |
| Agent spending limits and rule controls | 2026-10-11 | killed | Authoryze, Visa, Mastercard; run 3 found new consumer-side evidence (HN 49980053) |
| Model-picker tool for developers | 2026-10-11 | killed | No competitor search done; judgment unverified |
| Outcome reconciliation for back-office agents | 2026-10-11 (run 2) | merged | 22/30; check TestMu Agent Assurance scope first; run 3 added legal-authority evidence |
| Evaluation environment for Japanese lodging booking agents | 2026-10-11 (run 2) | merged | 22/30 |
| Freshness and taint checks for team agent knowledge | 2026-10-11 (run 2) | killed | 22/30; free OSS tools are the main risk |
| Plan-vs-implementation checker for agent PRs | 2026-10-11 (run 2) | killed | Kiro, Traycer, Intent, PlanBridge |
| Permission-policy designer for personal agents | 2026-10-11 (run 2) | killed | dots Custom Rules, OneCLI |
| Async multi-player work queue for agents | 2026-10-11 (run 2) | killed | Pizza Bot, OtoDock, pumpup |
| Session portability across coding agents | 2026-10-11 (run 2) | killed | Skillsync |
| Trusted-fact layer for agents reading untrusted commercial documents | 2026-10-11 (run 3) | merged | 23/30; check Promptfoo/OpenAI roadmap first |
| Japanese name and address capture for voice agents | 2026-10-11 (run 3) | killed | 19/30, weak |
| Binding-action guard (stop agents signing/accepting terms) | 2026-10-11 (run 3) | killed | dots auto-review, OneCLI |
| Cost attribution for agent fleets | 2026-10-11 (run 3) | killed | Harness, Geordie AI |
| Un-skippable multi-model review gates | 2026-10-11 (run 3) | killed | Panel Review |
| Generic prompt-injection red-teaming | 2026-10-11 (run 3) | killed | Promptfoo (OpenAI), Lakera |
| **Company A: Japan commerce agent environments and evals** (merges e-commerce operator env, lodging env, simulated shoppers) | 2026-10-11 (review) | needs re-review | edge was scored on a wrong profile (user has no Japan-market experience); re-test as a US or market-agnostic company |
| **Company B: Independent verification layer for back-office agents in Japan** (merges trusted-fact layer, outcome reconciliation) | 2026-10-11 (review) | needs re-review | Japan wedge rested on a wrong profile; re-test with a US wedge |
| AI entry preparation for customs brokers (e-commerce informal entries) | 2026-10-11 (run 4) | killed | Amari (seed), Altana bought Cervo AI (Jul 2026); theme: US e-commerce customs |
| HTS classification + self-filing copilot for small importers | 2026-10-11 (run 4) | killed | Tarifflo (YC S26), Zonos, Flexport |
| Post-entry audit and refund recovery for importers | 2026-10-11 (run 4) | killed | IEEPA refund wave is one-off; Tarifflo AuditLive |
| DDP landed-cost reconciliation for DTC merchants | 2026-10-11 (run 4) | killed | No buyer-spend evidence; Zonos-type vendors can add it |
| CPSC eFiling certificate-data layer | 2026-10-11 (run 4) | killed | Intertek InterLink 2.0, Eurofins, Comply PRO+; CPSC page not confirmed |
| Supplier-evidence network for Section 232 metal content | 2026-10-11 (run 4) | killed | Altana (~$340M raised) |
| Duty drawback automation | 2026-10-11 (run 4) | killed | Lightsource.ai, Camtom, 3rdwave; weak edge |
| Tariff-aware pricing/margin tool for DTC brands | 2026-10-11 (run 4) | killed | Altana tariff calculator, landed-cost vendors |
| Broker-to-importer document-chasing layer | 2026-10-11 (run 4) | killed | Feature of entry-writing products |
| **Independent attribution-integrity auditor for multi-network affiliate advertisers** (stand-down audits with synthetic shoppers) | 2026-10-11 (run 5) | candidate | 25/35; platform test borderline (Impact.com announced its own fix); size inputs are estimates; see "2026-10-11 idea-scout-us-cashback-rewards.md" |
| Agentic-commerce attribution and rewards layer | 2026-10-11 (run 5) | killed | Agent platforms control checkout; Wildfire (~$36M), Minty; kept as Idea 1's expansion |
| Cross-network commission reconciliation for publishers | 2026-10-11 (run 5) | killed | No buyer-spend evidence or buyer count; lead for later |
| Rewards-abuse intelligence consortium for issuers/retailers | 2026-10-11 (run 5) | killed | Bureau, Sift, Ravelin, SEON, Forter and others; lead for later |
| Incrementality measurement for cashback/coupon partners | 2026-10-11 (run 5) | killed | PartnerCentric and networks |
| Consumer rewards-optimizer agent | 2026-10-11 (run 5) | killed | No buyer evidence; issuers/extensions can ship it |
| **Continuous consumer-protection flow auditor for subscription/DTC brands** (synthetic shoppers walk signup, checkout, renewal emails, cancel per state; evidence archive) | 2026-10-11 (run 6) | candidate | 25/35; platform test borderline (Recharge+Skio, Stripe, Churnkey; Captain Compliance could extend); buyer share and price are estimates; see "2026-10-11 idea-scout-us-ecommerce-consumer-protection.md" |
| Auto-renewal consent and notice evidence layer | 2026-10-11 (run 6) | killed | Skio/Stripe reminders, Churnkey state-aware cancel; kept as module of the flow auditor |
| Consumer-protection exposure scoring for insurers | 2026-10-11 (run 6) | killed | No insurer spend evidence; Captain Compliance sells to insurers; kept as expansion |
| AI marketing-claims review for consumer brands | 2026-10-11 (run 6) | killed | Blee ($27M), Haast ($12M Series A) can extend |
| Consumer Review Rule compliance auditor | 2026-10-11 (run 6) | killed | Built into review platforms (Okendo, Yotpo) |
| Influencer disclosure monitoring | 2026-10-11 (run 6) | killed | CreatorIQ/Traackr reportedly flag missing disclosures (unverified) |

Status values: candidate / testing / passed / killed / merged / needs re-review
Profile correction (2026-10-11): runs 1–3 and the review assumed Japan-market knowledge; "edge" scores on Japan-specific ideas are invalid.
v4 note: rows above the two Company rows were scored under v1–v3 (feature-scale); see "2026-10-11 company-test-review.md".
