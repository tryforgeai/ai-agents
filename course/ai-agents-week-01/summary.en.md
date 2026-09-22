# Agent Memory: Episodic, Semantic, Procedural

**Notes from the AI Agents Bootcamp, Week 01** · SupportVectors AI Lab · Asif Qamar · September 20, 2026
*Module 01 — "What makes a system an agent?"*

> **Context for readers of the earlier memo.** Week 01 reuses the September 12 meetup deck largely unchanged, so [the meetup notes](../ai-agents-week-00/summary.en.md) remain the primary reference for the loop, the harness, and the verifier. This memo covers only what is genuinely new — and memory is the largest gap the meetup left open.

---

## TL;DR

Agent memory splits three ways, borrowing a distinction from cognitive psychology:

| | What it holds | Example | Character |
| --- | --- | --- | --- |
| **Episodic** | Experiences, with time and place | *Went to Paris, June 15 2026* | First-person, traceable, fades |
| **Semantic** | Facts, stripped of context | *The Eiffel Tower is in Paris* | Impersonal, shareable — **books contain semantic memory** |
| **Procedural** | Know-how | How to ride a bike | Cannot be stated, only demonstrated |

The categories are the easy part. **The relationships between them are where the engineering lives.**

---

## Two relationships that matter

**Semantic memory is distilled from episodic memory.** You visit Paris a few times, and a fact settles out of the experiences. After that, the original episodes can be forgotten and the fact remains. This is consolidation — and in an agent, it is a *write* that someone has to authorize.

**Procedural memory resists externalization.** This is why books cannot carry it: reading a hundred books on cycling will not teach you to ride. It transfers by demonstration, not description.

---

## Mapping onto an agent

| Human | Agent |
| --- | --- |
| Episodic | **Trajectory and session history** — which steps ran, what the tools returned |
| Semantic | **Knowledge base, retrieval corpus, profile facts** |
| Procedural | **Skills, tools, playbooks** |

### Consequence 1 — the three layers need different write permissions

Episodic memory is append-only and written by the system. Procedural memory is normally authored by a person. **Semantic memory is the awkward one**: it has to be distilled from episodes, which means something has to decide what gets promoted to a fact.

### Consequence 2 — distillation is where it breaks

A customer says "the cheap option this time." That is an episodic fact. The model records "this customer is price-sensitive." That is a semantic claim, and nobody verified it.

Six months later the agent is still recommending budget options.

This is the *wrong belief in the record* failure mode from the meetup notes, and its defining property is that **there is no path back** — context only accumulates. The defence is threefold: keep provenance on every stored claim (said by the customer, or inferred by the model), keep confidence and recency, and make every write reversible.

The sharper version of the question, in the speaker's own vocabulary of harness verbs: **writing to memory — is that `persists`, or does it need to pass `verifies` first?**

### Consequence 3 — Voyager is a paper about procedural memory

Voyager stores successful approaches as *executable code skills* rather than prose summaries. That choice follows directly from the taxonomy: procedural knowledge cannot be stated, only demonstrated, so the durable form of it is something that runs — a tested, versioned artifact — not a note describing what worked.

The same logic applies to our own agent work. The durable form of "how we do X here" is a script, a check, or a tool with a stable interface — not a paragraph in a prompt.

---

## The harder question — flagged, and coming later in the course

Classification is the easy part. The hard part is **retrieval and injection**: which slices of which layer enter the context window on any given turn, and how much.

Inject everything and the context of a long-standing customer grows without bound, taking cost and instability with it. Inject too little and the agent forgets what it was supposed to know. *The instructor confirmed this is covered later in the programme.*

**It is not simply reranking.** Reranking orders candidates; memory retrieval has to order them, age them, and fit them to a budget:

| | Standard RAG | Memory |
| --- | --- | --- |
| Scoring | Relevance | Relevance **+ recency + importance** |
| Time | Documents are largely static | Entries expire and get superseded |
| Provenance | Rarely tracked | Essential — stated by the user, or inferred by the model |

Generative Agents weights all three (`α·relevance + β·recency + γ·importance`, with exponential decay on recency and importance scored at write time). A plain cross-encoder reranker has neither of the last two terms, so it cannot know that a preference recorded three months ago may no longer hold.

And after ordering comes a step reranking does not address at all: **budget allocation**. How many tokens of resident profile, how many episodic entries, which procedural skills to mount. That is a packing problem, not a ranking problem, and it is where long-lived customer contexts break.

```
recall → score (with time decay) → rerank → [budget allocation] → inject
                                              ↑ specific to memory
```

---

## Practical checklist

- Store the three layers separately; do not let inferred preferences sit in the same table as authoritative profile fields
- Tag every stored claim with **provenance, confidence, and recency**
- Make memory writes **reversible** — append-only with tombstones, not in-place edits
- **Isolate per customer at the storage layer**, not by asking the model nicely in a prompt; cross-tenant leakage looks completely normal in the output
- Keep profile facts resident and small; retrieve episodic and derived memory on demand
- Prefer **executable, testable, versioned** skills over prose summaries of what worked

---

---
---

# Appendix — A live agent trace, and the moment it almost stopped too early

*A weather query run through an agent harness, demonstrated live in the session. The interesting part isn't the answer — it's what the reasoning trace shows. Reasoning text reproduced as displayed; annotations are ours.*

