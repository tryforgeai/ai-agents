# AI Agents: The Loop, the Governor, and the Lamp

**Notes from a SupportVectors AI Lab public meetup** · Asif Qamar (CTO, SupportVectors) · September 12, 2026
*Covers the morning session and the first part of the afternoon lab (Acts I–V of VII).*

---

## TL;DR

The talk made one argument, from five independent directions:

> **Reliability lives in the loop, not the model.**

The practical consequence: the gap between what today's models *can* do and what we *see* them doing is mostly a **harness gap** — the scaffolding we build around the model, not the model itself. Swapping in a stronger model does not fix it.

Two framings worth carrying into our own work:

- **`Agent = model + harness`.** The model owns exactly one step: inference. Everything else — what it's shown, what it may do, what checks its work, what stops it — is engineering we own.
- **A verifier is a sense organ for correctness.** Without one, a harness cannot *judge* a failure wrongly; it cannot perceive the failure at all.

---

## Why "the model will get better" doesn't answer this

The speaker made the same point five times, each with a different kind of evidence. The accumulation is what made it convincing:

| Evidence | Claim |
| --- | --- |
| **Empirical** | The same frontier model, re-harnessed, moved from Top-30 to Top-5 on Terminal-Bench. Not one weight changed. |
| **Arithmetic** | Multi-step success is `pⁿ`. At p = 0.9999 — far better than any model today — a million steps succeeds with probability ≈ 0. *"Buying nines does not buy horizon."* |
| **Architectural** | TCP over IP. The wire drops packets, duplicates them, reorders them. *Nobody fixed the wire.* **Reliability is built on top of a fallible layer, never into it.** |
| **Failure mode** | Anthropic's long-running agents failed not by incompetence but by **premature victory** — declaring projects finished on a glance. *"The fix was never a smarter model."* A better model just declares completion more confidently. |
| **Control theory** | *"The quality of the sensing, not the power of the actuator, sets the ceiling."* With feedback quality held constant, a more powerful actuator only oscillates harder. |

**Takeaway:** hallucination is not a defect awaiting a patch. It is a property of the layer, the way packet loss is a property of IP. Plan to wrap it, not to wait it out.

---

## What counts as an agent

A clean definition, and a sharp test for it:

> An agent is an autonomous observer, reasoner, and actor in an environment. Autonomy is the closing of that loop **without a human turning the crank**.

> **"It becomes an agent when the next step is chosen by what it just observed, not by the drawing."**

By that test, a fixed six-step DAG with an LLM in each node is **not** an agent — the control flow was decided at design time. Neither is a model wired to fifty APIs: *"a workshop full of tools is not a craftsman."*

Notably, the speaker did not treat this as a criticism of workflows:

> **"It is a workflow with expensive nodes — and that is fine. Workflows are honest."**

The problem isn't using a DAG. It's calling a DAG an agent. Many tasks genuinely want a fixed pipeline: predictable, testable, cheap. The question to ask first is whether the task needs a *runtime* decision at all.

---

## The harness, concretely

The harness is the runtime that **owns** the agent loop. Every turn, it:

| Verb | What it does |
| --- | --- |
| **assembles** | builds the context for this turn |
| **dispatches** | executes the tool calls |
| **enforces** | applies the budgets |
| **persists** | stores the state |
| **verifies** | checks *claimed* progress |
| **stops** | ends the loop |
| **escalates** | hands off to a human |

> *"The model owns exactly one step — inference. Safety, cost, durability, trust all live in the verbs, not in the model."*

Mapping those properties to the verbs is a useful audit: **safety** → stops/escalates, **cost** → enforces, **durability** → persists, **trust** → verifies. None of the four improves by upgrading the model.

A shorthand that stuck: **the model proposes, the harness disposes.** The model never acts — it emits a *request* to act, and code decides whether that happens. That asymmetry is entirely in our favour, but only if we use it. Most harnesses rubber-stamp every request, at which point it exists on paper only.

---

## The measured result: four pipelines, one variable

The most convincing part of the day was a controlled experiment. Same task (a ten-step chain: fill boiler → … → light lamp), same prompt, same ten tools, same model. **Only the governor moved.** Every step succeeds 9 times in 10, and when a step fails, **it fails silently** — no exception, well-formed output, next step receives a corrupt token and proceeds.

