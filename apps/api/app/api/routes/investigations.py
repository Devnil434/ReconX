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
