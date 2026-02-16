"use client";

import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { StockSearchBar } from "@/components/stock/stock-search-bar";
import { useAddHolding } from "@/hooks/use-holdings";
import { cn } from "@/lib/utils";

interface AddHoldingFormProps {
  portfolioId: number;
}

export function AddHoldingForm({ portfolioId }: AddHoldingFormProps) {
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("100");
  const [purchaseDate, setPurchaseDate] = useState<Date | undefined>(undefined);
  const [costBasis, setCostBasis] = useState("");
  const [calendarOpen, setCalendarOpen] = useState(false);
  const addHolding = useAddHolding(portfolioId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ticker.trim()) return;
    const sharesNum = parseFloat(shares);
    if (isNaN(sharesNum) || sharesNum <= 0) return;

    const costBasisNum = costBasis ? parseFloat(costBasis) : undefined;
    if (costBasis && (isNaN(costBasisNum!) || costBasisNum! < 0)) return;

    addHolding.mutate(
      {
        ticker: ticker.trim().toUpperCase(),
        shares: sharesNum,
        purchased_at: purchaseDate
          ? format(purchaseDate, "yyyy-MM-dd")
          : undefined,
        cost_basis: costBasisNum,
      },
      {
        onSuccess: () => {
          toast.success(`${ticker.toUpperCase()} added`);
          setTicker("");
          setShares("100");
          setPurchaseDate(undefined);
          setCostBasis("");
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {/* Row 1: Ticker + Shares */}
      <div className="flex items-end gap-3">
        <div className="flex-1">
          <label className="mb-1 block text-sm font-medium">Ticker</label>
          <StockSearchBar
            placeholder="Search ticker..."
            onSelect={(selectedTicker) => setTicker(selectedTicker)}
          />
          {ticker && (
            <p className="mt-1 text-sm text-muted-foreground">
              Selected: <span className="font-medium">{ticker}</span>
            </p>
          )}
        </div>
        <div className="w-32">
          <label className="mb-1 block text-sm font-medium">Shares</label>
          <Input
            type="number"
            min="0.01"
            step="any"
            value={shares}
            onChange={(e) => setShares(e.target.value)}
          />
        </div>
      </div>

      {/* Row 2: Purchase Date + Cost Basis + Add Button */}
      <div className="flex items-end gap-3">
        <div className="w-48">
          <label className="mb-1 block text-sm font-medium">
            Purchase Date <span className="text-muted-foreground font-normal">(optional)</span>
          </label>
          <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
            <PopoverTrigger asChild>
              <Button
                type="button"
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !purchaseDate && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {purchaseDate ? format(purchaseDate, "MMM d, yyyy") : "Pick a date"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={purchaseDate}
                onSelect={(day) => {
                  setPurchaseDate(day);
                  setCalendarOpen(false);
                }}
                disabled={{ after: new Date() }}
                defaultMonth={purchaseDate ?? new Date()}
              />
            </PopoverContent>
          </Popover>
        </div>
        <div className="w-36">
          <label className="mb-1 block text-sm font-medium">
            Cost Basis <span className="text-muted-foreground font-normal">(optional)</span>
          </label>
          <Input
            type="number"
            min="0"
            step="any"
            placeholder="$/share"
            value={costBasis}
            onChange={(e) => setCostBasis(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={!ticker || addHolding.isPending}>
          <Plus className="mr-1 h-4 w-4" />
          {addHolding.isPending ? "Adding..." : "Add"}
        </Button>
      </div>
    </form>
  );
}
