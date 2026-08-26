import type { InvestigationCase } from "@/lib/api/investigations";
import { Clock } from "lucide-react";

const recColor = {
  AUTO_RESOLVE: { bar: "bg-emerald-500", badge: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
  HUMAN_REVIEW: { bar: "bg-amber-500",   badge: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  BLOCK:        { bar: "bg-destructive", badge: "bg-destructive/15 text-destructive border-destructive/30" },
};

interface CaseStreamProps {
  cases: InvestigationCase[];
  onSelect: (caseId: string) => void;
  selectedId?: string | null;
}

export function CaseStream({ cases, onSelect, selectedId }: CaseStreamProps) {
  const recent = cases.slice(0, 12);

  return (
    <div className="rounded-xl border border-border/60 bg-card overflow-hidden fade-up">
      <div className="flex items-center justify-between border-b border-border/60 px-5 py-3">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Live Case Stream</h3>
          <p className="text-[11px] text-muted-foreground">Recent reconciliation exceptions</p>
        </div>
        <span className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
          <Clock className="h-3 w-3" />
          {cases.length} total
        </span>
      </div>

      <div className="divide-y divide-border/40">
        {recent.length === 0 ? (
          <div className="py-10 text-center text-sm text-muted-foreground">
            No exceptions yet — run batch reconciliation to populate.
          </div>
        ) : (
          recent.map((c) => {
            const rec = (c.recommendation ?? "HUMAN_REVIEW") as keyof typeof recColor;
            const styles = recColor[rec] ?? recColor.HUMAN_REVIEW;
            const active = selectedId === c.case_id;

            return (
              <button
                key={c.case_id}
                id={`case-row-${c.case_id}`}
                onClick={() => onSelect(c.case_id)}
                className={`group relative flex w-full items-center gap-3 px-5 py-3 text-left transition-colors hover:bg-accent/50 ${active ? "bg-primary/10" : ""}`}
              >
                {/* Severity indicator bar */}
                <span className={`absolute left-0 top-0 h-full w-0.5 ${styles.bar}`} />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-foreground truncate">
                      {c.case_id}
                    </span>
                    <span className={`rounded border px-1.5 py-0.5 text-[9px] font-bold uppercase ${styles.badge}`}>
                      {rec.replace("_", " ")}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[10px] text-muted-foreground capitalize">
                    {c.exception_type.replace(/_/g, " ")} · {c.payment_id}
                  </p>
                </div>

                <div className="flex-shrink-0 text-right">
                  <span className="font-mono text-xs font-semibold text-foreground">
                    ₹{(Math.abs(c.difference) / 100).toFixed(2)}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
