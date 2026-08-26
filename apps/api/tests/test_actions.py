import pytest
from unittest.mock import MagicMock
from app.actions.dispatcher import ActionDispatcher
from app.actions.refund import RefundAction
from app.core.action_types import ActionType
from app.services.action_verifier import ActionVerifier


@pytest.mark.asyncio
async def test_action_dispatcher_dispatch():
    dispatcher = ActionDispatcher()
    result = await dispatcher.dispatch(
        action_type=ActionType.MARK_RECONCILED.value,
        action_id="ACT-TST-001",
        payload={"case_id": "CASE-TEST-1"},
    )
    assert result["action_id"] == "ACT-TST-001"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_refund_action_execution():
    action = RefundAction()
    result = await action.execute(
        action_id="ACT-REF-001",
        payload={"payment_id": "pay_test_123", "amount": 2500},
    )
    assert result["action_id"] == "ACT-REF-001"
    assert result["status"] == "submitted"
    assert result["refund"]["amount"] == 2500


def test_action_verifier():
    mock_client = MagicMock()
    mock_client.fetch_refund.return_value = {"id": "rfnd_123", "status": "processed"}
    
    verifier = ActionVerifier(mock_client)
    res = verifier.verify_refund("rfnd_123")
    
    assert res["verified"] is True
    assert res["status"] == "processed"
