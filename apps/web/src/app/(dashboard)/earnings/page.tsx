"use client";

import { useState } from "react";
import { FileText } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { AnalyzeEarningsForm } from "@/components/earnings/analyze-earnings-form";
import { EarningsCard } from "@/components/earnings/earnings-card";
import { useEarnings } from "@/hooks/use-earnings";
import { EarningsCalendar } from "@/components/portfolio/earnings-calendar";

export default function EarningsPage() {
  const [selectedTicker, setSelectedTicker] = useState("");
  const { data: earnings, isPending } = useEarnings(selectedTicker);

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Earnings Analysis</h2>
      <p className="mt-2 text-muted-foreground">
        Analyze earnings call transcripts with AI to extract sentiment, key
        metrics, and growth insights.
      </p>

      <div className="mt-6">
        <EarningsCalendar />
      </div>

      <div className="mt-6">
        <AnalyzeEarningsForm onTickerSelect={setSelectedTicker} />
      </div>

      {selectedTicker && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold">
            Earnings History — {selectedTicker}
          </h3>
          <div className="mt-4 space-y-4">
            {isPending ? (
              Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))
            ) : earnings && earnings.length > 0 ? (
              earnings.map((ec) => <EarningsCard key={ec.id} earnings={ec} />)
            ) : (
              <EmptyState
                icon={<FileText className="h-10 w-10" />}
                title={`No earnings data for ${selectedTicker}`}
                description="Run an analysis above to get started."
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
