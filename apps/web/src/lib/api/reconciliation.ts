import { api } from "./client";

export interface ReconciliationSummary {
  total: number;
  matched: number;
  exceptions: number;
  match_rate: number;
}

export interface BatchRunResult {
  total: number;
  matched: number;
  exceptions: number;
  match_rate: number;
  elapsed_seconds: number;
  transactions_per_second: number;
}

export async function getReconciliationSummary(): Promise<ReconciliationSummary> {
  const response = await api.get("/reconciliation/summary");
  return response.data;
}

export async function runBatchReconciliation(): Promise<BatchRunResult> {
  const response = await api.post("/reconciliation/run");
  return response.data;
}
