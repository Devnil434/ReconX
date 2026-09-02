import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 6000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Returns true when the error is a network/connection problem
 * (backend unreachable, CORS failure, timeout, etc.).
 * Used by every API module to trigger the offline demo fallback.
 */
export function isNetworkError(err: unknown): boolean {
  if (!axios.isAxiosError(err)) return false;
  // No response at all = network error or CORS preflight failure
  if (!err.response) return true;
  // 502 / 503 / 504 = gateway / server down
  const code = err.response.status;
  return code === 502 || code === 503 || code === 504;
}
