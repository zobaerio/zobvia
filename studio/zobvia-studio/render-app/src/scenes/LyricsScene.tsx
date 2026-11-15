import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { FadeUp } from "../components/anim";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * LyricsScene — Lyrics genre scene (lyrics), data-driven.
 * The cue is split into whole lines only — preferring sentence
 * punctuation (splitChunks already prefers it), never splitting
 * words. Lines fade up in stagger; the latest line reached is in
 * the foreground colour, earlier lines fall back to muted.
 */
export const LyricsScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;

  // Prefer sentence punctuation when present; splitChunks does the
  // same preference internally, this keeps the intent explicit.
  const bySentence = scene.text
    .split(/(?<=[।.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean);
  const lines =
    bySentence.length >= 2
      ? bySentence.slice(0, 4)
      : splitChunks(scene.text, 4);

  const durationInFrames = Math.max(
    1,
    Math.round((scene.end - scene.start) * fps),
  );
  const progress = (frame / durationInFrames) * lines.length;
  const currentLine = Math.min(
    lines.length - 1,
    Math.max(0, Math.floor(progress)),
  );

  return (
    <SceneShell kicker="Lyrics">
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 30 * s,
          textAlign: "center",
          padding: `0 ${60 * s}px`,
        }}
      >
        {lines.map((line, i) => (
          <FadeUp key={`${line}-${i}`} delay={i * 10}>
            <div
              style={{
                fontSize: 64 * s,
                fontWeight: 700,
                lineHeight: 1.4,
                color: i === currentLine ? theme.fg : theme.muted,
                letterSpacing: 0,
              }}
            >
              {line}
            </div>
          </FadeUp>
        ))}
      </div>
    </SceneShell>
  );
};
