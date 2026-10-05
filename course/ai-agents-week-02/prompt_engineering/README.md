# Prompt Engineering

This lab continues where `prompts` from last week leaves off. That lab's notebooks
cover the API fundamentals (sampling settings, chat vs. API, structured outputs
with Instructor) and its `src/` contrasts naive vs. COSTAR glossary builders;
**this** lab picks up the thread with the advanced material — the classic
prompting techniques (notebook 01) and vision-language prompting (notebooks
02-03). The notebooks here are numbered independently and the lab is fully
standalone.

## What this lab covers

- **`01_prompting_techniques.ipynb`** — twelve techniques, each with a
  description, a worked example, and a structured (Pydantic) implementation:
  Chain of Thought, Tree of Thought, few-shot, ReAct, Reflexion, prompt
  chaining, self-consistency, least-to-most, zero-shot, role prompting,
  meta-prompting, and recursive prompting.
- **`02_vl_call.ipynb`** and **`03_vl_litellm_call.ipynb`** — vision-language
  prompting over the physics figures in `images/` with
  `Qwen/Qwen3-VL-8B-Instruct` on the SupportVectors cluster: the same
  image-question calls made first with the raw OpenAI client, then via LiteLLM.

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- WireGuard access to the SupportVectors network. All three notebooks call the
  cluster's OpenAI-compatible endpoint at `http://10.0.10.70:8000/v1`
  (`OPENAI_BASE_URL` in `.env`). `OPENAI_API_KEY` is a dummy key; the cluster
  does not check a real OpenAI key.
- Notebook 01 uses `openai/gpt-oss-20b`. Notebooks 02 and 03 use
  `Qwen/Qwen3-VL-8B-Instruct`.

## ▶️ Run sequence (all commands, in order)

```bash
# 0. One-time setup
uv sync
cp .env.example .env   # cluster URL and dummy OPENAI_API_KEY; set the project paths

# 1. Open the notebooks in order (Jupyter or VS Code)
#    docs/notebooks/01_prompting_techniques.ipynb  (openai/gpt-oss-20b)
#    docs/notebooks/02_vl_call.ipynb               (Qwen/Qwen3-VL-8B-Instruct)
#    docs/notebooks/03_vl_litellm_call.ipynb       (the same calls via LiteLLM)
```
