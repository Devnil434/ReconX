from datetime import datetime

from app.models.approval import Approval
from app.models.exception import (
    ReconciliationException,
)


class ApprovalService:

    def __init__(self, db):

        self.db = db

    def approve(
        self,
        case_id: str,
        reviewer: str,
        reason: str | None = None,
    ):

        approval = Approval(
            case_id=case_id,
            decision="approved",
            reviewer=reviewer,
            reason=reason,
            created_at=datetime.utcnow(),
        )

        self.db.add(approval)

        self.db.commit()

        return approval

    def reject(
        self,
        case_id: str,
        reviewer: str,
        reason: str,
    ):

        approval = Approval(
            case_id=case_id,
            decision="rejected",
            reviewer=reviewer,
            reason=reason,
            created_at=datetime.utcnow(),
        )

        self.db.add(approval)

        self.db.commit()

        return approval
