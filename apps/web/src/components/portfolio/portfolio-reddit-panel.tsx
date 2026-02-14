"use client";

import {
  ExternalLink,
  MessageSquare,
  ArrowBigUp,
  MessageCircle,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { usePortfolioReddit } from "@/hooks/use-portfolios";
import type { RedditPost } from "@/types";

interface Props {
  portfolioId: number;
}

function formatRelativeTime(utcSeconds: number): string {
  const now = Date.now() / 1000;
  const diff = now - utcSeconds;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function groupByTicker(posts: RedditPost[]): Record<string, RedditPost[]> {
  const groups: Record<string, RedditPost[]> = {};
  for (const post of posts) {
    if (!groups[post.ticker]) groups[post.ticker] = [];
    groups[post.ticker].push(post);
  }
  return groups;
}

export function PortfolioRedditPanel({ portfolioId }: Props) {
  const { data: posts, isPending, isError } = usePortfolioReddit(portfolioId);

  if (isPending) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !posts || posts.length === 0) {
    return (
      <EmptyState
        icon={<MessageSquare className="h-10 w-10" />}
        title="No Reddit discussions found"
        description="No recent discussions found for your portfolio holdings on finance subreddits."
      />
    );
  }

  const grouped = groupByTicker(posts);

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([ticker, tickerPosts]) => (
        <div key={ticker}>
          <div className="mb-3 flex items-center gap-2">
            <Badge variant="default" className="text-sm">
              {ticker}
            </Badge>
            <span className="text-sm text-muted-foreground">
              {tickerPosts.length} post{tickerPosts.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="space-y-3">
            {tickerPosts.map((post, i) => (
              <Card key={i} className="overflow-hidden">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <a
                        href={post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-primary hover:underline line-clamp-2"
                      >
                        {post.title}
                        <ExternalLink className="ml-1 inline h-3 w-3" />
                      </a>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        <Badge variant="secondary" className="text-xs">
                          r/{post.subreddit}
                        </Badge>
                        {post.flair && (
                          <Badge variant="outline" className="text-xs">
                            {post.flair}
                          </Badge>
                        )}
                        <span>u/{post.author}</span>
                        <span>&middot;</span>
                        <span>{formatRelativeTime(post.created_utc)}</span>
                      </div>
                      {post.selftext_preview && (
                        <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                          {post.selftext_preview}
                        </p>
                      )}
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <ArrowBigUp className="h-4 w-4" />
                        <span>{post.score.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageCircle className="h-3 w-3" />
                        <span>{post.num_comments.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
