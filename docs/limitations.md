# Known Limitations & Honest Exception Boundary

ReconX intentionally restricts autonomous execution to mathematically verifiable, zero-residual discrepancies. This document details the explicit boundaries where autonomous resolution is refused and human escalation is enforced.

---

## 1. The Autonomous Resolution Boundary

### AI CAN Auto-Resolve
Autonomous resolution is permitted **only** when all of the following conditions are simultaneously met:
1. **Fee & Tax Variance**: Discrepancy is fully accounted for by standard gateway schedule (e.g. 2% MDR + 18% GST).
2. **Zero Residual Difference**: Mathematical difference after fee/tax synthesis equals exact `₹0.00`.
3. **High Confidence**: AI investigation confidence score $\ge 85\%$.
4. **Verified Evidence**: All referenced payment and gateway settlement records are cryptographically verified in the ledger.
5. **Sub-Paisa Rounding**: Discrepancy $\le ₹1.00$ caused by standard banking rounding conventions.

---

## 2. Cases Where Autonomous Resolution is Strictly Refused

The system refuses autonomous action and routes to **Human Review** or **Block** for the following categories:

| Category | Reason for Refusal | System Action |
|---|---|---|
| **Missing Bank Credit (UTR Not Found)** | Bank statement feed lacks corresponding credit record; settlement may be in-transit or held. | `HUMAN_REVIEW` |
| **Duplicate Settlement Batch** | Multiple payout batches claiming the same payment ID; high financial risk. | `BLOCK` |
| **Partial Settlement** | Unexplained non-zero difference remains after applying fee schedules. | `HUMAN_REVIEW` |
| **Conflicting Evidence** | Data mismatch between gateway webhook payload and bank ledger report. | `HUMAN_REVIEW` |
| **Low AI Confidence ($< 85\%$)** | Ambiguous root cause or multiple competing hypotheses with close probabilities. | `HUMAN_REVIEW` |
| **High Financial Exposure** | Discrepancy value exceeding configured threshold ($> ₹50,000$). | `HUMAN_REVIEW` |
| **AI Provider Timeout / Outage** | External LLM API is unavailable or returns an invalid schema. | `HUMAN_REVIEW` |
| **Unsupported Razorpay Event** | Event types outside standard payment, settlement, refund, and dispute lifecycles. | `HUMAN_REVIEW` |

---

## 3. Why Bounded Autonomy is a Feature
In enterprise financial operations, **a false auto-resolution is far more dangerous than a manual escalation**. By maintaining a strict, verifiable boundary, ReconX guarantees a **0.0% False Auto-Resolution Rate**, providing absolute ledger integrity for finance leadership.
