"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, TrendingUp } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { StockSearchBar } from "@/components/stock/stock-search-bar";
import { useStockSearch } from "@/hooks/use-stocks";

export default function StocksPage() {
  const [query, setQuery] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("");

  return (
    <div>
      <h2 className="text-2xl font-bold tracking-tight">Stocks</h2>
      <p className="mt-2 text-muted-foreground">
        Search for stocks to view charts, fundamentals, and technical analysis.
      </p>

      <div className="mt-6 max-w-lg">
        <StockSearchBar
          placeholder="Search by ticker or company name..."
          onSelect={(ticker) => {
            setSelectedTicker(ticker);
          }}
        />
      </div>

      {selectedTicker ? (
        <div className="mt-6">
          <Link href={`/dashboard/stocks/${selectedTicker}`}>
            <Card className="max-w-md transition-colors hover:bg-accent">
              <CardContent className="flex items-center gap-3 p-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-semibold">{selectedTicker}</p>
                  <p className="text-sm text-muted-foreground">
                    View stock details, charts, and analysis
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      ) : (
        <div className="mt-12">
          <EmptyState
            icon={<Search className="h-12 w-12" />}
            title="Search for a stock"
            description="Enter a ticker symbol or company name above to explore detailed stock information."
          />
        </div>
      )}
    </div>
  );
}
