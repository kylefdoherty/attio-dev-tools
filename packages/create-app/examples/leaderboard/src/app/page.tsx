import { getSession } from "@/lib/session";
import { getAttioClient } from "@/lib/attio";
import { getLeaderboardData } from "@/lib/leaderboard";
import { ConnectButton } from "@/components/connect-button";
import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { MetricCard } from "@/components/metric-card";
import { TimePeriodSelect } from "@/components/time-period-select";
import { formatCurrency, formatCurrencyFull } from "@/lib/utils";
import Link from "next/link";

interface PageProps {
  searchParams: { period?: string; sort?: string };
}

export const revalidate = 30;

export default async function Home({ searchParams }: PageProps) {
  const session = await getSession();
  const connected = !!session.accessToken;

  if (!connected) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3 mb-6">
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-yellow-500"
            >
              <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 7 7 7 7" />
              <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 17 7 17 7" />
              <path d="M4 22h16" />
              <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
              <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
              <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold tracking-tight">
            Sales Leaderboard
          </h1>
          <p className="text-lg text-muted-foreground max-w-md mx-auto">
            Track your team&apos;s performance in real-time. See who&apos;s
            closing deals, driving revenue, and crushing their quota.
          </p>
        </div>

        <ConnectButton connected={false} />

        <p className="text-xs text-muted-foreground mt-4">
          Powered by Attio CRM
        </p>
      </div>
    );
  }

  // Connected — show the leaderboard
  const period = searchParams.period || "this-month";
  const sortBy = searchParams.sort || "revenue";

  const client = await getAttioClient();

  let data = null;
  if (client) {
    try {
      data = await getLeaderboardData(client, period);
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
    }
  }

  // Sort reps
  const sortedReps = data
    ? [...data.reps].sort((a, b) => {
        switch (sortBy) {
          case "deals":
            return b.dealsWon - a.dealsWon;
          case "avg-deal":
            return b.avgDealSize - a.avgDealSize;
          case "win-rate":
            return b.winRate - a.winRate;
          case "revenue":
          default:
            return b.totalRevenue - a.totalRevenue;
        }
      })
    : [];

  return (
    <div className="flex h-screen">
      <Sidebar workspaceName={session.workspaceName} />
      <div className="flex flex-1 flex-col">
        <Topbar connected={true} />
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-tight">
                  Sales Leaderboard
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  Track team performance across deals, revenue, and win rates.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href={`/tv?period=${period}`}
                  className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
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
                    <rect width="20" height="15" x="2" y="3" rx="2" />
                    <polyline points="8 21 12 21 16 21" />
                    <line x1="12" x2="12" y1="18" y2="21" />
                  </svg>
                  TV Mode
                </Link>
                <TimePeriodSelect currentPeriod={period} />
              </div>
            </div>

            {/* Summary Metrics */}
            {data && (
              <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard
                  title="Total Revenue"
                  value={formatCurrencyFull(data.totalRevenue)}
                  subtitle={`${data.reps.length} reps contributing`}
                  trend="up"
                />
                <MetricCard
                  title="Deals Closed"
                  value={data.totalDeals.toString()}
                  subtitle={period
                    .replace("-", " ")
                    .replace(/^\w/, (c) => c.toUpperCase())}
                />
                <MetricCard
                  title="Average Deal Size"
                  value={formatCurrency(data.avgDealSize)}
                  subtitle="Across all reps"
                />
                <MetricCard
                  title="Team Win Rate"
                  value={
                    data.reps.length > 0
                      ? `${Math.round(
                          (data.reps.reduce((sum, r) => sum + r.winRate, 0) /
                            data.reps.length) *
                            100
                        )}%`
                      : "0%"
                  }
                  subtitle="Won vs. total closed"
                />
              </div>
            )}

            {/* Leaderboard Table */}
            {data ? (
              <LeaderboardTable
                reps={sortedReps}
                sortBy={sortBy}
                period={period}
              />
            ) : (
              <div className="rounded-lg border border-border bg-card p-12 text-center">
                <p className="text-muted-foreground">
                  Unable to load leaderboard data. Please check your connection.
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
