export interface PriceAlert {
  id: number;
  user_id: string;
  ticker: string;
  target_price: number;
  direction: "above" | "below";
  triggered: boolean;
  triggered_at: string | null;
  triggered_price: number | null;
  created_at: string;
}

export interface PriceAlertCreate {
  ticker: string;
  target_price: number;
  direction: "above" | "below";
}

export interface AlertsSummary {
  active_count: number;
  triggered_count: number;
}
