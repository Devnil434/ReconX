# ReconX — 5-Minute Pitch & Demo Script (Video Recording Edition)

> **Before you record — 3-step setup:**
> 1. Run the warm-up command below to wake the Render backend.
> 2. Open these tabs in order and keep them ready:
>    - Tab 1: `https://reconx-phi.vercel.app/dashboard`
>    - Tab 2: `https://reconx-phi.vercel.app/test-payment`
>    - Tab 3: `https://reconx-phi.vercel.app/benchmark`
> 3. Set browser to **1920×1080, dark mode, fullscreen**, hide bookmarks bar & extensions.
>
> Recommended recorder: **OBS Studio** (window capture) or **Windows + Alt + R** (Xbox Game Bar).

---

## Quick Warm-Up (run this before hitting Record)

```powershell
# Wake up the Render backend to avoid cold-start lag during the demo
Invoke-RestMethod -Uri "https://reconx-7aa4.onrender.com/health"
# Confirm: status → ok

# Confirm order creation returns a REAL Razorpay order_id (not order_mock_...)
Invoke-RestMethod -Uri "https://reconx-7aa4.onrender.com/api/payments/create-order" `
  -Method Post -ContentType "application/json" `
  -Body '{"amount_paise": 50000, "currency": "INR"}' | Select-Object order_id
# Confirm: order_id starts with "order_TX..."

Write-Host "✅ Backend is warm and Razorpay orders are live. Start recording."
```

---

## Timing Overview

```
0:00 – 0:40 │ The Problem                    (dashboard cold open)
0:40 – 1:20 │ Architecture Principle         (scroll + narration)
1:20 – 3:00 │ Live Razorpay Payment Demo     ← REAL SANDBOX TRANSACTION
3:00 – 4:00 │ Command Center — 4 Scenarios   (case board walkthrough)
4:00 – 4:30 │ Webhook Security               (/system page)
4:30 – 5:00 │ Benchmarks + Close             (/benchmark page)
```

---

## SEGMENT 1 — The Problem (0:00 – 0:40)

**Screen:** Navigate to Tab 1 — `https://reconx-phi.vercel.app/dashboard`

Let the KPI bar animate naturally:
**1,284 transactions · 97.1% match rate · 37 exceptions · 0.0% false auto-resolve**

**Narration:**
> "Every merchant running at scale faces the same hidden cost — payment reconciliation
> mismatches. Gateway fee variance, GST rounding, delayed bank credits, duplicate settlement
> batches. Finance teams spend hundreds of hours cross-checking spreadsheets,
> or write fragile scripts that risk double refunds.
>
> Introducing **ReconX** — an autonomous payment reconciliation command center
> built specifically for Razorpay payment operations."

---

## SEGMENT 2 — Core Architecture Principle (0:40 – 1:20)

**Screen:** Remain on dashboard. Slowly scroll down to show the 3-lane case board.

**Narration:**
> "ReconX is founded on a strict financial safety principle:
>
> **Code determines what happened.**
> **AI determines why it happened.**
> **Policy determines what can happen next.**
>
> Deterministic matching runs at over 144,000 transactions per second —
> with sub-millisecond P99 latency.
> When a discrepancy is found, Gemini AI diagnoses the root cause.
> And our policy engine ensures zero unauthorized autonomous actions."

---

## SEGMENT 3 — Live Razorpay End-to-End Payment Demo (1:20 – 3:00)

> ⚡ **The centrepiece of this demo.**
> What you are about to see is a **genuine** Razorpay Test Mode sandbox payment
> flowing through the live, deployed ReconX pipeline. No mocks. No fakes.

### Step 3.1 — Navigate to Test Payment (1:20 – 1:30)

**Action:** Click **"Test Payment"** in the top navigation bar.

**Narration:**
> "Let me show you a live, end-to-end Razorpay Test Mode payment — from
> the official checkout all the way through to reconciliation."

---

### Step 3.2 — Show the page & explain the architecture (1:30 – 1:45)

**Action:** Hover over the amount presets and the Test Credentials card.

**Narration:**
> "This page uses Razorpay's **official Checkout.js** — not a custom UI.
> When you click Pay, our FastAPI backend on Render calls Razorpay's Orders API
> and returns a real, server-side order ID. The API secret never reaches the browser."

---

### Step 3.3 — Initiate the payment (1:45 – 2:00)

**Action:**
1. Select the **₹500** preset.
2. Click **"Pay with Razorpay (Test Mode)"**.

**Narration:**
> "Clicking Pay creates a genuine Razorpay Order on the server — the Order ID
> beginning with `order_TX...` is passed to the checkout SDK.
> Razorpay's official modal is now opening."

---

### Step 3.4 — Complete payment in Razorpay modal (2:00 – 2:25)

**Action inside the official Razorpay Checkout modal:**
1. Select **UPI** as the payment method.
2. Enter UPI ID: `success@razorpay`
3. Click **Pay Now**.
4. Wait for the modal to close automatically with success.

**Narration:**
> "This is Razorpay's official Test Mode checkout — entirely their UI.
> We enter `success@razorpay` — the test UPI ID Razorpay provides for sandbox simulation.
> Zero real money is involved. This is Razorpay's official test environment."

---

### Step 3.5 — Watch the live 7-step pipeline tracker (2:25 – 2:55)

**Action:** Stay on the `/test-payment` page. Watch the steps turn green in real time.

