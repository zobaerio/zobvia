# Zobvia Studio (prototype)

**The owner's own software for the Zobvia skill.** A local web app with one
simple promise:

> Upload a **voice file** + an **SRT file**, answer **one question — which
> colour?** — click **Generate**, and get a finished motion-graphics video.

No terminal, no commands, no code. Everything runs on your own machine.

## Run it

```bash
cd ~/workspace/zobvia-studio
python3 server.py
```

Then open **http://localhost:8770** in a browser. Stop with `Ctrl+C`.
The server binds to `127.0.0.1` only — nothing is exposed to the network.

## How to use

1. **SRT file** (required) — drag & drop or click. Every scene of the video
   is built from its cues.
2. **Voice file** (optional) — MP3/WAV/M4A/… If given, your voice is mixed
   into the video. Without it, the video still renders (SFX sound only).
3. **Colour** — pick one of the 11 WCAG-checked tones as a swatch chip, or
   type/pick a custom `#RRGGBB` hex. This is Zobvia's famous ONE question.
4. **Format** — aspect (16:9 / 9:16 / 1:1) and a caption style
   (karaoke highlight, word-by-word, bilingual stack, classic bottom,
   boxed bold, minimal line).
5. **Generate** — watch the progress bar; when done, preview the video in
   the page and download the MP4.

## How it works

```
browser ──POST /api/jobs──▶ server.py (Python stdlib only)
                              │  saves uploads to jobs/<id>/
                              │  voice → ffmpeg → voice.mp3
                              ▼
              zobvia skill: scripts/create_video.py
              (--palette <tone|hex> --captions karaoke-highlight
               --sfx-theme cinematic [--voiceover voice.mp3])
                              │  generates a full Remotion project
                              ▼
              sync project src/ + public/ into render-app/
              (a prebuilt Remotion 4.0.543 app with node_modules and
               SELF-HOSTED Hind Siliguri fonts — required because
               Google Fonts is unreachable from headless Chromium
               on this machine; Root.patched.tsx restores the
               patched Root.tsx after every sync)
                              ▼
              npx remotion render Main          (no voice)
              npx remotion render PreviewAudio  (with voice)
                              ▼
              ffmpeg polish: stereo widen + loudnorm −14 LUFS
                              ▼
                        jobs/<id>/final.mp4 ──▶ preview + download
```

- Job status is polled at `GET /api/jobs/<id>` (JSON): `queued →
  preparing → rendering (live % parsed from Remotion's output) →
  done / failed`.
- The generated project's `src/` was diff-verified against the prebuilt
  render-app: identical code, only `src/data` + `src/theme.ts` differ —
  which is why syncing data/theme/SFX into one shared render app is safe.
- Voice files are converted to MP3 first because the skill only flips
  `HAS_VOICEOVER` (and the `PreviewAudio` composition only plays)
  `public/voiceover.mp3`.
- One compatibility shim lives in the sync step: v1.4 scene components
  import a `sceneAccent()` helper from `theme.ts`, which the skill's
  generated `theme.ts` does not always export yet. When it is missing,
  the server appends the starter's own helper (derived from the theme's
  `accent/accent2/accent3`, which the generator does provide). It is a
  no-op once the generator emits the export itself.

## Honest limits

- **Sequential jobs.** One render at a time; extra jobs wait in a queue.
  A 45-second video takes roughly **2.5–4 minutes** to render here.
- **SRT is required in practice.** Voice-only upload tries the skill's
  `transcribe.py`, but **Whisper is not bundled/installed on this
  machine**, so the job fails with an honest message asking for an SRT.
- **Prototype, not a product (yet).** No installer, no accounts, no
  settings persistence, no job history after a server restart (job
  folders stay on disk under `jobs/`).
- `render-app/` is ~920 MB because it carries `node_modules`.
- Under heavy machine load a render can occasionally die mid-encode
  (Remotion/ffmpeg pipe error). The job is marked failed honestly —
  just submit it again; the retry succeeds on an unloaded machine.
- Renders use the machine's cached headless Chromium; first-ever render
  on a new machine may need network access for Remotion's browser
  download and npm packages.

## Roadmap

- Bundle Whisper (faster-whisper) so voice-only → SRT works offline.
- Package as a real desktop app (installer) — e.g. PyInstaller + a small
  native shell, or Tauri/Electron around this same server.
- Job history page, recent-videos gallery, and one-click re-render with
  a different colour.
- Optional: expose on the home LAN with a password for phone uploads.

## Files

| File | What |
|---|---|
| `server.py` | The whole backend — stdlib-only HTTP server + job worker |
| `index.html` | The whole UI — one page, dark Zobvia theme |
| `render-app/` | Prebuilt Remotion render app (from the verified demo project) |
| `Root.patched.tsx` | Pristine copy of the self-hosted-font `Root.tsx`, restored after each sync |
| `jobs/` | Per-job inputs, generated project, `job.json`, `final.mp4` |
| `test-output.mp4` | A real end-to-end test render produced through this UI pipeline |
