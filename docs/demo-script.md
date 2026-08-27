# ReconX — 5-Minute Pitch & Live Demo Script

This script outlines the exact structure for the 5-minute buildathon pitch video and live walkthrough.

---

## Pitch Outline (5 Minutes)

```
0:00 - 0:45 | The Problem: The Hidden Cost of Broken Reconciliation
0:45 - 1:30 | Core Principle: Code Determines, AI Investigates, Policy Authorizes
1:30 - 3:00 | Live Interactive Demo: The 5 Scenarios & "Why?" Drawer
3:00 - 4:00 | Architecture & Razorpay Hardening (HMAC, Dedupe, Idempotency)
4:00 - 4:45 | Benchmarks & Financial Safety (144k tx/s, 0.0% False Auto-Resolve)
4:45 - 5:00 | Summary & Submission Wrap-up
```

---

## Detailed Minute-by-Minute Script

### Minute 1: Problem & Vision (0:00 – 0:45)
- **Visual**: Show Razorpay Test Mode transactions flowing into a ledger.
- **Narrative**:
  > "Every merchant running at scale faces payment reconciliation mismatches — gateway fee variance, GST changes, delayed bank credits, and duplicate batches. Today, finance teams spend hundreds of hours manually cross-checking spreadsheets, or worse, writing fragile scripts that risk double refunds.
  >
  > Introducing **ReconX** — an autonomous payment reconciliation investigator built specifically for Razorpay payment operations."

---

### Minute 2: The Core Principle & Architecture (0:45 – 1:30)
- **Visual**: Show the Architecture diagram in `docs/architecture.md`.
- **Narrative**:
  > "ReconX is founded on a fundamental safety principle:
  > **Code determines what happened.**
  > **AI determines why it happened.**
  > **Policy determines what can happen next.**
  >
  > Financial matching is 100% deterministic — sub-millisecond, handling over 144,000 transactions a second. When an exception occurs, our AI investigator diagnoses the root cause, and our policy engine ensures zero unauthorized actions."

---

### Minute 3: Live Command Center Walkthrough (1:30 – 3:00)
- **Visual**: Open the ReconX Dashboard (`http://localhost:3000/dashboard`).
- **Narrative & Actions**:
  1. **Show KPI Bar & Health Meters**:
     > "Here in our Command Center, we see 100,000 transactions processed with a 91.2% match rate. Crucially, our False Auto-Resolution rate is 0.0%."
  2. **Trigger Scenario 1 (Fee Mismatch - Auto-Resolve)**:
     - Click **Fee Mismatch** button.
     - Open the **Why?** drawer.
     - Point out: *Financial state (₹10,000 - ₹200 - ₹36 = ₹9,764), 98.2% AI confidence, Evidence checks (✓), and Policy approval (Low Risk).*
  3. **Trigger Scenario 2 (Missing Bank Credit - Human Review)**:
     - Click **Missing Bank Credit**.
     - Open **Why?** drawer.
     - Point out: *UTR not found in bank statement -> Residual difference exists -> Policy forces HUMAN REVIEW.*
  4. **Trigger Scenario 3 (Duplicate Settlement - Blocked)**:
     - Click **Duplicate Settlement**.
     - Show: *Policy engine immediately triggers a BLOCK to prevent duplicate payouts.*
  5. **Trigger Scenario 4 (AI Outage Fallback)**:
     - Click **AI Failure**.
     - Show: *Zero automated action. Safe degradation to manual queue.*

---

### Minute 4: Razorpay Hardening & Idempotency (3:00 – 4:00)
- **Visual**: Show code snippets or terminal logs for webhook handling.
- **Narrative**:
  > "We engineered ReconX according to strict Razorpay webhook standards:
  > - **HMAC-SHA256 verification** computed over raw request bodies.
  > - **Event ID deduplication** using `X-Razorpay-Event-Id` headers so retried webhooks never cause duplicate actions.
  > - **Out-of-order event resilience** so settlements arriving before captures don't cause false alarms.
  > - **Action idempotency keys** preventing double refunds or double payouts."

---

### Minute 5: Benchmarks & Submission Wrap-Up (4:00 – 5:00)
- **Visual**: Navigate to `/benchmark` and `/system` pages.
- **Narrative**:
  > "In rigorous testing on 100,000 transactions:
  > - We achieved **144,550 tx/s throughput** with **P99 latency under 0.01ms**.
  > - AI root-cause investigation reached **97.6% accuracy**.
  > - **False auto-resolution was 0.0%** across all evaluation runs.
  >
  > ReconX delivers the speed of deterministic code, the intelligence of AI, and the safety of policy-governed financial operations. Thank you!"
