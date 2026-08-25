"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { runInvestigation } from "@/lib/api/investigations";

export function InvestigationPanel({
  caseId,
}: {
  caseId: string;
}) {
  const [result, setResult] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(false);

  async function investigate() {
    setLoading(true);

    try {
      const data =
        await runInvestigation(caseId);

      setResult(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Button
        onClick={investigate}
        disabled={loading}
      >
        {loading
          ? "Investigating..."
          : "Investigate Exception"}
      </Button>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>
                AI Investigation
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">
                  Root Cause
                </p>

                <p className="font-medium">
                  {result.root_cause}
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Confidence
                </p>

                <Badge>
                  {(
                    result.confidence * 100
                  ).toFixed(1)}
                  %
                </Badge>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Recommendation
                </p>

                <Badge>
                  {result.recommendation}
                </Badge>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Summary
                </p>

                <p>
                  {result.summary}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                Evidence
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                {result.evidence?.map(
                  (
                    item: any,
                    index: number,
                  ) => (
                    <div
                      key={index}
                      className="rounded-lg border p-3"
                    >
                      <div className="font-medium">
                        {
                          item.source_type
                        }
                      </div>

                      <div className="text-sm text-muted-foreground">
                        {
                          item.source_id
                        }
                      </div>

                      <div className="mt-1">
                        {item.field}:{" "}
                        {
                          item.observed_value
                        }
                      </div>

                      <div className="text-sm text-muted-foreground">
                        {
                          item.significance
                        }
                      </div>
                    </div>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}