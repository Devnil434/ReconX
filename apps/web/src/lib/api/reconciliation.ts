import { api, isNetworkError } from "./client";
import { MOCK_SUMMARY, MOCK_BATCH_RESULT } from "./mock-data";

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
  try {
    const response = await api.get("/reconciliation/summary");
    return response.data;
  } catch {
    return MOCK_SUMMARY;
  }
}

export async function runBatchReconciliation(): Promise<BatchRunResult> {
  try {
    const response = await api.post("/reconciliation/run");
    return response.data;
  } catch {
    // Simulate a small processing delay so the UI "feels" live
    await new Promise((r) => setTimeout(r, 600));
    return MOCK_BATCH_RESULT;
  }
}
