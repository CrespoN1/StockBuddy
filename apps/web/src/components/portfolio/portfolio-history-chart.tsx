"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePortfolioHistoryWithBenchmark } from "@/hooks/use-portfolios";

interface Props {
  portfolioId: number;
}

export function PortfolioHistoryChart({ portfolioId }: Props) {
  const { data: response, isPending } =
    usePortfolioHistoryWithBenchmark(portfolioId);

  if (isPending) return <Skeleton className="h-[300px] w-full" />;
  if (!response || response.data.length < 2) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Portfolio vs S&amp;P 500</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Run &quot;Analyze Portfolio&quot; at least twice to see your performance compared to the S&amp;P 500.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">
          Portfolio vs S&P 500
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={response.data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              className="text-muted-foreground"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              tickFormatter={(v: number) => `${v > 0 ? "+" : ""}${v.toFixed(1)}%`}
              className="text-muted-foreground"
              width={65}
            />
            <Tooltip
              formatter={(value, name) => {
                const v = Number(value);
                return [
                  `${v > 0 ? "+" : ""}${v.toFixed(2)}%`,
                  name === "portfolio_pct" ? "Portfolio" : "S&P 500",
                ];
              }}
              labelStyle={{ fontWeight: 600 }}
            />
            <Legend
              formatter={(value: string) =>
                value === "portfolio_pct" ? "Portfolio" : "S&P 500"
              }
            />
            <Line
              type="monotone"
              dataKey="portfolio_pct"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="sp500_pct"
              stroke="hsl(var(--muted-foreground))"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
