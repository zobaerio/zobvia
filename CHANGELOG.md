# Changelog

## 1.2.0 — 2026-11-15

The professional release: every pipeline in code, a family-respecting
planner, coded transitions and captions, and pro converter flags.

### Added
- **All 16 style pipelines implemented as data-driven components** in
  the starter (`src/scenes/`), registered in `Main`'s component map
  (unknown ids still fall back to Statement Card). The 10 new ones:
  Glossy UI Mockup (`glossy-ui`, browser-frame stage), 3D Carousel
  (`carousel-3d`, perspective arc with a cycling hero card), Dark Tech
  (`dark-tech`, grid-lined stage with a terminal panel — a layout, not
  just a theme: the reference defines it as "stage with terminal/code
  panels"; body text stays in the Bengali-safe theme font, no
  monospace), Glass Cards (`glass-cards`, frosted cards over blurred
  colour blobs), Minimal Clean (`minimal-clean`, the light look —
  light surface / dark ink from the theme, one centred element),
  Gradient Fluid (`gradient-fluid`, drifting blurred colour field),
  Hub-and-Spoke (`hub-spoke`, SVG spokes draw on to chunk satellites),
  Before/After Split (`before-after`, the cue's own halves, dim vs
  tinted, divider reveal), Flat Vector/Isometric (`flat-vector`, flat
  primitives + chunk label chips), Line-Draw/Doodle (`line-draw`,
  paper ground, dashed sketch box, draw-on squiggle, ticking sketch
  rows). Content still comes only from the SRT cue in every component.
- **Transitions in code** (`src/components/transitions.tsx`):
  `SceneTransition` wraps each incoming scene per its `transition`
  value — cut/none (untouched), fade, slide, zoom, whip (fast slide
  with a decaying horizontal blur).
- **6 caption presets implemented** (`src/components/CaptionRenderer.tsx`,
  word onsets distributed evenly across the scene, whitespace-only word
  splitting): `word-by-word` (the default — the scenes' built-in
  WordByWord treatment, no overlay), `karaoke-highlight`,
  `bilingual-stack` (the cue's own Bengali-script words on top, Latin
  words below — no translation is invented; single-script cues render
  one line), `classic-bottom`, `boxed-bold`, `minimal-line`.
- **Family planner in `create_video.py`** (SKILL.md B4, enforced):
  one layout family per video, chosen from the middle cues' dominant
  signal — step words → flow (Timeline/Hub-and-Spoke), numbers → grid
  (Dashboard/Bento), otherwise stage (Glossy UI/3D Carousel/Glass
  Cards/Minimal Clean/Gradient Fluid rotation, list-like cues →
  Carousel). The free family (Dark Tech, Before/After, Flat Vector,
  Line-Draw) is not auto-selected; it stays available to
  hand-authored timelines. Every scene gains a `transition` (~80%
  cuts; whip only on topic change — ≥ 1.5 s gap or a section keyword —
  capped at 3, then zoom; slide/zoom/fade sparingly on pipeline
  changes). `timeline.json` gains `family`; `timeline.md` gains a
  Transition column.
- **Converter pro flags:** `--captions <preset-id>` (invalid id exits
  2 listing the valid ids); `--aspects 16:9,9:16,1:1` (one project per
  aspect under `<out>/16x9` etc.; single `--aspect` unchanged);
  `--voiceover <mp3|wav>` (copied into `public/`, ffprobe-probed,
  drift vs the SRT printed as a warning beyond 1 s and recorded in
  `timeline.json`; mp3 flips `HAS_VOICEOVER` on, wav is copied as-is
  with a note that PreviewAudio expects mp3); `--render` (npm install
  → remotion render → `qc_check.py` on the first project; any failure
  exits 1 with `RENDER FAILED at step: <name>` — success is only
  reported when an MP4 exists and QC passes).
- **CI** (`.github/workflows/tests.yml`): Python 3.11 unittest suite +
  Node 20 starter typecheck on push and pull requests.
- **Committed sample output:** `examples/generated-project/` — the
  real output of the converter on `examples/example-bengali.srt`
  (palette tech, 16:9), machine-generated, node_modules excluded.
- Tests: 21 → **27** (24-cue planner family/rotation/transitions,
  captions flag + bad preset, multi-aspect dimensions, voiceover
  drift warning, stubbed `--render` failure naming, demo-timeline
  registration).

### Still unverified (honest list, unchanged in kind)
- A live end-to-end render on this build machine: the sandbox proxy
  still blocks Google Fonts for headless Chromium, so `--render`'s
  plumbing is verified with stubbed tools and its failure reporting
  is exercised for real; the render step itself needs a machine with
  direct font access.
- Live Whisper transcription (no backend on the build machine; the
  exit-3 degradation path is what is tested).

## 1.1.0 — 2026-11-15

The converter release: SRT in → ready Remotion project out, in one command.

### Added
- **`scripts/create_video.py`** — the one-command converter:
  `create_video.py --srt <file> --palette "<tone|#hex>" --out <dir>
  [--aspect 16:9|9:16|1:1] [--title ...]`. Parses via `srt_parse.py`,
  plans scenes (Kinetic Hook → rotating Bento/Dashboard/Timeline middles
  with number/step-word keyword overrides → Statement/Recap/CTA ending
  for SRTs with ≥ 6 cues), resolves the palette via `color_palette.py`
  into `src/theme.ts` (WCAG-checked, black/white fallback when no swatch
  reaches AA against the background), and writes
  `src/data/timeline.json`, `timeline.md`, `src/data/sfx.json`,
  generated SFX WAVs in `public/sfx/` (5–7 events, role-mapped:
  whoosh/thud/pluck/chime + rotating pop/click/swipe) and
  `PROJECT_README.md`. Deterministic; bad SRT or unknown palette exits 2
  with the valid tones listed.
