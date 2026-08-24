# RecoverRecon Architecture

## Objective

RecoverRecon is an autonomous payment reconciliation
investigator for Razorpay payment operations.

## Core principle

> Code determines what happened.
> AI determines why it happened.
> Policy determines what can happen next.

## Architecture

Razorpay
    |
    v
Ingestion Layer
    |
    v
Normalization
    |
    v
PostgreSQL
    |
    v
Deterministic Reconciliation Engine
    |
    +------> MATCHED
    |
    +------> EXCEPTION
                |
                v
         AI Investigator
                |
                v
          Policy Engine
             /     \
            /       \
           v         v
      Auto Resolve  Human Review
            \       /
             \     /
              v   v
             Audit Log
                |
                v
         Control Center