export interface StockSearchResult {
  ticker: string;
  name: string;
}

export interface StockQuote {
  ticker: string;
  price: number | null;
  currency: string;
}

export interface StockInfo {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: string;
  pe_ratio: number | string;
  forward_pe: number | string;
  dividend_yield: number | string;
  beta: number | string;
  week_52_high: number | string;
  week_52_low: number | string;
  avg_volume: number | string;
  volume: number | string;
  employees: number | string;
  website: string;
  summary: string;
  top_institutional: Record<string, unknown>[] | null;
  latest_recommendation: {
    firm: string;
    rating: string;
    action: string;
  } | null;
}

export interface StockFundamentals {
  ticker: string;
  price: number | null;
  sector: string | null;
  market_cap: string | null;
  pe_ratio: string | null;
  beta: number | null;
  dividend_yield: number | null;
  next_earnings_date: string | null;
}

export interface OHLCVBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TechnicalIndicators {
  ticker: string;
  current_price: number;
  ma_20: number | null;
  ma_50: number | null;
  ma_200: number | null;
  rsi_14: number | null;
  rsi_signal: string;
  current_volume: number;
  avg_volume: number;
  volume_ratio: number;
  support: number | null;
  resistance: number | null;
}
