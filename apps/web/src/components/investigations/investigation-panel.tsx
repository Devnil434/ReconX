"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ActionCenter } from "@/components/cases/action-center";
import { runInvestigation } from "@/lib/api/investigations";

export function InvestigationPanel({
  caseId,
  onActionComplete,
}: {
  caseId: string;
  onActionComplete?: () => void;
}) {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function investigate() {
    setLoading(true);
    try {
      const data = await runInvestigation(caseId);
      setResult(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (caseId) {
      investigate();
    }
  }, [caseId]);

  return (
    <div className="space-y-6">
      <Button onClick={investigate} disabled={loading}>
        {loading ? "Investigating..." : "Investigate Exception"}
      </Button>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>AI Investigation Findings</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Root Cause</p>
                <p className="font-medium text-foreground mt-0.5">
                  {result.root_cause}
                </p>
              </div>

              <div className="flex gap-6">
                <div>
                  <p className="text-sm text-muted-foreground">Confidence</p>
                  <Badge className="mt-1" variant="outline">
                    {(result.confidence * 100).toFixed(1)}%
                  </Badge>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">Recommendation</p>
                  <Badge
                    className="mt-1"
                    variant={
                      result.recommendation === "AUTO_RESOLVE"
                        ? "default"
                        : result.recommendation === "BLOCK"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {result.recommendation}
                  </Badge>
                </div>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Summary</p>
                <p className="text-sm text-foreground mt-0.5">{result.summary}</p>
              </div>
            </CardContent>
          </Card>

          {/* Action Center for Human Review / Resolution */}
          <ActionCenter
            caseId={caseId}
            recommendation={result.recommendation}
            onActionComplete={onActionComplete}
          />

          <Card>
            <CardHeader>
              <CardTitle>Evidence Chain</CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                {result.evidence?.map((item: any, index: number) => (
                  <div key={index} className="rounded-lg border p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize text-foreground">
                        {item.source_type}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        {item.source_id}
                      </span>
                    </div>

                    <div className="mt-1.5 font-mono text-xs">
                      <span className="text-muted-foreground">{item.field}:</span>{" "}
                      <span className="font-semibold">{item.observed_value}</span>
                    </div>

                    <div className="mt-1 text-xs text-muted-foreground">
                      {item.significance}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}