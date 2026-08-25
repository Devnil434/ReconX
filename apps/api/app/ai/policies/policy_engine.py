from dataclasses import dataclass

from app.core.action_types import ActionType


@dataclass
class PolicyResult:
    action: str
    allowed: bool
    reason: str


class PolicyEngine:

    def evaluate(
        self,
        investigation,
        exception,
        risk,
    ) -> PolicyResult:

        # --------------------------------
        # HARD BLOCKS
        # --------------------------------

        if risk.level == "high":

            return PolicyResult(
                action=ActionType.BLOCK.value,
                allowed=False,
                reason=(
                    "Risk exceeds autonomous "
                    "execution threshold."
                ),
            )

        confidence = getattr(investigation, "confidence", 0.0)
        if confidence < 0.95:

            return PolicyResult(
                action=(
                    ActionType.REQUEST_REVIEW.value
                ),
                allowed=False,
                reason=(
                    "AI confidence below "
                    "autonomous threshold."
                ),
            )

        unresolved_questions = getattr(
            investigation, "unresolved_questions", []
        )
        if unresolved_questions:

            return PolicyResult(
                action=(
                    ActionType.REQUEST_REVIEW.value
                ),
                allowed=False,
                reason=(
                    "Investigation contains "
                    "unresolved questions."
                ),
            )

        # --------------------------------
        # SAFE AUTO-RESOLUTION
        # --------------------------------

        recommendation = getattr(
            investigation, "recommendation", ""
        )
        difference = getattr(
            exception, "difference", 0
        )

        if (
            recommendation == "AUTO_RESOLVE"
            and difference == 0
            and risk.level == "low"
        ):

            return PolicyResult(
                action=(
                    ActionType.MARK_RECONCILED.value
                ),
                allowed=True,
                reason=(
                    "Evidence is complete and "
                    "financial state is balanced."
                ),
            )

        # --------------------------------
        # DEFAULT
        # --------------------------------

        return PolicyResult(
            action=(
                ActionType.REQUEST_REVIEW.value
            ),
            allowed=False,
            reason=(
                "Case requires human review."
            ),
        )
