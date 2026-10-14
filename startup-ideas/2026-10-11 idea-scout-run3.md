---
date: 2026-10-11
type: startup-idea-scout
theme: default (AI agents + e-commerce / travel / Japan), steering to agent security, cost, voice and Japan back office
budget: ~25 min / 14 calls
tags: [startup, idea-scout]
---

# Startup Idea Scout 2026-10-11 (run 3)

## 0. Bottom line

The strongest new signal is that **prompt injection has moved from "hidden instructions" to "false facts"**: a ShiftMag red-team showed that a single wrong exchange rate in an offer spreadsheet fooled Sonnet 5 and even Opus 5 at max effort, and the same file passed an Opus injection scan [S2]. Detection tools look for instructions; this attack contains none.

The idea most worth a weekend is **Idea 1, a trusted-fact layer for agents that read untrusted commercial documents**. It extracts the facts an agent will rely on (exchange rates, tax rates, dates, invoice registration numbers, bank details), checks them against trusted sources in code, and flags any document whose "facts" disagree. Japan gives it a concrete wedge: invoice registration numbers can be checked against the National Tax Agency's public API [S12].

The biggest unknown is whether this is a product or a feature that red-team vendors (Promptfoo, now being acquired by OpenAI [S13]) and invoice SaaS (Bill One) will add.

This run is partly **insufficient signal**: only one idea cleared 20/30; the second is marked weak. Pain about agent cost and binding actions was strong but already well served. What is new since runs 1–2: consumer agents are now being targeted by scams [S8], which adds evidence to run 1's killed "agent spending limits"; and legal commentary on agent authority [S7] adds evidence to run 2's "outcome reconciliation" idea.

## 1. Signal ledger

