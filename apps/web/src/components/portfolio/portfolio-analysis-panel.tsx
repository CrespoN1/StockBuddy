"use client";

import { Sparkles, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyzePortfolio } from "@/hooks/use-analysis";
import { useJobPolling } from "@/hooks/use-job-polling";

interface PortfolioAnalysisPanelProps {
  portfolioId: number;
}

export function PortfolioAnalysisPanel({ portfolioId }: PortfolioAnalysisPanelProps) {
  const { job, isPolling, startPolling } = useJobPolling();
  const analyzePortfolio = useAnalyzePortfolio();

  function handleAnalyze() {
    analyzePortfolio.mutate(portfolioId, {
      onSuccess: (pendingJob) => {
        startPolling(pendingJob);
        toast.info("Analysis started — this may take a minute");
      },
      onError: (err) => toast.error(err.message),
    });
  }

  const isRunning = analyzePortfolio.isPending || isPolling;

  const analysis = job?.status === "completed"
    ? (job.result as { analysis?: string })?.analysis
    : null;

  const snapshot = job?.status === "completed"
    ? (job.result as { snapshot?: Record<string, unknown> })?.snapshot
    : null;

  return (
    <div className="space-y-4">
      <Button
        onClick={handleAnalyze}
        disabled={isRunning}
      >
        {isRunning ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {isPolling ? "Processing..." : "Submitting..."}
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            Analyze Portfolio
          </>
        )}
      </Button>

      {job?.status === "failed" && (
        <Card className="border-destructive/50">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{job.error}</p>
          </CardContent>
        </Card>
      )}

      {snapshot && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Total Value", value: snapshot.total_value != null ? `$${Number(snapshot.total_value).toLocaleString()}` : "--" },
            { label: "Health Score", value: snapshot.health_score != null ? `${snapshot.health_score}/100` : "--" },
            { label: "Positions", value: String(snapshot.num_positions ?? 0) },
            { label: "Concentration Risk", value: snapshot.concentration_risk != null ? `${(Number(snapshot.concentration_risk) * 100).toFixed(1)}%` : "--" },
          ].map((s) => (
            <Card key={s.label}>
              <CardContent className="p-4">
                <p className="text-xs text-muted-foreground">{s.label}</p>
                <p className="mt-1 text-lg font-semibold">{s.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">AI Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {analysis}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
