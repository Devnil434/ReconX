from app.core.enums import InvestigationDecision


SAFE_AUTO_RESOLUTION_CAUSES = {
    "fee_difference",
    "tax_difference",
    "exact_partial_settlement",
}


def is_safe_to_auto_resolve(
    investigation,
) -> bool:

    return (
        investigation.confidence >= 0.95
        and investigation.recommendation == "AUTO_RESOLVE"
        and len(getattr(investigation, "unresolved_questions", [])) == 0
    )


class PolicyService:

    def decide(
        self,
        investigation,
    ) -> str:

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