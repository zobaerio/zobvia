import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { truncateWords } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * NewsScene — News genre scene (news), data-driven.
 * Accent banner with the cue's first words, the full cue large in
 * the middle, and a lower-third bar repeating the cue verbatim.
 */
export const NewsScene: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;

  return (
    <SceneShell kicker="News">
      <div
        style={{
          backgroundColor: theme.accent,
          color: theme.bg,
          fontWeight: 700,
          fontSize: 34 * s,
          lineHeight: 1.3,
          padding: `${18 * s}px ${28 * s}px`,
          borderRadius: 8,
          letterSpacing: 0,
        }}
      >
        {truncateWords(scene.text, 6)}
      </div>
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: `0 ${40 * s}px`,
        }}
      >
        <WordByWord
          text={scene.text}
          style={{ fontSize: 72 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>
      <div style={{ display: "flex", alignItems: "stretch" }}>
        <div style={{ width: 18 * s, backgroundColor: theme.accent }} />
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(0,0,0,0.55)",
            padding: `${22 * s}px ${28 * s}px`,
          }}
        >
          <span
            style={{ fontSize: 32 * s, lineHeight: 1.4, letterSpacing: 0 }}
          >
            {scene.text}
          </span>
        </div>
      </div>
    </SceneShell>
  );
};
