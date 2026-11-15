import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * ParallaxScene — Parallax 3D pipeline (parallax-3d), data-driven.
 * CSS 3D only. Three layers drift at 0.3× / 0.7× / 1.2× rates inside
 * a gently tilting perspective container: blurred accent circles at
 * the back, the cue's chunk chips in the middle, the full cue big
 * at the front. All text comes from the cue.
 */
export const ParallaxScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 3);

  const tiltX = Math.sin(frame / 140) * 3;
  const tiltY = Math.cos(frame / 140) * 3;
  const baseDrift = Math.sin(frame / 110) * 20;
  const backX = baseDrift * 0.3;
  const midX = baseDrift * 0.7;
  const frontX = Math.sin(frame / 90) * 14;

  return (
    <SceneShell kicker="3D • Parallax">
      <div
        style={{
          flex: 1,
          position: "relative",
          perspective: 1200,
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            transformStyle: "preserve-3d",
            transform: `rotateX(${tiltX}deg) rotateY(${tiltY}deg)`,
          }}
        >
          {/* Back layer — blurred accent circles at 0.3x */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              transform: `translateX(${backX}px) translateZ(-120px)`,
            }}
          >
            <div
              style={{
                position: "absolute",
                left: "6%",
                top: "8%",
                width: 520 * s,
                height: 520 * s,
                borderRadius: "50%",
                backgroundColor: theme.accent,
                opacity: 0.16,
                filter: "blur(70px)",
              }}
            />
            <div
              style={{
                position: "absolute",
                right: "8%",
                bottom: "6%",
                width: 420 * s,
                height: 420 * s,
                borderRadius: "50%",
                backgroundColor: theme.accent,
                opacity: 0.12,
                filter: "blur(60px)",
              }}
            />
          </div>

          {/* Mid layer — chunk chips at 0.7x */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "center",
              gap: theme.gap,
              paddingBottom: 40 * s,
              boxSizing: "border-box",
              transform: `translateX(${midX}px) translateZ(40px)`,
            }}
          >
            {chunks.map((chunk, i) => (
              <div
                key={`${chunk}-${i}`}
                style={{
                  backgroundColor: "rgba(255,255,255,0.07)",
                  border: `1px solid ${theme.accent}55`,
                  borderRadius: theme.radius,
                  padding: `${22 * s}px ${30 * s}px`,
                  fontSize: 30 * s,
                  lineHeight: 1.4,
                  textAlign: "center",
                  maxWidth: 480 * s,
                  color: theme.fg,
                  letterSpacing: 0,
                }}
              >
                {chunk}
              </div>
            ))}
          </div>

          {/* Front layer — full cue at 1.2x subtle drift */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              padding: `0 ${80 * s}px`,
              boxSizing: "border-box",
              transform: `translateX(${frontX}px) translateZ(90px)`,
            }}
          >
            <WordByWord
              text={scene.text}
              style={{ fontSize: 72 * s, fontWeight: 700, lineHeight: 1.3 }}
            />
          </div>
        </div>
      </div>
    </SceneShell>
  );
};
