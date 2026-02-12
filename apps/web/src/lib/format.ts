import { format } from "date-fns";

export function formatCurrency(value: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(value);
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatLargeNumber(value: number | string): string {
  if (typeof value === "string") return value;
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  return formatCurrency(value);
}

export function formatDate(isoString: string): string {
  return format(new Date(isoString), "MMM d, yyyy");
}

export function formatNumber(value: number | string | null, fallback = "--"): string {
  if (value === null || value === undefined || value === "N/A") return fallback;
  if (typeof value === "string") return value;
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
}
