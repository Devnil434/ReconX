import json
import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_scenarios import choose_scenario, SCENARIO_GROUND_TRUTH


def generate_transaction(index: int) -> dict:
    amount = random.randint(1000, 500000)
    fee = int(amount * 0.02)
    tax = int(fee * 0.18)
    expected = amount - fee - tax
    scenario = choose_scenario()

    return {
        'payment_id': 'pay_test_' + uuid.uuid4().hex[:16],
        'amount': amount,
        'fee': fee,
        'tax': tax,
        'expected_settlement': expected,
        'index': index,
        'scenario': scenario,
    }


def generate(count: int) -> None:
    transactions = [generate_transaction(i) for i in range(count)]

    ground_truth = [
        {
            'case_id': 'EVAL-%05d' % tx['index'],
            'payment_id': tx['payment_id'],
            'scenario': tx['scenario'],
            'expected_root_cause': SCENARIO_GROUND_TRUTH[tx['scenario']]['expected_root_cause'],
            'expected_action': SCENARIO_GROUND_TRUTH[tx['scenario']]['expected_action'],
        }
        for tx in transactions
    ]

    for base_dir in [Path('data/benchmark'), Path('../../data/benchmark')]:
        base_dir.mkdir(parents=True, exist_ok=True)
        (base_dir / 'transactions.json').write_text(json.dumps(transactions, indent=2))
        (base_dir / 'ground_truth.json').write_text(json.dumps(ground_truth, indent=2))

    print('Generated %d synthetic transactions and ground truth.' % count)


if __name__ == '__main__':
    generate(100000)
