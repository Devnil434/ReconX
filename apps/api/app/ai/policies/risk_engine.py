from dataclasses import dataclass


@dataclass
class RiskAssessment:
    score: float
    level: str
    reasons: list[str]


class RiskEngine:

    def assess(
        self,
        investigation,
        exception,
    ) -> RiskAssessment:

        score = 0.0
        reasons = []

        # Low confidence = risk
        confidence = getattr(investigation, "confidence", 0.0)
        if confidence < 0.80:
            score += 0.40
            reasons.append(
                "LOW_AI_CONFIDENCE"
            )

        elif confidence < 0.95:
            score += 0.15
            reasons.append(
                "MEDIUM_AI_CONFIDENCE"
            )

        # Financial discrepancy
        difference = getattr(exception, "difference", 0)
        if difference != 0:
            score += 0.15
            reasons.append(
                "NON_ZERO_DIFFERENCE"
            )

        # High severity
        severity = getattr(exception, "severity", "medium")
        if severity == "high":
            score += 0.25
            reasons.append(
                "HIGH_SEVERITY"
            )

        # Critical unknowns
        unresolved_questions = getattr(
            investigation, "unresolved_questions", []
        )
        if unresolved_questions:
            score += 0.25
            reasons.append(
                "UNRESOLVED_QUESTIONS"
            )

        if score >= 0.60:
            level = "high"

        elif score >= 0.30:
            level = "medium"

        else:
            level = "low"

        return RiskAssessment(
            score=min(score, 1.0),
            level=level,
            reasons=reasons,
        )
