# Changelog

## 1.11.0 — 2026-11-18

### Added
- **The specialist layer: the six remaining kajisho5 ecosystem skills (all MIT) that the BRAIN's registry knows — detection, dubbing, diarization, ingest, artifacts, imagemagick.**
  - **DETECTION (Part T)** — kajisho5/detection-skill v0.2.3 (main @ 43cc556), 10 commands, 39 files. Doctor-verified: document tools (tracks, reframe, speakers, pii) ready; the vision engines (faces/text/objects/shots) are optional installs and report not-ready honestly — no detection run is claimed here.
  - **DUBBING (Part U)** — kajisho5/dubbing-skill v0.2.1 (main @ d886971), 6 commands, 33 files. Doctor/engines verified: it drives local offline TTS engines (Chatterbox, Kokoro class), none bundled or installed here, so no synthesis is claimed; install an engine to enable narrate/dub/describe.
  - **DIARIZATION (Part V)** — kajisho5/diarization-skill v0.3.2 (main @ 6fcb3bb), 6 commands, 25 files. Doctor-verified: assign/check ready; `diarize` needs pyannote.audio (not installed here).
  - **INGEST (Part W)** — kajisho5/ingest-skill v0.1.0 (main @ 38f2c29), 4 commands, 16 files. Verified end-to-end: doctor ok, and an offload of a real clip completed with sha256 verification and a card manifest.
  - **ARTIFACTS (Part X)** — kajisho5/artifacts-skill v0.4.0 (main @ ae039d3), 7 commands, 71 files. Verified: doctor runs; `inspect` produced a full structural report (hash, dimensions, format) for a real PNG.
  - **IMAGEMAGICK (Part Y)** — kajisho5/imagemagick-skill v0.10.0 (main @ ab89bf9), 21 tools, 31 files. Doctor-verified only: the `magick` binary is not installed on the build machine (and could not be installed there), so no image operation is claimed — the tools report the missing binary honestly.
- Capability index: 431 -> **485** named items (+10 detection, +6 dubbing, +6 diarization, +4 ingest, +7 artifacts, +21 imagemagick).


## 1.10.0 — 2026-11-18

### Added
- **Tier 1 complete: the remaining six kajisho5 ecosystem skills (all MIT), so the BRAIN (Part K) now has its full measurement/QC/subtitle/transcription/editing/graphics layer.**
  - **MEDIA ANALYSIS (Part N)** — kajisho5/media-analysis-skill v0.1.19 (main @ bec48a9), 14 tools, 41 files. Verified: doctor ok; loudness and scene_detection analyses returned ok on real clips. NOT bundled: the two binary ONNX models (yamnet_patches.onnx ~7.5 MB, silero_vad_16k_op15.onnx ~1.3 MB — text-only channel); the vad and audio_events analyzers need them copied in from upstream, everything else works without them.
  - **QC (Part O)** — kajisho5/qc-skill v1.4.0 (main @ 9c61ed7), 3 tools / 72 checks, 37 files. Verified: doctor AVAILABLE; a `check` operation on a rendered MP4 completed with a per-check report.
  - **SUBTITLE (Part P)** — kajisho5/subtitle-skill v0.10.0 (main @ c1d699d), 4 tools, 34 files. Verified: doctor healthy against the bundled ffmpeg-skill; `generate` wrote a correct SRT from a decided cue document.
  - **TRANSCRIPTION (Part Q)** — kajisho5/transcription-skill v0.13.0 (main @ d8ad0bf), 7 tools, 50 files. Verified: doctor ok when run under a python with faster-whisper installed (engines and cached tiny/small/medium models reported AVAILABLE), and a transcribe run completed and wrote its transcript JSON. Honest caveat: on the synthetic Bengali promo voice the small model's output hallucinated — the pipeline is proven, recognition quality is content-dependent and must be spot-checked (the skill itself never invents speech labels; the ASR model is the limit).
  - **VIDEO EDITING (Part R)** — kajisho5/video-editing-skill v0.8.0 (main @ c473780), 15 operation types, 25 files. Verified: doctor ok; a TRIM graph executed end-to-end into a real output file.
  - **MOTION GRAPHICS (Part S)** — kajisho5/motion-graphics-skill v0.4.0 (main @ f9aecfe), 15 element types, 25 files. Verified: doctor ok; a title element rendered over real footage and visually confirmed.
