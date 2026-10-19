"""SQLite access and deterministic synthetic seed data. No business rules live here."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "rules.json").read_text(encoding="utf-8"))

SCHEMA = """
CREATE TABLE customers (customer_id TEXT PRIMARY KEY, name TEXT, points INTEGER);
CREATE TABLE products  (sku TEXT PRIMARY KEY, product_id TEXT, name TEXT, category TEXT,
                        price_cents INTEGER, stock INTEGER, final_sale INTEGER);
CREATE TABLE orders    (order_id TEXT PRIMARY KEY, customer_id TEXT, delivered TEXT);
CREATE TABLE order_lines (line_id INTEGER PRIMARY KEY, order_id TEXT, sku TEXT, paid_cents INTEGER);
CREATE TABLE coupons   (code TEXT PRIMARY KEY, customer_id TEXT, kind TEXT, value INTEGER,
                        min_cents INTEGER, category TEXT, expires TEXT, used INTEGER);
CREATE TABLE returns   (return_id INTEGER PRIMARY KEY AUTOINCREMENT, line_id INTEGER UNIQUE,
                        kind TEXT, new_sku TEXT, refund_cents INTEGER, created TEXT);
"""

CUSTOMERS = [("C001", "Ana Ruiz", 1200), ("C002", "Ben Okafor", 50), ("C003", "Chen Wei", 0)]
PRODUCTS = [
    ("RUN-9", "RUN", "Trail runner, size 9", "shoes", 8999, 3, 0),
    ("RUN-10", "RUN", "Trail runner, size 10", "shoes", 8999, 2, 0),
    ("RUN-11", "RUN", "Trail runner, size 11", "shoes", 8999, 0, 0),
    ("SOCK-M", "SOCK", "Merino socks, M", "accessories", 1499, 20, 0),
    ("SOCK-L", "SOCK", "Merino socks, L", "accessories", 1499, 20, 0),
    ("JKT-M", "JKT", "Rain jacket, M", "outerwear", 12999, 5, 0),
    ("JKT-L", "JKT", "Rain jacket, L", "outerwear", 12999, 0, 0),
    ("TEE-CLR", "TEE", "Clearance tee", "tops", 999, 10, 1),
]
ORDERS = [  # delivered dates are relative to the default today, 2026-10-18
    ("O-1001", "C001", "2026-09-28"),  # 20 days ago
    ("O-1002", "C001", "2026-09-10"),  # 38 days ago
    ("O-1003", "C002", "2026-08-25"),  # 54 days ago
    ("O-1004", "C002", "2026-10-15"),  # final-sale item
    ("O-1005", "C003", "2026-09-18"),  # exactly 30 days ago
]
LINES = [(1, "O-1001", "RUN-9", 8999), (2, "O-1002", "JKT-M", 11699), (3, "O-1003", "SOCK-M", 1499),
         (4, "O-1004", "TEE-CLR", 999), (5, "O-1005", "RUN-10", 8999)]
COUPONS = [
    ("SAVE10", "C001", "percent", 10, None, None, "2026-12-31", 0),
    ("FIVEOFF", "C001", "amount", 500, None, None, "2026-12-31", 0),
    ("BIG20", "C001", "threshold", 2000, 10000, None, "2026-11-30", 0),
    ("SHOES15", "C001", "category", 15, None, "shoes", "2026-12-31", 0),
    ("SHIPFREE", "C001", "free_shipping", 0, None, None, "2026-12-31", 0),
    ("OLD5", "C001", "amount", 500, None, None, "2026-10-01", 0),
    ("USED10", "C002", "percent", 10, None, None, "2026-12-31", 1),
    ("BEN-ACC", "C002", "category", 20, None, "accessories", "2026-12-31", 0),
]


def db_path() -> Path:
    return Path(os.environ.get("FINEPRINT_DB", ROOT / "fineprint.db"))


def today() -> date:
    return date.fromisoformat(os.environ.get("FINEPRINT_TODAY", "2026-10-18"))


def seed(path: Path | None = None) -> Path:
    """(Re)create the database with the synthetic data. Deterministic."""
    path = Path(path or db_path())
    path.unlink(missing_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO customers VALUES (?,?,?)", CUSTOMERS)
    con.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", PRODUCTS)
    con.executemany("INSERT INTO orders VALUES (?,?,?)", ORDERS)
    con.executemany("INSERT INTO order_lines VALUES (?,?,?,?)", LINES)
    con.executemany("INSERT INTO coupons VALUES (?,?,?,?,?,?,?,?)", COUPONS)
    con.commit()
    con.close()
    return path


def connect() -> sqlite3.Connection:
    path = db_path()
    if not path.exists():
        seed(path)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


if __name__ == "__main__":
    print("seeded", seed())
