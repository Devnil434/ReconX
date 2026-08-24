import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT / "scripts"),
)

from generator.anomalies.allocator import allocate_cases
from generator.anomalies.config import ANOMALY_DISTRIBUTION
from generator.anomalies.apply import apply_anomalies
from generator.utils.ids import seed_ids

from generator.generator.payments import generate_payments
from generator.generator.settlements import generate_settlements
from generator.generator.bank import generate_bank_transactions
from generator.generator.refunds import generate_refunds

from generator.utils.csv import write_csv
from generator.utils.output import write_json


def main():
    seed = 42
    count = 1000

    seed_ids(seed)

    print(
        f"Generating {count} synthetic payments..."
    )

    payments = generate_payments(
        count=count,
        seed=seed,
    )

    settlements = generate_settlements(
        payments
    )

    bank_transactions = (
        generate_bank_transactions(
            settlements
        )
    )

    refunds = generate_refunds(
        payments,
        seed=seed,
    )

    cases = allocate_cases(
        [
            payment.razorpay_payment_id
            for payment in payments
        ],
        ANOMALY_DISTRIBUTION,
    )

    ground_truth = apply_anomalies(
        payments=payments,
        settlements=settlements,
        bank_transactions=bank_transactions,
        refunds=refunds,
        cases=cases,
    )

    print("\nAllocated anomaly cases:")

    for anomaly_type, ids in cases.items():
        print(
            f"  {anomaly_type}: {len(ids)}"
        )

    write_csv(
        payments,
        ROOT / "data/raw/payments.csv",
    )

    write_csv(
        settlements,
        ROOT / "data/raw/settlements.csv",
    )

    write_csv(
        bank_transactions,
        ROOT / "data/raw/bank_transactions.csv",
    )

    write_csv(
        refunds,
        ROOT / "data/raw/refunds.csv",
    )

    write_json(
        {
            "dataset_size": count,
            "seed": seed,
            "cases": ground_truth,
        },
        ROOT / "data/ground_truth/ground_truth.json",
    )

    write_json(
        {
            "dataset_size": count,
            "seed": seed,
            "anomaly_distribution": {
                k: v
                for k, v in cases.items()
            },
        },
        ROOT / "data/ground_truth/allocation.json",
    )

    print("\nDataset generated successfully.")


if __name__ == "__main__":
    main()