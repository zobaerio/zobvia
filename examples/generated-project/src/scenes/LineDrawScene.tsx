import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * LineDrawScene — Line-Draw / Doodle pipeline (Free family),
 * data-driven. A paper ground (light override on the shell) with a
 * dashed-border "sketch box" holding the cue word-by-word, an SVG
 * squiggle underline that draws on via the pathLength trick, and the
 * cue's chunks as sketch rows whose dashed checkbox squares tick (✓)
 * in sequence. All text comes from the cue.
 */
export const LineDrawScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 4);
  const squiggle = interpolate(frame, [14, 44], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell
      kicker="Line-Draw • Doodle"
      style={{ backgroundColor: "#F8F5EE", color: theme.bg }}
    >
      <div
        style={{
          border: `3px dashed ${theme.bg}`,
          borderRadius: theme.radius,
          padding: `${44 * s}px ${48 * s}px`,
          backgroundColor: "rgba(255,255,255,0.35)",
        }}
      >
        <div style={{ color: theme.bg }}>
          <WordByWord
            text={scene.text}
            style={{
              fontSize: 56 * s,
              fontWeight: 700,
              lineHeight: 1.35,
              color: theme.bg,
            }}
          />
        </div>
        <svg
          viewBox="0 0 600 24"
          style={{ width: "62%", height: 24 * s, marginTop: 18 * s }}
        >
          <path
            d="M4 14 Q 40 4, 80 14 T 156 14 T 232 14 T 308 14 T 384 14 T 460 14 T 536 14 T 596 14"
            fill="none"
            stroke={theme.accent}
            strokeWidth={5}
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - squiggle}
          />
        </svg>
      </div>
      {chunks.length >= 2 ? (
        <div
          style={{
            marginTop: 44 * s,
            display: "flex",
            flexDirection: "column",
            gap: 24 * s,
          }}
        >
          {chunks.map((chunk, i) => {
            const ticked = frame >= 30 + i * 14;
            const rowIn = interpolate(frame - 22 - i * 14, [0, 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={`${chunk}-${i}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 22 * s,
                  opacity: rowIn,
                  fontSize: 36 * s,
                  lineHeight: 1.45,
                  color: theme.bg,
                }}
              >
                <div
                  style={{
                    flexShrink: 0,
                    width: 46 * s,
                    height: 46 * s,
                    border: `3px dashed ${theme.bg}`,
                    borderRadius: 10,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 30 * s,
                    fontWeight: 700,
                    color: theme.accent,
                    backgroundColor: ticked
                      ? "rgba(255,255,255,0.55)"
                      : "transparent",
                  }}
                >
                  {ticked ? "✓" : ""}
                </div>
                <div>{chunk}</div>
              </div>
            );
          })}
        </div>
      ) : null}
    </SceneShell>
  );
};
