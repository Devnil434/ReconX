import { api, isNetworkError } from "./client";
import { MOCK_DEMO_SCENARIOS } from "./mock-data";

export interface DemoFinancialState {
  payment_amount: number;
  fee: number;
  tax: number;
  expected_settlement: number;
  actual_settlement: number;
  bank_credit: number;
  difference: number;
}

export interface DemoHypothesis {
  cause: string;
  confidence: number;
}

export interface DemoEvidence {
  field: string;
  value: string;
  verified: boolean;
}

export interface DemoPolicyDecision {
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  difference_zero: boolean;
  unresolved_questions: number;
  action: "AUTO_RESOLVE" | "HUMAN_REVIEW" | "BLOCK";
  allowed: boolean;
}

export interface DemoTimelineEvent {
  time: string;
  event: string;
}

export interface DemoScenarioResult {
  case_id: string;
  scenario: string;
  financial_state: DemoFinancialState;
  ai_investigation: {
    root_cause: string;
    confidence: number;
    hypotheses: DemoHypothesis[];
    summary: string;
  };
  evidence: DemoEvidence[];
  policy_decision: DemoPolicyDecision;
  status: string;
  timeline: DemoTimelineEvent[];
}

export type DemoScenario =
  | "fee-mismatch"
  | "missing-bank"
  | "duplicate-settlement"
  | "unknown"
  | "ai-failure";

export async function triggerDemoScenario(
  scenario: DemoScenario
): Promise<DemoScenarioResult> {
  try {
    const res = await api.post(`/demo/scenarios/${scenario}`);
    return res.data;
  } catch {
    return MOCK_DEMO_SCENARIOS[scenario];
  }
}
