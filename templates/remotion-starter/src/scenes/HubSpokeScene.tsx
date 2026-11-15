import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks, truncateWords } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * HubSpokeScene — Hub-and-Spoke pipeline (Flow family), data-driven.
 * The centre node carries the cue's first chunk (truncated to ~4
 * words); 3–5 satellite pills carry the remaining chunks. SVG lines
 * from the centre to each satellite draw on in sequence (pathLength
 * trick), and each satellite pops in as its line completes. All text
 * comes from the cue — satellites are its own chunks, never invented.
 */
export const HubSpokeScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 6);
  const centre = truncateWords(chunks[0] ?? scene.text, 4);
  let satellites = chunks.slice(1, 6);
  // A single-chunk cue: split its words so spokes still come from the cue.
  if (satellites.length === 0) {
    const words = scene.text.split(/\s+/).filter(Boolean);
    satellites = words.slice(4, 9).map((w) => w);
    if (satellites.length === 0) satellites = [truncateWords(scene.text, 4)];
  }
  satellites = satellites.slice(0, 5);

  // Geometry in a 1000x620 viewBox, centred on the hub.
  const cx = 500;
  const cy = 310;
  const positions = satellites.map((_, i) => {
    const angle = (i / satellites.length) * Math.PI * 2 - Math.PI / 2;
    return {
      x: cx + Math.cos(angle) * 360,
      y: cy + Math.sin(angle) * 210,
    };
  });
  void height;

  return (
    <SceneShell kicker="Hub & Spoke">
      <div style={{ textAlign: "center" }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 40 * s, fontWeight: 600, lineHeight: 1.3 }}
        />
      </div>
      <div style={{ flex: 1, position: "relative" }}>
        <svg
          viewBox="0 0 1000 620"
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
          }}
        >
          {positions.map((pos, i) => {
            const draw = interpolate(frame - 16 - i * 14, [0, 14], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <line
                key={i}
                x1={cx}
                y1={cy}
                x2={pos.x}
                y2={pos.y}
                stroke={theme.accent}
                strokeWidth={3}
                strokeOpacity={0.65}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - draw}
              />
            );
          })}
        </svg>
        {/* Centre node */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            width: 320 * s,
            minHeight: 160 * s,
            borderRadius: theme.radius,
            backgroundColor: theme.accent,
            color: theme.bg,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: 28 * s,
            boxSizing: "border-box",
            fontSize: 38 * s,
            fontWeight: 700,
            lineHeight: 1.35,
            zIndex: 2,
          }}
        >
          {centre}
        </div>
        {/* Satellites */}
        {satellites.map((sat, i) => {
          const pos = positions[i];
          const pop = spring({
            frame: frame - 28 - i * 14,
            fps,
            config: { damping: 14, stiffness: 180, mass: 0.6 },
          });
          return (
            <div
              key={`${sat}-${i}`}
              style={{
                position: "absolute",
                left: `${(pos.x / 1000) * 100}%`,
                top: `${(pos.y / 620) * 100}%`,
                transform: `translate(-50%, -50%) scale(${0.6 + pop * 0.4})`,
                opacity: pop,
                maxWidth: 340 * s,
                backgroundColor: "rgba(255,255,255,0.07)",
                border: `1px solid ${theme.accent}55`,
                borderRadius: 999,
                padding: `${18 * s}px ${28 * s}px`,
                fontSize: 30 * s,
                lineHeight: 1.4,
                textAlign: "center",
                zIndex: 2,
              }}
            >
              {sat}
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
