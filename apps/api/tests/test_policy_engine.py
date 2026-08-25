from types import SimpleNamespace

from app.ai.policies.policy_engine import PolicyEngine
from app.ai.policies.risk_engine import RiskEngine
from app.core.action_types import ActionType
from app.services.policy_service import PolicyService, is_safe_to_auto_resolve


def test_safe_auto_resolve():
    policy = PolicyService()
    inv = SimpleNamespace(
        confidence=0.98,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=[],
    )
    assert is_safe_to_auto_resolve(inv) is True
    assert policy.decide(inv) == "AUTO_RESOLVE"


def test_unsafe_auto_resolve_due_to_unresolved_questions():
    policy = PolicyService()
    inv = SimpleNamespace(
        confidence=0.98,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=["Missing bank statement file."],
    )
    assert is_safe_to_auto_resolve(inv) is False
    assert policy.decide(inv) == "HUMAN_REVIEW"


def test_human_review_medium_confidence():
    policy = PolicyService()
    inv = SimpleNamespace(
        confidence=0.82,
        recommendation="HUMAN_REVIEW",
        unresolved_questions=[],
    )
    assert policy.decide(inv) == "HUMAN_REVIEW"


def test_block_low_confidence():
    policy = PolicyService()
    inv = SimpleNamespace(
        confidence=0.60,
        recommendation="BLOCK",
        unresolved_questions=["Ambiguous transaction source."],
    )
    assert policy.decide(inv) == "BLOCK"


def test_risk_and_policy_engine_evaluation():
    risk_engine = RiskEngine()
    policy_engine = PolicyEngine()

    inv_safe = SimpleNamespace(
        confidence=0.98,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=[],
    )
    exc_safe = SimpleNamespace(difference=0, severity="low")

    risk = risk_engine.assess(inv_safe, exc_safe)
    assert risk.level == "low"

    result = policy_engine.evaluate(inv_safe, exc_safe, risk)
    assert result.allowed is True
    assert result.action == ActionType.MARK_RECONCILED.value


def test_policy_engine_blocks_high_risk():
    risk_engine = RiskEngine()
    policy_engine = PolicyEngine()

    inv_risky = SimpleNamespace(
        confidence=0.70,
        recommendation="AUTO_RESOLVE",
        unresolved_questions=["Duplicate UTR found"],
    )
    exc_risky = SimpleNamespace(difference=15000, severity="high")

    risk = risk_engine.assess(inv_risky, exc_risky)
    assert risk.level == "high"

    result = policy_engine.evaluate(inv_risky, exc_risky, risk)
    assert result.allowed is False
    assert result.action == ActionType.BLOCK.value
