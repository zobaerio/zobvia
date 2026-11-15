import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

/**
 * MinimalCleanScene — Minimal Clean pipeline (Stage family),
 * data-driven. A light look: the shell is overridden to a light ground
 * (theme.fg) with dark text (theme.bg). One centred element only — a
 * small accent rule, the cue text large in a light weight, generous
 * empty space, and the scene index as small chrome. Nothing else.
 * The cue text is rendered whole (never split internally).
 */
export const MinimalCleanScene: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;

  return (
    <SceneShell style={{ backgroundColor: theme.fg, color: theme.bg }}>
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: `0 ${140 * s}px`,
        }}
      >
        <div
          style={{
            width: 72 * s,
            height: 4,
            borderRadius: 2,
            backgroundColor: theme.accent,
            marginBottom: 48 * s,
          }}
        />
        <div
          style={{
            fontSize: 68 * s,
            fontWeight: 400,
            lineHeight: 1.45,
            letterSpacing: 0,
          }}
        >
          {scene.text}
        </div>
        <div
          style={{
            marginTop: 56 * s,
            fontSize: 24 * s,
            color: theme.muted,
            letterSpacing: 0,
          }}
        >
          {scene.index}
        </div>
      </div>
    </SceneShell>
  );
};
