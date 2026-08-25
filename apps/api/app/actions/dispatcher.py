from typing import Any

from app.core.action_types import ActionType
from app.actions.reconcile import (
    ReconciliationAction,
)
from app.actions.refund import (
    RefundAction,
)


class ActionDispatcher:

    def __init__(self):

        self.reconciliation = (
            ReconciliationAction()
        )

        self.refund = RefundAction()

    async def dispatch(
        self,
        action_type: str,
        action_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        if (
            action_type
            == ActionType.MARK_RECONCILED.value
        ):

            return await (
                self.reconciliation.execute(
                    action_id,
                    payload,
                )
            )

        if (
            action_type
            == ActionType.CREATE_REFUND.value
        ):

            return await (
                self.refund.execute(
                    action_id,
                    payload,
                )
            )

        raise ValueError(
            f"Unsupported action: "
            f"{action_type}"
        )
