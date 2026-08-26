"""
send_webhook.py — Webhook simulator (§5.19)

Signs and POSTs a settlement.processed event to the local API.

Usage:
    python scripts\send_webhook.py

Expected responses:
    First run:   200 {"received": true}
    Second run:  200 {"received": true, "duplicate": true}
"""
import hashlib
import hmac
import json
import os
import sys

import requests

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    print("ERROR: RAZORPAY_WEBHOOK_SECRET is not set", file=sys.stderr)
    sys.exit(1)

BASE_URL = os.getenv("API_URL", "http://localhost:8000")

payload = {
    "entity": "event",
    "event": "settlement.processed",
    "created_at": int(__import__("time").time()),
    "payload": {
        "settlement": {
            "entity": {
                "id": "setl_test_001",
                "amount": 9764,
                "fees": 200,
                "tax": 36,
                "utr": "UTRTEST001",
                "status": "processed",
            }
        }
    },
}

body = json.dumps(payload, separators=(",", ":")).encode()

signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    body,
    hashlib.sha256,
).hexdigest()

response = requests.post(
    f"{BASE_URL}/webhooks/razorpay",
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "evt_test_001",
    },
    timeout=10,
)

print(response.status_code, response.text)
