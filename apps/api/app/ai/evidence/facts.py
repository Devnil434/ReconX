def build_financial_facts(
    payment,
    settlements,
    bank_transactions,
    refunds,
):

    expected_net = (
        payment.amount
        - payment.fee
        - payment.tax
    )

    settlement_total = sum(
        settlement.amount
        for settlement in settlements
    )

    bank_total = sum(
        transaction.amount
        for transaction in bank_transactions
    )

    refund_total = sum(
        refund.amount
        for refund in refunds
        if refund.status == "processed"
    )

    return {
        "payment_amount": payment.amount,
        "payment_fee": payment.fee,
        "payment_tax": payment.tax,
        "expected_net_settlement": expected_net,
        "settlement_total": settlement_total,
        "bank_total": bank_total,
        "refund_total": refund_total,
        "settlement_difference": (
            expected_net
            - settlement_total
        ),
        "bank_difference": (
            settlement_total
            - bank_total
        ),
    }