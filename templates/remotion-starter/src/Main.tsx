import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { BentoScene } from "./scenes/BentoScene";
import { DashboardScene } from "./scenes/DashboardScene";
import { HookScene } from "./scenes/HookScene";
import { theme } from "./theme";
import {
  HAS_VOICEOVER,
  sceneSegments,
  secToFrames,
  type SceneId,
} from "./timing";

const SCENE_COMPONENTS: Record<SceneId, React.FC> = {
  hook: HookScene,
  bento: BentoScene,
  dashboard: DashboardScene,
};

/**
 * The Main composition: the demo scenes sequenced back-to-back.
 * Sequence boundaries come entirely from timing.ts — in CREATE mode the
 * skill regenerates that file from the SRT and this component is untouched.
 */
export const Main: React.FC = () => {
  return (
    <AbsoluteFill
      style={{ backgroundColor: theme.bg, fontFamily: theme.font }}
    >
      {sceneSegments.map((segment) => {
        const Scene = SCENE_COMPONENTS[segment.scene];
        return (
          <Sequence
            key={segment.scene}
            from={secToFrames(segment.startSec)}
            durationInFrames={secToFrames(segment.durationSec)}
            name={segment.scene}
          >
            <Scene />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

/**
 * Same visuals as Main, plus the voiceover track.
 *
 * The <Audio> element is only rendered when HAS_VOICEOVER is true in
 * timing.ts, which the skill flips ONLY after a real file has been placed
 * at public/voiceover.mp3. Because the file is referenced with staticFile()
 * (a runtime URL, not a bundled import), a missing file can never break
 * bundling, typechecking or a still render.
 */
export const PreviewAudio: React.FC = () => {
  return (
    <AbsoluteFill
      style={{ backgroundColor: theme.bg, fontFamily: theme.font }}
    >
      <Main />
      {HAS_VOICEOVER ? <Audio src={staticFile("voiceover.mp3")} /> : null}
    </AbsoluteFill>
  );
};
