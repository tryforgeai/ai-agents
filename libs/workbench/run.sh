#!/usr/bin/env bash
set -euo pipefail
WORKBENCH_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd -- "$WORKBENCH_DIR/../.." && pwd)"
PYTHON_BIN="${WORKBENCH_PYTHON:-$WORKSPACE_DIR/course/ai-agents-week-02/google_adk_basics/.venv312/bin/python}"
PORT="${1:-9010}"
export PYTHONPATH="$WORKBENCH_DIR:$WORKSPACE_DIR/libs/adk_patterns/src:$WORKSPACE_DIR/libs/llm_patterns/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON_BIN" -m uvicorn server:app --app-dir "$WORKBENCH_DIR" --host 127.0.0.1 --port "$PORT"
