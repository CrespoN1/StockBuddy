"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/format";
import type { EarningsCallRead } from "@/types";

interface EarningsCardProps {
  earnings: EarningsCallRead;
}

export function EarningsCard({ earnings }: EarningsCardProps) {
  const [expanded, setExpanded] = useState(false);

  const sentimentVariant =
    earnings.sentiment_score != null && earnings.sentiment_score > 0.2
      ? "default"
      : earnings.sentiment_score != null && earnings.sentiment_score < -0.1
        ? "destructive"
        : "secondary";

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Badge>{earnings.ticker}</Badge>
            <CardTitle className="text-sm font-normal text-muted-foreground">
              {earnings.call_date
                ? formatDate(earnings.call_date)
                : formatDate(earnings.created_at)}
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {earnings.sentiment_score != null && (
              <Badge variant={sentimentVariant}>
                Sentiment: {earnings.sentiment_score.toFixed(2)}
              </Badge>
            )}
            {earnings.guidance_outlook && (
              <Badge
                variant={
                  earnings.guidance_outlook === "positive"
                    ? "default"
                    : earnings.guidance_outlook === "negative"
                      ? "destructive"
                      : "secondary"
                }
              >
                {earnings.guidance_outlook}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {earnings.summary ? (
          <div>
            <p
              className={`whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground ${
                !expanded ? "line-clamp-3" : ""
              }`}
            >
              {earnings.summary}
            </p>
            {earnings.summary.split("\n").length > 3 && (
              <Button
                variant="link"
                size="sm"
                className="mt-1 h-auto p-0 text-xs"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? "Show less" : "Show more"}
              </Button>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No summary available</p>
        )}
        {(earnings.risk_mentions != null || earnings.growth_mentions != null) && (
          <div className="mt-3 flex gap-2">
            {earnings.growth_mentions != null && (
              <Badge variant="secondary">
                Growth: {earnings.growth_mentions}
              </Badge>
            )}
            {earnings.risk_mentions != null && (
              <Badge variant="secondary">
                Risk: {earnings.risk_mentions}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
