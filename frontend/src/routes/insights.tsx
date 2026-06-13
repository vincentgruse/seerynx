import { createFileRoute } from "@tanstack/react-router";
import { Lightbulb, TrendingUp, Wheat, Home } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { EChart } from "@/components/charts/EChart";
import { useQuery } from "@tanstack/react-query";
import {
  getAttractApiAttractGetOptions,
  getWeatherCorrelationApiWeatherCorrelationGetOptions,
} from "@/client/@tanstack/react-query.gen";
import { useHeatmap } from "@/features/sightings/hooks/useSightings";
import { celsiusToFahrenheit } from "@/utils/format";

export const Route = createFileRoute("/insights")({
  component: Insights,
});

const miniChartOption = {
  tooltip: { show: false },
  legend: { show: false },
  visualMap: { show: false },
  grid: { left: 8, right: 8, top: 4, bottom: 4 },
};

function Insights() {
  const { data: heatmap, isLoading: heatmapLoading } = useHeatmap();
  const { data: correlation, isLoading: correlationLoading } = useQuery(
    getWeatherCorrelationApiWeatherCorrelationGetOptions(),
  );
  const { data: suggestions, isLoading: suggestionsLoading } = useQuery(
    getAttractApiAttractGetOptions(),
  );

  const hours = Array.from({ length: 24 }, (_, i) =>
    String(i).padStart(2, "0"),
  );
  const audioCounts = hours.map(
    (h) => heatmap?.find((e) => e.hour === h)?.audio_count ?? 0,
  );
  const visionCounts = hours.map(
    (h) => heatmap?.find((e) => e.hour === h)?.vision_count ?? 0,
  );

  const humidities = correlation?.map((c) => c.humidity) ?? [];
  const minHumidity = humidities.length ? Math.min(...humidities) : 0;
  const maxHumidity = humidities.length ? Math.max(...humidities) : 100;

  const heatmapOption = {
    tooltip: { trigger: "axis" as const },
    legend: { data: ["Audio", "Vision"], top: 0 },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: "category" as const,
      data: hours.map((h) => `${h}:00`),
      axisLabel: { hideOverlap: true },
    },
    yAxis: { type: "value" as const },
    series: [
      {
        name: "Audio",
        type: "line" as const,
        smooth: true,
        data: audioCounts,
        itemStyle: { color: "#76c09e" },
      },
      {
        name: "Vision",
        type: "line" as const,
        smooth: true,
        data: visionCounts,
        itemStyle: { color: "#0d9298" },
      },
    ],
  };

  const correlationOption = {
    tooltip: {
      trigger: "item" as const,
      formatter: (param: unknown) => {
        const p = param as { data: number[] };
        return `Temp: ${p.data[0]}°F<br/>Visits: ${p.data[1]}<br/>Humidity: ${p.data[2]}%`;
      },
    },
    grid: { left: 50, right: 30, top: 30, bottom: 60 },
    xAxis: {
      type: "value" as const,
      name: "Temperature (°F)",
      nameLocation: "middle" as const,
      nameGap: 30,
    },
    yAxis: {
      type: "value" as const,
      name: "Visits",
      nameLocation: "middle" as const,
      nameGap: 40,
    },
    visualMap: {
      dimension: 2,
      min: minHumidity,
      max: maxHumidity,
      calculable: true,
      orient: "horizontal" as const,
      left: "center" as const,
      bottom: 0,
      text: ["Humid", "Dry"],
      inRange: { color: ["#bfe8e8", "#0d9298"] },
    },
    series: [
      {
        type: "scatter" as const,
        symbolSize: 14,
        data: correlation?.map((c) => [
          celsiusToFahrenheit(c.temperature_c),
          c.visit_count,
          c.humidity,
        ]),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Insights</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Activity patterns, weather effects, and feeder tips
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CollapsibleSection
          title="Activity by Hour"
          collapsedPreview={
            !heatmapLoading && (
              <EChart
                height="8vh"
                option={{
                  ...heatmapOption,
                  ...miniChartOption,
                  xAxis: { ...heatmapOption.xAxis, show: false },
                  yAxis: { ...heatmapOption.yAxis, show: false },
                }}
              />
            )
          }
        >
          {heatmapLoading ? (
            <Skeleton className="h-[30vh] rounded-lg" />
          ) : (
            <EChart height="30vh" option={heatmapOption} />
          )}
        </CollapsibleSection>

        <CollapsibleSection
          title="Weather Correlation"
          collapsedPreview={
            !correlationLoading &&
            correlation &&
            correlation.length > 0 && (
              <EChart
                height="8vh"
                option={{
                  ...correlationOption,
                  ...miniChartOption,
                  xAxis: {
                    ...correlationOption.xAxis,
                    show: false,
                    name: undefined,
                  },
                  yAxis: {
                    ...correlationOption.yAxis,
                    show: false,
                    name: undefined,
                  },
                }}
              />
            )
          }
        >
          {correlationLoading ? (
            <Skeleton className="h-[30vh] rounded-lg" />
          ) : correlation?.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <TrendingUp className="size-12 mb-4" />
              <p className="text-sm">Not enough data yet</p>
            </div>
          ) : (
            <EChart height="30vh" option={correlationOption} />
          )}
        </CollapsibleSection>
      </div>

      <CollapsibleSection title="Attract More Birds" maxHeight="max-h-[40vh]">
        {suggestionsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-28 rounded-lg" />
            ))}
          </div>
        ) : suggestions?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <Lightbulb className="size-12 mb-4" />
            <p className="text-sm">No suggestions available yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suggestions?.map((s) => (
              <Card key={s.common_name}>
                <CardHeader className="flex flex-row items-center gap-2 pb-2">
                  <Lightbulb className="h-4 w-4 text-muted-foreground" />
                  <CardTitle className="text-sm">{s.common_name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-muted-foreground">
                  {s.food && (
                    <p className="flex items-center gap-1.5">
                      <Wheat className="size-3.5 shrink-0" /> {s.food}
                    </p>
                  )}
                  {s.feeder_types && (
                    <p className="flex items-center gap-1.5">
                      <Home className="size-3.5 shrink-0" /> {s.feeder_types}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CollapsibleSection>
    </div>
  );
}
