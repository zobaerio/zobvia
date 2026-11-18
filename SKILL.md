---
name: zobvia
description: "Four modes plus bundled sub-skills. LEARN: watch a video and extract its editing style into a reusable style skill — use when the user says 'watch this', 'learn this style', 'analyse this video', pastes a video link (YouTube, Shorts, Reels, TikTok) or gives a local video file without an SRT. CREATE: turn an SRT/subtitle file into a Remotion motion-graphics video (1920x1080, 30fps, word-by-word animation, SFX only, full Bengali support) — use when the user says 'make a motion graphics video from this SRT', 'edit in <style> style', pastes or attaches an .srt file, or gives both a video and an SRT (learn the style, then create in it). DOCUMENTARY: turn a documentary title or topic into a complete 10-minute VOX-style YouTube documentary production package (research, script, 8-second scene map, text-to-video prompts, audio package, SEO packaging, thumbnails, checklist) in 10 approval-gated stages — use when the user says 'documentary', 'ডকুমেন্টারি', 'make a documentary about', or gives a documentary title/topic. EDIT: edit an existing video or audio file with local FFmpeg (cut, join, silence removal, reframe, captions, loudness, platform exports, delivery checks) via the bundled ffmpeg-skill — use when the user gives a video/audio file and asks to trim, cut, resize, reframe, caption, clean up, or export it for a platform."
---

# Zobvia

One skill, four jobs: **learn how a video is edited**, **create a new
video in a learned or built-in style**, **plan a full documentary
production package** from a title or topic, and **edit real footage**
with FFmpeg. Style is learned; footage, voice, and music are never
reused. Bundled sub-skills extend it further: a 3D cartoon
explainer engine (Part E), the ffmpeg-skill toolset (Part F), a
headless-Blender 3D asset toolkit (Part G), a typed audio-production
engine (Part H), a colour-grading engine (Part I) and an HTML-scene
video renderer (Part J).

## Philosophy

- **Measurable numbers over adjectives.** Not "fast-paced" — "median shot
  1.8 s, 34 cuts/min, captions 3 words/line". Every claim in a style skill
  or a plan must be a number, a frame count, or a hex value.
- **Never guess.** If a tool, file, or measurement is missing, say so and
  stop that step. Do not estimate a cut point, a colour, or a duration.
- **Save progress to disk after every batch.** Analysis, timelines, and
  plans are files, not chat text. A crashed session must be resumable
  from disk alone.
- **Learn style only.** Never copy a creator's footage, voice, music, or
  wording into a new video.
- **CREATE: user is DIRECTOR, skill is EDITOR.** The skill decides
  pacing, scenes, pipelines, animation, and SFX. The only decision it
  asks for is colour — exactly one question, never a second.

## Access gate (run once per machine, before anything else)

Zobvia is password-gated at install, by the author's decision. Before the
first LEARN or CREATE run on a machine:

