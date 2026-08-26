"use client";

import { use, useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock,
  Brain,
  DollarSign,
  ShieldCheck,
  ShieldOff,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { TopNav } from "@/components/layout/top-nav";
import { getInvestigation, runInvestigation } from "@/lib/api/investigations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Params { caseId: string }

function ConfidenceMeter({ value }: { value: number }) {
  const color =
    value >= 85 ? "bg-emerald-500" : value >= 60 ? "bg-amber-500" : "bg-destructive";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700`}
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
      <span className="w-12 text-right font-mono text-xs font-bold tabular-nums text-foreground">
        {value.toFixed(1)}%
      </span>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-border/60 bg-card p-6 fade-up">
      <h2 className="mb-4 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
        {title}
      </h2>
      {children}
    </section>
  );
}

const ACTION_STYLES = {
  AUTO_RESOLVE: { bg: "bg-emerald-500/15", text: "text-emerald-400", border: "border-emerald-500/30" },
  HUMAN_REVIEW: { bg: "bg-amber-500/15",   text: "text-amber-400",   border: "border-amber-500/30" },
  BLOCK:        { bg: "bg-destructive/15", text: "text-destructive", border: "border-destructive/30" },
};

export default function CaseDetailPage({ params }: { params: Promise<Params> }) {
  const { caseId } = use(params);

  const [caseData, setCaseData] = useState<any>(null);
  const [investigation, setInvestigation] = useState<any>(null);
  const [loadingCase, setLoadingCase] = useState(true);
  const [runningInv, setRunningInv] = useState(false);

  useEffect(() => {
    async function load() {
      setLoadingCase(true);
      try {
        const data = await getInvestigation(caseId);
        setCaseData(data);
      } finally {
        setLoadingCase(false);
      }
    }
    load();
  }, [caseId]);

  async function handleRunInvestigation() {
    setRunningInv(true);
    try {
      const inv = await runInvestigation(caseId);
      setInvestigation(inv);
      // refresh case data
      const updated = await getInvestigation(caseId);
      setCaseData(updated);
    } finally {
      setRunningInv(false);
    }
  }

  if (loadingCase) {
    return (
      <div className="min-h-screen bg-background bg-grid">
        <TopNav />
        <div className="flex items-center justify-center py-32">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  const inv = investigation ?? (caseData?.recommendation ? caseData : null);
  const action = (inv?.recommendation ?? "HUMAN_REVIEW") as keyof typeof ACTION_STYLES;
  const aStyle = ACTION_STYLES[action] ?? ACTION_STYLES.HUMAN_REVIEW;

  return (
    <div className="min-h-screen bg-background bg-grid">
      <TopNav />
      <main className="mx-auto max-w-[1100px] space-y-5 px-6 py-8">
        {/* Back + header */}
        <div>
          <Link
            href="/dashboard"
            className="mb-4 inline-flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Dashboard
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-1">
                Case Investigation
              </p>
              <h1 className="font-mono text-2xl font-bold text-foreground">{caseId}</h1>
              {caseData && (
                <div className="mt-2 flex items-center gap-2">
                  <Badge variant="secondary" className="capitalize text-[10px]">
                    {caseData.exception_type?.replace(/_/g, " ")}
                  </Badge>
                  <Badge variant="outline" className="text-[10px]">
                    {caseData.severity ?? "medium"}
                  </Badge>
                </div>
              )}
            </div>
            <Button
              onClick={handleRunInvestigation}
              disabled={runningInv}
              className="gap-1.5"
            >
              {runningInv ? (
                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Investigating…</>
              ) : (
                <><Brain className="h-3.5 w-3.5" /> Run AI Investigation</>
              )}
            </Button>
          </div>
        </div>

        {/* ── §6.36 Financial State ─────────────────── */}
        {caseData && (
          <Section title="§ Financial State">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {[
                { label: "Payment ID",          value: caseData.payment_id,                                         mono: true },
                { label: "Expected Amount",      value: `₹${(caseData.expected_amount / 100).toFixed(2)}`,          mono: true },
                { label: "Actual Amount",        value: `₹${(caseData.actual_amount / 100).toFixed(2)}`,            mono: true },
                { label: "Difference",           value: `₹${(Math.abs(caseData.difference) / 100).toFixed(2)}`,     mono: true, highlight: caseData.difference !== 0 },
                { label: "Status",               value: caseData.status,                                             mono: false },
                { label: "Created",              value: caseData.created_at ? new Date(caseData.created_at).toLocaleString() : "—", mono: false },
              ].map(({ label, value, mono, highlight }) => (
                <div
                  key={label}
                  className="rounded-lg border border-border/40 bg-background/60 p-3"
                >
                  <p className="text-[10px] text-muted-foreground">{label}</p>
                  <p
                    className={`mt-0.5 truncate text-sm font-bold ${
                      mono ? "font-mono" : ""
                    } ${highlight ? "text-destructive" : "text-foreground"}`}
                  >
                    {value ?? "—"}
                  </p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* ── §6.37 AI Investigation & Hypotheses ───── */}
        {inv ? (
          <Section title="§ AI Investigation & Hypotheses">
            <div className="space-y-4">
              {/* Root cause */}
              <div className="rounded-lg border border-border/40 bg-background/60 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[10px] text-muted-foreground">Root Cause</p>
                    <p className="mt-1 text-sm font-semibold text-foreground">
                      {inv.root_cause ?? "—"}
                    </p>
                  </div>
                  <div className={`rounded border px-2.5 py-1 text-[10px] font-bold ${aStyle.bg} ${aStyle.text} ${aStyle.border} flex-shrink-0`}>
                    {action}
                  </div>
                </div>
                {inv.confidence !== undefined && (
                  <div className="mt-3">
                    <p className="mb-1.5 text-[10px] text-muted-foreground">Confidence</p>
                    <ConfidenceMeter value={inv.confidence * 100} />
                  </div>
                )}
                {inv.summary && (
                  <p className="mt-3 text-[11px] leading-relaxed text-muted-foreground">
                    {inv.summary}
                  </p>
                )}
              </div>

              {/* Evidence chain */}
              {inv.evidence && inv.evidence.length > 0 && (
                <div>
                  <p className="mb-2 text-[11px] font-semibold text-muted-foreground">
                    Evidence Chain
                  </p>
                  <div className="space-y-1.5">
                    {inv.evidence.map((ev: any, i: number) => (
                      <div
                        key={i}
                        className="flex items-center gap-3 rounded-lg border border-border/40 bg-background/60 px-3 py-2.5"
                      >
                        {ev.verified !== false ? (
                          <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-400" />
                        ) : (
                          <XCircle className="h-4 w-4 flex-shrink-0 text-destructive" />
                        )}
                        <div className="flex flex-1 min-w-0 items-center justify-between gap-2">
                          <span className="text-xs capitalize text-muted-foreground truncate">
                            {ev.source_type ?? ev.field ?? "Evidence"}
                          </span>
                          <span className="font-mono text-xs font-semibold text-foreground">
                            {ev.source_id ?? ev.observed_value ?? ev.value ?? ""}
                          </span>
                        </div>
                        {ev.significance && (
                          <span className="text-[10px] text-muted-foreground hidden sm:block">
                            {ev.significance}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>
        ) : (
          <Section title="§ AI Investigation & Hypotheses">
            <div className="flex flex-col items-center justify-center py-10 gap-3 text-center">
              <Brain className="h-8 w-8 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                No investigation run yet.
              </p>
              <Button size="sm" onClick={handleRunInvestigation} disabled={runningInv}>
                {runningInv ? "Investigating…" : "Run Investigation Now"}
              </Button>
            </div>
          </Section>
        )}

        {/* ── §6.39 Policy Decision Explanation ────── */}
        <Section title="§ Policy Decision Explanation">
          {inv?.recommendation ? (
            <div className={`rounded-lg border p-5 ${aStyle.border} ${aStyle.bg}`}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-[10px] text-muted-foreground mb-1">Decision</p>
                  <p className={`text-2xl font-bold ${aStyle.text}`}>{action}</p>
                </div>
                {action === "AUTO_RESOLVE" ? (
                  <ShieldCheck className="h-8 w-8 text-emerald-400 mt-1" />
                ) : (
                  <ShieldOff className="h-8 w-8 text-destructive mt-1" />
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  {
                    label: "AI Confidence",
                    value: inv.confidence !== undefined ? `${(inv.confidence * 100).toFixed(1)}%` : "—",
                    ok: inv.confidence >= 0.85,
                  },
                  {
                    label: "Root Cause Identified",
                    value: inv.root_cause ? "YES" : "NO",
                    ok: !!inv.root_cause,
                  },
                  {
                    label: "Recommendation",
                    value: inv.recommendation,
                    ok: inv.recommendation === "AUTO_RESOLVE",
                  },
                  {
                    label: "Policy Allows Auto-Action",
                    value: inv.recommendation === "AUTO_RESOLVE" ? "YES" : "NO",
                    ok: inv.recommendation === "AUTO_RESOLVE",
                  },
                ].map(({ label, value, ok }) => (
                  <div key={label} className="rounded-lg bg-background/40 p-3">
                    <p className="text-[10px] text-muted-foreground">{label}</p>
                    <p className={`mt-0.5 text-sm font-bold ${ok ? "text-emerald-400" : "text-foreground"}`}>
                      {value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-6">
              Run an AI investigation first to see policy evaluation.
            </p>
          )}
        </Section>

        {/* ── §6.40 Execution Timeline ──────────────── */}
        <Section title="§ Execution Timeline">
          {caseData ? (
            <div className="relative border-l border-border/60 pl-5 space-y-4">
              {[
                { time: caseData.created_at ? new Date(caseData.created_at).toLocaleTimeString() : "—", event: "Exception detected & case created", done: true },
                { time: "—", event: "Queued for AI investigation", done: !!inv },
                { time: "—", event: `AI investigation completed (${inv ? `${(inv.confidence * 100).toFixed(1)}% confidence` : "pending"})`, done: !!inv },
                { time: "—", event: `Policy evaluated → ${inv?.recommendation ?? "pending"}`, done: !!inv?.recommendation },
                { time: "—", event: caseData.status === "resolved" ? "Auto-resolved ✓" : "Awaiting resolution", done: caseData.status === "resolved" },
              ].map((ev, i) => (
                <div key={i} className="relative">
                  <span
                    className={`absolute -left-[21px] top-0.5 h-3 w-3 rounded-full border-2 ${
                      ev.done
                        ? "border-primary bg-primary/50"
                        : "border-border/60 bg-background"
                    }`}
                  />
                  <div className="flex items-start gap-2">
                    <Clock className="h-3 w-3 flex-shrink-0 mt-0.5 text-muted-foreground" />
                    <span className="font-mono text-[10px] text-muted-foreground w-16 flex-shrink-0">
                      {ev.time}
                    </span>
                    <span className={`text-xs ${ev.done ? "text-foreground" : "text-muted-foreground"}`}>
                      {ev.event}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-6">
              No case data loaded.
            </p>
          )}
        </Section>
      </main>
    </div>
  );
}
