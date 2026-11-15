import React from "react";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { theme } from "../theme";
import { cuesForScene } from "../timing";

/**
 * HookScene — Kinetic Typography / Statement Card pipeline.
 * One big line, revealed word by word. Nothing else competes with it.
 */
export const HookScene: React.FC = () => {
  const headline = cuesForScene("hook")[0]?.text ?? "";
  return (
    <SceneShell kicker="Hook • Statement Card">
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <WordByWord
          text={headline}
          accentWords={["তিন", "সেকেন্ডই"]}
          style={{ fontSize: 104, fontWeight: 700, lineHeight: 1.25 }}
        />
        <div
          style={{
            marginTop: 44,
            width: 180,
            height: 8,
            borderRadius: 4,
            backgroundColor: theme.accent,
          }}
        />
        <div style={{ marginTop: 28, fontSize: 34, color: theme.muted }}>
          Kinetic Typography — একটি বাক্য, পুরো স্ক্রিন
        </div>
      </div>
    </SceneShell>
  );
};
