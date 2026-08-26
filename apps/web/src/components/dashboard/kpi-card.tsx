import { LucideIcon, TrendingDown, TrendingUp } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  trendLabel?: string;
  accentColor?: "indigo" | "emerald" | "amber" | "red" | "purple";
  /** Render value as full-width gradient text */
  highlight?: boolean;
}

const accentMap = {
  indigo: {
    ring: "ring-primary/20",
    bg: "bg-primary/10",
    text: "text-primary",
    bar: "bg-primary",
    glow: "glow-indigo",
    border: "border-primary/20",
  },
  emerald: {
    ring: "ring-emerald-500/20",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    bar: "bg-emerald-500",
    glow: "glow-emerald",
    border: "border-emerald-500/20",
  },
  amber: {
    ring: "ring-amber-500/20",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    bar: "bg-amber-500",
    glow: "glow-amber",
    border: "border-amber-500/20",
  },
  red: {
    ring: "ring-destructive/20",
    bg: "bg-destructive/10",
    text: "text-destructive",
    bar: "bg-destructive",
    glow: "glow-red",
    border: "border-destructive/20",
  },
  purple: {
    ring: "ring-purple-500/20",
    bg: "bg-purple-500/10",
    text: "text-purple-400",
    bar: "bg-purple-500",
    glow: "",
    border: "border-purple-500/20",
  },
};

export function KpiCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendLabel,
  accentColor = "indigo",
  highlight = false,
}: KpiCardProps) {
  const a = accentMap[accentColor];

  return (
    <div
      className={`relative overflow-hidden rounded-xl border ${a.border} bg-card p-5 transition-all duration-200 hover:scale-[1.01] hover:${a.glow} fade-up`}
    >
      {/* Top accent line */}
      <div className={`absolute inset-x-0 top-0 h-0.5 ${a.bar} opacity-70`} />

      {/* Header row */}
      <div className="mb-3 flex items-start justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          {title}
        </p>
        {Icon && (
          <div className={`flex h-7 w-7 items-center justify-center rounded-md ${a.bg} ring-1 ${a.ring}`}>
            <Icon className={`h-3.5 w-3.5 ${a.text}`} />
          </div>
        )}
      </div>

      {/* Value */}
      <div
        className={`text-3xl font-bold tracking-tight ${highlight ? "gradient-text" : "text-foreground"}`}
      >
        {value}
      </div>

      {/* Footer */}
      <div className="mt-2 flex items-center justify-between">
        {subtitle && (
          <p className="text-[11px] text-muted-foreground">{subtitle}</p>
        )}
        {trend && trendLabel && (
          <span
            className={`flex items-center gap-0.5 text-[11px] font-medium ${
              trend === "up" ? "text-emerald-400" : trend === "down" ? "text-destructive" : "text-muted-foreground"
            }`}
          >
            {trend === "up" ? (
              <TrendingUp className="h-3 w-3" />
            ) : trend === "down" ? (
              <TrendingDown className="h-3 w-3" />
            ) : null}
            {trendLabel}
          </span>
        )}
      </div>
    </div>
  );
}
