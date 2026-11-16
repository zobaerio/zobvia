#!/usr/bin/env python3
"""Make an SRT file from a plain script — no transcription needed.

Many creators have their script typed out but no subtitle file. Give this
script the text and the total duration (seconds, or an audio file to
measure) and it writes a timed SRT:

* the script is split into cues — one cue per line; long lines are split
  further at sentence ends (. ! ? ।) and, if still long, at commas or
  word boundaries;
* each cue's on-screen time is proportional to its grapheme count
  (Bengali conjuncts/combining marks count as one), clamped so no cue is
  shorter than --min or longer than --max seconds — neighbours are
  merged or split to respect the clamps;
* cues are contiguous and cover exactly the requested duration.

Usage:
    python3 scripts/make_srt.py --text script.txt --duration 45 --out subs.srt
    python3 scripts/make_srt.py --text script.txt --audio voice.mp3 --out subs.srt

Exit codes: 0 ok, 2 bad input.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

SENTENCE_END = re.compile(r"(?<=[.!?।])\s+")
MAX_CUE_GRAPHEMES = 84


def grapheme_len(text: str) -> int:
    """Approximate grapheme count: combining marks join the previous char."""
    return sum(1 for ch in text if not unicodedata.category(ch).startswith("M"))


def split_long(text: str) -> list[str]:
    """Split one long sentence into <= MAX_CUE_GRAPHEMES pieces."""
    if grapheme_len(text) <= MAX_CUE_GRAPHEMES:
        return [text]
    pieces: list[str] = []
    rest = text
    while grapheme_len(rest) > MAX_CUE_GRAPHEMES:
        # prefer a comma break, else a word break, near the limit
        cut = -1
        for i, ch in enumerate(rest):
            if grapheme_len(rest[: i + 1]) > MAX_CUE_GRAPHEMES:
                break
            if ch in ",;:—- ":
                cut = i
        if cut < 10:  # no decent break found; hard cut at a word boundary
            words = rest.split(" ")
            acc = ""
            for w in words:
                if grapheme_len(acc + " " + w) > MAX_CUE_GRAPHEMES and acc:
                    break
                acc = (acc + " " + w).strip()
            pieces.append(acc)
            rest = rest[len(acc):].strip()
        else:
            pieces.append(rest[: cut + 1].strip(" ,;:"))
            rest = rest[cut + 1:].strip()
    if rest:
        pieces.append(rest)
    return [p for p in pieces if p]


def split_cues(script: str) -> list[str]:
    cues: list[str] = []
    for line in script.splitlines():
        line = line.strip()
        if not line:
            continue
        for sentence in SENTENCE_END.split(line):
            sentence = sentence.strip()
            if sentence:
                cues.extend(split_long(sentence))
    return cues


def allocate(cues: list[str], duration: float, min_s: float, max_s: float) -> list[tuple[float, float, str]]:
    """Assign contiguous [start, end) spans proportional to grapheme length,
    respecting min/max per cue by merging/splitting where needed."""
    # split cues that would exceed max at an even share
    total_g = sum(grapheme_len(c) for c in cues) or 1
    expanded: list[str] = []
    for c in cues:
        share = duration * grapheme_len(c) / total_g
        if share > max_s and grapheme_len(c) > 20:
            parts = split_long(c) if grapheme_len(c) > MAX_CUE_GRAPHEMES else None
            if parts and len(parts) > 1:
                expanded.extend(parts)
            else:
                # split at the middle word boundary
                words = c.split(" ")
                mid, acc = len(words) // 2, ""
                left = " ".join(words[:mid]).strip()
                right = " ".join(words[mid:]).strip()
                expanded.extend([left, right] if left and right else [c])
        else:
            expanded.append(c)
    cues = expanded
    # merge neighbours that would be shorter than min
    merged: list[str] = []
    for c in cues:
        total_g = sum(grapheme_len(x) for x in cues) or 1
        if merged and duration * grapheme_len(c) / total_g < min_s:
            merged[-1] = merged[-1] + " " + c
        else:
            merged.append(c)
    cues = merged
    total_g = sum(grapheme_len(c) for c in cues) or 1
    spans: list[tuple[float, float, str]] = []
    t = 0.0
    for i, c in enumerate(cues):
        if i == len(cues) - 1:
            end = duration
        else:
            end = t + duration * grapheme_len(c) / total_g
        spans.append((round(t, 3), round(end, 3), c))
        t = end
    return spans


def fmt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(script: str, duration: float, min_s: float = 1.0, max_s: float = 8.0) -> str:
    cues = split_cues(script)
    if not cues:
        raise ValueError("script is empty")
    spans = allocate(cues, duration, min_s, max_s)
    blocks = []
    for i, (start, end, text) in enumerate(spans, 1):
        blocks.append(f"{i}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}")
    return "\n\n".join(blocks) + "\n"


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, timeout=60)
    return float(out.stdout.strip())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Script text -> timed SRT file.")
    p.add_argument("--text", required=True, help="Script .txt file")
    p.add_argument("--duration", type=float, help="Total seconds")
    p.add_argument("--audio", help="Audio file to measure instead of --duration")
    p.add_argument("--out", required=True, help="Output .srt path")
    p.add_argument("--min", type=float, default=1.0, help="Min cue seconds")
    p.add_argument("--max", type=float, default=8.0, help="Max cue seconds")
    a = p.parse_args(argv)

    text_path = Path(a.text)
    if not text_path.exists():
        print(f"error: script file not found: {text_path}", file=sys.stderr)
        return 2
    script = text_path.read_text(encoding="utf-8").strip()
    if not script:
        print("error: script file is empty", file=sys.stderr)
        return 2
    if a.audio:
        try:
            duration = audio_duration(Path(a.audio))
        except Exception as e:  # noqa: BLE001
            print(f"error: could not measure audio: {e}", file=sys.stderr)
            return 2
    elif a.duration:
        duration = a.duration
    else:
        print("error: give --duration or --audio", file=sys.stderr)
        return 2
    if duration <= 0:
        print("error: duration must be positive", file=sys.stderr)
        return 2
    try:
        srt = build_srt(script, duration, a.min, a.max)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    Path(a.out).write_text(srt, encoding="utf-8")
    print(f"wrote {a.out}: {srt.count('-->')} cues over {duration:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
