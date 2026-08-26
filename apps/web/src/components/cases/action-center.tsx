"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api/client";

export function ActionCenter({
  caseId,
  recommendation,
  onActionComplete,
}: {
  caseId: string;
  recommendation: string;
  onActionComplete?: () => void;
}) {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  async function approve() {
    setLoading(true);
    setStatusMessage(null);
    try {
      await api.post(`/cases/${caseId}/approve`, null, {
        params: {
          reviewer: "demo-user",
          reason: reason || "Manual analyst approval granted",
        },
      });
      setStatusMessage("Case approved successfully.");
      onActionComplete?.();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message;
      setStatusMessage(`Approval failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  }

  async function reject() {
    setLoading(true);
    setStatusMessage(null);
    try {
      await api.post(`/cases/${caseId}/reject`, null, {
        params: {
          reviewer: "demo-user",
          reason: reason || "Manual analyst rejection",
        },
      });
      setStatusMessage("Case rejected.");
      onActionComplete?.();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message;
      setStatusMessage(`Rejection failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  }

  async function resolve() {
    setLoading(true);
    setStatusMessage(null);
    try {
      const res = await api.post(`/cases/${caseId}/resolve`);
      setStatusMessage(`Resolved: ${res.data.action} (${res.data.status})`);
      onActionComplete?.();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message;
      setStatusMessage(`Resolution failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="space-y-4 p-6 border-muted-foreground/20">
      <div>
        <h3 className="font-semibold text-base">Action Center</h3>
        <p className="text-sm text-muted-foreground">
          AI recommendation:{" "}
          <span className="font-medium text-foreground">{recommendation}</span>
        </p>
      </div>

      <Textarea
        placeholder="Review reason or notes..."
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        disabled={loading}
      />

      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={resolve} disabled={loading} size="sm">
          Auto Resolve
        </Button>
        <Button
          onClick={approve}
          disabled={loading}
          variant="outline"
          size="sm"
        >
          Approve
        </Button>
        <Button
          onClick={reject}
          disabled={loading}
          variant="destructive"
          size="sm"
        >
          Reject
        </Button>
      </div>

      {statusMessage && (
        <p className="text-xs text-muted-foreground mt-2">{statusMessage}</p>
      )}
    </Card>
  );
}
