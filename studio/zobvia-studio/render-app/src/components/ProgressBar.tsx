import React from "react";
import { useCurrentFrame } from "remotion";
import { timeline, totalDurationInFrames } from "../data/timeline";
import { theme } from "../theme";

/**
 * ProgressBar — v1.4 interactivity layer (rendered by Main at the
 * composition level, so useCurrentFrame() is the GLOBAL frame).
 *
 * A thin (6px) track at the very bottom edge of the frame fills with
 * an accent → accent2 → accent3 gradient as the video plays, with a
 * small dot at every scene boundary. It sits below the caption
 * overlay (captions rest at bottom: 64 * scale, well above 6px), so
 * the two never collide.
 */
export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const total = Math.max(1, totalDurationInFrames);
  const progress = Math.min(1, Math.max(0, frame / total));

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 0,
        height: 6,
        backgroundColor: "rgba(255, 255, 255, 0.10)",
        zIndex: 30,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${progress * 100}%`,
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.accent2}, ${theme.accent3})`,
        }}
      />
      {timeline.scenes.slice(1).map((scene) => (
        <div
          key={scene.index}
          style={{
            position: "absolute",
            top: "50%",
            left: `${(scene.start / timeline.totalDuration) * 100}%`,
            width: 6,
            height: 6,
            marginLeft: -3,
            marginTop: -3,
            borderRadius: "50%",
            backgroundColor: theme.fg,
            opacity: 0.65,
          }}
        />
      ))}
    </div>
  );
};
