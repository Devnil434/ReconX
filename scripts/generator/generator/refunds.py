import random
from datetime import timedelta

from ..models.financial import Payment, Refund
from ..utils.ids import refund_id


def generate_refunds(
    payments: list[Payment],
    refund_rate: float = 0.08,
    seed: int = 42,
) -> list[Refund]:

    random.seed(seed)

    refunds = []

    for payment in payments:

        if random.random() > refund_rate:
            continue

        max_refund = payment.amount

        refund_amount = random.randint(
            100,
            max_refund,
        )

        refund = Refund(
            id=refund_id(),
            payment_id=payment.razorpay_payment_id,
            amount=refund_amount,
            status="processed",
            created_at=(
                payment.captured_at
                + timedelta(days=1)
            ),
        )

        refunds.append(refund)

    return refunds