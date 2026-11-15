import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * CubeScene — Cube 3D pipeline (cube-3d), data-driven.
 * CSS 3D only (perspective / preserve-3d / translateZ) — no
 * three.js / WebGL. A rotating cube carries the cue's own chunks
 * cycled across its six faces; the full cue runs underneath.
 */
export const CubeScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const size = 400 * s;
  const half = size / 2;
  const chunks = splitChunks(scene.text, 4);
  const safeChunks = chunks.length > 0 ? chunks : [scene.text];

  const faceTransforms = [
    `rotateY(0deg) translateZ(${half}px)`,
    `rotateY(90deg) translateZ(${half}px)`,
    `rotateY(180deg) translateZ(${half}px)`,
    `rotateY(270deg) translateZ(${half}px)`,
    `rotateX(90deg) translateZ(${half}px)`,
    `rotateX(-90deg) translateZ(${half}px)`,
  ];

  return (
    <SceneShell kicker="3D • Cube">
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
            width: size,
            height: size,
            transformStyle: "preserve-3d",
            transform: `rotateX(-14deg) rotateY(${frame * 1.1}deg)`,
          }}
        >
          {faceTransforms.map((transform, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                width: size,
                height: size,
                boxSizing: "border-box",
                backgroundColor: theme.accentSoft,
                border: `2px solid ${theme.accent}`,
                borderRadius: 12,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                padding: 28 * s,
                fontSize: 34 * s,
                fontWeight: 600,
                lineHeight: 1.4,
                color: theme.fg,
                backfaceVisibility: "visible",
                transform,
                letterSpacing: 0,
              }}
            >
              {safeChunks[i % safeChunks.length]}
            </div>
          ))}
        </div>
      </div>
      <div style={{ textAlign: "center", marginTop: 24 * s }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 36 * s, fontWeight: 600, lineHeight: 1.35 }}
        />
      </div>
    </SceneShell>
  );
};