1. Run `python3 scripts/access_check.py --status`.
2. If it reports **unlocked**, proceed silently — never mention it again.
3. If it reports **locked**, ask the user for the Zobvia access password
   (this is an install-time gate, separate from CREATE's colour question),
   then verify with `ZOBVIA_PASSWORD=<their answer> python3 scripts/access_check.py`.
   On success the script writes a marker (`~/.zobvia/access-ok`) and the
   user is never asked again on that machine.
4. Never store, log, or repeat the plain password anywhere. Only its
   SHA-256 hash exists in the code. The password is the author's GitHub
   username — if the user asks what it is, tell them that.

## Mode routing

| Input | Mode |
|---|---|
| SRT / subtitle file, no video | CREATE |
| Video link or file, no SRT | LEARN |
| Video + SRT | LEARN first, then CREATE in that style |
| "edit in `<style>` style" + SRT | CREATE using `.claude/skills/style-<slug>/` |
| Documentary title/topic, "documentary", "ডকুমেন্টারি" | DOCUMENTARY |
| 3D cartoon explainer / "what if" short with characters | 3D EXPLAINER (Part E) |
| An existing video/audio file to trim, cut, reframe, caption, clean or export | EDIT (Part F) |
| A 3D model file (glb/fbx/obj/stl/usd/blend) to inspect, convert, optimise, bake or render | BLENDER (Part G) |
| An audio operation graph: gain/trim/mix/stems/loudness versions/downmix/noise reduction | AUDIO PRODUCTION (Part H) |
| A colour treatment on a video: HDR to SDR, LUT, retag, primary correction, legalize, camera match | COLOR GRADING (Part I) |
| An HTML scene / title card / slate / stinger to render to video | HYPERFRAMES (Part J) |
| Neither, or genuinely unclear | Ask one question: learn or create? |

Auto-selection rules:

1. An `.srt` attachment or pasted SRT block always selects CREATE,
   even if the message also names a style.
2. A video URL (YouTube, Shorts, Reels, TikTok) or video file with no
   SRT always selects LEARN.
3. Both present: run LEARN to completion (style skill saved), then run
   CREATE using that style. Do not ask which to do first.
4. A style name with no SRT and no video is not enough to start CREATE —
   ask for the SRT (this is a missing-input request, not a design
   question, and does not count against the one-question rule in B2).
5. A documentary request (a title/topic plus documentary intent, e.g.
   "make a documentary about X") selects DOCUMENTARY even with no SRT
   and no video. Inside a documentary project, the master prompt's
   stage-approval gates replace CREATE's one-question rule.

---

## PART A — LEARN

Goal: one source video → one reusable style skill at
`.claude/skills/style-<slug>/`, where `<slug>` is a kebab-case name
derived from the creator or the dominant look (e.g. `style-dark-tech-ali`).

### A0 — Check tools

Run `scripts/check_tools.py`. It verifies `ffmpeg`, `ffprobe`, `yt-dlp`,
and a Whisper backend (`faster-whisper` preferred, `openai-whisper`
fallback). If anything required is missing, report the exact missing
tool and its install hint from the script output, then stop. Do not
attempt extraction with a partial toolchain.

### A1 — Extract

Run `scripts/extract.py <url-or-path> --name <slug>`. Outputs land in
`references/watch/<slug>/`:

| File | Contents |
|---|---|
| `source.mp4` | Downloaded/copied source, normalised |
| `frames/` | Extracted frames at cut points and intervals |
| `pairs/` | Before/after frame pairs straddling each cut |
| `cuts.json` | Cut timestamps, shot durations, cut rate |
| `words.json` | Whisper word-level timestamps |
| `audio_profile.json` | Loudness, silence, beat/onset and SFX-event profile |
| `summary.json` | Video metadata: duration, fps, resolution, totals |

If a download fails, retry once with a fresh yt-dlp
(`pip install -U yt-dlp`); if it still fails, ask the user to download
the video and give the file path. For other failures, read
`references/troubleshooting.md` before retrying.

Long videos (over 3 minutes): run the thin pass first (wider frame
interval), then re-run dense windows with `--start` / `--end` on the
interesting ranges. Always study the first 60 seconds densely — the
hook decides the style. State clearly in the analysis which time
ranges were studied densely and which were only sampled.

### A2 — Frame-pair analysis

Read `pairs/` **10 pairs at a time**. For each pair record, in
`references/watch/<slug>/analysis/timeline.md`:

- Time range and shot duration from `cuts.json`.
- Shot type: talking head, b-roll, screen recording, text card,
  graphic, product shot.
- Framing: close / medium / wide, and the subject's position.
- What changed across the cut (subject, scale, angle, background,
  text) and the transition type (hard cut, zoom in/out, punch-in, pan,
  whip, fade, glitch, shake, speed ramp, none — vocabulary in
  `references/animation-library.md`).
- On-screen text: the exact words, position, font look (bold / thin /
  serif / sans), size, colours, outline or shadow, background box.
- Overlays: emojis, stickers, arrows, icons, lower thirds, progress
  bars, logos.
- Colour look: warm / cool, contrast, saturation, filters, vignette,
  grain.

Save the file after every batch of 10. Never analyse from memory of
the video; only from the frames on disk.

### A3 — Caption analysis

From `words.json` and the frames, measure: words per caption line,
lines per caption block, words on screen at once, caption position
(% from bottom) and safe margins, font weight/size relative to frame
height, highlight style (colour swap, scale, background box, karaoke
fill), and whether captions are word-by-word, phrase, or full-line.
Also measure: caption timing offset (do words land exactly on the
spoken word, or slightly before/after — in ms), casing (UPPER / Title
/ lower), punctuation shown or hidden, emojis near words, which words
get emphasis (numbers, keywords, verbs) and how, typical words per
second, and the longest time a caption stays on screen. Record
numbers, not impressions.

### A4 — Audio, SFX, and music analysis

From `audio_profile.json` and listening checkpoints at detected events:
classify each recurring sound against the 7 types in
`references/sfx-library.md`, count SFX events per 60 s, note what visual
event each sound is locked to, and record music presence (genre feel,
BPM if measurable, volume relative to voice in dB, where it drops out).
For the voice: measure pace (words per second), pause pattern, and
whether silences are cut out (jump cuts). For every SFX type, also
write search keywords so the sound can be found later on free SFX
sources (e.g. Openverse).
Write the result as an **SFX map** — JSON in
`analysis/sfx-map.json`:

```json
{ "events": [ { "at_sec": 12.4, "type": "soft pop", "locked_to": "word highlight", "gain_db": -18 } ],
  "events_per_60s": 6, "music": { "present": true, "relative_to_voice_db": -14 },
  "voice": { "words_per_sec": 2.6, "silences_cut": true },
  "sfx_search_keywords": { "soft pop": "soft pop sound effect free" } }
```

### A5 — Hook and ending

Analyse the first 3 s and the last 5 s separately, frame by frame:
hook type (question, claim, pattern interrupt, result-first), time to
first cut, time to first text on screen, text size as % of frame
height; ending type (loop-back, CTA, recap, abrupt), and whether the
last frame connects to the first.

### A6 — Synthesise measurable numbers

Aggregate A2–A5 into the style's headline numbers: median and mean shot
length, cuts/min, zoom frequency and magnitude, caption stats, SFX
density, hook timing, colour palette sampled from frames (hex values),
and font characteristics. Any field you could not measure is written
as `not measured` — never filled with a plausible value.

### A7 — Save as a style skill

Copy `references/style-skill-template.md`, fill every section from the
measured analysis, and save as `.claude/skills/style-<slug>/SKILL.md`.
Copy the sampled palette, SFX map, and 3–5 representative frames into
that folder as supporting references. The saved skill must be usable
by CREATE without re-watching the source.

Then index it: add one line under a "Learned styles" heading in the
project `CLAUDE.md` (style name + when to use it; create the heading
if missing). If an editor skill already exists in `.claude/skills/`
(a folder with "editor" in its name), add one short line to it
pointing at the new style skill — do not rewrite that editor skill.
If a style skill with the same name already exists, ask before
overwriting, or save as `style-<slug>-v2`.

### A8 — Report

Tell the user: style name and slug, the 5–8 headline numbers, hook
type, caption style, SFX density, the saved path, anything that could
not be learned and why, and one example prompt ("Edit my video in the
style-<slug> style"). Offer CREATE ("give me an SRT and I'll cut it
in this style") — do not start CREATE without an SRT.

---

## PART B — CREATE

Goal: one SRT → one Remotion project (1920×1080, 30 fps) delivered as
a Preview ZIP by default. SFX only, no music. Nothing appears in the
video that is not in the SRT.

**Golden rule:** decide everything yourself — scenes, pipelines,
animation, pacing, SFX — except colour. Ask **exactly one question**
(the colour question, B2), **in the SRT's language**, and never a
second question. Missing inputs (no SRT, missing asset) are reported
as blockers, not turned into design questions.

### B0 — Inputs

Required: one `.srt` file. Optional: a style (built-in pipeline from
`references/style-pipelines.md`, or a learned `style-<slug>`), and
assets in `public/` supplied by the user. If a learned style is named,
read its `SKILL.md` fully before planning; its measured numbers
override the built-in defaults wherever they conflict.

### B1 — Read the SRT fully

Run `scripts/srt_parse.py <file.srt>`. It returns cues with start/end
times, duration, word counts, total duration, and language detection.
Read **every cue** before planning — never plan from the first minute
and improvise the rest. Malformed SRT: see
`references/troubleshooting.md`; fix only unambiguous formatting
(numbering, blank lines), never rewrite cue text.

### B2 — The one question: colour

Run `scripts/color_palette.py` to build 6 options suited to the SRT's
topic and the chosen style. Ask once, in the SRT's language, presenting
each option as **name + hex + one-line meaning**, e.g.:

> Which colour should this video use?
> 1. Deep Navy `#0A1929` — trust, serious, professional
> 2. …

Wait for the answer. The chosen palette follows
`references/color-system.md` (primary + neutral + 1 accent, contrast
≥ 4.5:1). If the user has already stated a colour in their message,
skip the question entirely — do not ask a question already answered.

The chosen palette now also yields `accent2`/`accent3` companions
(derived in `scripts/color_palette.py`, each contrast-ensured to
≥ 4.5:1 WCAG AA against the tone's scene background): headline
colour rotates accent → accent2 → accent3 across scenes, and keyword
words (numbers, Latin terms, the first content word) take a companion
accent. The user still answers only ONE colour question — the
companions are derived, never asked.

### B3 — Timeline planning

Write `out/timeline.md` before writing any code: **one cue = one
scene**. For each cue: scene number, start/end (frame numbers at
30 fps), the exact on-screen text (from the SRT, unedited), pipeline,
text animation, card/UI element if any, transition in, and SFX events.
Total scenes must equal total cues. Save it; it is the contract the
code is checked against.

### B4 — Choose pipelines

Pick from the 16 in `references/style-pipelines.md`. Rules:

- Maximum **2–3 styles per minute** of video; a 60–90 s video uses
  2–4 pipelines total.
- **Never mix layout families** in one video: grid family (Bento,
  Dashboard, Checklist) does not mix with stage family (Carousel,
  Kinetic, Statement) or flow family (Timeline, Hub-and-Spoke) —
  pick one family and vary within it.
- The converter's planner enforces this automatically: it picks ONE
  family from the SRT's dominant signal (step words → flow, numbers →
  grid, otherwise stage), rotates pipelines within that family for the
  middle scenes, and writes a per-scene `transition` into
  `timeline.json` — about 80% hard cuts; a whip appears only on a topic
  change (a ≥ 1.5 s pause between cues or a section keyword), capped
  at 3 per video, with slide/zoom/fade used sparingly. All 16
  pipelines are implemented as data-driven components in the starter,
  so any pipeline id the planner (or a hand-authored timeline) emits
  renders as-is.
- **v1.3 expansion:** a 3D set (`cube-3d`, `flip-3d`, `parallax-3d` —
  CSS 3D transforms in Remotion, not WebGL; stage-compatible) brings
  the implemented total to 19 pipelines, and 8 genre scene types
  (`news`, `podcast`, `product`, `slideshow`, `quote`, `tutorial`,
  `scoreboard`, `lyrics`) are available via `--genre` (B5). Genre mode
  replaces the middle scenes with the genre's component; the hook and
  the Statement → Recap → CTA ending stay. Hand-authored timelines may
  use any of these ids.
- A learned style's recipe section overrides these defaults.

### B5 — Scaffold the project

**Fast path (default):** run the one-command converter —

```bash
python3 scripts/create_video.py --srt <file.srt> --palette "<tone-or-#hex>" \
    --out <dir> [--aspect 16:9|9:16|1:1] [--title "..."] \
    [--captions <preset>] [--aspects 16:9,9:16] [--voiceover <file>] [--render]
```

It copies `templates/remotion-starter/`, plans the scenes (cue 1 =
Kinetic Hook; middle scenes rotate within ONE layout family chosen
from the SRT's dominant signal — see B4; last three cues of longer
SRTs = Statement → Recap → CTA), resolves the palette through
`scripts/color_palette.py` into `src/theme.ts`, writes
`src/data/timeline.json` (scenes with pipelines + transitions, plus
project-level `family` and `captions`), `timeline.md`,
`src/data/sfx.json` (full-coverage plan, B8) plus the generated
WAVs in `public/sfx/`, and a `PROJECT_README.md`. The starter's `Main` composition is data-driven:
it builds Sequences from `timeline.json` and plays the SFX from
`sfx.json` — so the generated project previews immediately. Customise
the generated project afterwards only where the user's style or a
learned style requires it.

Pro flags on the same command: `--captions <preset-id>` picks one of
the 6 implemented caption presets (`word-by-word` default,
`karaoke-highlight`, `bilingual-stack`, `classic-bottom`, `boxed-bold`,
`minimal-line`); `--aspects 16:9,9:16,1:1` generates one project per
aspect into `<out>/16x9`, `<out>/9x16`, …; `--voiceover <file.mp3|wav>`
copies a real voiceover into each project, probes its duration with
ffprobe and warns when it drifts from the SRT by more than 1 s;
`--render` runs install → render → `qc_check.py` on the first project
and fails loudly, naming the step, if any step fails — never report a
render that did not produce an MP4. `--genre <id>` (v1.3) picks one of
the 8 genre scene types for the middle scenes (`news`, `podcast`,
`product`, `slideshow`, `quote`, `tutorial`, `scoreboard`, `lyrics`;
default `general` = the family planner above) and applies the genre's
default caption preset when `--captions` is not given (news →
classic-bottom, lyrics → karaoke-highlight, podcast → boxed-bold);
when no genre is given but the SRT strongly matches one, the converter
only *suggests* it — it never switches silently. `--sfx-theme
soft|cinematic|playful` (v1.3) flavours the hook accent and the
rotation for unlisted pipelines under the v1.4 coverage table (B8).

**Manual path:** copy `templates/remotion-starter/` yourself and shape
it per `references/remotion-structure.md`: compositions `Main` and
`PreviewAudio` at 1920×1080 / 30 fps, duration computed from the SRT's
last cue end, `theme.ts` carrying the chosen palette, fonts loaded via
`@remotion/google-fonts`. **One font family per video.**

### B6 — Word-by-word text animation

Default treatment: words appear in sync with their cue timing,
animated per `references/animation-library.md` (word scale is the
default; offset 3–6 frames between words). Within a cue, distribute
word onsets evenly across the cue's duration unless word-level
timestamps were supplied. Emphasis words (numbers, names, negations,
the cue's key noun/verb) get the kinetic-emphasis treatment — sparingly,
max 1–2 per cue. Keyword words get companion-accent colouring, and the
karaoke preset's active word pops with a spring scale (~1.12x).

### B7 — Bengali rules

If the SRT language is Bengali (or mixed Bengali/Latin), follow
`references/bengali-text-rules.md` in full: Hind Siliguri by default,
grapheme segmentation, syllable-level animation, `letterSpacing: 0`,
conjunct test set checked before render. No exceptions.

### B8 — SFX implementation

Follow `references/sfx-library.md`: SFX only, **no music track**.
v1.4 **FULL COVERAGE** is a hard expectation — every scene must carry
its matched accent per the coverage table in
`references/sfx-library.md`, every non-cut transition adds its
whoosh-family entry sound, and colliding accents are offset +6 frames;
a silent scene is a defect. Generated or sourced per that reference
and `scripts/sfx_gen.py`. The library has 12 procedurally generated
types (v1.3: + riser, sparkle, ding, shutter, boom-soft),
peak-normalised to −3 dBFS; the converter's `--sfx-theme` (`soft`
default, `cinematic`, `playful`) flavours the hook accent and the
unlisted-pipeline rotation. Every SFX in the timeline (B3) must exist
as a file in `public/sfx/` before rendering.

### B9 — Asset matching

Match each scene only to files that actually exist in `public/`
(images, `voiceover.mp3`, `sfx/`, `assets/`). **Never rename, invent,
or fabricate an asset.** A scene with no matching asset becomes a
text/card scene — that is a design decision the editor makes silently,
not a question for the user.

### B10 — Preview mode (default)

Default delivery is **Preview**: the complete project ZIP plus the
exact commands —

```bash
npm install
npx remotion studio
npx remotion render Main out/video.mp4
```

— per `references/delivery-protocol.md`. Do not render the full video
yourself unless the user asks for a render.

### B11 — Re-render mode

Only when the user asks ("render it", "give me the MP4", or reports
changes after a Preview): apply the requested scene changes, re-render,
and deliver MP4 + updated ZIP per `references/delivery-protocol.md`.
Change only the scenes named; do not restyle the rest.

### B12 — Delivery

Deliver per `references/delivery-protocol.md`: ZIP contents rules,
what to report (duration, scenes, pipelines, palette, SFX count), and
the closing line. Verify before delivering: scene count = cue count,
every timeline SFX file exists, text matches the SRT exactly, and the
project opens in Remotion Studio without errors.

---

## PART C — Style template

`references/style-skill-template.md` is the single source for what a
learned style contains: 12 sections, each with measurable fields. LEARN
fills it (A7); CREATE reads it (B0). Do not invent extra sections in a
learned style, and do not omit sections — write `not measured` where
LEARN could not measure.

## PART D — DOCUMENTARY

Turn one documentary title or topic into a complete 10-minute YouTube
documentary production package, VOX-style paper-collage look, in 10
approval-gated stages. The full, canonical workflow is
`references/master-documentary-prompt.md` (owner-supplied, verbatim) —
read it before starting a documentary project and follow it exactly,
including its exact opening question and its exact stage-closing lines.

The 10 stages: (1) project setup, (2) research and factual foundation,
(3) full ~1,400–1,500-word narration script, (4) script revision gate,
(5) 8-second scene map (~75 scenes), (6) text-to-video prompts in
batches of 10, (7) voiceover direction + music prompt + sound-design
map, (8) YouTube SEO packaging, (9) thumbnail package, (10) final
production checklist.

Rules specific to this mode:

- **One stage at a time.** Never produce two stages together, never
  continue without the user's clear approval ("Approved", "ঠিক আছে",
  "Next", "Proceed"). A revision request redoes only the current stage.
- **Accuracy before drama.** Every factual claim traces to Stage 2
  research; never invent facts, dates, quotes, or sources. If research
  cannot verify something, say so in the package.
- **The deliverable is a package, not a render.** DOCUMENTARY produces
  the script, scene map, and generation prompts. From there the user
  may (a) generate scenes with an external text-to-video tool, or
  (b) hand the approved script back to CREATE: `scripts/make_srt.py`
  turns the script into a timed SRT (or the recorded voiceover into
  one via `scripts/transcribe.py`), and CREATE renders it as a
  motion-graphics video.
- **Never use em dashes** inside documentary deliverables (the master
  prompt's rule): commas, colons, parentheses, or normal hyphens.
- Save each approved stage to disk in the project folder before asking
  for the next approval, so a documentary in progress survives a
  crashed session.

## PART E — 3D EXPLAINER (bundled sub-skill)

For a 3D cartoon "what if" explainer short (9:16, procedural cartoon
people and props, slow-motion impacts, 1–3 word captions timed to a
voiceover), use the bundled sub-skill at `extras/zach-d-films/` —
read its `SKILL.md` and follow it. It is a real Three.js engine
(`extras/zach-d-films/engine/`), NOT one of CREATE's CSS-3D pipelines:
it renders WebGL in headless Chrome via Playwright, at 720×1280,
then upscales to 1080×1920. It ships with a worked example ("Could
ancient armour stop a bullet?", 29.5 s). Word timings come from
`extras/zach-d-films/tools/words.py` (faster-whisper). Bring your own
voiceover; there is no bundled TTS. On a GPU-less machine set
`GL=swiftshader` (renders, but slowly).

## PART F — EDIT (bundled ffmpeg-skill)

For editing an EXISTING video or audio file — trim/cut/join, silence
removal (jump cuts), reframing (16:9 to 9:16 and friends), burned or
muxed captions, overlays, audio cleanup and sync, loudness
normalisation, platform exports (Reels, TikTok, Shorts, YouTube, X,
LinkedIn, Facebook, podcast, audiogram) and delivery checks — use the
bundled ffmpeg-skill at `extras/ffmpeg-skill/`: read its `SKILL.md`
and follow its workflow (probe first, prefer lossless, dry-run plan,
check, verify, never overwrite the source). Its 42 tools run as
`python3 extras/ffmpeg-skill/scripts/<name>.py` with only FFmpeg 6.1+
and Python 3.10+; no cloud, no API keys. EDIT cuts and finishes real
footage; CREATE (Part B) still makes motion graphics from an SRT —
do not use EDIT tools to build a CREATE video or vice versa. Its
`--transcribe` captions need a local speech engine; without one, use
Zobvia's own transcribe.py / make_srt.py to make the SRT first, then
caption.py burns or muxes it. Upstream: kajisho5/ffmpeg-skill, MIT.

## PART G — BLENDER (bundled blender-skill)

For 3D asset work — inspect, convert (glb/gltf/fbx/obj/stl/usd/ply),
optimise (decimate, cap textures), bake maps (AO/normal/roughness),
LOD, thumbnails/turntable/4-view renders, budget checks for
three.js/Unity/Unreal/Godot/iOS-AR/Android-AR/WebXR/3D-print — use
the bundled blender-skill at `extras/blender-skill/`: read its
`SKILL.md` and run `python3 extras/blender-skill/scripts/<name>.py`
(14 tools). It drives a LOCAL headless Blender 4.2+ (`blender -b`);
if Blender is not installed the tools answer with a structured
`missing_tool` error — report that honestly, never fake a result.
Upstream: kajisho5/blender-skill, MIT.

## PART H — AUDIO PRODUCTION (bundled audio-production-skill)

For executing an ALREADY-DECIDED audio operation graph — gain, trim,
cut, silence/filler removal at given timestamps, fades, EBU R128 /
ATSC loudness setting and multi-version delivery, mixing 2–8 tracks
with ducking, stems, mono/stereo/surround downmix, FFT noise
reduction, speech cleanup, format conversion (18 operation types) —
use the bundled audio-production-skill at
`extras/audio-production-skill/`: read its `SKILL.md`; it takes an
`audio-production/request@1` JSON document on stdin and answers with
one response document (`PYTHONPATH=extras/audio-production-skill/src
python3 -m audio_production.cli run - --json`, or `doctor`/`plan`/
`validate`). It delegates measurement and execution to the bundled
ffmpeg-skill (Part F) — set `AUDIO_PRODUCTION_FFMPEG_SKILL_DIR` to
`extras/ffmpeg-skill` when it cannot find it. Deciding WHAT to do
(cut points, targets) stays with you or the user; this engine only
executes and validates. Upstream: kajisho5/audio-production-skill,
MIT.

## PART I — COLOR GRADING (bundled color-grading-skill)

For executing an ALREADY-DECIDED colour treatment — HDR (PQ/HLG) to
SDR BT.709 tone mapping, applying a 3D .cube LUT, rewriting colour
tags without re-encode, stripping a Dolby Vision RPU, typed primary
correction (exposure, contrast, saturation, temperature/tint,
gamma, lift/gain, levels, curves), broadcast-legal soft-clipping
(EBU R 103), camera matching from a named frame pair, and OCIO/ACES
transforms (8 operation types) — use the bundled color-grading-skill
at `extras/color-grading-skill/`: read its `SKILL.md`; same
request/response pattern (`color-grading/request@1` on stdin,
`PYTHONPATH=extras/color-grading-skill/src python3 -m
color_grading.cli run - --json`); set
`COLOR_GRADING_FFMPEG_SKILL_DIR` to `extras/ffmpeg-skill`. Choosing
the look is a human/CREATE decision; this engine applies and
validates it. For a quick one-off grade inside an edit, EDIT's
`color.py` (Part F) is the lighter tool. Upstream:
kajisho5/color-grading-skill, MIT.

## PART J — HYPERFRAMES (bundled hyperframes-skill)

For rendering video from HTML scenes — title cards, lower thirds,
session slates, break screens and stingers from ready templates, or
an already-decided scene description (size, duration, fps, ordered
text/image/video layers) rendered deterministically to MP4/WebM/MOV
— use the bundled hyperframes-skill at `extras/hyperframes-skill/`:
read its `SKILL.md`; run `npm install` there once, then
`node extras/hyperframes-skill/scripts/<name>.mjs` (7 tools: doctor,
template, scene, render, probe, preview, batch). Needs Node >= 22,
FFmpeg >= 5 and a headless Chromium (on this machine set
`HYPERFRAMES_BROWSER_PATH` to the Playwright chromium and `TMPDIR`
to a roomy folder — renders stage frames in temp space). This is a
scene renderer, not an editor: CREATE (Part B) remains the tool for
SRT-driven motion graphics. Upstream: kajisho5/hyperframes-skill,
MIT.

## Hard Rules

1. Measurable numbers over adjectives — in analysis, plans, and reports.
2. Never guess a measurement, colour, duration, or asset. Missing means
   reported missing.
3. Save progress to disk after every batch (frames, analysis, timeline).
4. Learn style only — never reuse a creator's footage, voice, or music.
5. Never invent content that is not in the SRT: no added claims, words,
   captions, or scenes.
6. Never rename or fabricate assets; use only what exists in `public/`,
   exactly as named.
7. CREATE asks exactly one question — colour, in the SRT's language.
   Never a second design question. (DOCUMENTARY mode is the exception:
   it follows its own stage-approval gates, Part D.)
8. SFX only in CREATE output. No music track, ever.
9. One font family per video.
10. Default delivery is Preview (ZIP + commands). Render only on request.
11. Access gate first: on a machine where `scripts/access_check.py`
    reports locked, verify the access password before any LEARN/CREATE
    work (see "Access gate" above). Never bypass it, never store the
    plain password.

## References index

Read these on demand (progressive disclosure) — do not load all of them
up front.

| File | When to read it |
|---|---|
| `references/style-skill-template.md` | LEARN A7; CREATE B0 with a learned style |
| `references/bengali-text-rules.md` | Any Bengali or mixed-language job (A3, B7) |
| `references/sfx-library.md` | LEARN A4; CREATE B8 |
| `references/animation-library.md` | LEARN A2–A3 vocabulary; CREATE B6 |
| `references/style-pipelines.md` | CREATE B4; LEARN A6 naming the look |
| `references/color-system.md` | CREATE B2; LEARN A6 palette sampling |
| `references/remotion-structure.md` | CREATE B5 |
| `references/delivery-protocol.md` | CREATE B10–B12 |
| `references/troubleshooting.md` | Any tool, download, font, or render failure |
| `scripts/check_tools.py` | LEARN A0 |
| `scripts/extract.py` | LEARN A1 |
| `scripts/srt_parse.py` | CREATE B1 |
| `scripts/color_palette.py` | CREATE B2 |
| `scripts/create_video.py` | CREATE B5 fast path — SRT + palette → full data-driven project in one command |
| `scripts/sfx_gen.py` | CREATE B8 |
| `scripts/transcribe.py` | Media → SRT when the user has audio/video but no subtitles (faster-whisper or whisper CLI; exits 3 with install hint when neither exists) |
| `scripts/make_srt.py` | Script text → timed SRT when the user has a typed script but no subtitles (timing proportional to grapheme count, measured from --duration or an --audio file) |
| `scripts/qc_check.py` | After a render (B11/B12): ffprobe check of dimensions / fps / duration / audio |
| `templates/remotion-starter/` | CREATE B5 scaffold source |

### Expanded library (P5)

| File | When to read it |
|---|---|
| `references/platform-specs.md` | Any job: sizes, fps, safe zones, caption rules per platform |
| `references/captions-library.md` | Choosing/building a caption style (14 presets) |
| `references/transitions-library.md` | Transition selection beyond the basics (18) |
| `references/camera-moves.md` | Zooms, pans, parallax and other moves (14) |
| `references/hooks-library.md` | First-3-seconds hook design (18 patterns) |
| `references/cta-outro-library.md` | Endings and calls to action (12 patterns) |
| `references/thumbnail-title.md` | Thumbnail design + title formulas (12) |
| `references/voiceover-workflow.md` | Recording/TTS, cleanup, loudness, VO↔SRT sync |
| `references/music-sfx-sourcing.md` | Licensing-safe music/SFX sourcing and attribution |
| `references/genre-recipes.md` | Genre-first planning (20 recipes) |
| `references/multilingual-typography.md` | Arabic/Urdu RTL, Hindi/Devanagari, mixed scripts |
| `references/export-matrix.md` | Aspect/resolution matrix + per-platform export settings |
| `references/project-workflow.md` | Client-job folder structure and delivery flow |
| `references/qc-checklist.md` | Pre-delivery quality check (always run before delivery) |
| `references/client-brief-template.md` | Starting a client job — copy-paste brief form |
| `references/freelancer-pricing.md` | Pricing/packages guidance (BD + international) |
| `references/prompt-library.md` | Ready prompts that trigger each capability (32) |
| `references/master-create-prompt.md` | The flagship CREATE prompt (owner-supplied, verbatim) — paste into any Claude session with an SRT; runs the full pipeline with one colour question |
| `references/master-documentary-prompt.md` | The flagship DOCUMENTARY prompt (owner-supplied, verbatim) — paste into any Claude session with a documentary title/topic; runs the 10-stage gated documentary package workflow (Part D) |
| `extras/zach-d-films/SKILL.md` | 3D EXPLAINER sub-skill (Part E) — Three.js cartoon explainer shorts; read before any 3D explainer job |
| `extras/ffmpeg-skill/SKILL.md` | EDIT sub-skill (Part F) — 42 FFmpeg tools for editing real footage; read before any EDIT job |
| `extras/blender-skill/SKILL.md` | BLENDER sub-skill (Part G) — headless-Blender 3D asset tools; read before any 3D asset job |
| `extras/audio-production-skill/SKILL.md` | AUDIO PRODUCTION sub-skill (Part H) — typed audio operation graphs; read before any audio-production job |
| `extras/color-grading-skill/SKILL.md` | COLOR GRADING sub-skill (Part I) — typed colour treatments; read before any grading job |
| `extras/hyperframes-skill/SKILL.md` | HYPERFRAMES sub-skill (Part J) — HTML-scene video rendering; read before any HyperFrames job |
