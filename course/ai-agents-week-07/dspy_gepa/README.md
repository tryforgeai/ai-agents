## Overview

This lab demonstrates **automatic prompt optimization** with DSPy: you define a
program and a metric, and an optimizer rewrites the prompts for you. GEPA
(Genetic-Pareto) is the star — a reflective evolutionary optimizer whose
"teacher" LM reads execution traces and proposes better instructions — compared
head-to-head against MIPROv2, COPRO, and SIMBA on the same task, and then
exercised on two more tasks of increasing subtlety.

## The notebooks (run in order)

Start with **00** if DSPy's signatures and modules are new to you; it is pure background, and 01 onward assume it.

| # | Notebook | Task | Optimizer |
|---|---|---|---|
| 00 | `00_dspy_fundamentals.ipynb` | — | Primer: signatures, modules and predictions, the module zoo (Predict, ChainOfThought, ReAct, ProgramOfThought, Refine/BestOfN, composing a `dspy.Module`), **and the optimization loop end-to-end** — examples, a metric, `Evaluate`, compiling with `BootstrapFewShot`, and re-evaluating to compare. The vocabulary notebook 02 opens with |
| 01 | `01_optimizers_intro.ipynb` | — | Lecture notes: the DSPy optimizer landscape (few-shot generation, instruction rewriting, finetuning) and when to use which |
| 02 | `02_gepa_1_info_extraction.ipynb` | Facility-support message analysis (urgency, sentiment, categories; Meta `llama-prompt-ops` dataset) | **GEPA** |
| 03 | `03_miprov2_1_info_extraction.ipynb` | same | MIPROv2 |
| 04 | `04_copro_1_info_extraction.ipynb` | same | COPRO |
| 05 | `05_simba_1_info_extraction.ipynb` | same | SIMBA |
| 06 | `06_gepa_2_papillon.ipynb` | PAPILLON privacy-preserving delegation (PUPA dataset; dual metric: quality + PII leakage) | **GEPA** |
| 07 | `07_miprov2_2_papillon.ipynb` | same | MIPROv2 |
| 08 | `08_gepa_3_tldr.ipynb` | Reddit TL;DR: exact 25-word single-line summaries, semantic fidelity via a MiniLM metric (`mlabonne/smoltldr`) | **GEPA** (with textual feedback) |
| 09 | `09_miprov2_3_tldr.ipynb` | same | MIPROv2 |
| 10 | `10_gepa_3_tldr_without_textual_feedback.ipynb` | same | GEPA on scalar scores only — shows what the textual feedback was worth |

Notebooks 02–05 are the apples-to-apples comparison: one task, one model, four
optimizers. The PAPILLON pair adds a two-model trust split, and the TL;DR trio
isolates GEPA's signature ingredient (textual feedback) by removing it.

## Model policy

Notebooks build every language model with `make_lm()` from
`svlearn_dspy.llm`. Which backend that function uses is decided by
`LLM_PROVIDER` in `.env`:

- **`supportvectors`** — the SupportVectors cluster at
  `http://10.0.10.70:8000/v1`. The task model is `openai/gpt-oss-20b`, and
  the stronger model (the `gpt-5` analog) is `openai/gpt-oss-120b`. Override
  with `SV_API_BASE`, `SV_MODEL`, `SV_STRONG_MODEL`, and `SV_API_KEY` if the
  server differs.
- **anything else, including `openai` or leaving it unset** — hosted OpenAI,
  which is how the lab runs by default:
  - **Task LM: `gpt-5-mini`** — the model whose prompts get optimized
    (`make_lm()`).
  - **`gpt-5`** only where *a stronger model is the point*
    (`make_lm(strong=True)`): GEPA's **reflection LM** (the teacher that
    reads traces and rewrites prompts), and PAPILLON's **untrusted external
    LM** (the powerful outsider the system must use without leaking PII to it).

That split is itself the lesson: optimization lets a cheap model with an
evolved prompt close much of the gap to a strong model — but the *evolving*
benefits from a strong reflector. On the SV cluster that reflector is
`gpt-oss-120b`. gpt-5-family models require `temperature=1.0` and a
generous `max_tokens`; `make_lm()` sets both. The TL;DR notebooks were
originally developed against `gpt-oss:20b` and run well on the cluster.

## Reference results

The info-extraction rows (notebooks 02–05) are from the **validated run on
hosted `gpt-5-mini`** (2026-10-20) at the shipped cheap budgets, scored on the
held-out test set (68 examples). The PAPILLON and TL;DR rows come from earlier
development runs (earlier task models; TL;DR on `gpt-oss:20b`) and are kept as
reference — those notebooks (06–10) apply the same optimizers to different
tasks, so they are shipped runnable but are not re-run on every pass, to avoid
duplicate long optimization costs. The *pattern* — GEPA leading, textual
feedback mattering — holds across tasks and budgets:

| Task | Optimizer | Baseline | Optimized | Improvement |
|------|-----------|----------|-----------|-------------|
| Information Extraction | GEPA (`auto="light"`) | 77.16% | 88.38% | +11.22 pp |
| Information Extraction | MIPROv2 (`auto="light"`) | 77.16% | 80.54% | +3.38 pp |
| Information Extraction | COPRO (breadth 3 × depth 2) | 77.16% | 79.75% | +2.59 pp |
| Information Extraction | SIMBA (4 steps) | 77.16% | 86.86% | +9.70 pp |
| PAPILLON | GEPA | 80.76% | 84.25% | +3.49 pp |
| PAPILLON | MIPROv2 | 78.96% | 82.17% | +3.21 pp |
| TL;DR | GEPA | 90.92% | 93.21% | +2.29 pp |
| TL;DR | MIPROv2 | 90.92% | 91.13% | +0.21 pp |
| TL;DR (w/o textual feedback) | GEPA | 90.7% | 91.83% | +1.13 pp |

*pp = percentage points.* Note the budget asymmetry on PAPILLON: GEPA used
`max_full_evals=1` against MIPROv2's `auto="heavy"` and still led — GEPA's
efficiency is part of the story.

**Budgets:** notebooks 02–05 ship with deliberately **cheap budgets** (GEPA
and MIPROv2 `auto="light"`, COPRO breadth 3 × depth 2, SIMBA 4 steps) so a
pass doesn't burn an hour of optimization tokens per notebook — and as the
table shows, the reflection-driven optimizers still deliver double-digit
gains at those budgets (GEPA +11.2 pp in ~30 minutes). The PAPILLON/TL;DR
reference rows used `auto="heavy"`. Each optimizer cell says what to raise
for larger-budget runs.

## Setup and running

1. `cp .env.example .env` and set your paths, `LLM_PROVIDER`, and
   `OPENAI_API_KEY`. Leave `LLM_PROVIDER` as `openai` to use hosted OpenAI
   (all notebooks bill to that key; optimization runs make *many* calls —
   the shipped budgets are the cheap ones, and raising them raises cost
   accordingly). Set `LLM_PROVIDER=supportvectors` to send every notebook
   through the SV cluster instead; no API key is required for that.

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Select the project kernel in Jupyter and run the notebooks in order.
   Notebook 01 is pure reading; 02–05 share the dataset download; with the
   shipped cheap budgets each optimization run takes minutes, versus an
   hour-plus for `auto="heavy"` with many threads.

