#!/usr/bin/env python3
"""Zobvia Auto-Shorts: turn one long video into vertical shorts.

Pipeline (all local, no API keys):
  1. Highlight candidates from the bundled ffmpeg-skill `scenes.py`
     (scene cuts + a 0.5s RMS audio-energy envelope, ranked loudest
     first). These are PROXIES, not a judgement of what matters —
     the manifest says so, and every window is reported for review.
  2. Each window is expanded to at least --min-seconds (and capped
     at --max-seconds), cut with ffmpeg-skill `cut.py`, reframed to
     9:16 with `fit.py` (blur-pad, nothing cropped away), captioned
     from the caller's SRT when one is given (cues sliced + re-timed,
     burned with `caption.py`), and loudness-normalized to the
     platform target (-14 LUFS / -1.5 dBTP) with FFmpeg loudnorm.

Usage:
  python3 scripts/auto_shorts.py VIDEO [--srt FILE] [--count 3]
      [--min-seconds 20] [--max-seconds 58] [--width 1080]
      [--out DIR] [--rank-by audio|duration] [--json]

Outputs: <out>/short-1.mp4 ... and <out>/manifest.json describing
every window, its source range and the tools that produced it.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def ffmpeg_skill_scripts() -> Path:
    env = os.environ.get("ZOBVIA_FFMPEG_SKILL_DIR")
    candidates = []
    if env:
        candidates.append(Path(env) / "scripts")
        candidates.append(Path(env))
    candidates.append(SKILL_ROOT / "extras" / "ffmpeg-skill" / "scripts")
    for c in candidates:
        if (c / "scenes.py").is_file():
            return c
    raise SystemExit(
        "ffmpeg-skill not found: set ZOBVIA_FFMPEG_SKILL_DIR or keep "
        "extras/ffmpeg-skill/ next to this skill.")


def run(cmd, **kw):
    proc = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-600:]
        raise SystemExit(f"command failed ({' '.join(map(str, cmd[:3]))}...):\n{tail}")
    return proc


def tool(scripts: Path, name: str, *args) -> subprocess.CompletedProcess:
    return run([sys.executable, str(scripts / name), *map(str, args)])


def probe_duration(video: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration", "-of", "json", str(video)]).stdout
    return float(json.loads(out)["format"]["duration"])


# ---------- SRT helpers ----------
_TS = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


def _ts_to_sec(ts: str) -> float:
    m = _TS.search(ts)
    h, mnt, s, ms = (int(m.group(i)) for i in range(1, 5))
    return h * 3600 + mnt * 60 + s + ms / 1000.0


def _sec_to_ts(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    mnt = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{mnt:02d}:{s:02d},{ms:03d}"


def parse_srt(path: Path):
    cues = []
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    for block in blocks:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        tline = next((ln for ln in lines if "-->" in ln), None)
        if not tline:
            continue
        start_s, end_s = tline.split("-->")
        text = "\n".join(ln for ln in lines
                         if "-->" not in ln and not ln.strip().isdigit())
        cues.append({"start": _ts_to_sec(start_s), "end": _ts_to_sec(end_s),
                     "text": text.strip()})
    return cues


def slice_srt(cues, start: float, end: float) -> str:
    out = []
    for i, cue in enumerate(
            (c for c in cues if c["end"] > start and c["start"] < end), 1):
        out.append(f"{i}\n{_sec_to_ts(cue['start'] - start)} --> "
                   f"{_sec_to_ts(cue['end'] - start)}\n{cue['text']}\n")
    return "\n".join(out)


# ---------- window planning ----------
def plan_windows(highlights, duration, count, min_s, max_s):
    windows = []
    for h in highlights:
        start, end = float(h["start"]), float(h["end"])
        if end - start > max_s:
            mid = (start + end) / 2
            start, end = mid - max_s / 2, mid + max_s / 2
        if end - start < min_s:
            mid = (start + end) / 2
            start = max(0.0, mid - min_s / 2)
            end = min(duration, start + min_s)
            start = max(0.0, end - min_s)
        windows.append({"start": round(start, 2), "end": round(end, 2)})
        if len(windows) >= count * 2:
            break
    chosen = []
    for w in windows:
        if any(w["start"] < c["end"] and w["end"] > c["start"] for c in chosen):
            continue
        chosen.append(w)
        if len(chosen) >= count:
            break
    return sorted(chosen, key=lambda w: w["start"])


def main() -> int:
    ap = argparse.ArgumentParser(description="Zobvia Auto-Shorts")
    ap.add_argument("video")
    ap.add_argument("--srt", help="caller-supplied SRT for burned captions")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--min-seconds", type=float, default=20.0)
    ap.add_argument("--max-seconds", type=float, default=58.0)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--out", default=None)
    ap.add_argument("--rank-by", choices=["audio", "duration"], default="audio")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.is_file():
        raise SystemExit(f"video not found: {video}")
    out_dir = Path(args.out).resolve() if args.out else \
        video.parent / f"{video.stem}-shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    scripts = ffmpeg_skill_scripts()
    duration = probe_duration(video)

    raw = tool(scripts, "scenes.py", video, "--highlights", args.count * 2,
               "--target", args.max_seconds, "--rank-by", args.rank_by,
               "--json").stdout
    highlights = json.loads(raw).get("highlights") or []
    if not highlights:
        raise SystemExit("no highlight candidates found "
                         "(no scene cuts / audio energy?)")
    windows = plan_windows(highlights, duration, args.count,
                           args.min_seconds, args.max_seconds)
    cues = parse_srt(Path(args.srt)) if args.srt else []

    manifest = {"source": str(video), "source_duration": round(duration, 2),
                "rank_by": args.rank_by,
                "ranking_note": "audio-energy/scene proxy, not a judgement "
                                "of what matters — review before posting",
                "shorts": []}
    for i, w in enumerate(windows, 1):
        seg = out_dir / f".seg-{i}.mp4"
        vert = out_dir / f".vert-{i}.mp4"
        final = out_dir / f"short-{i}.mp4"
        tool(scripts, "cut.py", video, "--start", w["start"], "--end",
             w["end"], "-o", seg, "--overwrite")
        tool(scripts, "fit.py", seg, "--aspect", "9:16", "--fit", "blur",
             "--width", args.width, "-o", vert, "--overwrite")
        stage = vert
        temps = [seg, vert]
        captioned_burned = False
        if cues:
            srt_path = out_dir / f".seg-{i}.srt"
            srt_text = slice_srt(cues, w["start"], w["end"])
            if srt_text.strip():
                srt_path.write_text(srt_text, encoding="utf-8")
                captioned = out_dir / f".cap-{i}.mp4"
                tool(scripts, "caption.py", vert, "--srt", srt_path,
                     "-o", captioned, "--overwrite")
                stage = captioned
                temps.append(captioned)
                captioned_burned = True
        run(["ffmpeg", "-y", "-v", "error", "-i", str(stage),
             "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:a", "aac", "-b:a", "192k", str(final)])
        for tmp in temps:
            tmp.unlink(missing_ok=True)
        (out_dir / f".seg-{i}.srt").unlink(missing_ok=True)
        (out_dir / f".cap-{i}_adjusted.srt").unlink(missing_ok=True)
        manifest["shorts"].append(
            {"file": final.name, "source_start": w["start"],
             "source_end": w["end"],
             "duration": round(w["end"] - w["start"], 2),
             "captions": captioned_burned,
             "size": f"{args.width}x{round(args.width * 16 / 9)} (9:16)"})
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"{len(manifest['shorts'])} short(s) in {out_dir}")
        for s in manifest["shorts"]:
            print(f"  {s['file']}: source {s['source_start']}s-"
                  f"{s['source_end']}s ({s['duration']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
