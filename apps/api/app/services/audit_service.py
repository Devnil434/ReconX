import json
import uuid
from datetime import datetime

from app.models.audit_event import (
    AuditEvent,
)


class AuditService:

    def __init__(self, db):
        self.db = db

    def record(
        self,
        case_id: str,
        event_type: str,
        actor: str,
        payload: dict,
    ):

        event = AuditEvent(
            event_id=(
                f"AUD-{uuid.uuid4().hex}"
            ),
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            payload=json.dumps(
                payload
            ),
            created_at=datetime.utcnow(),
        )

        self.db.add(event)
        self.db.commit()

        return event
