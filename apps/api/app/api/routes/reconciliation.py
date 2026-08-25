import time
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reconciliation import (
    ReconciliationResult,
)
from app.repositories.bank_repository import (
    BankRepository,
)
from app.repositories.payment_repository import (
    PaymentRepository,
)
from app.repositories.settlement_repository import (
    SettlementRepository,
)
from app.services.reconciliation_service import (
    ReconciliationService,
)

router = APIRouter(
    prefix="/reconciliation",
    tags=["Reconciliation"],
)


@router.post(
    "/payments/{payment_id}"
)
def reconcile_payment(
    payment_id: str,
    db: Session = Depends(get_db),
):

    payment_repo = PaymentRepository(db)
    settlement_repo = SettlementRepository(db)
    bank_repo = BankRepository(db)

    payment = (
        payment_repo.get_by_id(
            payment_id
        )
    )

    if not payment:
        return {
            "error": "Payment not found"
        }

    settlements = (
        settlement_repo.get_by_payment_id(
            payment_id
        )
    )

    bank_transactions = []

    for settlement in settlements:

        bank_transactions.extend(
            bank_repo.get_by_utr(
                settlement.utr
            )
        )

    service = ReconciliationService(db)

    result = service.reconcile_payment(
        payment,
        settlements,
        bank_transactions,
    )

    return {
        "id": result.id,
        "payment_id": result.payment_id,
        "status": result.status,
        "match_type": result.match_type,
        "expected_amount": (
            result.expected_amount
        ),
        "actual_amount": (
            result.actual_amount
        ),
        "difference": result.difference,
        "reason_codes": (
            result.reason_codes
        ),
    }


@router.post("/run")
def run_reconciliation(
    db: Session = Depends(get_db),
):
    payment_repo = PaymentRepository(db)
    settlement_repo = SettlementRepository(db)
    bank_repo = BankRepository(db)
    service = ReconciliationService(db)

    payments = payment_repo.list_all()
    results = []

    start = time.perf_counter()

    for payment in payments:
        settlements = (
            settlement_repo.get_by_payment_id(
                payment.razorpay_payment_id
            )
        )

        bank_transactions = []
        for settlement in settlements:
            bank_transactions.extend(
                bank_repo.get_by_utr(
                    settlement.utr
                )
            )

        result = service.reconcile_payment(
            payment,
            settlements,
            bank_transactions,
        )
        results.append(result)

    elapsed = time.perf_counter() - start

    matched = sum(
        1 for result in results if result.status == "matched"
    )
    exceptions = len(results) - matched

    return {
        "total": len(results),
        "matched": matched,
        "exceptions": exceptions,
        "match_rate": (
            matched / len(results) if results else 0
        ),
        "elapsed_seconds": round(
            elapsed, 4
        ),
        "transactions_per_second": (
            round(len(results) / elapsed, 2) if elapsed > 0 else 0
        ),
    }


@router.get("/summary")
def reconciliation_summary(
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(
            func.count(
                ReconciliationResult.id
            )
        )
    ) or 0

    matched = db.scalar(
        select(
            func.count(
                ReconciliationResult.id
            )
        ).where(
            ReconciliationResult.status == "matched"
        )
    ) or 0

    exceptions = (
        total - matched
    )

    return {
        "total": total,
        "matched": matched,
        "exceptions": exceptions,
        "match_rate": (
            matched / total if total else 0
        ),
    }