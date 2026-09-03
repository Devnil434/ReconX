# ReconX — 5-Minute Pitch & Demo Script (Video Recording Edition)

> **Before you record:** Open these tabs and stage them in order:
> 1. `https://reconx-phi.vercel.app/dashboard`
> 2. `https://reconx-phi.vercel.app/test-payment`
> 3. Render logs at `https://dashboard.render.com` (optional cut-away)
>
> Use **1920×1080**, hide all browser extensions & bookmarks bar, browser fullscreen.
> Recommended recorder: **OBS Studio** or **Windows + G (Xbox Game Bar)**.

---

## Timing Overview

```
0:00 – 0:40 │ Problem Statement           (narration over dashboard cold-open)
0:40 – 1:20 │ Core Architecture Principle (keep dashboard, voice-over)
1:20 – 3:00 │ Live Razorpay E2E Payment   ← REAL RAZORPAY SANDBOX DEMO
3:00 – 4:00 │ Command Center Walkthrough  (5 scenarios + Why? drawer)
4:00 – 4:30 │ Webhook Hardening           (terminal/code cut-away)
4:30 – 5:00 │ Benchmarks + Wrap-Up
```

---

## SEGMENT 1 — Problem Statement (0:00 – 0:40)

**Screen:** Open `https://reconx-phi.vercel.app/dashboard` cold.
Let the KPI bar animate: **1,284 transactions · 97.1% match rate · 37 exceptions · 0.0% false auto-resolve.**

**Narration:**
> "Every merchant running at scale faces payment reconciliation mismatches —
> gateway fee variance, GST rounding, delayed bank credits, and duplicate batches.
> Finance teams spend hundreds of hours manually cross-checking spreadsheets,
> or write fragile scripts that risk double refunds.
>
> Introducing **ReconX** — an autonomous payment reconciliation command center
> built specifically for Razorpay payment operations."

---

## SEGMENT 2 — Core Architecture Principle (0:40 – 1:20)

**Screen:** Remain on dashboard. Scroll to the Reconciliation Health card.

**Narration:**
> "ReconX is built on a strict financial safety principle:
>
> **Code determines what happened.**
> **AI determines why it happened.**
> **Policy determines what can happen next.**
>
> Deterministic matching runs at over 144,000 transactions per second.
> When a discrepancy is found, Gemini AI diagnoses the root cause.
> And our policy engine ensures zero unauthorized autonomous actions."

---

## SEGMENT 3 — Live Razorpay End-to-End Payment Demo (1:20 – 3:00)

> **This is the centrepiece of the demo for judges.**
> This is a **genuine** Razorpay Test Mode sandbox payment flowing through
> the real ReconX reconciliation pipeline. No mocks, no fakes.

### Step 3.1 — Navigate to Test Payment page (1:20)

**Action:** Click **"Test Payment"** in the top navigation bar.
**Screen lands on:** `https://reconx-phi.vercel.app/test-payment`

**Narration:**
> "Let me show you a live end-to-end Razorpay Test Mode payment flowing through
> the entire ReconX pipeline — from checkout all the way to reconciliation."

---

### Step 3.2 — Explain the page (1:30)

**Action:** Gesture at the amount presets and test credentials card.

**Narration:**
> "This page uses Razorpay's official Checkout.js — not a custom payment form.
> Our backend creates a real Razorpay Order server-side using Test Mode API keys.
> The secret never reaches the browser."

---

### Step 3.3 — Initiate the payment (1:40)

**Action:**
1. Select **₹500** preset.
2. Click **"Pay with Razorpay (Test Mode)"**.

**Narration:**
> "Clicking Pay calls our backend — which creates a Razorpay Order and returns
> the order ID and public key. Razorpay's official Checkout modal is now opening."

---

### Step 3.4 — Complete payment inside Razorpay Checkout (1:55)

**Action inside the real Razorpay modal:**
1. Select **UPI**.
2. Enter UPI ID: `success@razorpay`
3. Click **Pay Now**.
4. Modal closes with confirmation.

**Narration:**
> "This is the real, official Razorpay Checkout — not a UI we built.
> We enter the test UPI ID `success@razorpay` that Razorpay provides for sandboxing.
> No real money is deducted. This is Razorpay's official Test Mode simulation."

---

### Step 3.5 — Watch the live pipeline tracker (2:20)

**Action:** Stay on the test-payment page and watch the 7 steps turn green.

Steps that will update automatically:
1. ✅ Razorpay Checkout
2. ✅ POST /webhooks/razorpay
3. ✅ Signature Verified (HMAC-SHA256)
4. ✅ Event Persisted (Neon PostgreSQL)
5. ✅ Job Enqueued (Upstash Redis / RQ)
6. ✅ Worker → Reconciliation
7. ✅ Reconciliation Result

