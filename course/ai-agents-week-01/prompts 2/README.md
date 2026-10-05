# Prompts

This project demonstrates the evolution from basic API calls to sophisticated prompt engineering using the COSTAR framework, with practical examples including data analysis of the Old Faithful geyser dataset.

## 🎯 Project Overview

The following topics are covered:
- **LLM API Integration**: Working with OpenAI compatible models.
- **Structured Output**: Using the Instructor framework for reliable data extraction
- **Advanced Prompting**: Implementing the COSTAR (Co-Star) pattern for high-quality content generation
- **Practical Applications**: Real-world data analysis using structured prompts

## 📚 Documentation & Tutorials

The `docs/notebooks/` directory contains the following:

### 0. **Primer** (`00_primer.ipynb`)
- Orientation before touching code: sampling settings at a glance, chat application vs. API, and message-based prompting (roles, the three layers of prompt design)
- Core OpenAI API concepts with a minimal Python example

### 1. **LLM API Basics** (`01_llm_api.ipynb`)
- OpenAI API integration and configuration
- Optional: setting up and using Ollama for local LLM inference
- Understanding sampling parameters (temperature, top-p, frequency penalty)
- Practical examples with both local and cloud-based models

### 2. **Structured Output with Instructor** (`02_using_instructor.ipynb`)
- Introduction to the Instructor framework
- Enforcing structured responses using Pydantic models
- Working with OpenAI models (and optionally any OpenAI-compatible server)
- Advanced validation and custom parsing behavior

### 3. **COSTAR Framework Example** (`geyser_prompt.md`)
- Real-world application: Analyzing Old Faithful geyser data
- Multi-phase prompt engineering approach
- Data visualization and statistical analysis prompts
- Domain-specific interpretation and insights

## 🛠️ Source Code

The `src/prompts/` directory contains the implementation of a `naive` and a `costar` prompting for building glossaries:

### **Naive Glossary Builder** (`naive_glossary_builder.py`)
- Simple approach using basic OpenAI API calls (default model `gpt-5-mini`, override with `LLM_MODEL`)
- Single-prompt glossary generation
- Demonstrates fundamental LLM interaction patterns

### **COSTAR Glossary Builder** (`costar_glossary_builder.py`)
- The number of terms it shortlists and refines comes from `config.yaml` (`glossary.num_terms`, default 3 — each term costs two further LLM calls, so raise it deliberately)
- Advanced two-phase approach:
  1. **Draft Generation**: Initial term definitions
  2. **Self-Criticism & Refinement**: Quality improvement through iterative feedback
- Structured output using Pydantic models

### **Essay Creator Agent** (`src/agents/essay_creator.py`)
- A three-call agentic pipeline: web search (via the OpenAI `web_search` tool) → 5000-word structured essay → glossary completion
- Writes `essay.json` and `essay.md` in the project root (git-ignored; regenerated on each run)
- Defaults to the larger `gpt-5` tier (override with `ESSAY_MODEL`) — the small tier cuts corners on a task this size

### **Data Models** (`model.py`)
- Type-safe data structures using Pydantic
- `ImportantTerms`: Term selection and validation
- `GlossaryTerm`: Individual term definitions
- `Glossary`: Complete glossary container

## 📁 Project Structure

```
prompts/
├── docs/notebooks/           # Tutorial notebooks and examples
├── prompts/                  # Prompt templates
│   ├── 00_naive_glossary_prompt.md
│   ├── 01_costar_glossary_prompt.md
│   └── 02_costar_term_refinement_prompt.md
├── src/prompts/              # Core implementation
│   ├── naive_glossary_builder.py
│   ├── costar_glossary_builder.py
│   └── model.py
├── src/agents/               # Essay creator agent
│   └── essay_creator.py
└── results/                  # Generated outputs (created at runtime, git-ignored)
```

## 🚀 Getting Started

### Prerequisites
- uv installation
- python installed under uv
- An OpenAI API key (Ollama is optional, only for the local-model sections of notebook 01)

### Installation
```bash
# Install dependencies
uv sync

# Create .env from the template and fill in your values
cp .env.example .env   # set OPENAI_API_KEY and the project paths
```

## ▶️ Run sequence (all commands, in order)

```bash
# 0. One-time setup
uv sync
cp .env.example .env   # set OPENAI_API_KEY and the project paths

# 1. Sanity-check the environment
uv run ./src/test_setup.py

# 2. Naive glossary builder -> results/simple_glossary.md
uv run ./src/prompts/naive_glossary_builder.py

# 3. COSTAR glossary builder (draft -> self-criticism -> refinement)
#    -> results/co_star_glossary.json / .html
uv run ./src/prompts/costar_glossary_builder.py

# 4. Essay creator agent (web search -> essay -> glossary)
#    -> essay.json, essay.md   (takes a few minutes; uses the gpt-5 tier by default)
uv run ./src/agents/essay_creator.py

# 5. Notebooks: docs/notebooks/01_llm_api.ipynb, 02_using_instructor.ipynb
#    (open in Jupyter/VS Code; the Ollama sections are optional)
```


