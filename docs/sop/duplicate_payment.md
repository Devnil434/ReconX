# Standard Operating Procedure: Duplicate Payments & Double Settlements

## Objective
Detect and quarantine duplicate settlements, ghost credits, or repeated transaction records sharing the same UTR or payment ID.

## Policy Rules
1. **Duplicate Detection Criteria**:
   - Multiple settlement records referencing the same `payment_id` or identical `utr` with the same amount.
2. **Action Required**:
   - MUST recommend `BLOCK` immediately to prevent double ledger crediting.
   - Do NOT attempt autonomous resolution.
