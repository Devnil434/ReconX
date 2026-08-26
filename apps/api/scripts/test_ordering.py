r"""
test_ordering.py — Out-of-order event test (§5.20)

Sends webhook events in a non-natural order to verify the system:
  1. Does not crash
  2. Does not create duplicate settlement records
  3. Ends in the correct final state

Sequence:
  - settlement.processed  (arrives first — out of order)
  - payment.captured
  - settlement.processed  (duplicate — should be ignored)

Run:
    python scripts\test_ordering.py
"""
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from project root or current dir
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    print("ERROR: RAZORPAY_WEBHOOK_SECRET is not set in environment or .env file", file=sys.stderr)
    sys.exit(1)

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def send(event_id: str, event_type: str, extra_payload: dict = {}) -> None:
    payload = {
        "entity": "event",
        "event": event_type,
        "created_at": int(time.time()),
        **extra_payload,
    }

    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    resp = requests.post(
        f"{BASE_URL}/webhooks/razorpay",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": event_id,
        },
        timeout=10,
    )
    print(f"[{event_id}] {event_type} -> {resp.status_code} {resp.text}")


SETTLEMENT_PAYLOAD = {
    "payload": {
        "settlement": {
            "entity": {
                "id": "setl_order_test_001",
                "amount": 15000,
                "fees": 300,
                "tax": 54,
                "utr": "UTRORDER001",
                "status": "processed",
            }
        }
    }
}

# Step 1: settlement arrives before payment
send("evt_order_001", "settlement.processed", SETTLEMENT_PAYLOAD)

# Step 2: payment arrives after settlement (out of order)
send(
    "evt_order_002",
    "payment.captured",
    {"payload": {"payment": {"entity": {"id": "pay_order_test_001"}}}},
)

# Step 3: settlement duplicate — must be deduplicated
send("evt_order_001", "settlement.processed", SETTLEMENT_PAYLOAD)

print("\nExpected: no crash, no duplicate settlement, final state correct.")
print("Check DB: SELECT event_id, status, attempts FROM webhook_events;")
