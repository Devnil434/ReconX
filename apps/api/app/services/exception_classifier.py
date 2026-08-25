from dataclasses import dataclass


@dataclass
class ExceptionClassification:
    exception_type: str
    severity: str
    reason: str


class ExceptionClassifier:

    def classify(
        self,
        decision,
        has_duplicate: bool = False,
        is_late: bool = False,
    ) -> ExceptionClassification:

        if has_duplicate:

            return ExceptionClassification(
                exception_type="duplicate",
                severity="high",
                reason=(
                    "Duplicate financial reference detected."
                ),
            )

        if (
            decision.match_type
            == "no_settlement"
        ):

            return ExceptionClassification(
                exception_type="missing_settlement",
                severity="high",
                reason=(
                    "Captured payment has no "
                    "corresponding settlement."
                ),
            )

        if (
            decision.match_type
            == "no_bank_credit"
        ):

            return ExceptionClassification(
                exception_type="missing_bank_credit",
                severity="high",
                reason=(
                    "Settlement exists but "
                    "corresponding bank credit is absent."
                ),
            )

        if is_late:

            return ExceptionClassification(
                exception_type="timing_anomaly",
                severity="medium",
                reason=(
                    "Settlement occurred outside "
                    "the configured timing window."
                ),
            )

        if decision.difference != 0:

            return ExceptionClassification(
                exception_type="amount_mismatch",
                severity="medium",
                reason=(
                    "Expected and observed amounts differ."
                ),
            )

        return ExceptionClassification(
            exception_type="unknown",
            severity="low",
            reason="No known exception pattern.",
        )