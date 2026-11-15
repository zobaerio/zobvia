import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * BentoScene — Bento Grid pipeline, data-driven.
 * The heading is the scene text word-by-word; below it, tiles spring in
 * one by one carrying the text's own chunks (sentences / phrases) —
 * content always comes from the SRT cue, never invented.
 */
export const BentoScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 4);

  return (
    <SceneShell kicker="Bento Grid">
      <WordByWord
        text={scene.text}
        style={{ fontSize: 60 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      {chunks.length >= 2 ? (
        <div
          style={{
            marginTop: 48 * s,
            display: "grid",
            gridTemplateColumns: chunks.length > 2 ? "1fr 1fr" : "1fr",
            gap: theme.gap,
            flex: 1,
          }}
        >
          {chunks.map((chunk, i) => {
            const entrance = spring({
              frame: frame - 20 - i * 8,
              fps,
              config: { damping: 16, stiffness: 140, mass: 0.8 },
            });
            return (
              <div
                key={`${chunk}-${i}`}
                style={{
                  backgroundColor: theme.accentSoft,
                  border: `1px solid ${theme.accent}33`,
                  borderRadius: theme.radius,
                  padding: 40 * s,
                  opacity: entrance,
                  transform: `translateY(${(1 - entrance) * 48}px) scale(${0.97 + entrance * 0.03})`,
                  display: "flex",
                  alignItems: "center",
                  fontSize: 38 * s,
                  lineHeight: 1.45,
                  color: theme.fg,
                }}
              >
                {chunk}
              </div>
            );
          })}
        </div>
      ) : null}
    </SceneShell>
  );
};
