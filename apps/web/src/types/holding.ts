export interface HoldingRead {
  id: number;
  portfolio_id: number;
  ticker: string;
  shares: number;
  purchased_at: string | null;
  cost_basis: number | null;
  last_price: number | null;
  previous_close: number | null;
  sector: string | null;
  beta: number | null;
  dividend_yield: number | null;
  next_earnings_date: string | null;
  latest_earnings_call: string | null;
  earnings_call_summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface HoldingCreate {
  ticker: string;
  shares: number;
  purchased_at?: string | null;
  cost_basis?: number | null;
}

export interface HoldingUpdate {
  shares: number;
  purchased_at?: string | null;
  cost_basis?: number | null;
}

export function holdingValue(h: HoldingRead): number {
  return (h.last_price ?? 0) * h.shares;
}

export function holdingGainLoss(h: HoldingRead): number | null {
  if (h.cost_basis == null || h.last_price == null) return null;
  return (h.last_price - h.cost_basis) * h.shares;
}

export function holdingGainLossPct(h: HoldingRead): number | null {
  if (h.cost_basis == null || h.cost_basis === 0 || h.last_price == null) return null;
  return ((h.last_price - h.cost_basis) / h.cost_basis) * 100;
}
