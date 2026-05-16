import { NextResponse } from "next/server";
import { getSession } from "@/lib/session";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const error = url.searchParams.get("error");

  if (error) {
    console.error("OAuth error:", error);
    return NextResponse.redirect(new URL("/?error=oauth_denied", request.url));
  }

  if (!code || !state) {
    return NextResponse.redirect(
      new URL("/?error=missing_params", request.url)
    );
  }

  // Verify state matches
  const session = await getSession();
  if ((session as any).oauthState !== state) {
    return NextResponse.redirect(
      new URL("/?error=invalid_state", request.url)
    );
  }
  delete (session as any).oauthState;

  // Exchange code for tokens
  const tokenResponse = await fetch("https://app.attio.com/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "authorization_code",
      client_id: process.env.ATTIO_CLIENT_ID,
      client_secret: process.env.ATTIO_CLIENT_SECRET,
      redirect_uri: process.env.ATTIO_REDIRECT_URI,
      code,
    }),
  });

  if (!tokenResponse.ok) {
    console.error(
      "Token exchange failed:",
      tokenResponse.status,
      await tokenResponse.text()
    );
    return NextResponse.redirect(
      new URL("/?error=token_exchange_failed", request.url)
    );
  }

  const tokenData = await tokenResponse.json();

  // Store tokens in session
  session.accessToken = tokenData.access_token;
  session.refreshToken = tokenData.refresh_token;
  session.expiresAt = Date.now() + tokenData.expires_in * 1000;

  // Fetch workspace info
  try {
    const workspaceResponse = await fetch(
      "https://api.attio.com/v2/self",
      {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      }
    );
    if (workspaceResponse.ok) {
      const workspaceData = await workspaceResponse.json();
      session.workspaceName = workspaceData.data?.workspace?.name;
      session.workspaceId = workspaceData.data?.workspace?.id;
    }
  } catch {
    // Non-fatal — workspace name is optional
  }

  await session.save();

  return NextResponse.redirect(new URL("/", request.url));
}
