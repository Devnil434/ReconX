def build_transaction_graph(
    payment,
    settlements,
    bank_transactions,
    refunds,
):

    return {
        "payment": {
            "id": payment.razorpay_payment_id if payment else None,
            "amount": payment.amount if payment else 0,
        },

        "settlements": [
            {
                "id": settlement.razorpay_settlement_id,
                "amount": settlement.amount,
                "utr": settlement.utr,
            }
            for settlement in settlements
        ],

        "bank_transactions": [
            {
                "id": transaction.id,
                "amount": transaction.amount,
                "utr": transaction.utr,
            }
            for transaction in bank_transactions
        ],

        "refunds": [
            {
                "id": refund.razorpay_refund_id,
                "amount": refund.amount,
                "status": refund.status,
            }
            for refund in refunds
        ],
    }
