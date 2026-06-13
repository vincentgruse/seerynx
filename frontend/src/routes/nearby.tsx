import { createFileRoute } from "@tanstack/react-router";
import { Music } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { SightingsGrid } from "@/features/sightings/components/SightingsGrid";
import { useQuery } from "@tanstack/react-query";
import { getNearbyApiSightingsNearbyGetOptions } from "@/client/@tanstack/react-query.gen";

export const Route = createFileRoute("/nearby")({
  component: NearbyBirds,
});

function NearbyBirds() {
  const { data: sightings, isLoading } = useQuery(
    getNearbyApiSightingsNearbyGetOptions(),
  );

  const uniqueSpecies = new Set(sightings?.map((s) => s.common_name)).size;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Nearby Birds</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Audio detections from today
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Audio Detections"
          value={sightings?.length ?? 0}
          icon={Music}
          subtitle="birds heard today"
        />
        <StatCard
          title="Species Heard"
          value={uniqueSpecies}
          icon={Music}
          subtitle="unique species"
        />
      </div>
      <SightingsGrid
        title="Today's Audio Detections"
        sightings={sightings}
        isLoading={isLoading}
        emptyIcon={Music}
        emptyMessage="No audio detections yet today"
        emptySubMessage="Check back later!"
      />
    </div>
  );
}
