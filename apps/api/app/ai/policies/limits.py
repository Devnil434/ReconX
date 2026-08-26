MAX_AUTO_RESOLVE_AMOUNT = 100_000
MAX_AUTO_REFUND_AMOUNT = 0

REQUIRE_HUMAN_FOR_REFUNDS = True


def action_allowed(
    action: str,
    amount: int,
) -> bool:

    if action == "create_refund":

        if REQUIRE_HUMAN_FOR_REFUNDS:
            return False

        if amount > MAX_AUTO_REFUND_AMOUNT:
            return False

    if action == "mark_reconciled":

        if amount > MAX_AUTO_RESOLVE_AMOUNT:
            return False

    return True
