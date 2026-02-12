export interface HoldingRead {
  id: number;
  portfolio_id: number;
  ticker: string;
  shares: number;
  last_price: number | null;
  sector: string | null;
  beta: number | null;
  dividend_yield: number | null;
  latest_earnings_call: string | null;
  earnings_call_summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface HoldingCreate {
  ticker: string;
  shares: number;
}

export interface HoldingUpdate {
  shares: number;
}

export function holdingValue(h: HoldingRead): number {
  return (h.last_price ?? 0) * h.shares;
}
