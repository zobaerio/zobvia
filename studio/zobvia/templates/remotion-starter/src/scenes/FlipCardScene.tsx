import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * FlipCardScene — Flip Card 3D pipeline (flip-3d), data-driven.
 * CSS 3D only. A card flips 0→180deg over frames 14–44 and holds:
 * the front carries the first half of the cue's chunks, the back
 * the rest. A single-chunk cue splits by words instead.
 */
export const FlipCardScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 4);

  let frontText: string;
  let backText: string;
  if (chunks.length >= 2) {
    const mid = Math.ceil(chunks.length / 2);
    frontText = chunks.slice(0, mid).join(" ");
    backText = chunks.slice(mid).join(" ");
  } else {
    const words = scene.text.split(/\s+/).filter(Boolean);
    if (words.length >= 2) {
      const mid = Math.ceil(words.length / 2);
      frontText = words.slice(0, mid).join(" ");
      backText = words.slice(mid).join(" ");
    } else {
      frontText = scene.text;
      backText = scene.text;
    }
  }

  const rotateY = interpolate(frame, [14, 44], [0, 180], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const faceStyle: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    boxSizing: "border-box",
    borderRadius: theme.radius,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    padding: 48 * s,
    fontSize: 52 * s,
    fontWeight: 700,
    lineHeight: 1.4,
    color: theme.fg,
    backfaceVisibility: "hidden",
    letterSpacing: 0,
  };

  return (
    <SceneShell kicker="3D • Flip Card">
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          perspective: 1400,
        }}
      >
        <div
          style={{
            position: "relative",
            width: 900 * s,
            height: 480 * s,
            transformStyle: "preserve-3d",
            transform: `rotateY(${rotateY}deg)`,
          }}
        >
          <div
            style={{
              ...faceStyle,
              backgroundColor: theme.accentSoft,
              border: `2px solid ${theme.accent}`,
            }}
          >
            {frontText}
          </div>
          <div
            style={{
              ...faceStyle,
              backgroundColor: "rgba(255,255,255,0.06)",
              border: `2px solid ${theme.accent}88`,
              transform: "rotateY(180deg)",
            }}
          >
            {backText}
          </div>
        </div>
      </div>
    </SceneShell>
  );
};
