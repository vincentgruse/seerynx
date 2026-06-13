import { Camera, Mic2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SpeciesBadgeProps {
  source: "vision" | "audio" | string;
  className?: string;
}

export function SpeciesBadge({ source, className }: SpeciesBadgeProps) {
  const Icon = source === "vision" ? Camera : Mic2;
  return (
    <Badge
      variant="outline"
      className={cn(
        "text-xs gap-1",
        source === "vision" && "border-blue-500 text-blue-500",
        source === "audio" && "border-green-500 text-green-500",
        className,
      )}
    >
      <Icon className="size-3" />
      {source === "vision" ? "Camera" : "Audio"}
    </Badge>
  );
}
