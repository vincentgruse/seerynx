import ReactECharts from "echarts-for-react";
import { useTheme } from "next-themes";
import type { EChartsOption } from "echarts";

interface EChartProps {
  option: EChartsOption;
  height?: number | string;
  className?: string;
}

export function EChart({ option, height = 300, className }: EChartProps) {
  const { resolvedTheme } = useTheme();
  const textColor = resolvedTheme === "dark" ? "#a1a1aa" : "#71717a";
  const splitLineColor = resolvedTheme === "dark" ? "#27272a" : "#e4e4e7";

  const axisDefaults = {
    axisLabel: { color: textColor },
    axisLine: { lineStyle: { color: splitLineColor } },
    splitLine: { lineStyle: { color: splitLineColor } },
  };

  const themedOption: EChartsOption = {
    textStyle: { color: textColor },
    ...option,
    xAxis: mergeAxis(option.xAxis, axisDefaults) as EChartsOption["xAxis"],
    yAxis: mergeAxis(option.yAxis, axisDefaults) as EChartsOption["yAxis"],
  };

  return (
    <ReactECharts
      option={themedOption}
      style={{ height, width: "100%" }}
      className={className}
    />
  );
}

function mergeAxis<T>(
  axis: T | T[] | undefined,
  defaults: object,
): T | T[] | undefined {
  if (!axis) return axis;
  if (Array.isArray(axis)) {
    return axis.map((a) => ({ ...defaults, ...a }));
  }
  return { ...defaults, ...axis } as T;
}
