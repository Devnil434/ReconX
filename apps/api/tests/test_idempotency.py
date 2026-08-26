import pytest
from unittest.mock import MagicMock
from app.models.action import Action
from app.services.action_service import ActionService


@pytest.mark.asyncio
async def test_action_is_idempotent():
    db = MagicMock()
    # Mock existing completed action
    existing_action = Action(
        case_id="CASE-001",
        action_id="ACT-EXISTING-001",
        action_type="mark_reconciled",
        status="completed",
        request_json='{"case_id": "CASE-001"}',
    )
    db.scalar.return_value = existing_action

    service = ActionService(db)
    result = await service.execute(
        case_id="CASE-001",
        action_type="mark_reconciled",
        payload={"case_id": "CASE-001"},
    )

    assert result["status"] == "already_completed"
    assert result["action_id"] == "ACT-EXISTING-001"

