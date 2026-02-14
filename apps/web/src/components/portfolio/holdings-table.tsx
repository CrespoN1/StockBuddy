"use client";

import { useState } from "react";
import Link from "next/link";
import { Download, Pencil, RefreshCw, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { useUpdateHolding, useDeleteHolding, useRefreshHoldings } from "@/hooks/use-holdings";
import { formatCurrency, formatNumber } from "@/lib/format";
import { exportHoldingsCSV } from "@/lib/csv-export";
import type { HoldingRead } from "@/types";
import { holdingValue } from "@/types";

interface HoldingsTableProps {
  holdings: HoldingRead[];
  portfolioId: number;
  portfolioName?: string;
}

export function HoldingsTable({ holdings, portfolioId, portfolioName }: HoldingsTableProps) {
  const [editingHolding, setEditingHolding] = useState<HoldingRead | null>(null);
  const [editShares, setEditShares] = useState("");
  const updateHolding = useUpdateHolding(portfolioId);
  const deleteHolding = useDeleteHolding(portfolioId);
  const refreshHoldings = useRefreshHoldings(portfolioId);

  function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!editingHolding) return;
    const shares = parseFloat(editShares);
    if (isNaN(shares) || shares <= 0) return;
    updateHolding.mutate(
      { holdingId: editingHolding.id, data: { shares } },
      {
        onSuccess: () => {
          toast.success("Holding updated");
          setEditingHolding(null);
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  function handleDelete(holding: HoldingRead) {
    deleteHolding.mutate(holding.id, {
      onSuccess: () => toast.success(`${holding.ticker} removed`),
      onError: (err) => toast.error(err.message),
    });
  }

  if (holdings.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No holdings yet. Add a stock below.
      </p>
    );
  }

  function handleRefresh() {
    refreshHoldings.mutate(undefined, {
      onSuccess: () => toast.success("Prices refreshed"),
      onError: (err) => toast.error(err.message),
    });
  }

  return (
    <>
      <div className="flex justify-end gap-2 mb-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => exportHoldingsCSV(holdings, portfolioName ?? "portfolio")}
        >
          <Download className="h-3.5 w-3.5 mr-1.5" />
          Export CSV
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshHoldings.isPending}
        >
          <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${refreshHoldings.isPending ? "animate-spin" : ""}`} />
          {refreshHoldings.isPending ? "Refreshing..." : "Refresh Prices"}
        </Button>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ticker</TableHead>
              <TableHead className="text-right">Shares</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead className="text-right">Value</TableHead>
              <TableHead>Sector</TableHead>
              <TableHead className="text-right">Beta</TableHead>
              <TableHead>Earnings</TableHead>
              <TableHead className="w-20" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {holdings.map((h) => (
              <TableRow key={h.id}>
                <TableCell className="font-medium">
                  <Link
                    href={`/stocks/${h.ticker}`}
                    className="text-primary hover:underline"
                  >
                    {h.ticker}
                  </Link>
                </TableCell>
                <TableCell className="text-right">{h.shares}</TableCell>
                <TableCell className="text-right">
                  {h.last_price ? formatCurrency(h.last_price) : "--"}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(holdingValue(h))}
                </TableCell>
                <TableCell>{h.sector ?? "N/A"}</TableCell>
                <TableCell className="text-right">
                  {formatNumber(h.beta)}
                </TableCell>
                <TableCell>
                  <Badge variant={h.latest_earnings_call ? "default" : "secondary"}>
                    {h.latest_earnings_call ? "Yes" : "No"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => {
                        setEditingHolding(h);
                        setEditShares(String(h.shares));
                      }}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      onClick={() => handleDelete(h)}
                      disabled={deleteHolding.isPending}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog
        open={!!editingHolding}
        onOpenChange={(open) => !open && setEditingHolding(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Edit {editingHolding?.ticker} Shares
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditSubmit}>
            <div className="py-4">
              <Input
                type="number"
                min="0.01"
                step="any"
                value={editShares}
                onChange={(e) => setEditShares(e.target.value)}
                autoFocus
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditingHolding(null)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={updateHolding.isPending}>
                {updateHolding.isPending ? "Saving..." : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
