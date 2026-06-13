import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useFeederStatus } from "@/features/devices/hooks/useFeederStatus";
import { cn } from "@/lib/utils";

const STATUS_LABEL = {
  online: "Online",
  offline: "Offline",
  connecting: "Connecting",
} as const;

const STATUS_TOOLTIP = {
  online: "The Seerynx sensor is connected",
  offline: "The Seerynx sensor is not responding",
  connecting: "Connecting to the Seerynx sensor...",
} as const;

const STATUS_COLOR = {
  online: "bg-primary",
  offline: "bg-destructive",
  connecting: "bg-muted-foreground/40",
} as const;

const STATUS_TEXT_COLOR = {
  online: "text-primary",
  offline: "text-destructive",
  connecting: "text-muted-foreground",
} as const;

export function FeederStatusIndicator() {
  const status = useFeederStatus();

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Badge
            variant="outline"
            className={cn(
              "cursor-default gap-1.5 border-transparent bg-muted/50 backdrop-blur-sm",
              STATUS_TEXT_COLOR[status],
            )}
          >
            <span
              className={cn(
                "size-2 rounded-full",
                STATUS_COLOR[status],
                status === "connecting" && "animate-pulse",
              )}
            />
            {STATUS_LABEL[status]}
          </Badge>
        }
      />
      <TooltipContent>{STATUS_TOOLTIP[status]}</TooltipContent>
    </Tooltip>
  );
}
