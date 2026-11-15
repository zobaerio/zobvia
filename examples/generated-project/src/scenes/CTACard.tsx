import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * CTACard — closing call-to-action card, data-driven.
 * The final cue's text, large and centred, above a gently pulsing
 * accent pill with a play glyph. The words are the CTA — they come
 * from the SRT, never from a template.
 */
export const CTACard: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const pulse = interpolate(
    Math.sin((frame / fps) * Math.PI * 1.4),
    [-1, 1],
    [0.94, 1.06],
  );
  const ring = interpolate((frame % (fps * 1.5)) / (fps * 1.5), [0, 1], [0, 1]);

  return (
    <SceneShell kicker="Call to Action">
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: `0 ${80 * s}px`,
        }}
      >
        <WordByWord
          text={scene.text}
          style={{ fontSize: 84 * s, fontWeight: 700, lineHeight: 1.3 }}
        />
        <div
          style={{
            marginTop: 64 * s,
            position: "relative",
            width: 120 * s,
            height: 120 * s,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: `3px solid ${theme.accent}`,
              opacity: 0.55 * (1 - ring),
              transform: `scale(${1 + ring * 0.45})`,
            }}
          />
          <div
            style={{
              width: 104 * s,
              height: 104 * s,
              borderRadius: "50%",
              backgroundColor: theme.accent,
              color: theme.bg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 44 * s,
              transform: `scale(${pulse})`,
              paddingLeft: 8 * s,
              boxSizing: "border-box",
            }}
          >
            ▶
          </div>
        </div>
      </div>
    </SceneShell>
  );
};
