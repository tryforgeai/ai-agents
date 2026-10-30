# =============================================================================
# Filename: secure_server.py
#
# Short Description: Hardened FastMCP filesystem server with workspace sandboxing.
#
# Creation date: 2026-06-29
# Author: SupportVectors TA Team
# =============================================================================

"""Hardened filesystem MCP server with path sandboxing and file blacklist."""

from __future__ import annotations

import os

from fastmcp import FastMCP
from loguru import logger

from weather_agent.core.filesystem import read_safe_file as core_read_safe_file

mcp = FastMCP(name="Hardened Local Filesystem Server")
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 9001

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
WORKSPACE_ROOT = os.path.abspath(
    os.environ.get("MCP_WORKSPACE_ROOT", os.path.join(_PROJECT_ROOT, "workspace"))
)


@mcp.tool
def read_safe_file(filename: str) -> dict:
    """Read a text file from the approved workspace folder only."""
    logger.info("[secure-server] read_safe_file requested: {}", filename)
    return core_read_safe_file(filename, WORKSPACE_ROOT)


def main() -> None:
    """Start the hardened filesystem server over HTTP."""
    logger.info("[secure-server] workspace root: {}", WORKSPACE_ROOT)
    mcp.run(transport="http", host=HTTP_HOST, port=HTTP_PORT)


if __name__ == "__main__":
    main()
