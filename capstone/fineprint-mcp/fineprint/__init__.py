"""FinePrint: a small synthetic store exposed as MCP tools (capstone prototype)."""
import sys

if sys.version_info < (3, 10):  # technique #50: declare the runtime, fail in words
    raise SystemExit("FinePrint needs Python 3.10+; you are running "
                     f"{sys.version.split()[0]}. Try: uv run --python 3.12 python ...")
