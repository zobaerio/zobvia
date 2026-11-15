import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { sceneAccent, theme } from "../theme";

/**
 * Scene metadata for the v1.4 multi-colour / interactivity layer.
 * Main.tsx provides it around every scene (0-based position + total
 * scene count); SceneShell and WordByWord consume it. Outside a
 * provider (standalone component previews) it is null and both fall
 * back to the single-accent behaviour.
 */
export interface SceneMeta {
  /** 0-based position of the scene in the video. */
  position: number;
  /** Total number of scenes in the video. */
  total: number;
}

export const SceneMetaContext = React.createContext<SceneMeta | null>(null);

export interface SceneShellProps {
  /** Optional small label shown at the top, e.g. "HOOK • STATEMENT CARD". */
  kicker?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * Layout shell shared by every scene: theme background, safe margins
 * (96px sides / 72px top-bottom inside 1920x1080) and an optional kicker.
 * Children get a subtle entrance — a 10-frame fade/rise — so every
 * pipeline shares the same calm way of arriving on screen.
 *
 * v1.4: the kicker wears the per-scene rotating accent (sceneAccent),
 * and a low-opacity scene counter chip ("3 / 10") sits top-right so
 * the viewer always knows where they are in the video.
 */
export const SceneShell: React.FC<SceneShellProps> = ({
  kicker,
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const meta = React.useContext(SceneMetaContext);
  const entrance = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const accent = meta ? sceneAccent(meta.position) : theme.accent;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.bg,
        color: theme.fg,
        fontFamily: theme.font,
        letterSpacing: 0,
        padding: "72px 96px",
        boxSizing: "border-box",
        ...style,
      }}
    >
      {meta ? (
        <div
          style={{
            position: "absolute",
            top: 30,
            right: 40,
            fontSize: 22,
            fontWeight: 600,
            color: theme.fg,
            backgroundColor: theme.accentSoft,
            borderRadius: 999,
            padding: "6px 16px",
            opacity: 0.55 * entrance,
            zIndex: 15,
          }}
        >
          {meta.position + 1} / {meta.total}
        </div>
      ) : null}
      {kicker ? (
        <div
          style={{
            fontSize: 26,
            fontWeight: 600,
            color: accent,
            textTransform: "uppercase",
            marginBottom: 36,
            opacity: entrance,
          }}
        >
          {kicker}
        </div>
      ) : null}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          opacity: entrance,
          transform: `translateY(${(1 - entrance) * 24}px)`,
        }}
      >
        {children}
      </div>
    </AbsoluteFill>
  );
};
