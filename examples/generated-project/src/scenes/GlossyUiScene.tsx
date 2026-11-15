import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * GlossyUiScene — Glossy UI Mockup pipeline (Stage family), data-driven.
 * A browser frame sits centre-stage. Inside it, the heading is the cue
 * text word-by-word, and the cue's own chunks become UI list rows with
 * small accent markers. The frame chrome (dots, empty URL pill) carries
 * no text — all content comes from the cue.
 */
export const GlossyUiScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 5);
  const entrance = spring({
    frame: frame - 4,
    fps,
    config: { damping: 16, stiffness: 120, mass: 0.9 },
  });

  return (
    <SceneShell kicker="Glossy UI Mockup">
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "88%",
            borderRadius: theme.radius + 8,
            backgroundColor: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.16)",
            boxShadow:
              "0 40px 80px rgba(0,0,0,0.45), 0 4px 18px rgba(0,0,0,0.35)",
            overflow: "hidden",
            opacity: entrance,
            transform: `translateY(${(1 - entrance) * 40}px) scale(${0.97 + entrance * 0.03})`,
          }}
        >
          {/* Browser chrome: dots + empty URL pill — no fake text. */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14 * s,
              padding: `${20 * s}px ${28 * s}px`,
              background:
                "linear-gradient(180deg, rgba(255,255,255,0.14), rgba(255,255,255,0.04))",
              borderBottom: "1px solid rgba(255,255,255,0.10)",
            }}
          >
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 18 * s,
                  height: 18 * s,
                  borderRadius: "50%",
                  backgroundColor:
                    i === 0 ? theme.accent : "rgba(255,255,255,0.28)",
                }}
              />
            ))}
            <div
              style={{
                flex: 1,
                marginLeft: 18 * s,
                height: 34 * s,
                borderRadius: 17 * s,
                backgroundColor: "rgba(255,255,255,0.10)",
                border: "1px solid rgba(255,255,255,0.10)",
              }}
            />
          </div>
          <div style={{ padding: `${44 * s}px ${48 * s}px` }}>
            <WordByWord
              text={scene.text}
              style={{ fontSize: 56 * s, fontWeight: 700, lineHeight: 1.3 }}
            />
            {chunks.length >= 2 ? (
              <div
                style={{
                  marginTop: 40 * s,
                  display: "flex",
                  flexDirection: "column",
                  gap: 18 * s,
                }}
              >
                {chunks.map((chunk, i) => {
                  const rowIn = spring({
                    frame: frame - 18 - i * 8,
                    fps,
                    config: { damping: 16, stiffness: 150, mass: 0.7 },
                  });
                  return (
                    <div
                      key={`${chunk}-${i}`}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 20 * s,
                        backgroundColor: "rgba(255,255,255,0.05)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: 16,
                        padding: `${18 * s}px ${24 * s}px`,
                        opacity: rowIn,
                        transform: `translateX(${(1 - rowIn) * 28}px)`,
                        fontSize: 34 * s,
                        lineHeight: 1.4,
                      }}
                    >
                      <div
                        style={{
                          flexShrink: 0,
                          width: 14 * s,
                          height: 14 * s,
                          borderRadius: "50%",
                          backgroundColor: theme.accent,
                        }}
                      />
                      <div>{chunk}</div>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </SceneShell>
  );
};
