import json
from datetime import datetime

from sqlalchemy import select

from app.models.webhook_event import (
    WebhookEvent,
)


class WebhookService:

    def __init__(self, db):
        self.db = db

    def already_processed(
        self,
        event_id: str,
    ) -> bool:

        event = self.db.scalar(
            select(WebhookEvent).where(
                WebhookEvent.event_id
                == event_id
            )
        )

        return event is not None

    def persist(
        self,
        event_id: str,
        event_type: str,
        body: bytes,
        signature: str,
    ):

        event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            payload=body.decode(
                "utf-8"
            ),
            signature=signature,
            status="received",
            created_at=datetime.utcnow(),
        )

        self.db.add(event)
        self.db.commit()

        return event