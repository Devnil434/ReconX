from datetime import datetime

from sqlalchemy.orm import Session

from app.models.exception import (
    ReconciliationException,
)
from app.models.reconciliation import (
    ReconciliationResult,
)
from app.services.reconciliation_engine import (
    ReconciliationEngine,
)
from app.utils.ids import generate_case_id


class ReconciliationService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.engine = (
            ReconciliationEngine()
        )

    def reconcile_payment(
        self,
        payment,
        settlements,
        bank_transactions,
    ):

        decision = self.engine.reconcile(
            payment=payment,
            settlements=settlements,
            bank_transactions=bank_transactions,
        )

        result = ReconciliationResult(
            payment_id=(
                payment.razorpay_payment_id
            ),
            settlement_id=(
                settlements[0]
                .razorpay_settlement_id
                if settlements
                else None
            ),
            bank_transaction_id=(
                bank_transactions[0].id
                if bank_transactions
                else None
            ),
            status=decision.status,
            match_type=decision.match_type,
            expected_amount=(
                decision.expected_amount
            ),
            actual_amount=(
                decision.actual_amount
            ),
            difference=(
                decision.difference
            ),
            reason_codes=",".join(
                decision.reason_codes
            ),
            created_at=datetime.utcnow(),
        )

        self.db.add(result)

        if decision.status == "exception":

            exception = ReconciliationException(
                case_id=generate_case_id(),
                payment_id=payment.razorpay_payment_id,
                exception_type=(
                    decision.reason_codes[0].lower()
                ),
                severity="medium",
                expected_amount=(
                    decision.expected_amount
                ),
                actual_amount=(
                    decision.actual_amount
                ),
                difference=(
                    decision.difference
                ),
                status="open",
                reason=", ".join(
                    decision.reason_codes
                ),
                created_at=datetime.utcnow(),
            )

            self.db.add(exception)

        self.db.commit()
        self.db.refresh(result)

        return result