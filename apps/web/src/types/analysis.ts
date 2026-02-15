export interface PortfolioSnapshotRead {
  id: number;
  portfolio_id: number;
  created_at: string;
  total_value: number | null;
  num_positions: number;
  recent_earnings_coverage: number | null;
  avg_sentiment_score: number | null;
  risk_exposure_score: number | null;
  health_score: number | null;
  concentration_risk: number | null;
  daily_change: number | null;
  daily_change_pct: number | null;
}

export interface BenchmarkPoint {
  date: string;
  portfolio_pct: number;
  sp500_pct: number;
}

export interface PortfolioHistoryWithBenchmark {
  data: BenchmarkPoint[];
}

export interface SectorAllocation {
  sector: string;
  weight: number;
  value: number;
}

export interface EarningsInsights {
  holdings_with_recent_earnings: string[];
  positive_outlooks: string[];
  risk_warnings: string[];
  recommended_reviews: string[];
  sentiment_summary: Record<string, number>;
}

export interface JobStatus {
  id: string;
  job_type: string;
  status: string;
  input_data: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface PerformerInfo {
  ticker: string;
  daily_change_pct: number;
}

export interface DashboardSummary {
  best_performer: PerformerInfo | null;
  worst_performer: PerformerInfo | null;
  upcoming_earnings_count: number;
  upcoming_earnings_tickers: string[];
}
