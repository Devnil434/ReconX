import { api } from "./client";

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
  const response = await api.get("/investigations");
  return response.data;
}

export async function runInvestigation(caseId: string) {
  const response = await api.post(`/investigations/${caseId}/run`);
  return response.data;
}

export async function getInvestigation(caseId: string) {
  const response = await api.get(`/investigations/${caseId}`);
  return response.data;
}
