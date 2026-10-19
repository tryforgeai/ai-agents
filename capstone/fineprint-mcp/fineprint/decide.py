"""Pure decision code: no I/O, no LLM, no clock. Every rule cites its id in rules.md.

Inputs are plain data; outputs are dicts with a closed `outcome` and `notes` that record
every choice the code made (technique #7: visible readings).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Coupon:
    code: str
    owner: str
    kind: str
    value: int
    min_cents: int | None
    category: str | None
    expires: date
    used: bool


@dataclass(frozen=True)
class CartLine:
    sku: str
    category: str
    unit_cents: int
    qty: int


def _pct(amount: int, pct: int) -> int:
    return (amount * pct + 50) // 100  # round half up, in cents


def quote(lines: list[CartLine], coupons: dict[str, Coupon | None], customer_id: str,
          points: int, balance: int, today: date, rules: dict) -> dict:
    """Price a cart. Outcome is 'ok' or 'rejected'; a rejection lists every broken rule."""
    reasons: list[str] = []
    notes: list[str] = []
    subtotal = sum(l.unit_cents * l.qty for l in lines)

    valid: list[Coupon] = []
    for code, c in coupons.items():
        if c is None:
            reasons.append(f"C7 coupon {code} does not exist")
        elif c.owner != customer_id:
            reasons.append(f"C7 coupon {code} belongs to another customer")
        elif c.used:
            reasons.append(f"C7 coupon {code} was already used")
        elif c.expires < today:
            reasons.append(f"C7 coupon {code} expired on {c.expires.isoformat()}")
        else:
            valid.append(c)

    order_c = [c for c in valid if c.kind in rules["order_coupon_kinds"]]
    cat_c = [c for c in valid if c.kind == "category"]
    ship_c = [c for c in valid if c.kind == "free_shipping"]
    if len(order_c) > 1:
        reasons.append("C2 only one order coupon allowed, got " + ", ".join(c.code for c in order_c))
    if len(cat_c) > 1:
        reasons.append("C3 only one category coupon allowed, got " + ", ".join(c.code for c in cat_c))

    # C5: category first
    cat_discount = 0
    if len(cat_c) == 1:
        c = cat_c[0]
        base = sum(l.unit_cents * l.qty for l in lines if l.category == c.category)
        cat_discount = _pct(base, c.value)
        if base == 0:
            notes.append(f"{c.code} applies to '{c.category}' but the cart has none; discount 0")
    after_cat = subtotal - cat_discount

    order_discount = 0
    if len(order_c) == 1:
        c = order_c[0]
        if c.kind == "percent":
            order_discount = _pct(after_cat, c.value)
        elif c.kind == "amount":
            order_discount = min(c.value, after_cat)
        elif c.kind == "threshold":  # C6: minimum checked after category discount
            if after_cat < (c.min_cents or 0):
                reasons.append(f"C6 {c.code} needs ${(c.min_cents or 0)/100:.2f} after category "
                               f"discount; cart has ${after_cat/100:.2f}")
            else:
                order_discount = min(c.value, after_cat)
    goods = after_cat - order_discount

    # S1 / C4
    if ship_c:
        shipping = 0
        notes.append(f"{ship_c[0].code}: free shipping")
    else:
        shipping = 0 if goods >= rules["free_shipping_min_cents"] else rules["shipping_cents"]
    before_points = goods + shipping

    # P1-P3
    per = rules["points_per_dollar_redeem"]
    points_discount = 0
    if points:
        if points < 0 or points % per:
            reasons.append(f"P1 points must be a positive multiple of {per}, got {points}")
        elif points > balance:
            reasons.append(f"P3 customer has {balance} points, asked for {points}")
        elif any(c.kind == "threshold" for c in order_c):
            reasons.append("P2 points cannot be combined with a threshold coupon")
        else:
            points_discount = points // per * 100
            if points_discount > before_points:
                reasons.append(f"P3 {points} points (${points_discount/100:.2f}) exceed the "
                               f"total ${before_points/100:.2f}")
                points_discount = 0

    if reasons:  # never show a price for a cart the store would not accept
        notes.append("rejected: no total is given; fix the reasons above and quote again")
        return {"outcome": "rejected", "reasons": reasons, "subtotal_cents": subtotal,
                "category_discount_cents": None, "order_discount_cents": None,
                "shipping_cents": None, "points_discount_cents": None, "total_cents": None,
                "notes": notes}
    return {
        "outcome": "ok",
        "reasons": reasons,
        "subtotal_cents": subtotal,
        "category_discount_cents": cat_discount,
        "order_discount_cents": order_discount,
        "shipping_cents": shipping,
        "points_discount_cents": points_discount,
        "total_cents": before_points - points_discount,
        "notes": notes,
    }


def return_decision(*, kind: str, delivered: date, final_sale: bool, already_returned: bool,
                    paid_cents: int, sku: str, product_id: str, new_sku: str | None,
                    new_product_id: str | None, new_stock: int | None, today: date,
                    rules: dict) -> dict:
    """Decide one return. Outcome is one of a closed list:
    eligible | already | final_sale | outside_window | invalid_exchange | out_of_stock."""
    days = (today - delivered).days
    window = rules["refund_window_days"] if kind == "refund" else rules["exchange_window_days"]
    deadline = delivered + timedelta(days=window)
    base = {"days_since_delivery": days, "deadline": deadline.isoformat(), "refund_cents": 0,
            "notes": [f"{kind} window is {window} days (R1/R2); delivered {delivered.isoformat()}"]}

    def out(outcome: str, reason: str, **extra) -> dict:
        return {**base, "outcome": outcome, "reason": reason, **extra}

    if already_returned:  # R5 first: an already-processed line is 'already', whatever else holds
        return out("already", "R5 this order line already has a return")
    if final_sale:
        return out("final_sale", "R4 final-sale items cannot be refunded or exchanged")
    if days > window:
        return out("outside_window", f"R{'1' if kind == 'refund' else '2'} day {days} is past the "
                                     f"{window}-day window (deadline {deadline.isoformat()})")
    if kind == "exchange":
        if new_product_id is None:
            return out("invalid_exchange", f"R3 SKU {new_sku} does not exist")
        if new_sku == sku:
            return out("invalid_exchange", "R3 the new SKU is the same as the one being returned")
        if new_product_id != product_id or new_sku is None:
            return out("invalid_exchange", "R3 an exchange must be another size/colour of the same product")
        if not new_stock or new_stock < 1:
            return out("out_of_stock", f"R3 {new_sku} is out of stock")
        return out("eligible", f"R2 exchange allowed on day {days} of {window}")
    return out("eligible", f"R1 refund allowed on day {days} of {window}", refund_cents=paid_cents)
