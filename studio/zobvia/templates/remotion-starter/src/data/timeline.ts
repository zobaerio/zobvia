import rawTimeline from "./timeline.json";

/**
 * timeline.ts — typed access to the data-driven timeline.
 *
 * DEMO MODE (as shipped): timeline.json holds a small 9-scene demo so the
 * starter compiles and renders standalone.
 *
 * CREATE MODE: zobvia's scripts/create_video.py regenerates
 * timeline.json (and sfx.json) from the user's SRT — one scene per cue,
 * each with a pipeline id that Main.tsx maps to a scene component.
 * No code changes are needed when the data changes.
 */
export interface TimelineScene {
  index: number;
  /** Start time in seconds. */
  start: number;
  /** End time in seconds. */
  end: number;
  /** Exact on-screen text (from the SRT, unedited). */
  text: string;
  /** Pipeline id: kinetic-hook | glossy-ui | carousel-3d | dark-tech | glass-cards | minimal-clean | gradient-fluid | statement | bento | dashboard | recap | timeline | hub-spoke | before-after | flat-vector | line-draw | cta | cube-3d | flip-3d | parallax-3d | news | podcast | product | slideshow | quote | tutorial | scoreboard | lyrics */
  pipeline: string;
  /** Entrance transition for this scene: none | cut | fade | slide | zoom | whip */
  transition?: string;
}

export interface VoiceoverInfo {
  file: string;
  durationSeconds: number | null;
  srtDurationSeconds: number;
  driftSeconds: number | null;
}

export interface TimelineData {
  title: string;
  fps: number;
  width: number;
  height: number;
  /** Total duration in seconds. */
  totalDuration: number;
  scenes: TimelineScene[];
  /** Caption preset id from captions-library (e.g. "word-by-word"). */
  captions?: string;
  /** Layout family for the video (e.g. "stage", "grid", "flow"). */
  family?: string;
  /** Genre id for genre scenes (e.g. "news", "podcast", "lyrics"). */
  genre?: string;
  /** SFX theme id chosen for this video, when one applies. */
  sfxTheme?: string;
  voiceover?: VoiceoverInfo | null;
}

/** Props every data-driven scene component receives. */
export interface SceneProps {
  scene: TimelineScene;
  allScenes: TimelineScene[];
}

export const timeline = rawTimeline as unknown as TimelineData;

export const totalDurationInFrames: number = Math.round(
  timeline.totalDuration * timeline.fps,
);
