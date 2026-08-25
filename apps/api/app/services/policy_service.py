import json
from datetime import datetime

from app.ai.policies.policy_engine import (
    PolicyEngine,
    PolicyResult,
)
from app.ai.policies.risk_engine import (
    RiskEngine,
    RiskAssessment,
)
from app.models.policy_decision import (
    PolicyDecision,
)


def is_safe_to_auto_resolve(
    investigation,
) -> bool:

    return (
        getattr(investigation, "confidence", 0.0) >= 0.95
        and getattr(investigation, "recommendation", "") == "AUTO_RESOLVE"
        and len(getattr(investigation, "unresolved_questions", [])) == 0
    )


class PolicyService:

    def __init__(self, db=None):

        self.db = db

        self.risk_engine = RiskEngine()
        self.policy_engine = PolicyEngine()

    def evaluate(
        self,
        investigation,
        exception,
    ) -> PolicyResult:

        risk = self.risk_engine.assess(
            investigation,
            exception,
        )

        policy = self.policy_engine.evaluate(
            investigation,
            exception,
            risk,
        )

        if self.db:
            case_id = getattr(exception, "case_id", getattr(investigation, "case_id", "CASE-UNKNOWN"))
            confidence = getattr(investigation, "confidence", 0.0)
            decision = PolicyDecision(
                case_id=case_id,
                ai_confidence=confidence,
                risk_score=risk.score,
                action=policy.action,
                allowed=policy.allowed,
                reason=(
                    policy.reason
                    + " | Risk: "
                    + json.dumps(risk.reasons)
                ),
                created_at=datetime.utcnow(),
            )

            self.db.add(decision)
            self.db.commit()

        return policy

    def decide(
        self,
        investigation,
    ) -> str:
        """Compatibility helper for older simple checks."""
        confidence = getattr(investigation, "confidence", 0.0)
        recommendation = getattr(investigation, "recommendation", "HUMAN_REVIEW")

        if (
            recommendation == "AUTO_RESOLVE"
            and confidence >= 0.95
            and is_safe_to_auto_resolve(investigation)
        ):
            return "AUTO_RESOLVE"

        if confidence >= 0.75:
            return "HUMAN_REVIEW"

        return "BLOCK"