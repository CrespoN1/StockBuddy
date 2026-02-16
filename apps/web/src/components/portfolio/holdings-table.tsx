"use client";

import { useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import { CalendarIcon, Download, Pencil, RefreshCw, Trash2 } from "lucide-react";
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
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { useUpdateHolding, useDeleteHolding, useRefreshHoldings } from "@/hooks/use-holdings";
import { formatCurrency, formatNumber } from "@/lib/format";
import { exportHoldingsCSV } from "@/lib/csv-export";
import type { HoldingRead } from "@/types";
import { holdingValue, holdingGainLoss, holdingGainLossPct } from "@/types";
import { cn } from "@/lib/utils";

interface HoldingsTableProps {
  holdings: HoldingRead[];
  portfolioId: number;
  portfolioName?: string;
}

export function HoldingsTable({ holdings, portfolioId, portfolioName }: HoldingsTableProps) {
  const [editingHolding, setEditingHolding] = useState<HoldingRead | null>(null);
  const [editShares, setEditShares] = useState("");
  const [editPurchaseDate, setEditPurchaseDate] = useState<Date | undefined>(undefined);
  const [editCostBasis, setEditCostBasis] = useState("");
  const [editCalendarOpen, setEditCalendarOpen] = useState(false);
  const updateHolding = useUpdateHolding(portfolioId);
  const deleteHolding = useDeleteHolding(portfolioId);
  const refreshHoldings = useRefreshHoldings(portfolioId);

  function openEditDialog(h: HoldingRead) {
    setEditingHolding(h);
    setEditShares(String(h.shares));
    setEditPurchaseDate(h.purchased_at ? new Date(h.purchased_at + "T00:00:00") : undefined);
    setEditCostBasis(h.cost_basis != null ? String(h.cost_basis) : "");
  }

  function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!editingHolding) return;
    const shares = parseFloat(editShares);
    if (isNaN(shares) || shares <= 0) return;

    const costBasisNum = editCostBasis ? parseFloat(editCostBasis) : undefined;
    if (editCostBasis && (isNaN(costBasisNum!) || costBasisNum! < 0)) return;

    updateHolding.mutate(
      {
        holdingId: editingHolding.id,
        data: {
          shares,
          purchased_at: editPurchaseDate
            ? format(editPurchaseDate, "yyyy-MM-dd")
            : null,
          cost_basis: costBasisNum ?? null,
        },
      },
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
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ticker</TableHead>
              <TableHead className="text-right">Shares</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead className="text-right">Cost</TableHead>
              <TableHead className="text-right">Value</TableHead>
              <TableHead className="text-right">Gain/Loss</TableHead>
              <TableHead>Sector</TableHead>
              <TableHead>Earnings</TableHead>
              <TableHead className="w-20" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {holdings.map((h) => {
              const gl = holdingGainLoss(h);
              const glPct = holdingGainLossPct(h);
              return (
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
                    {h.cost_basis != null ? formatCurrency(h.cost_basis) : "--"}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(holdingValue(h))}
                  </TableCell>
                  <TableCell className="text-right">
                    {gl != null ? (
                      <span className={gl >= 0 ? "text-green-600" : "text-red-600"}>
                        {gl >= 0 ? "+" : ""}{formatCurrency(gl)}
                        {glPct != null && (
                          <span className="ml-1 text-xs">
                            ({glPct >= 0 ? "+" : ""}{glPct.toFixed(1)}%)
                          </span>
                        )}
                      </span>
                    ) : (
                      "--"
                    )}
                  </TableCell>
                  <TableCell>{h.sector ?? "N/A"}</TableCell>
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
                        onClick={() => openEditDialog(h)}
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
              );
            })}
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
              Edit {editingHolding?.ticker}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Shares</label>
              <Input
                type="number"
                min="0.01"
                step="any"
                value={editShares}
                onChange={(e) => setEditShares(e.target.value)}
                autoFocus
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">
                Purchase Date <span className="text-muted-foreground font-normal">(optional)</span>
              </label>
              <Popover open={editCalendarOpen} onOpenChange={setEditCalendarOpen}>
                <PopoverTrigger asChild>
                  <Button
                    type="button"
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !editPurchaseDate && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {editPurchaseDate
                      ? format(editPurchaseDate, "MMM d, yyyy")
                      : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={editPurchaseDate}
                    onSelect={(day) => {
                      setEditPurchaseDate(day);
                      setEditCalendarOpen(false);
                    }}
                    disabled={{ after: new Date() }}
                    defaultMonth={editPurchaseDate ?? new Date()}
                  />
                </PopoverContent>
              </Popover>
              {editPurchaseDate && (
                <Button
                  type="button"
                  variant="link"
                  size="sm"
                  className="mt-1 h-auto p-0 text-xs text-muted-foreground"
                  onClick={() => setEditPurchaseDate(undefined)}
                >
                  Clear date
                </Button>
              )}
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">
                Cost Basis <span className="text-muted-foreground font-normal">($/share, optional)</span>
              </label>
              <Input
                type="number"
                min="0"
                step="any"
                placeholder="$/share"
                value={editCostBasis}
                onChange={(e) => setEditCostBasis(e.target.value)}
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
