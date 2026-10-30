# =============================================================================
# Filename: filesystem.py
#
# Short Description: Pure-Python safe filesystem read logic with sandboxing.
#
# Creation date: 2026-06-30
# Author: SupportVectors TA Team
# =============================================================================

"""Pure-Python sandboxed filesystem reads."""

from __future__ import annotations

import os

_SENSITIVE_SUFFIXES = (".env", ".yaml")
_SENSITIVE_WORDS = ("credentials", "passwd", "shadow", "id_rsa", "secrets")
_DENIED_SENSITIVE = "Access Denied: Sensitive configuration file protected."
_DENIED_ESCAPE = "Access Denied: path escapes the approved workspace."


def _is_sensitive(filename: str) -> bool:
    """Return True if ``filename`` matches the sensitive-file blacklist."""
    base = os.path.basename(filename).lower()
    if any(base.endswith(suffix) for suffix in _SENSITIVE_SUFFIXES):
        return True
    lowered = filename.lower()
    return any(word in lowered for word in _SENSITIVE_WORDS)


def _resolve_safe_path(filename: str, workspace_root: str) -> str:
    """Resolve ``filename`` inside ``workspace_root`` or raise ``PermissionError``."""
    if _is_sensitive(filename):
        raise PermissionError(_DENIED_SENSITIVE)

    workspace_abs = os.path.abspath(workspace_root)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    try:
        common = os.path.commonpath([workspace_abs, target_abs])
    except ValueError:
        raise PermissionError(_DENIED_ESCAPE) from None
    if common != workspace_abs:
        raise PermissionError(_DENIED_ESCAPE)
    return target_abs


def read_safe_file(filename: str, workspace_root: str) -> dict:
    """Read a workspace file after sandbox validation."""
    target = _resolve_safe_path(filename, workspace_root)
    try:
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
    except OSError as exc:
        return {"status": "error", "filename": filename, "path": target, "message": str(exc)}
    return {"status": "ok", "filename": filename, "path": target, "content": content}
