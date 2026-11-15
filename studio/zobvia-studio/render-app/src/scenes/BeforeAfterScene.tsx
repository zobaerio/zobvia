import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * BeforeAfterScene — Before/After Split pipeline (Free family),
 * data-driven. The cue text is split into two halves (its chunks, or
 * its words in half when there is only one chunk). The left half is
 * desaturated/dim, the right half accent-tinted, and a centre divider
 * reveal animates over the first ~30 frames: the right side's clipPath
 * inset animates to 50%. "BEFORE" / "AFTER" are layout chrome labels
 * only — both halves' text comes from the cue.
 */
export const BeforeAfterScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const s = width / 1920;

  const chunks = splitChunks(scene.text, 4);
  let leftText: string;
  let rightText: string;
  if (chunks.length >= 2) {
    const mid = Math.ceil(chunks.length / 2);
    leftText = chunks.slice(0, mid).join(" ");
    rightText = chunks.slice(mid).join(" ");
    if (!rightText) rightText = leftText;
  } else {
    const words = scene.text.split(/\s+/).filter(Boolean);
    if (words.length >= 2) {
      const mid = Math.ceil(words.length / 2);
      leftText = words.slice(0, mid).join(" ");
      rightText = words.slice(mid).join(" ");
    } else {
      leftText = scene.text;
      rightText = scene.text;
    }
  }

  // Right side reveals from the right edge to the centre over ~30f.
  const reveal = interpolate(frame, [0, 30], [100, 50], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const halfStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    bottom: 0,
    width: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    padding: `${40 * s}px ${56 * s}px`,
    boxSizing: "border-box",
    fontSize: 52 * s,
    fontWeight: 700,
    lineHeight: 1.4,
    letterSpacing: 0,
  };
  const labelStyle: React.CSSProperties = {
    position: "absolute",
    top: 28 * s,
    fontSize: 24 * s,
    fontWeight: 700,
    letterSpacing: 0,
    padding: `${10 * s}px ${20 * s}px`,
    borderRadius: 999,
  };

  return (
    <SceneShell kicker="Before / After">
      <div
        style={{
          flex: 1,
          position: "relative",
          borderRadius: theme.radius,
          overflow: "hidden",
          border: "1px solid rgba(255,255,255,0.12)",
        }}
      >
        {/* Left half — desaturated / dim */}
        <div
          style={{
            ...halfStyle,
            left: 0,
            backgroundColor: "rgba(255,255,255,0.04)",
            color: theme.muted,
            filter: "saturate(0.25) brightness(0.75)",
          }}
        >
          {leftText}
          <div
            style={{
              ...labelStyle,
              left: 28 * s,
              backgroundColor: "rgba(0,0,0,0.45)",
              color: theme.fg,
            }}
          >
            BEFORE
          </div>
        </div>
        {/* Right half — accent-tinted, clipped by the animated reveal */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            clipPath: `inset(0 0 0 ${reveal}%)`,
          }}
        >
          <div
            style={{
              ...halfStyle,
              right: 0,
              backgroundColor: theme.accentSoft,
              color: theme.fg,
            }}
          >
            {rightText}
            <div
              style={{
                ...labelStyle,
                right: 28 * s,
                backgroundColor: theme.accent,
                color: theme.bg,
              }}
            >
              AFTER
            </div>
          </div>
        </div>
        {/* Centre divider */}
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: "50%",
            width: 4,
            marginLeft: -2,
            backgroundColor: theme.accent,
          }}
        />
      </div>
    </SceneShell>
  );
};
