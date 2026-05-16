# Sales Leaderboard — an Attio App Example

A real-time sales leaderboard that ranks reps by deals closed, revenue booked, and win rate. Designed to be displayed on a TV in the office or viewed by sales managers.

Built with the [create-attio-app](../../) scaffold framework.

## Features

- **Leaderboard Rankings** — Reps ranked by revenue, deals, avg deal size, or win rate
- **Time Period Filtering** — This Week, This Month, This Quarter, This Year, All Time
- **Rep Detail Pages** — Click any rep to see their individual stats and deal history
- **TV Mode** — Fullscreen display optimized for wall-mounted TVs with auto-refresh every 60s
- **Dark Mode** — High-contrast dark theme by default (looks great on TVs)

## Screenshots

The leaderboard displays:
- Gold/silver/bronze rank badges for the top 3
- Revenue numbers with emphasis (glow effect for #1)
- Win rate color coding (green > 70%, yellow > 40%, red below)
- Sortable columns and time period selector

## Getting Started

### 1. Create an Attio OAuth App

Go to [Attio Developer Settings](https://app.attio.com/settings/developers) and create a new OAuth app with:
- **Redirect URI:** `http://localhost:3000/api/auth/callback`
- **Scopes:** `record:read`, `user:read`

### 2. Configure Environment

```bash
cp .env.example .env
```

Fill in your credentials:
```
ATTIO_CLIENT_ID=your_client_id
ATTIO_CLIENT_SECRET=your_client_secret
ATTIO_REDIRECT_URI=http://localhost:3000/api/auth/callback
SESSION_SECRET=<run: openssl rand -hex 32>
```

### 3. Install & Run

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and connect your Attio workspace.

### 4. TV Mode

Navigate to `/tv` or click the "TV Mode" button. Click the fullscreen icon to go truly fullscreen. The board auto-refreshes every 60 seconds.

## Data Requirements

This app reads from your Attio workspace's **Deals** object. For best results:

- Deals should have a `stage` field with statuses named "Closed Won" and "Closed Lost"
- Deals should have an `owner` field pointing to a workspace member
- Deals should have a `deal_value` (or `value`) currency field
- Deals should have a `close_date` date field

## Tech Stack

- **Next.js 14** — App Router, Server Components, ISR
- **Attio Node SDK** — OAuth + data fetching
- **Tailwind CSS** — Styling and dark mode
- **iron-session** — Encrypted session cookies
- **recharts** — Charts (optional, for future sparklines)

## Project Structure

```
src/
├── app/
│   ├── (app)/
│   │   ├── page.tsx              # Main leaderboard
│   │   ├── rep/[id]/page.tsx     # Rep detail
│   │   └── tv/page.tsx           # TV/fullscreen mode
│   ├── api/
│   │   ├── auth/                 # OAuth connect/callback/disconnect
│   │   └── leaderboard/route.ts  # JSON API for client-side polling
│   ├── layout.tsx                # Root layout (dark mode)
│   └── page.tsx                  # Landing / connect page
├── components/
│   ├── leaderboard-table.tsx     # Main rankings table
│   ├── rep-card.tsx              # Rep profile card
│   ├── time-period-select.tsx    # Period dropdown
│   ├── metric-card.tsx           # Summary stat cards
│   └── tv-leaderboard.tsx        # TV mode display
└── lib/
    ├── leaderboard.ts            # Data fetching + aggregation
    ├── attio.ts                  # Attio client wrapper
    ├── session.ts                # Session management
    ├── auth.ts                   # Auth middleware
    └── utils.ts                  # Formatting helpers
```

## License

MIT
