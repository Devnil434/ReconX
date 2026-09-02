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
  } catch (err) {
    if (isNetworkError(err)) return MOCK_CASES;
    throw err;
  }
}

export async function runInvestigation(caseId: string) {
  try {
    const response = await api.post(`/investigations/${caseId}/run`);
    return response.data;
  } catch (err) {
    if (isNetworkError(err)) {
      // Return a mock investigation result for the requested case
      const found = MOCK_CASES.find((c) => c.case_id === caseId);
      if (found) {
        return {
          case_id: found.case_id,
          status: found.status,
          root_cause: found.root_cause,
          confidence: found.confidence,
          recommendation: found.recommendation,
          summary: found.root_cause,
          evidence: [],
          hypotheses: [],
        };
      }
    }
    throw err;
  }
}

export async function getInvestigation(caseId: string) {
  try {
    const response = await api.get(`/investigations/${caseId}`);
    return response.data;
  } catch (err) {
    if (isNetworkError(err)) {
      const found = MOCK_CASES.find((c) => c.case_id === caseId);
      if (found) {
        return {
          case_id: found.case_id,
          status: found.status,
          root_cause: found.root_cause,
          confidence: found.confidence,
          recommendation: found.recommendation,
          summary: found.root_cause,
          evidence: [],
          hypotheses: [],
        };
      }
    }
    throw err;
  }
}
