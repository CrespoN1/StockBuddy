"use client";

import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ComparisonResult } from "@/components/compare/comparison-result";
import { usePastComparisons } from "@/hooks/use-analysis";
import { formatDate } from "@/lib/format";
import type { JobStatus } from "@/types";

export function PastComparisons() {
  const { data: comparisons, isPending } = usePastComparisons();
  const [selected, setSelected] = useState<JobStatus | null>(null);

  if (isPending) return <Skeleton className="h-[80px] w-full" />;
  if (!comparisons || comparisons.length === 0) return null;

  if (selected) {
    const tickers =
      (selected.input_data?.tickers as string[]) ?? [];
    return (
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelected(null)}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to past comparisons
        </Button>
        <ComparisonResult job={selected} tickers={tickers} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Past Comparisons</h3>
      <div className="grid gap-3 sm:grid-cols-2">
        {comparisons.map((c) => {
          const tickers = (c.input_data?.tickers as string[]) ?? [];
          return (
            <Card
              key={c.id}
              className="cursor-pointer transition-colors hover:bg-accent"
              onClick={() => setSelected(c)}
            >
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-1 mb-2">
                  {tickers.map((t) => (
                    <Badge key={t} variant="secondary">
                      {t}
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {c.completed_at
                    ? formatDate(c.completed_at)
                    : formatDate(c.created_at)}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
