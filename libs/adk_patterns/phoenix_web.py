"""Configure OTEL before ADK Web adds its own event/trace exporters."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from adk_patterns.observability import enable_phoenix

if __name__ == "__main__":
    provider = enable_phoenix(
        os.getenv("PHOENIX_PROJECT_NAME", "ai-agents-labs"),
        mode=os.getenv("ADK_PHOENIX_MODE", "native"),
    )
    from google.adk.cli.cli_tools_click import main
    try:
        main(args=["web", "--host", "127.0.0.1", "--port", os.getenv("ADK_WEB_PORT", "9001"),
                   str(Path(__file__).resolve().parent / "examples" / "phoenix")])
    finally:
        provider.force_flush()
