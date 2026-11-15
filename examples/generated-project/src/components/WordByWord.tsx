import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

/**
 * Split a string into grapheme clusters.
 *
 * Bengali safety: conjuncts (যুক্তাক্ষর, e.g. ক্ষ, স্ত্র) and vowel signs are
 * multiple code points but ONE visible unit. Splitting by code point (or by
 * UTF-16 unit) tears them apart mid-animation, so we segment by grapheme
 * with Intl.Segmenter and fall back to Array.from (code points) only where
 * Segmenter is unavailable.
 */
export const splitGraphemes = (value: string): string[] => {
  const SegmenterCtor = (
    Intl as unknown as {
      Segmenter?: new (
        locales?: string,
        options?: { granularity: "grapheme" },
      ) => { segment: (input: string) => Iterable<{ segment: string }> };
    }
  ).Segmenter;
  if (SegmenterCtor) {
    const segmenter = new SegmenterCtor(undefined, {
      granularity: "grapheme",
    });
    return Array.from(segmenter.segment(value), (part) => part.segment);
  }
  return Array.from(value);
};

/** Frames between one word appearing and the next (kept in the 3-6 range). */
export const WORD_OFFSET_FRAMES = 4;

export interface WordByWordProps {
  text: string;
  /** Whole words to render in the accent colour (exact word match). */
  accentWords?: string[];
  style?: React.CSSProperties;
  /** Frame at which the first word starts appearing. Default 0. */
  startFrame?: number;
}

/**
 * Word-by-word animated text: each word fades / rises / settles in turn.
 * Words are never split internally — the grapheme splitter is used to
 * measure word length for a subtle per-word stagger, and rendering keeps
 * each word whole so Bengali conjuncts stay intact.
 */
export const WordByWord: React.FC<WordByWordProps> = ({
  text,
  accentWords = [],
  style,
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(/\s+/).filter(Boolean);
  const accentSet = new Set(accentWords);

  return (
    <span
      style={{
        fontFamily: theme.font,
        // Bengali rule: NEVER track Bengali text out — it breaks conjuncts.
        letterSpacing: 0,
        ...style,
      }}
    >
      {words.map((word, i) => {
        // Longer (multi-grapheme) words get a touch more settle time.
        const graphemeCount = splitGraphemes(word).length;
        const local = frame - startFrame - i * WORD_OFFSET_FRAMES;
        const opacity = interpolate(local, [0, 6], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const settle = spring({
          frame: local,
          fps,
          config: { damping: 18, stiffness: 160, mass: 0.7 },
          durationInFrames: 14 + Math.min(graphemeCount, 6),
        });
        const translateY = interpolate(settle, [0, 1], [26, 0]);
        const scale = interpolate(settle, [0, 1], [0.96, 1]);

        return (
          <React.Fragment key={`${word}-${i}`}>
            <span
              style={{
                display: "inline-block",
                opacity,
                transform: `translateY(${translateY}px) scale(${scale})`,
                color: accentSet.has(word) ? theme.accent : undefined,
                whiteSpace: "pre",
              }}
            >
              {word}
            </span>
            {i < words.length - 1 ? <span> </span> : null}
          </React.Fragment>
        );
      })}
    </span>
  );
};
