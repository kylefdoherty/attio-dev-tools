import { NextResponse } from "next/server";
import { getSession } from "./session";
import { createHmac } from "node:crypto";

/**
 * Wraps an API route handler to require a valid Attio OAuth session.
 * Returns 401 if the user is not connected.
 */
export function withAuth(
  handler: (request: Request) => Promise<Response>
): (request: Request) => Promise<Response> {
  return async (request: Request) => {
    const session = await getSession();

    if (!session.accessToken) {
      return NextResponse.json(
        { error: "Not authenticated. Connect your Attio workspace first." },
        { status: 401 }
      );
    }

    return handler(request);
  };
}

/**
 * Verify an Attio webhook signature.
 * Pass the raw request body and the signature header value.
 */
export function verifyWebhookSignature(
  body: string,
  signature: string
): boolean {
  const secret = process.env.ATTIO_WEBHOOK_SECRET;
  if (!secret) {
    console.warn("ATTIO_WEBHOOK_SECRET not set — skipping verification");
    return true;
  }

  const expected = createHmac("sha256", secret).update(body).digest("hex");
  return expected === signature;
}
