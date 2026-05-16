# create-attio-app

Scaffold an Attio-powered Next.js app with OAuth, session management, and a ready-to-use app shell.

## Usage

```bash
npx create-attio-app my-app
cd my-app
cp .env.example .env.local
npm run dev
```

## What You Get

- **Attio OAuth flow** — Connect/disconnect a workspace. Tokens stored in encrypted cookies (no database).
- **Attio client wrapper** — `getAttioClient()` for Server Components and API routes.
- **App shell** — Sidebar + topbar layout with Tailwind CSS. Dark mode ready.
- **Auth helpers** — `withAuth()` wrapper for API routes, webhook signature verification.
- **Vercel-ready** — `vercel.json` and `.env.example` included.

## Stack

- Next.js 14 (App Router)
- attio-node SDK
- iron-session (encrypted cookies)
- Tailwind CSS + shadcn/ui design tokens
- TypeScript

## Development

This package lives in the `attio-dev-tools` monorepo at `packages/create-app/`.

To test the scaffolder locally:

```bash
node bin/create-app.js test-app
cd test-app
npm run dev
```
