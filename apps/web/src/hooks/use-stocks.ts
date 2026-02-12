"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type {
  StockSearchResult,
  StockInfo,
  StockQuote,
  StockFundamentals,
  OHLCVBar,
  TechnicalIndicators,
  NewsArticle,
  StockForecast,
} from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useStockSearch(q: string, limit = 20) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", "search", q, limit],
    queryFn: () =>
      fetchApi<StockSearchResult[]>(
        `/api/v1/stocks/search?q=${encodeURIComponent(q)}&limit=${limit}`
      ),
    enabled: q.length > 0,
  });
}

export function useStockInfo(ticker: string) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "info"],
    queryFn: () => fetchApi<StockInfo>(`/api/v1/stocks/${ticker}`),
    enabled: ticker.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockQuote(ticker: string) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "quote"],
    queryFn: () => fetchApi<StockQuote>(`/api/v1/stocks/${ticker}/quote`),
    enabled: ticker.length > 0,
    staleTime: 30 * 1000,
  });
}

export function useStockFundamentals(ticker: string) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "fundamentals"],
    queryFn: () => fetchApi<StockFundamentals>(`/api/v1/stocks/${ticker}/fundamentals`),
    enabled: ticker.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockHistory(ticker: string, period = "1y") {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "history", period],
    queryFn: () =>
      fetchApi<OHLCVBar[]>(`/api/v1/stocks/${ticker}/history?period=${period}`),
    enabled: ticker.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockTechnicals(ticker: string) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "technicals"],
    queryFn: () =>
      fetchApi<TechnicalIndicators>(`/api/v1/stocks/${ticker}/technicals`),
    enabled: ticker.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockNews(ticker: string, limit = 10) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "news", limit],
    queryFn: () =>
      fetchApi<NewsArticle[]>(
        `/api/v1/stocks/${ticker}/news?limit=${limit}`
      ),
    enabled: ticker.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockForecast(ticker: string, days = 30) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["stocks", ticker, "forecast", days],
    queryFn: () =>
      fetchApi<StockForecast>(
        `/api/v1/stocks/${ticker}/forecast?days=${days}`
      ),
    enabled: ticker.length > 0,
    staleTime: 10 * 60 * 1000,
  });
}
