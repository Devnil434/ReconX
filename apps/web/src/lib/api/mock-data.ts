/**
 * mock-data.ts
 *
 * Offline fallback dataset for ReconX.
 * Used automatically when NEXT_PUBLIC_API_URL is unreachable
 * (e.g., Vercel deployment with no deployed backend yet).
 *
 * All shapes mirror the real API response exactly.
 */

import type { ReconciliationSummary, BatchRunResult } from "./reconciliation";
import type { InvestigationCase } from "./investigations";
import type { DemoScenarioResult } from "./demo";
import type { SystemHealth, QueueStats, BenchmarkReport } from "./system";

// ─── Summary / KPI ────────────────────────────────────────────────────────────

export const MOCK_SUMMARY: ReconciliationSummary = {
  total: 1284,
  matched: 1247,
  exceptions: 37,
  match_rate: 0.9712,
};

export const MOCK_BATCH_RESULT: BatchRunResult = {
  total: 1284,
  matched: 1247,
  exceptions: 37,
  match_rate: 0.9712,
  elapsed_seconds: 0.0089,
  transactions_per_second: 144157.3,
};

// ─── Investigation Cases ───────────────────────────────────────────────────────

export const MOCK_CASES: InvestigationCase[] = [
  // AUTO_RESOLVE lane ──────────────────────────────────────────────────────────
  {
    case_id: "CASE-1042",
    payment_id: "pay_QmK9X3nRpT",
    exception_type: "FEE_TAX_DIFFERENCE",
    severity: "low",
    expected_amount: 976400,
    actual_amount: 976400,
    difference: 0,
    status: "resolved",
    recommendation: "AUTO_RESOLVE",
    confidence: 0.982,
    root_cause: "Fee + GST deduction fully accounts for the ₹236 variance.",
    created_at: "2026-09-01T08:14:11Z",
  },
  {
    case_id: "CASE-1043",
    payment_id: "pay_RnL0Y4oSpU",
    exception_type: "FEE_TAX_DIFFERENCE",
    severity: "low",
    expected_amount: 488200,
    actual_amount: 488200,
    difference: 0,
    status: "resolved",
    recommendation: "AUTO_RESOLVE",
    confidence: 0.977,
    root_cause: "Standard 2% gateway fee + 18% GST deducted correctly.",
    created_at: "2026-09-01T08:20:33Z",
  },
  {
    case_id: "CASE-1044",
    payment_id: "pay_SoM1Z5pTqV",
    exception_type: "ROUNDING_ADJUSTMENT",
    severity: "low",
    expected_amount: 250000,
    actual_amount: 249999,
    difference: 1,
    status: "resolved",
    recommendation: "AUTO_RESOLVE",
    confidence: 0.998,
    root_cause: "Sub-paisa rounding adjustment. Zero financial exposure.",
    created_at: "2026-09-01T08:31:05Z",
  },
  {
    case_id: "CASE-1055",
    payment_id: "pay_TpN2A6qUrW",
    exception_type: "FEE_TAX_DIFFERENCE",
    severity: "low",
    expected_amount: 1952800,
    actual_amount: 1952800,
    difference: 0,
    status: "resolved",
    recommendation: "AUTO_RESOLVE",
    confidence: 0.991,
    root_cause: "Tax schedule variance within known fee band. Auto-resolved.",
    created_at: "2026-09-01T09:05:47Z",
  },
  {
    case_id: "CASE-1061",
    payment_id: "pay_UqO3B7rVsX",
    exception_type: "FEE_TAX_DIFFERENCE",
    severity: "low",
    expected_amount: 73640,
    actual_amount: 73640,
    difference: 0,
    status: "resolved",
    recommendation: "AUTO_RESOLVE",
    confidence: 0.964,
    root_cause: "GST component fully reconciled after fee schedule lookup.",
    created_at: "2026-09-01T09:44:12Z",
  },

  // HUMAN_REVIEW lane ──────────────────────────────────────────────────────────
  {
    case_id: "CASE-1048",
    payment_id: "pay_VrP4C8sWtY",
    exception_type: "MISSING_BANK_CREDIT",
    severity: "medium",
    expected_amount: 1250000,
    actual_amount: 0,
    difference: 1250000,
    status: "human_review",
    recommendation: "HUMAN_REVIEW",
    confidence: 0.825,
    root_cause: "UTR ABC123 not found in bank statement. Settlement shows processed.",
    created_at: "2026-09-01T10:02:19Z",
  },
  {
    case_id: "CASE-1050",
    payment_id: "pay_WsQ5D9tXuZ",
    exception_type: "AMOUNT_MISMATCH",
    severity: "medium",
    expected_amount: 500000,
    actual_amount: 492500,
    difference: 7500,
    status: "human_review",
    recommendation: "HUMAN_REVIEW",
    confidence: 0.71,
    root_cause: "₹75 unexplained variance after fee/tax reconciliation. Analyst sign-off required.",
    created_at: "2026-09-01T10:18:44Z",
  },
  {
    case_id: "CASE-1057",
    payment_id: "pay_XtR6E0uYvA",
    exception_type: "TIMING_ANOMALY",
    severity: "low",
    expected_amount: 320000,
    actual_amount: 320000,
    difference: 0,
    status: "human_review",
    recommendation: "HUMAN_REVIEW",
    confidence: 0.68,
    root_cause: "Settlement arrived 5 days after expected window. May be bank-side delay.",
    created_at: "2026-09-01T11:00:31Z",
  },
  {
    case_id: "CASE-1063",
    payment_id: "pay_YuS7F1vZwB",
    exception_type: "REFUND_MISMATCH",
    severity: "medium",
    expected_amount: 150000,
    actual_amount: 200000,
    difference: -50000,
    status: "human_review",
    recommendation: "HUMAN_REVIEW",
    confidence: 0.79,
    root_cause: "Refund of ₹500 applied but settlement reflects full ₹2,000. Possible double credit.",
    created_at: "2026-09-01T11:22:08Z",
  },

  // BLOCKED lane ───────────────────────────────────────────────────────────────
  {
    case_id: "CASE-1045",
    payment_id: "pay_ZvT8G2wAxC",
    exception_type: "DUPLICATE_SETTLEMENT",
    severity: "critical",
    expected_amount: 2441000,
    actual_amount: 4882000,
    difference: -2441000,
    status: "blocked",
    recommendation: "BLOCK",
    confidence: 0.974,
    root_cause: "Two settlement batches (setl_001, setl_002) claiming same payment ID. Payout blocked.",
    created_at: "2026-09-01T12:05:00Z",
  },
  {
    case_id: "CASE-1051",
    payment_id: "pay_AwU9H3xByD",
    exception_type: "SUSPICIOUS_PATTERN",
    severity: "critical",
    expected_amount: 800000,
    actual_amount: 800000,
    difference: 0,
    status: "blocked",
    recommendation: "BLOCK",
    confidence: 0.936,
    root_cause: "Same bank reference UTR across 3 different payment orders. High fraud risk.",
    created_at: "2026-09-01T12:41:17Z",
  },
  {
    case_id: "CASE-1066",
    payment_id: "pay_BxV0I4yCzE",
    exception_type: "DUPLICATE_PAYMENT",
    severity: "critical",
    expected_amount: 100000,
    actual_amount: 200000,
    difference: -100000,
    status: "blocked",
    recommendation: "BLOCK",
    confidence: 0.961,
    root_cause: "Order ORD-9921 has two captured payments. Manual reversal required.",
    created_at: "2026-09-01T13:15:42Z",
  },
];

