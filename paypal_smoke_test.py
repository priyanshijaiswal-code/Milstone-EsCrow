"""Step 3: prove authorize -> capture works in your sandbox.

Run from backend/:  python scripts/paypal_smoke_test.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paypal

order = paypal.create_order(
    amount=10.00, description="Smoke test milestone", reference_id="smoke-1",
    return_url="http://localhost:8000/paypal/return",
    cancel_url="http://localhost:8000/paypal/cancel",
)
print("Order:", order["id"], "status:", order["status"])
print("\nOpen this URL, log in with your SANDBOX PERSONAL (client) account and approve:")
print(order["approve_url"])
print("\n(The browser will redirect to localhost and show an error. That's fine.)")
input("\nPress Enter after approving...")

auth = paypal.authorize_order(order["id"])
print("Authorized. authorization_id:", auth["authorization_id"])
input("Press Enter to CAPTURE (release funds to freelancer)...")

cap = paypal.capture_authorization(auth["authorization_id"])
print("Capture status:", cap["status"])
print("\nIf you see COMPLETED, check the sandbox Business account balance. Step 3 done.")
