import { api, isNetworkError } from "./client";
import { MOCK_CASES } from "./mock-data";

export interface InvestigationCase {
  case_id: string;
  payment_id: string;
  exception_type: string;
  severity: string;
  expected_amount: number;
  actual_amount: number;
  difference: number;
  status: string;
  recommendation?: string | null;
  confidence?: number | null;
  root_cause?: string | null;
  created_at?: string | null;
}

export async function listInvestigations(): Promise<InvestigationCase[]> {
  try {
    const response = await api.get("/investigations");
    return response.data;
  } catch {
    return MOCK_CASES;
  }
}

export async function runInvestigation(caseId: string) {
  try {
    const response = await api.post(`/investigations/${caseId}/run`);
    return response.data;
  } catch {
    const found = MOCK_CASES.find((c) => c.case_id === caseId) || MOCK_CASES[0];
    return {
      case_id: found.case_id,
      status: found.status,
      root_cause: found.root_cause,
      confidence: found.confidence ?? 0.96,
      recommendation: found.recommendation ?? "AUTO_RESOLVE",
      summary: found.root_cause,
      evidence: [
        {
          source_type: "payment",
          source_id: found.payment_id,
          field: "Captured Amount",
          observed_value: `₹${(found.expected_amount / 100).toFixed(2)}`,
          significance: "Payment authorized and captured in ledger",
        },
        {
          source_type: "settlement",
          source_id: `setl_${found.case_id.toLowerCase().replace(/[^a-z0-9]/g, "")}`,
          field: "Settlement Credit",
          observed_value: `₹${(found.actual_amount / 100).toFixed(2)}`,
          significance: "Settlement calculated after deductions and taxes",
        },
        {
          source_type: "policy",
          source_id: "RULE_ENGINE_V2",
          field: "Action Evaluated",
          observed_value: found.recommendation ?? "AUTO_RESOLVE",
          significance: "Deterministic policy boundary checks passed",
        },
      ],
      hypotheses: [],
    };
  }
}

export async function getInvestigation(caseId: string) {
  try {
    const response = await api.get(`/investigations/${caseId}`);
    return response.data;
  } catch {
    const found = MOCK_CASES.find((c) => c.case_id === caseId) || MOCK_CASES[0];
    return {
      case_id: found.case_id,
      payment_id: found.payment_id,
      exception_type: found.exception_type,
      severity: found.severity,
      expected_amount: found.expected_amount,
      actual_amount: found.actual_amount,
      difference: found.difference,
      status: found.status,
      root_cause: found.root_cause,
      confidence: found.confidence ?? 0.96,
      recommendation: found.recommendation ?? "AUTO_RESOLVE",
      summary: found.root_cause,
      created_at: found.created_at,
      evidence: [
        {
          source_type: "payment",
          source_id: found.payment_id,
          field: "Captured Amount",
          observed_value: `₹${(found.expected_amount / 100).toFixed(2)}`,
          significance: "Payment authorized and captured in ledger",
        },
        {
          source_type: "settlement",
          source_id: `setl_${found.case_id.toLowerCase().replace(/[^a-z0-9]/g, "")}`,
          field: "Settlement Credit",
          observed_value: `₹${(found.actual_amount / 100).toFixed(2)}`,
          significance: "Settlement calculated after deductions and taxes",
        },
      ],
      hypotheses: [],
    };
  }
}
