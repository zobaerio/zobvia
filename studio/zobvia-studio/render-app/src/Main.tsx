import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { BeforeAfterScene } from "./scenes/BeforeAfterScene";
import { BentoScene } from "./scenes/BentoScene";
import { CarouselScene } from "./scenes/CarouselScene";
import { CTACard } from "./scenes/CTACard";
import { DarkTechScene } from "./scenes/DarkTechScene";
import { DashboardScene } from "./scenes/DashboardScene";
import { FlatVectorScene } from "./scenes/FlatVectorScene";
import { GlassCardsScene } from "./scenes/GlassCardsScene";
import { GlassShowcaseScene } from "./scenes/GlassShowcaseScene";
import { GlossyUiScene } from "./scenes/GlossyUiScene";
import { GradientFluidScene } from "./scenes/GradientFluidScene";
import { HubSpokeScene } from "./scenes/HubSpokeScene";
import { KineticHook } from "./scenes/KineticHook";
import { LineDrawScene } from "./scenes/LineDrawScene";
import { MinimalCleanScene } from "./scenes/MinimalCleanScene";
import { RecapGrid } from "./scenes/RecapGrid";
import { StatementCard } from "./scenes/StatementCard";
import { TimelineScene } from "./scenes/TimelineScene";
import { CubeScene } from "./scenes/CubeScene";
import { FlipCardScene } from "./scenes/FlipCardScene";
import { ParallaxScene } from "./scenes/ParallaxScene";
import { NewsScene } from "./scenes/NewsScene";
import { PodcastScene } from "./scenes/PodcastScene";
import { ProductScene } from "./scenes/ProductScene";
import { SlideshowScene } from "./scenes/SlideshowScene";
import { QuoteScene } from "./scenes/QuoteScene";
import { TutorialScene } from "./scenes/TutorialScene";
import { ScoreboardScene } from "./scenes/ScoreboardScene";
import { LyricsScene } from "./scenes/LyricsScene";
import { CaptionRenderer } from "./components/CaptionRenderer";
import { ProgressBar } from "./components/ProgressBar";
import { SceneMetaContext } from "./components/SceneShell";
import { SceneTransition } from "./components/transitions";
import { timeline, type SceneProps } from "./data/timeline";
import rawSfx from "./data/sfx.json";
import { theme } from "./theme";
import { HAS_VOICEOVER } from "./timing";

/** Pipeline id (from timeline.json) -> scene component. */
const PIPELINE_COMPONENTS: Record<string, React.FC<SceneProps>> = {
  "kinetic-hook": KineticHook,
  "glossy-ui": GlossyUiScene,
  "carousel-3d": CarouselScene,
  "dark-tech": DarkTechScene,
  "glass-cards": GlassCardsScene,
  "glass-showcase": GlassShowcaseScene,
  "minimal-clean": MinimalCleanScene,
  "gradient-fluid": GradientFluidScene,
  statement: StatementCard,
  bento: BentoScene,
  dashboard: DashboardScene,
  recap: RecapGrid,
  timeline: TimelineScene,
  "hub-spoke": HubSpokeScene,
  "before-after": BeforeAfterScene,
  "flat-vector": FlatVectorScene,
  "line-draw": LineDrawScene,
  cta: CTACard,
  "cube-3d": CubeScene,
  "flip-3d": FlipCardScene,
  "parallax-3d": ParallaxScene,
  news: NewsScene,
  podcast: PodcastScene,
  product: ProductScene,
  slideshow: SlideshowScene,
  quote: QuoteScene,
  tutorial: TutorialScene,
  scoreboard: ScoreboardScene,
  lyrics: LyricsScene,
};

interface SfxEvent {
  file: string;
  sound?: string;
  atSeconds: number;
  sceneIndex: number;
  /** v1.4: full sound length so long sounds (riser, ding…) play whole. */
  durationSeconds?: number;
  kind?: string;
}

const sfxEvents: SfxEvent[] = (
  rawSfx as { events?: SfxEvent[] }
).events ?? [];

/**
 * The Main composition — fully data-driven.
 *
 * Sequences are built from src/data/timeline.json: one scene per SRT
 * cue, each rendered by the component for its pipeline id, wrapped in
 * a SceneTransition (from scene.transition) and overlaid with a
 * CaptionRenderer (preset from timeline.captions). SFX events
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
      {timeline.scenes.map((scene, position) => {
        const Scene = PIPELINE_COMPONENTS[scene.pipeline] ?? StatementCard;
        const durationInFrames = Math.max(
          1,
          Math.round((scene.end - scene.start) * fps),
        );
        return (
          <Sequence
            key={scene.index}
            from={Math.round(scene.start * fps)}
            durationInFrames={durationInFrames}
            name={`${scene.index}-${scene.pipeline}`}
          >
            <SceneTransition type={scene.transition}>
              <SceneMetaContext.Provider
                value={{ position, total: timeline.scenes.length }}
              >
                <Scene scene={scene} allScenes={timeline.scenes} />
              </SceneMetaContext.Provider>
            </SceneTransition>
            <CaptionRenderer
              text={scene.text}
              preset={timeline.captions}
              durationInFrames={durationInFrames}
            />
          </Sequence>
        );
      })}
      {sfxEvents.map((event, i) => (
        <Sequence
          key={`sfx-${i}`}
          from={Math.round(event.atSeconds * fps)}
          durationInFrames={
            Math.ceil((event.durationSeconds ?? 0.5) * fps) + 2
          }
          name={event.file}
        >
          <Audio src={staticFile(event.file)} />
        </Sequence>
      ))}
      <ProgressBar />
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
