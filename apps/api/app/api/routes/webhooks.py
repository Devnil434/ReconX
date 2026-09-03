import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
)
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.razorpay.webhooks import (
    verify_webhook_signature,
)
from app.models.webhook_event import WebhookEvent
from app.queue.config import reconciliation_queue
from app.queue.retry import DEFAULT_RETRY
from app.services.webhook_service import WebhookService

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


# ---------------------------------------------------------------------------
# Schema for the events list endpoint
# ---------------------------------------------------------------------------

class WebhookEventOut(BaseModel):
    event_id: str
    event_type: str
    status: str
    attempts: int
    created_at: datetime
    processed_at: Optional[datetime]

    model_config = {"from_attributes": True}

# ---------------------------------------------------------------------------
# Replay guard (§5.18)
# ---------------------------------------------------------------------------

_MAX_WEBHOOK_AGE_SECONDS = 300  # 5 minutes


def is_replay(created_at: int) -> bool:
    """
    Return True if the event timestamp is older than MAX_WEBHOOK_AGE_SECONDS.

    This is a defence-in-depth guard against replayed requests.
    Signature verification and event-ID deduplication are still the
    primary defences; this check is supplemental.
    """
    now = datetime.now(timezone.utc).timestamp()
    age = now - created_at
    return age > _MAX_WEBHOOK_AGE_SECONDS


# ---------------------------------------------------------------------------
# Endpoint (§5.6)
# ---------------------------------------------------------------------------


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    body = await request.body()

    # 0. Header presence checks
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing signature",
        )

    if not x_razorpay_event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing event ID",
        )

    # 1. Verify raw body signature
    if not verify_webhook_signature(body, x_razorpay_signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )

    # 2. Replay guard — reject stale events
    try:
        payload = json.loads(body)
        created_at = payload.get("created_at", 0)
        if created_at and is_replay(created_at):
            raise HTTPException(
                status_code=400,
                detail="Webhook too old",
            )
    except HTTPException:
        raise
    except Exception:
        # If we cannot parse the timestamp, skip the replay check
        # rather than rejecting a valid webhook.
        payload = {}

    service = WebhookService(db)

    # 3. Deduplicate by Razorpay event ID
    if service.already_processed(x_razorpay_event_id):
        return {
            "received": True,
            "duplicate": True,
        }

    event_type = payload.get("event", "unknown")

    # 4. Persist before enqueue (at-least-once guarantee)
    service.persist(
        event_id=x_razorpay_event_id,
        event_type=event_type,
        body=body,
        signature=x_razorpay_signature,
    )

    # 5. Enqueue heavy processing with retry (§5.12)
    reconciliation_queue.enqueue(
        "app.workers.webhook_worker.process_event",
        x_razorpay_event_id,
        retry=DEFAULT_RETRY,
    )

    # 6. Acknowledge immediately
    return {
        "received": True,
    }


# ---------------------------------------------------------------------------
# Read-only events list — used by the frontend test-payment pipeline tracker
# ---------------------------------------------------------------------------


@router.get("/events", response_model=List[WebhookEventOut])
def list_webhook_events(
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
) -> List[WebhookEventOut]:
    """
    Return the most recent webhook events ordered by creation time desc.

    This endpoint is intentionally unauthenticated (no Razorpay secrets
    are exposed) and is used only by the internal test-payment page to
    display live pipeline status.  Payload/signature columns are excluded.
    """
    rows = db.execute(
        select(WebhookEvent)
        .order_by(desc(WebhookEvent.created_at))
        .limit(limit)
    ).scalars().all()
    return [WebhookEventOut.model_validate(r) for r in rows]
