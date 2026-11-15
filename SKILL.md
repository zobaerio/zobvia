---
name: zobvia
description: "Two modes. LEARN: watch a video and extract its editing style into a reusable style skill — use when the user says 'watch this', 'learn this style', 'analyse this video', pastes a video link (YouTube, Shorts, Reels, TikTok) or gives a local video file without an SRT. CREATE: turn an SRT/subtitle file into a Remotion motion-graphics video (1920x1080, 30fps, word-by-word animation, SFX only, full Bengali support) — use when the user says 'make a motion graphics video from this SRT', 'edit in <style> style', pastes or attaches an .srt file, or gives both a video and an SRT (learn the style, then create in it)."
---

# Zobvia

One skill, two jobs: **learn how a video is edited**, and **create a new
video in a learned or built-in style**. Style is learned; footage, voice,
and music are never reused.

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

Run `scripts/extract.py <url-or-path> --slug <slug>`. Outputs land in
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

If download or transcription fails, read
`references/troubleshooting.md` before retrying. Videos over 3 minutes
get the thin pass (wider frame interval) — note that in the analysis.

### A2 — Frame-pair analysis

Read `pairs/` **10 pairs at a time**. For each pair record, in
`references/watch/<slug>/analysis/timeline.md`: what changed across the
cut (subject, scale, angle, background, text), the transition type
(hard cut, zoom, slide, mask, etc. — vocabulary in
`references/animation-library.md`), and the shot duration from
`cuts.json`. Save the file after every batch of 10. Never analyse from
memory of the video; only from the frames on disk.

### A3 — Caption analysis

From `words.json` and the frames, measure: words per caption line,
lines per caption block, words on screen at once, caption position
(% from bottom), font weight/size relative to frame height, highlight
style (colour swap, scale, background box, karaoke fill), and whether
captions are word-by-word, phrase, or full-line. Record numbers, not
impressions.

### A4 — Audio, SFX, and music analysis

From `audio_profile.json` and listening checkpoints at detected events:
classify each recurring sound against the 7 types in
`references/sfx-library.md`, count SFX events per 60 s, note what visual
event each sound is locked to, and record music presence (genre feel,
BPM if measurable, volume relative to voice in dB, where it drops out).
Write the result as an **SFX map** — JSON in
`analysis/sfx-map.json`:

```json
{ "events": [ { "at_sec": 12.4, "type": "soft pop", "locked_to": "word highlight", "gain_db": -18 } ],
  "events_per_60s": 6, "music": { "present": true, "relative_to_voice_db": -14 } }
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

### A8 — Report

Tell the user: style name and slug, the 5–8 headline numbers, hook
type, caption style, SFX density, and the saved path. Offer CREATE
("give me an SRT and I'll cut it in this style") — do not start CREATE
without an SRT.

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
   Never a second design question.
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
