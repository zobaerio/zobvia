import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * KineticHook — Kinetic Typography pipeline, data-driven.
 * The scene's whole text, huge, revealed word by word; an accent bar
 * grows underneath. Nothing else competes with the words.
 */
export const KineticHook: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const barWidth = interpolate(frame, [8, 26], [0, 180 * s], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell kicker="Hook • Kinetic Typography">
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <WordByWord
          text={scene.text}
          style={{ fontSize: 108 * s, fontWeight: 700, lineHeight: 1.25 }}
        />
        <div
          style={{
            marginTop: 44 * s,
            width: barWidth,
            height: 8,
            borderRadius: 4,
            backgroundColor: theme.accent,
          }}
        />
      </div>
    </SceneShell>
  );
};
