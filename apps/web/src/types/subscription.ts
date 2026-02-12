export interface SubscriptionRead {
  plan: "free" | "pro";
  status: string;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  earnings_analysis_count: number;
  portfolio_analysis_count: number;
  earnings_analysis_limit: number | null;
  portfolio_analysis_limit: number | null;
  portfolio_limit: number | null;
  holdings_per_portfolio_limit: number | null;
}

export interface UsageInfo {
  plan: "free" | "pro";
  earnings_analysis_used: number;
  earnings_analysis_limit: number | null;
  portfolio_analysis_used: number;
  portfolio_analysis_limit: number | null;
  portfolio_count: number;
  portfolio_limit: number | null;
  can_create_portfolio: boolean;
  can_analyze_earnings: boolean;
  can_analyze_portfolio: boolean;
  can_compare: boolean;
  can_forecast: boolean;
  can_export_csv: boolean;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
}

export interface BillingPortalResponse {
  portal_url: string;
}
