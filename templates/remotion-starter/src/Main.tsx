import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { BentoScene } from "./scenes/BentoScene";
import { CTACard } from "./scenes/CTACard";
import { DashboardScene } from "./scenes/DashboardScene";
import { KineticHook } from "./scenes/KineticHook";
import { RecapGrid } from "./scenes/RecapGrid";
import { StatementCard } from "./scenes/StatementCard";
import { TimelineScene } from "./scenes/TimelineScene";
import { timeline, type SceneProps } from "./data/timeline";
import rawSfx from "./data/sfx.json";
import { theme } from "./theme";
import { HAS_VOICEOVER } from "./timing";

/** Pipeline id (from timeline.json) -> scene component. */
const PIPELINE_COMPONENTS: Record<string, React.FC<SceneProps>> = {
  "kinetic-hook": KineticHook,
  bento: BentoScene,
  dashboard: DashboardScene,
  timeline: TimelineScene,
  statement: StatementCard,
  recap: RecapGrid,
  cta: CTACard,
};

interface SfxEvent {
  file: string;
  atSeconds: number;
  sceneIndex: number;
}

const sfxEvents: SfxEvent[] = (
  rawSfx as { events?: SfxEvent[] }
).events ?? [];

/**
 * The Main composition — fully data-driven.
 *
 * Sequences are built from src/data/timeline.json: one scene per SRT
 * cue, each rendered by the component for its pipeline id. SFX events
 * from src/data/sfx.json play from public/ at their planned times
 * (files are referenced with staticFile(), so the demo's empty event
 * list — and any missing file — can never break bundling).
 *
 * As shipped, timeline.json is a small demo so the starter renders
 * standalone; zobvia's scripts/create_video.py regenerates both JSON
 * files from a real SRT.
 */
export const Main: React.FC = () => {
  const { fps } = timeline;
  return (
    <AbsoluteFill
      style={{ backgroundColor: theme.bg, fontFamily: theme.font }}
    >
      {timeline.scenes.map((scene) => {
        const Scene = PIPELINE_COMPONENTS[scene.pipeline] ?? StatementCard;
        return (
          <Sequence
            key={scene.index}
            from={Math.round(scene.start * fps)}
            durationInFrames={Math.max(
              1,
              Math.round((scene.end - scene.start) * fps),
            )}
            name={`${scene.index}-${scene.pipeline}`}
          >
            <Scene scene={scene} allScenes={timeline.scenes} />
          </Sequence>
        );
      })}
      {sfxEvents.map((event, i) => (
        <Sequence
          key={`sfx-${i}`}
          from={Math.round(event.atSeconds * fps)}
          durationInFrames={Math.round(0.5 * fps)}
          name={event.file}
        >
          <Audio src={staticFile(event.file)} />
        </Sequence>
      ))}
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
