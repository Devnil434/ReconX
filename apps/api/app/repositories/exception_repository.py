from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exception import (
    ReconciliationException,
)


class ExceptionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_case_id(
        self,
        case_id: str,
    ):

        return self.db.scalar(
            select(
                ReconciliationException
            ).where(
                ReconciliationException.case_id
                == case_id
            )
        )

    def list_open(self):

        return list(
            self.db.scalars(
                select(
                    ReconciliationException
                ).where(
                    ReconciliationException.status
                    == "open"
                )
            ).all()
        )
