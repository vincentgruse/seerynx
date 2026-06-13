// The API returns naive timestamps (no timezone suffix) that represent UTC.
// Without a "Z", `Date` would parse them as local time, so add it if missing.
function parseUTCTimestamp(ts: string): Date {
  const hasTimezone = /Z|[+-]\d{2}:\d{2}$/.test(ts);
  return new Date(hasTimezone ? ts : `${ts}Z`);
}

const DISPLAY_TIMEZONE = import.meta.env.VITE_DISPLAY_TIMEZONE || "UTC";

export function formatTimestamp(ts: string): string {
  return parseUTCTimestamp(ts).toLocaleString("en-US", {
    timeZone: DISPLAY_TIMEZONE,
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatTime(ts: string): string {
  return parseUTCTimestamp(ts).toLocaleString("en-US", {
    timeZone: DISPLAY_TIMEZONE,
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatConfidence(confidence: number | null): string {
  if (confidence === null) return "N/A";
  return `${Math.round(confidence * 100)}%`;
}

export function celsiusToFahrenheit(celsius: number): number {
  return (celsius * 9) / 5 + 32;
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
