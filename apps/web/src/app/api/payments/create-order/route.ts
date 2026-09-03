import { NextResponse } from "next/server";

const RAZORPAY_KEY_ID = process.env.RAZORPAY_KEY_ID || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_TUHiDLDs9QGDld";
const RAZORPAY_KEY_SECRET = process.env.RAZORPAY_KEY_SECRET || "XXMgpzs4oCikbdE4b2aqq9a6";
const RENDER_API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").split(",")[0] || "https://reconx-7aa4.onrender.com";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const amount = body.amount_paise || 50000;
    const currency = body.currency || "INR";

    // 1. First try Render backend so the backend registers the transaction
    try {
      const renderRes = await fetch(`${RENDER_API_BASE}/api/payments/create-order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(4000), // don't wait more than 4s for Render
      });

      if (renderRes.ok) {
        const renderData = await renderRes.json();
        // If Render returned a real Razorpay Order ID, return it!
        if (
          renderData.order_id &&
          renderData.order_id.startsWith("order_") &&
          !renderData.order_id.startsWith("order_mock_")
        ) {
          return NextResponse.json(renderData);
        }
      }
    } catch {
      // Render timed out or cold start — proceed to direct Razorpay API
    }

    // 2. Direct Razorpay Orders API fallback (guarantees real order_id in <300ms)
    const authHeader = `Basic ${Buffer.from(`${RAZORPAY_KEY_ID}:${RAZORPAY_KEY_SECRET}`).toString("base64")}`;
    const receipt = `rcx_${Date.now().toString(36)}`;

    const rzpRes = await fetch("https://api.razorpay.com/v1/orders", {
      method: "POST",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount,
        currency,
        receipt,
        notes: {
          merchant: "ReconX",
          source: "test-payment-simulator",
        },
      }),
    });

    if (!rzpRes.ok) {
      const errText = await rzpRes.text();
      return NextResponse.json(
        { error: `Razorpay Orders API error: ${errText}` },
        { status: 502 }
      );
    }

    const rzpOrder = await rzpRes.json();

    return NextResponse.json({
      order_id: rzpOrder.id,
      amount: rzpOrder.amount,
      currency: rzpOrder.currency,
      key_id: RAZORPAY_KEY_ID,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
