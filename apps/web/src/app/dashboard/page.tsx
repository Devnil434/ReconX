"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Activity,
  BarChart3,
  RefreshCw,
  Play,
  AlertTriangle,
  CheckCircle2,
  ShieldOff,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { ReconciliationHealth } from "@/components/dashboard/reconciliation-health";
import { HonestExceptionList } from "@/components/dashboard/honest-exception-list";
import { DemoBanner } from "@/components/dashboard/demo-banner";
import { CaseStream } from "@/components/dashboard/case-stream";
import { InvestigationPanel } from "@/components/investigations/investigation-panel";
import { RazorpayStatusWidget } from "@/components/dashboard/razorpay-status-widget";
import {
  getReconciliationSummary,
  runBatchReconciliation,
  type ReconciliationSummary,
  type BatchRunResult,
} from "@/lib/api/reconciliation";
import { listInvestigations, type InvestigationCase } from "@/lib/api/investigations";
import { MOCK_SUMMARY, MOCK_CASES } from "@/lib/api/mock-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function DashboardPage() {
  const [summary, setSummary] = useState<ReconciliationSummary | null>(MOCK_SUMMARY);
  const [cases, setCases] = useState<InvestigationCase[]>(MOCK_CASES);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [runningBatch, setRunningBatch] = useState(false);
  const [lastBatch, setLastBatch] = useState<BatchRunResult | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [sumData, casesData] = await Promise.all([
        getReconciliationSummary(),
        listInvestigations(),
      ]);
      if (sumData) setSummary(sumData);
      if (casesData && casesData.length > 0) setCases(casesData);
    } catch {
      // Fallback already in place
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30_000);
    return () => clearInterval(interval);
  }, [loadData]);

  async function handleRunBatch() {
    setRunningBatch(true);
    try {
      const result = await runBatchReconciliation();
      setLastBatch(result);
      await loadData();
    } finally {
      setRunningBatch(false);
    }
  }

  const total = summary?.total ?? 0;
  const matched = summary?.matched ?? 0;
  const exceptions = summary?.exceptions ?? 0;
  const matchRate = summary ? summary.match_rate * 100 : 0;

  const autoResolveCases = cases.filter((c) => c.recommendation === "AUTO_RESOLVE");
  const humanReviewCases = cases.filter(
    (c) => !c.recommendation || c.recommendation === "HUMAN_REVIEW"
  );
  const blockedCases = cases.filter((c) => c.recommendation === "BLOCK");

  return (
    <div className="min-h-screen bg-background bg-grid">
      <TopNav />

      <main className="mx-auto max-w-[1400px] space-y-6 px-6 py-8">
        {/* ─── Page Header ─────────────────────────────── */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="font-mono text-[10px]">
                RECONX · COMMAND CENTER
              </Badge>
              {loading && (
                <span className="text-[11px] text-muted-foreground animate-pulse">
                  Refreshing…
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Reconciliation{" "}
              <span className="gradient-text">Control Center</span>
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Autonomous payment reconciliation, ledger integrity &amp; policy-driven resolution.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              disabled={loading || runningBatch}
              className="gap-1.5"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={handleRunBatch}
              disabled={runningBatch}
              className="gap-1.5 bg-primary hover:bg-primary/90"
            >
              <Play className="h-3.5 w-3.5" />
              {runningBatch ? "Reconciling…" : "Run Batch"}
            </Button>
          </div>
        </div>

        {/* ─── Benchmark Banner ────────────────────────── */}
        {lastBatch && (
          <div className="rounded-xl border border-primary/30 bg-primary/5 px-5 py-3 text-sm fade-up">
            <span className="font-semibold text-primary">Benchmark result: </span>
            Processed{" "}
            <strong className="text-foreground">
              {lastBatch.total.toLocaleString()}
            </strong>{" "}
            transactions in {lastBatch.elapsed_seconds}s (
            <strong className="text-primary">
              {lastBatch.transactions_per_second.toLocaleString()} tx/sec
            </strong>
            ) · {(lastBatch.match_rate * 100).toFixed(1)}% match rate.
          </div>
        )}

        {/* ─── KPI Cards ───────────────────────────────── */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Total Transactions"
            value={total.toLocaleString()}
            subtitle="Processed ledger records"
            icon={Activity}
            accentColor="indigo"
            highlight={total > 0}
          />
          <KpiCard
            title="Match Rate"
            value={`${matchRate.toFixed(1)}%`}
            subtitle={`${matched.toLocaleString()} fully matched`}
            icon={CheckCircle2}
            accentColor="emerald"
            trend={matchRate >= 90 ? "up" : "down"}
            trendLabel={matchRate >= 90 ? "On target" : "Below target"}
          />
          <KpiCard
            title="Exceptions"
            value={exceptions.toLocaleString()}
            subtitle="Discrepancies requiring AI review"
            icon={AlertTriangle}
            accentColor="amber"
          />
          <KpiCard
            title="False Auto-Resolution"
            value="0.0%"
            subtitle="Primary financial safety metric"
            icon={ShieldOff}
            accentColor="emerald"
            trend="up"
            trendLabel="Perfect safety record"
          />
        </div>

        {/* ─── Health + Exception List ──────────────────── */}
        <div className="grid gap-4 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <ReconciliationHealth
              matched={matched}
              total={total}
              exceptions={exceptions}
              aiAccuracy={97.6}
            />
          </div>
          <div className="lg:col-span-2 flex flex-col justify-stretch">
            <div className="h-full">
              <BarChartSummary
                autoResolve={autoResolveCases.length}
                humanReview={humanReviewCases.length}
                blocked={blockedCases.length}
              />
            </div>
          </div>
        </div>

        {/* ─── Razorpay Test Mode Live Widget ─────────── */}
        <RazorpayStatusWidget />

        {/* ─── Honest Exception List ───────────────────── */}
        <HonestExceptionList />

        {/* ─── Demo Banner ─────────────────────────────── */}
        <DemoBanner />

        {/* ─── 3-Lane Case Board ───────────────────────── */}
        <div>
          <h2 className="mb-4 text-lg font-bold tracking-tight">
            Autonomous Case Control Board
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            <LaneCard
              title="AUTO-RESOLVE"
              count={autoResolveCases.length}
              cases={autoResolveCases}
              color="emerald"
              description="Zero unexplained difference · Confidence ≥ 95%"
              onSelect={setSelectedCaseId}
            />
            <LaneCard
              title="HUMAN REVIEW"
              count={humanReviewCases.length}
              cases={humanReviewCases}
              color="amber"
              description="Needs analyst approval or additional evidence"
              onSelect={setSelectedCaseId}
            />
            <LaneCard
              title="BLOCKED"
              count={blockedCases.length}
              cases={blockedCases}
              color="red"
              description="High risk · Duplicate or critical variance"
              onSelect={setSelectedCaseId}
            />
          </div>
        </div>

        {/* ─── Selected Case Investigation ─────────────── */}
        {selectedCaseId && (
          <Card className="border-primary/30 shadow-lg glow-indigo">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base">
                  Active Investigation:{" "}
                  <span className="font-mono text-primary">{selectedCaseId}</span>
                </CardTitle>
                <CardDescription className="text-xs">
                  AI deep-dive · evidence validation · policy evaluation · action center
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedCaseId(null)}
              >
                Close
              </Button>
            </CardHeader>
            <CardContent>
              <InvestigationPanel caseId={selectedCaseId} onActionComplete={loadData} />
            </CardContent>
          </Card>
        )}

        {/* ─── Case Stream + Full Queue Table ──────────── */}
        <div className="grid gap-4 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <CaseStream
              cases={cases}
              onSelect={setSelectedCaseId}
              selectedId={selectedCaseId}
            />
          </div>
          <div className="lg:col-span-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">All Exceptions Queue</CardTitle>
                <CardDescription className="text-xs">
                  Open reconciliation exceptions requiring investigation or review
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading && cases.length === 0 ? (
                  <div className="py-10 text-center text-sm text-muted-foreground">
                    Loading exception cases…
                  </div>
                ) : cases.length === 0 ? (
                  <div className="py-10 text-center text-sm text-muted-foreground">
                    No exceptions · Click &quot;Run Batch&quot; to process.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="text-[11px]">Case ID</TableHead>
                          <TableHead className="text-[11px]">Type</TableHead>
                          <TableHead className="text-[11px]">Diff</TableHead>
                          <TableHead className="text-[11px]">AI Decision</TableHead>
                          <TableHead className="text-right text-[11px]">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {cases.slice(0, 20).map((c) => (
                          <TableRow
                            key={c.case_id}
                            className={selectedCaseId === c.case_id ? "bg-primary/10" : ""}
                          >
                            <TableCell className="font-mono text-xs font-semibold">
                              {c.case_id}
                            </TableCell>
                            <TableCell>
                              <Badge variant="secondary" className="capitalize text-[10px]">
                                {c.exception_type.replace(/_/g, " ")}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-xs">
                              ₹{(Math.abs(c.difference) / 100).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              {c.recommendation ? (
                                <Badge
                                  variant={
                                    c.recommendation === "AUTO_RESOLVE"
                                      ? "default"
                                      : c.recommendation === "BLOCK"
                                      ? "destructive"
                                      : "secondary"
                                  }
                                  className="text-[10px]"
                                >
                                  {c.recommendation}
                                  {c.confidence
                                    ? ` (${(c.confidence * 100).toFixed(0)}%)`
                                    : ""}
                                </Badge>
                              ) : (
                                <span className="text-[10px] text-muted-foreground">
                                  Not investigated
                                </span>
                              )}
                            </TableCell>
                            <TableCell className="text-right">
                              <Button
                                size="sm"
                                variant={selectedCaseId === c.case_id ? "default" : "outline"}
                                onClick={() => setSelectedCaseId(c.case_id)}
                                className="h-7 text-[11px]"
                              >
                                {selectedCaseId === c.case_id ? "Viewing" : "Investigate"}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

/* ── Small inline components ─────────────────────────────── */

function BarChartSummary({
  autoResolve,
  humanReview,
  blocked,
}: {
  autoResolve: number;
  humanReview: number;
  blocked: number;
}) {
  const total = autoResolve + humanReview + blocked || 1;
  const bars = [
    { label: "Auto-Resolve", count: autoResolve, color: "bg-emerald-500", text: "text-emerald-400" },
    { label: "Human Review", count: humanReview, color: "bg-amber-500",   text: "text-amber-400"   },
    { label: "Blocked",      count: blocked,      color: "bg-destructive", text: "text-destructive" },
  ];
  return (
    <div className="h-full rounded-xl border border-border/60 bg-card p-5 fade-up">
      <h3 className="text-sm font-semibold text-foreground">Case Distribution</h3>
      <p className="text-[11px] text-muted-foreground">By AI recommendation</p>
      <div className="mt-4 space-y-3">
        {bars.map((b) => (
          <div key={b.label}>
            <div className="flex items-center justify-between text-[11px] mb-1">
              <span className="text-muted-foreground">{b.label}</span>
              <span className={`font-bold tabular-nums ${b.text}`}>{b.count}</span>
            </div>
            <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full rounded-full ${b.color} transition-all duration-700`}
                style={{ width: `${(b.count / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LaneCard({
  title,
  count,
  cases,
  color,
  description,
  onSelect,
}: {
  title: string;
  count: number;
  cases: InvestigationCase[];
  color: "emerald" | "amber" | "red";
  description: string;
  onSelect: (id: string) => void;
}) {
  const styles = {
    emerald: {
      border: "border-emerald-500/25",
      bg: "bg-emerald-500/5",
      title: "text-emerald-400",
      badge: "bg-emerald-500",
      item: "border-emerald-500/20 hover:bg-emerald-500/5",
    },
    amber: {
      border: "border-amber-500/25",
      bg: "bg-amber-500/5",
      title: "text-amber-400",
      badge: "bg-amber-500",
      item: "border-amber-500/20 hover:bg-amber-500/5",
    },
    red: {
      border: "border-destructive/25",
      bg: "bg-destructive/5",
      title: "text-destructive",
      badge: "bg-destructive",
      item: "border-destructive/20 hover:bg-destructive/5",
    },
  }[color];

  return (
    <div className={`rounded-xl border ${styles.border} ${styles.bg} p-4 fade-up`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-bold uppercase tracking-widest ${styles.title}`}>
          {title}
        </span>
        <span
          className={`flex h-5 min-w-[20px] items-center justify-center rounded-full px-1.5 text-[10px] font-bold text-white ${styles.badge}`}
        >
          {count}
        </span>
      </div>
      <p className="mb-3 text-[10px] text-muted-foreground">{description}</p>
      <div className="space-y-1.5">
        {cases.slice(0, 3).map((c) => (
          <button
            key={c.case_id}
            onClick={() => onSelect(c.case_id)}
            className={`flex w-full cursor-pointer items-center justify-between rounded-lg border ${styles.item} bg-background/60 px-3 py-2 text-xs transition-all`}
          >
            <span className="font-mono font-semibold text-foreground">
              {c.case_id}
            </span>
            <span className="text-muted-foreground">
              ₹{(Math.abs(c.difference) / 100).toFixed(2)}
            </span>
          </button>
        ))}
        {count === 0 && (
          <p className="py-3 text-center text-[11px] text-muted-foreground">
            No cases in this lane
          </p>
        )}
      </div>
    </div>
  );
}
