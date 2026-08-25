import { api } from "./client";

export async function runInvestigation(caseId: string) {
  const response = await api.post(`/investigations/${caseId}/run`);
  return response.data;
}

export async function getInvestigation(caseId: string) {
  const response = await api.get(`/investigations/${caseId}`);
  return response.data;
}
