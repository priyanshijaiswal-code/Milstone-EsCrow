# Milestone Escrow (working title)

Freelancer milestone payments held via PayPal, released after an AI verifier
checks the deliverable against the agreed acceptance checklist. A human always
makes the final release decision.

Built for the PayPal AI Hackathon.

## Setup
1. `cd backend && python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in PayPal sandbox credentials
4. Smoke test the money flow: `python scripts/paypal_smoke_test.py`
5. Run the API: `uvicorn main:app --reload`

(More to come: architecture, demo link, tools used.)
