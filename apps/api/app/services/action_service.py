import json
import uuid
from datetime import datetime

from sqlalchemy import select

from app.actions.dispatcher import (
    ActionDispatcher,
)
from app.models.action import Action


class ActionService:

    def __init__(self, db):

        self.db = db
        self.dispatcher = (
            ActionDispatcher()
        )

    async def execute(
        self,
        case_id: str,
        action_type: str,
        payload: dict,
    ):

        action_id = (
            f"ACT-{uuid.uuid4().hex}"
        )

        existing = self.db.scalar(
            select(Action).where(
                Action.case_id == case_id,
                Action.action_type
                == action_type,
                Action.status
                == "completed",
            )
        )

        if existing:

            return {
                "action_id": existing.action_id,
                "status": "already_completed",
            }

        action = Action(
            case_id=case_id,
            action_id=action_id,
            action_type=action_type,
            status="executing",
            request_json=json.dumps(
                payload
            ),
            created_at=datetime.utcnow(),
        )

        self.db.add(action)
        self.db.commit()

        try:

            result = (
                await self.dispatcher.dispatch(
                    action_type,
                    action_id,
                    payload,
                )
            )

            action.status = "completed"

            action.response_json = (
                json.dumps(result)
            )

            action.completed_at = (
                datetime.utcnow()
            )

            self.db.commit()

            return result

        except Exception as exc:

            action.status = "failed"
            action.error = str(exc)

            self.db.commit()

            raise
