from types import SimpleNamespace

from app.services.reconciliation_engine import (
    ReconciliationEngine,
)


def payment():
    return SimpleNamespace(
        amount=100_000,
        fee=2_000,
        tax=360,
    )


def settlement(amount=97_640):
    return SimpleNamespace(
        amount=amount,
        utr="UTR123",
    )


def bank(amount=97_640):
    return SimpleNamespace(
        amount=amount,
        utr="UTR123",
        id="BANK1",
    )


def test_exact_match():
    engine = ReconciliationEngine()
    result = engine.reconcile(
        payment(),
        [settlement()],
        [bank()],
    )
    assert result.status == "matched"
    assert result.difference == 0


def test_amount_mismatch():
    engine = ReconciliationEngine()
    result = engine.reconcile(
        payment(),
        [settlement(95_000)],
        [bank(95_000)],
    )
    assert result.status == "exception"
    assert result.difference != 0


def test_missing_settlement():
    engine = ReconciliationEngine()
    result = engine.reconcile(
        payment(),
        [],
        [],
    )
    assert result.status == "exception"
    assert (
        result.match_type == "no_settlement"
    )


def test_missing_bank():
    engine = ReconciliationEngine()
    result = engine.reconcile(
        payment(),
        [settlement()],
        [],
    )
    assert result.status == "exception"
    assert (
        result.match_type == "no_bank_credit"
    )
