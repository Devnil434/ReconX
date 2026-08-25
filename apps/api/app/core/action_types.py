from enum import Enum


class ActionType(str, Enum):
    NOOP = "noop"
    MARK_RECONCILED = "mark_reconciled"
    CREATE_REFUND = "create_refund"
    REQUEST_REVIEW = "request_review"
    BLOCK = "block"
    BLOCK_CASE = "block_case"
    REFETCH_TRANSACTION = "refetch_transaction"
