import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * SlideshowScene — Slideshow genre scene (slideshow), data-driven.
 *
 * The themed gradient panel stands in for photos; real images from
 * public/ slot in via hand-authored timelines. A slow Ken Burns
 * scale (1→1.1 across the scene) drifts over the panel, framed like
 * a photo, with the cue as a caption strip at the bottom.
 */
export const SlideshowScene: React.FC<SceneProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = width / 1920;
  const durationInFrames = Math.max(
    1,
    Math.round((scene.end - scene.start) * fps),
  );
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(frame, [0, durationInFrames], [0, -16 * s], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame, [0, durationInFrames], [0, -10 * s], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell kicker="Slideshow">
      <div
        style={{
          flex: 1,
          position: "relative",
          overflow: "hidden",
          border: "12px solid rgba(255,255,255,0.85)",
          borderRadius: 8,
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(135deg, ${theme.bg} 0%, ${theme.accentSoft} 50%, ${theme.bg} 100%)`,
            transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.55)",
            padding: `${26 * s}px ${32 * s}px`,
            textAlign: "center",
          }}
        >
          <WordByWord
            text={scene.text}
            style={{ fontSize: 42 * s, fontWeight: 600, lineHeight: 1.35 }}
          />
        </div>
      </div>
    </SceneShell>
  );
};
