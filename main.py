"""Minimal escrow API. In-memory store for now; swap for Postgres (db/schema.sql)."""
import os
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import paypal

app = FastAPI(title="Milestone Escrow")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
MILESTONES: dict[str, dict] = {}


class MilestoneIn(BaseModel):
    title: str
    amount: float


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/milestones")
def create_milestone(m: MilestoneIn):
    mid = str(uuid.uuid4())[:8]
    MILESTONES[mid] = {"id": mid, "title": m.title, "amount": m.amount,
                       "status": "created"}
    return MILESTONES[mid]


def _get(mid: str) -> dict:
    if mid not in MILESTONES:
        raise HTTPException(404, "milestone not found")
    return MILESTONES[mid]


@app.post("/milestones/{mid}/fund")
def fund(mid: str):
    """Client starts funding: returns PayPal approval URL."""
    m = _get(mid)
    order = paypal.create_order(
        m["amount"], m["title"], mid,
        return_url=f"{APP_BASE_URL}/paypal/return?milestone_id={mid}",
        cancel_url=f"{APP_BASE_URL}/paypal/cancel?milestone_id={mid}",
    )
    m.update(order_id=order["id"], status="awaiting_approval")
    return {"approve_url": order["approve_url"]}


@app.get("/paypal/return")
def paypal_return(milestone_id: str, token: str):
    """PayPal redirects here after the client approves; token = order id."""
    m = _get(milestone_id)
    auth = paypal.authorize_order(token)
    m.update(authorization_id=auth["authorization_id"], status="funded")
    return {"status": "funded", "milestone": m}


@app.post("/milestones/{mid}/release")
def release(mid: str):
    """Capture held funds (call only after human approval)."""
    m = _get(mid)
    if m["status"] != "funded":
        raise HTTPException(400, f"cannot release from status {m['status']}")
    cap = paypal.capture_authorization(m["authorization_id"])
    m["status"] = "released"
    return {"status": m["status"], "paypal_status": cap["status"]}


@app.post("/milestones/{mid}/void")
def void(mid: str):
    m = _get(mid)
    if m["status"] != "funded":
        raise HTTPException(400, f"cannot void from status {m['status']}")
    paypal.void_authorization(m["authorization_id"])
    m["status"] = "voided"
    return {"status": m["status"]}


@app.get("/milestones/{mid}")
def read(mid: str):
    return _get(mid)
