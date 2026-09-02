"use client";

import { useEffect, useState } from "react";
import {
  Server,
  Database,
  Layers,
  Bot,
  CreditCard,
  RefreshCw,
  Boxes,
  DollarSign,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { getSystemHealth, getQueueStats, type SystemHealth, type QueueStats } from "@/lib/api/system";

type ServiceKey = keyof SystemHealth["services"];

const SERVICE_META: { key: ServiceKey; label: string; icon: React.ElementType }[] = [
  { key: "api",         label: "API Server",     icon: Server    },
  { key: "database",    label: "PostgreSQL",      icon: Database  },
  { key: "redis",       label: "Redis",           icon: Layers    },
  { key: "workers",     label: "Workers",         icon: Boxes     },
  { key: "ai_provider", label: "AI Provider",     icon: Bot       },
  { key: "razorpay",    label: "Razorpay",        icon: CreditCard},
];

function StatusDot({ status }: { status: string }) {
  const isHealthy = status === "healthy";
  return (
    <span
      className={`flex h-2 w-2 rounded-full ${
        isHealthy ? "bg-emerald-400 status-pulse" : "bg-destructive"
      }`}
    />
  );
}

function ServiceCard({
  label,
  icon: Icon,
  status,
  detail,
}: {
  label: string;
  icon: React.ElementType;
  status: string;
  detail?: string;
}) {
  const isHealthy = status === "healthy";
  return (
    <div
      className={`flex items-start gap-3 rounded-xl border p-4 transition-all ${
        isHealthy
          ? "border-emerald-500/25 bg-emerald-500/5"
          : "border-destructive/25 bg-destructive/5"
      }`}
    >
      <div
        className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ring-1 ${
          isHealthy
            ? "bg-emerald-500/15 ring-emerald-500/30"
            : "bg-destructive/15 ring-destructive/30"
        }`}
      >
        <Icon
          className={`h-4 w-4 ${isHealthy ? "text-emerald-400" : "text-destructive"}`}
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-foreground">{label}</span>
          <div className="flex items-center gap-1.5">
            <StatusDot status={status} />
            <span
              className={`text-[11px] font-medium capitalize ${
                isHealthy ? "text-emerald-400" : "text-destructive"
              }`}
            >
              {status}
            </span>
          </div>
        </div>
        {detail && (
          <p className="mt-0.5 text-[10px] text-muted-foreground truncate">{detail}</p>
        )}
      </div>
    </div>
  );
}

function QueueBar({
  label,
  queued,
  failed,
}: {
  label: string;
  queued: number;
  failed?: number;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/40 bg-background/60 px-4 py-3">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="flex items-center gap-3">
        <span className="text-[11px] text-muted-foreground">
          {queued} queued
        </span>
        {failed !== undefined && failed > 0 && (
          <span className="rounded border border-destructive/30 bg-destructive/10 px-1.5 py-0.5 text-[10px] font-bold text-destructive">
            {failed} failed
          </span>
        )}
        <span
          className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
            queued === 0
              ? "bg-emerald-500/15 text-emerald-400"
              : "bg-amber-500/15 text-amber-400"
          }`}
        >
          {queued === 0 ? "IDLE" : "ACTIVE"}
        </span>
      </div>
    </div>
  );
}

