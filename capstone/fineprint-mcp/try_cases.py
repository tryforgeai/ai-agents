"""Edge cases against the running server (python3 -m fineprint.server --http).
Read-only: every case uses confirm=False or quote_cart, so it can be run any number of times.
Exit code 0 = all as expected.
"""
import asyncio
import sys

from fastmcp import Client

RET = "request_return"
QC = "quote_cart"
CASES = [  # (tool, args, expected outcome, expected rule prefix or None, what it shows)
    (RET, {"order_id": "O-1005", "sku": "RUN-10", "kind": "refund", "new_sku": None, "confirm": False},
     "preview", "R1", "day 30 exactly: still refundable"),
    (RET, {"order_id": "O-1002", "sku": "JKT-M", "kind": "refund", "new_sku": None, "confirm": False},
     "outside_window", "R1", "day 38: past the refund window"),
    (RET, {"order_id": "O-1002", "sku": "JKT-M", "kind": "exchange", "new_sku": "JKT-L", "confirm": False},
     "out_of_stock", "R3", "day 38 exchange is allowed, but size L is out of stock"),
    (RET, {"order_id": "O-1004", "sku": "TEE-CLR", "kind": "refund", "new_sku": None, "confirm": False},
     "final_sale", "R4", "final-sale item"),
    (RET, {"order_id": "O-1001", "sku": "RUN-9", "kind": "exchange", "new_sku": "SOCK-L", "confirm": False},
     "invalid_exchange", "R3", "exchange for a different product"),
    (QC, {"customer_id": "C001", "items": [{"sku": "RUN-10", "qty": 1}, {"sku": "SOCK-L", "qty": 1}],
          "coupon_codes": ["SHOES15", "BIG20"], "points": 0},
     "rejected", "C6", "threshold checked after the category discount"),
    (QC, {"customer_id": "C001", "items": [{"sku": "JKT-M", "qty": 1}], "coupon_codes": ["BIG20"], "points": 100},
     "rejected", "P2", "points + threshold coupon"),
    (QC, {"customer_id": "C001", "items": [{"sku": "SOCK-L", "qty": 1}], "coupon_codes": ["OLD5"], "points": 0},
     "rejected", "C7", "expired coupon"),
    (QC, {"customer_id": "C002", "items": [{"sku": "SOCK-L", "qty": 1}], "coupon_codes": ["SAVE10"], "points": 0},
     "rejected", "C7", "someone else's coupon"),
    (QC, {"customer_id": "C001", "items": [{"sku": "RUN-9", "qty": 1}],
          "coupon_codes": ["SHOES15", "SAVE10", "SHIPFREE"], "points": 0},
     "ok", None, "category + percent + free shipping stack"),
    (RET, {"order_id": "O-9999", "sku": "RUN-9", "kind": "refund", "new_sku": None, "confirm": False},
     "ToolError", None, "unknown order -> clear error, not a guess"),
]


async def main() -> int:
    bad = 0
    async with Client("http://localhost:8000/mcp") as c:
        for tool, args, want, rule, why in CASES:
            try:
                r = (await c.call_tool(tool, args)).structured_content
                got = r["outcome"]
                text = (r.get("reasons") or [r.get("reason", "")])[0] if got != "ok" else f"total ${r['total_cents']/100:.2f}"
                ok = got == want and (rule is None or text.startswith(rule))
                if got == "rejected" and r["total_cents"] is not None:
                    ok, text = False, "rejected quote still shows a total"
            except Exception as e:
                got, text = "ToolError", str(e).splitlines()[0]
                ok = want == "ToolError"
            bad += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {why:48} {got:16} {text[:60]}")
    print(f"\n{len(CASES) - bad}/{len(CASES)} as expected")
    return 1 if bad else 0


sys.exit(asyncio.run(main()))
