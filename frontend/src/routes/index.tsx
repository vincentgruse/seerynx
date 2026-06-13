import { createFileRoute } from "@tanstack/react-router";
import { Bird, Flame, Music, Star } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { StatCard } from "@/components/StatCard";
import { SightingsGrid } from "@/features/sightings/components/SightingsGrid";
import {
  useTodaySightings,
  useStreak,
} from "@/features/sightings/hooks/useSightings";
import { getNearbyApiSightingsNearbyGetOptions } from "@/client/@tanstack/react-query.gen";

export const Route = createFileRoute("/")({
  component: Dashboard,
});

function Dashboard() {
  const { data: sightings, isLoading: sightingsLoading } = useTodaySightings();
  const { data: streak } = useStreak();
  const { data: nearbySightings } = useQuery(
    getNearbyApiSightingsNearbyGetOptions(),
  );

  const uniqueSpecies = new Set(sightings?.map((s) => s.common_name)).size;
  const audioCount = nearbySightings?.length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Today's feeder activity
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Today's Visits"
          value={sightings?.length ?? 0}
          icon={Bird}
          subtitle="feeder sightings"
        />
        <StatCard
          title="Species Seen"
          value={uniqueSpecies}
          icon={Star}
          subtitle="unique species today"
        />
        <StatCard
          title="Audio Detections"
          value={audioCount}
          icon={Music}
          subtitle="nearby birds heard"
        />
        <StatCard
          title="Day Streak"
          value={streak?.streak ?? 0}
          icon={Flame}
          subtitle="consecutive days"
        />
      </div>

      <SightingsGrid
        title="Today's Visitors"
        sightings={sightings}
        isLoading={sightingsLoading}
        emptyIcon={Bird}
        emptyMessage="No visitors yet today"
        emptySubMessage="Check back later!"
      />
    </div>
  );
}
