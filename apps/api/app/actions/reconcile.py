from typing import Any

from app.actions.base import ActionExecutor


class ReconciliationAction(ActionExecutor):

    async def execute(
        self,
        action_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "action_id": action_id,
            "status": "completed",
            "operation": "mark_reconciled",
            "case_id": payload.get("case_id"),
        }

