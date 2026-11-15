#!/usr/bin/env python3
"""create_video.py — the one-command SRT → Remotion project converter.

Usage:
    python3 scripts/create_video.py --srt <file.srt> --palette "<tone|#hex>" \
        --out <dir> [--aspect 16:9|9:16|1:1] [--title "..."]

What it does (deterministically — same input, same plan):
  1. Parses the SRT with srt_parse.parse_srt (zero cues -> exit 2).
  2. Plans scenes: cue 1 = Kinetic Hook; middle cues rotate through
     Bento / Dashboard / Timeline (a cue whose text contains a number is
     planned as Dashboard, a cue containing a step word — first/then/
     next/finally or প্রথমে/তারপর/এরপর/শেষে — as Timeline; otherwise the
     rotation advances). Never more than 3 distinct middle styles.
     When there are >= 6 cues, the last three cues are Statement Card ->
     Recap Grid -> CTA; shorter SRTs end with a single CTA cue.
  3. Copies templates/remotion-starter/ into --out (no node_modules/out),
     then writes src/data/timeline.json, src/theme.ts (palette resolved
     through color_palette.py, WCAG-checked), timeline.md,
     public/sfx/*.wav + src/data/sfx.json (5-7 SFX events at scene
     boundaries, generated with sfx_gen.py's generators), and
     PROJECT_README.md with the 3 delivery commands.
"""
import argparse
import json
import re
import shutil
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

# Pipeline ids — must match the component map in the starter's Main.tsx.
HOOK = "kinetic-hook"
BENTO = "bento"
DASHBOARD = "dashboard"
TIMELINE = "timeline"
STATEMENT = "statement"
RECAP = "recap"
CTA = "cta"
MIDDLE_ROTATION = [BENTO, DASHBOARD, TIMELINE]

NUMBER_RE = re.compile(r"[0-9\u09e6-\u09ef]")  # ASCII + Bengali digits
STEP_WORDS = (
    "first", "then", "next", "finally", "step",
    "প্রথমে", "তারপর", "এরপর", "শেষে", "ধাপ",
)

# SFX locked to scene roles (see references/sfx-library.md mapping).
ROLE_SFX = {HOOK: "whoosh", STATEMENT: "thud", RECAP: "pluck", CTA: "chime"}
MIDDLE_SFX = ["pop", "click", "swipe"]


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
        return {
            "bg": bg,
            "fg": _pick_text(bg),
            "accent": hex_value,
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
        "accentSoft": _rgba(accent, 0.14),
        "muted": muted,
        "label": f"tone '{tone}'",
    }


# ---------------------------------------------------------------- planning

def plan_scenes(cues):
    """Assign a pipeline to every cue. Returns a list of scene dicts."""
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
    rotation = 0
    for i in middle:
        text = cues[i]["text"]
        lowered = text.lower()
        if NUMBER_RE.search(text):
            pipelines[i] = DASHBOARD
        elif any(w in lowered for w in STEP_WORDS):
            pipelines[i] = TIMELINE
        else:
            pipelines[i] = MIDDLE_ROTATION[rotation % len(MIDDLE_ROTATION)]
            rotation += 1
    scenes = []
    for cue, pipeline in zip(cues, pipelines):
        scenes.append({
            "index": cue["index"],
            "start": cue["start"],
            "end": cue["end"],
            "text": cue["text"],
            "pipeline": pipeline,
        })
    return scenes