- Capability index: 373 -> **431** named items (+14 analysis tools, +3 QC tools, +4 subtitle tools, +7 transcription tools, +15 editing operations, +15 graphics element types).


## 1.9.0 — 2026-11-18

### Added
- **The owner's Top-3 picks from the kajisho5 ecosystem (all MIT): the Brain, the Remotion bridge, and Thumbnails.**
  - **BRAIN (Part K)** — kajisho5/video-production-agent v0.1.0 (main @ 7162c69) at `extras/video-production-agent/`: the ecosystem's orchestrator. The chat model reasons; the agent plans, validates, gates on human approval and records provenance, driving the bundled execution skills through the `video-agent` CLI (24 commands). Bundled: SKILL.md, CLAUDE.md, src/, schemas/, profiles/, tools/, pyproject.toml, LICENSE (209 files). Verified here: `doctor` (ffmpeg/encoders/filters AVAILABLE), `skills` (found the bundled ffmpeg-skill 21/21 tools, audio-production v1.3.2 and color-grading v1.1.0 as AVAILABLE; unbundled siblings honestly UNAVAILABLE), and an `analyze` run on a real 54 s promo (probe + silence + loudness observations recorded, -13.9 LUFS). Young software (0.1.x) — its approval gates stay on.
  - **REMOTION (Part L)** — kajisho5/remotion-ffmpeg-skill v0.14.0 (main @ e34a10d) at `extras/remotion-ffmpeg-skill/`: motion graphics over real footage, driven by ffmpeg-skill measurements — 9 compositions (Captioned, Jumpcut, PeakPulse, Titled, Highlights, BeatMontage, Karaoke, Pip, Emphasis) + 7 tools. Bundled: SKILL.md, AGENTS.md, scripts/, templates/, references/, cli/, package.json, LICENSE (39 files). Verified end-to-end here: doctor all-ok (it auto-located the bundled ffmpeg-skill), init + npm install, analyze of a 10 s clip with an SRT into a measured timeline, and a Captioned render — verified 1920x1080 / 30 fps / 10.13 s with the animated captions visible on the tool's own contact sheet.
  - **THUMBNAIL (Part M)** — kajisho5/thumbnail-skill v0.1.18 (main @ d063550) at `extras/thumbnail-skill/`: renders caller-decided thumbnails (still or exact video timestamp + text + layout) to PNG/JPEG with provenance — 9 tools including batch, variants and layers. Bundled: SKILL.md, src/, pyproject.toml, LICENSE (23 files). Verified here: doctor ok, and a real 1280x720 thumbnail rendered from a promo frame + title text and visually checked. Needs Pillow.
- Capability index: 324 -> **373** named items (+24 agent commands, +16 Remotion compositions/tools, +9 thumbnail tools).


## 1.8.0 — 2026-11-18

### Added
- **Four more bundled sub-skills from the kajisho5 ecosystem (all MIT), at the owner's request** — the same author as the ffmpeg-skill bundled in 1.7.0, designed to work together:
  - **BLENDER (Part G)** — kajisho5/blender-skill v0.31.0 (main @ fad904d) at `extras/blender-skill/`: 14 host tools driving a local headless Blender 4.2+ to inspect, convert, optimise, bake, LOD and render 3D assets (glb/fbx/obj/stl/usd/.blend) and check them against engine/AR/print budgets. Bundled: SKILL.md, scripts/, references/, LICENSE (41 files). Host CLIs verified here (compile, help, structured missing_tool error); the 3D operations themselves need a Blender binary, which this machine does not have — stated honestly, not faked.
  - **AUDIO PRODUCTION (Part H)** — kajisho5/audio-production-skill v1.3.2 (main @ d179cac) at `extras/audio-production-skill/`: 18 typed audio operations (gain, trim/cut, silence/filler removal, fades, loudness set + multi-version delivery, mix with ducking, stems, downmix, noise reduction, voice cleanup, conversion) executed as validated request/response JSON graphs via the bundled ffmpeg-skill. Bundled: SKILL.md, src/, pyproject.toml, LICENSE (17 files). Verified end-to-end here: doctor ok against the bundled ffmpeg-skill, and a GAIN operation executed on a real WAV with full provenance.
  - **COLOR GRADING (Part I)** — kajisho5/color-grading-skill v1.1.0 (main @ 0ddeaac) at `extras/color-grading-skill/`: 8 typed colour operations (HDR to SDR tone mapping, .cube LUT apply, retag, strip Dolby Vision RPU, primary correction, broadcast legalize, camera match, OCIO/ACES transform). Bundled: SKILL.md, src/, pyproject.toml, LICENSE (17 files; upstream assets/ held only a logo and was not bundled). Verified end-to-end here: a PRIMARY_CORRECTION (exposure/saturation) rendered a graded MP4 via the bundled ffmpeg-skill.
  - **HYPERFRAMES (Part J)** — kajisho5/hyperframes-skill v0.10.0 (main @ 193f84d) at `extras/hyperframes-skill/`: 7 Node tools rendering HTML scenes to video (9 templates: title cards, lower thirds, slates, break screens, stingers). Bundled: SKILL.md, scripts/, lib/, templates/, references/, bin/, package.json + lock, LICENSE (49 files). Verified end-to-end here: npm install, doctor fully ok (with TMPDIR on a roomy disk and HYPERFRAMES_BROWSER_PATH pointing at the Playwright Chromium), and a template -> scene -> render run produced a verified 1920x1080 / 30 fps / 2 s MP4.
