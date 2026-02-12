"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useStockForecast } from "@/hooks/use-stocks";
import { formatCurrency } from "@/lib/format";

interface ForecastPanelProps {
  ticker: string;
}

const FORECAST_PERIODS = [
  { value: "14", label: "2 Weeks" },
  { value: "30", label: "1 Month" },
  { value: "60", label: "2 Months" },
  { value: "90", label: "3 Months" },
];

function TrendIcon({ signal }: { signal: string }) {
  if (signal === "Bullish") return <TrendingUp className="h-5 w-5 text-green-500" />;
  if (signal === "Bearish") return <TrendingDown className="h-5 w-5 text-red-500" />;
  return <Minus className="h-5 w-5 text-yellow-500" />;
}

function trendBadgeVariant(signal: string): "default" | "secondary" | "destructive" {
  if (signal === "Bullish") return "default";
  if (signal === "Bearish") return "destructive";
  return "secondary";
}

export function ForecastPanel({ ticker }: ForecastPanelProps) {
  const [days, setDays] = useState("30");
  const { data: forecast, isPending, isError } = useStockForecast(ticker, parseInt(days));

  if (isPending) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-32" />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <Skeleton className="h-[300px] w-full" />
      </div>
    );
  }

  if (isError || !forecast) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          Unable to generate forecast for {ticker.toUpperCase()}. Insufficient historical data.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold">Price Forecast</h3>
        </div>
        <Select value={days} onValueChange={setDays}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {FORECAST_PERIODS.map((p) => (
              <SelectItem key={p.value} value={p.value}>
                {p.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Current Price</p>
            <p className="mt-1 text-lg font-semibold">
              {formatCurrency(forecast.current_price)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">
              Predicted ({days}d)
            </p>
            <div className="mt-1 flex items-center gap-2">
              <p className="text-lg font-semibold">
                {formatCurrency(forecast.predicted_price)}
              </p>
              <TrendIcon signal={forecast.trend_signal} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Expected Change</p>
            <p
              className={`mt-1 text-lg font-semibold ${
                forecast.pct_change > 0
                  ? "text-green-600"
                  : forecast.pct_change < 0
                    ? "text-red-600"
                    : ""
              }`}
            >
              {forecast.pct_change > 0 ? "+" : ""}
              {forecast.pct_change.toFixed(2)}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Signal</p>
            <div className="mt-1">
              <Badge variant={trendBadgeVariant(forecast.trend_signal)}>
                {forecast.trend_signal}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Technical Indicators */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Technical Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <p className="text-xs text-muted-foreground">RSI (14)</p>
              <p className="text-sm font-medium">
                {forecast.rsi.toFixed(1)}
                <span className="ml-1 text-xs text-muted-foreground">
                  {forecast.rsi > 70
                    ? "(Overbought)"
                    : forecast.rsi < 30
                      ? "(Oversold)"
                      : "(Neutral)"}
                </span>
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">MA 20</p>
              <p className="text-sm font-medium">{formatCurrency(forecast.ma_20)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">MA 50</p>
              <p className="text-sm font-medium">{formatCurrency(forecast.ma_50)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">R-squared</p>
              <p className="text-sm font-medium">
                {(forecast.model_info?.r_squared ?? 0).toFixed(4)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Forecast Table */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Forecast Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="pb-2 pr-4">Date</th>
                  <th className="pb-2 pr-4 text-right">Predicted</th>
                  <th className="pb-2 pr-4 text-right">Low</th>
                  <th className="pb-2 text-right">High</th>
                </tr>
              </thead>
              <tbody>
                {/* Show every 7th day for readability */}
                {(forecast.forecast?.dates ?? [])
                  .map((date, i) => ({
                    date,
                    price: forecast.forecast?.prices[i],
                    low: forecast.forecast?.lower_bound[i],
                    high: forecast.forecast?.upper_bound[i],
                  }))
                  .filter((_, i) => i % 7 === 6 || i === (forecast.forecast?.dates ?? []).length - 1)
                  .map((row) => (
                    <tr key={row.date} className="border-b last:border-0">
                      <td className="py-2 pr-4">{row.date}</td>
                      <td className="py-2 pr-4 text-right font-medium">
                        {formatCurrency(row.price)}
                      </td>
                      <td className="py-2 pr-4 text-right text-muted-foreground">
                        {formatCurrency(row.low)}
                      </td>
                      <td className="py-2 text-right text-muted-foreground">
                        {formatCurrency(row.high)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Model Info */}
      <Card>
        <CardContent className="p-4">
          <p className="text-xs text-muted-foreground">
            Model: {forecast.model_info?.method ?? "N/A"} &middot; Training: {forecast.model_info?.training_period ?? "N/A"} &middot; Trend: {(forecast.model_info?.slope_per_day ?? 0) > 0 ? "+" : ""}{(forecast.model_info?.slope_per_day ?? 0).toFixed(4)}/day
          </p>
          <p className="mt-1 text-xs text-muted-foreground italic">
            Disclaimer: This forecast is for educational purposes only and should not be used as investment advice. Past performance does not guarantee future results.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
