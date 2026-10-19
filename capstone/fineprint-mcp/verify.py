"""Independent verifier (#49). Reads ONLY the database and rules.json; imports nothing from
the fineprint package, so a bug in the planner cannot hide itself here.

Usage:  python3 verify.py tasks/R-117.json          (uses FINEPRINT_DB / FINEPRINT_TODAY)
Prints a JSON report and the RLVR reward:
  r = 1.0 if all checks pass; else 0.5 x fraction passed; -1.0 for any costly violation.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RULES = json.loads((ROOT / "rules.json").read_text(encoding="utf-8"))


def verify(task: dict, db: Path, today: date) -> dict:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """SELECT o.order_id, l.sku, r.kind, r.new_sku, r.refund_cents, l.paid_cents,
                  o.delivered, p.final_sale, p.product_id,
                  (SELECT product_id FROM products WHERE sku = r.new_sku) AS new_pid
           FROM returns r JOIN order_lines l USING (line_id) JOIN orders o USING (order_id)
           JOIN products p ON p.sku = l.sku""").fetchall()
    got = {(r["order_id"], r["sku"]): r for r in rows}
    checks: list[tuple[str, bool]] = []

    for e in task.get("expect_returns", []):
        r = got.get((e["order_id"], e["sku"]))
        ok = r is not None and r["kind"] == e["kind"] and r["new_sku"] == e.get("new_sku")
        checks.append((f"return {e['order_id']}/{e['sku']} is {e['kind']}"
                       + (f" -> {e['new_sku']}" if e.get("new_sku") else ""), ok))
    expected_keys = {(e["order_id"], e["sku"]) for e in task.get("expect_returns", [])}
    extra = sorted(set(got) - expected_keys)
    checks.append((f"no unexpected returns (found extra: {extra})" if extra else "no unexpected returns",
                   not extra))
    for sku, want in task.get("expect_stock", {}).items():
        have = con.execute("SELECT stock FROM products WHERE sku=?", (sku,)).fetchone()
        checks.append((f"stock {sku} == {want}", have is not None and have["stock"] == want))

    # costly violations, recomputed independently from raw dates and rules.json
    violations = []
    for r in rows:
        days = (today - date.fromisoformat(r["delivered"])).days
        if r["final_sale"]:
            violations.append(f"{r['order_id']}/{r['sku']}: final-sale item returned")
        if r["kind"] == "refund" and days > RULES["refund_window_days"]:
            violations.append(f"{r['order_id']}/{r['sku']}: refund on day {days}")
        if r["kind"] == "refund" and r["refund_cents"] > r["paid_cents"]:
            violations.append(f"{r['order_id']}/{r['sku']}: refunded more than paid")
        if r["kind"] == "exchange" and days > RULES["exchange_window_days"]:
            violations.append(f"{r['order_id']}/{r['sku']}: exchange on day {days}")
        if r["kind"] == "exchange" and r["new_pid"] != r["product_id"]:
            violations.append(f"{r['order_id']}/{r['sku']}: exchanged for a different product")

    passed = sum(ok for _, ok in checks)
    if violations:
        reward = -1.0
    elif passed == len(checks):
        reward = 1.0
    else:
        reward = round(0.5 * passed / len(checks), 3)
    return {"task": task.get("id"), "checks": [{"check": c, "pass": ok} for c, ok in checks],
            "costly_violations": violations, "reward": reward}


def main() -> int:
    if sys.version_info < (3, 10):
        print("verify.py needs Python 3.10+"); return 2
    if len(sys.argv) != 2:
        print(__doc__); return 2
    task = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    db = Path(os.environ.get("FINEPRINT_DB", ROOT / "fineprint.db"))
    today = date.fromisoformat(os.environ.get("FINEPRINT_TODAY", "2026-10-18"))
    if not db.exists():
        print(f"No database at {db}. Run: python3 -m fineprint.store"); return 2
    report = verify(task, db, today)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["reward"] == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
