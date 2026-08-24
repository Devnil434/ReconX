def inject_fee_mismatch(
    settlement,
    difference: int = 500,
):
    """
    Creates a settlement amount that differs
    from the expected deterministic amount.
    """

    settlement.amount -= difference

    return settlement