import { X, Check, Binoculars, Clock, Bird } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { SpeciesBadge } from "@/components/SpeciesBadge";
import { formatTimestamp, formatTime, formatConfidence } from "@/utils/format";
import { cn } from "@/lib/utils";
import type { SightingResponse } from "@/client/types.gen";

interface SightingCardProps {
  sightings: SightingResponse[];
  selectMode?: boolean;
  selected?: boolean;
  onToggleSelect?: () => void;
  onDelete?: () => void;
  showDetectionCount?: boolean;
}

export function SightingCard({
  sightings,
  selectMode = false,
  selected = false,
  onToggleSelect,
  onDelete,
  showDetectionCount = true,
}: SightingCardProps) {
  const latest = sightings[0];
  const navigate = useNavigate();

  const handleClick = () => {
    if (selectMode) {
      onToggleSelect?.();
    } else {
      navigate({ to: "/species/$name", params: { name: latest.common_name } });
    }
  };

  return (
    <Card
      className={cn(
        "pt-0 overflow-hidden hover:shadow-md hover:scale-[1.02] transition duration-300 ease-out relative group cursor-pointer",
        selected && "ring-2 ring-primary",
      )}
      onClick={handleClick}
    >
      {selectMode && (
        <div
          className={cn(
            "absolute top-2 left-2 z-10 flex size-5 items-center justify-center rounded-full border-2 bg-background/80",
            selected
              ? "border-primary bg-primary text-primary-foreground"
              : "border-muted-foreground/50",
          )}
        >
          {selected && <Check className="size-3.5" />}
        </div>
      )}
      {!selectMode && onDelete && (
        <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
          <DropdownMenu>
            <DropdownMenuTrigger
              className="flex size-6 items-center justify-center rounded-full bg-background/80 text-muted-foreground hover:text-foreground hover:bg-background"
              aria-label="Sighting options"
              onClick={(e) => e.stopPropagation()}
            >
              <X className="size-3.5" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem variant="destructive" onClick={onDelete}>
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
      {latest.photo_path || latest.species_photo_path ? (
        <div className="aspect-video bg-muted relative overflow-hidden rounded-t-xl">
          <img
            src={`${import.meta.env.VITE_API_URL}/api/photos/${latest.photo_path ?? latest.species_photo_path}`}
            alt={latest.common_name}
            className="w-full h-full object-contain rounded-t-xl"
          />
        </div>
      ) : (
        <div className="aspect-video bg-muted flex items-center justify-center rounded-t-xl">
          <Bird className="size-10 text-muted-foreground" />
        </div>
      )}
      <CardHeader className="pb-2 pt-3 px-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-semibold text-sm leading-tight">
              {latest.common_name}
            </h3>
            {latest.scientific_name && (
              <p className="text-xs text-muted-foreground italic mt-0.5">
                {latest.scientific_name}
              </p>
            )}
          </div>
          <ConfidenceBadge confidence={latest.confidence} />
        </div>
      </CardHeader>
      <CardContent className="px-3">
        <div className="flex items-center justify-between">
          <SpeciesBadge source={latest.source} />
          {showDetectionCount && sightings.length > 1 ? (
            <DropdownMenu>
              <DropdownMenuTrigger
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                onClick={(e) => e.stopPropagation()}
              >
                {sightings.length}
                <Binoculars className="size-3" />
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="min-w-48 max-h-64 overflow-y-auto"
              >
                <DropdownMenuGroup>
                  <DropdownMenuLabel>All sightings today</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {sightings.map((s) => (
                    <DropdownMenuItem
                      key={s.id}
                      className="flex items-center justify-between gap-3 text-foreground focus:text-foreground"
                    >
                      <span className="flex items-center gap-1.5 whitespace-nowrap">
                        <Clock className="size-3 text-muted-foreground" />
                        {formatTime(s.timestamp)}
                      </span>
                      <span className="text-xs font-medium tabular-nums">
                        {formatConfidence(s.confidence)}
                      </span>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <span className="text-xs text-muted-foreground">
              {formatTimestamp(latest.timestamp)}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
