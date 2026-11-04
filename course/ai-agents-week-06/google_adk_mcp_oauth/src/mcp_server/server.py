"""
MCP Resource Server protected by Google OAuth 2.0.

Serves both as:
  - Resource Server (RS): protected /mcp endpoint
  - Authorization Server facade: DCR, PKCE, resource-bound tokens, delegates to Google
"""

from __future__ import annotations

import logging
import os
from typing import Any

from starlette.responses import JSONResponse
from starlette.requests import Request

import dotenv

from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider
import uuid
import datetime

# -----------------------------------------------------------------------------
# Dummy In-Memory Store
# -----------------------------------------------------------------------------

PRODUCTS = {
    "p1": {"name": "Pro Plan", "price": 10.0},
    "p2": {"name": "Premium Plan", "price": 25.0},
}

USER_BALANCES: dict[str, float] = {}
USER_ORDERS: dict[str, list] = {}



# -----------------------------------------------------------------------------
# Logging & Environment
# -----------------------------------------------------------------------------

logger = logging.getLogger("mcp.rs.google")
logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

BASE_URL = os.environ.get("RS_BASE_URL", "http://localhost:8026")
HOST = os.environ.get("RS_HOST", "0.0.0.0")
PORT = int(os.environ.get("RS_PORT", "8026"))

MCP_PATH = os.environ.get("MCP_PATH", "/mcp")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

REDIRECT_PATH = os.environ.get("GOOGLE_REDIRECT_PATH", "/auth/callback")

REQUIRED_SCOPES = os.environ.get(
    "REQUIRED_SCOPES",
    "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
).split()

ALLOWED_CLIENT_REDIRECTS = os.environ.get(
    "ALLOWED_CLIENT_REDIRECT_URIS",
    "http://localhost:*;http://127.0.0.1:*",
).split(";")

RESOURCE = f"{BASE_URL}{MCP_PATH}"


# -----------------------------------------------------------------------------
# OAuth Provider (AS facade delegating to Google)
# -----------------------------------------------------------------------------

google_auth = GoogleProvider(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    base_url=BASE_URL,
    redirect_path=REDIRECT_PATH,
    required_scopes=REQUIRED_SCOPES,
    allowed_client_redirect_uris=ALLOWED_CLIENT_REDIRECTS,
)


# -----------------------------------------------------------------------------
# MCP Application
# -----------------------------------------------------------------------------

mcp = FastMCP(
    name="MCP RS with Google OAuth",
    instructions=(
        "Protected MCP server that delegates OAuth to Google via a DCR-capable proxy."
    ),
    auth=google_auth,
)


# -----------------------------------------------------------------------------
# MCP Tools (protected; require valid Google bearer token)
# -----------------------------------------------------------------------------

@mcp.tool()
async def purchase_item(item_id: str) -> dict[str, Any]:
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()
    user_id = token.claims.get("sub")
    email = token.claims.get("email")
    name = token.claims.get("name")

    if not user_id:
        return {"error": "Invalid authentication"}

    if item_id not in PRODUCTS:
        return {"error": "Invalid product"}

    product = PRODUCTS[item_id]
    price = product["price"]

    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 100.0

    balance = USER_BALANCES[user_id]

    if price > balance:
        return {"error": "Insufficient funds", "balance": balance}

    USER_BALANCES[user_id] -= price

    txn_id = str(uuid.uuid4())

    transaction = {
        "transaction_id": txn_id,
        "user_email": email,
        "user_name": name,
        "item_id": item_id,
        "item_name": product["name"],
        "amount": price,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "completed"
    }

    USER_ORDERS.setdefault(user_id, []).append(transaction)

    return {
        "message": "Purchase successful",
        "user": {
            "name": name,
            "email": email,
        },
        "transaction": transaction,
        "remaining_balance": USER_BALANCES[user_id],
    }


@mcp.tool()
async def view_my_orders() -> dict[str, Any]:
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()
    user_id = token.claims.get("sub")
    email = token.claims.get("email")
    name = token.claims.get("name")

    return {
        "user": {
            "name": name,
            "email": email,
        },
        "orders": USER_ORDERS.get(user_id, [])
    }

    
@mcp.tool()
async def refund_purchase(transaction_id: str) -> dict[str, Any]:
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()
    user_id = token.claims.get("sub")
    email = token.claims.get("email")
    name = token.claims.get("name")

    orders = USER_ORDERS.get(user_id, [])

    for order in orders:
        if order["transaction_id"] == transaction_id:
            if order["status"] == "refunded":
                return {"error": "Already refunded"}

            order["status"] = "refunded"
            USER_BALANCES[user_id] += order["amount"]

            return {
                "message": "Refund successful",
                "user": {
                    "name": name,
                    "email": email,
                },
                "updated_balance": USER_BALANCES[user_id],
                "transaction": order
            }

    return {"error": "Transaction not found"}

# -----------------------------------------------------------------------------
# unprotected endpoint
# -----------------------------------------------------------------------------


@mcp.custom_route("/products", methods=["GET"])
async def list_products(request: Request):
    """
    Public endpoint to list available products.
    No authentication required.
    """
    return JSONResponse({"products": PRODUCTS})



# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        logger.error(
            "GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not set. "
            "Put them in your shell env or a .env file before starting the server."
        )
        raise SystemExit(1)

    logger.info("🚀 RS base URL: %s", BASE_URL)
    logger.info("🛣  MCP endpoint path: %s", MCP_PATH)
    logger.info("🔁 Redirect path (Google): %s", REDIRECT_PATH)
    logger.info("🔐 Required scopes: %s", " ".join(REQUIRED_SCOPES))
    logger.info("🏁 Allowed DCR client redirects: %s", ALLOWED_CLIENT_REDIRECTS)
    logger.info("🎯 Resource (audience): %s", RESOURCE)

    mcp.run(
        transport="streamable-http",
        host=HOST,
        port=PORT,
        path=MCP_PATH,
    )
