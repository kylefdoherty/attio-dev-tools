import { getAttioClient } from "@/lib/attio";
import { getLeaderboardData } from "@/lib/leaderboard";
import { RepCard } from "@/components/rep-card";
import { MetricCard } from "@/components/metric-card";
import { formatCurrency, formatCurrencyFull, formatPercent } from "@/lib/utils";
import Link from "next/link";

interface PageProps {
  params: { id: string };
  searchParams: { period?: string };
}

export default async function RepDetailPage({ params, searchParams }: PageProps) {
  const period = searchParams.period || "all-time";

  const client = await getAttioClient();
  if (!client) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Failed to connect to Attio.</p>
      </div>
    );
  }

  const data = await getLeaderboardData(client, period);
  const rep = data.reps.find((r) => r.id === params.id);

  if (!rep) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <p className="text-muted-foreground">Rep not found.</p>
        <Link
          href="/"
          className="text-sm text-primary underline hover:no-underline"
        >
          Back to Leaderboard
        </Link>
      </div>
    );
  }

  // Calculate rank
  const sortedByRevenue = [...data.reps].sort(
    (a, b) => b.totalRevenue - a.totalRevenue
  );
  const rank = sortedByRevenue.findIndex((r) => r.id === rep.id) + 1;

  // Separate won and lost deals
  const wonDeals = rep.deals.filter((d) => d.status === "won");
  const lostDeals = rep.deals.filter((d) => d.status === "lost");

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Back link */}
      <Link
        href={`/?period=${period}`}
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m15 18-6-6 6-6" />
        </svg>
        Back to Leaderboard
      </Link>

      {/* Rep Header */}
      <RepCard rep={rep} rank={rank} />

      {/* Metrics */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Revenue"
          value={formatCurrencyFull(rep.totalRevenue)}
          subtitle={`Rank #${rank} on team`}
          trend="up"
        />
        <MetricCard
          title="Deals Won"
          value={rep.dealsWon.toString()}
          subtitle={`${rep.dealsLost} lost`}
        />
        <MetricCard
          title="Avg Deal Size"
          value={formatCurrency(rep.avgDealSize)}
          subtitle="Per closed-won deal"
        />
        <MetricCard
          title="Win Rate"
          value={formatPercent(rep.winRate)}
          subtitle={`${rep.dealsWon + rep.dealsLost} total closed`}
          trend={rep.winRate >= 0.5 ? "up" : "down"}
        />
      </div>

      {/* Deals Table */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Closed Deals</h2>

        {wonDeals.length === 0 && lostDeals.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No deals found for this period.
          </p>
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                    Deal
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                    Status
                  </th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                    Value
                  </th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                    Close Date
                  </th>
                </tr>
              </thead>
              <tbody>
                {rep.deals.map((deal) => (
                  <tr
                    key={deal.id}
                    className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium">{deal.name}</p>
                        {deal.company && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {deal.company}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          deal.status === "won"
                            ? "bg-green-500/10 text-green-400"
                            : "bg-red-500/10 text-red-400"
                        }`}
                      >
                        {deal.status === "won" ? "Won" : "Lost"}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-medium tabular-nums">
                      {formatCurrencyFull(deal.value)}
                    </td>
                    <td className="py-3 px-4 text-right text-muted-foreground tabular-nums">
                      {new Date(deal.closeDate).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
