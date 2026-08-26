import random


SCENARIOS = [
    "normal",
    "fee_tax_difference",
    "missing_settlement",
    "missing_bank_credit",
    "duplicate_settlement",
    "partial_settlement",
    "refund_mismatch",
    "unknown_difference",
]


def choose_scenario() -> str:
    value = random.random()

    if value < 0.90:
        return "normal"
    if value < 0.93:
        return "fee_tax_difference"
    if value < 0.945:
        return "missing_settlement"
    if value < 0.955:
        return "missing_bank_credit"
    if value < 0.963:
        return "duplicate_settlement"
    if value < 0.968:
        return "partial_settlement"
    if value < 0.973:
        return "refund_mismatch"
    return "unknown_difference"


SCENARIO_GROUND_TRUTH = {
    "normal": {
        "expected_root_cause": "none",
        "expected_action": "NONE",
    },
    "fee_tax_difference": {
        "expected_root_cause": "fee_tax_difference",
        "expected_action": "AUTO_RESOLVE",
    },
    "missing_settlement": {
        "expected_root_cause": "missing_settlement",
        "expected_action": "HUMAN_REVIEW",
    },
    "missing_bank_credit": {
        "expected_root_cause": "missing_bank_credit",
        "expected_action": "HUMAN_REVIEW",
    },
    "duplicate_settlement": {
        "expected_root_cause": "duplicate_settlement",
        "expected_action": "BLOCK",
    },
    "partial_settlement": {
        "expected_root_cause": "partial_settlement",
        "expected_action": "HUMAN_REVIEW",
    },
    "refund_mismatch": {
        "expected_root_cause": "refund_mismatch",
        "expected_action": "HUMAN_REVIEW",
    },
    "unknown_difference": {
        "expected_root_cause": "unknown_difference",
        "expected_action": "HUMAN_REVIEW",
    },
}
