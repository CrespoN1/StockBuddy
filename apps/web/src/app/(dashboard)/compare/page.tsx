"use client";

import { useState } from "react";
import { GitCompareArrows, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { TickerMultiSelect } from "@/components/compare/ticker-multi-select";
import { ComparisonResult } from "@/components/compare/comparison-result";
import { useCompare } from "@/hooks/use-analysis";
import { useJobPolling } from "@/hooks/use-job-polling";
import { useUsage } from "@/hooks/use-subscription";
import { UpgradePrompt } from "@/components/ui/upgrade-prompt";

export default function ComparePage() {
  const { job, isPolling, startPolling } = useJobPolling();
  const compare = useCompare();
  const { data: usage } = useUsage();
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);

  function handleCompare(tickers: string[]) {
    setSelectedTickers(tickers);
    compare.mutate(tickers, {
      onSuccess: (pendingJob) => {
        startPolling(pendingJob);
        toast.info("Comparison started — this may take a minute");
      },
      onError: (err) => toast.error(err.message),
    });
  }

  const isRunning = compare.isPending || isPolling;

  if (usage && !usage.can_compare) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Compare Stocks</h2>
        <p className="mt-2 text-muted-foreground">
          Select 2-3 stocks to run an AI-powered comparative analysis based on
          their earnings data.
        </p>
        <div className="mt-6">
          <UpgradePrompt
            feature="Stock Comparison"
            description="Compare stocks side-by-side with AI-powered analysis. Upgrade to Pro to unlock."
          />
        </div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Compare Stocks</h2>
      <p className="mt-2 text-muted-foreground">
        Select 2-3 stocks to run an AI-powered comparative analysis based on
        their earnings data.
      </p>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Select Stocks</CardTitle>
          </CardHeader>
          <CardContent>
            <TickerMultiSelect
              onCompare={handleCompare}
              isComparing={isRunning}
            />
          </CardContent>
        </Card>
      </div>

      <div className="mt-6">
        {isRunning ? (
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <Loader2 className="mr-2 h-5 w-5 animate-spin text-muted-foreground" />
              <span className="text-muted-foreground">
                {isPolling ? "Processing comparison..." : "Submitting..."}
              </span>
            </CardContent>
          </Card>
        ) : job ? (
          <ComparisonResult job={job} tickers={selectedTickers} />
        ) : (
          <EmptyState
            icon={<GitCompareArrows className="h-12 w-12" />}
            title="No comparison yet"
            description="Select at least 2 stocks above and click Compare to see an AI-powered comparison of their earnings data."
          />
        )}
      </div>
    </div>
  );
}
