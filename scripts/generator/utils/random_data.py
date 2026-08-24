import random
from datetime import datetime, timedelta


def random_amount(
    minimum: int = 100,
    maximum: int = 100_000,
) -> int:
    rupees = random.randint(minimum, maximum)
    return rupees * 100


def random_date(
    start: datetime,
    end: datetime,
) -> datetime:
    delta = end - start

    seconds = random.randint(
        0,
        int(delta.total_seconds()),
    )

    return start + timedelta(seconds=seconds)


def calculate_fee(amount: int) -> int:
    """
    Synthetic fee model.

    2% processing fee.
    """
    return round(amount * 0.02)


def calculate_tax(fee: int) -> int:
    """
    Synthetic GST model.

    18% GST on fee.
    """
    return round(fee * 0.18)