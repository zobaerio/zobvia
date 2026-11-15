import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { keywordIndices } from "./WordByWord";

/**
 * CaptionRenderer — caption overlay for a scene, from captions-library.
 *
 * Rendered inside the scene's Sequence, so `useCurrentFrame()` is
 * scene-local. Word onsets are distributed evenly across the scene:
 * onset_i = floor(i * durationInFrames / wordCount). Words are split
 * on whitespace ONLY — never inside a word — so Bengali conjuncts and
 * vowel signs stay whole (grapheme safety).
 *
 * Preset "word-by-word" (the DEFAULT) renders null: the scenes'
 * built-in WordByWord treatment IS that preset, so an overlay would
 * only duplicate it. Unknown presets behave as "word-by-word".
 */

export interface CaptionRendererProps {
  text: string;
  preset?: string;
  durationInFrames: number;
}

const BENGALI_RE = /[\u0980-\u09FF]/;

export const CaptionRenderer: React.FC<CaptionRendererProps> = ({
  text,
  preset,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { width, fps } = useVideoConfig();
  const s = width / 1920;

  const words = text.split(/\s+/).filter(Boolean);
  const wordCount = words.length;
  if (wordCount === 0) return null;

  const onset = (i: number) =>
    Math.floor((i * durationInFrames) / wordCount);
  // The currently-spoken word: last word whose onset is <= frame.
  let activeIndex = -1;
  for (let i = 0; i < wordCount; i++) {
    if (onset(i) <= frame) activeIndex = i;
  }

  const wrapperStyle: React.CSSProperties = {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 64 * s,
    display: "flex",
    justifyContent: "center",
    textAlign: "center",
    pointerEvents: "none",
    fontFamily: theme.font,
    letterSpacing: 0,
    padding: `0 ${96 * s}px`,
    boxSizing: "border-box",
    zIndex: 20,
  };
  const strokeShadow =
    "0 2px 6px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9), 2px 0 2px rgba(0,0,0,0.7), -2px 0 2px rgba(0,0,0,0.7)";

  switch (preset) {
    case "karaoke-highlight": {
      // v1.4: keyword words (numbers, Latin terms, first content word)
      // wear accent2 even when not active; the active word keeps the
      // primary accent and gets a spring scale pop (overshoot to
      // ~1.12x, then settle) instead of a static scale.
      const keywords = keywordIndices(words);
      const pop =
        activeIndex >= 0
          ? spring({
              frame: frame - onset(activeIndex),
              fps,
              config: { damping: 11, stiffness: 220, mass: 0.55 },
              durationInFrames: 14,
            })
          : 0;
      const activeScale = 1 + 0.12 * pop;
      return (
        <div style={wrapperStyle}>
          <div
            style={{
              fontSize: 54 * s,
              fontWeight: 700,
              lineHeight: 1.35,
              color: theme.fg,
              textShadow: strokeShadow,
              maxWidth: "92%",
            }}
          >
            {words.map((word, i) => (
              <React.Fragment key={`${word}-${i}`}>
                <span
                  style={{
                    display: "inline-block",
                    color:
                      i === activeIndex
                        ? theme.accent
                        : keywords.has(i)
                          ? theme.accent2
                          : theme.fg,
                    transform:
                      i === activeIndex
                        ? `scale(${activeScale})`
                        : "scale(1)",
                  }}
                >
                  {word}
                </span>
                {i < words.length - 1 ? <span> </span> : null}
              </React.Fragment>
            ))}
          </div>
        </div>
      );
    }
    case "bilingual-stack": {
      // Group the cue's OWN words by script — no translation is invented.
      const bengaliWords = words.filter((w) => BENGALI_RE.test(w));
      const otherWords = words.filter((w) => !BENGALI_RE.test(w));
      const rawActive = activeIndex >= 0 ? words[activeIndex] : undefined;
      // Highlight applies to the Bengali line only.
      const activeWord =
        rawActive && BENGALI_RE.test(rawActive) ? rawActive : undefined;
      const renderLine = (
        lineWords: string[],
        fontSize: number,
        opacity: number,
        highlight: boolean,
      ) => (
        <div
          style={{
            fontSize: fontSize * s,
            fontWeight: 700,
            lineHeight: 1.4,
            color: theme.fg,
            opacity,
            textShadow: strokeShadow,
          }}
        >
          {lineWords.map((word, i) => (
            <React.Fragment key={`${word}-${i}`}>
              <span
                style={{
                  color:
                    highlight && word === activeWord ? theme.accent : theme.fg,
                }}
              >
                {word}
              </span>
              {i < lineWords.length - 1 ? <span> </span> : null}
            </React.Fragment>
          ))}
        </div>
      );
      return (
        <div style={{ ...wrapperStyle, flexDirection: "column", alignItems: "center" }}>
          {bengaliWords.length > 0
            ? renderLine(bengaliWords, 56, 1, true)
            : null}
          {otherWords.length > 0
            ? renderLine(otherWords, 38, 0.8, false)
            : null}
        </div>
      );
    }
    case "classic-bottom": {
      const opacity = interpolate(frame, [0, 6], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      return (
        <div style={{ ...wrapperStyle, opacity }}>
          <div
            style={{
              fontSize: 54 * s,
              lineHeight: 1.4,
              color: "#FFFFFF",
              textShadow: strokeShadow,
              maxWidth: "88%",
            }}
          >
            {text}
          </div>
        </div>
      );
    }
    case "boxed-bold": {
      return (
        <div style={wrapperStyle}>
          <div
            style={{
              fontSize: 52 * s,
              fontWeight: 700,
              lineHeight: 1.4,
              color: "#FFFFFF",
              backgroundColor: "rgba(0,0,0,0.75)",
              padding: `${18 * s}px ${28 * s}px`,
              borderRadius: 14,
              maxWidth: "88%",
            }}
          >
            {text}
          </div>
        </div>
      );
    }
    case "minimal-line": {
      const opacity =
        interpolate(frame, [0, 6], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }) * 0.9;
      return (
        <div style={{ ...wrapperStyle, opacity }}>
          <div
            style={{
              fontSize: 40 * s,
              lineHeight: 1.4,
              color: "#FFFFFF",
              textShadow: "0 1px 4px rgba(0,0,0,0.55)",
              maxWidth: "90%",
            }}
          >
            {text}
          </div>
        </div>
      );
    }
    case "word-by-word":
    default:
      // The scenes' built-in WordByWord treatment IS this preset.
      return null;
  }
};
