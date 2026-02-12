export interface EarningsCallRead {
  id: number;
  ticker: string;
  holding_id: number | null;
  call_date: string | null;
  summary: string | null;
  key_metrics: Record<string, unknown> | null;
  sentiment_score: number | null;
  risk_mentions: number | null;
  growth_mentions: number | null;
  guidance_outlook: string | null;
  created_at: string;
}
