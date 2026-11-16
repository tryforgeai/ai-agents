# Can MemGPT Serve as the Foundation for System 5?

Rosso Han · 2026-11-15

## Answer

MemGPT can be the **memory substrate** for System 5, but not System 5 itself. It stores identity well; it does not protect, arbitrate or version it.

Here "System 5" follows Stafford Beer's Viable System Model (VSM): the layer that holds identity and policy and has the final say when System 3 (the here-and-now, operations) and System 4 (the future, the environment) conflict.

## What MemGPT is

MemGPT (Packer et al., 2023) treats the LLM like an operating system. The context window is RAM; external recall and archival storage is disk. The agent pages content in and out through function calls, and can edit its own core memory, including the persona block.

## What it contributes to System 5

- **A persistent home for identity.** The core-memory persona block stays in context across sessions, which suits mission, values and principles.
- **Room for full policy.** Tiered storage keeps a compact policy summary resident and leaves the full text in archival memory, retrieved when needed.

## Why it cannot be System 5 on its own

1. **The agent can rewrite its own identity.** By default MemGPT lets the agent edit core memory, persona included. System 5 exists precisely so operations cannot change it at will. One prompt injection or one round of "self-improvement" could rewrite policy. This matches the secure-retrieval principle: a boundary the agent must remember to respect is a request, not a control.
2. **It manages memory; it does not arbitrate.** MemGPT decides what enters the context window. That is resource scheduling, closer to System 2 / System 3 in VSM terms. System 5 must choose between System 3 and System 4 when they conflict, and MemGPT has no such role.
3. **No versioning or audit.** Policy must answer "which version was in force at the time?". MemGPT's core memory is mutable current state with no history.

## Proposed architecture

| Layer | Role | Key properties |
| --- | --- | --- |
| **System 5: identity & policy** | Defines who the system is and its limits; arbitrates S3 vs S4 conflicts | Stored separately; **read-only to agents**; versioned; changes need human approval; enforced deterministically (policy engine / guardrails), not by prompt alone |
| **MemGPT memory layer** | Memory substrate | Injects a compact S5 summary into core memory as a **read-only block**; the agent may page its own working memory freely |
| **System 3 / System 4 agents** | Operations and environment scanning | Read and write their own working memory; escalate conflicts to S5 |

Design rule: agents may read System 5 but never write it. Identity is enforced by infrastructure, not remembered by the model.

## Open points

- Recent Letta (the MemGPT successor) versions are reported to support read-only memory blocks; this should be checked against the current documentation.
- If the course defines "System 5" differently from Beer's VSM, the mapping above needs adjusting.

## References

- Packer et al. (2023). *MemGPT: Towards LLMs as Operating Systems*, arXiv:2310.08560
- Beer, S. (1972). *Brain of the Firm* (the Viable System Model)
- Course notes: [LLM and Enterprise RAG Bootcamp, Week 09 Module 5](../../../LLM%20and%20Enterprise%20RAG%20Bootcamp/course/week_09/week-09.zh.md), secure retrieval — "a boundary that is only a request is not a control"
