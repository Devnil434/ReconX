"""
Deterministic ID generators.

All IDs are generated using a seeded random instance so that
seed=42 produces the same IDs every run, forever.

Call seed_ids(seed) once at the start of generate.py before
any generators run.
"""

import random as _random

_rng = _random.Random()


def seed_ids(seed: int) -> None:
    """Seed the shared RNG used by all ID generators."""
    _rng.seed(seed)


def _hex(n: int) -> str:
    return "".join(
        _rng.choice("0123456789abcdef")
        for _ in range(n)
    )


def payment_id() -> str:
    return f"pay_test_{_hex(16)}"


def order_id() -> str:
    return f"order_test_{_hex(16)}"


def settlement_id() -> str:
    return f"setl_test_{_hex(16)}"


def refund_id() -> str:
    return f"rfnd_test_{_hex(16)}"


def bank_transaction_id() -> str:
    return f"bank_txn_{_hex(16)}"


def utr() -> str:
    return f"UTR{_hex(18).upper()}"


def case_id() -> str:
    return f"CASE-{_hex(8).upper()}"