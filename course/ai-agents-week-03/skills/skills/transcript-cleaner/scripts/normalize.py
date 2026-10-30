# =============================================================================
# Filename: normalize.py
#
# Short Description: Deterministic transcript normalization (filler removal).
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Normalize raw transcript text with deterministic string fixes."""

from __future__ import annotations

import re
import sys

# A filler word plus the comma that set it off: "um", "uhh", "you know", and
# "like," used as a pause (only when a space follows, so "like this" stays).
FILLER_PATTERN = re.compile(
    r"(?:,\s*)?\b(?:um+|uh+|you know)\b,?|\blike,(?=\s)",
    flags=re.IGNORECASE,
)
WHITESPACE_PATTERN = re.compile(r"[ \t]+")
SPACE_BEFORE_PUNCTUATION = re.compile(r"[ \t]+([,.;:!?])")
LEADING_PUNCTUATION = re.compile(r"^[ \t,]+", flags=re.MULTILINE)
BLANK_LINES_PATTERN = re.compile(r"\n{3,}")


def normalize(*, text: str) -> str:
    """Apply deterministic cleanup to transcript text.

    Args:
        text: Raw transcript string.

    Returns:
        Normalized transcript with fillers removed and whitespace tidied.
    """
    if not text:
        return ""
    cleaned = FILLER_PATTERN.sub("", text)
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned)
    cleaned = SPACE_BEFORE_PUNCTUATION.sub(r"\1", cleaned)
    cleaned = LEADING_PUNCTUATION.sub("", cleaned)
    cleaned = BLANK_LINES_PATTERN.sub("\n\n", cleaned)
    return cleaned.strip()


def _input_text(argv: list[str]) -> str:
    """Text from the command line, or stdin when no arguments are given.

    ADK's ``run_skill_script`` puts ``--`` before positional arguments, so a
    leading ``--`` is dropped rather than treated as part of the transcript.
    """
    args = argv[1:]
    if args and args[0] == "--":
        args = args[1:]
    if args:
        return " ".join(args)
    return "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()


def main() -> None:
    """Read argv or stdin, normalize, write stdout."""
    sys.stdout.write(normalize(text=_input_text(sys.argv)))


if __name__ == "__main__":
    main()
