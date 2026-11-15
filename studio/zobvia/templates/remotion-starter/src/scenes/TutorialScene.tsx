import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { SpringPop } from "../components/anim";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * TutorialScene — Tutorial genre scene (tutorial), data-driven.
 * The step circle shows the real scene number (scene.index from
 * props); the progress bar tracks position across allScenes.
 */
export const TutorialScene: React.FC<SceneProps> = ({ scene, allScenes }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;
  const progress =
    (scene.index / Math.max(allScenes.length - 1, 1)) * 100;

  return (
    <SceneShell kicker="Tutorial">
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          gap: 64 * s,
        }}
      >
        <SpringPop delay={2}>
          <div
            style={{
              width: 220 * s,
              height: 220 * s,
              borderRadius: "50%",
              backgroundColor: theme.accent,
              color: theme.bg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 96 * s,
              fontWeight: 700,
              lineHeight: 1,
              flexShrink: 0,
              letterSpacing: 0,
            }}
          >
            {scene.index}
          </div>
        </SpringPop>
        <div style={{ flex: 1 }}>
          <WordByWord
            text={scene.text}
            style={{ fontSize: 64 * s, fontWeight: 700, lineHeight: 1.35 }}
          />
        </div>
      </div>
      <div
        style={{
          height: 16,
          borderRadius: 8,
          backgroundColor: "rgba(255,255,255,0.08)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress}%`,
            backgroundColor: theme.accent,
            borderRadius: 8,
          }}
        />
      </div>
    </SceneShell>
  );
};
