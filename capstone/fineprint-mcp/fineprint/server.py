"""FinePrint MCP server. Tools only read/write the store and call pure code in decide.py.

Design (Tools Prelude + kit):
- few, task-sized tools; observation tools vs one action tool (p.9-12)
- strong types in and out, so the schema carries the contract (p.14, lab 2b/2c)
- docstrings say when to use AND when not to (#25, p.15)
- preconditions raise ToolError with whose problem it is; postconditions re-read the DB (p.16, #48)
- output trimmed to intent, with source and as_of (p.17)
- the one write needs confirm=True; confirm=False returns a preview (principle 6)
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

from . import decide
from .store import RULES, connect, today

mcp = FastMCP("FinePrint Store")
SOURCE = "fineprint.db (synthetic store)"


def _stamp() -> dict:
    return {"source": SOURCE, "as_of": today().isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


# ---------- output / input models ----------

class OrderLineView(BaseModel):
    line_id: int
    sku: str
    name: str
    paid_cents: int
    final_sale: bool
    returned: Literal["no", "refund", "exchange"]


class OrderView(BaseModel):
    order_id: str
    customer_id: str
    delivered: str
    days_since_delivery: int
    lines: list[OrderLineView]
    source: str
    as_of: str
    generated_at: str


class CouponView(BaseModel):
    code: str
    kind: str
    value: int
    min_cents: int | None
    category: str | None
    expires: str
    usable_today: bool
    why_not: str | None


class CouponList(BaseModel):
    customer_id: str
    points_balance: int
    coupons: list[CouponView]
    source: str
    as_of: str
    generated_at: str


class CartItem(BaseModel):
    sku: str = Field(description="Product SKU, e.g. 'SOCK-L'")
    qty: int = Field(ge=1, le=20, description="Quantity, 1-20")


class Quote(BaseModel):
    outcome: Literal["ok", "rejected"]
    reasons: list[str]
    subtotal_cents: int
    category_discount_cents: int | None
    order_discount_cents: int | None
    shipping_cents: int | None
    points_discount_cents: int | None
    total_cents: int | None = Field(description="null when outcome is 'rejected'")
    notes: list[str]
    source: str
    as_of: str
    generated_at: str


class ReturnResult(BaseModel):
    outcome: Literal["preview", "done", "already", "final_sale", "outside_window",
                     "invalid_exchange", "out_of_stock"]
    reason: str
    order_id: str
    sku: str
    kind: Literal["refund", "exchange"]
    new_sku: str | None
    refund_cents: int
    days_since_delivery: int
    deadline: str
    notes: list[str]
    source: str
    as_of: str
    generated_at: str


# ---------- helpers ----------

def _norm_id(value: str, label: str) -> str:
    v = value.strip().upper()  # #47: normalise spelling at the boundary
    if not v:
        raise ToolError(f"{label} is empty. Ask the customer for it; do not guess.")
    return v


def _order_row(con, order_id: str):
    row = con.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
    if row is None:
        raise ToolError(f"Order {order_id} does not exist. Check the ID with the customer; "
                        "do not try other IDs.")
    return row


# ---------- tools ----------

@mcp.tool
def get_order(order_id: str) -> OrderView:
    """Look up one order: delivery date, lines, price paid per line, and whether each line
    was already returned.

    Use when the customer mentions a past purchase, a return or an exchange.
    Do not use to browse products or to price a new cart (use quote_cart).
    """
    oid = _norm_id(order_id, "order_id")
    con = connect()
    o = _order_row(con, oid)
    rows = con.execute(
        """SELECT l.line_id, l.sku, p.name, l.paid_cents, p.final_sale, r.kind AS rkind
           FROM order_lines l JOIN products p USING (sku)
           LEFT JOIN returns r ON r.line_id = l.line_id
           WHERE l.order_id=? ORDER BY l.line_id""", (oid,)).fetchall()
    delivered = date.fromisoformat(o["delivered"])
    return OrderView(
        order_id=oid, customer_id=o["customer_id"], delivered=o["delivered"],
        days_since_delivery=(today() - delivered).days,
        lines=[OrderLineView(line_id=r["line_id"], sku=r["sku"], name=r["name"],
                             paid_cents=r["paid_cents"], final_sale=bool(r["final_sale"]),
                             returned=r["rkind"] or "no") for r in rows],
        **_stamp())


@mcp.tool
def list_coupons(customer_id: str) -> CouponList:
    """List a customer's coupons with whether each is usable today, plus their points balance.

    Use before quoting a cart when the customer wants to save money.
    Do not use to decide whether coupons stack; quote_cart decides that.
    """
    cid = _norm_id(customer_id, "customer_id")
    con = connect()
    cust = con.execute("SELECT * FROM customers WHERE customer_id=?", (cid,)).fetchone()
    if cust is None:
        raise ToolError(f"Customer {cid} does not exist. Ask the customer to confirm their ID.")
    out = []
    for c in con.execute("SELECT * FROM coupons WHERE customer_id=? ORDER BY code", (cid,)):
        why = None
        if c["used"]:
            why = "already used"
        elif date.fromisoformat(c["expires"]) < today():
            why = f"expired {c['expires']}"
        out.append(CouponView(code=c["code"], kind=c["kind"], value=c["value"],
                              min_cents=c["min_cents"], category=c["category"],
                              expires=c["expires"], usable_today=why is None, why_not=why))
    return CouponList(customer_id=cid, points_balance=cust["points"], coupons=out, **_stamp())


@mcp.tool
def quote_cart(customer_id: str, items: list[CartItem], coupon_codes: list[str],
               points: int) -> Quote:
    """Price a cart with coupons and points under the store rules. Read-only: nothing is
    charged or reserved.

    Pass coupon_codes=[] and points=0 explicitly when none are wanted.
    Use to check whether a coupon combination is allowed and what the total is.
    Do not use for returns or exchanges (use request_return).
    If outcome is 'rejected', tell the customer the reasons; do not retry random combinations.
    """
    cid = _norm_id(customer_id, "customer_id")
    if not items:
        raise ToolError("items is empty. Ask the customer what they want to buy.")
    con = connect()
    cust = con.execute("SELECT * FROM customers WHERE customer_id=?", (cid,)).fetchone()
    if cust is None:
        raise ToolError(f"Customer {cid} does not exist. Ask the customer to confirm their ID.")
    lines = []
    for it in items:
        sku = _norm_id(it.sku, "sku")
        p = con.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
        if p is None:
            raise ToolError(f"SKU {sku} does not exist. Ask the customer which product they mean.")
        if p["stock"] < it.qty:
            raise ToolError(f"SKU {sku} has {p['stock']} in stock; requested {it.qty}.")
        lines.append(decide.CartLine(sku, p["category"], p["price_cents"], it.qty))
    coupons: dict[str, decide.Coupon | None] = {}
    for code in coupon_codes:
        code = _norm_id(code, "coupon code")
        r = con.execute("SELECT * FROM coupons WHERE code=?", (code,)).fetchone()
        coupons[code] = None if r is None else decide.Coupon(
            r["code"], r["customer_id"], r["kind"], r["value"], r["min_cents"], r["category"],
            date.fromisoformat(r["expires"]), bool(r["used"]))
    result = decide.quote(lines, coupons, cid, points, cust["points"], today(), RULES)
    q = Quote(**result, **_stamp())
    # postconditions: a rejection carries no price; an accepted quote adds up
    if q.outcome == "rejected":
        if q.total_cents is not None or not q.reasons:
            raise ToolError("Internal error: inconsistent rejected quote. Do not quote a price.")
    elif q.total_cents != (q.subtotal_cents - q.category_discount_cents - q.order_discount_cents
                           + q.shipping_cents - q.points_discount_cents):
        raise ToolError("Internal error: quote does not add up. Do not quote a price.")
    return q


@mcp.tool
def request_return(order_id: str, sku: str, kind: Literal["refund", "exchange"],
                   new_sku: str | None, confirm: bool) -> ReturnResult:
    """Refund or exchange one item from a past order.

    Always call first with confirm=False to get a preview, show it to the customer, and call
    again with confirm=True only after the customer says yes.
    For kind='exchange', new_sku must be another size/colour of the same product.
    For kind='refund', new_sku must be null.
    Do not use to price new purchases (use quote_cart).
    """
    oid = _norm_id(order_id, "order_id")
    s = _norm_id(sku, "sku")
    ns = _norm_id(new_sku, "new_sku") if new_sku else None
    if kind == "refund" and ns:
        raise ToolError("new_sku must be null for a refund. Use kind='exchange' to swap items.")
    if kind == "exchange" and not ns:
        raise ToolError("new_sku is required for an exchange. Ask the customer which size/colour.")
    con = connect()
    o = _order_row(con, oid)
    line = con.execute(
        """SELECT l.line_id, l.paid_cents, p.product_id, p.final_sale FROM order_lines l
           JOIN products p USING (sku) WHERE l.order_id=? AND l.sku=?""", (oid, s)).fetchone()
    if line is None:
        raise ToolError(f"Order {oid} has no item {s}. Call get_order to see its items.")
    already = con.execute("SELECT 1 FROM returns WHERE line_id=?", (line["line_id"],)).fetchone()
    new = con.execute("SELECT product_id, stock FROM products WHERE sku=?", (ns,)).fetchone() if ns else None

    d = decide.return_decision(
        kind=kind, delivered=date.fromisoformat(o["delivered"]), final_sale=bool(line["final_sale"]),
        already_returned=already is not None, paid_cents=line["paid_cents"], sku=s,
        product_id=line["product_id"], new_sku=ns,
        new_product_id=new["product_id"] if new else None,
        new_stock=new["stock"] if new else None, today=today(), rules=RULES)

    outcome = d.pop("outcome")
    if outcome == "eligible":
        outcome = "done" if confirm else "preview"
        if confirm:
            with con:  # one transaction
                con.execute("INSERT INTO returns (line_id, kind, new_sku, refund_cents, created) "
                            "VALUES (?,?,?,?,?)", (line["line_id"], kind, ns, d["refund_cents"],
                                                   today().isoformat()))
                con.execute("UPDATE products SET stock = stock + 1 WHERE sku=?", (s,))
                if ns:
                    con.execute("UPDATE products SET stock = stock - 1 WHERE sku=?", (ns,))
            # postcondition: read the write back
            if con.execute("SELECT 1 FROM returns WHERE line_id=?", (line["line_id"],)).fetchone() is None:
                raise ToolError("Internal error: the return was not recorded. Nothing was charged; "
                                "tell the customer to retry later.")
        else:
            d["notes"].append("preview only: nothing changed; call again with confirm=True after the customer agrees")
    return ReturnResult(outcome=outcome, order_id=oid, sku=s, kind=kind, new_sku=ns, **d, **_stamp())


def main() -> None:
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="http", port=8000)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
