"use client";

import { Badge } from "@/components/ui/badge";

interface UsageBadgeProps {
  used: number;
  limit: number | null;
  label: string;
}

export function UsageBadge({ used, limit, label }: UsageBadgeProps) {
  if (limit === null) {
    return (
      <Badge variant="secondary" className="text-xs">
        {label}: Unlimited
      </Badge>
    );
  }

  const isAtLimit = used >= limit;

  return (
    <Badge
      variant={isAtLimit ? "destructive" : "secondary"}
      className="text-xs"
    >
      {label}: {used}/{limit}
    </Badge>
  );
}
