import { NextResponse } from "next/server";
import { getSession } from "./session";

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
