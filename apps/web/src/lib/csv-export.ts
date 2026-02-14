import type { HoldingRead } from "@/types";
import { holdingValue } from "@/types";

function escapeCSV(value: string | number | null | undefined): string {
  if (value == null) return "";
  const str = String(value);
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function generateCSV(headers: string[], rows: (string | number | null | undefined)[][]): string {
  const headerLine = headers.map(escapeCSV).join(",");
  const dataLines = rows.map((row) => row.map(escapeCSV).join(","));
  return "\uFEFF" + [headerLine, ...dataLines].join("\n");
}

function downloadCSV(csv: string, filename: string): void {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function exportHoldingsCSV(holdings: HoldingRead[], portfolioName: string): void {
  const headers = ["Ticker", "Shares", "Price", "Value", "Sector", "Beta", "Dividend Yield"];
  const rows = holdings.map((h) => [
    h.ticker,
    h.shares,
    h.last_price,
    holdingValue(h),
    h.sector,
    h.beta,
    h.dividend_yield,
  ]);
  const date = new Date().toISOString().slice(0, 10);
  const safeName = portfolioName.replace(/[^a-zA-Z0-9-_]/g, "_");
  downloadCSV(generateCSV(headers, rows), `${safeName}-holdings-${date}.csv`);
}

export function exportComparisonCSV(text: string, tickers: string[]): void {
  const headers = ["Comparison Analysis"];
  const rows = text.split("\n").map((line) => [line]);
  const date = new Date().toISOString().slice(0, 10);
  const tickerStr = tickers.join("-");
  downloadCSV(generateCSV(headers, rows), `comparison-${tickerStr}-${date}.csv`);
}