| Step | What is Happening |
|------|-----------------|
| ✅ 1. Razorpay Checkout | Payment captured by Razorpay |
| ✅ 2. POST /webhooks/razorpay | Razorpay fires webhook to Render |
| ✅ 3. Signature Verified | HMAC-SHA256 validated over raw body |
| ✅ 4. Event Persisted | Row written to Neon PostgreSQL |
| ✅ 5. Job Enqueued | RQ job pushed to Upstash Redis |
| ✅ 6. Worker → Reconciliation | payment_worker runs matching engine |
| ✅ 7. Reconciliation Result | MATCHED or EXCEPTION logged |

**Narration:**
> "Razorpay's servers have just fired a real webhook to our deployed backend at
> `reconx-7aa4.onrender.com`.
>
> We verify the HMAC-SHA256 signature over the raw request body — not parsed JSON,
> which prevents payload tampering. The event is deduplicated by its Razorpay Event ID
> so retries never create duplicate jobs. It is then persisted to Neon PostgreSQL,
> dispatched to our Redis-backed RQ worker, and run through our reconciliation engine.
>
> If there is any discrepancy — our Gemini AI investigator activates automatically."

---

### Step 3.6 — Return to Dashboard & show Razorpay widget (2:55 – 3:00)

**Action:** Click **Dashboard** in the nav. Scroll to the **Razorpay Test Mode** status widget.

**Narration:**
> "Back on the Command Center — the live Razorpay widget confirms:
> event received, HMAC verified, persisted, processed.
> That was a genuine Razorpay transaction through our live reconciliation pipeline."

---

## SEGMENT 4 — Command Center: 4 Scenarios (3:00 – 4:00)

**Screen:** Dashboard. Scroll to the 3-lane autonomous case board.

### Scenario 1 — Fee Mismatch → AUTO-RESOLVE (3:00 – 3:18)

**Action:** Click a case in the **AUTO-RESOLVE** (green) lane → open **Why?** drawer.

**Narration:**
> "Fee mismatch: ₹10,000 minus ₹200 platform fee minus ₹36 GST equals ₹9,764 exactly.
> Code determined the match deterministically. AI confidence: **98.2%**. All evidence checks pass.
> Policy: **LOW RISK → AUTO-RESOLVE**. No human needed."

---

### Scenario 2 — Missing UTR → HUMAN REVIEW (3:18 – 3:35)

**Action:** Click a case in the **HUMAN REVIEW** (amber) lane.

**Narration:**
> "Missing bank UTR — the settlement amount has not appeared in the bank statement.
> A residual difference exists. AI confidence drops to 62%.
> Policy enforces **HUMAN REVIEW**. Zero autonomous financial action."

---

### Scenario 3 — Duplicate Settlement → BLOCK (3:35 – 3:50)

**Action:** Click a case in the **BLOCKED** (red) lane.

**Narration:**
> "Duplicate settlement batch detected.
> Our policy engine **BLOCKS** immediately — no payout is authorized.
> This is pure policy enforcement — not AI guesswork."

---

### Scenario 4 — AI Failure → Safe Degradation (3:50 – 4:00)

**Action:** Click a HUMAN REVIEW case tagged **AI_FAILURE**.

**Narration:**
> "If AI is unavailable — zero automated action.
> The system degrades safely to the human review queue.
> No financial decision is ever made on broken evidence."

---

## SEGMENT 5 — Webhook Security (4:00 – 4:30)

**Screen:** Navigate to `https://reconx-phi.vercel.app/system`

**Narration:**
> "Behind every event in that pipeline, four layers of security:
>
> - **HMAC-SHA256** computed over the raw request body — not parsed JSON —
>   so payload tampering is impossible.
> - **Event ID deduplication** via `X-Razorpay-Event-Id` — retried webhooks
>   never trigger duplicate reconciliation jobs.
> - **5-minute replay guard** — stale replayed events are rejected outright.
> - **Action idempotency keys** — preventing double refunds or double payouts,
>   even under network failure conditions."

---

## SEGMENT 6 — Benchmarks & Close (4:30 – 5:00)

**Screen:** Navigate to `https://reconx-phi.vercel.app/benchmark`

**Narration:**
> "In rigorous testing across all exception scenarios:
>
> - **144,157 transactions per second** — sub-millisecond deterministic matching.
> - **97.1% match rate** with **0.0% false auto-resolution** across every run.
> - **AI root-cause accuracy: 97.6%** — powered by Gemini.
>
> ReconX: the speed of deterministic code,
> the intelligence of AI,
> and the safety of policy-governed financial operations.
>
> Thank you."

---

## Pre-Recording Checklist

- [ ] Warm-up script ran — `health` returns `ok` and `order_id` starts with `order_TX...`
- [ ] Razorpay webhook in dashboard points to `https://reconx-7aa4.onrender.com/webhooks/razorpay`
- [ ] Razorpay dashboard shows **Test Mode** badge (top-right)
- [ ] `payment.captured` and `payment.authorized` events are subscribed
- [ ] Browser: 1920×1080, dark mode, bookmarks bar hidden, no extensions visible
- [ ] Recording software started **before** you open the dashboard tab
- [ ] Dry run completed — the Razorpay modal takes ~3–5s to open after clicking Pay
- [ ] All 3 tabs pre-opened in order: `/dashboard`, `/test-payment`, `/benchmark`
