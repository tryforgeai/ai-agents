# =============================================================================
# Filename: check_totals.py
#
# Short Description: Validate that revenue and cost subtotals reconcile.
#
# Creation date: 2026-07-03
# Author: SupportVectors AI Training Team
# =============================================================================
"""Validate QBR metric JSON for arithmetic consistency.

Usage: ``check_totals.py '<metrics JSON>'`` (or pipe the JSON on stdin).
"""

from __future__ import annotations

import json
import sys
from typing import Any


def check_totals(*, metrics: dict[str, Any]) -> list[str]:
    """Return a list of reconciliation errors (empty if valid).

    Args:
        metrics: Dictionary of numeric QBR fields.

    Returns:
        Human-readable error strings; empty when totals reconcile.
    """
    errors: list[str] = []
    product_a = float(metrics.get("product_a_revenue", 0))
    product_b = float(metrics.get("product_b_revenue", 0))
    total_revenue = float(metrics.get("total_revenue", 0))
    if abs((product_a + product_b) - total_revenue) > 0.01:
        errors.append(
            f"Revenue mismatch: {product_a} + {product_b} != {total_revenue}"
        )

    eng = float(metrics.get("eng_cost", 0))
    sm = float(metrics.get("sm_cost", 0))
    total_cost = float(metrics.get("total_cost", 0))
    if abs((eng + sm) - total_cost) > 0.01:
        errors.append(f"Cost mismatch: {eng} + {sm} != {total_cost}")

    net = float(metrics.get("net", 0))
    expected_net = total_revenue - total_cost
    if abs(net - expected_net) > 0.01:
        errors.append(f"Net mismatch: {net} != {expected_net}")
    return errors


def _input_json(argv: list[str]) -> str:
    """Metrics JSON from the command line, or stdin when no arguments are given.

    The agent's ``run_skill_script`` passes the JSON as an argument (with a
    leading ``--`` for positional arguments); a person can also pipe it in.
    """
    args = argv[1:]
    if args and args[0] == "--":
        args = args[1:]
    if args:
        return " ".join(args)
    return "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()


def main() -> None:
    """Read metrics JSON from argv or stdin; print OK or errors."""
    raw = _input_json(sys.argv)
    if not raw.strip():
        print("ERROR: no metrics JSON supplied")
        sys.exit(2)
    metrics = json.loads(raw)
    errors = check_totals(metrics=metrics)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
