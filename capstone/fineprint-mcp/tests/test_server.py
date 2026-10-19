"""MCP-level tests through an in-memory client: schemas, contracts, end-to-end tasks."""
import ast
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

ROOT = Path(__file__).resolve().parents[1]


def run(coro):
    return asyncio.run(coro)


async def call(name, args):
    from fineprint.server import mcp
    async with Client(mcp) as c:
        return (await c.call_tool(name, args)).structured_content


async def tools():
    from fineprint.server import mcp
    async with Client(mcp) as c:
        return {t.name: t for t in await c.list_tools()}


def test_four_tools_typed_with_when_not_to_use(fresh_db):
    ts = run(tools())
    assert set(ts) == {"get_order", "list_coupons", "quote_cart", "request_return"}
    for t in ts.values():
        assert "Do not use" in t.description                       # #25
        props = t.input_schema["properties"]
        assert all(p for p in props.values()), f"{t.name} has an untyped parameter"  # lab 2b
        assert t.output_schema is not None                          # structured output


def test_required_params_have_no_defaults(fresh_db):
    qc = run(tools())["quote_cart"].input_schema
    assert set(qc["required"]) == {"customer_id", "items", "coupon_codes", "points"}


def test_order_id_normalised_and_stamped(fresh_db):
    o = run(call("get_order", {"order_id": " o-1001 "}))
    assert o["order_id"] == "O-1001" and o["days_since_delivery"] == 20
    assert o["source"].startswith("fineprint.db") and o["as_of"] == "2026-10-18"


def test_missing_order_is_a_clear_error(fresh_db):
    with pytest.raises(ToolError, match="does not exist"):
        run(call("get_order", {"order_id": "O-9999"}))


def test_wrong_type_blocked_at_boundary(fresh_db):
    with pytest.raises(ToolError):
        run(call("quote_cart", {"customer_id": "C001", "items": [{"sku": "SOCK-L", "qty": 0}],
                                "coupon_codes": [], "points": 0}))


def test_refund_with_new_sku_is_contract_error(fresh_db):
    with pytest.raises(ToolError, match="must be null"):
        run(call("request_return", {"order_id": "O-1001", "sku": "RUN-9", "kind": "refund",
                                    "new_sku": "RUN-10", "confirm": False}))


def _verify(task):
    import os
    p = subprocess.run([sys.executable, str(ROOT / "verify.py"), str(ROOT / "tasks" / task)],
                       capture_output=True, text=True, env={**os.environ})
    return json.loads(p.stdout)


def test_task_R117_preview_changes_nothing_then_confirm(fresh_db):
    args = {"order_id": "O-1001", "sku": "RUN-9", "kind": "exchange", "new_sku": "RUN-10"}
    assert run(call("request_return", {**args, "confirm": False}))["outcome"] == "preview"
    assert _verify("R-117.json")["reward"] < 1.0                  # preview wrote nothing
    assert run(call("request_return", {**args, "confirm": True}))["outcome"] == "done"
    assert run(call("request_return", {**args, "confirm": True}))["outcome"] == "already"
    q = run(call("quote_cart", {"customer_id": "C001", "items": [{"sku": "SOCK-L", "qty": 1}],
                                "coupon_codes": [], "points": 1000}))
    assert q["outcome"] == "ok" and q["total_cents"] == 1098
    assert _verify("R-117.json")["reward"] == 1.0


def test_task_R201_refusal_is_correct_end_state(fresh_db):
    r = run(call("request_return", {"order_id": "O-1003", "sku": "SOCK-M", "kind": "refund",
                                    "new_sku": None, "confirm": True}))
    assert r["outcome"] == "outside_window" and "deadline" in r["reason"]
    assert _verify("R-201.json")["reward"] == 1.0


def test_verifier_flags_costly_violation_written_behind_the_tools(fresh_db):
    import sqlite3
    con = sqlite3.connect(fresh_db)   # simulate a buggy agent/tool that bypassed the rules
    con.execute("INSERT INTO returns (line_id, kind, new_sku, refund_cents, created) VALUES (3,'refund',NULL,1499,'2026-10-18')")
    con.commit()
    rep = _verify("R-201.json")
    assert rep["reward"] == -1.0 and rep["costly_violations"]


def test_verifier_imports_nothing_from_fineprint():
    tree = ast.parse((ROOT / "verify.py").read_text())
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
           {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not any(m and m.startswith("fineprint") for m in mods)