- Capability index: 277 -> **324** named items (+14 Blender tools, +18 audio operations, +8 grading operations, +7 HyperFrames tools).


## 1.7.0 — 2026-11-17

### Added
- **EDIT mode (Part F)** — the owner asked to add [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) (v3.10.1, main @ f1c97cb, MIT License). It is bundled at `extras/ffmpeg-skill/` (SKILL.md + `scripts/` + `references/` + `templates/` + LICENSE, 82 files) and wired into SKILL.md as the EDIT mode: 42 local FFmpeg tools for editing REAL footage — cut/join, silence removal and filler-word cuts, fit/reframe/crop, captions (burn, mux, karaoke), overlays and graphics, colour (HDR to SDR, LUTs), audio cleanup/sync/ducking, loudness versions, platform exports (tiktok, reels, shorts, youtube, x, linkedin, facebook, podcast, audiogram templates), delivery checks and before/after reports. Pure Python stdlib; needs FFmpeg 6.1+ and Python 3.10+; no cloud, no API keys. Not bundled: the upstream docs site, demos, tests and npm/MCP packaging (the tools run standalone). Verified on FFmpeg 8.1.2: `doctor` reports 86 capabilities, 0 required missing; a probe -> cut -> loudness -> check chain on a real Zobvia promo clip passed all 13 YouTube checks (loudness exactly -14.0 LUFS). EDIT complements CREATE: CREATE builds motion graphics from an SRT, EDIT cuts and finishes existing footage.
- Capability index: 235 -> **277** named items (+42 EDIT tools).


## 1.6.0 — 2026-11-17

Three owner-supplied additions: a documentary mode, a stronger LEARN, and a real-3D explainer.

### Added
- **DOCUMENTARY mode (Part D).** The owner's VOX-style documentary Master Prompt, saved verbatim as `references/master-documentary-prompt.md` and wired into SKILL.md: a title/topic becomes a complete 10-minute documentary production package in 10 approval-gated stages (research, ~1,450-word script, 75 x 8-second scene map, text-to-video prompts, voice/music/sound package, YouTube SEO packaging, thumbnail package, production checklist). Its stage gates replace CREATE's one-question rule inside documentary projects; the approved script can flow back into CREATE via make_srt/transcribe.
- **3D EXPLAINER sub-skill (Part E)** at `extras/zach-d-films/`: a real Three.js cartoon explainer engine (procedural poseable humans, props with slow-motion impacts and the red force-ripple, bloom/DOF, 9:16), shared by the owner (zach-d-films skill, with its worked 29.5 s armour-vs-bullet example). The original depended on an external "kit" that was not shared; Zobvia's bundle is self-contained: `engine/package.json` (three, @fontsource/montserrat, playwright), `tools/words.py` (faster-whisper word timings feeding the original captions.py), and `CHROME_PATH` support in render.mjs. No bundled TTS (bring your own voice). Verified on a GPU-less Linux VM with GL=swiftshader: stills and a short video render of the example.

