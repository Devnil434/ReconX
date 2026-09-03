"use client";

import { useEffect } from "react";
import Link from "next/link";
import { TopNav } from "@/components/layout/top-nav";
import { AlertTriangle, ArrowLeft, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TestPaymentError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Test Payment Error Boundary caught:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background bg-grid">
      <TopNav />
      <main className="mx-auto max-w-[600px] px-6 py-24 text-center">
        <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-8 backdrop-blur-sm">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-foreground">
            Payment Simulator Interrupted
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {error.message || "An unexpected error occurred during the test payment session."}
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <Button onClick={reset} variant="default" className="gap-2">
              <RefreshCw className="h-4 w-4" /> Try Again
            </Button>
            <Link href="/dashboard">
              <Button variant="outline" className="gap-2">
                <ArrowLeft className="h-4 w-4" /> Return to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
