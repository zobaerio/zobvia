import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { sceneAccent, theme } from "../theme";
import { SceneMetaContext } from "./SceneShell";

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

const DIGIT_RE = /[0-9\u09E6-\u09EF]/; // ASCII + Bengali digits
const LATIN_RE = /[A-Za-z]/;
const CONTENT_RE = /[\p{L}\p{N}]/u;

/**
 * v1.4 keyword colouring: indices of the "important" words in a cue —
 * words containing a number (ASCII or Bengali digits), Latin-script
 * words (brand names, tool names, terms), and the FIRST content word
 * of the cue (the first word carrying a letter or digit; leading
 * punctuation-only tokens like "—" are skipped). Words are matched
 * whole — grapheme clusters are never split.
 */
export const keywordIndices = (words: string[]): Set<number> => {
  const indices = new Set<number>();
  words.forEach((word, i) => {
    if (DIGIT_RE.test(word) || LATIN_RE.test(word)) {
      indices.add(i);
    }
  });
  const firstContent = words.findIndex((word) => CONTENT_RE.test(word));
  if (firstContent >= 0) {
    indices.add(firstContent);
  }
  return indices;
};

export interface WordByWordProps {
  text: string;
  /** Whole words to render in the accent colour (exact word match). */
  accentWords?: string[];
  /**
   * Base colour for ordinary words. Default: the per-scene rotating
   * accent (sceneAccent) when inside a scene, else inherited.
   */
  color?: string;
  /**
   * Colour for keyword words (numbers, Latin terms, first content
   * word). Default: the NEXT accent in the scene rotation, or
   * theme.accent2 outside a scene.
   */
  keywordColor?: string;
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
  color,
  keywordColor,
  style,
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const meta = React.useContext(SceneMetaContext);

  const words = text.split(/\s+/).filter(Boolean);
  const accentSet = new Set(accentWords);
  const keywords = keywordIndices(words);
  // v1.4 multi-colour: headline base colour rotates per scene;
  // keyword words take the next accent in the rotation so they always
  // stand apart from the headline colour.
  const baseColor = color ?? (meta ? sceneAccent(meta.position) : undefined);
  const keywordCol =
    keywordColor ?? (meta ? sceneAccent(meta.position + 1) : theme.accent2);

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

        const wordColor = accentSet.has(word)
          ? theme.accent
          : keywords.has(i)
            ? keywordCol
            : baseColor;
        return (
          <React.Fragment key={`${word}-${i}`}>
            <span
              style={{
                display: "inline-block",
                opacity,
                transform: `translateY(${translateY}px) scale(${scale})`,
                color: wordColor,
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
