#!/usr/bin/env bash
set -euo pipefail
LIB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd -- "$LIB_DIR/../.." && pwd)"
ADK_BIN="${ADK_PATTERNS_ADK_BIN:-$WORKSPACE_DIR/course/ai-agents-week-02/google_adk_basics/.venv312/bin/adk}"
EXAMPLE="${1:-calculator}"
PORT="${2:-9001}"
if [[ ! "$EXAMPLE" =~ ^[a-z_]+$ || ! -f "$LIB_DIR/examples/$EXAMPLE/agent.py" ]]; then
  echo "示例不存在。可选：calculator counter routing parallel loop approval travel agent_tools mcp reviewed_digest phoenix" >&2
  exit 1
fi
if [[ ! -x "$ADK_BIN" ]]; then
  echo "找不到 adk。请安装本库后设置 ADK_PATTERNS_ADK_BIN 为 adk 可执行文件的绝对路径。" >&2
  exit 1
fi
export PYTHONPATH="$LIB_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$ADK_BIN" web --host 127.0.0.1 --port "$PORT" "$LIB_DIR/examples/$EXAMPLE"
