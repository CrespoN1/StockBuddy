"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ErrorState } from "@/components/ui/error-state";
import { CandlestickChart } from "@/components/stock/candlestick-chart";
import { TechnicalsPanel } from "@/components/stock/technicals-panel";
import { FundamentalsCard } from "@/components/stock/fundamentals-card";
import { NewsPanel } from "@/components/stock/news-panel";
import { ForecastPanel } from "@/components/stock/forecast-panel";
import { useStockInfo, useStockQuote, useStockHistory } from "@/hooks/use-stocks";
import { useEarnings } from "@/hooks/use-earnings";
import { formatCurrency, formatDate } from "@/lib/format";

const PERIODS = [
  { value: "1mo", label: "1M" },
  { value: "3mo", label: "3M" },
  { value: "6mo", label: "6M" },
  { value: "1y", label: "1Y" },
  { value: "2y", label: "2Y" },
  { value: "5y", label: "5Y" },
];

export default function StockDetailPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const [period, setPeriod] = useState("1y");

  const { data: info, isPending: infoLoading, isError: infoError } = useStockInfo(ticker);
  const { data: quote } = useStockQuote(ticker);
  const { data: history, isPending: historyLoading } = useStockHistory(ticker, period);
  const { data: earnings } = useEarnings(ticker);

  if (infoError) {
    return (
      <div>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/stocks">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Link>
        </Button>
        <div className="mt-6">
          <ErrorState message={`Stock "${ticker}" not found`} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/stocks">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight">
              {ticker.toUpperCase()}
            </h2>
            {infoLoading ? (
              <Skeleton className="h-5 w-32" />
            ) : info ? (
              <span className="text-lg text-muted-foreground">{info.name}</span>
            ) : null}
          </div>
          <div className="flex items-center gap-2 mt-1">
            {quote?.price != null ? (
              <span className="text-xl font-semibold">
                {formatCurrency(quote.price)}
              </span>
            ) : (
              <Skeleton className="h-7 w-20" />
            )}
            {quote?.currency && (
              <Badge variant="secondary">{quote.currency}</Badge>
            )}
          </div>
        </div>
      </div>

      <Tabs defaultValue="chart" className="mt-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="chart">Chart</TabsTrigger>
          <TabsTrigger value="company">Company</TabsTrigger>
          <TabsTrigger value="news">News</TabsTrigger>
          <TabsTrigger value="forecast">Forecast</TabsTrigger>
          <TabsTrigger value="earnings">Earnings</TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="space-y-4">
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PERIODS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Card>
            <CardContent className="p-4">
              {historyLoading ? (
                <Skeleton className="h-[400px] w-full" />
              ) : (
                <CandlestickChart data={history ?? []} />
              )}
            </CardContent>
          </Card>
          <TechnicalsPanel ticker={ticker} />
        </TabsContent>

        <TabsContent value="company">
          <FundamentalsCard ticker={ticker} />
        </TabsContent>

        <TabsContent value="news">
          <NewsPanel ticker={ticker} />
        </TabsContent>

        <TabsContent value="forecast">
          <ForecastPanel ticker={ticker} />
        </TabsContent>

        <TabsContent value="earnings" className="space-y-4">
          {earnings && earnings.length > 0 ? (
            earnings.map((ec) => (
              <Card key={ec.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">
                      {ec.call_date
                        ? formatDate(ec.call_date)
                        : formatDate(ec.created_at)}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      {ec.guidance_outlook && (
                        <Badge
                          variant={
                            ec.guidance_outlook === "positive"
                              ? "default"
                              : ec.guidance_outlook === "negative"
                                ? "destructive"
                                : "secondary"
                          }
                        >
                          {ec.guidance_outlook}
                        </Badge>
                      )}
                      {ec.sentiment_score != null && (
                        <Badge
                          variant={
                            ec.sentiment_score > 0.2
                              ? "default"
                              : ec.sentiment_score < -0.1
                                ? "destructive"
                                : "secondary"
                          }
                        >
                          Sentiment: {ec.sentiment_score.toFixed(2)}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {ec.summary && (
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                      {ec.summary}
                    </p>
                  )}
                  {(ec.risk_mentions != null || ec.growth_mentions != null) && (
                    <div className="mt-3 flex gap-3">
                      {ec.growth_mentions != null && (
                        <Badge variant="secondary">
                          Growth mentions: {ec.growth_mentions}
                        </Badge>
                      )}
                      {ec.risk_mentions != null && (
                        <Badge variant="secondary">
                          Risk mentions: {ec.risk_mentions}
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-sm text-muted-foreground">
                No earnings data available for {ticker.toUpperCase()}. Run an
                analysis from the{" "}
                <Link
                  href="/earnings"
                  className="text-primary hover:underline"
                >
                  Earnings page
                </Link>{" "}
                to get started.
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
