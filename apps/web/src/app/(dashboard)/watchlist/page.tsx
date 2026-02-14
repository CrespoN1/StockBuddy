"use client";

import { useState } from "react";
import { Eye, RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import {
  useWatchlist,
  useAddToWatchlist,
  useRemoveFromWatchlist,
  useRefreshWatchlist,
} from "@/hooks/use-watchlist";
import { formatCurrency, formatPercent } from "@/lib/format";

export default function WatchlistPage() {
  const [ticker, setTicker] = useState("");
  const { data: items, isPending, isError, error, refetch } = useWatchlist();
  const addItem = useAddToWatchlist();
  const removeItem = useRemoveFromWatchlist();
  const refreshPrices = useRefreshWatchlist();

  function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    const t = ticker.trim().toUpperCase();
    if (!t || !/^[A-Za-z.]+$/.test(t)) {
      toast.error("Enter a valid ticker symbol");
      return;
    }
    addItem.mutate(t, {
      onSuccess: () => {
        toast.success(`${t} added to watchlist`);
        setTicker("");
      },
      onError: (err) => toast.error(err.message),
    });
  }

  function handleRefresh() {
    refreshPrices.mutate(undefined, {
      onSuccess: () => toast.success("Prices refreshed"),
      onError: (err) => toast.error(err.message),
    });
  }

  if (isPending) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Watchlist</h2>
        <div className="mt-6 space-y-4">
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Watchlist</h2>
        <div className="mt-6">
          <ErrorState message={error.message} onRetry={() => refetch()} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Watchlist</h2>
          <p className="mt-1 text-muted-foreground">
            Track tickers you&apos;re interested in without adding them to a portfolio.
          </p>
        </div>
        {items && items.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshPrices.isPending}
          >
            <RefreshCw
              className={`h-3.5 w-3.5 mr-1.5 ${refreshPrices.isPending ? "animate-spin" : ""}`}
            />
            {refreshPrices.isPending ? "Refreshing..." : "Refresh Prices"}
          </Button>
        )}
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Add Ticker</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="flex gap-2">
            <Input
              placeholder="e.g. AAPL"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="max-w-xs"
              disabled={addItem.isPending}
            />
            <Button type="submit" disabled={addItem.isPending}>
              {addItem.isPending ? "Adding..." : "Add"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="mt-6">
        {!items || items.length === 0 ? (
          <EmptyState
            icon={<Eye className="h-12 w-12" />}
            title="Watchlist is empty"
            description="Add a ticker above to start tracking prices."
          />
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ticker</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead className="text-right">Daily Change</TableHead>
                  <TableHead>Sector</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => {
                  const change =
                    item.last_price != null && item.previous_close != null
                      ? item.last_price - item.previous_close
                      : null;
                  const changePct =
                    change != null && item.previous_close
                      ? (change / item.previous_close) * 100
                      : null;
                  const isPositive = change != null && change >= 0;

                  return (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.ticker}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {item.name ?? "--"}
                      </TableCell>
                      <TableCell className="text-right">
                        {item.last_price != null
                          ? formatCurrency(item.last_price)
                          : "--"}
                      </TableCell>
                      <TableCell className="text-right">
                        {change != null ? (
                          <span
                            className={isPositive ? "text-green-600" : "text-red-600"}
                          >
                            {isPositive ? "+" : ""}
                            {formatCurrency(change)}{" "}
                            ({isPositive ? "+" : ""}
                            {formatPercent(changePct! / 100)})
                          </span>
                        ) : (
                          "--"
                        )}
                      </TableCell>
                      <TableCell>{item.sector ?? "--"}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={() =>
                            removeItem.mutate(item.id, {
                              onSuccess: () =>
                                toast.success(`${item.ticker} removed`),
                              onError: (err) => toast.error(err.message),
                            })
                          }
                          disabled={removeItem.isPending}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
