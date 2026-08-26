from typing import Any

from app.actions.base import ActionExecutor
from app.integrations.razorpay.client import RazorpayClient


class RefundAction(ActionExecutor):

    def __init__(self):
        self.client = RazorpayClient()

    async def execute(
        self,
        action_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        payment_id = payload.get("payment_id")
        amount = payload.get("amount")

        if not payment_id or not amount:
            return {
                "action_id": action_id,
                "status": "failed",
                "reason": "missing payment_id or amount",
            }

        # Must reuse the same idempotency key on any retry.
        # Razorpay deduplicates based on this.
        idempotency_key = f"refund-{action_id}"

        result = self.client.create_refund(
            payment_id=payment_id,
            amount=amount,
            idempotency_key=idempotency_key,
        )

        return {
            "action_id": action_id,
            "status": "submitted",
            "refund": result,
        }
