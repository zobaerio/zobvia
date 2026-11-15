import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { theme } from "../theme";
import { cuesForScene } from "../timing";

interface Metric {
  label: string;
  target: number;
  suffix: string;
  /** Bar width at full growth, 0-1. */
  bar: number;
}

const METRICS: Metric[] = [
  { label: "মোট ভিউ", target: 128400, suffix: "", bar: 0.92 },
  { label: "ওয়াচ আওয়ার", target: 8640, suffix: " ঘণ্টা", bar: 0.68 },
  { label: "নতুন সাবস্ক্রাইবার", target: 3120, suffix: "", bar: 0.47 },
];

const COUNT_FRAMES = 50;

/**
 * DashboardScene — Data Dashboard pipeline.
 * Numbers counter-roll from zero while their bars grow underneath.
 */
export const DashboardScene: React.FC = () => {
  const frame = useCurrentFrame();
  const heading = cuesForScene("dashboard")[0]?.text ?? "";

  return (
    <SceneShell kicker="Data Dashboard • সংখ্যায় প্রমাণ">
      <WordByWord
        text={heading}
        accentWords={["সংখ্যা"]}
        style={{ fontSize: 64, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          marginTop: 56,
          display: "flex",
          flexDirection: "column",
          gap: 44,
          flex: 1,
          justifyContent: "center",
        }}
      >
        {METRICS.map((metric, i) => {
          const progress = interpolate(
            frame - 15 - i * 10,
            [0, COUNT_FRAMES],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            },
          );
          const value = Math.round(metric.target * progress);
          return (
            <div key={metric.label}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "baseline",
                }}
              >
                <span style={{ fontSize: 36, color: theme.muted }}>
                  {metric.label}
                </span>
                <span
                  style={{
                    fontSize: 72,
                    fontWeight: 700,
                    color: theme.fg,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {value.toLocaleString("en-IN")}
                  <span style={{ fontSize: 34, color: theme.accent }}>
                    {metric.suffix}
                  </span>
                </span>
              </div>
              <div
                style={{
                  marginTop: 14,
                  height: 18,
                  borderRadius: 9,
                  backgroundColor: "rgba(255,255,255,0.08)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${progress * metric.bar * 100}%`,
                    backgroundColor: theme.accent,
                    borderRadius: 9,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
