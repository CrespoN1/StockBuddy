"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StockSearchBar } from "@/components/stock/stock-search-bar";

interface TickerMultiSelectProps {
  onCompare: (tickers: string[]) => void;
  isComparing?: boolean;
}

export function TickerMultiSelect({ onCompare, isComparing }: TickerMultiSelectProps) {
  const [tickers, setTickers] = useState<string[]>([]);

  function addTicker(ticker: string) {
    if (tickers.length >= 3) return;
    if (tickers.includes(ticker.toUpperCase())) return;
    setTickers([...tickers, ticker.toUpperCase()]);
  }

  function removeTicker(ticker: string) {
    setTickers(tickers.filter((t) => t !== ticker));
  }

  return (
    <div className="space-y-4">
      {tickers.length < 3 && (
        <div>
          <label className="mb-1 block text-sm font-medium">
            Add ticker ({tickers.length}/3)
          </label>
          <StockSearchBar
            placeholder="Search to add ticker..."
            onSelect={(t) => addTicker(t)}
          />
        </div>
      )}

      {tickers.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tickers.map((t) => (
            <Badge key={t} variant="secondary" className="gap-1 pr-1 text-sm">
              {t}
              <button
                onClick={() => removeTicker(t)}
                className="ml-1 rounded-full p-0.5 hover:bg-muted"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      <Button
        onClick={() => onCompare(tickers)}
        disabled={tickers.length < 2 || isComparing}
      >
        {isComparing ? "Comparing..." : `Compare ${tickers.length} Stocks`}
      </Button>
    </div>
  );
}
