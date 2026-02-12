"use client";

import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StockSearchBar } from "@/components/stock/stock-search-bar";
import { useAnalyzeEarnings } from "@/hooks/use-earnings";
import { useJobPolling } from "@/hooks/use-job-polling";

interface AnalyzeEarningsFormProps {
  onTickerSelect?: (ticker: string) => void;
}

export function AnalyzeEarningsForm({ onTickerSelect }: AnalyzeEarningsFormProps) {
  const [ticker, setTicker] = useState("");
  const [transcript, setTranscript] = useState("");
  const { job, isPolling, startPolling, reset } = useJobPolling();
  const analyzeEarnings = useAnalyzeEarnings();

  function handleAnalyze() {
    if (!ticker) return;
    analyzeEarnings.mutate(
      { ticker, transcript: transcript || undefined },
      {
        onSuccess: (pendingJob) => {
          startPolling(pendingJob);
          toast.info("Earnings analysis started — this may take a minute");
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  const isRunning = analyzeEarnings.isPending || isPolling;

  const analysisText =
    job?.status === "completed"
      ? (job.result as { analysis?: string })?.analysis
      : null;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Analyze Earnings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Ticker</label>
            <StockSearchBar
              placeholder="Search ticker..."
              onSelect={(t) => {
                setTicker(t);
                reset();
                onTickerSelect?.(t);
              }}
            />
            {ticker && (
              <p className="mt-1 text-sm text-muted-foreground">
                Selected: <span className="font-medium">{ticker}</span>
              </p>
            )}
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Earnings Transcript
            </label>
            <textarea
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              rows={6}
              placeholder="Paste earnings call transcript here, or leave empty for automatic fetching..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Paste the full transcript for best results, or leave empty to
              automatically fetch the latest transcript via FMP.
            </p>
          </div>
          <Button
            onClick={handleAnalyze}
            disabled={!ticker || isRunning}
          >
            {isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {isPolling ? "Processing..." : "Submitting..."}
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Analyze
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {job?.status === "failed" && (
        <Card className="border-destructive/50">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              {job.error ?? "Analysis failed. Check your transcript and try again."}
            </p>
          </CardContent>
        </Card>
      )}

      {analysisText && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">AI Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {analysisText}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
