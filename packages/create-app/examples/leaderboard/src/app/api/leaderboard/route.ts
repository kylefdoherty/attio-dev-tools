import { NextResponse } from "next/server";
import { getAttioClient } from "@/lib/attio";
import { getLeaderboardData } from "@/lib/leaderboard";
import { withAuth } from "@/lib/auth";

/**
 * GET /api/leaderboard?period=this-month&sort=revenue
 *
 * Returns aggregated leaderboard data for client-side refresh (TV mode polling).
 */
export const GET = withAuth(async (request: Request) => {
  const url = new URL(request.url);
  const period = url.searchParams.get("period") || "this-month";

  const client = await getAttioClient();
  if (!client) {
    return NextResponse.json(
      { error: "Failed to initialize Attio client" },
      { status: 500 }
    );
  }

  try {
    const data = await getLeaderboardData(client, period);
    return NextResponse.json(data, {
      headers: {
        "Cache-Control": "s-maxage=30, stale-while-revalidate=60",
      },
    });
  } catch (error) {
    console.error("Error fetching leaderboard data:", error);
    return NextResponse.json(
      { error: "Failed to fetch leaderboard data" },
      { status: 500 }
    );
  }
});
