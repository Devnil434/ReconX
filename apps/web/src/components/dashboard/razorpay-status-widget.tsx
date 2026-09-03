"use client";

/**
 * RazorpayStatusWidget
 *
 * Dashboard panel showing the live Razorpay Test Mode integration status.
 * Polls GET /webhooks/events every 10 s.
 *
 * Displays:
 *   Connection:     CONNECTED (test) | NOT CONNECTED
 *   Latest payment: pay_xxx
 *   Latest event:   evt_xxx
 *   Webhook:        RECEIVED
 *   Signature:      VERIFIED (inferred from persistence)
 *   Processing:     QUEUED | PROCESSING | COMPLETE
 *   Reconciliation: MATCHED | EXCEPTION | PENDING
 *
 * Labels clearly distinguish:
 *   RAZORPAY TEST MODE  ← real Razorpay test transactions
 *   DEMO / SYNTHETIC    ← generated benchmark data
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  ExternalLink,
  Loader2,
  Radio,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getWebhookEvents, type WebhookEventRow } from "@/lib/api/payments";

// ---------------------------------------------------------------------------
// Helper components
// ---------------------------------------------------------------------------

function StatusDot({ ok, label }: { ok: boolean | null; label: string }) {
  if (ok === null)
    return (
      <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" /> {label}
      </span>
    );
  return (
    <span className={`flex items-center gap-1.5 text-xs ${ok ? "text-emerald-400" : "text-muted-foreground"}`}>
      {ok
        ? <CheckCircle2 className="h-3 w-3" />
        : <Clock className="h-3 w-3" />
      }
      {label}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
    SUCCEEDED: "default",
    FAILED:    "destructive",
    PROCESSING: "secondary",
    QUEUED:    "secondary",
  };
  return (
    <Badge variant={variantMap[status] ?? "outline"} className="text-[10px] font-mono">
      {status}
    </Badge>
  );
}

// ---------------------------------------------------------------------------
// Main widget
// ---------------------------------------------------------------------------

export function RazorpayStatusWidget() {
  const [events, setEvents]           = useState<WebhookEventRow[]>([]);
  const [connected, setConnected]     = useState<boolean | null>(null);
  const [lastFetch, setLastFetch]     = useState<Date | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchStatus = useCallback(async () => {
    const data = await getWebhookEvents(5);
    setConnected(true); // if fetch succeeded the backend is reachable
    setLastFetch(new Date());
    setEvents(data);
  }, []);

  useEffect(() => {
    fetchStatus();
    pollRef.current = setInterval(fetchStatus, 10_000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [fetchStatus]);

  const latest = events[0] ?? null;

  // Infer reconciliation status from event_type
  // payment.captured → payment worker → SUCCEEDED = reconciled
  const paymentEvents = events.filter(e =>
    e.event_type === "payment.captured" || e.event_type === "payment.authorized"
  );
  const latestPayment = paymentEvents[0] ?? null;

  const reconStatus =
    latestPayment?.status === "SUCCEEDED" ? "COMPLETE" :
    latestPayment?.status === "PROCESSING" ? "PROCESSING" :
    latestPayment?.status === "FAILED" ? "FAILED" :
    latestPayment ? "QUEUED" :
    "—";

  // Extract payment_id from event_type field (not available directly — show event_id as proxy)
  const latestEventId   = latest?.event_id   ?? "—";
  const latestEventType = latest?.event_type  ?? "—";

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Zap className="h-4 w-4 text-primary" />
            Razorpay Test Mode
          </CardTitle>
          <div className="flex items-center gap-2">
            {connected === null && <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />}
            {connected === true  && (
              <Badge variant="outline" className="text-[10px] gap-1 text-emerald-400 border-emerald-500/30">
                <Wifi className="h-2.5 w-2.5" /> CONNECTED
              </Badge>
            )}
            {connected === false && (
              <Badge variant="outline" className="text-[10px] gap-1 text-muted-foreground">
                <WifiOff className="h-2.5 w-2.5" /> NOT CONNECTED
              </Badge>
            )}
            <Badge variant="secondary" className="text-[10px] font-mono">TEST MODE</Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Status grid */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {[
            { label: "Webhook",        ok: !!latest,                             text: latest ? "RECEIVED"  : "—"         },
            { label: "Signature",      ok: !!latest,                             text: latest ? "VERIFIED"  : "—"         },
            { label: "DB Persisted",   ok: !!latest,                             text: latest ? "YES"       : "—"         },
            { label: "RQ Enqueued",    ok: !!latestPayment,                      text: latestPayment ? "YES" : "—"        },
            { label: "Processing",     ok: reconStatus === "COMPLETE",           text: reconStatus                         },
            { label: "Last Updated",   ok: !!lastFetch,                          text: lastFetch?.toLocaleTimeString() ?? "—" },
          ].map(item => (
            <div key={item.label} className="rounded-lg border border-border/40 bg-card px-3 py-2">
              <p className="text-[10px] text-muted-foreground mb-0.5">{item.label}</p>
              <StatusDot ok={item.ok ? true : null} label={item.text} />
            </div>
          ))}
        </div>

        {/* Latest event */}
        {latest && (
          <div className="rounded-lg border border-border/40 bg-card px-3 py-2 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground font-medium">Latest Event</span>
              <StatusBadge status={latest.status} />
            </div>
            <div className="flex items-start gap-2 text-[10px]">
              <span className="text-muted-foreground flex-shrink-0 w-14">event_id</span>
              <code className="font-mono text-primary truncate">{latestEventId}</code>
            </div>
            <div className="flex items-start gap-2 text-[10px]">
              <span className="text-muted-foreground flex-shrink-0 w-14">type</span>
              <code className="font-mono text-foreground">{latestEventType}</code>
            </div>
            <div className="flex items-start gap-2 text-[10px]">
              <span className="text-muted-foreground flex-shrink-0 w-14">attempts</span>
              <span className="font-mono">{latest.attempts}</span>
            </div>
          </div>
        )}

        {!latest && connected && (
          <div className="rounded-lg border border-dashed border-muted-foreground/30 px-3 py-4 text-center">
            <p className="text-xs text-muted-foreground">No webhook events yet.</p>
            <p className="text-[11px] text-muted-foreground mt-1">
              Make a test payment to see the live pipeline.
            </p>
          </div>
        )}

        {/* Polling indicator + link */}
        <div className="flex items-center justify-between pt-1">
          <span className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Radio className="h-2.5 w-2.5 animate-pulse text-primary" />
            Auto-refreshing every 10s
          </span>
          <Link href="/test-payment">
            <Button variant="outline" size="sm" className="h-6 text-[11px] gap-1 px-2">
              <ExternalLink className="h-2.5 w-2.5" /> Test Payment
            </Button>
          </Link>
        </div>

        {/* Distinction banner */}
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2">
          <p className="text-[10px] text-amber-400 font-semibold">
            ⚡ RAZORPAY TEST MODE &nbsp;·&nbsp; Real Razorpay transactions
          </p>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            Reconciliation KPIs above use <span className="text-foreground font-medium">DEMO / SYNTHETIC</span> data.
            This widget shows <span className="text-foreground font-medium">real Razorpay</span> test events.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
