def inject_missing_settlement(
    settlements,
    payment_id: str,
):
    return [
        settlement
        for settlement in settlements
        if settlement.payment_id != payment_id
    ]