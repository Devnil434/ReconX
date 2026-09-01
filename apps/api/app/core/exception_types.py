from enum import Enum


class ExceptionType(str, Enum):
    """
    Standardized classification of payment reconciliation exceptions.

    AI CAN AUTO-RESOLVE:
    - FEE_TAX_DIFFERENCE: Fee/tax schedule adjustment with clear mathematical evidence.

    AI REFUSES TO AUTO-RESOLVE (Requires Human Review / Escalation):
    - MISSING_SETTLEMENT: Payment captured on gateway but no settlement batch recorded.
    - MISSING_BANK_CREDIT: Settlement processed by gateway but UTR not found in bank statement.
    - DUPLICATE_SETTLEMENT: Multiple settlements claiming the same payment ID.
    - PARTIAL_SETTLEMENT: Incomplete payout with outstanding balance.
    - REFUND_MISMATCH: Gateway refund record does not match debit transaction.
    - UNKNOWN_DIFFERENCE: Unexplained discrepancy lacking deterministic evidence.
    - CONFLICTING_EVIDENCE: Conflicting ledger timestamps or mismatched amounts.
    """

    FEE_TAX_DIFFERENCE = "fee_tax_difference"
    MISSING_SETTLEMENT = "missing_settlement"
    MISSING_BANK_CREDIT = "missing_bank_credit"
    DUPLICATE_SETTLEMENT = "duplicate_settlement"
    PARTIAL_SETTLEMENT = "partial_settlement"
    REFUND_MISMATCH = "refund_mismatch"
    UNKNOWN_DIFFERENCE = "unknown_difference"
    CONFLICTING_EVIDENCE = "conflicting_evidence"


# Explicit policy boundaries for automated resolution
AUTO_RESOLVABLE_EXCEPTIONS = {
    ExceptionType.FEE_TAX_DIFFERENCE,
}

MANUAL_REVIEW_EXCEPTIONS = {
    ExceptionType.MISSING_SETTLEMENT,
    ExceptionType.MISSING_BANK_CREDIT,
    ExceptionType.PARTIAL_SETTLEMENT,
    ExceptionType.REFUND_MISMATCH,
    ExceptionType.UNKNOWN_DIFFERENCE,
    ExceptionType.CONFLICTING_EVIDENCE,
}

BLOCKED_EXCEPTIONS = {
    ExceptionType.DUPLICATE_SETTLEMENT,
}
