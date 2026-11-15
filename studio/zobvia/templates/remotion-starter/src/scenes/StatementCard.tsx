import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * StatementCard — Statement Card pipeline, data-driven.
 * One sentence, huge, centred on an accent-tinted ground. Nothing else.
 * Used for the single most important line of the video.
 */
export const StatementCard: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;

  return (
    <SceneShell
      kicker="Statement"
      style={{ backgroundColor: theme.accentSoft }}
    >
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: `0 ${60 * s}px`,
        }}
      >
        <WordByWord
          text={scene.text}
          style={{ fontSize: 96 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
      </div>
    </SceneShell>
  );
};
