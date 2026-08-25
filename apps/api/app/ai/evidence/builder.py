from datetime import datetime


class EvidenceBuilder:

    def build(
        self,
        exception,
        payment,
        settlements,
        bank_transactions,
        refunds,
    ):

        evidence = []

        if payment:

            evidence.extend(
                [
                    {
                        "source_type": "payment",
                        "source_id": (
                            payment.razorpay_payment_id
                        ),
                        "field": "amount",
                        "value": str(
                            payment.amount
                        ),
                    },
                    {
                        "source_type": "payment",
                        "source_id": (
                            payment.razorpay_payment_id
                        ),
                        "field": "fee",
                        "value": str(
                            payment.fee
                        ),
                    },
                    {
                        "source_type": "payment",
                        "source_id": (
                            payment.razorpay_payment_id
                        ),
                        "field": "tax",
                        "value": str(
                            payment.tax
                        ),
                    },
                ]
            )

        for settlement in settlements:

            evidence.extend(
                [
                    {
                        "source_type": "settlement",
                        "source_id": (
                            settlement
                            .razorpay_settlement_id
                        ),
                        "field": "amount",
                        "value": str(
                            settlement.amount
                        ),
                    },
                    {
                        "source_type": "settlement",
                        "source_id": (
                            settlement
                            .razorpay_settlement_id
                        ),
                        "field": "utr",
                        "value": settlement.utr,
                    },
                ]
            )

        for transaction in bank_transactions:

            evidence.extend(
                [
                    {
                        "source_type": "bank_transaction",
                        "source_id": transaction.id,
                        "field": "amount",
                        "value": str(
                            transaction.amount
                        ),
                    },
                    {
                        "source_type": "bank_transaction",
                        "source_id": transaction.id,
                        "field": "utr",
                        "value": transaction.utr,
                    },
                ]
            )

        for refund in refunds:

            evidence.extend(
                [
                    {
                        "source_type": "refund",
                        "source_id": (
                            refund.razorpay_refund_id
                        ),
                        "field": "amount",
                        "value": str(
                            refund.amount
                        ),
                    },
                    {
                        "source_type": "refund",
                        "source_id": (
                            refund.razorpay_refund_id
                        ),
                        "field": "status",
                        "value": refund.status,
                    },
                ]
            )

        return evidence