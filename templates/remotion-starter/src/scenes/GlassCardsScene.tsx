import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * GlassCardsScene — Glass Cards pipeline (Stage family), data-driven.
 * Two blurred colour blobs glow behind 1–3 frosted-glass cards that
 * float in with springs at slight offsets. Each card carries one chunk
 * of the cue's own text; the heading is the cue word-by-word.
 */
export const GlassCardsScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 3);
  const offsets = [-14, 10, -6];

  return (
    <SceneShell kicker="Glass Cards">
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: 620 * s,
            height: 620 * s,
            borderRadius: "50%",
            backgroundColor: theme.accent,
            opacity: 0.28,
            filter: "blur(120px)",
            left: "8%",
            top: "12%",
          }}
        />
        <div
          style={{
            position: "absolute",
            width: 540 * s,
            height: 540 * s,
            borderRadius: "50%",
            backgroundColor: theme.fg,
            opacity: 0.16,
            filter: "blur(130px)",
            right: "6%",
            bottom: "8%",
          }}
        />
      </div>
      <div style={{ position: "relative" }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 58 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>
      <div
        style={{
          position: "relative",
          marginTop: 48 * s,
          display: "flex",
          gap: theme.gap,
          flex: 1,
          alignItems: "stretch",
        }}
      >
        {chunks.map((chunk, i) => {
          const entrance = spring({
            frame: frame - 16 - i * 10,
            fps,
            config: { damping: 15, stiffness: 130, mass: 0.8 },
          });
          return (
            <div
              key={`${chunk}-${i}`}
              style={{
                flex: 1,
                backgroundColor: "rgba(255,255,255,0.08)",
                backdropFilter: "blur(18px)",
                WebkitBackdropFilter: "blur(18px)",
                border: "1px solid rgba(255,255,255,0.22)",
                borderRadius: theme.radius,
                padding: 38 * s,
                display: "flex",
                alignItems: "center",
                fontSize: 36 * s,
                lineHeight: 1.5,
                opacity: entrance,
                transform: `translateY(${(1 - entrance) * 52 + (offsets[i % offsets.length] ?? 0)}px) scale(${0.96 + entrance * 0.04})`,
              }}
            >
              {chunk}
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
