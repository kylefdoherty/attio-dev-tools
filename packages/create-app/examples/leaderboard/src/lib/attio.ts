import { AttioClient } from "attio-node";
import { getSession } from "./session";

/**
 * Get an authenticated Attio client using the OAuth token from the session.
 * Call this from Server Components or API routes.
 *
 * Returns null if no valid session exists (user not connected).
 */
export async function getAttioClient(): Promise<AttioClient | null> {
  const session = await getSession();

  if (!session.accessToken) {
    return null;
  }

  // Check if the token is expired and needs refresh
  if (session.expiresAt && Date.now() > session.expiresAt) {
    const refreshed = await refreshAccessToken(session.refreshToken!);
    if (!refreshed) {
      return null;
    }
    session.accessToken = refreshed.accessToken;
    session.refreshToken = refreshed.refreshToken;
    session.expiresAt = refreshed.expiresAt;
    await session.save();
  }

  return new AttioClient({ apiKey: session.accessToken });
}

async function refreshAccessToken(refreshToken: string) {
  try {
    const response = await fetch("https://app.attio.com/oauth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grant_type: "refresh_token",
        client_id: process.env.ATTIO_CLIENT_ID,
        client_secret: process.env.ATTIO_CLIENT_SECRET,
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return {
      accessToken: data.access_token as string,
      refreshToken: data.refresh_token as string,
      expiresAt: Date.now() + data.expires_in * 1000,
    };
  } catch {
    return null;
  }
}
