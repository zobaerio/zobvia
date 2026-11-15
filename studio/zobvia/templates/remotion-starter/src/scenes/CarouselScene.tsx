import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * CarouselScene — 3D Carousel pipeline (Stage family), data-driven.
 * The cue's chunks (up to 5) become cards on a 3D arc: the centre card
 * is the hero, neighbours angle away, smaller and dimmer. The hero
 * position cycles deterministically with the frame, advancing every
 * ~45 frames. The heading above is the cue text word-by-word.
 */
export const CarouselScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 5);
  const heroIndex =
    chunks.length > 0
      ? Math.floor(frame / 45) % chunks.length
      : 0;

  return (
    <SceneShell kicker="3D Carousel">
      <div style={{ textAlign: "center" }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 58 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>
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
            width: "100%",
            height: 420 * s,
            transformStyle: "preserve-3d",
          }}
        >
          {chunks.map((chunk, i) => {
            // Offset from the hero, wrapped so the arc stays centred.
            let offset = i - heroIndex;
            if (chunks.length > 2) {
              if (offset > chunks.length / 2) offset -= chunks.length;
              if (offset < -chunks.length / 2) offset += chunks.length;
            }
            const abs = Math.abs(offset);
            // Neighbours: left side turns +angle, right side -angle.
            const rotation =
              offset === 0 ? 0 : offset < 0 ? (abs === 1 ? 28 : 48) : -(abs === 1 ? 28 : 48);
            const scale = abs === 0 ? 1 : abs === 1 ? 0.82 : 0.64;
            const opacity = abs === 0 ? 1 : abs === 1 ? 0.72 : 0.42;
            const translateX = offset * 340 * s;
            return (
              <div
                key={`${chunk}-${i}`}
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  width: 520 * s,
                  minHeight: 300 * s,
                  marginLeft: -260 * s,
                  marginTop: -150 * s,
                  backgroundColor:
                    abs === 0 ? theme.accentSoft : "rgba(255,255,255,0.05)",
                  border: `1px solid ${abs === 0 ? theme.accent : "rgba(255,255,255,0.14)"}`,
                  borderRadius: theme.radius,
                  padding: 36 * s,
                  boxSizing: "border-box",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  fontSize: 36 * s,
                  lineHeight: 1.45,
                  color: theme.fg,
                  opacity,
                  zIndex: 10 - abs,
                  transform: `translateX(${translateX}px) rotateY(${rotation}deg) scale(${scale})`,
                }}
              >
                {chunk}
              </div>
            );
          })}
        </div>
      </div>
    </SceneShell>
  );
};
