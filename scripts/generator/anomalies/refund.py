def inject_refund_mismatch(
    refunds,
    payment_id: str,
):
    """
    Removes the refund for a given payment_id,
    simulating a refund that was processed but
    not reflected in the data.
    """

    return [
        refund
        for refund in refunds
        if refund.payment_id != payment_id
    ]
