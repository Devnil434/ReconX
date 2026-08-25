from collections import Counter


class DuplicateDetector:

    def duplicate_utrs(
        self,
        settlements,
    ) -> set[str]:

        counts = Counter(
            settlement.utr
            for settlement in settlements
        )

        return {
            utr
            for utr, count in counts.items()
            if count > 1
        }

    def duplicate_bank_references(
        self,
        bank_transactions,
    ) -> set[str]:

        counts = Counter(
            transaction.bank_reference
            for transaction in bank_transactions
        )

        return {
            reference
            for reference, count in counts.items()
            if count > 1
        }