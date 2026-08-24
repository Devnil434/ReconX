from copy import deepcopy


def inject_duplicate_payment(
    payments,
    payment,
):
    duplicate = deepcopy(payment)

    duplicate.id = f"{payment.id}_DUP"
    duplicate.razorpay_payment_id = (
        f"{payment.razorpay_payment_id}_DUP"
    )

    payments.append(duplicate)

    return payments