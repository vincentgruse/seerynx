import { Clock } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface RangeIndicatorProps {
  min: number;
  max: number;
  current: number;
  formatValue: (value: number) => string;
}

export function RangeIndicator({
  min,
  max,
  current,
  formatValue,
}: RangeIndicatorProps) {
  const pct = max > min ? ((current - min) / (max - min)) * 100 : 50;
  const clamped = Math.min(100, Math.max(0, pct));

  return (
    <div className="flex items-center justify-center gap-1.5 text-xs text-muted-foreground mt-1">
      <Tooltip>
        <TooltipTrigger render={<Clock className="size-3 shrink-0" />} />
        <TooltipContent>Last 24 hours</TooltipContent>
      </Tooltip>
      <span>{formatValue(min)}</span>
      <div className="relative w-12 h-1 rounded-full bg-muted-foreground/20">
        <div
          className="absolute top-1/2 size-1.5 -translate-y-1/2 -translate-x-1/2 rounded-full bg-foreground"
          style={{ left: `${clamped}%` }}
        />
      </div>
      <span>{formatValue(max)}</span>
    </div>
  );
}
