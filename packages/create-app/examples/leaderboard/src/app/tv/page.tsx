import { redirect } from "next/navigation";
import { getSession } from "@/lib/session";
import { getAttioClient } from "@/lib/attio";
import { getLeaderboardData } from "@/lib/leaderboard";
import { TvLeaderboard } from "@/components/tv-leaderboard";

interface PageProps {
  searchParams: { period?: string };
}

export const revalidate = 60;

export default async function TvModePage({ searchParams }: PageProps) {
  const session = await getSession();

  if (!session.accessToken) {
    redirect("/");
  }

  const period = searchParams.period || "this-month";

  const client = await getAttioClient();
  if (!client) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <p className="text-muted-foreground text-2xl">
          Unable to connect to Attio.
        </p>
      </div>
    );
  }

  const data = await getLeaderboardData(client, period);
  const sortedReps = [...data.reps].sort(
    (a, b) => b.totalRevenue - a.totalRevenue
  );

  return <TvLeaderboard reps={sortedReps} data={data} period={period} />;
}
