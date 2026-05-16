"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";

const periods = [
  { value: "this-week", label: "This Week" },
  { value: "this-month", label: "This Month" },
  { value: "this-quarter", label: "This Quarter" },
  { value: "this-year", label: "This Year" },
  { value: "all-time", label: "All Time" },
];

interface TimePeriodSelectProps {
  currentPeriod: string;
  className?: string;
}

export function TimePeriodSelect({
  currentPeriod,
  className,
}: TimePeriodSelectProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("period", e.target.value);
    router.push(`?${params.toString()}`);
  }

  return (
    <select
      value={currentPeriod}
      onChange={handleChange}
      className={cn(
        "rounded-md border border-border bg-card px-3 py-2 text-sm font-medium",
        "text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
        "appearance-none cursor-pointer pr-8",
        "bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%239ca3af%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m6%209%206%206%206-6%22%2F%3E%3C%2Fsvg%3E')] bg-[length:16px] bg-[right_8px_center] bg-no-repeat",
        className
      )}
    >
      {periods.map((p) => (
        <option key={p.value} value={p.value}>
          {p.label}
        </option>
      ))}
    </select>
  );
}
