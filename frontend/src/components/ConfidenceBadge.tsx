import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { formatConfidence } from "@/utils/format";

interface ConfidenceBadgeProps {
  confidence: number | null;
  className?: string;
}

export function ConfidenceBadge({
  confidence,
  className,
}: ConfidenceBadgeProps) {
  const value = confidence ?? 0;
  const variant =
    value >= 0.8 ? "default" : value >= 0.5 ? "secondary" : "outline";

  return (
    <Badge variant={variant} className={cn("text-xs", className)}>
      {formatConfidence(confidence)}
    </Badge>
  );
}
