"use client";

import { useState } from "react";
import { Loader2, FlaskConical, ChevronRight } from "lucide-react";
import {
  triggerDemoScenario,
  type DemoScenario,
  type DemoScenarioResult,
} from "@/lib/api/demo";
import { WhydDrawer } from "./why-drawer";

interface ScenarioDef {
  id: DemoScenario;
  label: string;
  description: string;
  expectedAction: string;
  color: string;
  borderColor: string;
  textColor: string;
}

const SCENARIOS: ScenarioDef[] = [
  {
    id: "fee-mismatch",
    label: "Fee Mismatch",
    description: "Fee + GST deduction — AUTO_RESOLVE",
    expectedAction: "AUTO_RESOLVE",
    color: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    textColor: "text-emerald-400",
  },
  {
    id: "missing-bank",
    label: "Missing Bank Credit",
    description: "UTR missing from bank feed — HUMAN_REVIEW",
    expectedAction: "HUMAN_REVIEW",
    color: "bg-amber-500/10",
    borderColor: "border-amber-500/30",
    textColor: "text-amber-400",
  },
  {
    id: "duplicate-settlement",
    label: "Duplicate Settlement",
    description: "Two batches, same payment — BLOCK",
    expectedAction: "BLOCK",
    color: "bg-destructive/10",
    borderColor: "border-destructive/30",
    textColor: "text-destructive",
  },
  {
    id: "unknown",
    label: "Unknown Discrepancy",
    description: "Low AI confidence (52%) — HUMAN_REVIEW",
    expectedAction: "HUMAN_REVIEW",
    color: "bg-amber-500/10",
    borderColor: "border-amber-500/30",
    textColor: "text-amber-400",
  },
  {
    id: "ai-failure",
    label: "AI Failure",
    description: "Provider timeout — Safe fallback enforced",
    expectedAction: "HUMAN_REVIEW",
    color: "bg-destructive/10",
    borderColor: "border-destructive/30",
    textColor: "text-destructive",
  },
];

export function DemoBanner() {
  const [loading, setLoading] = useState<DemoScenario | null>(null);
  const [result, setResult] = useState<DemoScenarioResult | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  async function run(scenario: DemoScenario) {
    setLoading(scenario);
    try {
      const data = await triggerDemoScenario(scenario);
      setResult(data);
      setDrawerOpen(true);
    } catch (err) {
      console.error("Demo trigger failed:", err);
    } finally {
      setLoading(null);
    }
  }

  return (
    <>
      <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 fade-up">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/15 ring-1 ring-amber-500/30">
              <FlaskConical className="h-3.5 w-3.5 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-amber-400">
                  DEMO MODE
                </span>
                <span className="rounded border border-amber-500/40 bg-amber-500/15 px-1.5 py-0.5 font-mono text-[9px] text-amber-400">
                  SYNTHETIC DATA
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                One-click scenario playback — not production data
              </p>
            </div>
          </div>
          {result && (
            <button
              onClick={() => setDrawerOpen(true)}
              className="flex items-center gap-1 text-[11px] font-medium text-primary hover:text-primary/80 transition-colors"
            >
              View Last Result <ChevronRight className="h-3 w-3" />
            </button>
          )}
        </div>

        {/* Scenario buttons */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              id={`demo-btn-${s.id}`}
              onClick={() => run(s.id)}
              disabled={loading !== null}
              className={`group relative flex flex-col items-start rounded-lg border ${s.borderColor} ${s.color} p-3 text-left transition-all duration-150 hover:scale-[1.02] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60`}
            >
              {loading === s.id && (
                <Loader2 className="absolute right-2 top-2 h-3 w-3 animate-spin text-muted-foreground" />
              )}
              <span className={`text-[11px] font-bold ${s.textColor}`}>
                {s.label}
              </span>
              <span className="mt-1 text-[10px] leading-tight text-muted-foreground">
                {s.description}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* WHY drawer */}
      {result && (
        <WhydDrawer
          result={result}
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        />
      )}
    </>
  );
}
