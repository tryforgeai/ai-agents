"""Walk through task R-117 against the running server (python3 -m fineprint.server --http).
Reset the store first with: python3 -m fineprint.store
"""
import asyncio
import json

from fastmcp import Client


def show(title, result):
    print(f"\n== {title}")
    print(json.dumps(result.structured_content, indent=2, ensure_ascii=False))


async def main():
    async with Client("http://localhost:8000/mcp") as c:
        print("Tools the model sees:")
        for t in await c.list_tools():
            print(f"- {t.name}: {t.description.splitlines()[0]}")

        show("get_order O-1001", await c.call_tool("get_order", {"order_id": "o-1001"}))
        args = {"order_id": "O-1001", "sku": "RUN-9", "kind": "exchange", "new_sku": "RUN-10"}
        show("request_return (preview)", await c.call_tool("request_return", {**args, "confirm": False}))
        show("request_return (confirmed)", await c.call_tool("request_return", {**args, "confirm": True}))
        show("request_return again -> already", await c.call_tool("request_return", {**args, "confirm": True}))
        show("quote_cart socks + 1000 points", await c.call_tool("quote_cart", {
            "customer_id": "C001", "items": [{"sku": "SOCK-L", "qty": 1}],
            "coupon_codes": [], "points": 1000}))
        show("quote_cart illegal stack SAVE10 + FIVEOFF", await c.call_tool("quote_cart", {
            "customer_id": "C001", "items": [{"sku": "JKT-M", "qty": 1}],
            "coupon_codes": ["SAVE10", "FIVEOFF"], "points": 0}))
        try:
            await c.call_tool("get_order", {"order_id": "O-9999"})
        except Exception as e:
            print("\n== get_order O-9999 ->", type(e).__name__, "-", e)
    print("\nNow check the end state independently:  python3 verify.py tasks/R-117.json")


asyncio.run(main())
