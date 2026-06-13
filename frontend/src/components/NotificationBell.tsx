import { useEffect, useRef, useState } from "react";
import { Bell, Camera, Mic2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useLatestSightings } from "@/features/sightings/hooks/useSightings";
import { formatTimestamp } from "@/utils/format";

const LAST_SEEN_KEY = "seerynx_last_seen_sighting_id";
const CLEARED_KEY = "seerynx_cleared_sighting_id";
const DISPLAY_LIMIT = 15;

export function NotificationBell() {
  const { data: sightings } = useLatestSightings(50);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [lastSeenId, setLastSeenId] = useState(() => {
    const stored = localStorage.getItem(LAST_SEEN_KEY);
    return stored ? Number(stored) : 0;
  });
  const [clearedId, setClearedId] = useState(() => {
    const stored = localStorage.getItem(CLEARED_KEY);
    return stored ? Number(stored) : 0;
  });
  const initialized = useRef(false);

  const latestId = sightings?.[0]?.id ?? 0;

  useEffect(() => {
    if (!sightings || sightings.length === 0) return;

    if (!initialized.current) {
      initialized.current = true;
      if (lastSeenId === 0) {
        // One-time seed on first load: treat existing sightings as already seen.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setLastSeenId(latestId);
        localStorage.setItem(LAST_SEEN_KEY, String(latestId));
      }
      return;
    }

    if (latestId > lastSeenId) {
      queryClient.invalidateQueries({
        predicate: (query) => {
          const id = (query.queryKey[0] as { _id?: string } | undefined)?._id;
          return id?.toLowerCase().includes("sighting") ?? false;
        },
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestId]);

  const visible = sightings?.filter((s) => s.id > clearedId) ?? [];
  const displayed = visible.slice(0, DISPLAY_LIMIT);
  const unread = visible.filter((s) => s.id > lastSeenId);

  const handleOpenChange = (open: boolean) => {
    if (!open && latestId > lastSeenId) {
      setLastSeenId(latestId);
      localStorage.setItem(LAST_SEEN_KEY, String(latestId));
    }
  };

  const handleClearAll = () => {
    setClearedId(latestId);
    localStorage.setItem(CLEARED_KEY, String(latestId));
    setLastSeenId(latestId);
    localStorage.setItem(LAST_SEEN_KEY, String(latestId));
  };

  const handleItemClick = (commonName: string) => {
    navigate({ to: "/species/$name", params: { name: commonName } });
  };

  return (
    <DropdownMenu onOpenChange={handleOpenChange}>
      <DropdownMenuTrigger
        render={
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-4 w-4" />
            {unread.length > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-4 min-w-4 px-1 text-[10px]"
              >
                {unread.length > 9 ? "9+" : unread.length}
              </Badge>
            )}
            <span className="sr-only">Notifications</span>
          </Button>
        }
      />
      <DropdownMenuContent
        align="end"
        className="w-80 max-h-80 overflow-y-auto"
      >
        <DropdownMenuGroup>
          <DropdownMenuLabel className="flex items-center justify-between gap-2">
            <span>Recent Sightings</span>
            {displayed.length > 0 && (
              <button
                type="button"
                className="text-xs font-normal text-muted-foreground hover:text-foreground"
                onClick={(e) => {
                  e.stopPropagation();
                  handleClearAll();
                }}
              >
                Clear all
              </button>
            )}
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          {displayed.length === 0 ? (
            <div className="px-2 py-4 text-center text-sm text-muted-foreground">
              No sightings yet
            </div>
          ) : (
            displayed.map((s) => (
              <DropdownMenuItem
                key={s.id}
                className="flex items-start gap-2"
                onClick={() => handleItemClick(s.common_name)}
              >
                {s.source === "audio" ? (
                  <Mic2 className="size-4 mt-0.5 shrink-0 text-green-500" />
                ) : (
                  <Camera className="size-4 mt-0.5 shrink-0 text-blue-500" />
                )}
                <div className="flex flex-col items-start gap-0.5">
                  <span className="font-medium">
                    {s.common_name}{" "}
                    {s.source === "audio" ? "heard near" : "seen in"} your yard
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatTimestamp(s.timestamp)}
                  </span>
                </div>
              </DropdownMenuItem>
            ))
          )}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
