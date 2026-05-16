"use client";

import { cn } from "@/lib/utils";

interface ConnectButtonProps {
  connected: boolean;
  className?: string;
}

export function ConnectButton({ connected, className }: ConnectButtonProps) {
  if (connected) {
    return (
      <a
        href="/api/auth/disconnect"
        className={cn(
          "inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium",
          "border border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground",
          "transition-colors",
          className
        )}
      >
        Disconnect
      </a>
    );
  }

  return (
    <a
      href="/api/auth/connect"
      className={cn(
        "inline-flex items-center gap-2 rounded-lg px-6 py-3 text-sm font-medium",
        "bg-primary text-primary-foreground hover:bg-primary/90",
        "transition-all shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30",
        className
      )}
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
        <polyline points="10 17 15 12 10 7" />
        <line x1="15" y1="12" x2="3" y2="12" />
      </svg>
      Connect Attio Workspace
    </a>
  );
}
