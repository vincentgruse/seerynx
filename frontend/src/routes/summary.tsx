import { createFileRoute } from "@tanstack/react-router";
import { Bird, BarChart3, Star } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { useQuery } from "@tanstack/react-query";
import { getWeeklySummaryApiSummaryWeeklyGetOptions } from "@/client/@tanstack/react-query.gen";

export const Route = createFileRoute("/summary")({
  component: WeeklySummary,
});

function WeeklySummary() {
  const { data: summary, isLoading } = useQuery(
    getWeeklySummaryApiSummaryWeeklyGetOptions(),
  );

  const totalVisits = summary?.reduce((sum, e) => sum + e.visits, 0) ?? 0;
  const totalSpecies =
    summary?.reduce((sum, e) => sum + e.species_count, 0) ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Weekly Summary</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Activity broken down by week
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Visits"
          value={totalVisits}
          icon={Bird}
          subtitle="all time"
        />
        <StatCard
          title="Species Recorded"
          value={totalSpecies}
          icon={Star}
          subtitle="all time"
        />
      </div>
      <CollapsibleSection title="By Week" maxHeight="max-h-[40vh]">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg" />
            ))}
          </div>
        ) : summary?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <BarChart3 className="size-12 mb-4" />
            <p className="text-sm">No weekly data yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {[...(summary ?? [])].reverse().map((entry) => (
              <Card key={entry.week}>
                <CardContent className="flex items-center justify-between py-3 px-4">
                  <p className="font-medium text-sm">Week of {entry.week}</p>
                  <div className="flex gap-6 text-sm">
                    <span>
                      <span className="font-semibold">{entry.visits}</span>
                      <span className="text-muted-foreground ml-1">visits</span>
                    </span>
                    <span>
                      <span className="font-semibold">
                        {entry.species_count}
                      </span>
                      <span className="text-muted-foreground ml-1">
                        species
                      </span>
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CollapsibleSection>
    </div>
  );
}
