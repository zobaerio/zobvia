import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * transitions.tsx — entrance transitions for data-driven scenes.
 *
 * A transition is applied to the INCOMING scene: it plays over that
 * scene's first frames (the frame here is scene-local, because the
 * wrapper renders inside the scene's Sequence). Types come from
 * timeline.json (`scene.transition`); an unknown or missing type is
 * treated as a cut — children render untouched.
 */

export interface SceneTransitionProps {
  type?: string;
  children: React.ReactNode;
}

export const SceneTransition: React.FC<SceneTransitionProps> = ({
  type,
  children,
}) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();

  switch (type) {
    case "fade": {
      const opacity = interpolate(frame, [0, 10], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      return (
        <AbsoluteFill style={{ overflow: "hidden", opacity }}>
          {children}
        </AbsoluteFill>
      );
    }
    case "slide": {
      const progress = interpolate(frame, [0, 12], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return (
        <AbsoluteFill
          style={{
            overflow: "hidden",
            opacity: progress,
            transform: `translateX(${(1 - progress) * 60}px)`,
          }}
        >
          {children}
        </AbsoluteFill>
      );
    }
    case "zoom": {
      const progress = interpolate(frame, [0, 9], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      return (
        <AbsoluteFill
          style={{
            overflow: "hidden",
            opacity: progress,
            transform: `scale(${1.1 - progress * 0.1})`,
          }}
        >
          {children}
        </AbsoluteFill>
      );
    }
    case "whip": {
      const progress = interpolate(frame, [0, 9], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      });
      const blur = interpolate(progress, [0, 1], [14, 0]);
      return (
        <AbsoluteFill
          style={{
            overflow: "hidden",
            transform: `translateX(${(1 - progress) * -0.6 * width}px)`,
            filter: blur > 0.1 ? `blur(${blur}px)` : undefined,
          }}
        >
          {children}
        </AbsoluteFill>
      );
    }
    case "none":
    case "cut":
    default:
      return <>{children}</>;
  }
};