### Changed
- **LEARN strengthened with the owner's "watch" skill methods:** per-pair note taxonomy (shot type, framing, exact on-screen text, overlays, colour look), caption lead/lag + casing + punctuation + dwell measurements, voice pace and jump-cut detection, SFX search keywords in the SFX map, dense-first-60-seconds + windowed re-runs for long videos, a CLAUDE.md "Learned styles" index line, and the same-name style rule (ask, or save as -v2). Also fixed: A1 documented `--slug`, but extract.py takes `--name`.
- Capability index: 217 -> **235** named items (+10 documentary stages, +8 3D explainer pieces). Reference files: 27 -> 28.


## 1.5.1 — 2026-11-16

Bug fix: a .wav voiceover could silently render with no voice at all.

### Fixed
- **.wav voiceovers now play.** `create_video.py` previously flipped `HAS_VOICEOVER` only for .mp3 voiceovers, and `Main.tsx` hardcoded `voiceover.mp3` — so a project generated with a .wav voiceover rendered SFX-only while looking successful. The converter now flips `HAS_VOICEOVER` for both formats and records the copied file's name in a new `VOICEOVER_FILE` export in `src/timing.ts`, which `PreviewAudio` plays via `staticFile(VOICEOVER_FILE)`. Covered by a regression test (the .wav drift test now asserts the flag, the file name, and the Main.tsx wiring), and verified end-to-end with a partial render whose audio carries the speech.

## 1.5.0 — 2026-11-16

### Added
- **Glass Showcase scene** (`glass-showcase`): animated mesh-gradient background with frosted-glass tiles carrying chunks of the cue's own text — the premium glassmorphism promo look. Joins the stage rotation with a sparkle entry sound. Style pipelines: 19 → **20**; named capability items: 216 → **217**.

## 1.4.0 — 2026-11-15

Multi-colour text, full-coverage sound, and an interactivity layer — every scene now carries colour and sound, with no scene left silent or single-accent.

### Added
- **Multi-colour text system.** `scripts/color_palette.py` gives every tone `accent2` + `accent3` companions (analogous/triadic picks), each passed through `ensure_contrast()` so it is ≥ 4.5:1 WCAG AA against the tone's scene background (darkest swatch); custom `#hex` accents get hue-rotated companions (+36°, +150°), also contrast-ensured. `theme.ts` (starter + generated) carries `accent2`/`accent3`. Headline colour rotates [accent, accent2, accent3] by scene position via a `sceneAccent()` helper in `theme.ts`, consumed through a `SceneMetaContext` (provided by `Main.tsx`) by `SceneShell` (kicker colour) and `WordByWord` (headline base colour). Body text stays `fg`.
- **Keyword colouring.** In `WordByWord` and the karaoke-highlight caption preset, "important" words — containing a number (ASCII or Bengali digits), Latin-script words (brands/terms), and the first content word of the cue — get the companion accent (`accent2`; in `WordByWord` the next accent in the scene rotation). Grapheme-safe, `letterSpacing: 0`. Karaoke's active word keeps the primary accent and now gets a spring scale pop (~1.12x with overshoot) instead of a static scale.
- **Full SFX coverage.** `create_video.py` `plan_sfx` now sounds every scene: each scene gets exactly one scene-entry accent by pipeline (hook = theme-flavoured soft pop / cinematic boom-soft / playful sparkle; glass-cards/bento/flip-3d = pop; carousel-3d/cube-3d/parallax-3d = whoosh; dashboard/scoreboard/news = ding; statement/quote = thud; tutorial = click; slideshow = shutter; lyrics/podcast = pluck; recap = sparkle; cta = chime), unlisted pipelines rotate the theme's middle set, and every non-cut transition adds a whoosh-family entry sound (whip→swipe, zoom→riser, slide→whoosh, fade→swipe). When a transition sound and the accent collide at a scene's first frame, the accent is offset +6 frames. Total events = scenes + non-cut transitions; the 10-cue Bengali example yields 11 events with every scene covered. `sfx.json` events now carry `file`, `sound`, `atSeconds`, `sceneIndex`, `scene`, `durationSeconds`, `kind` (`accent`|`transition`); `Main.tsx` sizes each SFX sequence from `durationSeconds` so long sounds (riser 0.8s, ding 0.6s, boom-soft 0.7s) are no longer truncated by the old fixed 0.5s cap. `timeline.md` and `PROJECT_README.md` report "N scenes → M SFX events, every scene covered".
- **Interactivity layer.** ProgressBar component (Main-level): 6px bottom track, accent→accent2→accent3 gradient fill across the whole video, a dot at each scene boundary; captions sit above it (bottom offset 64*scale), no collision. Scene counter chip "N / total" top-right inside `SceneShell`, low opacity (0.55), `accentSoft` pill.

