# Threat Model

This document outlines the primary security and operational threats to autonomous payment reconciliation systems and the specific mitigations enforced by ReconX.

---

## Threat Matrix

| Threat ID | Threat Scenario | Impact | Mitigation Mechanism |
|---|---|---|---|
| **T-01** | **Fake / Spoofed Webhook** | Unauthorized ledger mutation or case creation | **HMAC-SHA256 Signature Verification** using raw request payload and secret key (`RAZORPAY_WEBHOOK_SECRET`). Invalid signatures immediately rejected with `401`. |
| **T-02** | **Duplicate Webhook Delivery** | Double settlement, duplicate case creation | **Idempotent Ingestion**: `X-Razorpay-Event-Id` and `payment_id` deduplication via PostgreSQL uniqueness constraints and Redis locks. Returns `200 {"received": true, "duplicate": true}` without reprocessing. |
| **T-03** | **Replay Attack** | Malicious re-transmission of intercepted valid webhooks | **Timestamp Freshness Check**: Webhooks with `created_at` timestamps older than 5 minutes (300s) are automatically rejected. |
| **T-04** | **LLM Hallucination** | Incorrect root-cause attribution or invalid automated adjustment | **Dual-Engine Separation**: Reconciliation is 100% deterministic code. LLM output is constrained to structured evidence schema and must pass an independent deterministic Policy Engine. |
| **T-05** | **Unauthorized Financial Action** | AI taking autonomous financial actions without human oversight | **Bounded Autonomy Policy Engine**: High-risk, ambiguous, or non-zero residual difference cases are strictly blocked from auto-resolution and routed to `HUMAN_REVIEW`. |
| **T-06** | **Duplicate Action / Double Refund** | Network retry causing two payout or refund executions | **Action Idempotency Keys**: Every external action generates a deterministic `action_id` passed to Razorpay APIs. Re-executions return existing action status. |
| **T-07** | **Razorpay API Timeout** | Blind retry causing double debit or untracked state | **State Verification Loop**: Timeouts transition case to `UNKNOWN`, followed by an explicit state verification query before any further action is evaluated. |
| **T-08** | **AI Provider Outage / Timeout** | Pipeline failure or unhandled exception during surge | **Fail-Safe Degradation**: If the AI provider fails or times out, the system automatically tags the case for `HUMAN_REVIEW` with zero automated financial risk. |
| **T-09** | **Worker Pool Crash / Failure** | Unprocessed jobs lost in memory | **Persistent Redis Queue + Dead-Letter Queue (DLQ)**: Tasks remain persisted in Redis until acknowledged. Failed attempts retry with exponential backoff and route to DLQ on max retries. |
| **T-10** | **Out-of-Order Webhook Delivery** | Settlement arriving before payment capture event | **State-Aware Upsert**: Entity state models handle incomplete transitions gracefully without creating false discrepancy alarms. |

---

## Architectural Security Boundary

```
[ UNTRUSTED INTERNET ]
        │
        ▼  (HMAC SHA256 Verification + Event-ID Deduplication)
[ INGESTION GATEWAY ]
        │
        ▼  (Strict Paise Minor Units + SQL Parameterization)
[ EVENT STORE (Postgres) ]
        │
        ▼  (Deterministic Matching Only)
[ RECONCILIATION ENGINE ]
        │
        ▼  (Sandboxed Structured Prompting)
[ AI INVESTIGATOR ]
        │
        ▼  (Hardcoded Deterministic Rules & Thresholds)
[ POLICY ENGINE ]
        │
        ▼  (Idempotent API Calls + Post-Action Verification)
[ ACTION EXECUTOR ]
```
