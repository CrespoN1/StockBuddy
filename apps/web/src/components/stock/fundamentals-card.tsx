"use client";

import { ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useStockInfo } from "@/hooks/use-stocks";
import { formatNumber } from "@/lib/format";

interface FundamentalsCardProps {
  ticker: string;
}

export function FundamentalsCard({ ticker }: FundamentalsCardProps) {
  const { data, isPending, isError } = useStockInfo(ticker);

  if (isPending) return <Skeleton className="h-64 w-full" />;
  if (isError || !data) return null;

  const metrics = [
    { label: "Market Cap", value: data.market_cap },
    { label: "P/E Ratio", value: formatNumber(data.pe_ratio) },
    { label: "Forward P/E", value: formatNumber(data.forward_pe) },
    { label: "Beta", value: formatNumber(data.beta) },
    { label: "52W High", value: formatNumber(data.week_52_high) },
    { label: "52W Low", value: formatNumber(data.week_52_low) },
    { label: "Dividend Yield", value: formatNumber(data.dividend_yield) },
    { label: "Avg Volume", value: formatNumber(data.avg_volume) },
    { label: "Volume", value: formatNumber(data.volume) },
    { label: "Employees", value: formatNumber(data.employees) },
  ];

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Key Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {metrics.map((m) => (
              <div key={m.label} className="flex justify-between rounded-md border px-3 py-2">
                <span className="text-sm text-muted-foreground">{m.label}</span>
                <span className="text-sm font-medium">{m.value}</span>
              </div>
            ))}
          </div>
          {data.website && data.website !== "N/A" && (
            <a
              href={data.website}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              {data.website}
            </a>
          )}
        </CardContent>
      </Card>

      {data.summary && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">About</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {data.summary}
            </p>
          </CardContent>
        </Card>
      )}

      {data.latest_recommendation && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Latest Recommendation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Firm: </span>
                <span className="font-medium">{data.latest_recommendation.firm}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Rating: </span>
                <span className="font-medium">{data.latest_recommendation.rating}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Action: </span>
                <span className="font-medium">{data.latest_recommendation.action}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {data.top_institutional && data.top_institutional.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top Institutional Holders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.top_institutional.map((holder, i) => (
                <div key={i} className="flex justify-between rounded-md border px-3 py-2 text-sm">
                  <span>{String(holder.Holder ?? holder.holder ?? `Holder ${i + 1}`)}</span>
                  <span className="text-muted-foreground">
                    {String(holder.Shares ?? holder.shares ?? "")}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