def plan_sfx(scenes):
    """5-7 SFX events at scene boundaries (midpoints top up short SRTs).

    Role mapping: hook -> whoosh, statement -> thud, recap -> pluck,
    cta -> chime, middle scenes rotate pop/click/swipe. Boundary events
    are taken in priority order (hook, statement, recap, cta, then
    middles in scene order) up to 7; if fewer than 5 boundaries exist,
    scene midpoints are added until 5 events exist.
    """
    by_role = {}
    for pos, scene in enumerate(scenes):
        by_role.setdefault(scene["pipeline"], []).append(pos)

    def sound_for(pos):
        pipeline = scenes[pos]["pipeline"]
        if pipeline in ROLE_SFX:
            return ROLE_SFX[pipeline]
        middle_pos = [p for p, s in enumerate(scenes)
                      if s["pipeline"] not in ROLE_SFX]
        return MIDDLE_SFX[middle_pos.index(pos) % len(MIDDLE_SFX)]

    priority = []
    for role in (HOOK, STATEMENT, RECAP, CTA):
        priority.extend(by_role.get(role, []))
    priority.extend(p for p, s in enumerate(scenes)
                    if s["pipeline"] not in ROLE_SFX)
    chosen = sorted(priority[:7])

    events = [{
        "file": f"sfx/{sound_for(pos)}.wav",
        "sound": sound_for(pos),
        "atSeconds": scenes[pos]["start"],
        "sceneIndex": scenes[pos]["index"],
    } for pos in chosen]

    pos = 0
    while len(events) < 5 and pos < len(scenes):
        scene = scenes[pos]
        mid = round((scene["start"] + scene["end"]) / 2, 3)
        if all(abs(e["atSeconds"] - mid) > 0.05 for e in events):
            events.append({
                "file": f"sfx/{sound_for(pos)}.wav",
                "sound": sound_for(pos),
                "atSeconds": mid,
                "sceneIndex": scene["index"],
            })
        pos += 1
    events.sort(key=lambda e: e["atSeconds"])
    return events


# ---------------------------------------------------------------- outputs

def render_theme_ts(theme):
    fg_ratio = color_palette.contrast(theme["fg"], theme["bg"])
    accent_ratio = color_palette.contrast(theme["accent"], theme["bg"])
    return f'''/**
 * theme.ts — generated by zobvia scripts/create_video.py
 * Palette: {theme["label"]} (WCAG: fg on bg = {fg_ratio}:1, accent on bg = {accent_ratio}:1).
 * Regenerate by re-running create_video.py, or edit the values directly.
 */
export interface Theme {{
  /** Page / scene background. */
  bg: string;
  /** Primary text colour. */
  fg: string;
  /** The ONE accent colour for this video (CREATE mode asks only this). */
  accent: string;
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
  accentSoft: "{theme["accentSoft"]}",
  muted: "{theme["muted"]}",
  font: "Hind Siliguri",
  radius: 24,
  gap: 28,
}};
'''


def render_timeline_md(title, scenes, total, theme, aspect, sfx_events):
    lines = [
        f"# Timeline — {title}",
        "",
        f"- **Scenes:** {len(scenes)} (one per SRT cue)",
        f"- **Total duration:** {total:.3f} seconds @ {FPS} fps",
        f"- **Aspect:** {aspect}",
        f"- **Palette:** {theme['label']} — bg `{theme['bg']}`, accent `{theme['accent']}`",
        f"- **SFX events:** {len(sfx_events)} (SFX only, no music)",
        "",
        "| # | Start | End | Pipeline | Text |",
        "|---|-------|-----|----------|------|",
    ]
    for s in scenes:
        text = s["text"].replace("|", "\\|").replace("\n", "<br>")
        lines.append(
            f"| {s['index']} | {srt_parse.fmt_time(s['start'])} | "
            f"{srt_parse.fmt_time(s['end'])} | {s['pipeline']} | {text} |")
    lines += ["", "## SFX map", "",
              "| At | File | Scene |", "|----|------|-------|"]
    for e in sfx_events:
        lines.append(
            f"| {srt_parse.fmt_time(e['atSeconds'])} | `public/{e['file']}` | {e['sceneIndex']} |")
    lines.append("")
    return "\n".join(lines)


