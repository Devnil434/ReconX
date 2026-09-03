"""
Unit and integration tests for Razorpay Test Mode webhooks, workers, and reconciliation pipeline.
"""
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, Integer, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app
from app.models.exception import ReconciliationException
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.models.webhook_event import WebhookEvent
from app.workers.payment_worker import (
    process_payment_authorized,
    process_payment_captured,
)
from app.workers.webhook_worker import process_event

# ---------------------------------------------------------------------------
# Test Database Setup (In-Memory SQLite with BigInteger PK compatibility)
# ---------------------------------------------------------------------------
TEST_SECRET = "test_webhook_secret_key_123"
settings.razorpay_webhook_secret = TEST_SECRET
settings.razorpay_key_id = "rzp_test_TUHiDLDs9QGDld"
settings.razorpay_key_secret = "test_key_secret"

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Convert BigInteger PKs to Integer for SQLite autoincrement compatibility
for table in Base.metadata.tables.values():
    for col in table.columns:
        if col.primary_key and isinstance(col.type, BigInteger):
            col.type = Integer()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def compute_signature(body: bytes, secret: str = TEST_SECRET) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------------
# Tests 1-6: Webhook Endpoint, Signatures & Idempotency
# ---------------------------------------------------------------------------


def test_valid_webhook_signature_and_enqueue():
    """1. Valid webhook receives 200 and enqueues background processing."""
    payload = {
        "event": "payment.captured",
        "created_at": int(time.time()),
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_001",
                    "amount": 50000,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }
    body = json.dumps(payload).encode("utf-8")
    sig = compute_signature(body)

    with patch("app.api.routes.webhooks.reconciliation_queue.enqueue") as mock_enqueue:
        resp = client.post(
            "/webhooks/razorpay",
            content=body,
            headers={
                "x-razorpay-signature": sig,
                "x-razorpay-event-id": "evt_test_001",
            },
        )
        assert resp.status_code == 200
        assert resp.json() == {"received": True}
        assert mock_enqueue.called


def test_invalid_webhook_signature():
    """2. Invalid signature returns 401."""
    body = b'{"event":"payment.captured"}'
    resp = client.post(
        "/webhooks/razorpay",
        content=body,
        headers={
            "x-razorpay-signature": "bad_signature_hex",
            "x-razorpay-event-id": "evt_test_002",
        },
    )
    assert resp.status_code == 401
    assert "Invalid signature" in resp.json()["detail"]


def test_missing_signature_and_missing_event_id():
    """3. Missing signature returns 400. Missing event ID returns 400."""
    body = b'{"event":"payment.captured"}'
    resp1 = client.post(
        "/webhooks/razorpay",
        content=body,
        headers={"x-razorpay-event-id": "evt_test_003"},
    )
    assert resp1.status_code == 400

    sig = compute_signature(body)
    resp2 = client.post(
        "/webhooks/razorpay",
        content=body,
        headers={"x-razorpay-signature": sig},
    )
    assert resp2.status_code == 400


def test_duplicate_event_id_idempotency():
    """4 & 5. Duplicate event returns duplicate flag and does not re-persist."""
    payload = {
        "event": "payment.captured",
        "created_at": int(time.time()),
        "payload": {"payment": {"entity": {"id": "pay_test_004"}}},
    }
    body = json.dumps(payload).encode("utf-8")
    sig = compute_signature(body)

    with patch("app.api.routes.webhooks.reconciliation_queue.enqueue") as mock_enqueue:
        # First attempt
        r1 = client.post(
            "/webhooks/razorpay",
            content=body,
            headers={
                "x-razorpay-signature": sig,
                "x-razorpay-event-id": "evt_dup_001",
            },
        )
        assert r1.status_code == 200
        assert r1.json() == {"received": True}
        assert mock_enqueue.call_count == 1

        # Second attempt with same event ID
        r2 = client.post(
            "/webhooks/razorpay",
            content=body,
            headers={
                "x-razorpay-signature": sig,
                "x-razorpay-event-id": "evt_dup_001",
            },
        )
        assert r2.status_code == 200
        assert r2.json() == {"received": True, "duplicate": True}
        assert mock_enqueue.call_count == 1  # Not re-enqueued


def test_stale_replayed_webhook_rejection():
    """6. Webhooks older than 5 minutes are rejected by the replay guard."""
    payload = {
        "event": "payment.captured",
        "created_at": int(time.time()) - 600,  # 10 minutes ago
    }
    body = json.dumps(payload).encode("utf-8")
    sig = compute_signature(body)

    resp = client.post(
        "/webhooks/razorpay",
        content=body,
        headers={
            "x-razorpay-signature": sig,
            "x-razorpay-event-id": "evt_old_001",
        },
    )
    assert resp.status_code == 400
    assert "Webhook too old" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Tests 7-10: Payment Worker & Webhook Worker Dispatch
# ---------------------------------------------------------------------------


def test_payment_captured_worker_processing():
    """7. payment.captured worker processes event, creates Payment row, and reconciles."""
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_worker_001",
                    "amount": 10000,
                    "currency": "INR",
                    "status": "captured",
                    "fee": 200,
                    "tax": 36,
                }
            }
        },
    }

    with patch("app.workers.payment_worker.SessionLocal", TestingSessionLocal), \
         patch("app.workers.payment_worker.investigation_queue.enqueue") as mock_inv_queue:
        res = process_payment_captured(payload)
        assert res["payment_id"] == "pay_worker_001"
        assert res["reconciliation_status"] == "exception"  # Missing settlement initially

        # Verify Payment row was stored
        db = TestingSessionLocal()
        payment = db.query(Payment).filter(Payment.razorpay_payment_id == "pay_worker_001").first()
        assert payment is not None
        assert payment.amount == 10000
        assert payment.fee == 200
        db.close()


