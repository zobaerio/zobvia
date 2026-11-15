import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * PodcastScene — Podcast genre scene (podcast), data-driven.
 * Two speaker discs; the active speaker (scene.index % 2) pulses in
 * the accent colour. Between them a frame-driven waveform dances —
 * decoration only, heights come from the frame, never from data.
 */
export const PodcastScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const activeIndex = scene.index % 2;
  const pulse = 1 + 0.02 * (1 + Math.sin(frame * 0.12));

  const renderDisc = (discIndex: number) => {
    const active = discIndex === activeIndex;
    return (
      <div
        style={{
          width: 300 * s,
          height: 300 * s,
          borderRadius: "50%",
          border: `5px solid ${theme.accent}`,
          backgroundColor: active ? theme.accent : "rgba(255,255,255,0.05)",
          opacity: active ? 1 : 0.55,
          transform: active ? `scale(${pulse})` : "scale(1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: 110 * s,
            height: 110 * s,
            borderRadius: "50%",
            backgroundColor: active ? theme.bg : theme.muted,
            opacity: active ? 0.9 : 0.5,
          }}
        />
      </div>
    );
  };

  return (
    <SceneShell kicker="Podcast">
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 40 * s,
        }}
      >
        {renderDisc(0)}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 7 * s,
            height: 120 * s,
          }}
        >
          {Array.from({ length: 24 }, (_, i) => {
            const h = 20 + 60 * Math.abs(Math.sin(frame * 0.35 + i * 0.7));
            return (
              <div
                key={i}
                style={{
                  width: 10 * s,
                  height: h * s,
                  borderRadius: 5 * s,
                  backgroundColor: theme.accent,
                  opacity: 0.85,
                }}
              />
            );
          })}
        </div>
        {renderDisc(1)}
      </div>
      <div style={{ textAlign: "center", marginTop: 24 * s }}>
        <WordByWord
          text={scene.text}
          style={{ fontSize: 52 * s, fontWeight: 700, lineHeight: 1.35 }}
        />
      </div>
    </SceneShell>
  );
};
