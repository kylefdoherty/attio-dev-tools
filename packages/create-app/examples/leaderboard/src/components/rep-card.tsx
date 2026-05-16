import { cn, getInitials, formatCurrency, formatPercent } from "@/lib/utils";
import type { RepStats } from "@/lib/leaderboard";

interface RepCardProps {
  rep: RepStats;
  rank: number;
  className?: string;
}

export function RepCard({ rep, rank, className }: RepCardProps) {
  const initials = getInitials(rep.name);
  const colors = [
    "from-blue-500 to-blue-600",
    "from-purple-500 to-purple-600",
    "from-pink-500 to-pink-600",
    "from-emerald-500 to-emerald-600",
    "from-orange-500 to-orange-600",
    "from-cyan-500 to-cyan-600",
    "from-rose-500 to-rose-600",
    "from-indigo-500 to-indigo-600",
  ];
  const colorIndex =
    rep.name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0) %
    colors.length;

  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-6",
        className
      )}
    >
      <div className="flex items-center gap-4">
        {/* Avatar */}
        <div
          className={cn(
            "flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br text-xl font-bold text-white",
            colors[colorIndex],
            rank === 1 && "ring-3 ring-yellow-500/50 animate-pulse-gold"
          )}
        >
          {initials}
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold">{rep.name}</h2>
            {rank <= 3 && (
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold",
                  rank === 1 && "rank-badge-1 text-gray-900",
                  rank === 2 && "rank-badge-2 text-gray-900",
                  rank === 3 && "rank-badge-3 text-gray-900"
                )}
              >
                #{rank}
              </span>
            )}
          </div>
          {rep.email && (
            <p className="text-sm text-muted-foreground mt-0.5">{rep.email}</p>
          )}
        </div>

        {/* Key Stat */}
        <div className="text-right">
          <p className="text-3xl font-bold text-green-400">
            {formatCurrency(rep.totalRevenue)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {rep.dealsWon} deals | {formatPercent(rep.winRate)} win rate
          </p>
        </div>
      </div>
    </div>
  );
}
