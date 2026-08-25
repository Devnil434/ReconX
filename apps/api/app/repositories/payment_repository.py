from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        payment_id: str,
    ) -> Payment | None:

        return self.db.scalar(
            select(Payment).where(
                Payment.razorpay_payment_id
                == payment_id
            )
        )

    def list_all(self) -> list[Payment]:

        return list(
            self.db.scalars(
                select(Payment)
            ).all()
        )