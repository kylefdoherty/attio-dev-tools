import { cn } from "@/lib/utils";

interface WorkspaceBadgeProps {
  workspaceName: string | undefined;
  className?: string;
}

export function WorkspaceBadge({
  workspaceName,
  className,
}: WorkspaceBadgeProps) {
  if (!workspaceName) return null;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium",
        "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
        className
      )}
    >
      <span className="h-2 w-2 rounded-full bg-green-500" />
      Connected to {workspaceName}
    </div>
  );
}
