# Standard Operating Procedure: Refund Reconciliation

## Objective
Govern the handling of instant and normal customer refunds against settled merchant funds.

## Policy Rules
1. **Deduction Matching**:
   - Processed refunds must be deducted from the subsequent batch settlement or account balance.
   - Formula: $\text{Net Expected} = \text{Gross} - \text{Fees} - \text{Taxes} - \text{Refunds}$.
2. **Double Deductions & Unlinked Refunds**:
   - If a refund is deducted without a corresponding customer refund request ID, flag as `unlinked_refund` $\rightarrow$ `BLOCK`.
