import uuid
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix='/demo/scenarios', tags=['Demo Scenarios'])


@router.post('/fee-mismatch')
def trigger_fee_mismatch_scenario():
    case_id = f'CASE-DEMO-{uuid.uuid4().hex[:6].upper()}'
    return {
        'case_id': case_id,
        'scenario': 'fee_mismatch',
        'financial_state': {
            'payment_amount': 10000,
            'fee': 200,
            'tax': 36,
            'expected_settlement': 9764,
            'actual_settlement': 9764,
            'bank_credit': 9764,
            'difference': 0,
        },
        'ai_investigation': {
            'root_cause': 'Fee + GST deduction',
            'confidence': 98.2,
            'hypotheses': [
                {'cause': 'Fee/Tax Schedule Mismatch', 'confidence': 98.2},
                {'cause': 'Manual Adjustment', 'confidence': 1.1},
                {'cause': 'Bank Fee Discrepancy', 'confidence': 0.7},
            ],
            'summary': 'Discrepancy explained by standard 2% gateway fee + 18% GST.',
        },
        'evidence': [
            {'field': 'Payment Amount', 'value': '₹10,000', 'verified': True},
            {'field': 'Gateway Fee (2%)', 'value': '₹200', 'verified': True},
            {'field': 'GST (18% of Fee)', 'value': '₹36', 'verified': True},
            {'field': 'Settlement Payout', 'value': '₹9,764', 'verified': True},
            {'field': 'Bank Credit UTR', 'value': 'UTR9764001 (Matched)', 'verified': True},
        ],
        'policy_decision': {
            'risk_level': 'LOW',
            'difference_zero': True,
            'unresolved_questions': 0,
            'action': 'AUTO_RESOLVE',
            'allowed': True,
        },
        'status': 'RESOLVED',
        'timeline': [
            {'time': '13:04:11', 'event': 'Payment received'},
            {'time': '13:04:12', 'event': 'Settlement matched'},
            {'time': '13:04:12', 'event': 'Exception detected (Fee/Tax)'},
            {'time': '13:04:12', 'event': 'AI investigation completed'},
            {'time': '13:04:13', 'event': 'Policy evaluated (LOW RISK)'},
            {'time': '13:04:13', 'event': 'Auto-resolution executed'},
            {'time': '13:04:14', 'event': 'State verified & Case resolved'},
        ]
    }


@router.post('/missing-bank')
def trigger_missing_bank_scenario():
    case_id = f'CASE-DEMO-{uuid.uuid4().hex[:6].upper()}'
    return {
        'case_id': case_id,
        'scenario': 'missing_bank',
        'financial_state': {
            'payment_amount': 15000,
            'fee': 300,
            'tax': 54,
            'expected_settlement': 14646,
            'actual_settlement': 14646,
            'bank_credit': 0,
            'difference': 14646,
        },
        'ai_investigation': {
            'root_cause': 'Missing Bank Credit / Payout In-Transit',
            'confidence': 92.5,
            'hypotheses': [
                {'cause': 'Settlement Initiated, Bank Pending', 'confidence': 92.5},
                {'cause': 'Bank Account Hold', 'confidence': 5.0},
                {'cause': 'UTR Mismatch', 'confidence': 2.5},
            ],
            'summary': 'Razorpay status processed but UTR missing from bank statement feed.',
        },
        'evidence': [
            {'field': 'Payment Amount', 'value': '₹15,000', 'verified': True},
            {'field': 'Settlement Status', 'value': 'Processed by Razorpay', 'verified': True},
            {'field': 'Bank Statement UTR', 'value': 'NOT FOUND', 'verified': False},
        ],
        'policy_decision': {
            'risk_level': 'MEDIUM',
            'difference_zero': False,
            'unresolved_questions': 1,
            'action': 'HUMAN_REVIEW',
            'allowed': False,
        },
        'status': 'HUMAN_REVIEW',
        'timeline': [
            {'time': '13:05:01', 'event': 'Payment received'},
            {'time': '13:05:02', 'event': 'Settlement processed'},
            {'time': '13:05:03', 'event': 'Bank statement check (UTR missing)'},
            {'time': '13:05:03', 'event': 'AI investigation completed'},
            {'time': '13:05:04', 'event': 'Policy evaluated (HUMAN REVIEW)'},
            {'time': '13:05:04', 'event': 'Routed to Operations Queue'},
        ]
    }


