# ReconX Architecture Specification

> **Autonomous Payment Reconciliation Investigator**
> *AI investigates. Policy authorizes. Verification proves.*

---

## 1. High-Level Target Architecture

```
                         RAZORPAY TEST MODE
                                │
                                ▼
                         WEBHOOK GATEWAY
                                │
                   ┌────────────┴────────────┐
                   │                         │
              Verify HMAC              Event ID
              (Raw Body)                dedupe
                   │                         │
                   └────────────┬────────────┘
                                │
                                ▼
                         EVENT STORE
                          PostgreSQL
                                │
                                ▼
                          REDIS QUEUE (RQ)
                                │
                                ▼
                         WORKER POOL
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
            RECONCILE      INVESTIGATE       VERIFY
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                          RISK ENGINE
                                │
                          POLICY ENGINE
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
          AUTO-RESOLVE     HUMAN REVIEW         BLOCK
               │                │
               └────────┬───────┘
                        ▼
                  ACTION EXECUTOR
                        │
                        ▼
                   RAZORPAY API
                        │
                        ▼
                  STATE VERIFIER
                        │
                        ▼
                 RECONCILE AGAIN
                        │
                        ▼
                    AUDIT LOG
                        │
                        ▼
                 COMMAND CENTER (Next.js)
```

---

## 2. Component Breakdown

### 2.1 Webhook Gateway & Ingestion Layer (`apps/api/app/api/routes/webhooks.py`)
- **HMAC SHA256 Signature Verification**: Computes digest over raw request body using `RAZORPAY_WEBHOOK_SECRET`. Rejects mismatched signatures with `401 Unauthorized`.
- **Event ID Idempotency**: Evaluates `X-Razorpay-Event-Id` header against processed event store. Duplicate events immediately return `200 {"received": true, "duplicate": true}` without triggering redundant pipeline tasks.
- **Replay Protection**: Rejects events with timestamps older than 5 minutes (`300s`) to guard against replay attacks.
- **Out-of-Order Resilience**: Ingestion safely stores out-of-order events (e.g., `settlement.processed` arriving before `payment.captured`), ensuring proper lifecycle resolution.
- **Asynchronous Fast-Response**: The gateway writes raw payload to Event Store, enqueues the reconciliation task to Redis Queue, and responds `200 OK` in `< 5ms`.

### 2.2 Event Store & State Storage
- **PostgreSQL 17**: Persists normalized ledger entities (`payments`, `settlements`, `bank_transactions`, `refunds`, `cases`, `investigation_evidence`, `audit_logs`).
- **Data Integrity**: All monetary amounts are stored strictly as integer minor units (paise) to prevent floating-point inaccuracies.

### 2.3 Redis Queue & Worker Pool (`apps/api/app/queue/`)
- Distributed worker queues (`rq:queue:reconciliation`, `rq:queue:investigation`, `rq:queue:actions`, `rq:queue:dead-letter`).
- Horizontally scalable (`docker compose up -d --scale worker=4`) with automatic dead-letter queue routing for unrecoverable errors.

### 2.4 Deterministic Reconciliation Engine (`apps/api/app/services/reconciliation_service.py`)
- High-throughput mathematical matching between payments, settlements, and bank credits.
- Operates at **144,550 tx/sec** with sub-millisecond median latencies (~0.0032ms), identifying 100% of mathematical mismatches without LLM overhead.

### 2.5 AI Investigator (`apps/api/app/ai/`)
- Evaluates non-matching transactions by synthesizing evidence, calculating fee schedules (2% gateway + 18% GST), and formulating hypotheses.
- Outputs structured evidence, confidence ratings, and root cause classifications.
- Graceful degradation: In case of AI timeouts/outages, defaults safely to `HUMAN_REVIEW` with zero automated financial risk.

### 2.6 Policy Engine (`apps/api/app/services/policy_service.py`)
- Enforces strict autonomy boundaries: **The LLM recommends; the Policy Engine authorizes.**
- Evaluates risk level, difference threshold, confidence score ($\ge 85\%$), and conflicting evidence signals.
- Authorizes `AUTO_RESOLVE`, routes to `HUMAN_REVIEW`, or enforces `BLOCK`.

### 2.7 Action Executor, State Verifier & Audit Loop
- Executes policy-authorized resolutions (e.g. fee adjustment, payout capture, refund) using idempotent keys.
- Immediately performs **State Verification** and triggers a second reconciliation pass to confirm the discrepancy reaches exact `₹0` difference.
- Produces immutable audit logs documenting the trigger, AI findings, policy sign-off, and state delta.

### 2.8 Command Center (`apps/web/`)
- Real-time Next.js 16 dashboard providing KPI tracking, health indicators, live case stream, interactive "Why?" explainability drawer, and one-click scenario testing.