### Changed
- `plan_sfx` replaces the old 5–7-event role plan with the full-coverage mapping above; the `references/sfx-library.md` density rule (5–7 per 60 s) now scopes to extra within-scene hits in hand-authored timelines only.
- Honest note: for the playful tone (mid-purple scene background) the WCAG guarantee forces its companion accents to very dark shades — contrast-valid, hue-shifted; all other tones keep bright companions.
- Tests: 34 → **38**; named capability items: 210 → **216** (+6 = multi-colour accent system, keyword colouring, karaoke spring pop, full-coverage SFX mapping, progress bar, scene counter chip). SFX types unchanged at 12.

## 1.3.0 — 2026-11-15

More video kinds, a 3D set, an animation kit, and sound v2.

### Added
- **Sound v2 — 12 SFX types.** `scripts/sfx_gen.py` gains `riser`
  (0.8 s rising sweep), `sparkle` (0.5 s twinkle arpeggio), `ding`
  (0.6 s bell), `shutter` (0.15 s camera-click pair) and `boom-soft`
  (0.7 s soft cinematic low hit). Quality pass on all 12: ADSR-style
  envelopes, added harmonic content, a micro fade at the file edges,
  and peak normalisation to **−3 dBFS** — no clipping, consistent
  loudness (the test suite checks every WAV's duration and peak).
  `references/sfx-library.md` documents all 12 with recipes, an event
  mapping for the new types, and a sound-design section (themes,
  voice-first rule, −3 dB peak rule). Still **SFX only, no music**.
- **SFX themes** in the converter: `--sfx-theme soft|cinematic|playful`
  (default `soft`) changes which types voice the 5–7 events —
  cinematic leans on riser / boom-soft / whoosh / thud, playful on
  pop / sparkle / ding / pluck. Recorded in `timeline.json`.
- **3D set — 3 new pipelines** (`cube-3d`, `flip-3d`, `parallax-3d`):
  a rotating cube carrying the cue's chunks on its faces, a card flip
  revealing the cue's second half, and a three-layer parallax stage.
  Implemented with **CSS 3D transforms inside Remotion** (perspective,
  preserve-3d, translateZ) — honestly labelled: this is **not**
  Three.js/WebGL. Implemented pipelines: 16 core + 3 expansion = **19**.
- **8 genre video types** via `--genre news|podcast|product|
  slideshow|quote|tutorial|scoreboard|lyrics`: dedicated data-driven
  scenes (news banner + lower-third, podcast discs + waveform,
  product hero panel, Ken Burns slideshow panel, quote typography,
  numbered tutorial steps, sports scoreboard, lyrics lines). Middle
  scenes use the genre component; the hook and Statement → Recap →
  CTA ending stay. Each genre applies its default caption preset
  when `--captions` is not given (news → classic-bottom, lyrics →
  karaoke-highlight, podcast → boxed-bold). Without `--genre`, a
  strong keyword match only prints a suggestion — never a silent
  switch. Product and scoreboard scenes show **only numbers/prices
  written in the cue itself** — nothing is invented. The slideshow
  scene animates a themed gradient panel (Ken Burns), not photos;
  real images from `public/` slot into hand-authored timelines.
- **Animation kit** (`src/components/anim.tsx`): 8 reusable,
  frame-driven helpers — FadeUp, SpringPop, BlurIn, CounterUp,
  DrawLine, ShineText, FloatY, GlitchSlice — grapheme-safe (whole
  clusters only, `letterSpacing: 0`), used inside the new scenes.

### Verification
Tests 34/34 (7 new: 12-type SFX durations + peak levels, genre scene
planning + caption defaults, invalid genre/theme exit 2, cinematic
theme placement, 3D/genre registration, recorded defaults). Real
converter runs: `--genre news` (English example), `--genre podcast
--aspect 9:16` (Bengali example), `--sfx-theme cinematic` (riser +
boom-soft in the SFX map). `tsc --noEmit` passes in the starter and
in a generated project. Still unverified, unchanged from 1.2.0: a
live end-to-end render on this machine (sandbox proxy blocks Google
Fonts for headless Chromium) and live Whisper transcription (no
backend installed here; only the exit-3 degradation is exercised).

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
