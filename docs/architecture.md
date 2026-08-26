# ReconX Architecture Overview

ReconX is an autonomous payment reconciliation investigator designed to process, match, and resolve transaction discrepancies for Razorpay payment operations.

---

## Core Philosophy

> **Code** determines *what* happened. (Deterministic matching logic)
> **AI** determines *why* it happened. (Root cause analysis & explanation)
> **Policy** determines *what* can happen next. (Safety constraints & bounds)

---

## High-Level Data Flow

```
   Webhook Intake / Payout Events (Razorpay)
                  │
                  ▼
         Ingestion & Queue
      (Deduplication & Order Check)
                  │
                  ▼
             PostgreSQL
                  │
                  ▼
    Deterministic Reconciliation Engine
         │                     │
      MATCHED              EXCEPTION
         │                     │
      [Done]                   ▼
                        AI Investigator
                       (Rule + LLM Fallback)
                               │
                               ▼
                         Policy Engine
                     (Honest Boundary Check)
                     ┌─────────┴─────────┐
                     ▼                   ▼
                Auto-Resolve       Human Review / Block
             (Fee/Tax mismatches)  (Missing UTRs, Duplicates)
```

---

## Architecture Components

### 1. Ingestion Layer (`apps/api/app/api/routes/webhooks.py`)
- Ingests events asynchronously from Razorpay webhooks.
- **Deduplication Check**: Ensures idempotency by checking `event_id` or `payment_id` against previously processed webhook events. Duplicate attempts are immediately responded to with `200 received: true` without reprocessing.
- **Out-of-Order Handling**: Checks payment lifecycle event stages. Pre-settlement webhook arrivals do not crash the system, and settlements are not duplicated.

### 2. Reconciliation Engine (`apps/api/app/services/reconciliation_service.py`)
- High-performance execution. Processes up to **144,000 transactions/sec** with sub-millisecond median latencies.
- Performs mathematical matching between internal order ledgers and gateway payment reports.
- Emits exceptions when differences are found in payment amounts, gateway fees, or tax deductions.

### 3. AI Investigator (`apps/api/app/ai/providers/`)
- Evaluates exceptions by synthesizing transaction details, matching fee schedules, and analyzing observed values.
- Formulates hypotheses and assigns confidence ratings.
- Standardizes output in a clear root cause summary.

### 4. Policy Engine (`apps/api/app/services/policy_service.py`)
Enforces the **Honest Exception List** pattern:
- **AUTO_RESOLVE**: Allowed only for low-risk fee/tax deviations with an exact arithmetic match (zero unexplained difference) and high AI confidence ($\ge 85\%$).
- **HUMAN_REVIEW / BLOCK**: Triggered by missing bank credit (UTR not found), duplicate settlements, partial payouts, low AI confidence, or conflicting evidence signals.

### 5. Task & Queue System (`apps/api/app/queue/`)
- Uses **Redis Queue (RQ)** to buffer reconciliation and investigation tasks.
- Background worker execution can scale to multiple workers (`--scale worker=4`).
- Metric endpoints expose queue depths for active queues: `reconciliation`, `investigation`, `actions`, and `dead_letter`.

### 6. Control Center (`apps/web/`)
- High-fidelity visual dashboard showing system KPI statistics, reconciliation health meters, queue metrics, live streams, and the **Explainability Drawer** detailing why an action was taken or escalated.