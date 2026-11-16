import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneMetaContext, SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { sceneAccent, theme } from "../theme";

/**
 * GlassShowcaseScene — Glass Showcase pipeline (Stage family).
 * Inspired by premium SaaS promo videos: an animated mesh-gradient
 * (three colour blobs drifting slowly) behind a 2x2 grid of frosted
 * glass tiles. Each tile carries one chunk of the cue's own text with
 * a gradient shape chip; tiles spring in staggered, then float gently
 * on sine waves — smooth motion, glass effect, many colours.
 */
export const GlassShowcaseScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 4);
  const meta = React.useContext(SceneMetaContext);
  const sceneIndex = meta ? meta.position : 0;

  // Mesh-gradient blobs: theme colours drifting on slow sine paths.
  const blobs = [
    { color: theme.accent, size: 760, x: 6, y: 4, speed: 0.011, phase: 0.0, op: 0.5 },
    { color: sceneAccent(sceneIndex + 1), size: 680, x: 58, y: 0, speed: 0.009, phase: 2.1, op: 0.45 },
    { color: sceneAccent(sceneIndex + 2), size: 720, x: 30, y: 46, speed: 0.013, phase: 4.2, op: 0.4 },
  ];
  const chipGradients = [
    `linear-gradient(135deg, ${theme.accent}, ${sceneAccent(sceneIndex + 1)})`,
    `linear-gradient(135deg, ${sceneAccent(sceneIndex + 1)}, ${sceneAccent(sceneIndex + 2)})`,
    `linear-gradient(135deg, ${sceneAccent(sceneIndex + 2)}, ${theme.accent})`,
    `linear-gradient(135deg, ${theme.fg}, ${theme.accent})`,
  ];

  return (
    <SceneShell kicker="Glass Showcase">
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          pointerEvents: "none",
        }}
      >
        {blobs.map((b, i) => {
          const dx = Math.sin(frame * b.speed + b.phase) * 60 * s;
          const dy = Math.cos(frame * b.speed * 0.8 + b.phase) * 44 * s;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                width: b.size * s,
                height: b.size * s,
                borderRadius: "50%",
                backgroundColor: b.color,
                opacity: b.op,
                filter: "blur(110px)",
                left: `${b.x}%`,
                top: `${b.y}%`,
                transform: `translate(${dx}px, ${dy}px)`,
              }}
            />
          );
        })}
      </div>

      <div style={{ position: "relative" }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 54 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>

      <div
        style={{
          position: "relative",
          marginTop: 44 * s,
          display: "flex",
          flexWrap: "wrap",
          gap: 26 * s,
          flex: 1,
          alignContent: "stretch",
        }}
      >
        {chunks.map((chunk, i) => {
          const entrance = spring({
            frame: frame - 14 - i * 9,
            fps,
            config: { damping: 18, stiffness: 110, mass: 0.9 },
          });
          const floatY = Math.sin(frame * 0.045 + i * 1.7) * 7 * s;
          return (
            <div
              key={`${chunk}-${i}`}
              style={{
                flexBasis: "46%",
                flexGrow: 1,
                background:
                  "linear-gradient(135deg, rgba(255,255,255,0.16), rgba(255,255,255,0.05))",
                backdropFilter: "blur(20px)",
                WebkitBackdropFilter: "blur(20px)",
                border: "1px solid rgba(255,255,255,0.35)",
                borderRadius: 28 * s,
                boxShadow: "0 24px 60px rgba(0,0,0,0.35)",
                padding: 30 * s,
                display: "flex",
                alignItems: "center",
                gap: 22 * s,
                opacity: entrance,
                transform: `translateY(${(1 - entrance) * 46 * s + floatY}px) scale(${0.95 + entrance * 0.05})`,
              }}
            >
              <div
                style={{
                  width: 58 * s,
                  height: 58 * s,
                  flex: "none",
                  borderRadius: 16 * s,
                  background: chipGradients[i % chipGradients.length],
                  boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
                }}
              />
              <div style={{ fontSize: 35 * s, fontWeight: 600, lineHeight: 1.4 }}>
                {chunk}
              </div>
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
