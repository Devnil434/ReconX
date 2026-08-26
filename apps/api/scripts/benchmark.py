import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.reconciliation_engine import ReconciliationEngine


@dataclass
class MockPayment:
    amount: int
    fee: int
    tax: int


@dataclass
class MockSettlement:
    amount: int


@dataclass
class MockBankTransaction:
    amount: int


def percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (len(sorted_data) - 1) * pct
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_data[int(index)]
    return sorted_data[lower] * (upper - index) + sorted_data[upper] * (index - lower)


def run_benchmark():
    data_file = Path('data/benchmark/transactions.json')
    if not data_file.exists():
        data_file = Path('../../data/benchmark/transactions.json')

    if not data_file.exists():
        print('Error: transactions.json not found. Run generate_transactions.py first.', file=sys.stderr)
        sys.exit(1)

    print('Loading 100,000 synthetic transactions...')
    with open(data_file, 'r', encoding='utf-8') as f:
        transactions = json.load(f)

    engine = ReconciliationEngine()
    latencies_ms = []

    matched_count = 0
    exception_count = 0

    print('Starting deterministic reconciliation benchmark...')
    start_total = time.perf_counter()

    for tx in transactions:
        scenario = tx.get('scenario', 'normal')
        expected = tx['expected_settlement']

        payment = MockPayment(amount=tx['amount'], fee=tx['fee'], tax=tx['tax'])

        if scenario == 'missing_settlement':
            settlements = []
            bank_txs = [MockBankTransaction(amount=expected)]
        elif scenario == 'missing_bank_credit':
            settlements = [MockSettlement(amount=expected)]
            bank_txs = []
        elif scenario == 'duplicate_settlement':
            settlements = [MockSettlement(amount=expected), MockSettlement(amount=expected)]
            bank_txs = [MockBankTransaction(amount=expected)]
        elif scenario == 'partial_settlement':
            settlements = [MockSettlement(amount=int(expected * 0.5)), MockSettlement(amount=int(expected * 0.5))]
            bank_txs = [MockBankTransaction(amount=expected)]
        elif scenario in ('fee_tax_difference', 'unknown_difference', 'refund_mismatch'):
            settlements = [MockSettlement(amount=expected - 50)]
            bank_txs = [MockBankTransaction(amount=expected - 50)]
        else:
            settlements = [MockSettlement(amount=expected)]
            bank_txs = [MockBankTransaction(amount=expected)]

        t0 = time.perf_counter()
        decision = engine.reconcile(payment=payment, settlements=settlements, bank_transactions=bank_txs)
        t1 = time.perf_counter()

        latencies_ms.append((t1 - t0) * 1000.0)

        if decision.status == 'matched':
            matched_count += 1
        else:
            exception_count += 1

    total_elapsed = time.perf_counter() - start_total
    total_tx = len(transactions)
    throughput = total_tx / total_elapsed

    p50 = percentile(latencies_ms, 0.50)
    p90 = percentile(latencies_ms, 0.90)
    p95 = percentile(latencies_ms, 0.95)
    p99 = percentile(latencies_ms, 0.99)
    avg_lat = sum(latencies_ms) / total_tx

    print('================================================================================')
    print('          RECONX DETERMINISTIC RECONCILIATION BENCHMARK REPORT          ')
    print('================================================================================')
    print('  Transactions Processed : %d' % total_tx)
    print('  Total Execution Time   : %.4f seconds' % total_elapsed)
    print('  Throughput             : %.2f transactions/sec' % throughput)
    print('--------------------------------------------------------------------------------')
    print('  Latency Percentiles (ms):')
    print('    Average              : %.4f ms' % avg_lat)
    print('    P50 (Median)         : %.4f ms' % p50)
    print('    P90                  : %.4f ms' % p90)
    print('    P95                  : %.4f ms' % p95)
    print('    P99                  : %.4f ms' % p99)
    print('--------------------------------------------------------------------------------')
    print('  Reconciliation Outcomes:')
    print('    Matched Transactions : %d (%.1f%%)' % (matched_count, matched_count / total_tx * 100))
    print('    Exceptions Detected  : %d (%.1f%%)' % (exception_count, exception_count / total_tx * 100))
    print('================================================================================')


if __name__ == '__main__':
    run_benchmark()
