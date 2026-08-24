from copy import deepcopy


def inject_duplicate_settlement(
    settlements,
    settlement,
):
    duplicate = deepcopy(settlement)

    duplicate.id = f"{settlement.id}_DUP"
    duplicate.razorpay_settlement_id = (
        f"{settlement.razorpay_settlement_id}_DUP"
    )

    settlements.append(duplicate)

    return settlements