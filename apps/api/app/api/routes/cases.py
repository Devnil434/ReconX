from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exception import (
    ReconciliationException,
)
from app.models.investigation import (
    Investigation,
)
from app.models.policy_decision import (
    PolicyDecision,
)
from app.services.action_service import (
    ActionService,
)
from app.services.approval_service import (
    ApprovalService,
)
from app.services.policy_service import (
    PolicyService,
)

router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post("/{case_id}/approve")
def approve_case(
    case_id: str,
    reviewer: str,
    reason: str | None = None,
    db: Session = Depends(get_db),
):

    service = ApprovalService(db)

    approval = service.approve(
        case_id=case_id,
        reviewer=reviewer,
        reason=reason,
    )

    return {
        "case_id": case_id,
        "decision": approval.decision,
        "reviewer": approval.reviewer,
    }


@router.post("/{case_id}/reject")
def reject_case(
    case_id: str,
    reviewer: str,
    reason: str,
    db: Session = Depends(get_db),
):

    service = ApprovalService(db)

    approval = service.reject(
        case_id=case_id,
        reviewer=reviewer,
        reason=reason,
    )

    return {
        "case_id": case_id,
        "decision": approval.decision,
        "reviewer": approval.reviewer,
    }


@router.post("/{case_id}/resolve")
async def resolve_case(
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

    investigation = db.scalar(
        select(Investigation).where(
            Investigation.case_id
            == case_id
        )
    )

    if not investigation:
        raise HTTPException(
            status_code=409,
            detail=(
                "Case has not been investigated"
            ),
        )

    policy_service = PolicyService(db)

    policy = policy_service.evaluate(
        investigation,
        exception,
    )

    if not policy.allowed:

        return {
            "case_id": case_id,
            "status": "human_review",
            "action": policy.action,
            "reason": policy.reason,
        }

    action_service = ActionService(db)

    result = await action_service.execute(
        case_id=case_id,
        action_type=policy.action,
        payload={
            "case_id": case_id,
            "payment_id": (
                exception.payment_id
            ),
        },
    )

    exception.status = "resolved"

    db.commit()

    return {
        "case_id": case_id,
        "status": "resolved",
        "action": policy.action,
        "result": result,
    }
