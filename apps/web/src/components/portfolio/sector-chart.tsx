"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { usePortfolioSectors } from "@/hooks/use-portfolios";
import { formatCurrency, formatPercent } from "@/lib/format";

const COLORS = [
  "#2563eb", "#16a34a", "#dc2626", "#ca8a04",
  "#9333ea", "#0891b2", "#e11d48", "#ea580c",
];

interface SectorChartProps {
  portfolioId: number;
}

export function SectorChart({ portfolioId }: SectorChartProps) {
  const { data: sectors, isPending } = usePortfolioSectors(portfolioId);

  if (isPending) {
    return <Skeleton className="h-[300px] w-full" />;
  }

  if (!sectors || sectors.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No sector data available
      </p>
    );
  }

  const chartData = sectors.map((s) => ({
    name: s.sector,
    value: s.value,
    weight: s.weight,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
          label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(1)}%`}
        >
          {chartData.map((_, index) => (
            <Cell
              key={`cell-${index}`}
              fill={COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => formatCurrency(Number(value))}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
