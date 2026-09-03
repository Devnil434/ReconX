// api/create-order.js — Vercel Serverless Function at repo root

module.exports = async function handler(req, res) {
  // CORS
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS,PATCH,DELETE,POST,PUT");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version"
  );

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const amount = Number(body.amount_paise) || 50000;
    const currency = body.currency || "INR";
    const keyId = process.env.RAZORPAY_KEY_ID || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_TUHiDLDs9QGDld";
    const keySecret = process.env.RAZORPAY_KEY_SECRET || "XXMgpzs4oCikbdE4b2aqq9a6";

    const auth = Buffer.from(`${keyId}:${keySecret}`).toString("base64");
    const receipt = `rcx_${Date.now().toString(36)}`;

    const rzpRes = await fetch("https://api.razorpay.com/v1/orders", {
      method: "POST",
      headers: {
        Authorization: `Basic ${auth}`,
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
      return res.status(502).json({ error: `Razorpay Orders API failed: ${errText}` });
    }

    const data = await rzpRes.json();
    return res.status(200).json({
      order_id: data.id,
      amount: data.amount,
      currency: data.currency,
      key_id: keyId,
    });
  } catch (err) {
    return res.status(500).json({ error: err.message || String(err) });
  }
};
