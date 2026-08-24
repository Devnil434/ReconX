from app.core.enums import InvestigationDecision


SAFE_AUTO_RESOLUTION_CAUSES = {
    "fee_difference",
    "tax_difference",
    "exact_partial_settlement",
}


class PolicyService:

    def decide(
        self,
        root_cause: str,
        confidence: float,
    ) -> InvestigationDecision:

        if (
            confidence >= 0.95
            and root_cause in SAFE_AUTO_RESOLUTION_CAUSES
        ):
            return InvestigationDecision.AUTO_RESOLVE

        if confidence >= 0.75:
            return InvestigationDecision.HUMAN_REVIEW

        return InvestigationDecision.BLOCK