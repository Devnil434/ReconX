import json
import random
from pathlib import Path

# Action mapping based on financial risk policies
CASE_SPEC = {
    "fee_tax_difference": {
        "expected_root_cause": "fee_tax_difference",
        "expected_action": "AUTO_RESOLVE",
        "severity": "low",
    },
    "missing_bank_credit": {
        "expected_root_cause": "missing_bank_credit",
        "expected_action": "HUMAN_REVIEW",
        "severity": "high",
    },
    "duplicate_settlement": {
        "expected_root_cause": "duplicate_settlement",
        "expected_action": "BLOCK",
        "severity": "critical",
    },
    "partial_settlement": {
        "expected_root_cause": "partial_settlement",
        "expected_action": "HUMAN_REVIEW",
        "severity": "medium",
    },
    "unknown_difference": {
        "expected_root_cause": "unknown_difference",
        "expected_action": "HUMAN_REVIEW",
        "severity": "high",
    },
}

cases = []
expected = []

case_types = list(CASE_SPEC.keys())

for i in range(100):
    case_type = random.choice(case_types)
    spec = CASE_SPEC[case_type]
    case_id = f"EVAL-{i:04d}"

    case_obj = {
        "case_id": case_id,
        "type": case_type,
        "severity": spec["severity"],
        "expected_root_cause": spec["expected_root_cause"],
        "expected_action": spec["expected_action"],
    }
    cases.append(case_obj)
    expected.append({
        "case_id": case_id,
        "expected_root_cause": spec["expected_root_cause"],
        "expected_action": spec["expected_action"],
    })

# Save to local and root data directories
for target_dir in [Path("data/evaluation"), Path("../../data/evaluation")]:
    target_dir.mkdir(parents=True, exist_ok=True)
    with open(target_dir / "cases.json", "w") as f:
        json.dump(cases, f, indent=2)
    with open(target_dir / "expected.json", "w") as f:
        json.dump(expected, f, indent=2)

print(f"Generated 100 synthetic evaluation cases in data/evaluation/cases.json and expected.json")
