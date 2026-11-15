import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * FlatVectorScene — Flat Vector / Isometric pipeline (Free family),
 * data-driven. A flat-shape composition built only from geometric
 * primitives: an accent sun circle, layered hill/ground shapes in
 * accentSoft and muted tones, and simple blocks that slide/pop in
 * staggered. The cue's chunks ride above the shapes as label chips;
 * the heading is the cue word-by-word. No other text exists.
 */
export const FlatVectorScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 4);

  const sunIn = spring({
    frame: frame - 6,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.8 },
  });
  const blocks = [
    { w: 220, h: 150, color: theme.accent, delay: 18 },
    { w: 160, h: 230, color: theme.muted, delay: 26 },
    { w: 280, h: 110, color: theme.accentSoft, delay: 34 },
  ];

  return (
    <SceneShell kicker="Flat Vector">
      <WordByWord
        text={scene.text}
        style={{ fontSize: 58 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      {chunks.length >= 2 ? (
        <div
          style={{
            marginTop: 32 * s,
            display: "flex",
            gap: 16 * s,
            flexWrap: "wrap",
          }}
        >
          {chunks.map((chunk, i) => {
            const chipIn = spring({
              frame: frame - 12 - i * 8,
              fps,
              config: { damping: 15, stiffness: 160, mass: 0.7 },
            });
            return (
              <div
                key={`${chunk}-${i}`}
                style={{
                  backgroundColor: "rgba(255,255,255,0.08)",
                  border: `1px solid ${theme.accent}44`,
                  borderRadius: 999,
                  padding: `${14 * s}px ${26 * s}px`,
                  fontSize: 30 * s,
                  lineHeight: 1.4,
                  opacity: chipIn,
                  transform: `translateY(${(1 - chipIn) * 20}px)`,
                }}
              >
                {chunk}
              </div>
            );
          })}
        </div>
      ) : null}
      {/* Flat landscape: sun, hills, ground, blocks — primitives only. */}
      <div
        style={{
          flex: 1,
          position: "relative",
          marginTop: 36 * s,
          borderRadius: theme.radius,
          overflow: "hidden",
          backgroundColor: "rgba(255,255,255,0.03)",
        }}
      >
        <div
          style={{
            position: "absolute",
            right: "12%",
            top: "10%",
            width: 150 * s,
            height: 150 * s,
            borderRadius: "50%",
            backgroundColor: theme.accent,
            opacity: sunIn,
            transform: `scale(${0.5 + sunIn * 0.5})`,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: "-8%",
            bottom: "18%",
            width: "70%",
            height: "52%",
            borderRadius: "50%",
            backgroundColor: theme.accentSoft,
          }}
        />
        <div
          style={{
            position: "absolute",
            right: "-10%",
            bottom: "14%",
            width: "72%",
            height: "58%",
            borderRadius: "50%",
            backgroundColor: "rgba(154,167,180,0.18)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            height: "20%",
            backgroundColor: "rgba(154,167,180,0.28)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: "10%",
            bottom: "20%",
            display: "flex",
            alignItems: "flex-end",
            gap: 28 * s,
          }}
        >
          {blocks.map((block, i) => {
            const blockIn = spring({
              frame: frame - block.delay,
              fps,
              config: { damping: 15, stiffness: 150, mass: 0.7 },
            });
            return (
              <div
                key={i}
                style={{
                  width: block.w * s,
                  height: block.h * s * blockIn,
                  backgroundColor: block.color,
                  borderRadius: `${12 * s}px ${12 * s}px 0 0`,
                  opacity: blockIn,
                }}
              />
            );
          })}
        </div>
      </div>
    </SceneShell>
  );
};
