"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePortfolioHistory } from "@/hooks/use-portfolios";
import { formatCurrency } from "@/lib/format";

interface Props {
  portfolioId: number;
}

export function PortfolioHistoryChart({ portfolioId }: Props) {
  const { data: snapshots, isPending } = usePortfolioHistory(portfolioId);

  if (isPending) return <Skeleton className="h-[300px] w-full" />;
  if (!snapshots || snapshots.length < 2) return null;

  const chartData = snapshots.map((s) => ({
    date: new Date(s.created_at).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    value: s.total_value ?? 0,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Portfolio Value History</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              className="text-muted-foreground"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
              className="text-muted-foreground"
              width={60}
            />
            <Tooltip
              formatter={(value) => [formatCurrency(Number(value)), "Value"]}
              labelStyle={{ fontWeight: 600 }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
