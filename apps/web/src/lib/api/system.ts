import { api, isNetworkError } from "./client";
import { MOCK_SYSTEM_HEALTH, MOCK_QUEUE_STATS, MOCK_BENCHMARK } from "./mock-data";

export interface ServiceStatus {
  status: "healthy" | "unhealthy" | "degraded";
  type?: string;
  provider?: string;
  mode?: string;
  port?: number;
  count?: number;
}

export interface SystemHealth {
  status: "healthy" | "degraded" | "down";
  demo_mode: boolean;
  services: {
    api: ServiceStatus;
    database: ServiceStatus;
    redis: ServiceStatus;
    workers: ServiceStatus;
    ai_provider: ServiceStatus;
    razorpay: ServiceStatus;
  };
  queues: Record<string, number>;
  metrics: {
    total_transactions: number;
    exceptions_detected: number;
    ai_investigations: number;
    ai_calls_total: number;
    ai_tokens_input: number;
    ai_tokens_output: number;
    estimated_ai_cost_usd: number;
    ai_calls_per_tx_pct: number;
  };
}

export interface QueueStats {
  reconciliation: { queued: number; failed: number };
  investigation: { queued: number; failed: number };
  actions: { queued: number; failed: number };
  dead_letter: { queued: number };
}

export interface BenchmarkReport {
  dataset_size: number;
  throughput_tx_per_sec: number;
  execution_time_seconds: number;
  latencies_ms: {
    average: number;
    p50: number;
    p90: number;
    p95: number;
    p99: number;
  };
  reconciliation_outcomes: {
    matched: number;
    matched_pct: number;
    exceptions: number;
    exceptions_pct: number;
  };
  ai_evaluation: {
    evaluated_cases: number;
    false_auto_resolution_rate_pct: number;
    root_cause_accuracy_pct: number;
    action_recommendation_accuracy_pct: number;
    evidence_grounding_accuracy_pct: number;
    human_review_recall_pct: number;
    block_precision_pct: number;
    average_confidence_pct: number;
  };
  exception_taxonomy: Record<string, number>;
}

export async function getSystemHealth(): Promise<SystemHealth> {
  try {
    const res = await api.get("/system");
    return res.data;
  } catch {
    return MOCK_SYSTEM_HEALTH;
  }
}

export async function getQueueStats(): Promise<QueueStats> {
  try {
    const res = await api.get("/system/queues");
    return res.data;
  } catch {
    return MOCK_QUEUE_STATS;
  }
}

export async function getBenchmarkReport(): Promise<BenchmarkReport> {
  try {
    const res = await api.get("/benchmark");
    return res.data;
  } catch {
    return MOCK_BENCHMARK;
  }
}
