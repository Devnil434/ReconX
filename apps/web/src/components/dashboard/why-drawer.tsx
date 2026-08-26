"use client";

import { X, CheckCircle2, XCircle, ChevronRight } from "lucide-react";
import type { DemoScenarioResult } from "@/lib/api/demo";

interface WhydDrawerProps {
  result: DemoScenarioResult;
  open: boolean;
  onClose: () => void;
}

const actionStyle = {
  AUTO_RESOLVE: { bg: "bg-emerald-500/15", text: "text-emerald-400", border: "border-emerald-500/30" },
  HUMAN_REVIEW: { bg: "bg-amber-500/15", text: "text-amber-400", border: "border-amber-500/30" },
  BLOCK:        { bg: "bg-destructive/15", text: "text-destructive", border: "border-destructive/30" },
};

const riskStyle = {
  LOW:    { text: "text-emerald-400", bg: "bg-emerald-500/15" },
  MEDIUM: { text: "text-amber-400",   bg: "bg-amber-500/15" },
  HIGH:   { text: "text-destructive", bg: "bg-destructive/15" },
};

function ConfidenceMeter({ value }: { value: number }) {
  const color =
    value >= 85 ? "bg-emerald-500" : value >= 60 ? "bg-amber-500" : "bg-destructive";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="w-10 text-right font-mono text-xs font-bold tabular-nums text-foreground">
        {value.toFixed(1)}%
      </span>
    </div>
  );
}

