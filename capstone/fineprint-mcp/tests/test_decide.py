"""Decide-layer cases, one per rule line in rules.md. No database, no MCP."""
import json
from datetime import date
from pathlib import Path

import pytest

from fineprint.decide import CartLine, Coupon, quote, return_decision

RULES = json.loads((Path(__file__).resolve().parents[1] / "rules.json").read_text())
TODAY = date(2026, 10, 18)
SHOES = CartLine("RUN-9", "shoes", 8999, 1)
SOCKS = CartLine("SOCK-L", "accessories", 1499, 1)


def C(code, kind, value, min_cents=None, category=None, owner="C001", expires="2026-12-31", used=False):
    return Coupon(code, owner, kind, value, min_cents, category, date.fromisoformat(expires), used)


def q(lines, coupons=(), points=0, balance=1200):
    return quote(list(lines), {c.code: c for c in coupons}, "C001", points, balance, TODAY, RULES)


def test_s1_shipping_under_50():
    r = q([SOCKS])
    assert r["outcome"] == "ok" and r["shipping_cents"] == 599 and r["total_cents"] == 2098


def test_s1_free_shipping_at_50():
    assert q([SHOES])["shipping_cents"] == 0


def test_c2_two_order_coupons_rejected():
    r = q([SHOES], [C("SAVE10", "percent", 10), C("FIVEOFF", "amount", 500)])
    assert r["outcome"] == "rejected" and r["reasons"][0].startswith("C2")


def test_c3_c5_category_then_percent():
    r = q([SHOES], [C("SHOES15", "category", 15, category="shoes"), C("SAVE10", "percent", 10)])
    assert r["category_discount_cents"] == 1350          # 15% of 89.99
    assert r["order_discount_cents"] == 765               # 10% of 76.49, after category
    assert r["outcome"] == "ok"


def test_c4_free_shipping_stacks():
    r = q([SOCKS], [C("SAVE10", "percent", 10), C("SHIPFREE", "free_shipping", 0)])
    assert r["outcome"] == "ok" and r["shipping_cents"] == 0


def test_c6_threshold_checked_after_category_discount():
    jacket = CartLine("JKT-M", "outerwear", 12999, 1)
    shoes2 = CartLine("RUN-10", "shoes", 8999, 1)
    ok = q([jacket], [C("BIG20", "threshold", 2000, min_cents=10000)])
    assert ok["outcome"] == "ok" and ok["order_discount_cents"] == 2000
    # 89.99 + 15% off shoes = 76.49 < 100 -> threshold fails even though list price would not
    r = q([shoes2, SOCKS], [C("SHOES15", "category", 15, category="shoes"),
                           C("BIG20", "threshold", 2000, min_cents=10000)])
    assert r["outcome"] == "rejected" and any(x.startswith("C6") for x in r["reasons"])


@pytest.mark.parametrize("coupon,why", [
    (C("OLD5", "amount", 500, expires="2026-10-01"), "expired"),
    (C("USED10", "percent", 10, used=True), "already used"),
    (C("BEN-ACC", "category", 20, owner="C002", category="accessories"), "another customer"),
])
def test_c7_unusable_coupons(coupon, why):
    r = q([SOCKS], [coupon])
    assert r["outcome"] == "rejected" and why in r["reasons"][0]


def test_c7_expiry_day_is_inclusive():
    assert q([SOCKS], [C("LAST", "amount", 500, expires="2026-10-18")])["outcome"] == "ok"


def test_p1_points_multiple_of_100():
    assert q([SOCKS], points=150)["outcome"] == "rejected"


def test_p1_points_value():
    r = q([SOCKS], points=1000)
    assert r["outcome"] == "ok" and r["points_discount_cents"] == 1000 and r["total_cents"] == 1098


def test_p2_points_with_threshold_rejected():
    jacket = CartLine("JKT-M", "outerwear", 12999, 1)
    r = q([jacket], [C("BIG20", "threshold", 2000, min_cents=10000)], points=100)
    assert r["outcome"] == "rejected" and any(x.startswith("P2") for x in r["reasons"])


def test_p3_points_over_balance_and_over_total():
    assert q([SOCKS], points=1300)["outcome"] == "rejected"            # balance 1200
    assert q([SOCKS], points=2200, balance=5000)["outcome"] == "rejected"  # $22 > $20.98


def R(**kw):
    base = dict(kind="refund", delivered=date(2026, 9, 28), final_sale=False, already_returned=False,
                paid_cents=8999, sku="RUN-9", product_id="RUN", new_sku=None, new_product_id=None,
                new_stock=None, today=TODAY, rules=RULES)
    return return_decision(**{**base, **kw})


def test_r1_refund_day_30_inclusive_and_day_31_out():
    assert R(delivered=date(2026, 9, 18))["outcome"] == "eligible"      # day 30
    assert R(delivered=date(2026, 9, 17))["outcome"] == "outside_window"  # day 31


def test_r2_exchange_day_38_ok_refund_not():
    d = date(2026, 9, 10)
    assert R(delivered=d)["outcome"] == "outside_window"
    assert R(delivered=d, kind="exchange", new_sku="RUN-10", new_product_id="RUN", new_stock=2)["outcome"] == "eligible"


def test_r3_exchange_rules():
    ex = dict(kind="exchange")
    assert R(**ex, new_sku="JKT-M", new_product_id="JKT", new_stock=5)["outcome"] == "invalid_exchange"
    assert R(**ex, new_sku="RUN-9", new_product_id="RUN", new_stock=3)["outcome"] == "invalid_exchange"
    assert R(**ex, new_sku="RUN-11", new_product_id="RUN", new_stock=0)["outcome"] == "out_of_stock"
    assert R(**ex, new_sku="NOPE", new_product_id=None, new_stock=None)["outcome"] == "invalid_exchange"


def test_r4_final_sale_and_r5_already_first():
    assert R(final_sale=True)["outcome"] == "final_sale"
    assert R(final_sale=True, already_returned=True)["outcome"] == "already"


def test_r6_refund_amount_is_price_paid():
    assert R(paid_cents=11699, delivered=date(2026, 10, 1))["refund_cents"] == 11699


def test_rejected_quote_has_no_total():
    r = q([SHOES], [C("SAVE10", "percent", 10), C("FIVEOFF", "amount", 500)])
    assert r["outcome"] == "rejected" and r["total_cents"] is None and r["shipping_cents"] is None
    assert r["subtotal_cents"] == 8999
