from types import SimpleNamespace

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