**Narration:**
> "Razorpay's servers have fired a real webhook to our backend at
> `https://reconx-7aa4.onrender.com/webhooks/razorpay`.
>
> Our backend verifies the HMAC-SHA256 signature over the raw request body,
> deduplicates by Event ID, persists the event to Neon PostgreSQL,
> dispatches it to our Redis-backed RQ worker, and runs the reconciliation engine.
>
> If there's a discrepancy — our Gemini AI investigator activates automatically."

---

### Step 3.6 — Return to Dashboard (2:50)

**Action:** Click **Dashboard** in the nav. Scroll to the **Razorpay Test Mode** widget.

**Narration:**
> "Back on the Command Center — the live Razorpay Status widget confirms:
> event received, signature verified, persisted, and processed.
> That was a genuine Razorpay test transaction through our deployed pipeline."

---

## SEGMENT 4 — Command Center Scenarios (3:00 – 4:00)

**Screen:** Dashboard. Scroll to the 3-lane autonomous case board.

### Scenario 1 — Fee Mismatch → AUTO-RESOLVE (3:00)
**Action:** Click a case in the **AUTO-RESOLVE** lane → open **Why?** drawer.
> "₹10,000 - ₹200 - ₹36 = ₹9,764. Code determined the match.
> AI confidence 98.2%. Policy: **LOW RISK → AUTO-RESOLVE**."

### Scenario 2 — Missing UTR → HUMAN REVIEW (3:20)
**Action:** Click a case in the **HUMAN REVIEW** lane.
> "Missing bank UTR — residual difference exists.
> AI confidence only 62%. Policy enforces **HUMAN REVIEW**. Zero autonomous action."

### Scenario 3 — Duplicate Settlement → BLOCK (3:35)
**Action:** Click a case in the **BLOCKED** lane.
> "Duplicate settlement detected.
> Policy **BLOCKS** immediately — preventing any duplicate payout."

### Scenario 4 — AI Failure → Safe Degradation (3:50)
**Action:** Click a HUMAN REVIEW case with AI_FAILURE tag.
> "If AI is unavailable — zero automated action.
> Safe degradation to the human review queue. No financial decision is ever made blindly."

---

## SEGMENT 5 — Webhook Hardening (4:00 – 4:30)

**Screen:** Show `https://reconx-phi.vercel.app/system` or Render log screenshot.

**Narration:**
> "Behind every event in that pipeline:
>
> - **HMAC-SHA256** computed over the raw request body — not parsed JSON.
> - **Event ID deduplication** using `X-Razorpay-Event-Id` — retried webhooks never cause duplicate jobs.
> - **5-minute replay guard** — stale replayed events are rejected outright.
> - **Action idempotency keys** — preventing double refunds or double payouts."

---

## SEGMENT 6 — Benchmarks & Wrap-Up (4:30 – 5:00)

**Action:** Navigate to `https://reconx-phi.vercel.app/benchmark`.

**Narration:**
> "In rigorous testing across all exception scenarios:
>
> - **144,157 transactions per second** — sub-millisecond deterministic matching.
> - **97.1% match rate** with **0.0% false auto-resolution**.
> - **AI root-cause accuracy: 97.6%** across all evaluated cases.
>
> ReconX: the speed of deterministic code, the intelligence of AI,
> and the safety of policy-governed financial operations. Thank you."

---

## Pre-Recording Checklist

- [ ] Backend health check passes: `https://reconx-7aa4.onrender.com/health` → `{"status":"ok"}`
- [ ] Razorpay webhook configured: `https://reconx-7aa4.onrender.com/webhooks/razorpay`
- [ ] Razorpay dashboard shows **Test Mode** (not Live)
- [ ] `payment.captured` and `payment.authorized` events subscribed in Razorpay Webhooks
- [ ] Browser at 1920×1080, dark mode, no browser extensions visible
- [ ] Recording software started **before** navigating to the dashboard
- [ ] Complete a **dry run first** — Razorpay modal takes ~3-5s to open
- [ ] Render backend warmed up — cold starts take ~20s

## Quick Warm-Up (Run before hitting Record)

```powershell
# Wake up the Render backend before recording to avoid cold-start delay
Invoke-RestMethod -Uri "https://reconx-7aa4.onrender.com/health"
Invoke-RestMethod -Uri "https://reconx-7aa4.onrender.com/webhooks/events"
Write-Host "✅ Backend is warm. You may start recording now."
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
- **Visual**: Open the ReconX Dashboard (`https://reconx-phi.vercel.app/dashboard` or `http://localhost:3000/dashboard`).
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
