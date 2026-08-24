from datetime import datetime, timedelta

from ..models.financial import Payment
from ..utils.ids import order_id, payment_id
from ..utils.random_data import (
    calculate_fee,
    calculate_tax,
    random_amount,
    random_date,
)


def generate_payments(
    count: int,
    seed: int = 42,
) -> list[Payment]:

    import random

    random.seed(seed)

    # Fixed epoch — ensures seed=42 produces the same dataset forever.
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    payments = []

    for _ in range(count):
        amount = random_amount()

        fee = calculate_fee(amount)
        tax = calculate_tax(fee)

        created_at = random_date(start, end)

        payment = Payment(
            id=payment_id(),
            razorpay_payment_id=payment_id(),
            order_id=order_id(),
            amount=amount,
            currency="INR",
            status="captured",
            fee=fee,
            tax=tax,
            created_at=created_at,
            captured_at=created_at,
        )

        payments.append(payment)

    return payments