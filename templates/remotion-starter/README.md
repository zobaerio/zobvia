# zobvia — Remotion Starter

The working starter template for the **zobvia** skill's CREATE mode.
1920×1080, 30 fps, Bengali-first typography (Hind Siliguri), SFX only.

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
  Root.tsx               compositions Main + PreviewAudio, loads Hind Siliguri (400/600/700)
  Main.tsx               sequences the scenes from timing.ts; PreviewAudio adds <Audio>
  theme.ts               bg / fg / accent / accentSoft / muted / font / radius / gap
  timing.ts              THE timeline — cues, fps, HAS_VOICEOVER, secToFrames()
  components/
    WordByWord.tsx       word-by-word text (grapheme-safe for Bengali, letterSpacing: 0)
    SceneShell.tsx       background + safe margins + optional kicker
  scenes/
    HookScene.tsx        Kinetic Typography / Statement Card
    BentoScene.tsx       Bento Grid — 4 tiles springing in
    DashboardScene.tsx   Data Dashboard — counter-roll numbers + growing bars
public/
  voiceover.mp3          (you supply it — see public/README.md)
  sfx/                   sound effects only, no music
  assets/                images / logos / stills
```

Both compositions are **1920×1080 @ 30 fps**. As shipped, the demo timeline
in `src/timing.ts` is 90 seconds = **2700 frames**.

## How zobvia CREATE mode uses this template

1. **Copy** this folder to the project folder for the new video.
2. **Ask the ONE question** — the accent colour — and write it into
   `theme.accent` / `theme.accentSoft` in `src/theme.ts`. Nothing else is
   asked; everything else follows the chosen style skill.
3. **Parse the subtitles**: `scripts/srt_parse.py` (in the skill) turns the
   user's `.srt` into cue JSON. That output **replaces `DEMO_CUES`** in
   `src/timing.ts`, keeping the `{startSec, endSec, text, scene}` shape.
   Compositions, `<Sequence>` boundaries and the total duration re-time
   themselves from that data — no other file changes.
4. **Pick scenes per pipeline**: each cue's `scene` selects a scene
   component; swap / add scene components under `src/scenes/` to match the
   style skill's pipelines, reusing `WordByWord` and `SceneShell`.
5. **Assets**: voiceover goes to `public/voiceover.mp3` (then set
   `HAS_VOICEOVER = true` in `timing.ts`), generated SFX to `public/sfx/`,
   images to `public/assets/` — all referenced with `staticFile()`.
6. **Preview, then render**: `npm run still` for a frame check,
   `npm start` for Studio, `npm run build` for the final MP4.

## Bengali rules baked in

- Font is **Hind Siliguri**, loaded via `@remotion/google-fonts`.
- `letterSpacing` is **0 everywhere** — tracking breaks Bengali conjuncts.
- `WordByWord` segments with `Intl.Segmenter` (grapheme granularity) so
  যুক্তাক্ষর are never torn apart mid-animation.