export default function SystemPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [queues, setQueues] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [h, q] = await Promise.all([
        getSystemHealth(),
        getQueueStats(),
      ]);
      setHealth(h);
      setQueues(q);
    } catch {
      // Non-network error
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 15_000);
    return () => clearInterval(interval);
  }, []);

  const metrics = health?.metrics;

  return (
    <div className="min-h-screen bg-background bg-grid">
      <TopNav />
      <main className="mx-auto max-w-[1400px] space-y-6 px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-1">
              Observability
            </p>
            <h1 className="text-2xl font-bold sm:text-3xl">
              System{" "}
              <span className="gradient-text">Health</span>
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Live infrastructure status · auto-refreshes every 15s
            </p>
          </div>
          <div className="flex items-center gap-3">
            {health && (
              <span
                className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-bold ${
                  health.status === "healthy"
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : "border-destructive/30 bg-destructive/10 text-destructive"
                }`}
              >
                <span className={`h-1.5 w-1.5 rounded-full ${health.status === "healthy" ? "bg-emerald-400 status-pulse" : "bg-destructive"}`} />
                {health.status === "healthy" ? "All Systems Operational" : "Degraded"}
              </span>
            )}
            <button
              onClick={load}
              disabled={loading}
              className="flex items-center gap-1.5 rounded-lg border border-border/60 bg-card px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-accent transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {loading && !health ? (
          <div className="py-20 text-center text-sm text-muted-foreground animate-pulse">
            Connecting to infrastructure…
          </div>
        ) : health ? (
          <>
            {/* Demo Mode Badge */}
            {health.demo_mode && (
              <div className="flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/8 px-4 py-2.5 text-[11px]">
                <span className="font-bold text-amber-400">DEMO MODE</span>
                <span className="text-muted-foreground">—</span>
                <span className="text-muted-foreground">
                  Synthetic data only · No real transactions processed
                </span>
              </div>
            )}

            {/* Service Grid */}
            <div>
              <h2 className="mb-3 text-sm font-bold text-foreground">Infrastructure Services</h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {SERVICE_META.map(({ key, label, icon }) => {
                  const svc = health.services[key];
                  const detail =
                    svc.type ?? svc.provider ?? svc.mode ??
                    (svc.count !== undefined ? `${svc.count} active workers` : undefined) ??
                    (svc.port !== undefined ? `Port ${svc.port}` : undefined);
                  return (
                    <ServiceCard
                      key={key}
                      label={label}
                      icon={icon}
                      status={svc.status}
                      detail={detail}
                    />
                  );
                })}
              </div>
            </div>

            {/* Queue Depths */}
            {queues && (
              <div>
                <h2 className="mb-3 text-sm font-bold text-foreground">Queue Depths</h2>
                <div className="space-y-2">
                  <QueueBar label="Reconciliation Queue" queued={queues.reconciliation.queued} failed={queues.reconciliation.failed} />
                  <QueueBar label="Investigation Queue"  queued={queues.investigation.queued}  failed={queues.investigation.failed} />
                  <QueueBar label="Actions Queue"        queued={queues.actions.queued}        failed={queues.actions.failed} />
                  <QueueBar label="Dead Letter Queue"    queued={queues.dead_letter.queued} />
                </div>
              </div>
            )}

            {/* AI Cost Metrics */}
            {metrics && (
              <div>
                <h2 className="mb-3 text-sm font-bold text-foreground">AI Cost Metrics</h2>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {[
                    {
                      label: "AI Calls",
                      value: metrics.ai_calls_total.toLocaleString(),
                      sub: `${metrics.ai_calls_per_tx_pct.toFixed(1)}% of transactions`,
                      icon: Bot,
                      color: "indigo",
                    },
                    {
                      label: "Input Tokens",
                      value: `${(metrics.ai_tokens_input / 1000).toFixed(1)}k`,
                      sub: "Prompt tokens consumed",
                      icon: Layers,
                      color: "purple",
                    },
                    {
                      label: "Output Tokens",
                      value: `${(metrics.ai_tokens_output / 1000).toFixed(1)}k`,
                      sub: "Completion tokens generated",
                      icon: Layers,
                      color: "purple",
                    },
                    {
                      label: "Estimated Cost",
                      value: `$${metrics.estimated_ai_cost_usd.toFixed(2)}`,
                      sub: `For ${metrics.total_transactions.toLocaleString()} transactions`,
                      icon: DollarSign,
                      color: "emerald",
                    },
                  ].map(({ label, value, sub, icon: Icon, color }) => {
                    const colors: Record<string, string> = {
                      indigo: "border-primary/20 bg-primary/5",
                      purple: "border-purple-500/20 bg-purple-500/5",
                      emerald: "border-emerald-500/20 bg-emerald-500/5",
                    };
                    const textColors: Record<string, string> = {
                      indigo: "text-primary",
                      purple: "text-purple-400",
                      emerald: "text-emerald-400",
                    };
                    return (
                      <div
                        key={label}
                        className={`rounded-xl border p-4 fade-up ${colors[color]}`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className={`h-3.5 w-3.5 ${textColors[color]}`} />
                          <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                            {label}
                          </span>
                        </div>
                        <p className={`text-2xl font-bold ${textColors[color]}`}>{value}</p>
                        <p className="mt-1 text-[10px] text-muted-foreground">{sub}</p>
                      </div>
                    );
                  })}
                </div>
                <div className="mt-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-[11px] text-emerald-400">
                  ✦ AI is only invoked for exception cases ({metrics.ai_calls_per_tx_pct.toFixed(1)}% of transactions), keeping costs minimal while maintaining 97.6% investigation accuracy.
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="py-20 text-center text-sm text-destructive">
            Failed to connect to API. Is the server running on port 8000?
          </div>
        )}
      </main>
    </div>
  );
}
