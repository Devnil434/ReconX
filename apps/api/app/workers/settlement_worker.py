"""
settlement_worker.py

Processes Razorpay settlement.processed webhook payloads.

Design principles:
- Idempotent: safe to call multiple times for the same settlement_id
- Out-of-order safe: does not assume any prior event arrived first
- BANK_CONFIRMED only when we have a matching UTR in the bank statement;
  BANK_PENDING otherwise (settlement.processed != bank credit)
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.settlement import Settlement
from app.models.states import SettlementState
from app.services.bank_matcher import BankMatcher


def process_settlement_event(payload: dict) -> dict:
    """
    Entry point called by the RQ worker.

    payload shape (Razorpay webhook):
        {
            "entity": "event",
            "event": "settlement.processed",
            "payload": {
                "settlement": {
                    "entity": { ... }
                }
            }
        }
    """
    entity = (
        payload.get("payload", {})
        .get("settlement", {})
        .get("entity", {})
    )

    settlement_id = entity.get("id")
    amount = entity.get("amount", 0)
    fees = entity.get("fees", 0)
    tax = entity.get("tax", 0)
    utr = entity.get("utr")
    status = entity.get("status", "processed")

    if not settlement_id:
        return {"error": "missing settlement id"}

    db: Session = SessionLocal()
    try:
        return _upsert_settlement(
            db=db,
            settlement_id=settlement_id,
            amount=amount,
            fees=fees,
            tax=tax,
            utr=utr,
            razorpay_status=status,
        )
    finally:
        db.close()


def _upsert_settlement(
    db: Session,
    settlement_id: str,
    amount: int,
    fees: int,
    tax: int,
    utr: str | None,
    razorpay_status: str,
) -> dict:
    existing = db.scalar(
        select(Settlement).where(
            Settlement.razorpay_settlement_id == settlement_id
        )
    )

    if existing:
        # Out-of-order: already have this settlement — just re-evaluate state
        settlement = existing
    else:
        settlement = Settlement(
            razorpay_settlement_id=settlement_id,
            amount=amount,
            fee=fees,
            tax=tax,
            utr=utr or "",
            status=SettlementState.PROCESSED.value,
            settlement_date=datetime.utcnow(),
        )
        db.add(settlement)

    # Determine bank confirmation state via UTR matching
    if utr:
        matcher = BankMatcher(db)
        bank_tx = matcher.match_utr(utr)
        settlement.status = (
            SettlementState.BANK_CONFIRMED.value
            if bank_tx
            else SettlementState.BANK_PENDING.value
        )
    else:
        settlement.status = SettlementState.BANK_PENDING.value

    db.commit()
    db.refresh(settlement)

    return {
        "settlement_id": settlement_id,
        "state": settlement.status,
        "utr_matched": settlement.status == SettlementState.BANK_CONFIRMED.value,
    }