- **Data-driven starter**: `Main` now builds Sequences from
  `src/data/timeline.json` and plays `src/data/sfx.json` events;
  `Root` takes fps/width/height/duration from the JSON. Seven generic
  scene components driven by scene data — `KineticHook`, `BentoScene`,
  `DashboardScene` (counters for numbers in the cue, ASCII + Bengali
  digits, kept in the cue's digit script), `TimelineScene`,
  `StatementCard`, `RecapGrid`, `CTACard` — plus a shared
  `components/chunks.ts` (sentence splitting / word-boundary truncation)
  and a subtle entrance in `SceneShell`. A 9-scene demo `timeline.json`
  ships in the starter so it still compiles and renders standalone;
  `PreviewAudio` behaviour unchanged.
- **`scripts/transcribe.py`** — media → SRT via faster-whisper or the
  `whisper` CLI. With neither backend installed it prints the install
  commands and exits 3 (honest degradation, nothing faked).
- **`scripts/qc_check.py`** — ffprobe QC for rendered videos: reports
  dimensions/fps/duration/audio and PASS/FAILs each expectation given
  (exit 1 on a failed expectation, 3 when ffprobe is missing).
- Examples: `examples/example-bengali.srt` and
  `examples/example-english.srt` (10 cues / 45 s each).

### Verification (2026-11-15, build machine)
- Test suite: **21/21 pass** (`python3 -m unittest discover -s tests`) —
  6 new tests cover the converter (full Bengali run, bad palette,
  9:16 aspect, empty SRT), transcribe's no-backend exit 3, and
  qc_check against a real ffmpeg-generated clip.
- `create_video.py` run for real on both example SRTs: 10 scenes,
  45.0 s, 7 SFX events each (16:9 tech palette; 9:16 premium palette).
- `npx tsc --noEmit` passes in the starter **and** in a
  converter-generated project.

### Still unverified
- Live Whisper transcription (no Whisper backend on the build machine;
  the faster-whisper and whisper-CLI paths are code-complete but were
  only exercised up to the honest exit-3 degradation).
- Still-frame render — unchanged from 1.0.0: headless Chromium on the
  build machine cannot reach Google Fonts through the sandbox proxy.

## Unreleased

- **Access password gate** (owner's decision, 2026-11-15): installing or
  first-running Zobvia asks for a password once per machine — the author's
  GitHub username. Only its SHA-256 hash is stored (`scripts/access_check.py`,
  gate in `install.sh`, rule in `SKILL.md`); a marker at
  `~/.zobvia/access-ok` prevents repeat prompts. 3 new tests (15/15 total).
- **README**: animated demo banner (`assets/demo.svg`, pure SVG/SMIL) and a
  complete step-by-step "How to make a video" guide (install → SRT →
  colour question → preview → changes → render), a Bengali quick guide,
  and an FAQ. Fixed the clone URL to the real repo.
- Renamed the skill from the working title `video-master` to **Zobvia**
  (owner's final name choice, 2026-11-15 — an original coinage from the
  author's name, verified unused by web search before adoption).
  Folder, `SKILL.md` frontmatter name, README, scripts and templates all
  renamed; test suite re-run green (12/12) after the rename.

## 1.0.0 — 2026-11-15

First production release (built locally; GitHub publication pending owner approval).

### Added
- `SKILL.md` — LEARN (A0–A8) + CREATE (B0–B12) pipeline, mode routing, 10 hard rules.
- 9 core references: style template, Bengali text rules, SFX library, animation
  library, 16 style pipelines, colour system, Remotion structure, delivery
  protocol, troubleshooting.
- Expanded library (17 references): platform specs, 14 caption presets,
  18 transitions, 14 camera moves, 18 hooks, 12 CTAs, thumbnail/title,
  voiceover workflow, licensing-safe sourcing, 20 genre recipes,
  multilingual typography (RTL + Devanagari), export matrix, project
  workflow, QC checklist, client brief template, freelancer pricing,
  32-prompt library.
- Scripts (all real, tested): `extract.py` (444 lines, full LEARN engine),
  `srt_parse.py`, `color_palette.py` (WCAG contrast), `sfx_gen.py`
  (numpy + pure-Python fallback), `check_tools.py`, `style_stats.py`,
  `render_helper.sh`.
- `templates/remotion-starter/` — Remotion 4.0.543 starter: Main +
  PreviewAudio compositions, grapheme-safe WordByWord component, 3 demo
  scenes (Hook/Bento/Dashboard), Hind Siliguri loading.
- Examples: Bengali+English SRT → timeline JSON/Markdown generated by
  `srt_parse.py`; filled Dark Tech example style skill.
- `tests/` — 12 unittests covering SRT parsing (incl. Bengali, malformed,
  empty), palettes, and SFX WAV headers/durations.

### Verification log (2026-11-15, build machine)
- Tests: 12/12 pass (`python3 -m unittest discover -s tests`).
- `extract.py` end-to-end on a generated 4 s clip: frames, 1 scene cut,
  frame pairs, audio profile all produced; transcription skipped with the
  reason recorded (Whisper not installed) — never faked.
- Remotion starter: `npm install` OK (248 packages), `tsc --noEmit` PASS.
- Remotion still-frame render: **not verified** on the build machine —
  headless Chromium could not reach fonts.gstatic.com through the sandbox
  proxy (curl to the same URL returned 200). Run
  `npx remotion still Main out/preview.png` on a normal network to confirm.

### Fixed during build
- `srt_parse.py` now exits non-zero with a clear message on an SRT with
  zero valid cues (was: silent empty success). Caught by the test suite.
