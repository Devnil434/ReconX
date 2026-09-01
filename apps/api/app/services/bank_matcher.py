from sqlalchemy import select

from app.models.bank_transaction import BankTransaction


class BankMatcher:
    """
    Matches Razorpay UTRs against imported bank statement transactions.

    A UTR match confirms that the funds from a settlement actually
    arrived in the bank account (BANK_CONFIRMED).  No match means the
    transfer was initiated by Razorpay but not yet visible in the bank
    statement (BANK_PENDING).
    """

    def __init__(self, db):
        self.db = db

    def match_utr(
        self,
        utr: str,
    ) -> BankTransaction | None:
        """Return the BankTransaction whose UTR matches, or None."""

        return self.db.scalar(
            select(BankTransaction).where(
                BankTransaction.utr == utr
            )
        )
