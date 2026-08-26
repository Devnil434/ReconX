import hashlib
import hmac
import json
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def webhook_secret():
    secret = settings.razorpay_webhook_secret or "test_secret_for_webhook_suite"
    settings.razorpay_webhook_secret = secret
    return secret


def test_invalid_signature(client, webhook_secret):
    response = client.post(
        "/webhooks/razorpay",
        content=b'{"event":"payment.captured"}',
        headers={
            "X-Razorpay-Signature": "invalid_sig_here",
            "X-Razorpay-Event-Id": "evt_test_invalid_001",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"


def test_missing_signature(client):
    response = client.post(
        "/webhooks/razorpay",
        content=b'{"event":"payment.captured"}',
        headers={
            "X-Razorpay-Event-Id": "evt_test_missing_001",
        },
    )
    assert response.status_code == 400


def test_missing_event_id(client, webhook_secret):
    body = b'{"event":"payment.captured"}'
    sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    response = client.post(
        "/webhooks/razorpay",
        content=body,
        headers={
            "X-Razorpay-Signature": sig,
        },
    )
    assert response.status_code == 400


def test_duplicate_webhook(client, webhook_secret):
    payload = {
        "entity": "event",
        "event": "payment.captured",
        "created_at": int(__import__("time").time()),
        "payload": {"payment": {"entity": {"id": "pay_test_dup_001"}}},
    }
    body = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    event_id = f"evt_dup_test_{int(__import__('time').time() * 1000)}"

    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": sig,
        "X-Razorpay-Event-Id": event_id,
    }

    first = client.post("/webhooks/razorpay", content=body, headers=headers)
    assert first.status_code == 200
    assert first.json().get("received") is True

    second = client.post("/webhooks/razorpay", content=body, headers=headers)
    assert second.status_code == 200
    assert second.json().get("duplicate") is True