// ─── Demo Scenarios ────────────────────────────────────────────────────────────

export const MOCK_DEMO_SCENARIOS: Record<string, DemoScenarioResult> = {
  "fee-mismatch": {
    case_id: "CASE-DEMO-FEE001",
    scenario: "fee_mismatch",
    financial_state: {
      payment_amount: 10000,
      fee: 200,
      tax: 36,
      expected_settlement: 9764,
      actual_settlement: 9764,
      bank_credit: 9764,
      difference: 0,
    },
    ai_investigation: {
      root_cause: "Fee + GST deduction",
      confidence: 98.2,
      hypotheses: [
        { cause: "Fee/Tax Schedule Mismatch", confidence: 98.2 },
        { cause: "Manual Adjustment", confidence: 1.1 },
        { cause: "Bank Fee Discrepancy", confidence: 0.7 },
      ],
      summary: "Discrepancy explained by standard 2% gateway fee + 18% GST.",
    },
    evidence: [
      { field: "Payment Amount", value: "₹10,000", verified: true },
      { field: "Gateway Fee (2%)", value: "₹200", verified: true },
      { field: "GST (18% of Fee)", value: "₹36", verified: true },
      { field: "Settlement Payout", value: "₹9,764", verified: true },
      { field: "Bank Credit UTR", value: "UTR9764001 (Matched)", verified: true },
    ],
    policy_decision: {
      risk_level: "LOW",
      difference_zero: true,
      unresolved_questions: 0,
      action: "AUTO_RESOLVE",
      allowed: true,
    },
    status: "RESOLVED",
    timeline: [
      { time: "13:04:11", event: "Payment received" },
      { time: "13:04:12", event: "Settlement matched" },
      { time: "13:04:12", event: "Exception detected (Fee/Tax)" },
      { time: "13:04:12", event: "AI investigation completed" },
      { time: "13:04:13", event: "Policy evaluated (LOW RISK)" },
      { time: "13:04:13", event: "Auto-resolution executed" },
      { time: "13:04:14", event: "State verified & Case resolved" },
    ],
  },
  "missing-bank": {
    case_id: "CASE-DEMO-BANK002",
    scenario: "missing_bank",
    financial_state: {
      payment_amount: 15000,
      fee: 300,
      tax: 54,
      expected_settlement: 14646,
      actual_settlement: 14646,
      bank_credit: 0,
      difference: 14646,
    },
    ai_investigation: {
      root_cause: "Missing Bank Credit / Payout In-Transit",
      confidence: 92.5,
      hypotheses: [
        { cause: "Settlement Initiated, Bank Pending", confidence: 92.5 },
        { cause: "Bank Account Hold", confidence: 5.0 },
        { cause: "UTR Mismatch", confidence: 2.5 },
      ],
      summary: "Razorpay status processed but UTR missing from bank statement feed.",
    },
    evidence: [
      { field: "Payment Amount", value: "₹15,000", verified: true },
      { field: "Settlement Status", value: "Processed by Razorpay", verified: true },
      { field: "Bank Statement UTR", value: "NOT FOUND", verified: false },
    ],
    policy_decision: {
      risk_level: "MEDIUM",
      difference_zero: false,
      unresolved_questions: 1,
      action: "HUMAN_REVIEW",
      allowed: false,
    },
    status: "HUMAN_REVIEW",
    timeline: [
      { time: "13:05:01", event: "Payment received" },
      { time: "13:05:02", event: "Settlement processed" },
      { time: "13:05:03", event: "Bank statement check (UTR missing)" },
      { time: "13:05:03", event: "AI investigation completed" },
      { time: "13:05:04", event: "Policy evaluated (HUMAN REVIEW)" },
      { time: "13:05:04", event: "Routed to Operations Queue" },
    ],
  },
  "duplicate-settlement": {
    case_id: "CASE-DEMO-DUP003",
    scenario: "duplicate_settlement",
    financial_state: {
      payment_amount: 25000,
      fee: 500,
      tax: 90,
      expected_settlement: 24410,
      actual_settlement: 48820,
      bank_credit: 48820,
      difference: -24410,
    },
    ai_investigation: {
      root_cause: "Duplicate Gateway Settlement Batch",
      confidence: 97.4,
      hypotheses: [
        { cause: "Duplicate Batch Payout", confidence: 97.4 },
        { cause: "Multiple Payment Auth", confidence: 2.6 },
      ],
      summary: "Two separate settlement batches claim payout for payment ID pay_test_dup.",
    },
    evidence: [
      { field: "Payment ID", value: "pay_test_dup_999", verified: true },
      { field: "Settlement #1", value: "setl_001 (₹24,410)", verified: true },
      { field: "Settlement #2", value: "setl_002 (₹24,410 - DUPLICATE)", verified: false },
    ],
    policy_decision: {
      risk_level: "HIGH",
      difference_zero: false,
      unresolved_questions: 1,
      action: "BLOCK",
      allowed: false,
    },
    status: "BLOCKED",
    timeline: [
      { time: "13:06:10", event: "Duplicate settlement webhook received" },
      { time: "13:06:11", event: "AI investigation identified duplicate" },
      { time: "13:06:11", event: "Policy engine raised HIGH RISK alert" },
      { time: "13:06:12", event: "Automated payout BLOCKED" },
    ],
  },
  "unknown": {
    case_id: "CASE-DEMO-UNK004",
    scenario: "unknown_difference",
    financial_state: {
      payment_amount: 12000,
      fee: 240,
      tax: 48,
      expected_settlement: 11712,
      actual_settlement: 8312,
      bank_credit: 8312,
      difference: 3400,
    },
    ai_investigation: {
      root_cause: "Unexplained Margin Discrepancy",
      confidence: 52.0,
      hypotheses: [
        { cause: "Chargeback Reserve Deduction", confidence: 52.0 },
        { cause: "Partial Settlement Batch", confidence: 29.0 },
        { cause: "Bank Fee Mismatch", confidence: 19.0 },
      ],
      summary: "AI confidence below 85% threshold; root cause ambiguous.",
    },
    evidence: [
      { field: "Discrepancy Amount", value: "₹3,400", verified: false },
      { field: "Gateway Reserve Note", value: "Unspecified", verified: false },
    ],
    policy_decision: {
      risk_level: "HIGH",
      difference_zero: false,
      unresolved_questions: 2,
      action: "HUMAN_REVIEW",
      allowed: false,
    },
    status: "HUMAN_REVIEW",
    timeline: [
      { time: "13:07:00", event: "Discrepancy detected (₹3,400)" },
      { time: "13:07:01", event: "AI confidence low (52%)" },
      { time: "13:07:01", event: "Routed to Finance Review" },
    ],
  },
  "ai-failure": {
    case_id: "CASE-DEMO-AI005",
    scenario: "ai_failure",
    financial_state: {
      payment_amount: 8000,
      fee: 160,
      tax: 28,
      expected_settlement: 7812,
      actual_settlement: 7500,
      bank_credit: 7500,
      difference: 312,
    },
    ai_investigation: {
      root_cause: "AI Investigation Unavailable",
      confidence: 0.0,
      hypotheses: [],
      summary: "AI provider service error. Safe fallback enforced: zero autonomous action.",
    },
    evidence: [],
    policy_decision: {
      risk_level: "HIGH",
      difference_zero: false,
      unresolved_questions: 1,
      action: "HUMAN_REVIEW",
      allowed: false,
    },
    status: "HUMAN_REVIEW",
    timeline: [
      { time: "13:08:00", event: "Exception detected" },
      { time: "13:08:01", event: "AI Provider Timeout / Exception" },
      { time: "13:08:01", event: "Audit event AI_FAILURE recorded" },
      { time: "13:08:01", event: "Fallback: Enforced HUMAN REVIEW" },
    ],
  },
};

