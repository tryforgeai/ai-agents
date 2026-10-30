# Langgraph Basics

Detailed Explanation in "docs/notebooks/langgraph_basics.ipynb"


# Simple Newsletter Generator

A multi-agent powered newsletter generator that uses LangGraph, and FastMCP to create a basic newsletter on a given topic.


---

## Prerequisites

1. **FastMCP Server**
   - Clone and set up [fastmcp](https://github.com/langchain-ai/fastmcp) (or your local MCP server).
2. **API Keys**
   - Serper: https://serper.dev/
   - Add all keys to your `.env` file in the project root:
     ```
     OPENAI_API_KEY=not-needed
     OPENAI_BASE_URL=http://10.0.10.70:8000/v1
     OPENAI_MODEL=openai/gpt-oss-20b
     SERPER_API_KEY=your_serper_key
     ```

---

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Start the FastMCP Server

```bash
# From your fastmcp directory (or wherever your MCP server is)
uv run src/mcp/fastmcp_server.py
```
- The MCP server should run on: http://localhost:9000/mcp

### 3. Simultaneously run Langgraph

```bash
uv run src/basics/mini_newsletter.py
```

---

## Troubleshooting

- **MCP server not running:**  
  - Ensure `fastmcp_server.py` is running and accessible at http://localhost:9000/mcp

---