def test_payment_authorized_worker_processing():
    """8. payment.authorized worker updates payment status to authorized."""
    payload = {
        "event": "payment.authorized",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_auth_001",
                    "amount": 25000,
                    "currency": "INR",
                    "status": "authorized",
                }
            }
        },
    }

    with patch("app.workers.payment_worker.SessionLocal", TestingSessionLocal):
        res = process_payment_authorized(payload)
        assert res["payment_id"] == "pay_auth_001"

        db = TestingSessionLocal()
        payment = db.query(Payment).filter(Payment.razorpay_payment_id == "pay_auth_001").first()
        assert payment is not None
        assert payment.status == "authorized"
        db.close()


def test_webhook_worker_dispatch_and_unhandled_event():
    """9 & 10. Webhook worker routes known events and safely skips unknown events."""
    db = TestingSessionLocal()
    evt = WebhookEvent(
        event_id="evt_unknown_99",
        event_type="unknown.event.type",
        payload=json.dumps({"event": "unknown.event.type"}),
        signature="dummy_sig",
        status="received",
        created_at=datetime.now(timezone.utc),
    )
    db.add(evt)
    db.commit()
    db.close()

    with patch("app.workers.webhook_worker.SessionLocal", TestingSessionLocal):
        result = process_event("evt_unknown_99")
        assert result.get("skipped") is True

        db = TestingSessionLocal()
        updated_evt = db.query(WebhookEvent).filter(WebhookEvent.event_id == "evt_unknown_99").first()
        assert updated_evt.status == "succeeded"
        db.close()


# ---------------------------------------------------------------------------
# Tests 11-14: Reconciliation, AI Failure & Policy Decision
# ---------------------------------------------------------------------------


def test_reconciliation_exact_match():
    """11. Exact match when payment amount minus fees equals settlement amount."""
    from app.services.reconciliation_engine import ReconciliationEngine

    engine_svc = ReconciliationEngine()
    
    mock_payment = MagicMock(amount=10000, fee=200, tax=36)
    mock_settlement = MagicMock(amount=9764)
    mock_bank = MagicMock(amount=9764)

    decision = engine_svc.reconcile(
        payment=mock_payment,
        settlements=[mock_settlement],
        bank_transactions=[mock_bank],
    )
    assert decision.status == "matched"
    assert decision.difference == 0
    assert "EXACT_MATCH" in decision.reason_codes


def test_investigation_ai_failure_fallback():
    """12 & 13. When AI investigator raises an error, fallback safely sets HUMAN_REVIEW."""
    from app.workers.investigation_worker import investigate_case

    db = TestingSessionLocal()
    exc = ReconciliationException(
        case_id="CASE-FAIL-01",
        payment_id="pay_fail_01",
        exception_type="missing_settlement",
        severity="medium",
        expected_amount=5000,
        actual_amount=0,
        difference=5000,
        status="open",
        created_at=datetime.now(timezone.utc),
    )
    payment = Payment(
        razorpay_payment_id="pay_fail_01",
        order_id="btn_1",
        amount=5000,
        currency="INR",
        status="captured",
        created_at=datetime.now(timezone.utc),
    )
    db.add_all([exc, payment])
    db.commit()
    db.close()

    with patch("app.workers.investigation_worker.SessionLocal", TestingSessionLocal), \
         patch("app.ai.investigators.investigator.AIInvestigator.investigate", side_effect=Exception("AI connection timeout")):
        result = investigate_case("CASE-FAIL-01")
        assert result["status"] == "human_review"

        db = TestingSessionLocal()
        updated_exc = db.query(ReconciliationException).filter(ReconciliationException.case_id == "CASE-FAIL-01").first()
        assert updated_exc.status == "human_review"
        db.close()


def test_policy_engine_hard_block_on_high_risk():
    """14. Policy engine blocks autonomous action when risk level is high."""
    from app.ai.policies.policy_engine import PolicyEngine
    from app.ai.policies.risk_engine import RiskAssessment

    engine_policy = PolicyEngine()
    investigation = MagicMock(confidence=0.98, recommendation="AUTO_RESOLVE", unresolved_questions=[])
    exception = MagicMock(difference=0, severity="high")
    high_risk = RiskAssessment(score=0.85, level="high", reasons=["CRITICAL_VARIANCE"])

    policy_res = engine_policy.evaluate(investigation, exception, high_risk)
    assert policy_res.allowed is False
    assert policy_res.action == "block"


# ---------------------------------------------------------------------------
# Tests 15-16: Create Order API & Webhook Events Listing API
# ---------------------------------------------------------------------------


def test_create_order_endpoint():
    """15. POST /api/payments/create-order returns order details with public key."""
    with patch("app.api.routes.payments._rzp.create_order", return_value={"id": "order_test_123", "amount": 10000, "currency": "INR"}):
        resp = client.post(
            "/api/payments/create-order",
            json={"amount_paise": 10000, "name": "Nilan", "email": "test@reconx.dev"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["order_id"] == "order_test_123"
        assert data["key_id"] == "rzp_test_TUHiDLDs9QGDld"
        assert "secret" not in data


def test_list_webhook_events_endpoint():
    """16. GET /webhooks/events returns persisted events list."""
    db = TestingSessionLocal()
    evt = WebhookEvent(
        event_id="evt_list_01",
        event_type="payment.captured",
        payload=json.dumps({"event": "payment.captured"}),
        signature="sig1",
        status="succeeded",
        created_at=datetime.now(timezone.utc),
    )
    db.add(evt)
    db.commit()
    db.close()

    resp = client.get("/webhooks/events?limit=5")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert items[0]["event_id"] == "evt_list_01"
    assert "payload" not in items[0]  # No raw payload exposure