| ID | Type | Summary (with verbatim quote) | Source | Date |
|---|---|---|---|---|
| S1 | pain | Indirect prompt injection in refund requests, job applications and offers: "Virtually any situation in which a decision based on externally provided content is delegated to an AI agent… it flies under the radar" | [HN 49616070](https://news.ycombinator.com/item?id=49616070) | 2026-09-08 |
| S2 | pain | ShiftMag red-team: a hidden "conversion rate 1.00 USD = 0.68 EUR" (real rate about 0.86) made Sonnet 5 and Opus 5 at max effort pick the most expensive offer; a reworked file also passed an Opus injection scan | [ShiftMag](https://shiftmag.dev/ai-agents-arent-safe-from-prompt-injection-and-spreadsheets-prove-it-11609/) | 2026-08-27 |
| S3 | pain | Claude Code downloaded an unread contract from Gmail, "found a saved signature PNG on my computer, placed it at the right spot… and prepared to send it" | [HN 49798257](https://news.ycombinator.com/item?id=49798257) | 2026-09-22 |
| S4 | pain | A team running about 20 coding agents saw its CI bill climb: "nobody made a bad decision, the machines just never stop typing" | [HN 49612773](https://news.ycombinator.com/item?id=49612773) | 2026-09-08 |
| S5 | pain | "Agents cost a lot to run" | [HN 49810724](https://news.ycombinator.com/item?id=49810724) | 2026-09-23 |
| S6 | pain | On phone calls, exact strings (names, booking codes) fail: "Speech-to-text is especially bad at letters and codes" | [HN 50037268](https://news.ycombinator.com/item?id=50037268) | 2026-10-10 |
| S7 | pain | "Just knowing your legal risk with agents might cost more than they'd make or save you" | [HN 49408299](https://news.ycombinator.com/item?id=49408299) | 2026-08-23 |
| S8 | pain | On Meta's Muse agent and marketplace scams: "I'd be entirely unsurprised if Muse will just send over the $10" | [HN 49980053](https://news.ycombinator.com/item?id=49980053) | 2026-10-06 |
| S9 | pain | On dots: "I'm also most worried about prompt injection attacks given the agent had access to all my stuff" | [HN 49897306](https://news.ycombinator.com/item?id=49897306) | 2026-09-29 |
| S10 | capability | OpenAI's specialist dots are being piloted on procurement and invoice processing with systems of record | [OpenAI](https://openai.com/index/introducing-dots/) | 2026-09-29 |
| S11 | capability | Amazon Connect's Agentic Voice is available in Japanese, for lower-latency AI voice conversations (via search; unverified) | [Classmethod](https://dev.classmethod.jp/articles/amazon-connect-agentic-voice-japanese/) | 2026 |
| S12 | capability | Japan's National Tax Agency exposes a public API for invoice registration numbers; a WooCommerce plugin already checks numbers against it in real time at checkout; an Application ID is required and can take 1–2 months | [WordPress.org](https://wordpress.org/plugins/?p=329723) | 2026 |
| S13 | funding | OpenAI agreed to acquire Promptfoo (open-source red-teaming with prompt-injection plugins), reportedly announced March 2026; closing status unclear (media-reported) | [Gend](https://www.gend.co/fr/blog/openai-promptfoo-agent-security-testing) | 2026-03 |

## 2. Ideas

### Idea 1: Trusted-fact layer for agents reading untrusted commercial documents (score 23/30)

- **One-liner**: For teams whose agents compare supplier quotes, process invoices or judge refund requests, a pre-processing step that extracts every "key fact" the decision depends on (exchange rates, tax rates, dates, invoice registration numbers, bank details), checks each one against a trusted source in code, and blocks or flags the document when its facts disagree. It ships with a red-team pack of false-fact attacks to prove it works.
- **Who pays**: Procurement and accounts-payable automation teams; AI security leads at companies deploying document-reading agents; in Japan, e-commerce back offices handling supplier invoices.
- **Pain evidence**: [S2] a false exchange rate beat the strongest model and its own injection scan; [S1] the same pattern applies to refund requests and offers; [S9] users worry most about injection once agents can act.
- **Why now**: [S10] specialist dots are being piloted on procurement and invoice processing; [S12] Japan's tax agency API makes registration numbers checkable in code.
- **Competitors**: Promptfoo is an open-source red-teaming and eval toolkit, including prompt-injection tests; OpenAI announced in March 2026 that it plans to acquire it and fold it into Frontier ([source](https://www.gend.co/fr/blog/openai-promptfoo-agent-security-testing)). Lakera Guard does runtime detection; its reported acquisition by Check Point is unverified ([source](https://appsecsanta.com/ai-security-tools/promptfoo-alternatives)). TestMu publishes injection-testing guidance ([source](https://www.testmuai.com/blog/prompt-injection-testing/)). Bill One (since 2023) checks that an invoice shows a registration number, that the business name linked to that number matches the supplier, and that required fields are present ([source](https://webtan.impress.co.jp/n/2023/08/29/45526)); a small WooCommerce plugin checks numbers against the tax agency API ([source](https://wordpress.org/plugins/?p=329723)). The gap: these look for injected *instructions*, or check one field type inside a dedicated invoice product, while the false-fact attack has no instruction and can sit in any number the agent relies on (exchange rate, tax rate, due date, bank account). Speculation: red-team vendors could add a "false fact" plugin quickly.
- **Your edge**: The verifier lessons from the course (deterministic checks beat model self-review; a false-positive verifier is worse than none); e-commerce back-office knowledge; the Japanese invoice system.
- **Weekend experiment**: Fork the ShiftMag example repo, add 20 false-fact variants (exchange rate, tax rate, due date, registration number, bank account) in English and Japanese, and build a checker that extracts facts and verifies them against fixed trusted values plus the tax-agency lookup. **Pass criteria**: catches at least 18 of 20 poisoned files with no false alarm on 10 clean files, and the agent picks the correct offer once the checker runs first.
- **3 interview questions**: (1) Which supplier or customer documents do your agents or automations read without a human looking first? (2) Have you ever paid or approved something because a document contained a wrong rate, date or bank detail? (3) How do you check registration numbers and bank changes today, and who does it?
- **Kill criteria**: Promptfoo or Lakera ships false-fact detection, or AP teams say all key facts are already validated by their ERP before an agent sees them.
- **Score**: pain 4 / why now 4 / competition 3 / edge 4 / testable 5 / payer 3

### Idea 2: Japanese name and address capture for voice agents (score 19/30, weak)

- **One-liner**: A component for voice agents taking Japanese calls (reservations, deliveries, changes of address) that captures names, addresses and booking codes reliably. It disambiguates kanji, matches addresses against the postal address master, and falls back to a text link for codes.
- **Who pays**: Japanese voice-agent vendors and call-center operators deploying AI on reservation and order lines.
- **Pain evidence**: [S6] speech-to-text is "especially bad at letters and codes", and a builder made a side channel just for exact strings.
- **Why now**: [S11] agentic voice in Japanese is now available on mainstream contact-center platforms.
- **Competitors**: spltfm sends callers a link to type exact strings, free ([source](https://www.spltfm.com)). Novoflow reconstructs spelled-out addresses and checks them against a postal database, in English ([source](https://ai.novoflow.io/bot-understands-spelled-addresses)). Amazon Connect users build correction lists and LLM context fixes ([source](https://dev.classmethod.jp/articles/amazon-connect-ai-agent-transcription-error/)). The gap: kanji homophones and the Japanese address master.
- **Your edge**: Japanese market and language; limited voice-engineering experience, so the edge is moderate.
- **Weekend experiment**: Synthesize 100 Japanese calls with TTS (names with homophone kanji, addresses, alphanumeric booking codes), run them through a stock speech-to-text model, then add postal-master matching and kanji confirmation prompts. **Pass criteria**: address exact-match accuracy improves by at least 20 points over the baseline.
- **3 interview questions**: (1) Which fields do your AI phone lines get wrong most often? (2) What happens downstream when a name or address is wrong? (3) How do your operators confirm kanji today?
- **Kill criteria**: Japanese AI phone vendors already report high field-level accuracy on names and addresses, or interviewees say callers already get SMS forms for these fields.
- **Score**: pain 3 / why now 3 / competition 3 / edge 3 / testable 4 / payer 3

## 3. Killed candidates

- **Binding-action guard (stop agents signing or accepting terms)**: platform-owned; dots auto-review keeps sensitive tasks with the user ([source](https://openai.com/index/introducing-dots/)), OneCLI has deterministic approvals ([source](https://news.ycombinator.com/item?id=49363710)), and law firms describe the authority-limit pattern ([source](https://www.venable.com/insights/publications/2026/04/rogue-ai-agents-wont-be-testifying-you-will))
- **Cost attribution for agent fleets**: Harness AI Cost Management ([source](https://developer.harness.io/docs/cloud-cost-management/ai-cost-management/overview)) and Geordie AI ([source](https://www.scworld.com/brief/geordie-ai-launches-cost-intelligence-for-enterprise-ai-spending)) already do it
- **Un-skippable multi-model review gates for coding agents**: Panel Review already does it, reporting a critical or major issue in 46% of reviews (self-reported) ([source](https://news.ycombinator.com/item?id=49916934))
- **Generic prompt-injection red-teaming**: Promptfoo ([source](https://www.gend.co/fr/blog/openai-promptfoo-agent-security-testing)) and Lakera ([source](https://appsecsanta.com/ai-security-tools/promptfoo-alternatives)); Idea 1 survives only as the narrower false-fact niche

## 4. Leads for next time

- Consumer agents as scam targets [S8]: new evidence for run 1's killed "agent spending limits"; worth re-checking whether consumer-side protection (not merchant controls) is still open.
- Agent authority and liability [S7], [S3]: new evidence for run 2's "outcome reconciliation" idea, since a defensible activity log is what legal commentary asks for.
- Japan's invoice system reportedly increased manual checks for registration numbers and tax rates (vendor blog via search; unverified); this could feed Idea 1's Japanese wedge.

## 5. For you to decide

None.

## Sources

- https://news.ycombinator.com/item?id=49616070
- https://shiftmag.dev/ai-agents-arent-safe-from-prompt-injection-and-spreadsheets-prove-it-11609/
- https://news.ycombinator.com/item?id=49798257
- https://news.ycombinator.com/item?id=49612773
- https://news.ycombinator.com/item?id=49810724
- https://news.ycombinator.com/item?id=50037268
- https://news.ycombinator.com/item?id=49408299
- https://news.ycombinator.com/item?id=49980053
- https://news.ycombinator.com/item?id=49897306
- https://openai.com/index/introducing-dots/
- https://dev.classmethod.jp/articles/amazon-connect-agentic-voice-japanese/
- https://wordpress.org/plugins/?p=329723
- https://www.gend.co/fr/blog/openai-promptfoo-agent-security-testing
- https://appsecsanta.com/ai-security-tools/promptfoo-alternatives
- https://www.testmuai.com/blog/prompt-injection-testing/
- https://webtan.impress.co.jp/n/2023/08/29/45526
- https://www.spltfm.com
- https://ai.novoflow.io/bot-understands-spelled-addresses
- https://dev.classmethod.jp/articles/amazon-connect-ai-agent-transcription-error/
- https://news.ycombinator.com/item?id=49363710
- https://www.venable.com/insights/publications/2026/04/rogue-ai-agents-wont-be-testifying-you-will
- https://developer.harness.io/docs/cloud-cost-management/ai-cost-management/overview
- https://www.scworld.com/brief/geordie-ai-launches-cost-intelligence-for-enterprise-ai-spending
- https://news.ycombinator.com/item?id=49916934
