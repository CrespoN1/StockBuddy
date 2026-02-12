"use client";

import { useState, useEffect, useRef } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useStockSearch } from "@/hooks/use-stocks";

interface StockSearchBarProps {
  onSelect: (ticker: string, name: string) => void;
  placeholder?: string;
}

export function StockSearchBar({
  onSelect,
  placeholder = "Search stocks...",
}: StockSearchBarProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const { data: results, isPending } = useStockSearch(debouncedQuery);

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (query.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          className="pl-9"
        />
      </div>
      {isOpen && debouncedQuery.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
          {isPending ? (
            <div className="p-3 text-sm text-muted-foreground">Searching...</div>
          ) : results && results.length > 0 ? (
            <ul className="max-h-60 overflow-y-auto py-1">
              {results.map((result) => (
                <li key={result.ticker}>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
                    onClick={() => {
                      onSelect(result.ticker, result.name);
                      setQuery("");
                      setIsOpen(false);
                    }}
                  >
                    <span className="font-medium">{result.ticker}</span>
                    <span className="truncate text-muted-foreground">
                      {result.name}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-3 text-sm text-muted-foreground">No results found</div>
          )}
        </div>
      )}
    </div>
  );
}
