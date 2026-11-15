#!/usr/bin/env python3
"""create_video.py — the one-command SRT → Remotion project converter.

Usage:
    python3 scripts/create_video.py --srt <file.srt> --palette "<tone|#hex>" \
        --out <dir> [--aspect 16:9|9:16|1:1 | --aspects 16:9,9:16,1:1] \
        [--title "..."] [--captions <preset-id>] [--genre <genre>] \
        [--sfx-theme <theme>] \
        [--voiceover <file.mp3|file.wav>] [--render]

What it does (deterministically — same input, same plan):
  1. Parses the SRT with srt_parse.parse_srt (zero cues -> exit 2).
  2. Plans scenes with a family-based planner: cue 1 = Kinetic Hook;
     when there are >= 6 cues, the last three cues are Statement Card ->
     Recap Grid -> CTA; shorter SRTs (2-5 cues) end with a single CTA
     cue; a single cue is hook only. The remaining middle cues are
     assigned inside ONE layout family chosen from the middle cues:
       - Count middle cues containing a number (NUMBER_RE) = num_count
         and containing a step word (STEP_WORDS) = step_count.
       - If middles exist and step_count >= num_count and
         step_count * 2 >= len(middles) -> "flow".
       - Elif num_count > 0 and num_count * 2 >= len(middles) -> "grid".
       - Else -> "stage".
     Within-family assignment:
       - grid: number cue -> dashboard, else bento
         (family middles rotate [bento, dashboard]).
       - flow: step-word cue -> timeline, else hub-spoke
         (family middles rotate [timeline, hub-spoke]).
       - stage: rotate through [glossy-ui, carousel-3d, glass-cards,
         minimal-clean, gradient-fluid]; a cue with >= 2 commas
         (list-like) -> carousel-3d and does not advance the rotation.
     The free family (dark-tech / before-after / flat-vector /
     line-draw) is not auto-selected by the planner; those pipelines
     remain available to hand-authored timelines.
     Every scene also gains a "transition": scene 0 is "none"; a topic
     change (gap >= 1.5s from the previous cue, or a section keyword)
     is "whip" (at most 3 per video, further topic changes are
     "zoom"); otherwise a pipeline change at 0-based index % 6 == 5
     cycles slide/zoom/fade; everything else is "cut".
  3. Copies templates/remotion-starter/ into --out (no node_modules/out),
     then writes src/data/timeline.json (with top-level "family",
     "captions", "genre" and "sfxTheme", plus "voiceover" when
     --voiceover is given),
     src/theme.ts (palette resolved through color_palette.py,
     WCAG-checked, including the v1.4 accent2/accent3 companions),
     timeline.md (with a Transition column),
     public/sfx/*.wav + src/data/sfx.json (full-coverage SFX: one
     matched accent per scene plus a whoosh-family sound on every
     non-cut transition, generated with sfx_gen.py's generators), and
     PROJECT_README.md with the 3 delivery commands.

Extra flags:
  --captions <preset-id>  One of: word-by-word,
      karaoke-highlight, bilingual-stack, classic-bottom, boxed-bold,
      minimal-line. Invalid -> exit 2. Recorded in timeline.json and
      PROJECT_README.md. Default is resolved: an explicit flag wins;
      else the genre default when --genre is not "general" (news ->
      classic-bottom, lyrics -> karaoke-highlight, podcast ->
      boxed-bold, other genres -> word-by-word); else word-by-word.
  --genre <genre>         One of: general (default), news, podcast,
      product, slideshow, quote, tutorial, scoreboard, lyrics.
      Invalid -> exit 2. When not "general", every middle scene uses
      the genre id as its pipeline (hook and the statement/recap/cta
      ending are unchanged); the family is still computed from the
      SRT as usual. Recorded as "genre" in timeline.json. When
      omitted / "general", a keyword-based suggestion may be printed
      (never auto-applied).
  --sfx-theme <theme>     One of: soft (default), cinematic, playful.
      Invalid -> exit 2. Flavours the hook accent and the rotation
      used for pipelines without a fixed accent in plan_sfx's
      coverage table. Recorded as "sfxTheme" in timeline.json.
  --aspect / --aspects    Mutually exclusive. --aspect keeps the
      single-project output at --out itself (effective default 16:9).
      --aspects takes a comma-separated subset of 16:9,9:16,1:1 and
      generates one project per aspect into subdirectories of --out
      named with ":" replaced by "x" (e.g. <out>/16x9).
  --voiceover <file>      .mp3 or .wav only (else exit 2). Copied into
      each generated project's public/ as voiceover.mp3 / voiceover.wav.
      For .mp3, HAS_VOICEOVER is flipped to true in src/timing.ts.
      Duration is probed with ffprobe and compared with the SRT total;
      a drift > 1.0s prints a "WARNING: voiceover duration" line.
  --render                After generation, render the FIRST generated
      project only: "npm install", then "npx remotion render Main
      out/video.mp4", then a qc_check.py pass. Any step failure prints
      "RENDER FAILED at step: <step> — <reason>" to stderr and exits 1.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import color_palette
import sfx_gen
import srt_parse

FPS = 30
ASPECTS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
}

STARTER = Path(__file__).resolve().parent.parent / "templates" / "remotion-starter"
SCRIPTS_DIR = Path(__file__).resolve().parent

# Pipeline ids — must match the component map in the starter's Main.tsx.
HOOK = "kinetic-hook"
GLOSSY_UI = "glossy-ui"
CAROUSEL_3D = "carousel-3d"
DARK_TECH = "dark-tech"
GLASS_CARDS = "glass-cards"
MINIMAL_CLEAN = "minimal-clean"
GRADIENT_FLUID = "gradient-fluid"
STATEMENT = "statement"
BENTO = "bento"
DASHBOARD = "dashboard"
RECAP = "recap"
TIMELINE = "timeline"
HUB_SPOKE = "hub-spoke"
BEFORE_AFTER = "before-after"
FLAT_VECTOR = "flat-vector"
LINE_DRAW = "line-draw"
CTA = "cta"

# Layout families (see references/style-pipelines.md). The planner
# auto-selects grid / stage / flow only. The "free" family
# (dark-tech / before-after / flat-vector / line-draw) is NOT
# auto-selected by the planner; those pipelines remain available to
# hand-authored timelines.
GRID_MIDDLES = [BENTO, DASHBOARD]
STAGE_ROTATION = [GLOSSY_UI, CAROUSEL_3D, GLASS_CARDS, MINIMAL_CLEAN, GRADIENT_FLUID]
FLOW_MIDDLES = [TIMELINE, HUB_SPOKE]
FREE_FAMILY = [DARK_TECH, BEFORE_AFTER, FLAT_VECTOR, LINE_DRAW]

# Backwards-compatible alias (previous rotation list).
MIDDLE_ROTATION = [BENTO, DASHBOARD, TIMELINE]

NUMBER_RE = re.compile(r"[0-9\u09e6-\u09ef]")  # ASCII + Bengali digits
STEP_WORDS = (
    "first", "then", "next", "finally", "step",
    "প্রথমে", "তারপর", "এরপর", "শেষে", "ধাপ",
)

SECTION_KEYWORDS = (
    "chapter", "section", "part ", "next part",
    "এবার", "অধ্যায়", "পরের অংশ",
)

TRANSITION_CYCLE = ["slide", "zoom", "fade"]

CAPTION_PRESETS = [
    "word-by-word",
    "karaoke-highlight",
    "bilingual-stack",
    "classic-bottom",
    "boxed-bold",
    "minimal-line",
]

# SFX coverage (v1.4) — every scene gets a matched sound; see the
# coverage table in references/sfx-library.md. Two layers per scene:
# a transition sound at the scene entry (whoosh family, driven by the
# scene's transition type) and a scene-entry accent chosen by pipeline.
# Pipelines not in ACCENT_SFX rotate the theme's middle set.
SFX_THEMES = ["soft", "cinematic", "playful"]
THEME_MIDDLE_SFX = {
    "soft": ["pop", "click", "swipe"],
    "cinematic": ["whoosh", "riser", "thud"],
    "playful": ["pop", "ding", "sparkle"],
}
# Backwards-compatible alias for the default (soft) theme.
MIDDLE_SFX = THEME_MIDDLE_SFX["soft"]

# Transition type -> entry sound (cut / none add no transition sound;
# the scene accent below still plays, so no scene is ever silent).
TRANSITION_SFX = {
    "whip": "swipe",
    "zoom": "riser",
    "slide": "whoosh",
    "fade": "swipe",
}

# Pipeline id -> scene-entry accent sound.
ACCENT_SFX = {
    "glass-cards": "pop",
    "bento": "pop",
    "flip-3d": "pop",
    "carousel-3d": "whoosh",
    "cube-3d": "whoosh",
    "parallax-3d": "whoosh",
    "dashboard": "ding",
    "scoreboard": "ding",
    "news": "ding",
    "statement": "thud",
    "quote": "thud",
    "tutorial": "click",
    "slideshow": "shutter",
    "lyrics": "pluck",
    "podcast": "pluck",
    "recap": "sparkle",
    "cta": "chime",
}

# The hook's accent is the one theme-flavoured slot in the table.
HOOK_SFX_BY_THEME = {
    "soft": "pop",
    "cinematic": "boom-soft",
    "playful": "sparkle",
}

# Target durations (seconds) of the 12 generated types — mirrors
# scripts/sfx_gen.py; written into sfx.json so the Remotion side can
# give each <Audio> sequence its full length instead of a fixed cap.
SOUND_DURATIONS = {
    "pop": 0.12, "click": 0.06, "whoosh": 0.40, "pluck": 0.35,
    "chime": 0.40, "swipe": 0.30, "thud": 0.25, "riser": 0.80,
    "sparkle": 0.50, "ding": 0.60, "shutter": 0.15, "boom-soft": 0.70,
}

# When a transition sound and the scene accent would land on the same
# frame, the accent is offset by this many frames.
ACCENT_OFFSET_FRAMES = 6

GENRES = ["general", "news", "podcast", "product", "slideshow", "quote",
          "tutorial", "scoreboard", "lyrics"]
GENRE_IDS = [g for g in GENRES if g != "general"]
GENRE_CAPTION_DEFAULTS = {
    "news": "classic-bottom",
    "lyrics": "karaoke-highlight",
    "podcast": "boxed-bold",
}

GENRE_KEYWORDS = {
    "news": ("breaking", "news", "সংবাদ", "খবর"),
    "scoreboard": ("score", "goal", "match", "গোল", "স্কোর", "খেলা"),
    "product": ("price", "৳", "taka", "টাকা", "buy", "offer", "দাম", "কিনুন"),
    "tutorial": STEP_WORDS,
    "podcast": ("podcast", "episode", "পডকাস্ট"),
    "lyrics": ("song", "lyrics", "গান", "সুর"),
    "quote": ("quote", "উক্তি", "বলেছেন"),
    "slideshow": ("photo", "ছবি", "album", "ভ্রমণ"),
}


# ---------------------------------------------------------------- palettes

def _rgba(hex_value, alpha):
    h = hex_value.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def _pick_text(bg):
    """First light/dark candidate meeting WCAG AA (>= 4.5) on bg, else best."""
    candidates = ["#F5F7FA", "#FFFFFF", "#E2E8F0", "#111827", "#000000"]
    for cand in candidates:
        if color_palette.contrast(cand, bg) >= 4.5:
            return cand
    return max(candidates, key=lambda c: color_palette.contrast(c, bg))


def _pick_muted(bg):
    candidates = ["#9AA7B4", "#94A3B8", "#CBD5E1", "#64748B", "#475569"]
    for cand in candidates:
        if color_palette.contrast(cand, bg) >= 2.5:
            return cand
    return _pick_text(bg)


def _saturation(hex_value):
    h = hex_value.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return max(rgb) - min(rgb)


def resolve_palette(spec):
    """Return a theme dict {bg, fg, accent, accentSoft, muted, label}.

    Accepts a tone name from color_palette.PALETTES or a raw #RRGGBB hex
    (used as the accent on the standard dark background). All returned
    text colours are WCAG-checked against the background: palette
    swatches first, black/white fallbacks when no swatch reaches AA.
    Raises ValueError for an unknown tone / malformed hex.
    """
    spec = (spec or "").strip()
    if spec.startswith("#"):
        hex_value = spec.upper()
        if not re.fullmatch(r"#[0-9A-F]{6}", hex_value):
            raise ValueError(
                f"malformed hex colour '{spec}' — expected #RRGGBB, e.g. #0EA5E9")
        bg = color_palette.DARK_BG
        accent2_cand, accent3_cand = color_palette.harmonious_companions(hex_value)
        return {
            "bg": bg,
            "fg": _pick_text(bg),
            "accent": hex_value,
            "accent2": color_palette.ensure_contrast(accent2_cand, bg),
            "accent3": color_palette.ensure_contrast(accent3_cand, bg),
            "accentSoft": _rgba(hex_value, 0.14),
            "muted": _pick_muted(bg),
            "label": f"custom accent {hex_value}",
        }
    tone = spec.lower()
    if tone not in color_palette.PALETTES:
        valid = ", ".join(sorted(color_palette.PALETTES))
        raise ValueError(
            f"unknown palette '{spec}'. Valid tones: {valid} — or pass a #RRGGBB hex.")
    data = color_palette.build(tone)
    swatches = data["swatches"]
    # Background: the darkest swatch (the starter's scenes are dark-stage).
    bg_swatch = min(
        swatches,
        key=lambda s: color_palette.luminance(color_palette.hex_to_rgb(s["hex"])))
    bg = bg_swatch["hex"]
    rest = [s for s in swatches if s["hex"] != bg]
    # Foreground: highest-contrast remaining swatch if it reaches AA.
    fg_swatch = max(rest, key=lambda s: color_palette.contrast(s["hex"], bg))
    if color_palette.contrast(fg_swatch["hex"], bg) >= 4.5:
        fg = fg_swatch["hex"]
    else:
        fg = _pick_text(bg)
    used = {bg, fg}
    rest = [s for s in swatches if s["hex"] not in used]
    # Accent: most saturated remaining swatch that still reads on bg.
    vivid = [s for s in rest if color_palette.contrast(s["hex"], bg) >= 2.5]
    if vivid:
        accent = max(vivid, key=lambda s: _saturation(s["hex"]))["hex"]
    elif rest:
        accent = max(rest, key=lambda s: color_palette.contrast(s["hex"], bg))["hex"]
    else:
        accent = "#0EA5E9"
    used.add(accent)
    rest = [s for s in swatches if s["hex"] not in used]
    muted = None
    if rest:
        cand = max(rest, key=lambda s: color_palette.contrast(s["hex"], bg))["hex"]
        if color_palette.contrast(cand, bg) >= 2.0:
            muted = cand
    if muted is None:
        muted = _pick_muted(bg)
    return {
        "bg": bg,
        "fg": fg,
        "accent": accent,
        # v1.4 multi-colour system: companions precomputed per tone in
        # color_palette.build(), already WCAG-ensured against this bg
        # (build's scene_background is the same darkest-swatch pick).
        "accent2": data["accent2"],
        "accent3": data["accent3"],
        "accentSoft": _rgba(accent, 0.14),
        "muted": muted,
        "label": f"tone '{tone}'",
    }


# ---------------------------------------------------------------- planning

def plan_scenes(cues, genre="general"):
    """Assign a pipeline and a transition to every cue.

    Returns (scenes, family) where scenes is a list of scene dicts
    (each with "pipeline" and "transition") and family is one of
    "grid", "stage" or "flow".

    When genre != "general", every middle scene's pipeline is the
    genre id (hook and the statement/recap/cta ending are unchanged);
    family is still computed from the SRT signal as described below
    and returned unchanged.

    Family selection (deterministic, from the middle cues only):
      num_count  = middle cues containing a number (NUMBER_RE)
      step_count = middle cues containing a step word (STEP_WORDS)
      - middles exist and step_count >= num_count and
        step_count * 2 >= len(middles) -> "flow"
      - elif num_count > 0 and num_count * 2 >= len(middles) -> "grid"
      - else -> "stage"

    Within-family assignment:
      - grid: number cue -> dashboard, else bento.
      - flow: step-word cue -> timeline, else hub-spoke.
      - stage: rotate through STAGE_ROTATION; a cue with >= 2 commas
        -> carousel-3d and does not advance the rotation.

    Note: the "free" family (dark-tech / before-after / flat-vector /
    line-draw) is not auto-selected here; those pipelines remain
    available to hand-authored timelines.

    Hook / ending are fixed: cue 1 = kinetic-hook; >= 6 cues: last
    three = statement, recap, cta; 2-5 cues: last = cta; 1 cue: hook
    only.

    Transitions: scene 0 = "none"; topic change (gap >= 1.5s or a
    section keyword) = "whip" for at most 3 scenes, further topic
    changes = "zoom"; else a pipeline change at 0-based index
    % 6 == 5 cycles slide/zoom/fade; else "cut".
    """
    n = len(cues)
    pipelines = [None] * n
    pipelines[0] = HOOK
    if n >= 6:
        pipelines[n - 3] = STATEMENT
        pipelines[n - 2] = RECAP
        pipelines[n - 1] = CTA
        middle = list(range(1, n - 3))
    elif n >= 2:
        pipelines[n - 1] = CTA
        middle = list(range(1, n - 1))
    else:
        middle = []

    # --- family selection from the middle cues ---
    num_count = sum(1 for i in middle if NUMBER_RE.search(cues[i]["text"]))
    step_count = sum(
        1 for i in middle
        if any(w in cues[i]["text"].lower() for w in STEP_WORDS))
    if middle and step_count >= num_count and step_count * 2 >= len(middle):
        family = "flow"
    elif num_count > 0 and num_count * 2 >= len(middle):
        family = "grid"
    else:
        family = "stage"

    # --- within-family assignment ---
    if family == "grid":
        for i in middle:
            if NUMBER_RE.search(cues[i]["text"]):
                pipelines[i] = DASHBOARD
            else:
                pipelines[i] = BENTO
    elif family == "flow":
        for i in middle:
            lowered = cues[i]["text"].lower()
            if any(w in lowered for w in STEP_WORDS):
                pipelines[i] = TIMELINE
            else:
                pipelines[i] = HUB_SPOKE
    else:  # stage
        rotation = 0
        for i in middle:
            text = cues[i]["text"]
            if text.count(",") >= 2:
                pipelines[i] = CAROUSEL_3D
            else:
                pipelines[i] = STAGE_ROTATION[rotation % len(STAGE_ROTATION)]
                rotation += 1

    # --- genre override: middles use the genre's dedicated layout ---
    if genre != "general":
        for i in middle:
            pipelines[i] = genre

    scenes = []
    for cue, pipeline in zip(cues, pipelines):
        scenes.append({
            "index": cue["index"],
            "start": cue["start"],
            "end": cue["end"],
            "text": cue["text"],
            "pipeline": pipeline,
        })

    # --- transitions ---
    whip_count = 0
    cycle_idx = 0
    for pos, scene in enumerate(scenes):
        if pos == 0:
            scene["transition"] = "none"
            continue
        cue = cues[pos]
        prev_cue = cues[pos - 1]
        gap = cue["start"] - prev_cue["end"]
        lowered = cue["text"].lower()
        is_topic = gap >= 1.5 or any(kw in lowered for kw in SECTION_KEYWORDS)
        if is_topic:
            if whip_count < 3:
                scene["transition"] = "whip"
                whip_count += 1
            else:
                scene["transition"] = "zoom"
        elif scene["pipeline"] != scenes[pos - 1]["pipeline"] and pos % 6 == 5:
            scene["transition"] = TRANSITION_CYCLE[cycle_idx % len(TRANSITION_CYCLE)]
            cycle_idx += 1
        else:
            scene["transition"] = "cut"
    return scenes, family


def plan_sfx(scenes, theme="soft"):
    """Full-coverage SFX plan (v1.4): no scene is ever silent.

    Every scene gets exactly ONE scene-entry accent chosen by its
    pipeline (ACCENT_SFX; the hook's accent is theme-flavoured via
    HOOK_SFX_BY_THEME; unlisted pipelines rotate the theme's middle
    set). The CTA's accent is the final chime. On top of that, every
    non-cut transition adds its whoosh-family entry sound
    (TRANSITION_SFX) at the scene's first frame; when that would
    collide with the scene's accent, the accent is offset by
    ACCENT_OFFSET_FRAMES frames so both are heard distinctly.

    Total events = scenes + (number of non-cut transitions). The
    10-cue Bengali example (9 cuts + 1 slide) therefore yields
    10 + 1 = 11 events, with every scene index covered.
    """
    if theme not in THEME_MIDDLE_SFX:
        raise ValueError(
            f"unknown sfx theme '{theme}'. Valid themes: {', '.join(SFX_THEMES)}")
    middle_sfx = THEME_MIDDLE_SFX[theme]

    def make_event(sound, at_seconds, scene, kind):
        return {
            "file": f"sfx/{sound}.wav",
            "sound": sound,
            "atSeconds": round(at_seconds, 3),
            "sceneIndex": scene["index"],
            "scene": scene["index"],
            "durationSeconds": SOUND_DURATIONS[sound],
            "kind": kind,
        }

    events = []
    unlisted = 0
    for scene in scenes:
        pipeline = scene["pipeline"]
        if pipeline == HOOK:
            accent = HOOK_SFX_BY_THEME[theme]
        elif pipeline in ACCENT_SFX:
            accent = ACCENT_SFX[pipeline]
        else:
            accent = middle_sfx[unlisted % len(middle_sfx)]
            unlisted += 1
        start = scene["start"]
        transition_sound = TRANSITION_SFX.get(scene.get("transition"))
        accent_at = start
        if transition_sound is not None:
            events.append(
                make_event(transition_sound, start, scene, "transition"))
            accent_at = start + ACCENT_OFFSET_FRAMES / FPS
        events.append(make_event(accent, accent_at, scene, "accent"))
    events.sort(key=lambda e: (e["atSeconds"],
                               0 if e["kind"] == "transition" else 1))
    return events


def suggest_genre(cues):
    """Return the best-matching genre id for cues, or None.

    Counts case-insensitive substring hits of GENRE_KEYWORDS across
    all cue texts; returns the genre with the most hits only when
    that count is >= 2, otherwise None. Ties break in GENRE_KEYWORDS
    order.
    """
    texts = [c.get("text", "").lower() for c in cues]
    best_genre = None
    best_hits = 0
    for genre, keywords in GENRE_KEYWORDS.items():
        hits = 0
        for text in texts:
            for kw in keywords:
                hits += text.count(kw.lower())
        if hits > best_hits:
            best_hits = hits
            best_genre = genre
    if best_genre is not None and best_hits >= 2:
        return best_genre
    return None


# ---------------------------------------------------------------- voiceover

def probe_voiceover_duration(path):
    """Probe duration (seconds, float) with ffprobe, or None.

    ffprobe missing or probe failure -> None plus a printed note
    (not an error).
    """
    if shutil.which("ffprobe") is None:
        print("Note: ffprobe not found; voiceover duration unknown.")
        return None
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(path)],
            capture_output=True, text=True)
    except OSError as e:
        print(f"Note: could not probe voiceover duration ({e}); duration unknown.")
        return None
    if proc.returncode != 0:
        print("Note: ffprobe could not probe voiceover duration; duration unknown.")
        return None
    try:
        data = json.loads(proc.stdout)
        raw = data.get("format", {}).get("duration")
        return round(float(raw), 3) if raw is not None else None
    except (json.JSONDecodeError, ValueError, TypeError):
        print("Note: could not parse ffprobe voiceover duration; duration unknown.")
        return None


# ---------------------------------------------------------------- outputs

def render_theme_ts(theme):
    fg_ratio = color_palette.contrast(theme["fg"], theme["bg"])
    accent_ratio = color_palette.contrast(theme["accent"], theme["bg"])
    accent2_ratio = color_palette.contrast(theme["accent2"], theme["bg"])
    accent3_ratio = color_palette.contrast(theme["accent3"], theme["bg"])
    return f'''/**
 * theme.ts — generated by zobvia scripts/create_video.py
 * Palette: {theme["label"]} (WCAG: fg on bg = {fg_ratio}:1, accent on bg = {accent_ratio}:1,
 * accent2 on bg = {accent2_ratio}:1, accent3 on bg = {accent3_ratio}:1).
 * Regenerate by re-running create_video.py, or edit the values directly.
 */
export interface Theme {{
  /** Page / scene background. */
  bg: string;
  /** Primary text colour. */
  fg: string;
  /** The ONE accent colour for this video (CREATE mode asks only this). */
  accent: string;
  /** Companion accent 2 (v1.4 multi-colour system, WCAG AA on bg). */
  accent2: string;
  /** Companion accent 3 (v1.4 multi-colour system, WCAG AA on bg). */
  accent3: string;
  /** Low-opacity tint of the accent, for tiles / chips / bar fills. */
  accentSoft: string;
  /** Secondary / de-emphasised text. */
  muted: string;
  /** Bengali-safe display font. Never set letterSpacing with it. */
  font: string;
  radius: number;
  gap: number;
}}

export const theme: Theme = {{
  bg: "{theme["bg"]}",
  fg: "{theme["fg"]}",
  accent: "{theme["accent"]}",
  accent2: "{theme["accent2"]}",
  accent3: "{theme["accent3"]}",
  accentSoft: "{theme["accentSoft"]}",
  muted: "{theme["muted"]}",
  font: "Hind Siliguri",
  radius: 24,
  gap: 28,
}};

/**
 * v1.4 multi-colour system: the headline colour rotates through the
 * three accents by scene position (0-based), so consecutive scenes do
 * not all wear the same colour. Body text always stays theme.fg.
 * Consumed by SceneShell (kicker + counter chip) and WordByWord
 * (headline base colour, via SceneMetaContext).
 */
export const SCENE_ACCENTS: string[] = [
  theme.accent,
  theme.accent2,
  theme.accent3,
];

export const sceneAccent = (index: number): string =>
  SCENE_ACCENTS[((index % SCENE_ACCENTS.length) + SCENE_ACCENTS.length) %
    SCENE_ACCENTS.length];
'''


def render_timeline_md(title, scenes, total, theme, aspect, sfx_events,
                       family=None, captions=None, genre=None, sfx_theme=None):
    lines = [
        f"# Timeline — {title}",
        "",
        f"- **Scenes:** {len(scenes)} (one per SRT cue)",
        f"- **Total duration:** {total:.3f} seconds @ {FPS} fps",
        f"- **Aspect:** {aspect}",
        f"- **Palette:** {theme['label']} — bg `{theme['bg']}`, accent `{theme['accent']}`, accent2 `{theme['accent2']}`, accent3 `{theme['accent3']}`",
        f"- **SFX events:** {len(sfx_events)} — {len(scenes)} scenes → {len(sfx_events)} SFX events, every scene covered (SFX only, no music)",
    ]
    if family is not None:
        lines.append(f"- **Family:** {family}")
    if captions is not None:
        lines.append(f"- **Captions:** {captions}")
    if genre is not None:
        lines.append(f"- **Genre:** {genre}")
    if sfx_theme is not None:
        lines.append(f"- **SFX theme:** {sfx_theme}")
    lines += [
        "",
        "| # | Start | End | Pipeline | Transition | Text |",
        "|---|-------|-----|----------|------------|------|",
    ]
    for s in scenes:
        text = s["text"].replace("|", "\\|").replace("\n", "<br>")
        lines.append(
            f"| {s['index']} | {srt_parse.fmt_time(s['start'])} | "
            f"{srt_parse.fmt_time(s['end'])} | {s['pipeline']} | "
            f"{s.get('transition', 'cut')} | {text} |")
    lines += ["", "## SFX map", "",
              "| At | Sound | Kind | File | Scene |",
              "|----|-------|------|------|-------|"]
    for e in sfx_events:
        lines.append(
            f"| {srt_parse.fmt_time(e['atSeconds'])} | {e['sound']} | "
            f"{e['kind']} | `public/{e['file']}` | {e['sceneIndex']} |")
    lines.append("")
    return "\n".join(lines)


def render_project_readme(title, scenes, total, theme, aspect, sfx_events,
                          captions="word-by-word", family=None,
                          voiceover_info=None, genre=None, sfx_theme=None):
    # Voiceover section: detailed when a voiceover was supplied,
    # otherwise the original optional paragraph.
    if voiceover_info is not None:
        vo_file = voiceover_info["file"]
        vo_dur = voiceover_info.get("durationSeconds")
        srt_dur = voiceover_info.get("srtDurationSeconds", total)
        drift = voiceover_info.get("driftSeconds")
        vo_dur_str = f"{vo_dur:.3f} seconds" if vo_dur is not None else "unknown (ffprobe unavailable or probe failed)"
        drift_str = f"{drift:.3f} seconds" if drift is not None else "unknown"
        voiceover_section = (
            f"## Voiceover\n\n"
            f"- **File:** `public/{vo_file}`\n"
            f"- **Duration:** {vo_dur_str}\n"
            f"- **SRT duration:** {srt_dur:.3f} seconds\n"
            f"- **Drift:** {drift_str}\n"
        )
        if drift is not None and abs(drift) > 1.0:
            voiceover_section += (
                f"\nWARNING: voiceover duration differs from SRT duration "
                f"by {abs(drift):.3f} seconds.\n"
            )
        if vo_file.endswith(".wav"):
            voiceover_section += (
                f"\nNote: PreviewAudio plays `voiceover.mp3`, so a .wav "
                f"voiceover should be converted or renamed to "
                f"`voiceover.mp3` by the user before previewing with "
                f"PreviewAudio.\n"
            )
        else:
            voiceover_section += (
                f"\n`HAS_VOICEOVER` has been set to `true` in "
                f"`src/timing.ts` for this project.\n"
            )
    else:
        voiceover_section = (
            "## Voiceover (optional)\n\n"
            "Drop a real recording at `public/voiceover.mp3`, set `HAS_VOICEOVER = true`\n"
            "in `src/timing.ts`, and preview with the `PreviewAudio` composition.\n"
        )
    family_line = f"- **Family:** {family}\n" if family is not None else ""
    genre_line = f"- **Genre:** {genre}\n" if genre is not None else ""
    sfx_theme_line = f"- **SFX theme:** {sfx_theme}\n" if sfx_theme is not None else ""
    return f'''# {title}

A Remotion motion-graphics project generated by **zobvia**
(`scripts/create_video.py`) from an SRT subtitle file.

- **Scenes:** {len(scenes)} (one per SRT cue) — plan in `timeline.md`
- **Duration:** {total:.1f} seconds @ {FPS} fps
- **Aspect / size:** {aspect}
{family_line}{genre_line}{sfx_theme_line}- **Captions:** {captions}
- **Palette:** {theme["label"]} — bg `{theme["bg"]}`, accent `{theme["accent"]}`, accent2 `{theme["accent2"]}`, accent3 `{theme["accent3"]}`
- **SFX:** {len(sfx_events)} generated events in `public/sfx/` — {len(scenes)} scenes → {len(sfx_events)} SFX events, every scene covered (SFX only, no music)
- **Data:** scenes live in `src/data/timeline.json`, sounds in `src/data/sfx.json`

## Run it

```bash
npm install
npx remotion studio
npx remotion render Main out/video.mp4
```

- `npm install` — one-time dependency install.
- `npx remotion studio` — preview and scrub the video in your browser.
- `npx remotion render Main out/video.mp4` — render the final MP4.

{voiceover_section}
## Editing

Change scene text/timing in `src/data/timeline.json`, colours in
`src/theme.ts`, then re-render. Scene layouts live in `src/scenes/`.
'''


# ---------------------------------------------------------------- render

def _render_fail(step, reason):
    print(f"RENDER FAILED at step: {step} — {reason}", file=sys.stderr)
    return 1


def run_render(project_dir, width, height, total):
    """Render one generated project. Returns 0 on success, 1 on failure."""
    # Step: npm install
    print("Render step: npm install")
    if shutil.which("npm") is None:
        return _render_fail("npm install", "npm not found")
    try:
        proc = subprocess.run(
            ["npm", "install"], cwd=str(project_dir),
            capture_output=True, text=True)
    except OSError as e:
        return _render_fail("npm install", str(e))
    if proc.returncode != 0:
        return _render_fail(
            "npm install", f"npm install exited with code {proc.returncode}")

    # Step: remotion render
    print("Render step: remotion render")
    try:
        proc = subprocess.run(
            ["npx", "remotion", "render", "Main", "out/video.mp4"],
            cwd=str(project_dir), capture_output=True, text=True)
    except OSError as e:
        return _render_fail("remotion render", str(e))
    if proc.returncode != 0:
        return _render_fail(
            "remotion render", f"remotion render exited with code {proc.returncode}")
    mp4 = project_dir / "out" / "video.mp4"
    if not mp4.is_file():
        return _render_fail("remotion render", "out/video.mp4 not found after render")

    # Step: qc check
    print("Render step: qc check")
    qc_script = SCRIPTS_DIR / "qc_check.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(qc_script), "--file", str(mp4),
             "--expect-width", str(width), "--expect-height", str(height),
             "--expect-fps", "30", "--expect-duration", str(total)],
            capture_output=True, text=True)
    except OSError as e:
        return _render_fail("qc check", str(e))
    qc_output = (proc.stdout or "").strip()
    if qc_output:
        print(qc_output)
    if proc.returncode != 0:
        reason = f"qc_check exited with code {proc.returncode}"
        if proc.stderr and proc.stderr.strip():
            reason = proc.stderr.strip().splitlines()[-1][:120]
        return _render_fail("qc check", reason)
    # Success only here: MP4 exists and QC passed.
    print(f"Rendered: {mp4}")
    if qc_output:
        # QC summary line = last line of qc output (or full output).
        print(f"QC: {qc_output.splitlines()[-1] if qc_output else 'passed'}")
    else:
        print("QC: passed")
    return 0


# ---------------------------------------------------------------- generation

def generate_project(out_dir, title, scenes, family, captions, total,
                     theme, aspect, width, height, sfx_events,
                     voiceover_info=None, voiceover_src=None,
                     genre="general", sfx_theme="soft"):
    """Write one project into out_dir. Raises OSError on write failure."""
    shutil.copytree(
        STARTER, out_dir, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("node_modules", "out"))
    (out_dir / "src" / "data").mkdir(parents=True, exist_ok=True)
    timeline = {
        "title": title,
        "fps": FPS,
        "width": width,
        "height": height,
        "totalDuration": total,
        "family": family,
        "captions": captions,
        "genre": genre,
        "sfxTheme": sfx_theme,
        "scenes": scenes,
    }
    if voiceover_info is not None:
        timeline["voiceover"] = voiceover_info
    (out_dir / "src" / "data" / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (out_dir / "src" / "data" / "sfx.json").write_text(
        json.dumps({"events": [
            {"file": e["file"], "sound": e["sound"],
             "atSeconds": e["atSeconds"], "sceneIndex": e["sceneIndex"],
             "scene": e["scene"], "durationSeconds": e["durationSeconds"],
             "kind": e["kind"]} for e in sfx_events]},
            ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (out_dir / "src" / "theme.ts").write_text(
        render_theme_ts(theme), encoding="utf-8")
    (out_dir / "timeline.md").write_text(
        render_timeline_md(title, scenes, total, theme, aspect, sfx_events,
                           family=family, captions=captions, genre=genre,
                           sfx_theme=sfx_theme),
        encoding="utf-8")
    (out_dir / "PROJECT_README.md").write_text(
        render_project_readme(title, scenes, total, theme, aspect, sfx_events,
                              captions=captions, family=family,
                              voiceover_info=voiceover_info, genre=genre,
                              sfx_theme=sfx_theme),
        encoding="utf-8")
    sfx_dir = out_dir / "public" / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    gens = sfx_gen.NP_GENS if sfx_gen.HAS_NUMPY else sfx_gen.PY_GENS
    for sound in sorted({e["sound"] for e in sfx_events}):
        samples = sfx_gen.normalise(gens[sound]())
        sfx_gen.write_wav(sfx_dir / f"{sound}.wav", samples)
    # Voiceover copy (+ timing flip for .mp3).
    if voiceover_info is not None and voiceover_src is not None:
        dest = out_dir / "public" / voiceover_info["file"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(voiceover_src), str(dest))
        if voiceover_info["file"] == "voiceover.mp3":
            timing_path = out_dir / "src" / "timing.ts"
            if timing_path.is_file():
                content = timing_path.read_text(encoding="utf-8")
                needle = "export const HAS_VOICEOVER = false;"
                if needle in content:
                    timing_path.write_text(
                        content.replace(
                            needle, "export const HAS_VOICEOVER = true;"),
                        encoding="utf-8")
                else:
                    print("Warning: HAS_VOICEOVER pattern not found in "
                          f"{timing_path}; leaving timing.ts unchanged.")
            else:
                print(f"Warning: timing.ts not found at {timing_path}; "
                      "cannot set HAS_VOICEOVER.")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert an SRT into a ready Remotion project (zobvia CREATE fast path).")
    p.add_argument("--srt", required=True, help="Input .srt file")
    p.add_argument("--palette", required=True,
                   help="Palette tone name (see color_palette.py) or a #RRGGBB hex")
    p.add_argument("--out", required=True, help="Output project directory")
    aspect_group = p.add_mutually_exclusive_group()
    aspect_group.add_argument("--aspect", choices=sorted(ASPECTS), default=None)
    aspect_group.add_argument("--aspects", default=None,
                              help="Comma-separated aspects, e.g. 16:9,9:16")
    p.add_argument("--title", default=None, help="Project title (default: SRT file stem)")
    p.add_argument("--captions", default=None,
                   help="Caption preset id (default: resolved from genre, else word-by-word)")
    p.add_argument("--genre", default="general",
                   help="Genre id (default: general)")
    p.add_argument("--sfx-theme", default="soft", dest="sfx_theme",
                   help="SFX theme: soft, cinematic or playful (default: soft)")
    p.add_argument("--voiceover", default=None,
                   help="Voiceover audio file (.mp3 or .wav)")
    p.add_argument("--render", action="store_true",
                   help="Render the first generated project after generation")
    args = p.parse_args(argv)

    # --- genre validation (exit 2, listing valid ids) ---
    if args.genre not in GENRES:
        print(
            f"Error: invalid genre '{args.genre}'. "
            f"Valid genres: {', '.join(GENRES)}",
            file=sys.stderr)
        return 2

    # --- sfx theme validation (exit 2, listing valid ids) ---
    if args.sfx_theme not in SFX_THEMES:
        print(
            f"Error: invalid sfx theme '{args.sfx_theme}'. "
            f"Valid themes: {', '.join(SFX_THEMES)}",
            file=sys.stderr)
        return 2

    # --- captions validation / resolution (exit 2, listing valid ids) ---
    if args.captions is not None and args.captions not in CAPTION_PRESETS:
        print(
            f"Error: invalid captions preset '{args.captions}'. "
            f"Valid presets: {', '.join(CAPTION_PRESETS)}",
            file=sys.stderr)
        return 2
    if args.captions is not None:
        captions = args.captions
    elif args.genre != "general":
        captions = GENRE_CAPTION_DEFAULTS.get(args.genre, "word-by-word")
    else:
        captions = "word-by-word"

    # --- aspects validation / resolution ---
    if args.aspects is not None:
        aspects_list = [part.strip() for part in args.aspects.split(",")]
        if not aspects_list or any(a not in ASPECTS for a in aspects_list):
            print(
                f"Error: invalid --aspects entry in '{args.aspects}'. "
                f"Valid aspects: {', '.join(sorted(ASPECTS))}",
                file=sys.stderr)
            return 2
        out_base = Path(args.out)
        targets = [(asp, out_base / asp.replace(":", "x")) for asp in aspects_list]
    else:
        effective_aspect = args.aspect if args.aspect is not None else "16:9"
        aspects_list = [effective_aspect]
        targets = [(effective_aspect, Path(args.out))]

    # --- voiceover validation (extension, before generation) ---
    voiceover_src = None
    voiceover_ext = None
    if args.voiceover is not None:
        voiceover_src = Path(args.voiceover)
        voiceover_ext = voiceover_src.suffix.lower()
        if voiceover_ext not in (".mp3", ".wav"):
            print(
                f"Error: voiceover file must be .mp3 or .wav: {voiceover_src}",
                file=sys.stderr)
            return 2
        if not voiceover_src.is_file():
            print(f"Error: voiceover file not found: {voiceover_src}", file=sys.stderr)
            return 2

    srt_path = Path(args.srt)
    if not srt_path.is_file():
        print(f"Error: SRT file not found: {srt_path}", file=sys.stderr)
        return 2
    try:
        text = srt_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error: cannot read {srt_path}: {e}", file=sys.stderr)
        return 2
    data = srt_parse.parse_srt(text)
    if data["cue_count"] == 0:
        print(
            f"Error: no valid SRT cues found in {srt_path} "
            f"({data['warnings']} malformed block(s) skipped). "
            "Check that the file is a real .srt with timestamps like "
            "00:00:01,000 --> 00:00:03,000.",
            file=sys.stderr)
        return 2

    try:
        theme = resolve_palette(args.palette)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if not STARTER.is_dir():
        print(f"Error: Remotion starter not found at {STARTER}", file=sys.stderr)
        return 2

    # Non-empty check applies per target project dir.
    for _asp, target_dir in targets:
        if target_dir.exists() and any(target_dir.iterdir()):
            print(f"Error: output directory is not empty: {target_dir}", file=sys.stderr)
            return 2

    title = args.title or srt_path.stem
    scenes, family = plan_scenes(data["cues"], genre=args.genre)
    total = data["total_duration"]
    sfx_events = plan_sfx(scenes, theme=args.sfx_theme)

    # --- genre auto-suggest (only when genre is general; never auto-switch) ---
    if args.genre == "general":
        suggested = suggest_genre(data["cues"])
        if suggested is not None:
            print(f"Suggestion: this SRT looks like a '{suggested}' video — re-run with --genre {suggested} for its dedicated layout.")

    # --- voiceover probing / info (once) ---
    voiceover_info = None
    if voiceover_src is not None:
        vo_filename = "voiceover.mp3" if voiceover_ext == ".mp3" else "voiceover.wav"
        vo_duration = probe_voiceover_duration(voiceover_src)
        srt_duration = round(float(total), 3)
        if vo_duration is not None:
            drift = round(vo_duration - srt_duration, 3)
        else:
            drift = None
        voiceover_info = {
            "file": vo_filename,
            "durationSeconds": vo_duration,
            "srtDurationSeconds": srt_duration,
            "driftSeconds": drift,
        }
        if vo_filename.endswith(".wav"):
            print("Note: voiceover is .wav — PreviewAudio plays voiceover.mp3, "
                  "so a .wav should be converted or renamed to voiceover.mp3 "
                  "by the user before previewing with PreviewAudio.")
        if vo_duration is not None and abs(drift) > 1.0:
            print(f"WARNING: voiceover duration ({vo_duration:.3f}s) differs from "
                  f"SRT duration ({srt_duration:.3f}s) by {abs(drift):.3f}s.")

    # --- generate one project per target ---
    generated = []  # list of (aspect, out_dir, width, height)
    for aspect, out_dir in targets:
        width, height = ASPECTS[aspect]
        try:
            generate_project(
                out_dir, title, scenes, family, captions, total,
                theme, aspect, width, height, sfx_events,
                voiceover_info=voiceover_info, voiceover_src=voiceover_src,
                genre=args.genre, sfx_theme=args.sfx_theme)
        except OSError as e:
            print(f"Error: cannot write project to {out_dir}: {e}", file=sys.stderr)
            return 2
        generated.append((aspect, out_dir, width, height))
        print(f"Project created: {out_dir}")
        print(f"  Title:   {title}")
        print(f"  Scenes:  {len(scenes)} (one per SRT cue)")
        print(f"  Family:  {family}")
        print(f"  Genre:   {args.genre}")
        print(f"  SFX theme: {args.sfx_theme}")
        print(f"  Captions: {captions}")
        print(f"  Duration: {total:.1f}s @ {FPS} fps")
        print(f"  Aspect:  {aspect} ({width}x{height})")
        print(f"  Palette: {theme['label']} — bg {theme['bg']}, accent {theme['accent']}")
        print(f"  SFX:     {len(sfx_events)} events — {len(scenes)} scenes "
              f"covered, no silent scenes "
              f"({', '.join(sorted({e['sound'] for e in sfx_events}))})")
        if voiceover_info is not None:
            vo_dur = voiceover_info["durationSeconds"]
            vo_dur_str = f"{vo_dur:.3f}s" if vo_dur is not None else "unknown"
            print(f"  Voiceover: {voiceover_info['file']} (duration {vo_dur_str}, "
                  f"SRT {voiceover_info['srtDurationSeconds']:.3f}s, "
                  f"drift {voiceover_info['driftSeconds']})")
            if voiceover_info["file"].endswith(".wav"):
                print("  Note: PreviewAudio plays voiceover.mp3 — convert or "
                      "rename the .wav to voiceover.mp3 before previewing.")
        print("  Next:    npm install && npx remotion studio")

    if args.render:
        first_aspect, first_dir, first_w, first_h = generated[0]
        return run_render(first_dir, first_w, first_h, total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
