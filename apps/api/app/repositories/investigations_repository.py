from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investigation import (
    Investigation,
)


class InvestigationRepository:

    def __init__(self, db: Session):
        self.db = db

    def similar_root_causes(
        self,
        root_cause: str,
        limit: int = 5,
    ):

        return list(
            self.db.scalars(
                select(Investigation)
                .where(
                    Investigation.root_cause
                    == root_cause
                )
                .limit(limit)
            ).all()
        )