# Architecture notes: a multi-tenant agent service

Status: working notes · 2026-10-05
Scope: how to structure an agent service that serves many users concurrently, keeps each user's memory isolated, and stays affordable.

> Sources are mixed. Lines marked **[deck]** are from the SupportVectors Week 03 *Skillcraft* lesson plan and slides. Everything else is my own synthesis and should be read as opinion, not doctrine.

---

## 1. The organizing principle

**[deck]** Keep four concerns distinct, and most architectural arguments dissolve:

| Concern | Owned by | The usual mistake |
| --- | --- | --- |
| **Access** | Tools / MCP | Permission logic written inside a skill body |
| **Procedure** | Skills | Workflow hard-coded into agent source |
| **Selection** | Router / Loader | Everything poured into the context at once |
| **Governance** | Governor / observability | Added after the first incident, not before |

A design is coupled if you cannot say in one sentence which component owns each of the four.

---

## 2. Layers

```
┌─ Entry ─ stateless, scale on QPS ─────────────────────────────────┐
│  Client  →  API tier  →  Queue  →  Worker pool                    │
│  multi-tenant  submit/poll  backpressure  scale on queue depth    │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Harness ─ the runtime that owns the agent loop ──────────────────┐
│  Agent loop                                                       │
│  assemble · dispatch · enforce · persist · verify · stop · escalate│
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Selection ─ decides what the model sees this step ───────────────┐
│  Router                          │  Loader                        │
│  picks by description            │  progressive disclosure L1→L2→L3│
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Resources ─ five sides of one discipline ────────────────────────┐
│  Skills      │  Tools / MCP     │  RAG       │  Memory            │
│  procedure   │  capability+access│  facts     │  the past          │
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Storage ─ isolation is made real here ───────────────────────────┐
│  Session        │ Vector          │ Registry      │ Sandbox        │
│  user+session   │ namespace/user  │ skills,shared │ one per task   │
└───────────────────────────────────────────────────────────────────┘

┌─ Cross-cutting ───────────────────────────────────────────────────┐
│  Governor · Observability                                         │
│  budgets · permissions · rate limits                              │
│  per run: did it fire · did it help · what did it cost · collisions│
└───────────────────────────────────────────────────────────────────┘
```

**[deck]** The five resources are one discipline wearing different clothes: *context engineering — deciding what the model sees, and when.*

### Why the API tier and the worker pool are separate

They scale on different signals. The API tier handles millisecond submits and status polls; workers run minute-long loops. Put them in one service and the autoscaling rules fight each other.

---

## 3. One turn of the loop

**[deck]** The rhythm: *the harness assembles, the model proposes, the harness disposes.*

| Module | What it does | Verb |
| --- | --- | --- |
| **Assemble** | system prompt + session history + all L1 metadata + loaded L2 bodies + tool declarations + last result | assembles |
| **Infer** | the model emits text proposing one move | — |
| **Parse** | extract the proposed action from free text | — |
| **Gate** | budget left? permission? irreversible? | enforces |
| **Dispatch** | call the tool, run the script, read the file, load the skill | dispatches |
| **Persist** | write session, write ledger | persists |
| **Verify** | check *claimed* progress; continue, stop, or escalate | verifies / stops / escalates |

Three things that get missed:

**Parse is not in the seven verbs but it exists and it fails.** The model emits prose; something has to pull the answer out of it. A parser bug and a model error look identical from the outside.

