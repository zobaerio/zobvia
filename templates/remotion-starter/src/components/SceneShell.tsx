import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";

export interface SceneShellProps {
  /** Optional small label shown at the top, e.g. "HOOK • STATEMENT CARD". */
  kicker?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * Layout shell shared by every scene: theme background, safe margins
 * (96px sides / 72px top-bottom inside 1920x1080) and an optional kicker.
 */
export const SceneShell: React.FC<SceneShellProps> = ({
  kicker,
  children,
  style,
}) => {
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
      {kicker ? (
        <div
          style={{
            fontSize: 26,
            fontWeight: 600,
            color: theme.accent,
            textTransform: "uppercase",
            marginBottom: 36,
          }}
        >
          {kicker}
        </div>
      ) : null}
      {children}
    </AbsoluteFill>
  );
};
