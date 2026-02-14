"use client";

import Link from "next/link";
import { CalendarDays } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useEarningsCalendar } from "@/hooks/use-portfolios";
import { formatCurrency } from "@/lib/format";
import type { HoldingRead } from "@/types";

function groupByTimeframe(holdings: HoldingRead[]) {
  const now = new Date();
  const endOfWeek = new Date(now);
  endOfWeek.setDate(now.getDate() + (7 - now.getDay()));
  const endOfNextWeek = new Date(endOfWeek);
  endOfNextWeek.setDate(endOfNextWeek.getDate() + 7);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);

  const groups: Record<string, HoldingRead[]> = {
    "This Week": [],
    "Next Week": [],
    "This Month": [],
    Later: [],
  };

  for (const h of holdings) {
    if (!h.next_earnings_date) continue;
    const d = new Date(h.next_earnings_date + "T00:00:00");
    if (d <= endOfWeek) groups["This Week"].push(h);
    else if (d <= endOfNextWeek) groups["Next Week"].push(h);
    else if (d <= endOfMonth) groups["This Month"].push(h);
    else groups["Later"].push(h);
  }

  return groups;
}

export function EarningsCalendar() {
  const { data: holdings, isPending } = useEarningsCalendar();

  if (isPending) return <Skeleton className="h-[200px] w-full" />;
  if (!holdings || holdings.length === 0) {
    return (
      <EmptyState
        icon={<CalendarDays className="h-10 w-10" />}
        title="No upcoming earnings"
        description="Add holdings to your portfolios and refresh prices to see upcoming earnings dates."
      />
    );
  }

  const groups = groupByTimeframe(holdings);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <CalendarDays className="h-4 w-4" />
          Upcoming Earnings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {Object.entries(groups).map(([label, items]) => {
          if (items.length === 0) return null;
          return (
            <div key={label}>
              <h4 className="mb-2 text-sm font-medium text-muted-foreground">
                {label}
              </h4>
              <div className="space-y-2">
                {items.map((h) => (
                  <div
                    key={`${h.id}-${h.ticker}`}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <Link href={`/stocks/${h.ticker}`}>
                        <Badge variant="secondary" className="cursor-pointer">
                          {h.ticker}
                        </Badge>
                      </Link>
                      <span className="text-sm text-muted-foreground">
                        {new Date(
                          h.next_earnings_date + "T00:00:00"
                        ).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      {h.last_price != null
                        ? formatCurrency(h.last_price)
                        : "--"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
