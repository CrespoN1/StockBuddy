"use client";

import { Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { exportComparisonCSV } from "@/lib/csv-export";
import type { JobStatus } from "@/types";

interface ComparisonResultProps {
  job: JobStatus | null;
  tickers?: string[];
}

export function ComparisonResult({ job, tickers }: ComparisonResultProps) {
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
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Comparison Results</CardTitle>
          {comparison && tickers && tickers.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportComparisonCSV(comparison, tickers)}
            >
              <Download className="h-3.5 w-3.5 mr-1.5" />
              Export CSV
            </Button>
          )}
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
