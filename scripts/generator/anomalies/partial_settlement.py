from copy import deepcopy


def inject_partial_settlement(
    settlements,
    settlement,
    ratio: float = 0.6,
):
    settlement.amount = int(
        settlement.amount * ratio
    )

    second = deepcopy(settlement)

    second.id = f"{settlement.id}_PART2"
    second.razorpay_settlement_id = (
        f"{settlement.razorpay_settlement_id}_PART2"
    )

    second.amount = (
        settlement.amount
        // 2
    )

    settlements.append(second)

    return settlements