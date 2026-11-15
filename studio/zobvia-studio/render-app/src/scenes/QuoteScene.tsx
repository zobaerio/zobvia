import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { FadeUp } from "../components/anim";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * QuoteScene — Quote genre scene (quote), data-driven.
 * A giant quotation mark watches over the cue, centred and faded
 * up, with a small accent rule underneath. Text is the cue only.
 */
export const QuoteScene: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;

  return (
    <SceneShell kicker="Quote">
      <div style={{ position: "relative", flex: 1, display: "flex", flexDirection: "column" }}>
        <div
          aria-hidden
          style={{
            fontSize: 260 * s,
            lineHeight: 0.7,
            color: theme.accent,
            opacity: 0.9,
            fontWeight: 700,
            letterSpacing: 0,
          }}
        >
          &ldquo;
        </div>
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: `0 ${70 * s}px`,
          }}
        >
          <FadeUp delay={4}>
            <WordByWord
              text={scene.text}
              style={{ fontSize: 76 * s, fontWeight: 700, lineHeight: 1.35 }}
            />
          </FadeUp>
          <div
            style={{
              marginTop: 44 * s,
              width: 120 * s,
              height: 6,
              borderRadius: 3,
              backgroundColor: theme.accent,
            }}
          />
        </div>
      </div>
    </SceneShell>
  );
};
