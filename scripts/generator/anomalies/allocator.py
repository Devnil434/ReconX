import random


def allocate_cases(
    payment_ids: list[str],
    distribution: dict[str, float],
    seed: int = 42,
) -> dict[str, list[str]]:

    random.seed(seed)

    available = payment_ids.copy()

    random.shuffle(available)

    cases: dict[str, list[str]] = {}

    cursor = 0

    for anomaly_type, percentage in distribution.items():

        count = int(len(payment_ids) * percentage)

        selected = available[
            cursor: cursor + count
        ]

        cases[anomaly_type] = selected

        cursor += count

    return cases