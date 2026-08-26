"use client";

import { useEffect, useState } from "react";
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
import { InvestigationPanel } from "@/components/investigations/investigation-panel";
import {
  getReconciliationSummary,
  runBatchReconciliation,
  type ReconciliationSummary,
  type BatchRunResult,
} from "@/lib/api/reconciliation";
import {
  listInvestigations,
  type InvestigationCase,
} from "@/lib/api/investigations";

interface MetricProps {
  title: string;
  value: string;
  subtitle?: string;
}

function Metric({ title, value, subtitle }: MetricProps) {
  return (
    <Card className="shadow-xs transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        {subtitle && (
          <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const [summary, setSummary] = useState<ReconciliationSummary | null>(null);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningBatch, setRunningBatch] = useState(false);
  const [lastBatchBenchmark, setLastBatchBenchmark] =
    useState<BatchRunResult | null>(null);

  async function loadData() {
    setLoading(true);
    try {
      const [sumData, casesData] = await Promise.all([
        getReconciliationSummary().catch(() => null),
        listInvestigations().catch(() => []),
      ]);
      if (sumData) setSummary(sumData);
      setCases(casesData || []);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleRunBatch() {
    setRunningBatch(true);
    try {
      const result = await runBatchReconciliation();
      setLastBatchBenchmark(result);
      await loadData();
    } catch (err) {
      console.error("Batch run failed:", err);
    } finally {
      setRunningBatch(false);
    }
  }

  const matchRateFormatted = summary
    ? `${(summary.match_rate * 100).toFixed(1)}%`
    : "0.0%";

  // Categorize cases into 3 lanes
  const autoResolveCases = cases.filter(
    (c) => c.recommendation === "AUTO_RESOLVE"
  );
  const humanReviewCases = cases.filter(
    (c) => !c.recommendation || c.recommendation === "HUMAN_REVIEW"
  );
  const blockedCases = cases.filter((c) => c.recommendation === "BLOCK");

  return (
    <main className="min-h-screen bg-background p-6 md:p-10">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-xs">
                RECONX CORE
              </Badge>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Feed
              </span>
            </div>
            <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Reconciliation Control Center
            </h1>
            <p className="text-sm text-muted-foreground sm:text-base">
              Autonomous payment reconciliation, ledger integrity & policy-driven resolution.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              disabled={loading || runningBatch}
            >
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={handleRunBatch}
              disabled={runningBatch}
            >
              {runningBatch ? "Reconciling..." : "Run Batch Reconciliation"}
            </Button>
          </div>
        </div>

        {/* Benchmark Banner if recently executed */}
        {lastBatchBenchmark && (
          <div className="rounded-lg border border-primary/20 bg-primary/5 p-4 text-sm">
            <span className="font-semibold text-primary">Benchmark:</span>{" "}
            Processed {lastBatchBenchmark.total.toLocaleString()} transactions in{" "}
            {lastBatchBenchmark.elapsed_seconds}s (
            <strong>{lastBatchBenchmark.transactions_per_second} tx/sec</strong>) with{" "}
            {(lastBatchBenchmark.match_rate * 100).toFixed(1)}% match rate.
          </div>
        )}

        {/* Metric Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            title="Total Transactions"
            value={summary ? summary.total.toLocaleString() : "0"}
            subtitle="Processed ledger records"
          />
          <Metric
            title="Match Rate"
            value={matchRateFormatted}
            subtitle={
              summary
                ? `${summary.matched.toLocaleString()} fully matched`
                : "Awaiting run"
            }
          />
          <Metric
            title="Exceptions"
            value={summary ? summary.exceptions.toLocaleString() : "0"}
            subtitle="Discrepancies identified"
          />
          <Metric
            title="Auto Resolved"
            value={cases.length ? `${autoResolveCases.length}` : "0"}
            subtitle={`${autoResolveCases.length} eligible by policy`}
          />
        </div>

        {/* 3-Lane Case Control Board */}
        <div>
          <h2 className="text-xl font-bold tracking-tight mb-4">
            Autonomous Case Control Board
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            {/* Lane 1: Auto Resolve */}
            <Card className="border-emerald-500/30 bg-emerald-500/5">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base text-emerald-600 dark:text-emerald-400 font-semibold">
                    AUTO-RESOLVE
                  </CardTitle>
                  <Badge variant="default" className="bg-emerald-600">
                    {autoResolveCases.length}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Low risk | Difference balanced | High confidence ($\ge 95\%$)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {autoResolveCases.slice(0, 4).map((c) => (
                  <div
                    key={c.case_id}
                    onClick={() => setSelectedCaseId(c.case_id)}
                    className="cursor-pointer rounded-md border border-emerald-500/20 bg-background/80 p-2.5 text-xs transition-all hover:bg-muted"
                  >
                    <div className="flex justify-between font-mono font-medium">
                      <span>{c.case_id}</span>
                      <span>₹{(Math.abs(c.difference) / 100).toFixed(2)}</span>
                    </div>
                    <p className="text-muted-foreground capitalize mt-1">
                      {c.exception_type.replace(/_/g, " ")}
                    </p>
                  </div>
                ))}
                {autoResolveCases.length === 0 && (
                  <p className="text-xs text-muted-foreground py-4 text-center">
                    No cases in this lane
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Lane 2: Human Review */}
            <Card className="border-amber-500/30 bg-amber-500/5">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base text-amber-600 dark:text-amber-400 font-semibold">
                    HUMAN REVIEW
                  </CardTitle>
                  <Badge variant="secondary" className="bg-amber-500/20 text-amber-700 dark:text-amber-300">
                    {humanReviewCases.length}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Medium risk | Needs analyst review or approval
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {humanReviewCases.slice(0, 4).map((c) => (
                  <div
                    key={c.case_id}
                    onClick={() => setSelectedCaseId(c.case_id)}
                    className="cursor-pointer rounded-md border border-amber-500/20 bg-background/80 p-2.5 text-xs transition-all hover:bg-muted"
                  >
                    <div className="flex justify-between font-mono font-medium">
                      <span>{c.case_id}</span>
                      <span>₹{(Math.abs(c.difference) / 100).toFixed(2)}</span>
                    </div>
                    <p className="text-muted-foreground capitalize mt-1">
                      {c.exception_type.replace(/_/g, " ")}
                    </p>
                  </div>
                ))}
                {humanReviewCases.length === 0 && (
                  <p className="text-xs text-muted-foreground py-4 text-center">
                    No cases in this lane
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Lane 3: Blocked */}
            <Card className="border-destructive/30 bg-destructive/5">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base text-destructive font-semibold">
                    BLOCKED
                  </CardTitle>
                  <Badge variant="destructive">
                    {blockedCases.length}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  High risk | Duplicate settlement or critical variance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {blockedCases.slice(0, 4).map((c) => (
                  <div
                    key={c.case_id}
                    onClick={() => setSelectedCaseId(c.case_id)}
                    className="cursor-pointer rounded-md border border-destructive/20 bg-background/80 p-2.5 text-xs transition-all hover:bg-muted"
                  >
                    <div className="flex justify-between font-mono font-medium">
                      <span>{c.case_id}</span>
                      <span>₹{(Math.abs(c.difference) / 100).toFixed(2)}</span>
                    </div>
                    <p className="text-muted-foreground capitalize mt-1">
                      {c.exception_type.replace(/_/g, " ")}
                    </p>
                  </div>
                ))}
                {blockedCases.length === 0 && (
                  <p className="text-xs text-muted-foreground py-4 text-center">
                    No cases in this lane
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Selected Case Active Investigation & Action Panel */}
        {selectedCaseId && (
          <Card className="border-primary/40 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-lg">
                  Active Investigation: {selectedCaseId}
                </CardTitle>
                <CardDescription>
                  Deep-dive facts, competing hypotheses, policy evaluation & action center.
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
              <InvestigationPanel
                caseId={selectedCaseId}
                onActionComplete={loadData}
              />
            </CardContent>
          </Card>
        )}

        {/* Complete Investigation Queue Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Exceptions Queue</CardTitle>
            <CardDescription>
              Open reconciliation exceptions requiring automated investigation or review.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {loading && cases.length === 0 ? (
              <div className="py-12 text-center text-sm text-muted-foreground">
                Loading live exception cases...
              </div>
            ) : cases.length === 0 ? (
              <div className="py-12 text-center text-sm text-muted-foreground">
                No exceptions in queue. Click &quot;Run Batch Reconciliation&quot; above to process.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Case ID</TableHead>
                      <TableHead>Payment ID</TableHead>
                      <TableHead>Exception Type</TableHead>
                      <TableHead>Difference</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>AI Recommendation</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {cases.map((c) => (
                      <TableRow
                        key={c.case_id}
                        className={
                          selectedCaseId === c.case_id ? "bg-muted/50" : ""
                        }
                      >
                        <TableCell className="font-mono text-xs font-semibold">
                          {c.case_id}
                        </TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">
                          {c.payment_id}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="capitalize">
                            {c.exception_type.replace(/_/g, " ")}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs font-medium">
                          ₹{(Math.abs(c.difference) / 100).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              c.status === "completed" || c.status === "resolved"
                                ? "default"
                                : "outline"
                            }
                            className="capitalize"
                          >
                            {c.status}
                          </Badge>
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
                            >
                              {c.recommendation}
                              {c.confidence
                                ? ` (${(c.confidence * 100).toFixed(0)}%)`
                                : ""}
                            </Badge>
                          ) : (
                            <span className="text-xs text-muted-foreground">
                              Not investigated
                            </span>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            size="sm"
                            variant={
                              selectedCaseId === c.case_id
                                ? "default"
                                : "outline"
                            }
                            onClick={() => setSelectedCaseId(c.case_id)}
                          >
                            {selectedCaseId === c.case_id
                              ? "Viewing"
                              : "Investigate"}
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
    </main>
  );
}