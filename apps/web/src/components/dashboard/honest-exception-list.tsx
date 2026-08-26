import { ShieldCheck, ShieldOff } from "lucide-react";

const CAN_RESOLVE = [
  { label: "Fee + GST deduction",       detail: "Exact arithmetic match" },
  { label: "Tax schedule variance",      detail: "Zero unexplained difference" },
  { label: "Rounding adjustment ≤ ₹1",  detail: "Sub-paisa tolerance" },
  { label: "Known fee schedule delta",   detail: "High confidence ≥ 95%" },
];

const REFUSES_RESOLVE = [
  { label: "Missing bank credit (UTR)",     detail: "Unknown settlement status" },
  { label: "Duplicate settlement batch",    detail: "High financial exposure" },
  { label: "Partial settlement",            detail: "Unexplained difference remains" },
  { label: "Conflicting evidence sources",  detail: "Contradictory signals" },
  { label: "AI confidence < 85%",           detail: "Ambiguous root cause" },
  { label: "Unexplained margin drop",       detail: "Requires analyst sign-off" },
];

export function HonestExceptionList() {
  return (
    <div className="grid gap-4 md:grid-cols-2 fade-up">
      {/* CAN auto-resolve */}
      <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-5">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/15 ring-1 ring-emerald-500/30">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-emerald-400">
              AI CAN Auto-Resolve
            </p>
            <p className="text-[10px] text-muted-foreground">Low risk · Difference balanced</p>
          </div>
        </div>
        <ul className="space-y-2.5">
          {CAN_RESOLVE.map((item) => (
            <li key={item.label} className="flex items-start gap-2.5">
              <span className="mt-0.5 h-4 w-4 flex-shrink-0 rounded-full bg-emerald-500/20 text-center text-[9px] font-bold leading-4 text-emerald-400">
                ✓
              </span>
              <div>
                <p className="text-xs font-medium text-foreground">{item.label}</p>
                <p className="text-[10px] text-muted-foreground">{item.detail}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* REFUSES to auto-resolve */}
      <div className="rounded-xl border border-destructive/25 bg-destructive/5 p-5">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-destructive/15 ring-1 ring-destructive/30">
            <ShieldOff className="h-3.5 w-3.5 text-destructive" />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-destructive">
              AI Refuses to Auto-Resolve
            </p>
            <p className="text-[10px] text-muted-foreground">
              Human review or block enforced
            </p>
          </div>
        </div>
        <ul className="space-y-2.5">
          {REFUSES_RESOLVE.map((item) => (
            <li key={item.label} className="flex items-start gap-2.5">
              <span className="mt-0.5 h-4 w-4 flex-shrink-0 rounded-full bg-destructive/20 text-center text-[9px] font-bold leading-4 text-destructive">
                ✕
              </span>
              <div>
                <p className="text-xs font-medium text-foreground">{item.label}</p>
                <p className="text-[10px] text-muted-foreground">{item.detail}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
