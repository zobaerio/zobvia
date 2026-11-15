#!/usr/bin/env python3
"""qc_check.py — probe a rendered video and check it against expectations.

Usage:
    python3 scripts/qc_check.py --file <video.mp4> \
        [--expect-width N] [--expect-height N] [--expect-fps N] \
        [--expect-duration S] [--tolerance S]

Always reports the probed facts (dimensions, fps, duration, has_audio,
has_video). Each supplied expectation is printed as PASS/FAIL.
Exit codes: 0 = every supplied expectation passed (or report-only mode
with a successful probe), 1 = an expectation failed, 2 = file could not
be probed, 3 = ffprobe not installed.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def probe(path):
    """Return a facts dict from ffprobe, or None if probing failed."""
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format",
           "-of", "json", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    facts = {"has_video": video is not None, "has_audio": audio is not None}
    if video:
        facts["width"] = video.get("width")
        facts["height"] = video.get("height")
        fps = None
        for key in ("avg_frame_rate", "r_frame_rate"):
            raw = video.get(key)
            if raw and "/" in raw:
                num, den = raw.split("/", 1)
                try:
                    if float(den) != 0:
                        fps = float(num) / float(den)
                        break
                except ValueError:
                    pass
        facts["fps"] = round(fps, 3) if fps else None
    duration = None
    fmt = data.get("format", {})
    if fmt.get("duration"):
        try:
            duration = float(fmt["duration"])
        except ValueError:
            duration = None
    if duration is None and video and video.get("duration"):
        try:
            duration = float(video["duration"])
        except ValueError:
            duration = None
    facts["duration"] = round(duration, 3) if duration is not None else None
    return facts


def main(argv=None):
    p = argparse.ArgumentParser(
        description="QC-check a rendered video with ffprobe.")
    p.add_argument("--file", required=True, help="Video file to probe")
    p.add_argument("--expect-width", type=int, default=None)
    p.add_argument("--expect-height", type=int, default=None)
    p.add_argument("--expect-fps", type=float, default=None)
    p.add_argument("--expect-duration", type=float, default=None,
                   help="Expected duration in seconds")
    p.add_argument("--tolerance", type=float, default=1.0,
                   help="Duration tolerance in seconds (default: 1.0)")
    args = p.parse_args(argv)

    if not shutil.which("ffprobe"):
        print("Error: ffprobe not found. Install ffmpeg "
              "(Linux: sudo apt install ffmpeg; macOS: brew install ffmpeg; "
              "Windows: winget install Gyan.FFmpeg).", file=sys.stderr)
        return 3

    path = Path(args.file)
    if not path.is_file():
        print(f"FAIL  file exists — not found: {path}")
        return 2
    facts = probe(path)
    if facts is None:
        print(f"FAIL  ffprobe could not read: {path}")
        return 2

    print(f"File: {path}")
    print(f"  has_video: {facts['has_video']}")
    print(f"  has_audio: {facts['has_audio']}")
    print(f"  dimensions: {facts.get('width')}x{facts.get('height')}")
    print(f"  fps: {facts.get('fps')}")
    print(f"  duration: {facts.get('duration')}s")

    checks = []

    def check(name, ok, detail):
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name} — {detail}")

    if args.expect_width is not None:
        check("width", facts.get("width") == args.expect_width,
              f"expected {args.expect_width}, got {facts.get('width')}")
    if args.expect_height is not None:
        check("height", facts.get("height") == args.expect_height,
              f"expected {args.expect_height}, got {facts.get('height')}")
    if args.expect_fps is not None:
        got = facts.get("fps")
        check("fps", got is not None and abs(got - args.expect_fps) <= 0.1,
              f"expected {args.expect_fps}, got {got}")
    if args.expect_duration is not None:
        got = facts.get("duration")
        ok = got is not None and abs(got - args.expect_duration) <= args.tolerance
        check("duration", ok,
              f"expected {args.expect_duration}±{args.tolerance}s, got {got}s")

    if checks:
        return 0 if all(checks) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
