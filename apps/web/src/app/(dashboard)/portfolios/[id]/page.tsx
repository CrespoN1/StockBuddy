"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { HoldingsTable } from "@/components/portfolio/holdings-table";
import { AddHoldingForm } from "@/components/portfolio/add-holding-form";
import { SectorChart } from "@/components/portfolio/sector-chart";
import { PortfolioAnalysisPanel } from "@/components/portfolio/portfolio-analysis-panel";
import { PortfolioNewsPanel } from "@/components/portfolio/portfolio-news-panel";
import { usePortfolio, usePortfolioSnapshot, usePortfolioEarningsInsights } from "@/hooks/use-portfolios";
import { formatCurrency, formatPercent } from "@/lib/format";

export default function PortfolioDetailPage() {
  const { id } = useParams<{ id: string }>();
  const portfolioId = parseInt(id, 10);

  const { data: portfolio, isPending, isError, error, refetch } = usePortfolio(portfolioId);
  const { data: snapshot } = usePortfolioSnapshot(portfolioId, !!portfolio);
  const { data: insights } = usePortfolioEarningsInsights(portfolioId);

  if (isPending) {
    return (
      <div>
        <Skeleton className="h-8 w-48" />
        <div className="mt-6 space-y-4">
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    return <ErrorState message={error.message} onRetry={() => refetch()} />;
  }

  if (!portfolio) {
    return <ErrorState message="Portfolio not found" />;
  }

  return (
    <div>
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/portfolios">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h2 className="text-2xl font-bold tracking-tight">{portfolio.name}</h2>
      </div>

      <Tabs defaultValue="holdings" className="mt-6">
        <TabsList>
          <TabsTrigger value="holdings">Holdings</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="news">News & Sentiment</TabsTrigger>
          <TabsTrigger value="earnings">Earnings Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="holdings" className="space-y-6">
          <HoldingsTable
            holdings={portfolio.holdings}
            portfolioId={portfolioId}
            portfolioName={portfolio.name}
          />
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Add Holding</CardTitle>
            </CardHeader>
            <CardContent>
              <AddHoldingForm portfolioId={portfolioId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          {snapshot && (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground">Total Value</p>
                  <p className="mt-1 text-lg font-semibold">
                    {snapshot.total_value != null
                      ? formatCurrency(snapshot.total_value)
                      : "--"}
                  </p>
                  {snapshot.daily_change != null && (
                    <p
                      className={`text-xs font-medium ${
                        snapshot.daily_change >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {snapshot.daily_change >= 0 ? "+" : ""}
                      {formatCurrency(snapshot.daily_change)}
                      {snapshot.daily_change_pct != null &&
                        ` (${snapshot.daily_change_pct >= 0 ? "+" : ""}${snapshot.daily_change_pct.toFixed(2)}%)`}
                    </p>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground">Health Score</p>
                  <p className="mt-1 text-lg font-semibold">
                    {snapshot.health_score != null
                      ? `${snapshot.health_score}/100`
                      : "--"}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground">Positions</p>
                  <p className="mt-1 text-lg font-semibold">
                    {snapshot.num_positions}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground">
                    Concentration Risk
                  </p>
                  <p className="mt-1 text-lg font-semibold">
                    {snapshot.concentration_risk != null
                      ? formatPercent(snapshot.concentration_risk)
                      : "--"}
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Sector Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <SectorChart portfolioId={portfolioId} />
            </CardContent>
          </Card>

          <PortfolioAnalysisPanel portfolioId={portfolioId} />
        </TabsContent>

        <TabsContent value="news">
          <PortfolioNewsPanel portfolioId={portfolioId} />
        </TabsContent>

        <TabsContent value="earnings" className="space-y-4">
          {insights ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Sentiment Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-3">
                    {Object.entries(insights.sentiment_summary).map(
                      ([key, count]) => (
                        <div
                          key={key}
                          className="rounded-md border px-3 py-2 text-center"
                        >
                          <p className="text-xs capitalize text-muted-foreground">
                            {key.replace("_", " ")}
                          </p>
                          <p className="text-lg font-semibold">{count}</p>
                        </div>
                      )
                    )}
                  </div>
                </CardContent>
              </Card>

              {insights.positive_outlooks.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">
                      Positive Outlooks
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {insights.positive_outlooks.map((ticker) => (
                        <Badge key={ticker} variant="default">
                          {ticker}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {insights.risk_warnings.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Risk Warnings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {insights.risk_warnings.map((ticker) => (
                        <Badge key={ticker} variant="destructive">
                          {ticker}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {insights.holdings_with_recent_earnings.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">
                      Holdings with Recent Earnings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {insights.holdings_with_recent_earnings.map((ticker) => (
                        <Badge key={ticker} variant="secondary">
                          {ticker}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Skeleton className="h-48 w-full" />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
