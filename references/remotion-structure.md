# Remotion Structure

CREATE step B5 scaffolds every project from
`templates/remotion-starter/` into this shape. Do not restructure it
per job — consistency is what makes Preview, re-render, and debugging
fast.

## Project tree

```
<project>/
├── package.json            # remotion deps pinned; scripts: studio, render
├── remotion.config.ts      # Config.setVideoImageFormat / overwriteOutput
├── public/
│   ├── voiceover.mp3       # optional, user-supplied only
│   ├── sfx/                # every SFX file named in out/timeline.md
│   │   └── SOURCES.md      # licence/source record for sourced sounds
│   └── assets/             # user-supplied images/media, names untouched
├── src/
│   ├── index.ts            # registerRoot(RemotionRoot)
│   ├── Root.tsx            # compositions: Main + PreviewAudio
│   ├── Main.tsx            # sequences scenes per timing.ts
│   ├── theme.ts            # palette + font + type scale (only place colours live)
│   ├── timing.ts           # cue → frame ranges, generated from the SRT
│   ├── scenes/
│   │   ├── Scene001.tsx    # one component per cue, numbered in order
│   │   └── …
│   └── components/
│       ├── WordText.tsx    # word-by-word animated text (Bengali-safe)
│       ├── Card.tsx        # base card surface for the chosen pipeline
│       ├── Highlight.tsx   # highlight sweep / emphasis word
│       └── Sfx.tsx         # <Audio> placement helper (frame-locked)
└── out/
    ├── timeline.md         # the B3 plan the code is checked against
    └── video.mp4           # render output (render/re-render modes only)
```

Folder rules:

- `public/` contents are referenced with `staticFile()` and are never
  renamed (Hard Rule 6). Subfolders are exactly `sfx/` and `assets/`;
  voiceover sits at `public/voiceover.mp3`, nowhere else.
- One scene component per SRT cue, named by cue order (`Scene001`…).
  A scene component renders exactly its cue's text — nothing else.
- Shared visuals live in `components/`; scene files contain layout and
  timing only. If two scenes need the same element, it is a component.
- No colours, font names, or sizes hard-coded in scenes — everything
  reads from `theme.ts`. No timing numbers hard-coded in scenes —
  everything reads from `timing.ts`.

## Root.tsx — compositions

Two compositions, both **1920×1080, 30 fps**:

```tsx
import { Composition } from "remotion";
import { Main } from "./Main";
import { TOTAL_FRAMES } from "./timing";

export const RemotionRoot = () => (
  <>
    <Composition
      id="Main"
      component={Main}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="PreviewAudio"
      component={Main}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ previewAudioOnly: true }}
    />
  </>
);
```

- `Main` — the deliverable composition; the render command targets it.
- `PreviewAudio` — same picture, used in Studio to audition SFX/voice
  sync at full volume without rendering; keep it in lockstep with
  `Main` (same component, prop-switched mix levels if needed).
- **Duration comes from the SRT:** `TOTAL_FRAMES = ceil(last cue end
  (sec) × 30) + 30` (a 1 s hold on the last frame). It is computed in
  `timing.ts` from `scripts/srt_parse.py` output — never typed by hand.

## timing.ts

Generated per job: for each cue, `{ scene: 1, from: <frame>, durationInFrames: <n>, text: "<exact SRT text>" }`.
Frame = `round(sec × 30)`. Gaps between cues belong to the preceding
scene (hold) unless the timeline plan says otherwise. `Main.tsx` maps
this array to `<Sequence>` elements — if the sequence count ≠ cue
count, the build is wrong (B12 check).

## theme.ts

The single source of visual truth, filled from
`scripts/color_palette.py --anchor <hex>` output (see
`color-system.md`):

```ts
export const theme = {
  bg: "#0A1929",        // primary ground
  surface: "#12283F",   // card surface (derived shade)
  text: "#F8FAFC",      // neutral light
  textMuted: "#475569", // Slate
  accent: "#0EA5E9",    // Sky — the one accent
  fontFamily: "Hind Siliguri",   // one family per video
  type: {
    hero: 120,      // px — hook / statement text
    title: 84,      // scene headlines
    body: 54,       // word-by-word narration text
    caption: 44,    // secondary lines
    small: 34,      // labels, axis text
  },
  radius: 24,         // card corner radius, px
  sfxVolume: { pop: 0.16, whoosh: 0.13, click: 0.18, pluck: 0.13, chime: 0.14, swipe: 0.14, thud: 0.20 },
};
```

Type scale is in px at 1920×1080. Bengali body text uses the same
scale (Latin words inside it get +4–6% per `bengali-text-rules.md`).

## Font loading

Load exactly one family via `@remotion/google-fonts/<Family>` in
`Main.tsx` (or a `fonts.ts` imported by it), and gate rendering on it:

```ts
import { loadFont } from "@remotion/google-fonts/HindSiliguri";
const { fontFamily, waitUntilDone } = loadFont("normal", { weights: ["400", "600", "700"] });
```

Use the package's `delayRender`/`continueRender` handle so no frame
renders before the font is ready — unstyled fallback frames are the
main cause of preview≠render differences (see `troubleshooting.md`).
For Latin-only jobs the same pattern applies with the chosen family.

## Render commands

```bash
npm install
npx remotion studio                              # Preview
npx remotion render Main out/video.mp4           # full render
npx remotion still Main out/check.png --frame=45 # single-frame check
```

Still-render the hook frame and one mid-video frame before any full
render: font shaping (Bengali conjuncts) and contrast are checked on
stills, not after a 3-minute render.
