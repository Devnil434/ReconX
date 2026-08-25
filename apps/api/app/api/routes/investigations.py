import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.investigators.investigator import (
    AIInvestigator,
)
from app.db.session import get_db
from app.models.bank_transaction import (
    BankTransaction,
)
from app.models.exception import (
    ReconciliationException,
)
from app.models.investigation import (
    Investigation,
)
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.settlement import Settlement

router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


@router.get("")
def list_investigations(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    exceptions = list(
        db.scalars(
            select(ReconciliationException)
            .order_by(ReconciliationException.created_at.desc())
            .limit(limit)
        ).all()
    )

    results = []
    for exc in exceptions:
        inv = db.scalar(
            select(Investigation).where(Investigation.case_id == exc.case_id)
        )
        results.append({
            "case_id": exc.case_id,
            "payment_id": exc.payment_id,
            "exception_type": exc.exception_type,
            "severity": exc.severity,
            "expected_amount": exc.expected_amount,
            "actual_amount": exc.actual_amount,
            "difference": exc.difference,
            "status": inv.status if inv else exc.status,
            "recommendation": inv.recommendation if inv else None,
            "confidence": inv.confidence if inv else None,
            "root_cause": inv.root_cause if inv else None,
            "created_at": exc.created_at.isoformat() if exc.created_at else None,
        })

    return results


@router.post("/{case_id}/run")
async def run_investigation(
    case_id: str,
    db: Session = Depends(get_db),
):

    exception = db.scalar(
        select(
            ReconciliationException
        ).where(
            ReconciliationException.case_id
            == case_id
        )
    )

    if not exception:

        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    payment = db.scalar(
        select(Payment).where(
            Payment.razorpay_payment_id
            == exception.payment_id
        )
    )

    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    settlements = list(
        db.scalars(
            select(Settlement).where(
                Settlement.payment_id
                == exception.payment_id
            )
        ).all()
    )

    bank_transactions = []

    for settlement in settlements:

        bank_transactions.extend(
            db.scalars(
                select(
                    BankTransaction
                ).where(
                    BankTransaction.utr
                    == settlement.utr
                )
            ).all()
        )

    refunds = list(
        db.scalars(
            select(Refund).where(
                Refund.payment_id
                == exception.payment_id
            )
        ).all()
    )

    investigator = AIInvestigator(db)

    result = await investigator.investigate(
        exception=exception,
        payment=payment,
        settlements=settlements,
        bank_transactions=(
            bank_transactions
        ),
        refunds=refunds,
    )

    return result.model_dump()


@router.get("/{case_id}")
def get_investigation(
    case_id: str,
    db: Session = Depends(get_db),
):

    investigation = db.scalar(
        select(Investigation).where(
            Investigation.case_id
            == case_id
        )
    )

    if not investigation:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return {
        "case_id": investigation.case_id,
        "status": investigation.status,
        "root_cause": investigation.root_cause,
        "confidence": investigation.confidence,
        "recommendation": (
            investigation.recommendation
        ),
        "summary": investigation.summary,
        "evidence": json.loads(
            investigation.evidence_json
            or "[]"
        ),
        "hypotheses": json.loads(
            investigation.hypotheses_json
            or "[]"
        ),
    }
