import json
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.razorpay.webhooks import (
    verify_webhook_signature,
)
from app.queue.config import reconciliation_queue
from app.queue.retry import DEFAULT_RETRY
from app.services.webhook_service import WebhookService

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

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
