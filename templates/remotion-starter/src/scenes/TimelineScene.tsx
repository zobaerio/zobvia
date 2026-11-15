import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * TimelineScene — Timeline / Process Flow pipeline, data-driven.
 * A spine with nodes that light up in sequence; each node carries one
 * chunk of the cue's own text (a step, a phrase). The full cue also
 * appears word-by-word above the spine.
 */
export const TimelineScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const steps = splitChunks(scene.text, 4);
  const lineProgress = interpolate(
    frame,
    [10, 10 + steps.length * 14],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <SceneShell kicker="Timeline • Process Flow">
      <WordByWord
        text={scene.text}
        style={{ fontSize: 60 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: `0 ${20 * s}px`,
        }}
      >
        <div style={{ position: "relative", height: 6, margin: `0 ${30 * s}px` }}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundColor: "rgba(255,255,255,0.12)",
              borderRadius: 3,
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: 0,
              width: `${lineProgress * 100}%`,
              backgroundColor: theme.accent,
              borderRadius: 3,
            }}
          />
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: -21,
          }}
        >
          {steps.map((step, i) => {
            const pop = spring({
              frame: frame - 10 - i * 14,
              fps,
              config: { damping: 14, stiffness: 180, mass: 0.6 },
            });
            const active = frame >= 10 + i * 14;
            return (
              <div
                key={`${step}-${i}`}
                style={{
                  width: `${100 / steps.length}%`,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  textAlign: "center",
                  padding: `0 ${12 * s}px`,
                  boxSizing: "border-box",
                }}
              >
                <div
                  style={{
                    width: 48 * s,
                    height: 48 * s,
                    borderRadius: "50%",
                    backgroundColor: active ? theme.accent : theme.bg,
                    border: `3px solid ${theme.accent}`,
                    color: active ? theme.bg : theme.accent,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 26 * s,
                    fontWeight: 700,
                    transform: `scale(${0.6 + pop * 0.4})`,
                    zIndex: 1,
                  }}
                >
                  {i + 1}
                </div>
                <div
                  style={{
                    marginTop: 26 * s,
                    fontSize: 30 * s,
                    lineHeight: 1.4,
                    color: active ? theme.fg : theme.muted,
                    opacity: 0.35 + pop * 0.65,
                  }}
                >
                  {step}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </SceneShell>
  );
};
