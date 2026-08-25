from dataclasses import dataclass


@dataclass
class UTRMatch:
    matched: bool
    settlement_count: int
    bank_transaction_count: int
    reason: str


class UTRMatcher:

    def match(
        self,
        settlements,
        bank_transactions,
    ) -> UTRMatch:

        settlement_utrs = {
            settlement.utr
            for settlement in settlements
            if settlement.utr
        }

        bank_utrs = {
            transaction.utr
            for transaction in bank_transactions
            if transaction.utr
        }

        common = (
            settlement_utrs
            & bank_utrs
        )

        if common:
            return UTRMatch(
                matched=True,
                settlement_count=len(
                    settlements
                ),
                bank_transaction_count=len(
                    bank_transactions
                ),
                reason="UTR_MATCH",
            )

        return UTRMatch(
            matched=False,
            settlement_count=len(
                settlements
            ),
            bank_transaction_count=len(
                bank_transactions
            ),
            reason="UTR_NOT_FOUND",
        )