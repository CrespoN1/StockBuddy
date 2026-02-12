"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { JobStatus } from "@/types";

interface ComparisonResultProps {
  job: JobStatus | null;
}

export function ComparisonResult({ job }: ComparisonResultProps) {
  if (!job) return null;

  if (job.status === "failed") {
    return (
      <Card className="border-destructive/50">
        <CardContent className="pt-6">
          <p className="text-sm text-destructive">
            {job.error ?? "Comparison failed. Make sure all tickers have been analyzed first."}
          </p>
        </CardContent>
      </Card>
    );
  }

  if (job.status === "completed") {
    const comparison = (job.result as { comparison?: string })?.comparison;
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Comparison Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {comparison ?? "No comparison data available."}
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}
