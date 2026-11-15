import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * DarkTechScene — Dark Tech pipeline (Free family), data-driven.
 * A near-black stage with a faint accent grid, and a terminal panel
 * whose lines are the cue's own chunks, each prefixed with a ">"
 * chrome glyph and appearing in stagger, ending in a blinking accent
 * cursor block. The panel header carries dots only — no fake text.
 *
 * NOTE: body text stays in theme.font (Hind Siliguri). A monospace
 * font would tear Bengali conjuncts and vowel signs apart, so the
 * terminal look comes from the panel, glyphs and colour — never from
 * switching Bengali text to a mono face.
 */
export const DarkTechScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;
  const chunks = splitChunks(scene.text, 5);
  const cursorOn = Math.floor(frame / 15) % 2 === 0;

  return (
    <SceneShell
      kicker="Dark Tech"
      style={{
        backgroundColor: "#05070A",
        backgroundImage: `linear-gradient(${theme.accent}14 1px, transparent 1px), linear-gradient(90deg, ${theme.accent}14 1px, transparent 1px)`,
        backgroundSize: `${64 * s}px ${64 * s}px`,
      }}
    >
      <WordByWord
        text={scene.text}
        style={{ fontSize: 56 * s, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          marginTop: 44 * s,
          borderRadius: theme.radius,
          backgroundColor: "rgba(0,0,0,0.55)",
          border: `1px solid ${theme.accent}44`,
          boxShadow: `0 0 60px ${theme.accent}22`,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 12 * s,
            padding: `${18 * s}px ${26 * s}px`,
            borderBottom: `1px solid ${theme.accent}2E`,
            backgroundColor: "rgba(255,255,255,0.03)",
          }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 16 * s,
                height: 16 * s,
                borderRadius: "50%",
                backgroundColor:
                  i === 0 ? theme.accent : "rgba(255,255,255,0.25)",
              }}
            />
          ))}
        </div>
        <div
          style={{
            padding: `${34 * s}px ${40 * s}px`,
            display: "flex",
            flexDirection: "column",
            gap: 22 * s,
            fontFamily: theme.font,
            letterSpacing: 0,
          }}
        >
          {chunks.map((chunk, i) => {
            const lineIn = interpolate(frame - 14 - i * 12, [0, 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={`${chunk}-${i}`}
                style={{
                  display: "flex",
                  gap: 18 * s,
                  opacity: lineIn,
                  transform: `translateX(${(1 - lineIn) * 18}px)`,
                  fontSize: 36 * s,
                  lineHeight: 1.5,
                }}
              >
                <span style={{ color: theme.accent, fontWeight: 700 }}>
                  &gt;
                </span>
                <span>{chunk}</span>
              </div>
            );
          })}
          <div style={{ display: "flex", gap: 18 * s, alignItems: "center" }}>
            <span
              style={{ color: theme.accent, fontWeight: 700, fontSize: 36 * s }}
            >
              &gt;
            </span>
            <span
              style={{
                display: "inline-block",
                width: 20 * s,
                height: 38 * s,
                backgroundColor: theme.accent,
                opacity: cursorOn ? 1 : 0.15,
              }}
            />
          </div>
        </div>
      </div>
    </SceneShell>
  );
};
