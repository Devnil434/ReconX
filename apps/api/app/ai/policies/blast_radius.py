def calculate_blast_radius(
    exception,
    action: str,
) -> float:

    amount = abs(
        getattr(exception, "difference", 0)
    )

    if action == "mark_reconciled":
        return min(
            amount / 100_000,
            1.0,
        )

    if action == "create_refund":
        return min(
            amount / 50_000,
            1.0,
        )

    return 0.0
