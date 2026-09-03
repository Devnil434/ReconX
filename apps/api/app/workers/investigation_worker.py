"""
investigation_worker.py

RQ worker: runs AI investigation + policy evaluation for a reconciliation case.

Design principles:
  - Receives case_id from the investigation queue
  - Fetches all related data from PostgreSQL
  - Wraps async AIInvestigator.investigate() with asyncio.run()
  - AI failure → sets HUMAN_REVIEW + records AI_FAILURE audit event
  - Policy engine always runs after AI (never bypassed)
  - No autonomous financial action taken here — only investigation + decision
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
from app.models.refund import Refund
from app.models.settlement import Settlement

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point (enqueued by payment_worker)
# ---------------------------------------------------------------------------


def investigate_case(case_id: str) -> dict:
    """
    Entry point for the RQ investigation queue.
    Synchronous wrapper — asyncio.run() handles the async investigator.
    """
    logger.info("investigation_worker: started", extra={"case_id": case_id})

    db: Session = SessionLocal()
    try:
        return _run(db, case_id)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Internal implementation
# ---------------------------------------------------------------------------


def _run(db: Session, case_id: str) -> dict:
    # ── Fetch exception ──────────────────────────────────────────
    exception = db.scalar(
        select(ReconciliationException).where(
            ReconciliationException.case_id == case_id
        )
    )
    if exception is None:
        logger.error(
            "investigation_worker: case not found",
            extra={"case_id": case_id},
        )
        return {"error": f"case {case_id!r} not found"}

    # ── Fetch payment ────────────────────────────────────────────
    payment = None
    if exception.payment_id:
        payment = db.scalar(
            select(Payment).where(
                Payment.razorpay_payment_id == exception.payment_id
            )
        )

    if payment is None:
        logger.warning(
            "investigation_worker: payment not found — fallback HUMAN_REVIEW",
            extra={"case_id": case_id},
        )
        _set_human_review(db, exception, "Payment record not found")
        return {
            "case_id": case_id,
            "status": "human_review",
            "reason": "payment_not_found",
        }

    # ── Fetch settlements ────────────────────────────────────────
    settlements = list(
        db.scalars(
            select(Settlement).where(
                Settlement.payment_id == exception.payment_id
            )
        ).all()
    )

    # ── Fetch bank transactions ──────────────────────────────────
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

    # ── Fetch refunds ────────────────────────────────────────────
    refunds = list(
        db.scalars(
            select(Refund).where(
                Refund.payment_id == exception.payment_id
            )
        ).all()
    )

    logger.info(
        "investigation_worker: evidence gathered",
        extra={
            "case_id": case_id,
            "payment_id": exception.payment_id,
            "settlements": len(settlements),
            "bank_transactions": len(bank_transactions),
            "refunds": len(refunds),
        },
    )

    # ── Run AI investigation ─────────────────────────────────────
    try:
        from app.ai.investigators.investigator import AIInvestigator

        investigator = AIInvestigator(db)
        result = asyncio.run(
            investigator.investigate(
                exception=exception,
                payment=payment,
                settlements=settlements,
                bank_transactions=bank_transactions,
                refunds=refunds,
            )
        )

        logger.info(
            "investigation_worker: AI_complete",
            extra={
                "case_id": case_id,
                "confidence": getattr(result, "confidence", None),
                "recommendation": getattr(result, "recommendation", None),
                "root_cause": getattr(result, "root_cause", None),
            },
        )

        # ── Policy evaluation — always runs after AI ─────────────
        from app.services.policy_service import PolicyService

        policy_svc = PolicyService(db)
        policy = policy_svc.evaluate(result, exception)

        logger.info(
            "investigation_worker: policy_decision",
            extra={
                "case_id": case_id,
                "action": policy.action,
                "allowed": policy.allowed,
                "reason": policy.reason,
            },
        )

        return {
            "case_id": case_id,
            "recommendation": getattr(result, "recommendation", None),
            "confidence": getattr(result, "confidence", None),
            "policy_action": policy.action,
            "policy_allowed": policy.allowed,
        }

    except Exception as exc:
        # AI provider unavailable or raised — safe fallback
        logger.error(
            "investigation_worker: AI_failure",
            extra={"case_id": case_id, "error": str(exc)},
        )
        _set_human_review(db, exception, str(exc))
        return {
            "case_id": case_id,
            "status": "human_review",
            "reason": "ai_failure",
        }


def _set_human_review(
    db: Session,
    exception: ReconciliationException,
    reason: str,
) -> None:
    """Record AI_FAILURE audit event and set case to HUMAN_REVIEW."""
    try:
        from app.services.audit_service import AuditService

        AuditService(db).record(
            case_id=exception.case_id,
            event_type="AI_FAILURE",
            actor="system",
            payload={"reason": reason},
        )
    except Exception:
        pass  # audit must not break the safe fallback

    exception.status = "human_review"
    try:
        db.commit()
    except Exception:
        db.rollback()
