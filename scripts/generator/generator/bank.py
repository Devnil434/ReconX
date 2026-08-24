from ..models.financial import BankTransaction, Settlement
from ..utils.ids import bank_transaction_id


def generate_bank_transactions(
    settlements: list[Settlement],
) -> list[BankTransaction]:

    transactions = []

    for settlement in settlements:

        transaction = BankTransaction(
            id=bank_transaction_id(),
            bank_reference=f"BANK-{settlement.utr}",
            utr=settlement.utr,
            amount=settlement.amount,
            transaction_type="credit",
            transaction_date=settlement.settlement_date,
            description=(
                f"Razorpay Settlement "
                f"{settlement.razorpay_settlement_id}"
            ),
        )

        transactions.append(transaction)

    return transactions