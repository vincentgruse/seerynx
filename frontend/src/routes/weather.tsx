import { createFileRoute } from "@tanstack/react-router";
import { Droplets, Thermometer } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CollapsibleSection } from "@/components/CollapsibleSection";
import { RangeIndicator } from "@/components/RangeIndicator";
import { EChart } from "@/components/charts/EChart";
import { useQuery } from "@tanstack/react-query";
import { getWeatherApiWeatherGetOptions } from "@/client/@tanstack/react-query.gen";
import { celsiusToFahrenheit, formatTimestamp } from "@/utils/format";

export const Route = createFileRoute("/weather")({
  component: Weather,
});

function Weather() {
  const { data: readings, isLoading } = useQuery(
    getWeatherApiWeatherGetOptions(),
  );

  const latest = readings?.[0];
  const chronological = [...(readings ?? [])].reverse();

  const temps = chronological.map((r) => celsiusToFahrenheit(r.temperature_c));
  const humidities = chronological.map((r) => r.humidity);
  const tempMin = temps.length ? Math.min(...temps) : undefined;
  const tempMax = temps.length ? Math.max(...temps) : undefined;
  const humidityMin = humidities.length ? Math.min(...humidities) : undefined;
  const humidityMax = humidities.length ? Math.max(...humidities) : undefined;

  const chartOption = {
    tooltip: { trigger: "axis" as const },
    legend: { data: ["Temperature (°F)", "Humidity (%)"], top: 0 },
    grid: { left: 50, right: 50, top: 50, bottom: 40 },
    xAxis: {
      type: "time" as const,
      axisLabel: { hideOverlap: true },
    },
    yAxis: [
      { type: "value" as const, position: "left" as const },
      { type: "value" as const, position: "right" as const },
    ],
    series: [
      {
        name: "Temperature (°F)",
        type: "line" as const,
        smooth: true,
        yAxisIndex: 0,
        itemStyle: { color: "#ff9f1c" },
        data: chronological.map((r) => [
          new Date(r.timestamp).getTime(),
          celsiusToFahrenheit(r.temperature_c),
        ]),
      },
      {
        name: "Humidity (%)",
        type: "line" as const,
        smooth: true,
        yAxisIndex: 1,
        itemStyle: { color: "#0d9298" },
        data: chronological.map((r) => [
          new Date(r.timestamp).getTime(),
          r.humidity,
        ]),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Weather</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Temperature and humidity at the feeder
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Current Conditions</CardTitle>
          </CardHeader>
          <CardContent className="flex-1">
            <div className="relative flex flex-col justify-start pt-8 h-full gap-20">
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 text-muted-foreground mb-2">
                  <Thermometer className="h-5 w-5" />
                  <span className="text-lg">Temperature</span>
                </div>
                <div className="text-6xl font-bold">
                  {latest
                    ? `${celsiusToFahrenheit(latest.temperature_c).toFixed(1)}°F`
                    : "—"}
                </div>
                {tempMin !== undefined && tempMax !== undefined && latest && (
                  <RangeIndicator
                    min={tempMin}
                    max={tempMax}
                    current={celsiusToFahrenheit(latest.temperature_c)}
                    formatValue={(v) => `${v.toFixed(1)}°`}
                  />
                )}
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 text-muted-foreground mb-2">
                  <Droplets className="h-5 w-5" />
                  <span className="text-lg">Humidity</span>
                </div>
                <div className="text-6xl font-bold">
                  {latest ? `${latest.humidity.toFixed(1)}%` : "—"}
                </div>
                {humidityMin !== undefined &&
                  humidityMax !== undefined &&
                  latest && (
                    <RangeIndicator
                      min={humidityMin}
                      max={humidityMax}
                      current={latest.humidity}
                      formatValue={(v) => `${v.toFixed(1)}%`}
                    />
                  )}
              </div>
              {latest && (
                <p className="absolute inset-x-0 bottom-0 text-xs text-muted-foreground text-center">
                  as of {formatTimestamp(latest.timestamp)}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Temperature & Humidity</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[35vh] rounded-lg" />
            ) : readings && readings.length > 0 ? (
              <EChart height="35vh" option={chartOption} />
            ) : (
              <div className="flex flex-col items-center justify-center h-[35vh] text-muted-foreground">
                <Thermometer className="size-10 mb-2" />
                <p className="text-sm">No weather data yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <CollapsibleSection title="Recent Readings" maxHeight="max-h-[40vh]">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <Skeleton key={i} className="h-12 rounded-lg" />
            ))}
          </div>
        ) : readings?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <Thermometer className="size-12 mb-4" />
            <p className="text-sm">No weather data yet</p>
            <p className="text-xs mt-1">Check your DHT22 sensor connection</p>
          </div>
        ) : (
          <div className="space-y-2">
            {readings?.map((reading) => (
              <Card key={reading.id}>
                <CardContent className="flex items-center justify-between py-3 px-4">
                  <span className="text-xs text-muted-foreground">
                    {formatTimestamp(reading.timestamp)}
                  </span>
                  <div className="flex gap-6">
                    <span className="flex items-center gap-1.5 text-sm font-medium">
                      <Thermometer className="size-3.5" />
                      {celsiusToFahrenheit(reading.temperature_c).toFixed(1)}°F
                    </span>
                    <span className="flex items-center gap-1.5 text-sm font-medium">
                      <Droplets className="size-3.5" />
                      {reading.humidity.toFixed(1)}%
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
