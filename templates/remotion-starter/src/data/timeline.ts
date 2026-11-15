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
  /** Pipeline id: kinetic-hook | bento | dashboard | timeline | statement | recap | cta */
  pipeline: string;
}

export interface TimelineData {
  title: string;
  fps: number;
  width: number;
  height: number;
  /** Total duration in seconds. */
  totalDuration: number;
  scenes: TimelineScene[];
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
