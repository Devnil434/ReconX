# Standard Operating Procedure: Settlement Delay & Missing Bank Credits

## Objective
Define the workflow for handling payments that are captured or settled by the gateway but have not yet reflected in bank credit files.

## Policy Rules
1. **Settlement SLA**: Standard T+1 to T+3 business days.
2. **Missing Bank Credit**:
   - If payment age $< 3$ business days: Mark as `timing_difference` (Pending Settlement).
   - If payment age $\ge 3$ business days: Escalate to `HUMAN_REVIEW` with action `CONTACT_BANK_SUPPORT`.
3. **No Settlement from Gateway**:
   - If payment is `captured` but no `settlement_id` exists past T+2, flag as `gateway_unsettled`.
