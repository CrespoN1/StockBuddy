"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useStockTechnicals } from "@/hooks/use-stocks";
import { formatCurrency, formatNumber } from "@/lib/format";

interface TechnicalsPanelProps {
  ticker: string;
}

export function TechnicalsPanel({ ticker }: TechnicalsPanelProps) {
  const { data, isPending, isError } = useStockTechnicals(ticker);

  if (isPending) return <Skeleton className="h-48 w-full" />;
  if (isError || !data) return null;

  const rsiColor =
    data.rsi_signal === "Overbought"
      ? "destructive"
      : data.rsi_signal === "Oversold"
        ? "default"
        : "secondary";

  const volumeLabel =
    data.volume_ratio > 1.5
      ? "High Volume"
      : data.volume_ratio < 0.7
        ? "Low Volume"
        : "Normal";

  const volumeVariant =
    data.volume_ratio > 1.5
      ? "default"
      : data.volume_ratio < 0.7
        ? "destructive"
        : "secondary";

  function maComparison(ma: number | null, label: string) {
    if (ma === null) return null;
    const above = (data?.current_price ?? 0) > ma;
    return (
      <div className="flex items-center justify-between rounded-md border px-3 py-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{formatCurrency(ma)}</span>
          {above ? (
            <TrendingUp className="h-4 w-4 text-green-600" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-600" />
          )}
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Technical Indicators</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-md border px-3 py-2">
            <p className="text-xs text-muted-foreground">Current Price</p>
            <p className="text-lg font-semibold">
              {formatCurrency(data.current_price)}
            </p>
          </div>
          <div className="rounded-md border px-3 py-2">
            <p className="text-xs text-muted-foreground">RSI (14)</p>
            <div className="flex items-center gap-2">
              <p className="text-lg font-semibold">
                {data.rsi_14 !== null ? data.rsi_14.toFixed(1) : "--"}
              </p>
              <Badge variant={rsiColor}>{data.rsi_signal}</Badge>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium">Moving Averages</p>
          {maComparison(data.ma_20, "MA 20")}
          {maComparison(data.ma_50, "MA 50")}
          {maComparison(data.ma_200, "MA 200")}
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border px-3 py-2">
            <p className="text-xs text-muted-foreground">Volume Ratio</p>
            <div className="flex items-center gap-2">
              <p className="font-medium">{data.volume_ratio.toFixed(2)}x</p>
              <Badge variant={volumeVariant}>{volumeLabel}</Badge>
            </div>
          </div>
          <div className="rounded-md border px-3 py-2">
            <p className="text-xs text-muted-foreground">Support</p>
            <p className="font-medium">
              {data.support !== null ? formatCurrency(data.support) : "--"}
            </p>
          </div>
          <div className="rounded-md border px-3 py-2">
            <p className="text-xs text-muted-foreground">Resistance</p>
            <p className="font-medium">
              {data.resistance !== null ? formatCurrency(data.resistance) : "--"}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
