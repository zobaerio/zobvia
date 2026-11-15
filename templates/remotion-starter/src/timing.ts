/**
 * timing.ts — FPS constant + the voiceover flag.
 *
 * The actual timeline now lives in `src/data/timeline.json` (typed via
 * `src/data/timeline.ts`): Main.tsx builds its Sequences from that JSON
 * and Root.tsx takes fps / width / height / duration from it. The
 * one-command converter (scripts/create_video.py) regenerates the JSON
 * from an SRT.
 *
 * The DEMO_CUES helpers below are retained for the legacy hand-written
 * HookScene demo component; Main no longer reads them.
 */

export const FPS = 30;

/**
 * Set to `true` ONLY after a real file exists at `public/voiceover.mp3`.
 * It defaults to `false` so a missing voiceover can never break bundling
 * or rendering — see `PreviewAudio` in Main.tsx.
 */
export const HAS_VOICEOVER = false;

export type SceneId = "hook" | "bento" | "dashboard";

export interface SrtCue {
  startSec: number;
  endSec: number;
  text: string;
  scene: SceneId;
}

export interface SceneSegment {
  scene: SceneId;
  startSec: number;
  durationSec: number;
}

/** Demo timeline: 3 scenes x 30s = 90s total (2700 frames @ 30fps). */
export const DEMO_CUES: SrtCue[] = [
  // --- Hook: Kinetic Typography / Statement Card (0-30s) ---
  { startSec: 0, endSec: 10, text: "প্রথম তিন সেকেন্ডই ঠিক করে দর্শক থাকবে কি না", scene: "hook" },
  { startSec: 10, endSec: 20, text: "তাই হুক হতে হবে এক লাইনে, পরিষ্কার আর বড়", scene: "hook" },
  { startSec: 20, endSec: 30, text: "এটাই এই ভিডিওর প্রতিশ্রুতি", scene: "hook" },
  // --- Bento Grid (30-60s) ---
  { startSec: 30, endSec: 40, text: "চারটি ধারণা, এক স্ক্রিনে সাজানো", scene: "bento" },
  { startSec: 40, endSec: 50, text: "প্রতিটি টাইল আসে একে একে", scene: "bento" },
  { startSec: 50, endSec: 60, text: "চোখ যেখানে থামে, বার্তা সেখানেই", scene: "bento" },
  // --- Data Dashboard (60-90s) ---
  { startSec: 60, endSec: 70, text: "সংখ্যা বললে গল্প বিশ্বাসযোগ্য হয়", scene: "dashboard" },
  { startSec: 70, endSec: 80, text: "কাউন্টার আর বার নিজে নিজে গড়ে ওঠে", scene: "dashboard" },
  { startSec: 80, endSec: 90, text: "শেষে থাকে শুধু একটি সিদ্ধান্ত", scene: "dashboard" },
];

export const secToFrames = (sec: number, fps: number = FPS): number =>
  Math.round(sec * fps);

export const totalDurationSec: number = DEMO_CUES.reduce(
  (max, cue) => Math.max(max, cue.endSec),
  0,
);

export const totalDurationInFrames: number = secToFrames(totalDurationSec);

/** Contiguous per-scene ranges derived from the cues, in cue order. */
export const sceneSegments: SceneSegment[] = DEMO_CUES.reduce<SceneSegment[]>(
  (segments, cue) => {
    const last = segments[segments.length - 1];
    if (last && last.scene === cue.scene) {
      last.durationSec = cue.endSec - last.startSec;
      return segments;
    }
    segments.push({
      scene: cue.scene,
      startSec: cue.startSec,
      durationSec: cue.endSec - cue.startSec,
    });
    return segments;
  },
  [],
);

export const cuesForScene = (scene: SceneId): SrtCue[] =>
  DEMO_CUES.filter((cue) => cue.scene === scene);
