from datetime import timedelta

from ..models.financial import Payment, Settlement
from ..utils.ids import settlement_id, utr


def generate_settlements(
    payments: list[Payment],
) -> list[Settlement]:

    settlements = []

    for payment in payments:

        settlement_amount = (
            payment.amount
            - payment.fee
            - payment.tax
        )

        settlement = Settlement(
            id=settlement_id(),
            razorpay_settlement_id=settlement_id(),
            payment_id=payment.razorpay_payment_id,
            utr=utr(),
            amount=settlement_amount,
            fee=payment.fee,
            tax=payment.tax,
            status="processed",
            settlement_date=payment.captured_at
            + timedelta(days=2),
        )

        settlements.append(settlement)

    return settlements