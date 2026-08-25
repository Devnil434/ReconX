from dataclasses import dataclass

from app.core.enums import MatchType


@dataclass
class ReconciliationDecision:
    status: str
    match_type: str
    expected_amount: int
    actual_amount: int
    difference: int
    reason_codes: list[str]


class ReconciliationEngine:

    def reconcile(
        self,
        payment,
        settlements,
        bank_transactions,
    ) -> ReconciliationDecision:

        expected = (
            payment.amount
            - payment.fee
            - payment.tax
        )

        # --------------------------------
        # CASE 1: No settlement
        # --------------------------------

        if not settlements:

            return ReconciliationDecision(
                status="exception",
                match_type=MatchType.NO_SETTLEMENT.value,
                expected_amount=expected,
                actual_amount=0,
                difference=expected,
                reason_codes=[
                    "MISSING_SETTLEMENT"
                ],
            )

        # --------------------------------
        # CASE 2: Multiple settlements
        # --------------------------------

        settlement_total = sum(
            settlement.amount
            for settlement in settlements
        )

        # --------------------------------
        # CASE 3: No bank credit
        # --------------------------------

        if not bank_transactions:

            return ReconciliationDecision(
                status="exception",
                match_type=MatchType.NO_BANK_CREDIT.value,
                expected_amount=settlement_total,
                actual_amount=0,
                difference=settlement_total,
                reason_codes=[
                    "MISSING_BANK_CREDIT"
                ],
            )

        # --------------------------------
        # CASE 4: Bank credit
        # --------------------------------

        bank_total = sum(
            transaction.amount
            for transaction in bank_transactions
        )

        difference = (
            expected
            - bank_total
        )

        # --------------------------------
        # CASE 5: Exact match
        # --------------------------------

        if difference == 0:

            if len(settlements) > 1:

                return ReconciliationDecision(
                    status="matched",
                    match_type=(
                        MatchType.PARTIAL_SETTLEMENT.value
                    ),
                    expected_amount=expected,
                    actual_amount=bank_total,
                    difference=0,
                    reason_codes=[
                        "MULTIPLE_SETTLEMENTS",
                        "FULL_AMOUNT_RECONCILED",
                    ],
                )

            return ReconciliationDecision(
                status="matched",
                match_type=MatchType.EXACT_AMOUNT.value,
                expected_amount=expected,
                actual_amount=bank_total,
                difference=0,
                reason_codes=[
                    "EXACT_MATCH"
                ],
            )

        # --------------------------------
        # CASE 6: Mismatch
        # --------------------------------

        return ReconciliationDecision(
            status="exception",
            match_type=MatchType.FEE_ADJUSTED.value,
            expected_amount=expected,
            actual_amount=bank_total,
            difference=difference,
            reason_codes=[
                "AMOUNT_MISMATCH"
            ],
        )