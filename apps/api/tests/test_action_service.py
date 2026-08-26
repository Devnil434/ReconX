import pytest
from app.actions.dispatcher import ActionDispatcher
from app.actions.reconcile import ReconciliationAction
from app.actions.refund import RefundAction
from app.core.action_types import ActionType


@pytest.mark.asyncio
async def test_action_dispatcher_reconciliation():
    dispatcher = ActionDispatcher()
    result = await dispatcher.dispatch(
        action_type=ActionType.MARK_RECONCILED.value,
        action_id="ACT-12345",
        payload={"case_id": "CASE-101"},
    )
    assert result["action_id"] == "ACT-12345"
    assert result["status"] == "completed"
    assert result["operation"] == "mark_reconciled"
    assert result["case_id"] == "CASE-101"


@pytest.mark.asyncio
async def test_action_dispatcher_refund():
    dispatcher = ActionDispatcher()
    result = await dispatcher.dispatch(
        action_type=ActionType.CREATE_REFUND.value,
        action_id="ACT-67890",
        payload={"payment_id": "pay_test_999", "amount": 50000},
    )
    assert result["action_id"] == "ACT-67890"
    assert result["status"] == "submitted"
    assert "refund" in result
    assert result["refund"]["amount"] == 50000



@pytest.mark.asyncio
async def test_action_dispatcher_unsupported():
    dispatcher = ActionDispatcher()
    with pytest.raises(ValueError):
        await dispatcher.dispatch(
            action_type="unsupported_custom_action",
            action_id="ACT-00000",
            payload={},
        )
