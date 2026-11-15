#!/usr/bin/env python3
"""Parse an SRT subtitle file into JSON and optionally a Markdown timeline."""
import argparse
import json
import re
import sys
from pathlib import Path

TS_RE = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})"
)

def ts_to_seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

def fmt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def parse_srt(text):
    # Normalise line endings, split on blank lines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
    cues = []
    warnings = 0
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        # Find timestamp line
        ts_idx = None
        match = None
        for i, ln in enumerate(lines):
            m = TS_RE.search(ln)
            if m:
                ts_idx = i
                match = m
                break
        if match is None:
            warnings += 1
            print(f"Warning: skipping malformed block (no timestamp): {lines[0][:60]!r}", file=sys.stderr)
            continue
        try:
            start = ts_to_seconds(match.group(1), match.group(2), match.group(3), match.group(4))
            end = ts_to_seconds(match.group(5), match.group(6), match.group(7), match.group(8))
        except Exception:
            warnings += 1
            continue
        if end < start:
            warnings += 1
            print(f"Warning: cue ends before it starts, swapping/clamping: {lines[0][:60]!r}", file=sys.stderr)
            end = start
        # Index: line before timestamp if it's a number
        idx = len(cues) + 1
        if ts_idx > 0:
            try:
                idx = int(lines[0])
            except ValueError:
                pass
        text_lines = lines[ts_idx + 1:]
        cue_text = "\n".join(text_lines).strip()
        if not cue_text:
            warnings += 1
            print(f"Warning: cue {idx} has no text", file=sys.stderr)
        cues.append({
            "index": idx,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "text": cue_text,
        })
    total = max((c["end"] for c in cues), default=0.0)
    return {"total_duration": round(total, 3), "cue_count": len(cues), "warnings": warnings, "cues": cues}

def markdown_timeline(data):
    lines = []
    lines.append("# SRT Timeline")
    lines.append("")
    lines.append(f"- **Total duration:** {data['total_duration']:.3f} seconds")
    lines.append(f"- **Cue count:** {data['cue_count']}")
    if data.get("warnings"):
        lines.append(f"- **Warnings:** {data['warnings']}")
    lines.append("")
    lines.append("| # | Start | End | Duration | Text |")
    lines.append("|---|-------|-----|----------|------|")
    for c in data["cues"]:
        text = c["text"].replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| {c['index']} | {fmt_time(c['start'])} | {fmt_time(c['end'])} | {c['duration']:.3f}s | {text} |")
    lines.append("")
    return "\n".join(lines)

def main(argv=None):
    p = argparse.ArgumentParser(description="Parse an SRT file to JSON (and optionally Markdown).")
    p.add_argument("input", help="Input .srt file")
    p.add_argument("-o", "--output", dest="output", default=None, help="Output JSON file (default: stdout)")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    p.add_argument("--markdown", default=None, metavar="FILE", help="Also write a Markdown timeline to FILE")
    args = p.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"Error: input file not found: {path}", file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"Error: cannot read {path}: {e}", file=sys.stderr)
        return 2

    data = parse_srt(text)
    if data["cue_count"] == 0:
        print(
            f"Error: no valid SRT cues found in {path} "
            f"({data['warnings']} malformed block(s) skipped). "
            "Check that the file is a real .srt with timestamps like "
            "00:00:01,000 --> 00:00:03,000.",
            file=sys.stderr,
        )
        return 2
    out_json = json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        try:
            Path(args.output).write_text(out_json + "\n", encoding="utf-8")
        except OSError as e:
            print(f"Error: cannot write {args.output}: {e}", file=sys.stderr)
            return 2
    else:
        print(out_json)
    if args.markdown:
        try:
            Path(args.markdown).write_text(markdown_timeline(data), encoding="utf-8")
        except OSError as e:
            print(f"Error: cannot write markdown {args.markdown}: {e}", file=sys.stderr)
            return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
