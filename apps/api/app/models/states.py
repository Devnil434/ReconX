from enum import Enum


class WebhookStatus(str, Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    RETRYING = "retrying"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class ActionStatus(str, Enum):
    PLANNED = "planned"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    SUBMITTED = "submitted"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class SettlementState(str, Enum):
    CREATED = "created"
    PROCESSED = "processed"
    BANK_PENDING = "bank_pending"
    BANK_CONFIRMED = "bank_confirmed"
    RECONCILED = "reconciled"
    EXCEPTION = "exception"
