"use client";

import Link from "next/link";
import { useQueries } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { Briefcase, DollarSign, Heart, BarChart3, Plus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { usePortfolios } from "@/hooks/use-portfolios";
import { createClientFetch } from "@/lib/api";
import { formatCurrency, formatPercent, formatDate } from "@/lib/format";
import type { PortfolioSnapshotRead } from "@/types";

export default function DashboardPage() {
  const { getToken } = useAuth();
  const { data: portfolios, isPending, isError, error, refetch } = usePortfolios();

  const fetchApi = createClientFetch(getToken);
  const snapshotQueries = useQueries({
    queries: (portfolios ?? []).map((p) => ({
      queryKey: ["portfolios", p.id, "snapshot"],
      queryFn: () =>
        fetchApi<PortfolioSnapshotRead>(`/api/v1/portfolios/${p.id}/snapshot`),
      enabled: !!portfolios && portfolios.length > 0,
    })),
  });

  const snapshotsLoading = snapshotQueries.some((q) => q.isPending);
  const snapshots = snapshotQueries
    .map((q) => q.data)
    .filter((s): s is PortfolioSnapshotRead => !!s);

  const totalValue = snapshots.reduce((sum, s) => sum + (s.total_value ?? 0), 0);
  const totalDailyChange = snapshots.reduce((sum, s) => sum + (s.daily_change ?? 0), 0);
  const hasDailyChange = snapshots.some((s) => s.daily_change != null);
  const totalPrevValue = totalValue - totalDailyChange;
  const totalDailyChangePct = totalPrevValue > 0 ? (totalDailyChange / totalPrevValue) * 100 : null;
  const totalPositions = snapshots.reduce((sum, s) => sum + s.num_positions, 0);
  const avgHealthScore =
    snapshots.length > 0
      ? Math.round(
          snapshots.reduce((sum, s) => sum + (s.health_score ?? 0), 0) /
            snapshots.length
        )
      : null;
  const avgEarningsCoverage =
    snapshots.length > 0
      ? snapshots.reduce((sum, s) => sum + (s.recent_earnings_coverage ?? 0), 0) /
        snapshots.length
      : null;

  if (isPending) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="mt-2 h-8 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <div className="mt-8">
          <ErrorState message={error.message} onRetry={() => refetch()} />
        </div>
      </div>
    );
  }

  if (!portfolios || portfolios.length === 0) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <div className="mt-8">
          <EmptyState
            icon={<Briefcase className="h-12 w-12" />}
            title="No portfolios yet"
            description="Create your first portfolio and add holdings to get started with AI-powered analysis."
            action={
              <Button asChild>
                <Link href="/portfolios">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Portfolio
                </Link>
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: "Total Portfolio Value",
      value: snapshotsLoading ? null : formatCurrency(totalValue),
      icon: DollarSign,
    },
    {
      label: "Health Score",
      value: snapshotsLoading ? null : avgHealthScore !== null ? `${avgHealthScore}/100` : "--",
      icon: Heart,
    },
    {
      label: "Positions",
      value: snapshotsLoading ? null : String(totalPositions),
      icon: Briefcase,
    },
    {
      label: "Earnings Coverage",
      value:
        snapshotsLoading
          ? null
          : avgEarningsCoverage !== null
            ? formatPercent(avgEarningsCoverage)
            : "--",
      icon: BarChart3,
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
      <p className="mt-2 text-muted-foreground">
        Overview of your portfolio performance and earnings insights.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center gap-2">
                <stat.icon className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
              {stat.value === null ? (
                <Skeleton className="mt-2 h-8 w-20" />
              ) : (
                <p className="mt-1 text-2xl font-semibold">{stat.value}</p>
              )}
              {stat.label === "Total Portfolio Value" && !snapshotsLoading && hasDailyChange && (
                <p
                  className={`text-xs font-medium ${
                    totalDailyChange >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {totalDailyChange >= 0 ? "+" : ""}
                  {formatCurrency(totalDailyChange)}
                  {totalDailyChangePct != null &&
                    ` (${totalDailyChangePct >= 0 ? "+" : ""}${totalDailyChangePct.toFixed(2)}%)`}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Your Portfolios</h3>
          <Button variant="outline" size="sm" asChild>
            <Link href="/portfolios">View all</Link>
          </Button>
        </div>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {portfolios.slice(0, 6).map((portfolio) => (
            <Link
              key={portfolio.id}
              href={`/portfolios/${portfolio.id}`}
            >
              <Card className="transition-colors hover:bg-accent">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{portfolio.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Created {formatDate(portfolio.created_at)}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
