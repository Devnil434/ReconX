import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "apps" / "api"),
)

from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.models.bank_transaction import (
    BankTransaction,
)
from app.models.refund import Refund


DATA = ROOT / "data" / "raw"


def import_data():

    db = SessionLocal()

    try:

        payments = pd.read_csv(
            DATA / "payments.csv"
        )

        settlements = pd.read_csv(
            DATA / "settlements.csv"
        )

        bank = pd.read_csv(
            DATA / "bank_transactions.csv"
        )

        refunds = pd.read_csv(
            DATA / "refunds.csv"
        )

        print(
            f"Payments: {len(payments)}"
        )

        for _, row in payments.iterrows():

            db.add(
                Payment(
                    razorpay_payment_id=(
                        row["razorpay_payment_id"]
                    ),
                    order_id=row["order_id"],
                    amount=int(row["amount"]),
                    currency=row["currency"],
                    status=row["status"],
                    fee=int(row["fee"]),
                    tax=int(row["tax"]),
                    created_at=pd.to_datetime(
                        row["created_at"]
                    ).to_pydatetime(),
                    captured_at=pd.to_datetime(
                        row["captured_at"]
                    ).to_pydatetime(),
                )
            )

        for _, row in settlements.iterrows():

            db.add(
                Settlement(
                    razorpay_settlement_id=(
                        row[
                            "razorpay_settlement_id"
                        ]
                    ),
                    payment_id=row[
                        "payment_id"
                    ],
                    utr=row["utr"],
                    amount=int(row["amount"]),
                    fee=int(row["fee"]),
                    tax=int(row["tax"]),
                    status=row["status"],
                    settlement_date=pd.to_datetime(
                        row[
                            "settlement_date"
                        ]
                    ).to_pydatetime(),
                )
            )

        for _, row in bank.iterrows():

            db.add(
                BankTransaction(
                    bank_reference=(
                        row["bank_reference"]
                    ),
                    utr=row["utr"],
                    amount=int(row["amount"]),
                    transaction_type=(
                        row[
                            "transaction_type"
                        ]
                    ),
                    transaction_date=pd.to_datetime(
                        row[
                            "transaction_date"
                        ]
                    ).to_pydatetime(),
                    description=row[
                        "description"
                    ],
                )
            )

        for _, row in refunds.iterrows():

            db.add(
                Refund(
                    razorpay_refund_id=row["id"],
                    payment_id=row[
                        "payment_id"
                    ],
                    amount=int(row["amount"]),
                    status=row["status"],
                    created_at=pd.to_datetime(
                        row["created_at"]
                    ).to_pydatetime(),
                )
            )

        db.commit()

        print(
            "Dataset imported successfully."
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    import_data()