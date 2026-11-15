import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * GradientFluidScene — Gradient Fluid pipeline (Stage family),
 * data-driven. A full-bleed colour field: 2–3 huge blurred circles in
 * the accent and foreground colours drift slowly on sin/cos paths
 * driven by the frame. Bold centred text on top is the cue itself,
 * word-by-word — the colour field is decoration only.
 */
export const GradientFluidScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;

  const blobs = [
    {
      size: 900,
      color: theme.accent,
      opacity: 0.34,
      baseX: 12,
      baseY: 6,
      ampX: 90,
      ampY: 60,
      speed: 0.011,
      phase: 0,
    },
    {
      size: 760,
      color: theme.fg,
      opacity: 0.18,
      baseX: 52,
      baseY: 34,
      ampX: 110,
      ampY: 70,
      speed: 0.009,
      phase: 2.1,
    },
    {
      size: 640,
      color: theme.accent,
      opacity: 0.22,
      baseX: 30,
      baseY: 48,
      ampX: 70,
      ampY: 90,
      speed: 0.013,
      phase: 4.2,
    },
  ];

  return (
    <SceneShell kicker="Gradient Fluid">
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          pointerEvents: "none",
        }}
      >
        {blobs.map((blob, i) => {
          const dx = Math.sin(frame * blob.speed + blob.phase) * blob.ampX * s;
          const dy = Math.cos(frame * blob.speed * 0.9 + blob.phase) * blob.ampY * s;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `${blob.baseX}%`,
                top: `${blob.baseY}%`,
                width: blob.size * s,
                height: blob.size * s,
                borderRadius: "50%",
                backgroundColor: blob.color,
                opacity: blob.opacity,
                filter: "blur(110px)",
                transform: `translate(${dx}px, ${dy}px)`,
              }}
            />
          );
        })}
      </div>
      <div
        style={{
          position: "relative",
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: `0 ${100 * s}px`,
        }}
      >
        <WordByWord
          text={scene.text}
          style={{ fontSize: 84 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>
    </SceneShell>
  );
};
