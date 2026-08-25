# Standard Operating Procedure: Manual Review & Escalation Policy

## Objective
Establish safety guardrails for transferring uncertain or high-risk reconciliation exceptions to human finance analysts.

## Policy Rules
1. **Uncertainty Principle**:
   - If evidence is incomplete or the difference is unexplained by fee/tax/refund formulas, the AI system must declare uncertainty and assign `HUMAN_REVIEW`.
2. **Confidence Threshold**:
   - Any investigation with confidence $< 0.95$ must never be auto-resolved.
3. **Audit Trail**:
   - All AI hypotheses, evidence citations, and confidence scores must be logged in `investigation_evidence` and `audit_logs` for human review.
