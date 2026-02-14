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
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}