export function WhydDrawer({ result, open, onClose }: WhydDrawerProps) {
  if (!open) return null;

  const action = result.policy_decision.action as keyof typeof actionStyle;
  const risk = result.policy_decision.risk_level as keyof typeof riskStyle;
  const aStyle = actionStyle[action] ?? actionStyle.HUMAN_REVIEW;
  const rStyle = riskStyle[risk] ?? riskStyle.HIGH;

  const fs = result.financial_state;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="drawer-enter fixed right-0 top-0 z-50 flex h-full w-full max-w-lg flex-col overflow-y-auto border-l border-border/60 bg-card shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-start justify-between border-b border-border/60 bg-card/95 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
              AI Investigation Results
            </p>
            <h2 className="mt-1 font-mono text-sm font-bold text-foreground">
              {result.case_id}
            </h2>
            <div className="mt-1.5 flex items-center gap-2">
              <span
                className={`rounded border px-2 py-0.5 text-[10px] font-bold ${aStyle.bg} ${aStyle.text} ${aStyle.border}`}
              >
                {action}
              </span>
              <span
                className={`rounded px-2 py-0.5 text-[10px] font-semibold ${rStyle.bg} ${rStyle.text}`}
              >
                {risk} RISK
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="ml-4 flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 space-y-6 p-6">
          {/* Financial State */}
          <section>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
              Financial State
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: "Payment Amount", value: `₹${(fs.payment_amount / 100).toFixed(2)}`, highlight: false },
                { label: "Gateway Fee",    value: `₹${(fs.fee / 100).toFixed(2)}`,            highlight: false },
                { label: "GST",            value: `₹${(fs.tax / 100).toFixed(2)}`,            highlight: false },
                { label: "Expected Settlement", value: `₹${(fs.expected_settlement / 100).toFixed(2)}`, highlight: false },
                { label: "Actual Settlement",   value: `₹${(fs.actual_settlement / 100).toFixed(2)}`,   highlight: false },
                { label: "Difference",     value: `₹${(Math.abs(fs.difference) / 100).toFixed(2)}`,
                  highlight: fs.difference !== 0 },
              ].map(({ label, value, highlight }) => (
                <div key={label} className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <p className="text-[10px] text-muted-foreground">{label}</p>
                  <p className={`mt-0.5 font-mono text-sm font-bold ${highlight ? "text-destructive" : "text-foreground"}`}>
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Root Cause & Confidence */}
          <section>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
              Root Cause Analysis
            </h3>
            <div className="rounded-lg border border-border/40 bg-background/50 p-4 space-y-3">
              <div>
                <p className="text-[10px] text-muted-foreground">Root Cause</p>
                <p className="mt-1 text-sm font-semibold text-foreground">
                  {result.ai_investigation.root_cause}
                </p>
              </div>
              <div>
                <p className="mb-1.5 text-[10px] text-muted-foreground">AI Confidence</p>
                <ConfidenceMeter value={result.ai_investigation.confidence} />
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                {result.ai_investigation.summary}
              </p>
            </div>
          </section>

          {/* Competing Hypotheses */}
          {result.ai_investigation.hypotheses.length > 0 && (
            <section>
              <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                Competing Hypotheses
              </h3>
              <div className="space-y-2">
                {result.ai_investigation.hypotheses.map((h, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 rounded-lg border border-border/40 bg-background/50 p-3"
                  >
                    <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-bold text-muted-foreground">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-foreground truncate">{h.cause}</p>
                      <div className="mt-1">
                        <ConfidenceMeter value={h.confidence} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Evidence Checklist */}
          {result.evidence.length > 0 && (
            <section>
              <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                Evidence Checklist
              </h3>
              <div className="space-y-1.5">
                {result.evidence.map((ev, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 rounded-lg border border-border/40 bg-background/50 p-3"
                  >
                    {ev.verified ? (
                      <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-400" />
                    ) : (
                      <XCircle className="h-4 w-4 flex-shrink-0 text-destructive" />
                    )}
                    <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
                      <span className="text-xs text-muted-foreground truncate">{ev.field}</span>
                      <span className={`font-mono text-xs font-semibold ${ev.verified ? "text-foreground" : "text-destructive"}`}>
                        {ev.value}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Policy Decision */}
          <section>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
              Policy Decision
            </h3>
            <div className={`rounded-lg border ${aStyle.border} ${aStyle.bg} p-4 space-y-2`}>
              <div className="flex items-center justify-between">
                <span className={`text-sm font-bold ${aStyle.text}`}>{action}</span>
                <span className={`text-[10px] font-semibold ${rStyle.text}`}>
                  {risk} RISK
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <p className="text-[10px] text-muted-foreground">Difference Zero</p>
                  <p className={`text-xs font-bold ${result.policy_decision.difference_zero ? "text-emerald-400" : "text-destructive"}`}>
                    {result.policy_decision.difference_zero ? "YES ✓" : "NO ✕"}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground">Unresolved Questions</p>
                  <p className={`text-xs font-bold ${result.policy_decision.unresolved_questions === 0 ? "text-emerald-400" : "text-destructive"}`}>
                    {result.policy_decision.unresolved_questions}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground">Auto-Action Allowed</p>
                  <p className={`text-xs font-bold ${result.policy_decision.allowed ? "text-emerald-400" : "text-destructive"}`}>
                    {result.policy_decision.allowed ? "YES ✓" : "NO ✕"}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Timeline */}
          {result.timeline.length > 0 && (
            <section>
              <h3 className="mb-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                Execution Timeline
              </h3>
              <div className="relative border-l border-border/60 pl-4 space-y-3">
                {result.timeline.map((ev, i) => (
                  <div key={i} className="relative">
                    <span className="absolute -left-[17px] top-0.5 h-3 w-3 rounded-full border-2 border-primary/50 bg-primary/20" />
                    <p className="font-mono text-[10px] text-muted-foreground">{ev.time}</p>
                    <p className="text-xs text-foreground">{ev.event}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Footer CTA */}
        <div className="sticky bottom-0 border-t border-border/60 bg-card/95 px-6 py-4 backdrop-blur">
          <button
            onClick={onClose}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary/15 py-2.5 text-sm font-semibold text-primary ring-1 ring-primary/30 hover:bg-primary/25 transition-all"
          >
            Close Investigation <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </>
  );
}
