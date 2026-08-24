from datetime import timedelta


def inject_timing_anomaly(
    settlement,
    days: int = 5,
):
    settlement.settlement_date += timedelta(
        days=days
    )

    return settlement