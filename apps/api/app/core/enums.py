from enum import Enum


class ReconciliationStatus(str, Enum):
    MATCHED = "matched"
    EXCEPTION = "exception"
    PENDING = "pending"


class ExceptionType(str, Enum):
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_SETTLEMENT = "missing_settlement"
    MISSING_BANK_CREDIT = "missing_bank_credit"
    DUPLICATE_PAYMENT = "duplicate_payment"
    DUPLICATE_SETTLEMENT = "duplicate_settlement"
    REFUND_MISMATCH = "refund_mismatch"
    PARTIAL_SETTLEMENT = "partial_settlement"
    TIMING_ANOMALY = "timing_anomaly"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


class InvestigationDecision(str, Enum):
    AUTO_RESOLVE = "auto_resolve"
    HUMAN_REVIEW = "human_review"
    BLOCK = "block"


class InvestigationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"