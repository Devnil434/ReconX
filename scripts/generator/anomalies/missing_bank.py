def inject_missing_bank_credit(
    transactions,
    utr_value: str,
):
    return [
        transaction
        for transaction in transactions
        if transaction.utr != utr_value
    ]