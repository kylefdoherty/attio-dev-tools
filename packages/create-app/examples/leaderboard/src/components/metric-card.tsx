import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  trend,
  className,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-5 transition-all hover:border-border/80 hover:shadow-sm",
        className
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {title}
      </p>
      <div className="mt-2 flex items-baseline gap-2">
        <p className="text-2xl font-bold tracking-tight">{value}</p>
        {trend && trend !== "neutral" && (
          <span
            className={cn(
              "text-xs font-medium",
              trend === "up" && "text-green-400",
              trend === "down" && "text-red-400"
            )}
          >
            {trend === "up" ? (
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="inline"
              >
                <path d="m18 15-6-6-6 6" />
              </svg>
            ) : (
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="inline"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            )}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}