// ─── System Health ─────────────────────────────────────────────────────────────

export const MOCK_SYSTEM_HEALTH: SystemHealth = {
  status: "healthy",
  demo_mode: true,
  services: {
    api: { status: "healthy" },
    database: { status: "healthy", type: "PostgreSQL 17" },
    redis: { status: "healthy", port: 6379 },
    workers: { status: "healthy", count: 4 },
    ai_provider: { status: "healthy", provider: "Google Gemini (Flash) / Rule Fallback" },
    razorpay: { status: "healthy", mode: "mock" },
  },
  queues: {
    reconciliation: 0,
    investigation: 0,
    actions: 0,
    "dead-letter": 0,
  },
  metrics: {
    total_transactions: 100000,
    exceptions_detected: 8764,
    ai_investigations: 8764,
    ai_calls_total: 8764,
    ai_tokens_input: 1420800,
    ai_tokens_output: 315400,
    estimated_ai_cost_usd: 0.42,
    ai_calls_per_tx_pct: 8.76,
  },
};

export const MOCK_QUEUE_STATS: QueueStats = {
  reconciliation: { queued: 0, failed: 0 },
  investigation: { queued: 0, failed: 0 },
  actions: { queued: 0, failed: 0 },
  dead_letter: { queued: 0 },
};

// ─── Benchmark ─────────────────────────────────────────────────────────────────

export const MOCK_BENCHMARK: BenchmarkReport = {
  dataset_size: 100000,
  throughput_tx_per_sec: 144550.47,
  execution_time_seconds: 0.6918,
  latencies_ms: {
    average: 0.0038,
    p50: 0.0032,
    p90: 0.0058,
    p95: 0.0066,
    p99: 0.0082,
  },
  reconciliation_outcomes: {
    matched: 91236,
    matched_pct: 91.2,
    exceptions: 8764,
    exceptions_pct: 8.8,
  },
  ai_evaluation: {
    evaluated_cases: 1000,
    false_auto_resolution_rate_pct: 0.0,
    root_cause_accuracy_pct: 97.6,
    action_recommendation_accuracy_pct: 98.8,
    evidence_grounding_accuracy_pct: 99.7,
    human_review_recall_pct: 100.0,
    block_precision_pct: 100.0,
    average_confidence_pct: 93.6,
  },
  exception_taxonomy: {
    fee_tax_difference: 3000,
    missing_settlement: 1500,
    missing_bank_credit: 1000,
    duplicate_settlement: 800,
    partial_settlement: 500,
    refund_mismatch: 500,
    unknown_difference: 1464,
  },
};
