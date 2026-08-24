from copy import deepcopy

from .duplicate_payment import inject_duplicate_payment
from .duplicate_settlement import inject_duplicate_settlement
from .fee_mismatch import inject_fee_mismatch
from .missing_bank import inject_missing_bank_credit
from .missing_mismatch import inject_missing_settlement
from .partial_settlement import inject_partial_settlement
from .refund import inject_refund_mismatch
from .timing import inject_timing_anomaly


def apply_anomalies(
    payments,
    settlements,
    bank_transactions,
    refunds,
    cases,
):
    ground_truth = []

    payment_lookup = {
        payment.razorpay_payment_id: payment
        for payment in payments
    }

    for anomaly_type, payment_ids in cases.items():

        for payment_id in payment_ids:

            payment = payment_lookup.get(
                payment_id
            )

            if payment is None:
                continue

            if anomaly_type == "fee_mismatch":

                settlement = next(
                    (
                        s
                        for s in settlements
                        if s.payment_id == payment_id
                    ),
                    None,
                )

                if settlement:
                    inject_fee_mismatch(
                        settlement
                    )

            elif anomaly_type == "missing_settlement":

                settlements[:] = (
                    inject_missing_settlement(
                        settlements,
                        payment_id,
                    )
                )

            elif anomaly_type == "missing_bank_credit":

                settlement = next(
                    (
                        s
                        for s in settlements
                        if s.payment_id == payment_id
                    ),
                    None,
                )

                if settlement:
                    bank_transactions[:] = (
                        inject_missing_bank_credit(
                            bank_transactions,
                            settlement.utr,
                        )
                    )

            elif anomaly_type == "duplicate_payment":

                inject_duplicate_payment(
                    payments,
                    payment,
                )

            elif anomaly_type == "duplicate_settlement":

                settlement = next(
                    (
                        s
                        for s in settlements
                        if s.payment_id == payment_id
                    ),
                    None,
                )

                if settlement:
                    inject_duplicate_settlement(
                        settlements,
                        settlement,
                    )

            elif anomaly_type == "partial_settlement":

                settlement = next(
                    (
                        s
                        for s in settlements
                        if s.payment_id == payment_id
                    ),
                    None,
                )

                if settlement:
                    inject_partial_settlement(
                        settlements,
                        settlement,
                    )

            elif anomaly_type == "timing_anomaly":

                settlement = next(
                    (
                        s
                        for s in settlements
                        if s.payment_id == payment_id
                    ),
                    None,
                )

                if settlement:
                    inject_timing_anomaly(
                        settlement
                    )

            elif anomaly_type == "refund_mismatch":

                refunds[:] = (
                    inject_refund_mismatch(
                        refunds,
                        payment_id,
                    )
                )

            ground_truth.append(
                {
                    "payment_id": payment_id,
                    "exception_type": anomaly_type,
                    "expected_status": "exception",
                }
            )

    return ground_truth