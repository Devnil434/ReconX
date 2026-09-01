from types import SimpleNamespace
from app.ai.policies.policy_engine import PolicyEngine
from app.ai.policies.risk_engine import RiskEngine
from app.core.action_types import ActionType


def test_high_risk_case_blocks():
    policy_engine = PolicyEngine()
    
    high_risk_investigation = SimpleNamespace(
        confidence=0.65,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=["Suspicious bank discrepancy"],
    )
    exception = SimpleNamespace(difference=50000, severity="high")
    high_risk = SimpleNamespace(level="high")

    result = policy_engine.evaluate(
        investigation=high_risk_investigation,
        exception=exception,
        risk=high_risk,
    )

    assert result.allowed is False
    assert result.action == ActionType.BLOCK.value


def test_low_risk_auto_resolve():
    policy_engine = PolicyEngine()

    low_risk_investigation = SimpleNamespace(
        confidence=0.98,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=[],
    )
    exception = SimpleNamespace(difference=0, severity="low")
    low_risk = SimpleNamespace(level="low")

    result = policy_engine.evaluate(
        investigation=low_risk_investigation,
        exception=exception,
        risk=low_risk,
    )

    assert result.allowed is True
    assert result.action == ActionType.MARK_RECONCILED.value
