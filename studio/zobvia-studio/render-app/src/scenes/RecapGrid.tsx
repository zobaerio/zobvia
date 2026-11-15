import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { truncateWords } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * RecapGrid — Checklist / Recap Grid pipeline, data-driven.
 * Tiles tick off the scenes that came before this one — their own SRT
 * text, truncated on word boundaries — under this cue's heading.
 */
export const RecapGrid: React.FC<SceneProps> = ({ scene, allScenes }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const previous = allScenes
    .filter((other) => other.index < scene.index)
    .slice(-6);

  return (
    <SceneShell kicker="Recap">
      <WordByWord
        text={scene.text}
        style={{ fontSize: 60 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          marginTop: 48 * s,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: theme.gap,
          flex: 1,
          alignContent: "start",
        }}
      >
        {previous.map((prev, i) => {
          const pop = spring({
            frame: frame - 16 - i * 9,
            fps,
            config: { damping: 15, stiffness: 160, mass: 0.7 },
          });
          return (
            <div
              key={prev.index}
              style={{
                display: "flex",
                gap: 22 * s,
                alignItems: "flex-start",
                backgroundColor: "rgba(255,255,255,0.05)",
                border: `1px solid ${theme.accent}26`,
                borderRadius: theme.radius,
                padding: 30 * s,
                opacity: pop,
                transform: `translateY(${(1 - pop) * 32}px)`,
              }}
            >
              <div
                style={{
                  flexShrink: 0,
                  width: 44 * s,
                  height: 44 * s,
                  borderRadius: "50%",
                  backgroundColor: theme.accent,
                  color: theme.bg,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 26 * s,
                  fontWeight: 700,
                  transform: `scale(${pop})`,
                }}
              >
                ✓
              </div>
              <div style={{ fontSize: 32 * s, lineHeight: 1.45 }}>
                {truncateWords(prev.text, 8)}
              </div>
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