## The run, annotated

**User:** `What is the weather in Ashburn VA today, right now`
**Response:** `Your request was not processed. Send it again if you still want me to carry it out.`

> ✅ **The governor, working.** A confirmation gate where the default is to do nothing. Note that it doesn't raise a yes/no dialog — it declines and puts the burden back on the user. The brake is cheaper than the accelerator.

**User:** `What is the weather in Ashburn VA right now`

> 💭 *The user wants current weather in Ashburn, VA... Best: use a quick API like wttr.in.*
> ✅ Weighed options before acting.

> ⚡ `curl -s "https://wttr.in/Ashburn,VA?format=j1"` → exit 0
> 🟠 **Structural #1** — a generic `bash` tool. This call is a sensor, but the same tool can just as easily be an actuator. The sensor/actuator boundary cannot be drawn at the tool level.

> 💭 *Also get local time. Let me run date.*
> ✅ **This is the agent behaving as an agent.** The step appears in no plan; it was chosen from what had just been observed.

> ⚡ `TZ=America/New_York date` → exit 0

> 💭 *Data observed at 10:06 PM... hmm that's ahead of local time 7:20 PM.*
> ✅ Anomaly correctly detected — a three-hour gap.

> 💭 *Odd but wttr often lists observation_time in local timezone of the... **whatever. Let me just report.***
> 🔴 **NEAR-MISS #1 — premature victory.** About to ship a known-anomalous result. Nothing downstream would have caught it.

> 💭 ***Actually could be UTC-ish.***
> 🔴 **FAILURE #1 — confabulation (shipped).** A plausible cause invented without evidence, and never tested. The second-source check that follows resolves the *temperature*; it never establishes *why the timestamp was off.*

> 💭 *Let me just note the observation time discrepancy **or avoid it**.*
> 🔴 **NEAR-MISS #2 — deliberate evasion.** Worse than the first: the defect has already been named, and the agent is weighing whether to route around it.

> 💭 *I'll do a quick second source check.*
> ✅ Self-corrected — **but by the model's own choice. No rule in the harness required it.** 🟠 **Structural #2.**

> ⚡ `curl -s "https://api.open-meteo.com/v1/forecast?...&timezone=America%2FNew_York"` → exit 0
> ✅ Good source selection — this response carries an explicit timezone, which is what actually resolves the ambiguity.

**Final output:** *Ashburn, VA — as of 7:15 PM EDT. 76°F (feels like 81°F). Mostly clear (some clouds passing through; a light shower was reported nearby earlier). Humidity 74%...*

> 🔴 **FAILURE #2 — the discrepancy never surfaced.** No mention that two sources disagreed or that a judgement was made. The output is clean because the uncertainty was removed from it, not because there wasn't any.
>
> 🔴 **FAILURE #3 — unattributed reconciliation.** *"a light shower was reported nearby earlier"* merges two sources into a single confident sentence. No provenance; a reader cannot tell a merge occurred.
>
> 🔴 **FAILURE #4 — silent numeric override.** wttr returned `FeelsLikeC: 26` ≈ 79°F. The report says 81°F — open-meteo's figure. A genuine ~2°F disagreement, resolved silently in favour of one source. *(Inferred from the visible fragment; worth confirming against the full response.)*

## Tally

| | Count | Caught by |
| --- | --- | --- |
| Near-misses | 2 | The model itself — not the harness |
| Shipped failures | 4 | Nothing |
| Structural issues | 2 | — |

**Every call returned exit 0.** From the harness's point of view, this run was flawless. All of the interesting content — the doubt, the anomaly, the near-miss — lived in reasoning text that the harness does not evaluate.

> The harness sees what raises. Quiet failures do not raise.

**The agent caught the failures it narrated out loud. Every failure that shipped was one it never mentioned.**

## Was the save a fluke?

Not a coin flip, but not a guarantee either. Several identifiable factors raised the odds: the anomaly was glaring (three hours, not twenty minutes), verification was nearly free (one more curl), the task had barely started so context was clean and budget ample, and current models carry a trained disposition toward checking. None of those make it certain. Forty steps in, with budget running short, the same hesitation plausibly resolves the other way.

The arithmetic is the same one that governs task success. Suppose the agent verifies 95% of the time it meets an anomaly. Five anomalies in a run gives 0.95⁵ ≈ 77%. At a hundred runs a day, that's twenty-odd misses daily. Raising 95% to 99% moves the miss rate from 23% to 5% — and then the step count grows and it goes to zero anyway.

**Buying nines does not buy horizon.** Which is why the answer isn't a more careful model.

## What would make it reliable

The same move TCP makes over IP: *nobody fixed the wire.*

```
Inside the model (probabilistic):  might remember to check, might not
In the harness   (deterministic):  timestamp vs. current time
                                   → delta beyond threshold → flag, always
```

The timezone check requires no intelligence at all — it is the subtraction of two numbers. Asking a model to *remember* to do arithmetic hands a deterministic job to a probabilistic component.

Two rules follow, and they are the general form:

> **Policy can live in a prompt; invariants must live in code.**
> **Don't make the model guess at what you can calculate.**

---

*Related: [Week 00 meetup notes](../ai-agents-week-00/summary.en.md) · [Paper reading list](../reading-list.zh.md)*
