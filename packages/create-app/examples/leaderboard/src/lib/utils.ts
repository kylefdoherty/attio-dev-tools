import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(1)}M`;
  }
  if (amount >= 1_000) {
    return `$${(amount / 1_000).toFixed(0)}K`;
  }
  return `$${amount.toLocaleString()}`;
}

export function formatCurrencyFull(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getTimePeriodDates(period: string): { start: Date; end: Date } {
  const now = new Date();
  const end = now;

  switch (period) {
    case "this-week": {
      const start = new Date(now);
      start.setDate(now.getDate() - now.getDay());
      start.setHours(0, 0, 0, 0);
      return { start, end };
    }
    case "this-month": {
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      return { start, end };
    }
    case "this-quarter": {
      const quarter = Math.floor(now.getMonth() / 3);
      const start = new Date(now.getFullYear(), quarter * 3, 1);
      return { start, end };
    }
    case "this-year": {
      const start = new Date(now.getFullYear(), 0, 1);
      return { start, end };
    }
    case "all-time":
    default: {
      const start = new Date(2000, 0, 1);
      return { start, end };
    }
  }
}
