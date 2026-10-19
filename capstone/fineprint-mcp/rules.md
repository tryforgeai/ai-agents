# FinePrint store rules (synthetic, written from generic public e-commerce policies)

No employer data, code or internal rules. All customers, products and orders are invented.
Money is stored in integer cents. "Today" is fixed by `FINEPRINT_TODAY` (default 2026-10-18).
Each numbered rule maps to a key in `rules.json`.

## Returns
- R1 `refund_window_days = 30`: a refund is allowed up to and including day 30 after delivery.
- R2 `exchange_window_days = 45`: an exchange is allowed up to and including day 45 after delivery.
- R3 An exchange must be for another SKU of the **same product** (size/colour) that is **in stock**.
- R4 Items marked `final_sale` cannot be refunded or exchanged.
- R5 One return per order line. A second request on the same line is `already`.
- R6 The refund amount is the price actually paid for that line (stored on the order line).

## Coupons
- C1 Kinds: `percent`, `amount`, `threshold`, `category`, `free_shipping`.
- C2 At most **one order coupon** (`percent`, `amount` or `threshold`) per cart.
- C3 At most **one `category` coupon**; it stacks with one order coupon.
- C4 `free_shipping` stacks with anything.
- C5 Order of application: category coupon first, then the order coupon.
- C6 A `threshold` coupon checks its minimum against the subtotal **after** the category discount.
- C7 A coupon must belong to the customer, be unused, and not be expired (expiry day inclusive).

## Points
- P1 `points_per_dollar_redeem = 100`: 100 points = $1.00. Redeem in multiples of 100.
- P2 Points cannot be combined with a `threshold` coupon.
- P3 Points cannot take the total below $0 and cannot exceed the customer's balance.

## Shipping
- S1 `shipping_cents = 599` when the discounted subtotal is under `free_shipping_min_cents = 5000`; otherwise free.
