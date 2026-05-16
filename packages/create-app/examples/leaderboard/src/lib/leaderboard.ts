import { AttioClient } from "attio-node";
import { getTimePeriodDates } from "./utils";

export interface RepStats {
  id: string;
  name: string;
  email?: string;
  dealsWon: number;
  dealsLost: number;
  totalRevenue: number;
  avgDealSize: number;
  winRate: number;
  deals: DealRecord[];
}

export interface DealRecord {
  id: string;
  name: string;
  company?: string;
  value: number;
  closeDate: string;
  status: "won" | "lost";
}

export interface LeaderboardData {
  reps: RepStats[];
  totalRevenue: number;
  totalDeals: number;
  avgDealSize: number;
  period: string;
  lastUpdated: string;
}

/**
 * Fetch and aggregate leaderboard data from Attio.
 * Queries deals (won + lost), groups by owner, and calculates metrics.
 */
export async function getLeaderboardData(
  client: AttioClient,
  period: string = "this-month"
): Promise<LeaderboardData> {
  const { start, end } = getTimePeriodDates(period);

  // Fetch won deals and lost deals in parallel
  const [wonDeals, lostDeals, members] = await Promise.all([
    fetchDeals(client, "Won", start, end),
    fetchDeals(client, "Lost", start, end),
    fetchWorkspaceMembers(client),
  ]);

  // Build a map of member ID -> member info
  const memberMap = new Map<string, { name: string; email?: string }>();
  for (const member of members) {
    memberMap.set(member.id, { name: member.name, email: member.email });
  }

  // Aggregate deals by owner
  const repMap = new Map<
    string,
    {
      dealsWon: DealRecord[];
      dealsLost: DealRecord[];
    }
  >();

  for (const deal of wonDeals) {
    const ownerId = deal.ownerId || "unknown";
    if (!repMap.has(ownerId)) {
      repMap.set(ownerId, { dealsWon: [], dealsLost: [] });
    }
    repMap.get(ownerId)!.dealsWon.push(deal);
  }

  for (const deal of lostDeals) {
    const ownerId = deal.ownerId || "unknown";
    if (!repMap.has(ownerId)) {
      repMap.set(ownerId, { dealsWon: [], dealsLost: [] });
    }
    repMap.get(ownerId)!.dealsLost.push(deal);
  }

  // Calculate stats for each rep
  const reps: RepStats[] = [];
  for (const [ownerId, data] of repMap) {
    const memberInfo = memberMap.get(ownerId);
    const totalRevenue = data.dealsWon.reduce((sum, d) => sum + d.value, 0);
    const dealsWon = data.dealsWon.length;
    const dealsLost = data.dealsLost.length;
    const totalClosed = dealsWon + dealsLost;

    reps.push({
      id: ownerId,
      name: memberInfo?.name || "Unknown Rep",
      email: memberInfo?.email,
      dealsWon,
      dealsLost,
      totalRevenue,
      avgDealSize: dealsWon > 0 ? totalRevenue / dealsWon : 0,
      winRate: totalClosed > 0 ? dealsWon / totalClosed : 0,
      deals: [
        ...data.dealsWon.map((d) => ({ ...d, status: "won" as const })),
        ...data.dealsLost.map((d) => ({ ...d, status: "lost" as const })),
      ].sort(
        (a, b) =>
          new Date(b.closeDate).getTime() - new Date(a.closeDate).getTime()
      ),
    });
  }

  // Sort by revenue by default
  reps.sort((a, b) => b.totalRevenue - a.totalRevenue);

  const totalRevenue = reps.reduce((sum, r) => sum + r.totalRevenue, 0);
  const totalDeals = reps.reduce((sum, r) => sum + r.dealsWon, 0);

  return {
    reps,
    totalRevenue,
    totalDeals,
    avgDealSize: totalDeals > 0 ? totalRevenue / totalDeals : 0,
    period,
    lastUpdated: new Date().toISOString(),
  };
}

/**
 * Get stats for a single rep by ID.
 */
export async function getRepDetail(
  client: AttioClient,
  repId: string,
  period: string = "all-time"
): Promise<RepStats | null> {
  const data = await getLeaderboardData(client, period);
  return data.reps.find((r) => r.id === repId) || null;
}

// ─── Internal helpers ───────────────────────────────────────────────────────

interface RawDeal {
  id: string;
  name: string;
  company?: string;
  value: number;
  closeDate: string;
  ownerId?: string;
}

async function fetchDeals(
  client: AttioClient,
  status: "Won" | "Lost",
  start: Date,
  end: Date
): Promise<(RawDeal & { ownerId?: string })[]> {
  try {
    // Query deals with the given stage status
    const response = await (client as any).records.query({
      object: "deals",
      filter: {
        stage: {
          status: {
            title: `Closed ${status}`,
          },
        },
      },
      sorts: [
        {
          attribute: "close_date",
          direction: "desc",
        },
      ],
      limit: 500,
    });

    const records = response?.data || response || [];
    const deals: (RawDeal & { ownerId?: string })[] = [];

    for (const record of Array.isArray(records) ? records : []) {
      const closeDate = extractDate(record, "close_date");
      if (!closeDate) continue;

      const closeDateObj = new Date(closeDate);
      if (closeDateObj < start || closeDateObj > end) continue;

      deals.push({
        id: record.id?.record_id || record.id || "",
        name: extractText(record, "name") || "Untitled Deal",
        company: extractText(record, "company"),
        value: extractNumber(record, "deal_value") || extractNumber(record, "value") || 0,
        closeDate,
        ownerId: extractActorId(record, "owner"),
      });
    }

    return deals;
  } catch (error) {
    console.error(`Error fetching ${status} deals:`, error);
    return [];
  }
}

async function fetchWorkspaceMembers(
  client: AttioClient
): Promise<{ id: string; name: string; email?: string }[]> {
  try {
    const response = await (client as any).workspaceMembers.list();
    const members = response?.data || response || [];

    return (Array.isArray(members) ? members : []).map((m: any) => ({
      id: m.id?.workspace_member_id || m.id || "",
      name:
        [m.first_name, m.last_name].filter(Boolean).join(" ") ||
        m.name ||
        m.email_address ||
        "Unknown",
      email: m.email_address,
    }));
  } catch (error) {
    console.error("Error fetching workspace members:", error);
    return [];
  }
}

// ─── Attribute extraction helpers ──────────────────────────────────────────

function extractText(record: any, attribute: string): string | undefined {
  const values = record?.values?.[attribute];
  if (!values || !Array.isArray(values) || values.length === 0) return undefined;
  const first = values[0];
  return first?.value || first?.title || first?.name || first?.original_value || undefined;
}

function extractNumber(record: any, attribute: string): number {
  const values = record?.values?.[attribute];
  if (!values || !Array.isArray(values) || values.length === 0) return 0;
  const first = values[0];
  const raw = first?.value ?? first?.amount ?? first?.currency_value ?? 0;
  return typeof raw === "number" ? raw : parseFloat(raw) || 0;
}

function extractDate(record: any, attribute: string): string | undefined {
  const values = record?.values?.[attribute];
  if (!values || !Array.isArray(values) || values.length === 0) return undefined;
  const first = values[0];
  return first?.value || first?.original_value || undefined;
}

function extractActorId(record: any, attribute: string): string | undefined {
  const values = record?.values?.[attribute];
  if (!values || !Array.isArray(values) || values.length === 0) return undefined;
  const first = values[0];
  return (
    first?.referenced_actor_id ||
    first?.workspace_member_id ||
    first?.target_record_id ||
    first?.value ||
    undefined
  );
}
