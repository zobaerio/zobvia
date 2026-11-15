import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { FloatY } from "../components/anim";
import { extractNumbers, splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * ProductScene — Product genre scene (product), data-driven.
 * A floating hero panel carries the full cue; underneath, chips
 * show only the cue's own number / currency tokens (extractNumbers).
 * A cue with no numbers falls back to its own chunks as chips.
 * A price is never invented.
 */
export const ProductScene: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;
  const numberTokens = extractNumbers(scene.text);
  const chips =
    numberTokens.length > 0 ? numberTokens : splitChunks(scene.text, 3);

  return (
    <SceneShell kicker="Product">
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <FloatY amplitude={10 * s} period={90}>
          <div
            style={{
              backgroundColor: theme.accentSoft,
              border: `2px solid ${theme.accent}`,
              borderRadius: theme.radius,
              padding: `${56 * s}px ${64 * s}px`,
              textAlign: "center",
              maxWidth: 1300 * s,
              boxSizing: "border-box",
            }}
          >
            <WordByWord
              text={scene.text}
              style={{ fontSize: 64 * s, fontWeight: 700, lineHeight: 1.35 }}
            />
          </div>
        </FloatY>
        <div
          style={{
            marginTop: 44 * s,
            display: "flex",
            flexWrap: "wrap",
            gap: 18 * s,
            justifyContent: "center",
          }}
        >
          {chips.map((chip, i) => (
            <div
              key={`${chip}-${i}`}
              style={{
                border: `1px solid ${theme.accent}77`,
                backgroundColor: "rgba(255,255,255,0.06)",
                borderRadius: 999,
                padding: `${14 * s}px ${28 * s}px`,
                fontSize: 32 * s,
                fontWeight: 600,
                lineHeight: 1.3,
                letterSpacing: 0,
              }}
            >
              {chip}
            </div>
          ))}
        </div>
      </div>
    </SceneShell>
  );
};
