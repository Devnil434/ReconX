from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bank_transaction import (
    BankTransaction,
)


class BankRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_utr(
        self,
        utr: str,
    ) -> list[BankTransaction]:

        return list(
            self.db.scalars(
                select(BankTransaction).where(
                    BankTransaction.utr == utr
                )
            ).all()
        )

    def list_all(self) -> list[BankTransaction]:

        return list(
            self.db.scalars(
                select(BankTransaction)
            ).all()
        )