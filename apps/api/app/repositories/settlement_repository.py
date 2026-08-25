from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settlement import Settlement


class SettlementRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_payment_id(
        self,
        payment_id: str,
    ) -> list[Settlement]:

        return list(
            self.db.scalars(
                select(Settlement).where(
                    Settlement.payment_id
                    == payment_id
                )
            ).all()
        )

    def get_by_utr(
        self,
        utr: str,
    ) -> list[Settlement]:

        return list(
            self.db.scalars(
                select(Settlement).where(
                    Settlement.utr == utr
                )
            ).all()
        )