def render_project_readme(title, scenes, total, theme, aspect, sfx_events):
    return f'''# {title}

A Remotion motion-graphics project generated by **zobvia**
(`scripts/create_video.py`) from an SRT subtitle file.

- **Scenes:** {len(scenes)} (one per SRT cue) — plan in `timeline.md`
- **Duration:** {total:.1f} seconds @ {FPS} fps
- **Aspect / size:** {aspect}
- **Palette:** {theme["label"]} — bg `{theme["bg"]}`, accent `{theme["accent"]}`
- **SFX:** {len(sfx_events)} generated events in `public/sfx/` (SFX only, no music)
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

## Voiceover (optional)

Drop a real recording at `public/voiceover.mp3`, set `HAS_VOICEOVER = true`
in `src/timing.ts`, and preview with the `PreviewAudio` composition.

## Editing

Change scene text/timing in `src/data/timeline.json`, colours in
`src/theme.ts`, then re-render. Scene layouts live in `src/scenes/`.
'''


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert an SRT into a ready Remotion project (zobvia CREATE fast path).")
    p.add_argument("--srt", required=True, help="Input .srt file")
    p.add_argument("--palette", required=True,
                   help="Palette tone name (see color_palette.py) or a #RRGGBB hex")
    p.add_argument("--out", required=True, help="Output project directory")
    p.add_argument("--aspect", choices=sorted(ASPECTS), default="16:9")
    p.add_argument("--title", default=None, help="Project title (default: SRT file stem)")
    args = p.parse_args(argv)

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

    out_dir = Path(args.out)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"Error: output directory is not empty: {out_dir}", file=sys.stderr)
        return 2
    if not STARTER.is_dir():
        print(f"Error: Remotion starter not found at {STARTER}", file=sys.stderr)
        return 2

    title = args.title or srt_path.stem
    width, height = ASPECTS[args.aspect]
    scenes = plan_scenes(data["cues"])
    total = data["total_duration"]
    sfx_events = plan_sfx(scenes)

    try:
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
            "scenes": scenes,
        }
        (out_dir / "src" / "data" / "timeline.json").write_text(
            json.dumps(timeline, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        (out_dir / "src" / "data" / "sfx.json").write_text(
            json.dumps({"events": [
                {"file": e["file"], "atSeconds": e["atSeconds"],
                 "sceneIndex": e["sceneIndex"]} for e in sfx_events]},
                ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        (out_dir / "src" / "theme.ts").write_text(
            render_theme_ts(theme), encoding="utf-8")
        (out_dir / "timeline.md").write_text(
            render_timeline_md(title, scenes, total, theme, args.aspect, sfx_events),
            encoding="utf-8")
        (out_dir / "PROJECT_README.md").write_text(
            render_project_readme(title, scenes, total, theme, args.aspect, sfx_events),
            encoding="utf-8")
        sfx_dir = out_dir / "public" / "sfx"
        sfx_dir.mkdir(parents=True, exist_ok=True)
        gens = sfx_gen.NP_GENS if sfx_gen.HAS_NUMPY else sfx_gen.PY_GENS
        for sound in sorted({e["sound"] for e in sfx_events}):
            samples = sfx_gen.normalise(gens[sound]())
            sfx_gen.write_wav(sfx_dir / f"{sound}.wav", samples)
    except OSError as e:
        print(f"Error: cannot write project to {out_dir}: {e}", file=sys.stderr)
        return 2

    print(f"Project created: {out_dir}")
    print(f"  Title:   {title}")
    print(f"  Scenes:  {len(scenes)} (one per SRT cue)")
    print(f"  Duration: {total:.1f}s @ {FPS} fps")
    print(f"  Aspect:  {args.aspect} ({width}x{height})")
    print(f"  Palette: {theme['label']} — bg {theme['bg']}, accent {theme['accent']}")
    print(f"  SFX:     {len(sfx_events)} events "
          f"({', '.join(sorted({e['sound'] for e in sfx_events}))})")
    print("  Next:    npm install && npx remotion studio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
