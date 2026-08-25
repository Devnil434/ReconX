# Standard Operating Procedure: Fee & Tax Mismatches

## Objective
Establish deterministic procedures for identifying, validating, and resolving fee and tax discrepancies between payment capture and gateway settlement.

## Policy Rules
1. **Dynamic Gateway Fee Schedule**: Razorpay dynamic MDR fees and GST (18%) may adjust based on payment method (credit card, UPI, netbanking).
2. **Auto-Resolution Criteria**:
   - Discrepancy is fully accounted for by verified GST (18%) or contracted interchange fees.
   - Difference is $< \text{INR } 500$ and within acceptable variance tolerances.
   - UTR confirmation exists in the bank ledger.
3. **Escalation**:
   - Flag for `HUMAN_REVIEW` if fee exceeds contracted ceiling (>3.5%) or tax rate differs from 18%.