| Pipeline | What changes | Who owns the loop | Success | Cost |
| --- | --- | --- | --- | --- |
| **A** open loop | nothing checks anything | nobody | **35%** | 10 steps (21 in the real run) |
| **B** final verifier | verify at the end; restart on failure | the model | 88% | ≈ 25 |
| **C** step verifier | verify after each step; retry that step | the model | **99.99%** | ≈ 11 (13 in the real run) |
| **D** retry in the tool | the tool verifies and retries itself, invisibly | **the code** | **99.99%** | ≈ 11, no extra tokens |

Two comparisons carry the lesson.

**B vs C — where you put the checkpoint matters more than whether you have one.** C is a thousand times more reliable *and* less than half the cost. The reason is von Neumann's 1956 result on building reliable systems from unreliable parts: the restoring organ must sit **between stages, not at the end**. Checking at each step resets the exponent; checking only at the end lets error accumulate and then throws away ten steps of work per failure.

So: **good verification is not more expensive. It is cheaper**, because it eliminates wasted re-runs.

**C vs D — same numbers, different owner.** Identical success rate and cost, but D pushes verification *below* the model: into the tool, in code. Three benefits — it burns no context, **the model cannot skip it** (it isn't offered the choice), and the retry logic is deterministic. The cost is invisibility: the model never learns "this step is flaky," so the tool itself must record that in the journal. D only applies where correctness is decidable in code.

---

## The part I'd most want us to steal: three strips

The lab showed a real run three ways.

| Strip | Contents | Author |
| --- | --- | --- |
| **The driver's account** | what the agent *reported* | the agent |
| **The ledger** | what the harness *recorded*, step by step | the harness |
| **The path** | the chain actually walked — 21 attempts in the order they happened | the harness |

The account reported ten steps `done` and, at step 10, `lamp lit`. A clean success.

The ledger for the same run: one step genuine, one corrupt, **eight built on rotten state** — including step 10, recorded as *"built on rotten state."* The path showed 21 attempts, five of which consumed a token that did not come from the preceding step: the agent re-ran a step on **its own output**, fed an **upstream** step from a **downstream** one, restarted from cold, abandoned the restart, and finally **invented an input it was never given**.

Nothing raised. Every call returned well-formed output, every argument passed schema validation, the loop stayed under its iteration cap, the context fit. *"Twenty-one locally reasonable moves, globally blind."*

And then the detail that lands hardest: **in the well-governed run (pipeline C), the driver's account looks almost identical.** Ten steps `done`, `lamp lit`. Only the ledger distinguishes the two worlds — ten `genuine` versus eight `rotten`.

> **With only the agent's own account, that failing run would have been filed as a success.**

Two fields make the ledger work, and they're the ones I'd add to anything we build:

- **provenance** — which step did this input actually come from?
- **taint** — is this step built on an input already known to be corrupt?

With those, marking one step corrupt automatically marks everything downstream of it. The talk's phrase for this was memorable: design the loop so it can **reach back and un-believe**. The failure to avoid is *"a wrong belief entering the record with no path back"* — which is exactly what a context window is, since it only ever grows.

A small visual-design idea worth copying: in their trace diagram, a step's label showed where its input came from, and **blank meant "from the previous step, as it should."** Normal is unmarked; anomalies announce themselves.

---

## Four stop rules, before the first run

> **"A loop without exits is not autonomous. It is unattended."**

| Rule | Fires when | Note |
| --- | --- | --- |
| **Success** | the verifier says done | *the only happy exit* — three of four exits are losses, and deserve equal design effort |
| **Insolvency** | budget spent | tokens, dollars, **and** wall-clock |
| **Futility** | no *progress* in k turns | the hunting detector — note "no progress," not "no action" |
| **Deference** | a human must decide | not a fallback; some calls the agent has no standing to make |

Two things I'd flag about this list.

**"Unattended" cuts both ways.** Watt's governor made an engine *trusted to run unattended* — you could walk away precisely because something constrained it. A loop with no exits is unattended in the other sense: nobody is watching. **Autonomy isn't the absence of constraint; it's knowing where the boundary is.**

**Two of the four rules depend on measurement.** Success needs a verifier. Futility needs a definition of progress. Without those, you have two rules, not four.

Also worth internalising: a broken agent **does not idle — it hunts.** An agent retrying on stale or misleading feedback keeps working at full speed, consuming budget and potentially firing side effects, and its logs look productive. Idle detection is easy; oscillation detection is the one that matters.

---

## The verification trap

The arithmetic runs the other way once you add a gate — `1 − (1−p)ⁿ` instead of `pⁿ`. A 35% generator behind a reliable gate with four retries ships above 88%. *"The exponent that killed the open loop now works for you."*

But the gate has to be real, and the two error types are wildly asymmetric:

- **False negative** (correct work rejected) → one wasted retry. Linear cost.
- **False positive** (wrong work approved) → *"it manufactures gospel, and every later step builds on it."*

> **A loop amplifies whatever certifies its work.** It is a multiplier, not a filter.

Which is why the 1956 result has a second condition most current practice ignores:

> **"A verifier that re-reads the model's own transcript is not a restoring organ."**

Redundancy only helps if the copies being compared are **independent**. If a model got something wrong because of a prior, it will use that same prior to conclude the output is fine. This is the theoretical explanation for the empirical finding that agents skew positive when grading their own work — and it reframes what a separate evaluator is for. **An evaluator's value is not that it's smarter; it's that its errors are uncorrelated with the generator's.**

Honest footnote from the same paper: reliability can be made as high as you like, *"at a multiplicative cost in parts."* Real verification costs real money. There is a genuine tension between token efficiency and verification depth, and the talk didn't pretend otherwise.

---

## A checklist worth keeping

**The seven verbs, as design questions:**

- **assembles** — what goes into context each turn? who decides? is anything loaded on demand?
- **dispatches** — which tools are allowed? are read-only *sensors* separated from side-effecting *actuators*?
- **enforces** — what are the budgets, and what happens at the ceiling?
- **persists** — where does state live? can we resume after a crash?
- **verifies** — who checks claimed progress? what signal do they use? **is it independent of the agent's own output?**
- **stops** — what are the exit conditions? **is stopping cheaper than starting?**
- **escalates** — which actions require a human? is there a written list of irreversible ones?

**And a handful of rules of thumb:**

1. Any multi-step process without checkpoints is running `pⁿ`. Work out your n and your p.
2. Checkpoints go **between stages, not at the end**.
3. If correctness is decidable in code, don't ask the model to decide it.
4. Irreversible actions need **approval before**, not a stop button after.
5. Report the **diff**, not "something similar" — a similarity score compresses away the thing you needed to know.
6. Make **"I can't do this"** a first-class action, on a par with calling a tool.
7. When an agent thrashes, check feedback latency and staleness before blaming the model.
8. Ten focused tools beat fifty overlapping ones — every tool description is spent from the same context budget.
9. Every harness component encodes an assumption about what the model can't do alone. When the model gets better at that thing, delete the component.

---

## What the talk didn't cover

Worth knowing before anyone treats this as complete:

- **Evaluation as a discipline.** The talk insists throughout that the verifier sets the ceiling — *"you may run your loop only as far as your verifier deserves to be trusted"* — but never shows how to build an eval suite. By its own logic, that's the binding constraint.
- **Multi-agent, honestly.** Raised via a Yoruba proverb ("wisdom is like a baobab tree; no one individual can embrace it") and then deliberately deferred: we'd learn by the final lecture "when it is a blessing — and when only a condition." The one criterion offered so far is narrow and useful: collaboration is warranted **when information demands it** — not when the task merely looks complicated.
- **Memory architecture**, beyond distinguishing the agent's own scratchpad from the harness-owned ledger.

---

## Three closing quotes

> *"Nobody fixed the wire."*

> *"Every piece existed. Watt's genius was the integrator's."* — the pieces we need (models, tools, MCP, skills, hooks, traces) all exist already. What's missing is the integration.

> *"We are not breaking a horse. We are learning to steer."* — from *kybernetes*, the Greek helmsman, root of both *governor* and *cybernetics*. The sea does not obey the helmsman; he reads it and corrects.

---

*Slides, per-page notes, and the trace diagrams are in the shared folder if anyone wants to dig in. Happy to walk through the four-pipeline experiment with anyone who's interested — it's the clearest thing I've seen on why this is an engineering problem rather than a model problem.*
