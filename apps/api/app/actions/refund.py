from typing import Any

from app.actions.base import ActionExecutor


class RefundAction(ActionExecutor):

    async def execute(
        self,
        action_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "action_id": action_id,
            "status": "simulated",
            "operation": "create_refund",
            "payment_id": payload.get("payment_id"),
            "amount": payload.get("amount"),
        }
