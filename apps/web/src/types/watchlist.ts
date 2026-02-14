export interface WatchlistItem {
  id: number;
  ticker: string;
  name: string | null;
  last_price: number | null;
  previous_close: number | null;
  sector: string | null;
  added_at: string;
}

export interface WatchlistItemCreate {
  ticker: string;
}
