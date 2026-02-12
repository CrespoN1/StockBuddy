"use client";

import { useEffect, useRef } from "react";
import type { OHLCVBar } from "@/types";

interface CandlestickChartProps {
  data: OHLCVBar[];
  height?: number;
}

export function CandlestickChart({ data, height = 400 }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof import("lightweight-charts").createChart> | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data.length) return;

    let cancelled = false;

    async function initChart() {
      const { createChart, CandlestickSeries, ColorType } = await import(
        "lightweight-charts"
      );

      if (cancelled || !containerRef.current) return;

      // Remove previous chart
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }

      const chart = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height,
        layout: {
          background: { type: ColorType.Solid, color: "transparent" },
          textColor: "#64748b",
        },
        grid: {
          vertLines: { color: "#e2e8f0" },
          horzLines: { color: "#e2e8f0" },
        },
        timeScale: {
          borderColor: "#e2e8f0",
        },
        rightPriceScale: {
          borderColor: "#e2e8f0",
        },
      });

      const series = chart.addSeries(CandlestickSeries, {
        upColor: "#16a34a",
        downColor: "#dc2626",
        borderUpColor: "#16a34a",
        borderDownColor: "#dc2626",
        wickUpColor: "#16a34a",
        wickDownColor: "#dc2626",
      });

      const chartData = data.map((bar) => ({
        time: (Math.floor(new Date(bar.timestamp).getTime() / 1000)) as import("lightweight-charts").UTCTimestamp,
        open: bar.open,
        high: bar.high,
        low: bar.low,
        close: bar.close,
      }));

      series.setData(chartData);
      chart.timeScale().fitContent();
      chartRef.current = chart;

      const handleResize = () => {
        if (containerRef.current) {
          chart.applyOptions({ width: containerRef.current.clientWidth });
        }
      };
      window.addEventListener("resize", handleResize);

      // Store cleanup
      (chart as unknown as Record<string, () => void>).__resizeCleanup = () => {
        window.removeEventListener("resize", handleResize);
      };
    }

    initChart();

    return () => {
      cancelled = true;
      if (chartRef.current) {
        const cleanup = (chartRef.current as unknown as Record<string, () => void>).__resizeCleanup;
        if (cleanup) cleanup();
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data, height]);

  if (!data.length) {
    return (
      <div
        className="flex items-center justify-center text-sm text-muted-foreground"
        style={{ height }}
      >
        No chart data available
      </div>
    );
  }

  return <div ref={containerRef} />;
}
