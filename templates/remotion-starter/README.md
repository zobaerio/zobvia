# zobvia — Remotion Starter

The working starter template for the **zobvia** skill's CREATE mode.
Data-driven compositions, Bengali-first typography (Hind Siliguri),
SFX only, no music.

## Quick start

```bash
npm install
npm start          # Remotion Studio — live preview in the browser
```

## Render

```bash
npm run build      # full video  -> out/video.mp4   (composition: Main)
npm run render     # alias of build
npm run still      # one frame   -> out/preview.png (composition: Main)
npm run typecheck  # tsc --noEmit
```

Render a specific frame / the audio variant:

```bash
npx remotion still Main out/preview.png --frame=30
npx remotion render PreviewAudio out/video-with-voice.mp4
```

## What is in here

```
src/
  index.ts               registerRoot(RemotionRoot)
  Root.tsx               compositions Main + PreviewAudio; geometry from data/timeline.json; loads Hind Siliguri (400/600/700)
  Main.tsx               builds <Sequence>s from data/timeline.json + plays data/sfx.json events; PreviewAudio adds the voiceover <Audio>
  theme.ts               bg / fg / accent / accentSoft / muted / font / radius / gap
  timing.ts              FPS + HAS_VOICEOVER flag (legacy demo helpers for HookScene)
  data/
    timeline.json        THE timeline — {fps, width, height, totalDuration, scenes[{index, start, end, text, pipeline}]}
    sfx.json             SFX events — {events[{file, atSeconds, sceneIndex}]}
    timeline.ts          typed access to timeline.json
  components/
    WordByWord.tsx       word-by-word text (grapheme-safe for Bengali, letterSpacing: 0)
    SceneShell.tsx       theme background + safe margins + kicker + subtle entrance
    chunks.ts            sentence/phrase splitting + grapheme-safe truncation for tile/node layouts
  scenes/                data-driven, one component per pipeline id
    KineticHook.tsx      "kinetic-hook" — huge word-by-word hook text + accent bar
    BentoScene.tsx       "bento" — heading + tiles from the cue's own chunks
    DashboardScene.tsx   "dashboard" — counters for numbers in the cue (ASCII + Bengali digits) + bars
    TimelineScene.tsx    "timeline" — spine with nodes lighting up per step
    StatementCard.tsx    "statement" — one huge centred sentence
    RecapGrid.tsx        "recap" — tick-off tiles of the previous scenes' text
    CTACard.tsx          "cta" — final cue, large, with a pulsing play pill
    HookScene.tsx        legacy hand-written demo scene (not used by Main)
public/
  voiceover.mp3          (you supply it — see public/README.md)
  sfx/                   sound effects only, no music
  assets/                images / logos / stills
```

As shipped, `src/data/timeline.json` is a 90-second, 9-scene demo at
1920×1080 @ 30 fps, so the starter renders standalone.

## How zobvia CREATE mode uses this template

1. **Generate** the project with the skill's one-command converter:
   `python3 scripts/create_video.py --srt <file.srt> --palette <tone-or-hex> --out <dir>`
   (aspect via `--aspect 16:9|9:16|1:1`). It copies this starter and
   regenerates `src/data/timeline.json`, `src/data/sfx.json`,
   `src/theme.ts`, the SFX WAVs in `public/sfx/`, `timeline.md` and
   `PROJECT_README.md`.
2. **Or shape it manually**: copy this folder, write the palette into
   `src/theme.ts`, and write scenes into `src/data/timeline.json`
   yourself — one scene per SRT cue, each with a pipeline id from the
   table above. Compositions, `<Sequence>` boundaries, geometry and
   total duration all follow the JSON — no code changes.
3. **Assets**: voiceover goes to `public/voiceover.mp3` (then set
   `HAS_VOICEOVER = true` in `timing.ts`), generated SFX to
   `public/sfx/`, images to `public/assets/` — all referenced with
   `staticFile()`.
4. **Preview, then render**: `npm run still` for a frame check,
   `npm start` for Studio, `npm run build` for the final MP4.

## Bengali rules baked in

- Font is **Hind Siliguri**, loaded via `@remotion/google-fonts`.
- `letterSpacing` is **0 everywhere** — tracking breaks Bengali conjuncts.
- `WordByWord` segments with `Intl.Segmenter` (grapheme granularity) so
  যুক্তাক্ষর are never torn apart mid-animation; tile/node layouts split
  and truncate only on word boundaries (`components/chunks.ts`).
- Dashboard counters keep the cue's digit script: Bengali cues count
  in ০-৯, Latin cues in 0-9.
