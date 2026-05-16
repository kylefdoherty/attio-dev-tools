import { NextResponse } from "next/server";
import { clearSession } from "@/lib/session";

export async function POST() {
  await clearSession();
  return NextResponse.redirect(new URL("/", process.env.ATTIO_REDIRECT_URI!));
}

export async function GET() {
  await clearSession();
  return NextResponse.redirect(new URL("/", process.env.ATTIO_REDIRECT_URI!));
}
