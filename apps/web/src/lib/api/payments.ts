/**
 * payments.ts — frontend API client for the ReconX payments endpoints.
 *
 * createOrder()  → POST /api/payments/create-order
 *   Returns { order_id, amount, currency, key_id } for Checkout.js.
 *
 * getWebhookEvents() → GET /webhooks/events
 *   Returns recent WebhookEvent rows for the pipeline tracker.
 */

const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL ?? "").split(",")[0] ||
  "https://reconx-7aa4.onrender.com";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CreateOrderPayload {
  amount_paise: number;
  currency?: string;
  name?: string;
  email?: string;
  contact?: string;
}

export interface OrderDetails {
  order_id: string;
  amount: number;   // paise
  currency: string;
  key_id: string;   // public key only
}

export interface WebhookEventRow {
  event_id: string;
  event_type: string;
  status: string;
  attempts: number;
  created_at: string;
  processed_at: string | null;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function createOrder(
  payload: CreateOrderPayload
): Promise<OrderDetails> {
  // 1. In browser, try Vercel Serverless Function first (<200ms, guaranteed real order)
  if (typeof window !== "undefined") {
    try {
      const res = await fetch("/api/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const data = await res.json();
        if (
          data.order_id &&
          data.order_id.startsWith("order_") &&
          !data.order_id.startsWith("order_mock_")
        ) {
          return data as OrderDetails;
        }
      }
    } catch (err) {
      console.warn("Direct order endpoint failed, falling back to Render API:", err);
    }
  }

  // 2. Fallback to Render backend
  const renderEndpoint = `${API_BASE}/api/payments/create-order`;
  const resRender = await fetch(renderEndpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resRender.ok) {
    const detail = await resRender.text();
    throw new Error(`Order creation failed (${resRender.status}): ${detail}`);
  }

  return resRender.json() as Promise<OrderDetails>;
}

export async function getWebhookEvents(
  limit = 10
): Promise<WebhookEventRow[]> {
  try {
    const res = await fetch(`${API_BASE}/webhooks/events?limit=${limit}`);
    if (!res.ok) return [];
    return res.json() as Promise<WebhookEventRow[]>;
  } catch {
    return [];
  }
}
