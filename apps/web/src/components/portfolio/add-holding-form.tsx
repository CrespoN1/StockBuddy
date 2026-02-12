"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StockSearchBar } from "@/components/stock/stock-search-bar";
import { useAddHolding } from "@/hooks/use-holdings";

interface AddHoldingFormProps {
  portfolioId: number;
}

export function AddHoldingForm({ portfolioId }: AddHoldingFormProps) {
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("100");
  const addHolding = useAddHolding(portfolioId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ticker.trim()) return;
    const sharesNum = parseFloat(shares);
    if (isNaN(sharesNum) || sharesNum <= 0) return;

    addHolding.mutate(
      { ticker: ticker.trim().toUpperCase(), shares: sharesNum },
      {
        onSuccess: () => {
          toast.success(`${ticker.toUpperCase()} added`);
          setTicker("");
          setShares("100");
        },
        onError: (err) => toast.error(err.message),
      }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-3">
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
      <Button type="submit" disabled={!ticker || addHolding.isPending}>
        <Plus className="mr-1 h-4 w-4" />
        {addHolding.isPending ? "Adding..." : "Add"}
      </Button>
    </form>
  );
}