**[deck]** **"Verifies *claimed* progress."** The adjective is the point — progress is asserted by the agent, not observed. The harness checks it. Frameworks give you the signal channel (ADK's `EventActions(escalate=...)`) but the predicate is yours to write. No framework can define *done* for your domain.

**The gate is optional in a demo and first-order in production.** Iteration caps, token budgets, dry-run confirmation for irreversible actions all live here.

---

## 4. Memory: four kinds, four isolation stories

"Per-user memory" is four different things with different requirements.

| Kind | Stored where | Isolation key | Lifetime |
| --- | --- | --- | --- |
| **Operational** | not stored — reassembled every turn | none needed | one call |
| **Episodic** | relational store (sessions, events) | `user_id` + `session_id` | per session |
| **Semantic** | vector store / profile table | `user_id`, across sessions | long-lived |
| **Procedural** | skill folders | **shared, not per-user** | version-controlled |

Two non-obvious consequences:

**Operational memory needs no isolation** because it never lands anywhere. It is reconstructed each turn from the other three. The cross-tenant risk is not here.

**Procedural memory is a shared asset.** Skills are team property, not user data. If you find yourself forking a skill body per customer, the thing you actually need is semantic memory (preferences), not a second copy of the procedure. Forking is how a library drifts.

---

## 5. Isolation: where it actually breaks

Ranked by how hard it is to notice.

| # | Failure | Why it hides |
| --- | --- | --- |
| 1 | **Vector retrieval without a user filter** | Returns plausible, relevant-looking results. No error, ever. |
| 2 | **Process-global state** | Module-level singletons caching user context. Never reproduces in single-user local testing. |
| 3 | Session lookup by `session_id` alone | Guess an id, read a stranger's thread. |
| 4 | Cache keys missing `user_id` | Prompt caches, embedding caches. |
| 5 | Shared tool execution environment | Same `/tmp`, reused sandbox. |
| 6 | User data written into a skill body | Shouldn't happen; does. |

**Design so that omission is impossible, not so that omission is caught in review:**

- All storage access goes through one repository layer carrying tenant context. Business code never holds a raw client.
- Row-level security in the database, or a repository that injects the predicate.
- Vector store partitioned by **namespace per user** — not by metadata filter. A filter can be forgotten; a namespace cannot.
- Workers build context from scratch per task. No reuse of in-process objects between tasks.

### Verifying it

Assertion, not inspection:

```
Run users A and B concurrently, 50 sessions each, with unique markers.
Assert: no response, retrieval result, or log line for A ever contains
        B's user_id, session_id, or marker text.
```

Must run **under concurrency**. Race conditions and shared-state bugs are invisible in serial tests. This belongs in CI and should run on every storage-layer change.

---

## 6. Concurrency and horizontal scaling

The loop itself is stateless code — a `while`. What has state is everything the loop touches. Move session state out of the process and workers become disposable; replicas scale freely.

### This is not ordinary web concurrency

| | Ordinary service | Agent service |
| --- | --- | --- |
| Shape | many short requests | **few long** requests |
| Metric | QPS | **concurrent loops in flight** |
| Bottleneck | your CPU / DB | **LLM quota and money** |

**Async is the baseline, not an optimization.** One worker holds hundreds of sessions because they are all awaiting the network. A thread-per-session model falls over at a fraction of that.

**Autoscale on queue depth, never on CPU.** The loop is ~90% `await`. CPU sits at 10% forever; a CPU-based policy never fires.

### The real ceiling is quota, not machines

Ten replicas share one API key's quota. They do not multiply throughput — they hit 429 together, faster and more synchronously. Rate limiting must be **global** (a central token bucket), not per-instance, or every instance believes it owns the whole budget.

Four ways around it, the last one underrated:

1. Multiple keys / accounts / regions
2. Multiple providers; downgrade non-critical steps to a cheaper model
3. Prompt caching — cuts cost, does **not** raise the QPS ceiling
4. **Make fewer calls**

On (4): **[deck]** a ten-step procedure re-reasoned each run, 90% correct per step, succeeds about a third of the time (`0.9¹⁰ ≈ 0.35`). Two thirds of runs are retries. Writing the procedure down collapses the turn count.

```
same quota
  procedure re-reasoned  →  ~25 LLM calls/task  →  serves N users
  procedure as a skill   →  ~9 calls/task       →  serves ~2.7N users
```

**In a demo, a skill buys correctness. In a production service, it buys throughput.** **[deck]** *"Don't make the model rediscover what you already know"* acquires an operational meaning: rediscovery is paid for in quota.
*(The 25-vs-9 figures are illustrative, not measured.)*

### Can a loop migrate mid-run?

| | Single worker start to finish | Checkpoint every turn |
| --- | --- | --- |
| Complexity | simple; most systems do this | serialize full state each turn |
| Fits | loops of minutes | **hours-long agents** |
| On restart | task lost, re-run | resume from checkpoint |

Short tasks should not checkpoint — serialization costs more than migration saves. Anything running longer than ~30 minutes must, because containers get restarted, preempted, and evicted.

---

## 7. Practices

Ordered by how often they are the cause of an incident.

1. **Isolation by structure.** Repository layer with tenant context, RLS, per-user vector namespaces.
2. **A verifier on every step, and most can be ten lines of code.** **[deck]** The ladder: a check appended to the same prompt → a separate call → a different reasoning substrate → a rubric of deterministic checks. Use the cheapest rung that works.
3. **Deterministic steps go to scripts — and the skill must say *why the script is mandatory*.** Without the reason, the model does the arithmetic itself. (Observed: the same model, asked the same date question three times, produced 466, 496, and 497. Two of the three were off by one and looked entirely credible.)
4. **Dry-run every irreversible action.** **[deck]** *A guardrail refuses what is forbidden; a dry-run shows what is about to happen, so a wrong but permitted action can still be stopped.*
5. **Every skill needs a checkable "done when".** This is a cost control, not just a quality bar. A skill without a termination condition is a coroutine that quietly spends money — CPU normal, no exceptions, queue not backing up.
6. **Autoscale on queue depth.**
7. **Rate limit globally.**
8. **Treat third-party skills and MCP servers as untrusted code plus instruction.** Provenance, pinned version, your own eval, sandboxed execution, a human at the trust boundary. **[deck]** An audit of 3,984 publicly distributed skills found **36.8%** with at least one security flaw and **13.4%** with a critical one (Snyk Security Labs, *ToxicSkills*, Feb 2026). Note that stdio MCP servers run **on your machine with your permissions** — less isolated than remote ones, not more.
9. **Instrument four things per run:** did it fire, did it help, what did it cost, did it collide. **[deck]** *You cannot improve a library you cannot watch.*
10. **The skill library is shared.** Per-user customization belongs in semantic memory.

---

## 8. Do not build this on day one

**[deck]** *Sufficiency flows downward; necessity flows upward.* Not a menu — a forced sequence.

```
0 ad hoc → 1 authored → 2 curated library → 3 evaluated & governed → 4 self-improving
                                            ↑
                               the jump that matters
```

The diagram above is what maturity level 3 looks like. Building queues, vector stores and a governor before level 2 is infrastructure for a problem you do not have yet.

The honest progression is driven by specific failures:

| Add this | Because |
| --- | --- |
| external session store | you needed a second replica |
| queue | requests were timing out at the load balancer |
| global rate limiter | replicas started 429-ing together |
| governor / budgets | the bill was alarming |
| eval harness | you changed something and could not tell whether it improved |

---

## 9. Open questions

- Checkpoint granularity for long-running agents — per turn is expensive, per N turns loses work. No good rule of thumb yet.
- Whether the router should be a model call or pure vector retrieval at mid-size libraries (hundreds of skills). **[deck]** says small libraries put every description in context and let the model choose; large ones index by embedding. The crossover point is unstated.
- How to version skills safely once more than one team writes them.
