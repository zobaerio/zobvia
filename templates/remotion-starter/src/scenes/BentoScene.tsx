import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { theme } from "../theme";
import { cuesForScene } from "../timing";

interface Tile {
  title: string;
  body: string;
}

const TILES: Tile[] = [
  { title: "সমস্যা", body: "দর্শক স্ক্রল করে চলে যায়" },
  { title: "কারণ", body: "প্রথম লাইনেই মূল্য বোঝা যায় না" },
  { title: "সমাধান", body: "এক স্ক্রিনে চারটি স্পষ্ট ধারণা" },
  { title: "ফলাফল", body: "থামে চোখ, মনে থাকে বার্তা" },
];

/**
 * BentoScene — Bento Grid pipeline.
 * A word-by-word heading, then four tiles springing in one by one.
 */
export const BentoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const heading = cuesForScene("bento")[0]?.text ?? "";

  return (
    <SceneShell kicker="Bento Grid • চারটি ধারণা">
      <WordByWord
        text={heading}
        accentWords={["এক"]}
        style={{ fontSize: 64, fontWeight: 700, lineHeight: 1.3 }}
      />
      <div
        style={{
          marginTop: 48,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: theme.gap,
          flex: 1,
        }}
      >
        {TILES.map((tile, i) => {
          const entrance = spring({
            frame: frame - 20 - i * 8,
            fps,
            config: { damping: 16, stiffness: 140, mass: 0.8 },
          });
          return (
            <div
              key={tile.title}
              style={{
                backgroundColor: theme.accentSoft,
                border: `1px solid ${theme.accent}33`,
                borderRadius: theme.radius,
                padding: 40,
                opacity: entrance,
                transform: `translateY(${(1 - entrance) * 48}px) scale(${0.97 + entrance * 0.03})`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <div
                style={{ fontSize: 44, fontWeight: 700, color: theme.accent }}
              >
                {tile.title}
              </div>
              <div
                style={{
                  marginTop: 14,
                  fontSize: 32,
                  lineHeight: 1.45,
                  color: theme.fg,
                }}
              >
                {tile.body}
              </div>
            </div>
          );
        })}
      </div>
    </SceneShell>
  );
};
