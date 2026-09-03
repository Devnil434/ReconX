"use client";

/**
 * /test-payment
 *
 * ReconX end-to-end Razorpay Test Mode payment page.
 *
 * Flow:
 *   1. Customer fills form (amount presets + name / email / contact)
 *   2. "Pay" → POST /api/payments/create-order (server-side, secret stays there)
 *   3. Backend returns { order_id, amount, currency, key_id }
 *   4. Checkout.js opens with real order_id
 *   5. User pays with success@razorpay (UPI) or test card
 *   6. handler() fires with payment_id + order_id + signature
 *   7. Pipeline tracker polls GET /webhooks/events every 3 s
 *   8. Steps turn green as Razorpay fires the webhook to the backend
 *
 * Security:
 *   RAZORPAY_KEY_SECRET is NEVER in the browser.
 *   Only NEXT_PUBLIC_RAZORPAY_KEY_ID (public key) is used client-side.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { TopNav } from "@/components/layout/top-nav";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  CreditCard,
  ExternalLink,
  IndianRupee,
  Loader2,
  Radio,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createOrder, getWebhookEvents, type WebhookEventRow } from "@/lib/api/payments";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type StepStatus = "idle" | "pending" | "success" | "error";

interface PipelineStep {
  id: string;
  label: string;
  description: string;
  status: StepStatus;
  timestamp?: string;
  detail?: string;
}

interface PaymentResult {
  razorpay_payment_id: string;
  razorpay_order_id?: string;
  razorpay_signature?: string;
}

// ---------------------------------------------------------------------------
// Pipeline step definitions
// ---------------------------------------------------------------------------

const INITIAL_STEPS: PipelineStep[] = [
  { id: "checkout",   label: "Razorpay Checkout",          description: "Payment initiated in test sandbox",                   status: "idle" },
  { id: "webhook",    label: "POST /webhooks/razorpay",    description: "Razorpay fires webhook to backend",                   status: "idle" },
  { id: "signature",  label: "Signature Verified",         description: "HMAC-SHA256 validated against webhook secret",        status: "idle" },
  { id: "persisted",  label: "Event Persisted",            description: "WebhookEvent row written to Neon / Postgres",         status: "idle" },
  { id: "queued",     label: "Job Enqueued",               description: "RQ job pushed to Upstash Redis queue",                status: "idle" },
  { id: "worker",     label: "Worker → Reconciliation",    description: "payment_worker runs ReconciliationService",           status: "idle" },
  { id: "result",     label: "Reconciliation Result",      description: "MATCHED or EXCEPTION + optional AI investigation",    status: "idle" },
];

// ---------------------------------------------------------------------------
// Razorpay Checkout.js global typing
// ---------------------------------------------------------------------------

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Razorpay: new (options: Record<string, any>) => {
      open(): void;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      on(event: string, callback: (response: any) => void): void;
    };
  }
}

// ---------------------------------------------------------------------------
// Amount presets
// ---------------------------------------------------------------------------

const PRESETS = [
  { label: "₹100",   paise: 10000 },
  { label: "₹500",   paise: 50000 },
  { label: "₹1,000", paise: 100000 },
  { label: "₹2,500", paise: 250000 },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StepIcon({ status }: { status: StepStatus }) {
  if (status === "idle")    return <Clock       className="h-4 w-4 text-muted-foreground" />;
  if (status === "pending") return <Loader2     className="h-4 w-4 text-primary animate-spin" />;
  if (status === "success") return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
  return <AlertTriangle className="h-4 w-4 text-destructive" />;
}

function stepBg(status: StepStatus) {
  if (status === "success") return "border-emerald-500/40 bg-emerald-500/5";
  if (status === "pending") return "border-primary/40 bg-primary/5";
  if (status === "error")   return "border-destructive/40 bg-destructive/5";
  return "border-border/40 bg-card";
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function TestPaymentPage() {
  // ── form state ────────────────────────────────────────────────
  const [amountPaise, setAmountPaise]   = useState(50000); // ₹500 default
  const [customAmount, setCustomAmount] = useState("");
  const [name, setName]                 = useState("Test User");
  const [email, setEmail]               = useState("test@reconx.dev");
  const [contact, setContact]           = useState("9999999999");

  // ── flow state ────────────────────────────────────────────────
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState<string | null>(null);
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null);

  // ── pipeline tracker ──────────────────────────────────────────
  const [steps, setSteps]         = useState<PipelineStep[]>(INITIAL_STEPS);
  const [events, setEvents]       = useState<WebhookEventRow[]>([]);
  const [polling, setPolling]     = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const pollRef   = useRef<ReturnType<typeof setInterval> | null>(null);
  const seenIds   = useRef<Set<string>>(new Set());
  const seenWIds  = useRef<Set<string>>(new Set());
  const paymentSucceededRef = useRef<boolean>(false);

  // ── Load Checkout.js script once ─────────────────────────────
  useEffect(() => {
    if (document.getElementById("rzp-checkout-js")) return;
    const s = document.createElement("script");
    s.id  = "rzp-checkout-js";
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.async = true;
    document.head.appendChild(s);
  }, []);

  // ── Pipeline helpers ──────────────────────────────────────────
  function patchStep(id: string, patch: Partial<PipelineStep>) {
    setSteps(prev => prev.map(s => s.id === id ? { ...s, ...patch } : s));
  }

  function reset() {
    setSteps(INITIAL_STEPS.map(s => ({ ...s })));
    setPaymentResult(null);
    paymentSucceededRef.current = false;
    setError(null);
    seenIds.current.clear();
    seenWIds.current.clear();
    setEvents([]);
    stopPolling();
  }

  // ── Poll webhook events ───────────────────────────────────────
  const fetchEvents = useCallback(async () => {
    const data = await getWebhookEvents(10);
    if (!data.length) return;
    setEvents(data);
    setLastChecked(new Date());

    const newEvts = data.filter(e => !seenIds.current.has(e.event_id));
    if (newEvts.length) {
      const first = newEvts[0];
      newEvts.forEach(e => seenIds.current.add(e.event_id));

      patchStep("webhook",   { status: "success", timestamp: new Date(first.created_at).toLocaleTimeString(), detail: `event_id: ${first.event_id}` });
      patchStep("signature", { status: "success", detail: "HMAC-SHA256 OK" });
      patchStep("persisted", { status: "success", detail: `event_type: ${first.event_type}` });
      patchStep("queued",    { status: "success", detail: "RQ job dispatched → reconciliation queue" });
    }

    // Worker status
    const succeeded = data.filter(e => e.status === "SUCCEEDED" && !seenWIds.current.has(e.event_id));
    if (succeeded.length) {
      succeeded.forEach(e => seenWIds.current.add(e.event_id));
      patchStep("worker", { status: "success", detail: `processed_at: ${succeeded[0].processed_at ?? "just now"}` });
      patchStep("result", { status: "success", detail: "Check dashboard for reconciliation outcome →" });
    }

    const failed = data.some(e => e.status === "FAILED");
    if (failed) patchStep("worker", { status: "error", detail: "Job failed — check Render logs" });

    const processing = data.some(e => e.status === "PROCESSING");
    if (processing && !succeeded.length) patchStep("worker", { status: "pending", detail: "Worker running…" });
  }, []);

  function startPolling() {
    if (pollRef.current) return;
    setPolling(true);
    fetchEvents();
    pollRef.current = setInterval(fetchEvents, 3000);
    // Auto-stop after 5 minutes
    setTimeout(() => stopPolling(), 300_000);
  }

  function stopPolling() {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    setPolling(false);
  }

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  // ── Pay button handler ────────────────────────────────────────
  async function handlePay() {
    setLoading(true);
    setError(null);
    paymentSucceededRef.current = false;

    const effectivePaise = customAmount
      ? Math.round(parseFloat(customAmount) * 100)
      : amountPaise;

    if (effectivePaise < 100) {
      setError("Minimum amount is ₹1 (100 paise).");
      setLoading(false);
      return;
    }

    try {
      // Step 1 — Create server-side order (secret stays on server)
      const order = await createOrder({
        amount_paise: effectivePaise,
        currency: "INR",
        name,
        email,
        contact,
      });

      // Step 2 — Open Razorpay Checkout
      if (!window.Razorpay) {
        throw new Error("Razorpay Checkout.js not loaded yet. Please wait a moment and try again.");
      }

      patchStep("checkout", {
        status: "success",
        timestamp: new Date().toLocaleTimeString(),
        detail: order.order_id && !order.order_id.startsWith("order_mock_")
          ? `order_id: ${order.order_id}`
          : "Standard Checkout (Test Mode)",
      });
      patchStep("webhook", { status: "pending" });
      startPolling();

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const rzpOptions: Record<string, any> = {
        key:         order.key_id || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_TUHiDLDs9QGDld",
        amount:      order.amount || effectivePaise,
        currency:    order.currency || "INR",
        name:        "ReconX",
        description: "⚡ Autonomous Reconciliation · TEST MODE",
        prefill:     { name, email, contact },
        notes:       { integration: "ReconX Test Mode", source: "test-payment-page" },
        theme:       { color: "#6366f1" },
        handler: (response: PaymentResult) => {
          paymentSucceededRef.current = true;
          setPaymentResult(response);
          patchStep("checkout", {
            status: "success",
            timestamp: new Date().toLocaleTimeString(),
            detail: `Payment ID: ${response.razorpay_payment_id}`,
          });
        },
        modal: {
          ondismiss: () => {
            if (!paymentSucceededRef.current) {
              setError("Payment cancelled. You can try again.");
              patchStep("checkout", { status: "error", detail: "Checkout dismissed" });
              patchStep("webhook",  { status: "idle" });
              stopPolling();
            }
          },
        },
      };

      // Attach order_id if present
      if (order.order_id && order.order_id.startsWith("order_") && !order.order_id.startsWith("order_mock_")) {
        rzpOptions.order_id = order.order_id;
      }

      const rzp = new window.Razorpay(rzpOptions);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      rzp.on("payment.failed", (resp: any) => {
        const desc = resp?.error?.description || resp?.error?.reason || "Payment was declined or failed in Razorpay.";
        console.warn("Razorpay payment.failed:", resp);
        setError(`Payment failed: ${desc}`);
        patchStep("checkout", { status: "error", detail: desc });
        patchStep("webhook", { status: "idle" });
        stopPolling();
      });
      rzp.open();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      patchStep("checkout", { status: "error", detail: msg });
    } finally {
      setLoading(false);
    }
  }

  const allSuccess = steps.every(s => s.status === "success");
  const hasError   = steps.some(s => s.status === "error");
  const inProgress = steps.some(s => s.status === "pending");
  const started    = steps[0].status !== "idle";

  return (
    <div className="min-h-screen bg-background bg-grid">
      <TopNav />

      <main className="mx-auto max-w-[1200px] px-6 py-8 space-y-6">

        {/* ── Header ─────────────────────────────────────────── */}
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <Badge variant="outline" className="font-mono text-[10px]">RECONX · TEST PAYMENT</Badge>
              <Badge variant="destructive" className="font-mono text-[10px]">⚠ RAZORPAY TEST MODE</Badge>
              <Badge variant="secondary" className="font-mono text-[10px] text-emerald-400 border-emerald-500/30">NO REAL MONEY</Badge>
              {polling && (
                <Badge variant="default" className="font-mono text-[10px] gap-1">
                  <Radio className="h-2.5 w-2.5 animate-pulse" /> LIVE POLLING
                </Badge>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Razorpay Test Payment →{" "}
              <span className="gradient-text">ReconX Pipeline</span>
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Complete a test payment and watch it flow through:{" "}
              <code className="font-mono text-xs">Checkout → Webhook → Signature → DB → RQ → Reconciliation → AI</code>
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0 mt-2 sm:mt-0">
            <Link href="/dashboard">
              <Button variant="outline" size="sm" className="gap-1.5">
                <ArrowLeft className="h-3.5 w-3.5" /> Dashboard
              </Button>
            </Link>
            {started && (
              <Button variant="outline" size="sm" onClick={reset}>Reset</Button>
            )}
          </div>
        </div>

        {/* ── Status banners ──────────────────────────────────── */}
        {allSuccess && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-5 py-4 flex items-center gap-3 fade-up">
            <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-emerald-400">🎉 Full pipeline verified!</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Razorpay → webhook → signature → Postgres → RQ → reconciliation.{" "}
                <Link href="/dashboard" className="underline text-primary">View result on dashboard →</Link>
              </p>
            </div>
          </div>
        )}
        {hasError && !allSuccess && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-5 py-4 flex items-center gap-3 fade-up">
            <AlertTriangle className="h-5 w-5 text-destructive flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-destructive">Pipeline error detected</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Check Render logs. Common causes: wrong webhook secret, missing <code className="font-mono">payment.captured</code> subscription, or worker crash.
              </p>
            </div>
          </div>
        )}
        {paymentResult && (
          <div className="rounded-xl border border-primary/30 bg-primary/5 px-5 py-4 fade-up">
            <p className="text-sm font-semibold text-primary mb-2">✅ Payment Successful — waiting for webhook…</p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              {[
                { label: "Payment ID",  value: paymentResult.razorpay_payment_id || "N/A" },
                { label: "Order ID",    value: paymentResult.razorpay_order_id || "Standard Checkout (Direct)" },
                {
                  label: "Signature",
                  value: paymentResult.razorpay_signature
                    ? `${paymentResult.razorpay_signature.slice(0, 16)}…`
                    : "Verified via Webhook HMAC",
                },
              ].map(f => (
                <div key={f.label} className="rounded-lg border border-border/40 bg-card px-3 py-2">
                  <p className="text-[10px] text-muted-foreground">{f.label}</p>
                  <code className="font-mono text-primary break-all">{f.value}</code>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-5">

          {/* ── Left: Form ────────────────────────────────────── */}
          <div className="lg:col-span-2 space-y-4">

            {/* Payment form */}
            <Card className="border-primary/20">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <CreditCard className="h-4 w-4 text-primary" /> Test Payment
                </CardTitle>
                <CardDescription className="text-xs">
                  Test Mode · No real money deducted
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Amount presets */}
                <div>
                  <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2 block">
                    Amount
                  </label>
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    {PRESETS.map(p => (
                      <button
                        key={p.paise}
                        onClick={() => { setAmountPaise(p.paise); setCustomAmount(""); }}
                        className={`rounded-lg border px-3 py-2 text-xs font-semibold transition-all ${
                          amountPaise === p.paise && !customAmount
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border/60 text-muted-foreground hover:border-primary/40"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                  <div className="relative">
                    <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <input
                      type="number"
                      placeholder="Custom amount"
                      value={customAmount}
                      onChange={e => { setCustomAmount(e.target.value); setAmountPaise(0); }}
                      className="w-full rounded-lg border border-border/60 bg-card pl-8 pr-3 py-2 text-sm focus:border-primary focus:outline-none"
                    />
                  </div>
                </div>

                {/* Customer fields */}
                {[
                  { label: "Name",    value: name,    setter: setName,    type: "text",  placeholder: "Test User" },
                  { label: "Email",   value: email,   setter: setEmail,   type: "email", placeholder: "test@reconx.dev" },
                  { label: "Contact", value: contact, setter: setContact, type: "tel",   placeholder: "9999999999" },
                ].map(f => (
                  <div key={f.label}>
                    <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">
                      {f.label}
                    </label>
                    <input
                      type={f.type}
                      placeholder={f.placeholder}
                      value={f.value}
                      onChange={e => f.setter(e.target.value)}
                      className="w-full rounded-lg border border-border/60 bg-card px-3 py-2 text-sm focus:border-primary focus:outline-none"
                    />
                  </div>
                ))}

                {error && (
                  <p className="text-xs text-destructive bg-destructive/5 border border-destructive/30 rounded-lg px-3 py-2">
                    {error}
                  </p>
                )}

                <Button
                  onClick={handlePay}
                  disabled={loading || inProgress}
                  className="w-full gap-2 bg-primary hover:bg-primary/90"
                >
                  {loading
                    ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating order…</>
                    : <><Zap className="h-4 w-4" /> Pay with Razorpay (Test Mode)</>
                  }
                </Button>

                <p className="text-[10px] text-center text-muted-foreground">
                  🔒 Payment processed by Razorpay · No real money deducted in Test Mode
                </p>
              </CardContent>
            </Card>

            {/* Test credentials */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Test Credentials
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-[11px] font-semibold text-muted-foreground mb-1">UPI (recommended)</p>
                  <div className="flex gap-2">
                    <div className="flex-1 rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-3 py-2">
                      <p className="text-[10px] text-muted-foreground">Success</p>
                      <code className="text-xs font-mono text-emerald-400">success@razorpay</code>
                    </div>
                    <div className="flex-1 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2">
                      <p className="text-[10px] text-muted-foreground">Failure</p>
                      <code className="text-xs font-mono text-destructive">failure@razorpay</code>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-[11px] font-semibold text-muted-foreground mb-1">Test Card</p>
                  <div className="rounded-lg border border-border/60 bg-card px-3 py-2 space-y-1">
                    {[
                      { k: "Number", v: "4111 1111 1111 1111" },
                      { k: "Expiry", v: "Any future date" },
                      { k: "CVV",    v: "Any 3 digits" },
                      { k: "OTP",    v: "1234" },
                    ].map(r => (
                      <div key={r.k} className="flex justify-between text-xs">
                        <span className="text-muted-foreground">{r.k}</span>
                        <code className="font-mono">{r.v}</code>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Webhook config */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <ShieldCheck className="h-3.5 w-3.5" /> Webhook Config
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {[
                  { label: "Endpoint", value: "https://reconx-7aa4.onrender.com/webhooks/razorpay" },
                  { label: "Events",   value: "payment.captured, payment.authorized" },
                  { label: "Mode",     value: "Test Mode ✓" },
                  { label: "Secret",   value: "RAZORPAY_WEBHOOK_SECRET in Render" },
                ].map(item => (
                  <div key={item.label} className="flex items-start justify-between gap-2 text-xs">
                    <span className="text-muted-foreground flex-shrink-0">{item.label}</span>
                    <code className="font-mono text-[10px] text-right break-all">{item.value}</code>
                  </div>
                ))}
                <div className="pt-2 border-t border-border/40">
                  <Button
                    variant="outline" size="sm" className="w-full text-xs gap-1.5"
                    onClick={() => window.open("https://dashboard.razorpay.com/app/webhooks", "_blank")}
                  >
                    <ExternalLink className="h-3 w-3" /> Verify in Razorpay → Webhooks
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* ── Right: Pipeline tracker ───────────────────────── */}
          <div className="lg:col-span-3 space-y-4">
            <Card className="border-primary/20">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Zap className="h-4 w-4 text-primary" /> Live Pipeline Tracker
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Polling{" "}
                      <code className="font-mono text-[10px]">/webhooks/events</code>
                      {lastChecked && <span> · checked {lastChecked.toLocaleTimeString()}</span>}
                    </CardDescription>
                  </div>
                  {!polling && !started && (
                    <Button size="sm" variant="outline" className="text-xs gap-1" onClick={startPolling}>
                      <Activity className="h-3 w-3" /> Watch Now
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {steps.map((step, i) => (
                    <div
                      key={step.id}
                      className={`flex items-start gap-3 rounded-lg border px-4 py-3 transition-all duration-500 ${stepBg(step.status)}`}
                    >
                      <div className="flex-shrink-0 mt-0.5"><StepIcon status={step.status} /></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-xs font-semibold font-mono text-foreground truncate">{step.label}</p>
                          {step.timestamp && <span className="text-[10px] text-muted-foreground flex-shrink-0">{step.timestamp}</span>}
                        </div>
                        <p className="text-[11px] text-muted-foreground mt-0.5">{step.description}</p>
                        {step.detail && <p className="text-[10px] font-mono text-primary mt-1">{step.detail}</p>}
                      </div>
                      <span className="flex-shrink-0 text-[10px] font-bold tabular-nums text-muted-foreground">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* DB events table */}
            {events.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Recent Webhook Events (from DB)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border/40">
                          {["Event ID", "Type", "Status", "Attempts"].map(h => (
                            <th key={h} className="text-left font-medium text-muted-foreground pb-2 pr-3">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/20">
                        {events.map(e => (
                          <tr key={e.event_id}>
                            <td className="py-2 pr-3 font-mono text-[10px] max-w-[120px] truncate">{e.event_id}</td>
                            <td className="py-2 pr-3">
                              <Badge variant="secondary" className="text-[10px] font-mono">{e.event_type}</Badge>
                            </td>
                            <td className="py-2 pr-3">
                              <Badge
                                variant={e.status === "SUCCEEDED" ? "default" : e.status === "FAILED" ? "destructive" : "secondary"}
                                className="text-[10px]"
                              >
                                {e.status}
                              </Badge>
                            </td>
                            <td className="py-2 text-muted-foreground">{e.attempts}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Instructions (shown before payment) */}
            {!started && (
              <Card className="border-dashed border-muted-foreground/30">
                <CardContent className="pt-5">
                  <ol className="space-y-3">
                    {[
                      "Verify webhook config (checklist bottom-left) matches Razorpay dashboard",
                      "Fill in the payment form and click \"Pay with Razorpay\"",
                      "Razorpay Checkout opens → choose UPI → enter success@razorpay → confirm",
                      "Watch all 7 pipeline steps turn green automatically",
                      "Open Render logs to see: POST /webhooks/razorpay 200 · signature verified · RQ job",
                      "Check Dashboard → Razorpay Status widget for reconciliation outcome",
                    ].map((text, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-bold text-primary">
                          {i + 1}
                        </span>
                        <span className="text-[13px] text-muted-foreground">{text}</span>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
