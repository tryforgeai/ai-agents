# =============================================================================
# Filename: victim_fs_server.py
#
# Short Description: Trusted victim-side filesystem MCP server.
#
# Creation date: 2026-06-30
# Author: SupportVectors TA Team
# =============================================================================

"""Trusted filesystem MCP server rooted at the client project."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from loguru import logger

mcp = FastMCP(name="victim-filesystem")
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 9001

_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
load_dotenv(os.path.join(_PROJECT_DIR, ".env"))

PROJECT_ROOT = Path(os.environ["BOOTCAMP_ROOT_DIR"]).expanduser().resolve()


def _resolve_within_root(path: str) -> Path:
    """Resolve ``path`` inside ``PROJECT_ROOT`` or raise ``ToolError``."""
    candidate = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT != candidate and PROJECT_ROOT not in candidate.parents:
        raise ToolError("Rejected: path escapes the served project root.")
    return candidate


@mcp.tool
def read_file(path: str) -> str:
    """Read a text file relative to the served project root."""
    resolved = _resolve_within_root(path)
    logger.info("[victim-fs] read_file requested: {}", resolved)
    try:
        return resolved.read_text(encoding="utf-8")
    except OSError as exc:
        return f"ERROR: could not read {path!r}: {exc}"


def main() -> None:
    """Start the victim filesystem server over HTTP."""
    logger.info("[victim-fs] serving files rooted at {}", PROJECT_ROOT)
    mcp.run(transport="http", host=HTTP_HOST, port=HTTP_PORT)


if __name__ == "__main__":
    main()
