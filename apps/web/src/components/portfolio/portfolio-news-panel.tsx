"use client";

import { ExternalLink, Newspaper } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { usePortfolioNews } from "@/hooks/use-portfolios";

interface PortfolioNewsPanelProps {
  portfolioId: number;
}

function sentimentColor(label: string): "default" | "secondary" | "destructive" {
  const l = label.toLowerCase();
  if (l.includes("bullish") || l.includes("positive")) return "default";
  if (l.includes("bearish") || l.includes("negative")) return "destructive";
  return "secondary";
}

function formatNewsDate(raw: string): string {
  if (raw.length >= 8) {
    const y = raw.slice(0, 4);
    const m = raw.slice(4, 6);
    const d = raw.slice(6, 8);
    return `${m}/${d}/${y}`;
  }
  return raw;
}

export function PortfolioNewsPanel({ portfolioId }: PortfolioNewsPanelProps) {
  const { data: articles, isPending, isError } = usePortfolioNews(portfolioId);

  if (isPending) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !articles || articles.length === 0) {
    return (
      <EmptyState
        icon={<Newspaper className="h-10 w-10" />}
        title="No news available"
        description="No recent news found for your portfolio holdings."
      />
    );
  }

  return (
    <div className="space-y-3">
      {articles.map((article, i) => (
        <Card key={i} className="overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium hover:underline text-primary line-clamp-2"
                >
                  {article.title}
                  <ExternalLink className="inline ml-1 h-3 w-3" />
                </a>
                <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{article.source}</span>
                  <span>&middot;</span>
                  <span>{formatNewsDate(article.published_at)}</span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                  {article.summary}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <Badge variant={sentimentColor(article.ticker_sentiment_label)} className="text-xs">
                  {article.ticker_sentiment_label}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {article.ticker_sentiment_score.toFixed(3)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
