"use client";

interface HealthBar {
  label: string;
  value: number;
  max: number;
  color: "emerald" | "indigo" | "amber" | "red";
  suffix?: string;
}

const colorMap = {
  emerald: { bar: "bg-emerald-500", glow: "shadow-emerald-500/40", text: "text-emerald-400", track: "bg-emerald-500/15" },
  indigo:  { bar: "bg-primary",     glow: "shadow-primary/40",     text: "text-primary",     track: "bg-primary/15"     },
  amber:   { bar: "bg-amber-500",   glow: "shadow-amber-500/40",   text: "text-amber-400",   track: "bg-amber-500/15"   },
  red:     { bar: "bg-destructive", glow: "shadow-destructive/40", text: "text-destructive", track: "bg-destructive/15" },
};

interface ReconciliationHealthProps {
  matched: number;
  total: number;
  exceptions: number;
  aiAccuracy?: number;
}

export function ReconciliationHealth({
  matched,
  total,
  exceptions,
  aiAccuracy,
}: ReconciliationHealthProps) {
  const matchPct = total > 0 ? (matched / total) * 100 : 0;
  const exceptionPct = total > 0 ? (exceptions / total) * 100 : 0;

  const bars: HealthBar[] = [
    {
      label: "Matched Transactions",
      value: matchPct,
      max: 100,
      color: "emerald",
      suffix: `${matched.toLocaleString()} / ${total.toLocaleString()}`,
    },
    {
      label: "Exception Rate",
      value: exceptionPct,
      max: 100,
      color: exceptionPct > 15 ? "red" : exceptionPct > 10 ? "amber" : "amber",
      suffix: `${exceptions.toLocaleString()} exceptions`,
    },
    ...(aiAccuracy !== undefined
      ? [
          {
            label: "AI Accuracy (Root Cause)",
            value: aiAccuracy,
            max: 100,
            color: "indigo" as const,
            suffix: "0.0% False Auto-Resolution",
          },
        ]
      : []),
  ];

  return (
    <div className="rounded-xl border border-border/60 bg-card p-5 space-y-5 fade-up">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Reconciliation Health</h3>
          <p className="text-[11px] text-muted-foreground mt-0.5">Real-time engine performance metrics</p>
        </div>
        <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 status-pulse" />
          {total > 0 ? "Live Data" : "Awaiting Run"}
        </div>
      </div>

      <div className="space-y-4">
        {bars.map((bar) => {
          const c = colorMap[bar.color];
          const pct = Math.min(100, (bar.value / bar.max) * 100);
          return (
            <div key={bar.label} className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-muted-foreground">{bar.label}</span>
                <div className="flex items-center gap-2">
                  {bar.suffix && (
                    <span className="text-muted-foreground">{bar.suffix}</span>
                  )}
                  <span className={`font-bold tabular-nums ${c.text}`}>
                    {bar.value.toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className={`h-2 w-full rounded-full ${c.track} overflow-hidden`}>
                <div
                  className={`h-full rounded-full ${c.bar} shadow-sm ${c.glow} transition-all duration-700 ease-out`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
