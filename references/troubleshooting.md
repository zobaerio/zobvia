# Troubleshooting

Match the symptom, apply the fix in order, and re-run the failed step
only. If two fixes fail, stop and report the exact error text — do not
keep improvising (never guess).

## 1. yt-dlp download fails

- **Symptoms:** `extract.py` errors on a YouTube/Shorts/Reels/TikTok
  URL; HTTP 403/429; "Video unavailable".
- **Fixes:** (1) Update yt-dlp: `pip install -U yt-dlp` — most failures
  are a stale extractor. (2) Retry once after 60 s (429 = rate limit).
  (3) For age/login-gated videos, ask the user for the local file
  instead — do not attempt cookie extraction or workarounds.
  (4) Check the URL is a video page, not a playlist/channel link.

## 2. Whisper is very slow or runs out of memory

- **Symptoms:** transcription takes > 1× video duration; OOM kill.
- **Fixes:** (1) Confirm `faster-whisper` is the backend
  (`check_tools.py` reports it); it is several times faster than
  `openai-whisper` on CPU. (2) Drop one model size (`medium` → `small`;
  word timestamps stay usable) and note the change in `summary.json`.
  (3) Extract audio first (`ffmpeg -vn -ar 16000`) — never feed video
  directly. (4) For videos > 3 min, LEARN's thin pass applies:
  transcribe fully but sample frames sparsely.

## 3. Bengali conjuncts render broken

- **Symptoms:** ক্ষ / জ্ঞ / স্ত্র appear split, with a visible hasant,
  or as boxes in stills/renders.
- **Fixes:** (1) Run the conjunct test set
  (`bengali-text-rules.md`) — identify exactly which clusters break.
  (2) Check segmentation: any `.split("")` or per-character span is
  the usual cause; segment with `Intl.Segmenter("bn")` and animate
  whole words. (3) Check `letterSpacing` is exactly 0 everywhere,
  including inherited theme values. (4) Confirm the loaded font is
  Hind Siliguri (or another listed Bengali font) and the weight used
  was actually loaded. (5) If one rare cluster still breaks, switch
  the family to Noto Sans Bengali for the whole video (one-family
  rule still holds).

## 4. SFX clips or distorts in the mix

- **Symptoms:** crackling, pumping, or harsh peaks where SFX meets
  voice; master meter over −1 dBFS.
- **Fixes:** (1) Lower the offending SFX to the bottom of its volume
  range in `sfx-library.md` (via `theme.ts` `sfxVolume`, not by
  editing the audio file). (2) Check for stacked events on the same
  frame — separate by ≥ 3 frames or drop the lesser one. (3) Fade
  chime tails that run under speech. (4) Re-check the master: peak
  ≤ −1 dBFS is a hard requirement, not a target.

## 5. Remotion render fails

- **Symptoms:** `npx remotion render Main out/video.mp4` errors —
  Chromium launch failure, composition not found, or a frame timeout.
- **Fixes:** (1) Read the first error, not the last: composition id
  must be exactly `Main`. (2) Chromium: run
  `npx remotion browser ensure` to fetch the bundled browser.
  (3) Frame timeout on a heavy scene: still-render that frame
  (`npx remotion still Main out/check.png --frame=<n>`) to see the
  real error. (4) Verify `node_modules` matches `package-lock.json` —
  delete and `npm install` once, cleanly.

## 6. Preview (Studio) looks different from the render

- **Symptoms:** fonts, timing, or colours differ between Studio and
  the MP4.
- **Fixes:** (1) Font race: the render started before the webfont
  loaded — the `delayRender`/`continueRender` gate from
  `remotion-structure.md` must wrap first render. (2) Colour: a scene
  hard-codes a value instead of reading `theme.ts` — grep for hex
  values outside `theme.ts`. (3) Timing: Studio fps ≠ composition
  fps — both compositions are fixed at 30 fps; do not change one.
  (4) Clear the Studio cache by restarting it after dependency or
  font changes.

## 7. ffmpeg / ffprobe missing

- **Symptoms:** `check_tools.py` fails at A0; `extract.py` cannot
  start.
- **Fixes:** Install per platform — Linux: `sudo apt install ffmpeg`;
  macOS: `brew install ffmpeg`; Windows: `winget install ffmpeg` —
  then re-run `scripts/check_tools.py` and confirm both `ffmpeg` and
  `ffprobe` report versions. Do not substitute another tool silently;
  the pipeline's frame extraction depends on ffprobe metadata.

## 8. Assets missing at render time

- **Symptoms:** render or Studio shows blank images / 404s for
  `staticFile()` paths.
- **Fixes:** (1) Compare every `staticFile()` argument against the
  actual `public/` listing — names must match byte-for-byte,
  including case and spaces. (2) Never "fix" a mismatch by renaming
  the asset (Hard Rule 6); fix the code reference only if the code
  invented the name — otherwise the scene becomes a text/card scene
  (B9). (3) Check the file is not zero bytes or a download placeholder.

## 9. SRT is malformed

- **Symptoms:** `srt_parse.py` reports unparseable cues, negative
  durations, or overlapping times.
- **Fixes:** (1) Safe automatic fixes only: missing cue numbers,
  missing blank lines between cues, `.` instead of `,` in timestamps,
  UTF-8 BOM. (2) Overlapping cues: clamp the earlier cue's end to the
  next cue's start and note it in `out/timeline.md`. (3) Anything that
  would require editing cue *text* to fix: stop and report the exact
  cue numbers — never rewrite the user's words. (4) Empty SRT (0
  cues): stop; there is nothing to build a video from.

## 10. Font weights do not load

- **Symptoms:** bold text renders regular; FOUT/flash of fallback;
  console warnings from `@remotion/google-fonts`.
- **Fixes:** (1) The weight must be requested explicitly —
  `loadFont("normal", { weights: ["400", "600", "700"] })` loads only
  those; using 700 without listing it silently falls back.
  (2) Confirm the family actually ships that weight (Hind Siliguri:
  300/400/500/600/700). (3) Use numeric weights in CSS matching the
  loaded set; `fontWeight: "bold"` can map to an unloaded 700 in
  some pipelines. (4) No network at render time: the font package
  downloads at first load — load once with network before rendering
  offline.

## 11. Word timing drifts from the voiceover

- **Symptoms:** highlights land early/late against
  `public/voiceover.mp3`, worse toward the end.
- **Fixes:** (1) Cumulative drift = frame rounding: compute each
  word's frame from its absolute timestamp (`round(sec × 30)`),
  never by accumulating rounded per-word durations. (2) Constant
  offset = voiceover lead-in: measure the first word's actual onset
  in the audio and shift `timing.ts` by that many frames, once.
  (3) If word timestamps were estimated by even distribution (B6) and
  a real voiceover exists, prefer re-deriving onsets from the audio
  with Whisper word timestamps.

## 12. ZIP opens but Studio errors on another machine

- **Symptoms:** user unzips the Preview project and `npm install` or
  Studio fails.
- **Fixes:** (1) `package-lock.json` must be in the ZIP — without it,
  versions float and break. (2) Check no absolute paths or
  `file:` references exist in `package.json` or imports.
  (3) Confirm `public/` travelled with the ZIP intact (some unzip
  tools skip empty folders — `public/sfx/` must contain its files).
  (4) Node version: the project needs Node 18+; state this in the
  delivery message if the user's error mentions engine mismatch.
