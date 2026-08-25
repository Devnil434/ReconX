from enum import Enum


class CaseStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    INVESTIGATED = "investigated"
    POLICY_EVALUATED = "policy_evaluated"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    BLOCKED = "blocked"
    FAILED = "failed"
