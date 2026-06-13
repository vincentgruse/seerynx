import { createFileRoute } from "@tanstack/react-router";
import { Bird, CalendarDays } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { useQuery } from "@tanstack/react-query";
import { getCalendarApiSightingsCalendarGetOptions } from "@/client/@tanstack/react-query.gen";

export const Route = createFileRoute("/calendar")({
  component: Calendar,
});

function Calendar() {
  const { data: calendar, isLoading } = useQuery(
    getCalendarApiSightingsCalendarGetOptions(),
  );

  const totalDays = calendar?.length ?? 0;
  const totalVisits = calendar?.reduce((sum, e) => sum + e.count, 0) ?? 0;
  const maxCount = Math.max(...(calendar?.map((e) => e.count) ?? [1]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Calendar</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Daily visit history
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Active Days"
          value={totalDays}
          icon={Bird}
          subtitle="days with sightings"
        />
        <StatCard
          title="Total Visits"
          value={totalVisits}
          icon={Bird}
          subtitle="all time"
        />
      </div>
      <CollapsibleSection title="Visit History" maxHeight="max-h-[40vh]">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <Skeleton key={i} className="h-12 rounded-lg" />
            ))}
          </div>
        ) : calendar?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <CalendarDays className="size-12 mb-4" />
            <p className="text-sm">No visit history yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {[...(calendar ?? [])].reverse().map((entry) => (
              <Card key={entry.day}>
                <CardContent className="flex items-center justify-between py-3 px-4">
                  <p className="font-medium text-sm">{entry.day}</p>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${(entry.count / maxCount) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold w-8 text-right">
                      {entry.count}
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
