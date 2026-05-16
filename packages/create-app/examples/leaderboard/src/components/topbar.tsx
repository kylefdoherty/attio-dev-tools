import { ConnectButton } from "./connect-button";

interface TopbarProps {
  connected: boolean;
}

export function Topbar({ connected }: TopbarProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <div className="text-sm text-muted-foreground">
        Real-time sales performance
      </div>
      <div className="flex items-center gap-3">
        <ConnectButton connected={connected} />
      </div>
    </header>
  );
}
