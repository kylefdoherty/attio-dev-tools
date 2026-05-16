# My Attio App

A Next.js app powered by the Attio CRM API with OAuth authentication, session management, and a ready-to-use app shell.

## Quick Start

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env.local
   ```

   Fill in your Attio OAuth credentials. Get them from [Attio Developer Settings](https://app.attio.com/settings/developers).

   Generate a session secret:

   ```bash
   openssl rand -hex 32
   ```

3. **Run the dev server:**

   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) and click "Connect Attio Workspace".

## Project Structure

```
src/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing + dashboard
│   ├── api/auth/
│   │   ├── connect/route.ts    # Initiates OAuth flow
│   │   ├── callback/route.ts   # Handles OAuth callback
│   │   └── disconnect/route.ts # Clears session
│   └── (app)/                  # Authenticated pages (add yours here)
│       └── layout.tsx          # App shell with sidebar + topbar
├── lib/
│   ├── attio.ts                # getAttioClient() — server-side Attio SDK
│   ├── session.ts              # iron-session cookie management
│   ├── auth.ts                 # withAuth() route wrapper, webhook verification
│   └── utils.ts                # cn() Tailwind utility
└── components/
    ├── sidebar.tsx             # App sidebar navigation
    ├── topbar.tsx              # Top header bar
    ├── connect-button.tsx      # OAuth connect/disconnect button
    └── workspace-badge.tsx     # "Connected to X" indicator
```

## Using the Attio Client

In any Server Component or API route:

```typescript
import { getAttioClient } from "@/lib/attio";

export default async function MyPage() {
  const client = await getAttioClient();
  if (!client) return <p>Not connected</p>;

  const { data: records } = await client.records.query({
    object: "companies",
    limit: 10,
  });

  return <ul>{records.map((r) => <li key={r.id.record_id}>{r.id.record_id}</li>)}</ul>;
}
```

## Creating Authenticated API Routes

```typescript
import { withAuth } from "@/lib/auth";
import { getAttioClient } from "@/lib/attio";
import { NextResponse } from "next/server";

export const GET = withAuth(async () => {
  const client = (await getAttioClient())!;
  const { data } = await client.records.query({ object: "people", limit: 5 });
  return NextResponse.json(data);
});
```

## Deploy to Vercel

1. Push your repo to GitHub.
2. Import it on [vercel.com](https://vercel.com).
3. Add environment variables in the Vercel dashboard (see `.env.example`).
4. Update `ATTIO_REDIRECT_URI` to your production URL: `https://your-app.vercel.app/api/auth/callback`.

## Tech Stack

- [Next.js 14](https://nextjs.org/) (App Router)
- [Attio Node SDK](https://www.npmjs.com/package/attio-node)
- [iron-session](https://github.com/vvo/iron-session) (encrypted cookie sessions)
- [Tailwind CSS](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/) design tokens
- TypeScript
