import { NextResponse } from "next/server";
import { randomBytes } from "node:crypto";
import { getSession } from "@/lib/session";

export async function GET() {
  const state = randomBytes(16).toString("hex");

  // Store state in session for CSRF protection
  const session = await getSession();
  (session as any).oauthState = state;
  await session.save();

  const params = new URLSearchParams({
    client_id: process.env.ATTIO_CLIENT_ID!,
    redirect_uri: process.env.ATTIO_REDIRECT_URI!,
    response_type: "code",
    state,
  });

  const authorizeUrl = `https://app.attio.com/authorize?${params.toString()}`;

  return NextResponse.redirect(authorizeUrl);
}
