"""Thin PayPal Orders v2 / Payments v2 client (sandbox by default)."""
import os
import uuid

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")


def _token() -> str:
    r = httpx.post(
        f"{BASE}/v1/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
        "PayPal-Request-Id": str(uuid.uuid4()),  # idempotency key
    }


def _post(path: str, body: dict | None = None) -> dict:
    r = httpx.post(f"{BASE}{path}", headers=_headers(), json=body or {}, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"PayPal {path} -> {r.status_code}: {r.text}")
    return r.json()


def create_order(amount: float, description: str, reference_id: str,
                 return_url: str, cancel_url: str) -> dict:
    """Create an order with intent AUTHORIZE (funds held, not captured)."""
    body = {
        "intent": "AUTHORIZE",
        "purchase_units": [{
            "reference_id": reference_id,
            "description": description,
            "amount": {"currency_code": "USD", "value": f"{amount:.2f}"},
        }],
        "payment_source": {"paypal": {"experience_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "user_action": "PAY_NOW",
            "shipping_preference": "NO_SHIPPING",
        }}},
    }
    order = _post("/v2/checkout/orders", body)
    order["approve_url"] = next(
        (l["href"] for l in order.get("links", [])
         if l["rel"] in ("payer-action", "approve")), None)
    return order


def authorize_order(order_id: str) -> dict:
    """Call after the client approves. Returns the order incl. authorization id."""
    data = _post(f"/v2/checkout/orders/{order_id}/authorize")
    data["authorization_id"] = (
        data["purchase_units"][0]["payments"]["authorizations"][0]["id"])
    return data


def capture_authorization(authorization_id: str) -> dict:
    """Release the held funds to the freelancer."""
    return _post(f"/v2/payments/authorizations/{authorization_id}/capture",
                 {"final_capture": True})


def void_authorization(authorization_id: str) -> dict:
    """Release the hold back to the client (no money moves)."""
    return _post(f"/v2/payments/authorizations/{authorization_id}/void")
