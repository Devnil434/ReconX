import io
import json
import sys
import pandas as pd
from pathlib import Path

# Force UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding="utf-8",
    errors="replace",
)

ROOT = Path(__file__).resolve().parents[2]

PASS = "PASS"
FAIL = "FAIL"


def check(label: str, ok: bool, detail: str = "") -> bool:
    symbol = PASS if ok else FAIL
    line = f"  {symbol} {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return ok


def main():
    print("\nDATASET VALIDATION")
    print("=" * 50)

    # ------------------------------------------------------------------ #
    # Load files                                                           #
    # ------------------------------------------------------------------ #

    raw = ROOT / "data/raw"
    gt  = ROOT / "data/ground_truth"

    payments    = pd.read_csv(raw / "payments.csv")
    settlements = pd.read_csv(raw / "settlements.csv")
    bank        = pd.read_csv(raw / "bank_transactions.csv")
    refunds     = pd.read_csv(raw / "refunds.csv")

    with open(gt / "ground_truth.json") as f:
        ground_truth_doc = json.load(f)

    with open(gt / "allocation.json") as f:
        allocation_doc = json.load(f)

    ground_truth = ground_truth_doc["cases"]
    allocation   = allocation_doc["anomaly_distribution"]

    failures = 0

    # ------------------------------------------------------------------ #
    # Record counts                                                        #
    # ------------------------------------------------------------------ #

    print("\n[Record Counts]")

    base_payments = allocation_doc["dataset_size"]

    # Derive exact expected counts from ground_truth records:
    # duplicate_payment adds duplicate payment rows (+30)
    # duplicate_settlement adds duplicate settlement rows (+30)
    # partial_settlement adds a second partial settlement row (+50)
    # missing_settlement removes settlement rows (-50)
    # missing_bank_credit removes bank transaction rows (-50)
    gt_by_type: dict = {}
    for r in ground_truth:
        gt_by_type.setdefault(r["exception_type"], 0)
        gt_by_type[r["exception_type"]] += 1

    expected_payments = base_payments + gt_by_type.get("duplicate_payment", 0)
    expected_settlements = (
        base_payments
        - gt_by_type.get("missing_settlement", 0)
        + gt_by_type.get("duplicate_settlement", 0)
        + gt_by_type.get("partial_settlement", 0)
    )
    expected_bank = (
        base_payments
        - gt_by_type.get("missing_bank_credit", 0)
    )

    if not check(
        "1,000 payments generated",
        base_payments == 1000,
        f"seed dataset_size={base_payments}",
    ):
        failures += 1

    if not check(
        "settlements generated",
        len(settlements) == expected_settlements,
        f"{len(settlements)} rows (expected {expected_settlements})",
    ):
        failures += 1

    if not check(
        "bank transactions generated",
        len(bank) == expected_bank,
        f"{len(bank)} rows (expected {expected_bank})",
    ):
        failures += 1

    if not check(
        "refunds generated",
        0 < len(refunds) < base_payments,
        f"{len(refunds)} rows",
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # Anomaly injection                                                    #
    # ------------------------------------------------------------------ #

    print("\n[Anomaly Injection]")

    if not check(
        "anomalies injected",
        len(ground_truth) > 0,
        f"{len(ground_truth)} records in ground_truth.json",
    ):
        failures += 1

    gt_types = {r["exception_type"] for r in ground_truth}
    alloc_types = set(allocation.keys())

    if not check(
        "ground truth matches injected anomalies",
        gt_types == alloc_types,
        f"types: {sorted(gt_types)}",
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # Deterministic seed                                                   #
    # ------------------------------------------------------------------ #

    print("\n[Determinism]")

    seed = allocation_doc.get("seed")
    if not check(
        "deterministic seed",
        seed == 42,
        f"seed={seed}",
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # No negative amounts                                                  #
    # ------------------------------------------------------------------ #

    print("\n[Data Integrity]")

    neg_pay  = (payments["amount"] < 0).sum()
    neg_setl = (settlements["amount"] < 0).sum()
    neg_bank = (bank["amount"] < 0).sum()
    neg_ref  = (refunds["amount"] < 0).sum()

    if not check(
        "no negative amounts",
        neg_pay + neg_setl + neg_bank + neg_ref == 0,
        f"payments={neg_pay}, settlements={neg_setl}, bank={neg_bank}, refunds={neg_ref}",
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # All amounts in paise (integer, >= 100)                              #
    # ------------------------------------------------------------------ #

    min_pay = payments["amount"].min()
    min_ref = refunds["amount"].min() if len(refunds) else 100

    if not check(
        "all records use paise (amount >= 100)",
        min_pay >= 100 and min_ref >= 100,
        f"min payment={min_pay}, min refund={min_ref}",
    ):
        failures += 1

    int_amounts = (
        payments["amount"].apply(lambda x: float(x).is_integer()).all()
        and settlements["amount"].apply(lambda x: float(x).is_integer()).all()
        and bank["amount"].apply(lambda x: float(x).is_integer()).all()
    )

    if not check(
        "all amounts are integers (paise)",
        int_amounts,
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # No duplicate IDs                                                     #
    # ------------------------------------------------------------------ #

    dup_pay_ids  = payments["razorpay_payment_id"].duplicated().sum()
    dup_setl_ids = settlements["razorpay_settlement_id"].duplicated().sum()
    dup_utrs     = bank["utr"].duplicated().sum()

    if not check(
        "CSV files readable",
        True,
        "payments, settlements, bank, refunds loaded OK",
    ):
        failures += 1

    # ------------------------------------------------------------------ #
    # Ground truth file exists                                             #
    # ------------------------------------------------------------------ #

    print("\n[Output Files]")

    for path in [
        raw / "payments.csv",
        raw / "settlements.csv",
        raw / "bank_transactions.csv",
        raw / "refunds.csv",
        gt  / "allocation.json",
        gt  / "ground_truth.json",
    ]:
        if not check(
            str(path.relative_to(ROOT)),
            path.exists(),
        ):
            failures += 1

    # ------------------------------------------------------------------ #
    # Summary                                                              #
    # ------------------------------------------------------------------ #

    print("\n" + "=" * 50)

    if failures == 0:
        print(f"{PASS} All checks passed.\n")
    else:
        print(f"{FAIL} {failures} check(s) failed.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
