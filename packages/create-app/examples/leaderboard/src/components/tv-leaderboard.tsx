"use client";

import { useEffect, useState } from "react";
import { cn, formatCurrency, formatPercent, getInitials } from "@/lib/utils";
import type { RepStats, LeaderboardData } from "@/lib/leaderboard";

interface TvLeaderboardProps {
  reps: RepStats[];
  data: LeaderboardData;
  period: string;
}

export function TvLeaderboard({ reps: initialReps, data: initialData, period }: TvLeaderboardProps) {
  const [reps, setReps] = useState(initialReps);
  const [data, setData] = useState(initialData);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Auto-refresh every 60 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/leaderboard?period=${period}`);
        if (res.ok) {
          const newData: LeaderboardData = await res.json();
          const sorted = [...newData.reps].sort(
            (a, b) => b.totalRevenue - a.totalRevenue
          );
          setReps(sorted);
          setData(newData);
          setLastRefresh(new Date());
        }
      } catch {
        // Silently retry on next interval
      }
    }, 60_000);

    return () => clearInterval(interval);
  }, [period]);

  // Fullscreen toggle
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }

  // Listen for fullscreen changes
  useEffect(() => {
    function handleChange() {
      setIsFullscreen(!!document.fullscreenElement);
    }
    document.addEventListener("fullscreenchange", handleChange);
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, []);

  const periodLabel = period
    .replace("this-", "This ")
    .replace("all-time", "All Time")
    .replace(/^\w/, (c) => c.toUpperCase());

  return (
    <div className="min-h-screen bg-background p-8 tv-mode flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">
            Sales Leaderboard
          </h1>
          <p className="text-lg text-muted-foreground mt-1">
            {periodLabel} &middot; {formatCurrency(data.totalRevenue)} total revenue
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right text-sm text-muted-foreground">
            <p>Auto-refreshing every 60s</p>
            <p className="text-xs">
              Last update: {lastRefresh.toLocaleTimeString()}
            </p>
          </div>
          <button
            onClick={toggleFullscreen}
            className="rounded-md border border-border p-2 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? (
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M8 3v3a2 2 0 0 1-2 2H3" />
                <path d="M21 8h-3a2 2 0 0 1-2-2V3" />
                <path d="M3 16h3a2 2 0 0 1 2 2v3" />
                <path d="M16 21v-3a2 2 0 0 1 2-2h3" />
              </svg>
            ) : (
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 7V5a2 2 0 0 1 2-2h2" />
                <path d="M17 3h2a2 2 0 0 1 2 2v2" />
                <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
                <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
              </svg>
            )}
          </button>
          <a
            href={`/?period=${period}`}
            className="rounded-md border border-border px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          >
            Exit TV Mode
          </a>
        </div>
      </div>

      {/* Leaderboard Grid */}
      <div className="flex-1 grid gap-4">
        {reps.length === 0 ? (
          <div className="flex items-center justify-center">
            <p className="text-2xl text-muted-foreground">
              No deals closed yet for {periodLabel.toLowerCase()}.
            </p>
          </div>
        ) : (
          <>
            {/* Top 3 - Large Cards */}
            {reps.length >= 1 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2">
                {reps.slice(0, 3).map((rep, i) => (
                  <TvRepCard key={rep.id} rep={rep} rank={i + 1} />
                ))}
              </div>
            )}

            {/* Remaining reps - Compact rows */}
            {reps.length > 3 && (
              <div className="rounded-xl border border-border bg-card/50 overflow-hidden">
                {reps.slice(3).map((rep, i) => (
                  <TvRepRow key={rep.id} rep={rep} rank={i + 4} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function TvRepCard({ rep, rank }: { rep: RepStats; rank: number }) {
  const initials = getInitials(rep.name);

  const rankStyles = {
    1: {
      border: "border-yellow-500/30",
      bg: "bg-yellow-500/[0.05]",
      badge: "rank-badge-1 text-gray-900",
      glow: "shadow-lg shadow-yellow-500/10",
    },
    2: {
      border: "border-gray-400/20",
      bg: "bg-gray-400/[0.03]",
      badge: "rank-badge-2 text-gray-900",
      glow: "",
    },
    3: {
      border: "border-amber-700/20",
      bg: "bg-amber-700/[0.03]",
      badge: "rank-badge-3 text-gray-900",
      glow: "",
    },
  };

  const style = rankStyles[rank as 1 | 2 | 3];

  return (
    <div
      className={cn(
        "rounded-xl border p-6 flex flex-col items-center text-center transition-all",
        style.border,
        style.bg,
        style.glow,
        rank === 1 && "md:scale-105 md:-mt-2"
      )}
    >
      {/* Rank Badge */}
      <div
        className={cn(
          "flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold mb-4",
          style.badge
        )}
      >
        {rank}
      </div>

      {/* Avatar */}
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-xl font-bold mb-3">
        {initials}
      </div>

      {/* Name */}
      <h3 className="text-xl font-bold">{rep.name}</h3>

      {/* Revenue - BIG */}
      <p
        className={cn(
          "text-3xl font-bold mt-3 tabular-nums",
          rank === 1 ? "text-green-400 revenue-glow" : "text-foreground"
        )}
      >
        {formatCurrency(rep.totalRevenue)}
      </p>

      {/* Sub-metrics */}
      <div className="flex gap-4 mt-3 text-sm text-muted-foreground">
        <span>{rep.dealsWon} deals</span>
        <span>{formatPercent(rep.winRate)} win</span>
      </div>
    </div>
  );
}

function TvRepRow({ rep, rank }: { rep: RepStats; rank: number }) {
  const initials = getInitials(rep.name);

  return (
    <div className="flex items-center gap-4 px-6 py-4 border-b border-border last:border-0 hover:bg-muted/10 transition-colors">
      {/* Rank */}
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-sm font-medium text-muted-foreground shrink-0">
        {rank}
      </div>

      {/* Avatar */}
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted/50 text-sm font-semibold shrink-0">
        {initials}
      </div>

      {/* Name */}
      <div className="flex-1 min-w-0">
        <p className="text-lg font-semibold truncate">{rep.name}</p>
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-8 text-right">
        <div>
          <p className="text-xs text-muted-foreground">Deals</p>
          <p className="text-lg font-bold tabular-nums">{rep.dealsWon}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Win Rate</p>
          <p className="text-lg font-bold tabular-nums">
            {formatPercent(rep.winRate)}
          </p>
        </div>
        <div className="min-w-[100px]">
          <p className="text-xs text-muted-foreground">Revenue</p>
          <p className="text-lg font-bold tabular-nums text-green-400">
            {formatCurrency(rep.totalRevenue)}
          </p>
        </div>
      </div>
    </div>
  );
}
