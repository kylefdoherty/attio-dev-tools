import Link from "next/link";
import { cn } from "@/lib/utils";

interface SidebarProps {
  workspaceName?: string;
  className?: string;
}

export function Sidebar({ workspaceName, className }: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r border-border bg-card",
        className
      )}
    >
      {/* Logo / App Name */}
      <div className="flex h-14 items-center border-b border-border px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-yellow-500"
          >
            <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C7 4 7 7 7 7" />
            <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C17 4 17 7 17 7" />
            <path d="M4 22h16" />
            <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
            <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
            <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
          </svg>
          <span>Sales Leaderboard</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        <Link
          href="/"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-accent transition-colors"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 3v18h18" />
            <path d="m19 9-5 5-4-4-3 3" />
          </svg>
          Leaderboard
        </Link>
        <Link
          href="/tv"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect width="20" height="15" x="2" y="3" rx="2" />
            <polyline points="8 21 12 21 16 21" />
            <line x1="12" x2="12" y1="18" y2="21" />
          </svg>
          TV Mode
        </Link>
      </nav>

      {/* Workspace status */}
      <div className="border-t border-border p-3">
        {workspaceName ? (
          <div className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium bg-green-500/10 text-green-400">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            {workspaceName}
          </div>
        ) : (
          <div className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium bg-muted text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-muted-foreground" />
            Not connected
          </div>
        )}
      </div>
    </aside>
  );
}
