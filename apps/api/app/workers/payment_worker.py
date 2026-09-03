"""
payment_worker.py

Handles Razorpay payment.captured and payment.authorized webhook events.

Pipeline:
  1. Parse payment entity from Razorpay webhook payload
  2. Upsert Payment row (idempotent)
  3. Fetch linked settlements + bank transactions
  4. Run ReconciliationService → creates ReconciliationResult + optional Exception
  5. If exception created → enqueue AI investigation job
  6. Emit structured logs at each step (no secrets logged)
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.bank_transaction import BankTransaction
from app.models.exception import ReconciliationException
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.queue.config import investigation_queue
from app.queue.retry import DEFAULT_RETRY
from app.services.reconciliation_service import ReconciliationService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry points (registered in webhook_worker._DISPATCH)
# ---------------------------------------------------------------------------


def process_payment_captured(payload: dict) -> dict:
    """Handler for event_type=payment.captured"""
    return _process_payment_event(payload, expected_status="captured")


def process_payment_authorized(payload: dict) -> dict:
    """Handler for event_type=payment.authorized"""
    return _process_payment_event(payload, expected_status="authorized")


# ---------------------------------------------------------------------------
# Internal implementation
# ---------------------------------------------------------------------------


def _extract_payment_entity(payload: dict) -> dict:
    """Pull the payment entity from a Razorpay webhook payload dict."""
    return (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )


def _process_payment_event(payload: dict, expected_status: str) -> dict:
    entity = _extract_payment_entity(payload)
    payment_id = entity.get("id")

    if not payment_id:
        logger.error("payment_worker: missing payment id in payload")
        return {"error": "missing payment id"}

    logger.info(
        "payment_worker: received",
        extra={
            "payment_id": payment_id,
            "expected_status": expected_status,
            "amount": entity.get("amount"),
            "currency": entity.get("currency", "INR"),
        },
    )

    db: Session = SessionLocal()
    try:
        return _upsert_and_reconcile(db, entity, expected_status)
    finally:
        db.close()


def _upsert_and_reconcile(db: Session, entity: dict, expected_status: str) -> dict:
    payment_id: str = entity["id"]
    amount: int = entity.get("amount", 0)
    currency: str = entity.get("currency", "INR")
    # Payment Button payments have no server-side order; use sentinel
    order_id: str = entity.get("order_id") or "button_flow"
    status: str = entity.get("status", expected_status)
    fee: int = entity.get("fee") or 0
    tax: int = entity.get("tax") or 0
    created_ts = entity.get("created_at")
    created_at = (
        datetime.utcfromtimestamp(created_ts)
        if created_ts
        else datetime.utcnow()
    )

    # ── 1. Upsert payment row (idempotent) ───────────────────────
    existing = db.scalar(
        select(Payment).where(Payment.razorpay_payment_id == payment_id)
    )

    if existing:
        existing.status = status
        existing.fee = fee
        existing.tax = tax
        if status == "captured" and existing.captured_at is None:
            existing.captured_at = datetime.utcnow()
        payment = existing
        logger.info(
            "payment_worker: payment upserted (existing row)",
            extra={"payment_id": payment_id, "status": status},
        )
    else:
        payment = Payment(
            razorpay_payment_id=payment_id,
            order_id=order_id,
            amount=amount,
            currency=currency,
            status=status,
            fee=fee,
            tax=tax,
            created_at=created_at,
            captured_at=datetime.utcnow() if status == "captured" else None,
        )
        db.add(payment)
        logger.info(
            "payment_worker: payment created",
            extra={"payment_id": payment_id, "amount": amount, "status": status},
        )

    db.commit()
    db.refresh(payment)

    # ── 2. Fetch settlements for this payment ────────────────────
    settlements = list(
        db.scalars(
            select(Settlement).where(Settlement.payment_id == payment_id)
        ).all()
    )

    # ── 3. Fetch bank transactions via UTR ───────────────────────
    bank_transactions: list = []
    for s in settlements:
        if s.utr:
            bank_transactions.extend(
                db.scalars(
                    select(BankTransaction).where(
                        BankTransaction.utr == s.utr
                    )
                ).all()
            )

    logger.info(
        "payment_worker: reconciliation input ready",
        extra={
            "payment_id": payment_id,
            "settlements_count": len(settlements),
            "bank_transactions_count": len(bank_transactions),
        },
    )

    # ── 4. Reconcile ─────────────────────────────────────────────
    svc = ReconciliationService(db)
    result = svc.reconcile_payment(
        payment=payment,
        settlements=settlements,
        bank_transactions=bank_transactions,
    )

    logger.info(
        "payment_worker: reconciliation_complete",
        extra={
            "payment_id": payment_id,
            "reconciliation_status": result.status,
            "match_type": result.match_type,
            "difference": result.difference,
        },
    )

    # ── 5. Enqueue investigation if exception created ────────────
    if result.status == "exception":
        exc = db.scalar(
            select(ReconciliationException).where(
                ReconciliationException.payment_id == payment_id
            )
        )
        if exc:
            investigation_queue.enqueue(
                "app.workers.investigation_worker.investigate_case",
                exc.case_id,
                retry=DEFAULT_RETRY,
            )
            logger.info(
                "payment_worker: investigation_enqueued",
                extra={"case_id": exc.case_id, "payment_id": payment_id},
            )

    return {
        "payment_id": payment_id,
        "reconciliation_status": result.status,
        "match_type": result.match_type,
        "difference": result.difference,
    }
