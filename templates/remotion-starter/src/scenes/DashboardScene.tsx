import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { graphemeLength } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

interface Metric {
  raw: string;
  value: number;
  suffix: string;
  decimals: number;
}

const BN_DIGITS = "০১২৩৪৫৬৭৮৯";

/** Bengali digits (০-৯) -> ASCII, for parsing. */
const toAsciiDigits = (value: string): string =>
  value.replace(/[০-৯]/g, (d) => String(BN_DIGITS.indexOf(d)));

/** ASCII digits -> Bengali digits, for display in a Bengali cue. */
const toBnDigits = (value: string): string =>
  value.replace(/[0-9]/g, (d) => BN_DIGITS[Number(d)]);

/** Numbers written in the cue text itself — the only numbers ever shown. */
const extractMetrics = (text: string): Metric[] => {
  const matches =
    text.match(
      /[0-9০-৯]{1,3}(?:,[0-9০-৯]{3})+(?:\.[0-9০-৯]+)?|[0-9০-৯]+(?:\.[0-9০-৯]+)?%?/g,
    ) ?? [];
  return matches.slice(0, 3).map((raw) => {
    const suffix = raw.endsWith("%") ? "%" : "";
    const numeric = toAsciiDigits(raw.replace(/%$/, "").replace(/,/g, ""));
    return {
      raw,
      value: parseFloat(numeric),
      suffix,
      decimals: numeric.includes(".") ? numeric.split(".")[1].length : 0,
    };
  });
};

const COUNT_FRAMES = 50;

/**
 * DashboardScene — Data Dashboard pipeline, data-driven.
 * Numbers that appear in the cue count up with growing bars. A cue with
 * no numbers shows its words as labelled bars instead — decorative
 * rhythm from the text's own words, never invented statistics.
 */
export const DashboardScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const metrics = extractMetrics(scene.text);
  const maxValue = Math.max(...metrics.map((m) => m.value), 1);
  const words = scene.text.split(/\s+/).filter(Boolean).slice(0, 5);

  return (
    <SceneShell kicker="Data Dashboard">
      <WordByWord
        text={scene.text}
        style={{ fontSize: 60 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          marginTop: 56 * s,
          display: "flex",
          flexDirection: "column",
          gap: 44 * s,
          flex: 1,
          justifyContent: "center",
        }}
      >
        {metrics.length > 0
          ? metrics.map((metric, i) => {
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
              const shown = (metric.value * progress).toFixed(metric.decimals);
              const formatted = parseFloat(shown).toLocaleString("en-IN", {
                minimumFractionDigits: metric.decimals,
                maximumFractionDigits: metric.decimals,
              });
              // Keep the cue's own digit script (Bengali cues count in ০-৯).
              const shownNumber = /[০-৯]/.test(metric.raw)
                ? toBnDigits(formatted)
                : formatted;
              return (
                <div key={`${metric.raw}-${i}`}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "flex-end",
                      alignItems: "baseline",
                    }}
                  >
                    <span
                      style={{
                        fontSize: 76 * s,
                        fontWeight: 700,
                        color: theme.fg,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {shownNumber}
                      <span style={{ fontSize: 36 * s, color: theme.accent }}>
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
                        width: `${progress * (metric.value / maxValue) * 100}%`,
                        backgroundColor: theme.accent,
                        borderRadius: 9,
                      }}
                    />
                  </div>
                </div>
              );
            })
          : words.map((word, i) => {
              const target = 0.3 + (graphemeLength(word) % 7) / 10;
              const progress = interpolate(
                frame - 15 - i * 8,
                [0, COUNT_FRAMES],
                [0, 1],
                {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: Easing.out(Easing.cubic),
                },
              );
              return (
                <div key={`${word}-${i}`}>
                  <div style={{ fontSize: 34 * s, color: theme.muted }}>
                    {word}
                  </div>
                  <div
                    style={{
                      marginTop: 10,
                      height: 14,
                      borderRadius: 7,
                      backgroundColor: "rgba(255,255,255,0.08)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${progress * target * 100}%`,
                        backgroundColor: theme.accent,
                        borderRadius: 7,
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
