"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { cn, formatCurrency, formatPercent, getInitials } from "@/lib/utils";
import type { RepStats } from "@/lib/leaderboard";

interface LeaderboardTableProps {
  reps: RepStats[];
  sortBy: string;
  period: string;
}

function RankBadge({ rank }: { rank: number }) {
  if (rank === 1) {
    return (
      <div className="rank-badge-1 flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold text-gray-900">
        1
      </div>
    );
  }
  if (rank === 2) {
    return (
      <div className="rank-badge-2 flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold text-gray-900">
        2
      </div>
    );
  }
  if (rank === 3) {
    return (
      <div className="rank-badge-3 flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold text-gray-900">
        3
      </div>
    );
  }
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-sm font-medium text-muted-foreground">
      {rank}
    </div>
  );
}

function Avatar({ name, rank }: { name: string; rank: number }) {
  const initials = getInitials(name);
  const colors = [
    "bg-blue-500/20 text-blue-400",
    "bg-purple-500/20 text-purple-400",
    "bg-pink-500/20 text-pink-400",
    "bg-emerald-500/20 text-emerald-400",
    "bg-orange-500/20 text-orange-400",
    "bg-cyan-500/20 text-cyan-400",
    "bg-rose-500/20 text-rose-400",
    "bg-indigo-500/20 text-indigo-400",
  ];
  const colorIndex = name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0) % colors.length;

  return (
    <div
      className={cn(
        "flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold",
        colors[colorIndex],
        rank === 1 && "ring-2 ring-yellow-500/50"
      )}
    >
      {initials}
    </div>
  );
}

const sortOptions = [
  { value: "revenue", label: "Revenue" },
  { value: "deals", label: "Deals" },
  { value: "avg-deal", label: "Avg Deal" },
  { value: "win-rate", label: "Win Rate" },
];

export function LeaderboardTable({
  reps,
  sortBy,
  period,
}: LeaderboardTableProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function handleSort(sort: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("sort", sort);
    router.push(`?${params.toString()}`);
  }

  if (reps.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="mx-auto text-muted-foreground/50"
        >
          <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 7 7 7 7" />
          <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 17 7 17 7" />
          <path d="M4 22h16" />
          <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
          <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
          <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
        </svg>
        <h3 className="mt-4 text-lg font-semibold">No deals found</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          No closed deals found for this time period. Try selecting a different
          range.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Sort Controls */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Sort by:
        </span>
        <div className="flex gap-1">
          {sortOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleSort(opt.value)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                sortBy === opt.value
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="w-16 py-3 px-4 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Rank
              </th>
              <th className="py-3 px-4 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Rep
              </th>
              <th className="py-3 px-4 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Deals Won
              </th>
              <th className="py-3 px-4 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Revenue
              </th>
              <th className="py-3 px-4 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground hidden sm:table-cell">
                Avg Deal
              </th>
              <th className="py-3 px-4 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground hidden md:table-cell">
                Win Rate
              </th>
            </tr>
          </thead>
          <tbody>
            {reps.map((rep, index) => {
              const rank = index + 1;
              return (
                <tr
                  key={rep.id}
                  className={cn(
                    "border-b border-border last:border-0 transition-colors hover:bg-muted/20 animate-rank-shift",
                    rank === 1 && "bg-yellow-500/[0.03]"
                  )}
                >
                  <td className="py-3 px-4">
                    <RankBadge rank={rank} />
                  </td>
                  <td className="py-3 px-4">
                    <Link
                      href={`/rep/${rep.id}?period=${period}`}
                      className="flex items-center gap-3 group"
                    >
                      <Avatar name={rep.name} rank={rank} />
                      <div>
                        <p className="font-medium group-hover:text-primary transition-colors">
                          {rep.name}
                        </p>
                        {rep.email && (
                          <p className="text-xs text-muted-foreground">
                            {rep.email}
                          </p>
                        )}
                      </div>
                    </Link>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className="text-sm font-semibold tabular-nums">
                      {rep.dealsWon}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span
                      className={cn(
                        "text-sm font-bold tabular-nums",
                        rank === 1 && "text-green-400 revenue-glow"
                      )}
                    >
                      {formatCurrency(rep.totalRevenue)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right hidden sm:table-cell">
                    <span className="text-sm tabular-nums text-muted-foreground">
                      {formatCurrency(rep.avgDealSize)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right hidden md:table-cell">
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                        rep.winRate >= 0.7
                          ? "bg-green-500/10 text-green-400"
                          : rep.winRate >= 0.4
                          ? "bg-yellow-500/10 text-yellow-400"
                          : "bg-red-500/10 text-red-400"
                      )}
                    >
                      {formatPercent(rep.winRate)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