@router.post('/duplicate-settlement')
def trigger_duplicate_settlement_scenario():
    case_id = f'CASE-DEMO-{uuid.uuid4().hex[:6].upper()}'
    return {
        'case_id': case_id,
        'scenario': 'duplicate_settlement',
        'financial_state': {
            'payment_amount': 25000,
            'fee': 500,
            'tax': 90,
            'expected_settlement': 24410,
            'actual_settlement': 48820,
            'bank_credit': 48820,
            'difference': -24410,
        },
        'ai_investigation': {
            'root_cause': 'Duplicate Gateway Settlement Batch',
            'confidence': 97.4,
            'hypotheses': [
                {'cause': 'Duplicate Batch Payout', 'confidence': 97.4},
                {'cause': 'Multiple Payment Auth', 'confidence': 2.6},
            ],
            'summary': 'Two separate settlement batches claim payout for payment ID pay_test_dup.',
        },
        'evidence': [
            {'field': 'Payment ID', 'value': 'pay_test_dup_999', 'verified': True},
            {'field': 'Settlement #1', 'value': 'setl_001 (₹24,410)', 'verified': True},
            {'field': 'Settlement #2', 'value': 'setl_002 (₹24,410 - DUPLICATE)', 'verified': False},
        ],
        'policy_decision': {
            'risk_level': 'HIGH',
            'difference_zero': False,
            'unresolved_questions': 1,
            'action': 'BLOCK',
            'allowed': False,
        },
        'status': 'BLOCKED',
        'timeline': [
            {'time': '13:06:10', 'event': 'Duplicate settlement webhook received'},
            {'time': '13:06:11', 'event': 'AI investigation identified duplicate'},
            {'time': '13:06:11', 'event': 'Policy engine raised HIGH RISK alert'},
            {'time': '13:06:12', 'event': 'Automated payout BLOCKED'},
        ]
    }


@router.post('/unknown')
def trigger_unknown_scenario():
    case_id = f'CASE-DEMO-{uuid.uuid4().hex[:6].upper()}'
    return {
        'case_id': case_id,
        'scenario': 'unknown_difference',
        'financial_state': {
            'payment_amount': 12000,
            'fee': 240,
            'tax': 48,
            'expected_settlement': 11712,
            'actual_settlement': 8312,
            'bank_credit': 8312,
            'difference': 3400,
        },
        'ai_investigation': {
            'root_cause': 'Unexplained Margin Discrepancy',
            'confidence': 52.0,
            'hypotheses': [
                {'cause': 'Chargeback Reserve Deduction', 'confidence': 52.0},
                {'cause': 'Partial Settlement Batch', 'confidence': 29.0},
                {'cause': 'Bank Fee Mismatch', 'confidence': 19.0},
            ],
            'summary': 'AI confidence below 85% threshold; root cause ambiguous.',
        },
        'evidence': [
            {'field': 'Discrepancy Amount', 'value': '₹3,400', 'verified': False},
            {'field': 'Gateway Reserve Note', 'value': 'Unspecified', 'verified': False},
        ],
        'policy_decision': {
            'risk_level': 'HIGH',
            'difference_zero': False,
            'unresolved_questions': 2,
            'action': 'HUMAN_REVIEW',
            'allowed': False,
        },
        'status': 'HUMAN_REVIEW',
        'timeline': [
            {'time': '13:07:00', 'event': 'Discrepancy detected (₹3,400)'},
            {'time': '13:07:01', 'event': 'AI confidence low (52%)'},
            {'time': '13:07:01', 'event': 'Routed to Finance Review'},
        ]
    }


@router.post('/ai-failure')
def trigger_ai_failure_scenario():
    case_id = f'CASE-DEMO-{uuid.uuid4().hex[:6].upper()}'
    return {
        'case_id': case_id,
        'scenario': 'ai_failure',
        'financial_state': {
            'payment_amount': 8000,
            'fee': 160,
            'tax': 28,
            'expected_settlement': 7812,
            'actual_settlement': 7500,
            'bank_credit': 7500,
            'difference': 312,
        },
        'ai_investigation': {
            'root_cause': 'AI Investigation Unavailable',
            'confidence': 0.0,
            'hypotheses': [],
            'summary': 'AI provider service error. Safe fallback enforced: zero autonomous action.',
        },
        'evidence': [],
        'policy_decision': {
            'risk_level': 'HIGH',
            'difference_zero': False,
            'unresolved_questions': 1,
            'action': 'HUMAN_REVIEW',
            'allowed': False,
        },
        'status': 'HUMAN_REVIEW',
        'timeline': [
            {'time': '13:08:00', 'event': 'Exception detected'},
            {'time': '13:08:01', 'event': 'AI Provider Timeout / Exception'},
            {'time': '13:08:01', 'event': 'Audit event AI_FAILURE recorded'},
            {'time': '13:08:01', 'event': 'Fallback: Enforced HUMAN REVIEW'},
        ]
    }
