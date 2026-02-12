import type { HoldingRead } from "./holding";

export interface PortfolioRead {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface PortfolioDetail extends PortfolioRead {
  holdings: HoldingRead[];
}

export interface PortfolioCreate {
  name: string;
}

export interface PortfolioUpdate {
  name?: string;
}
