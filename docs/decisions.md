# Architecture Decisions

## ADR-001: Deterministic reconciliation

Financial matching must be performed by deterministic code.

The LLM must never be the source of truth for:

- transaction amounts
- fees
- taxes
- settlement totals
- UTR matching
- date calculations

## ADR-002: AI investigation

The AI investigator is responsible for:

- root-cause analysis
- evidence synthesis
- exception classification
- explanation
- recommended action

## ADR-003: Bounded autonomy

The AI cannot directly execute arbitrary financial operations.

All actions pass through a policy engine.

## ADR-004: Auditability

Every investigation and autonomous action must produce
an immutable audit record.

## ADR-005: Money representation

All monetary values are represented as integer minor units
such as paise.