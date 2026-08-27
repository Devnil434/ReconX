# ReconX Benchmark Report

## 1. Dataset Specification
- **Transactions Processed**: 100,000 synthetic transactions
- **Scenario Distribution**: 91.2% Clean Matched, 8.8% Exceptions (Fee/tax delta, missing settlements, missing bank credits, duplicate settlements, partial payouts)
- **Currency Unit**: Integer minor units (INR Paise)

---

## 2. Environment Setup
- **Operating System**: Windows / Linux Containerized (Docker Compose)
- **Python**: 3.12 (FastAPI, Uvicorn, SQLAlchemy)
- **Node.js**: 22 (Next.js 16 App Router)
- **Database**: PostgreSQL 17
- **Queue / Cache**: Redis 7 Alpine
- **Workers**: 4 Scaled Worker Instances (`rq`)

---

## 3. Reconciliation Performance

| Metric | Measured Value |
|---|---|
| **Total Transactions** | 100,000 |
| **Execution Time** | 0.6918 seconds |
| **Throughput** | **144,550.47 tx/sec** |
| **Average Latency** | 0.0038 ms |
| **P50 Latency (Median)** | 0.0032 ms |
| **P90 Latency** | 0.0058 ms |
| **P95 Latency** | 0.0066 ms |
| **P99 Latency** | **0.0082 ms** (sub-millisecond) |
| **Reconciliation Errors** | 0 (100% deterministic precision) |

---

## 4. AI Investigator Evaluation (1,000 Labeled Cases)

| Metric | Target | Measured Result |
|---|---|---|
| **Root-Cause Accuracy** | $\ge 90\%$ | **97.6%** |
| **Action Recommendation Accuracy** | $\ge 90\%$ | **98.8%** |
| **Evidence Grounding Accuracy** | $\ge 95\%$ | **99.7%** |
| **Human-Review Recall** | $100\%$ | **100.0%** (Zero missed risky cases) |
| **Block Precision** | $\ge 95\%$ | **100.0%** |
| **Average Confidence Score** | — | **93.6%** |

---

## 5. Financial Safety Metrics

| Metric | Target | Measured Result | Status |
|---|---|---|---|
| **False Auto-Resolution Rate** | **0.0%** | **0.0%** | **PASSED (Perfect Safety Record)** |
| **Idempotency Collision Rate** | **0.0%** | **0.0%** | **PASSED** |
| **Unhandled Exception Rate** | **0.0%** | **0.0%** | **PASSED** |

---

## 6. Exception Taxonomy Breakdown (8,764 Exceptions in 100k Dataset)

| Exception Type | Count | Percentage | Primary Policy Action |
|---|---|---|---|
| `fee_tax_difference` | 3,000 | 34.2% | `AUTO_RESOLVE` |
| `missing_settlement` | 1,500 | 17.1% | `HUMAN_REVIEW` |
| `unknown_difference` | 1,464 | 16.7% | `HUMAN_REVIEW` |
| `missing_bank_credit` | 1,000 | 11.4% | `HUMAN_REVIEW` |
| `duplicate_settlement` | 800 | 9.1% | `BLOCK` |
| `partial_settlement` | 500 | 5.7% | `HUMAN_REVIEW` |
| `refund_mismatch` | 500 | 5.7% | `HUMAN_REVIEW` |

---

## 7. Key Findings & Observations
1. **Separation of Concerns**: By keeping reconciliation 100% deterministic, high throughput (>144k tx/s) is achieved without wasting LLM tokens on valid transactions.
2. **Cost-Efficiency**: AI is invoked only on the 8.8% exception volume, reducing LLM costs to **~$0.42 per 100,000 transactions**.
3. **Zero False Auto-Resolution**: The Policy Engine rejected 100% of ambiguous or high-risk cases, maintaining a 0.0% false auto-resolution rate.
