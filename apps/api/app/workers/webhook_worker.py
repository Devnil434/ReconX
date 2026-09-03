"""
webhook_worker.py

RQ worker entry point.  Receives a webhook event_id, fetches the
persisted WebhookEvent, dispatches to the correct domain worker by
event_type, and updates the status field on the row.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.states import WebhookStatus
from app.models.webhook_event import WebhookEvent


_DISPATCH: dict = {}

try:
    from app.workers.settlement_worker import process_settlement_event
    _DISPATCH["settlement.processed"] = process_settlement_event
except ImportError:
    pass

try:
    from app.workers.payment_worker import (
        process_payment_captured,
        process_payment_authorized,
    )
    _DISPATCH["payment.captured"] = process_payment_captured
    _DISPATCH["payment.authorized"] = process_payment_authorized
except ImportError:
    pass


def process_event(event_id: str) -> dict:
    """
    Called by the RQ worker.  Updates status and routes to domain worker.
    """
    db: Session = SessionLocal()
    try:
        event = db.scalar(
            select(WebhookEvent).where(
                WebhookEvent.event_id == event_id
            )
        )

        if event is None:
            return {"error": f"event {event_id!r} not found"}

        event.status = WebhookStatus.PROCESSING.value
        event.attempts = (event.attempts or 0) + 1
        db.commit()

        try:
            import json as _json
            payload = _json.loads(event.payload)
            handler = _DISPATCH.get(event.event_type)
            if handler:
                result = handler(payload)
            else:
                result = {"skipped": True, "reason": "no handler"}

            event.status = WebhookStatus.SUCCEEDED.value
            event.processed_at = datetime.utcnow()
            db.commit()

            return result

        except Exception as exc:
            event.status = WebhookStatus.FAILED.value
            db.commit()
            raise exc

    finally:
        db.close()
