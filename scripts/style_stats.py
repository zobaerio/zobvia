#!/usr/bin/env python3
"""Summarise a watch directory (or individual JSON files) from extract.py."""
import argparse
import json
import sys
from pathlib import Path

def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"not found: {path}"
    except json.JSONDecodeError as e:
        return None, f"invalid JSON in {path}: {e}"
    except OSError as e:
        return None, f"cannot read {path}: {e}"

def extract_cuts(data):
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("cuts") or data.get("scenes") or []
    return []

def extract_words(data):
    if data is None:
        return [], None
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        return data.get("words", []), data.get("duration") or data.get("total_duration")
    return [], None

def compute(inputs):
    """inputs: dict with optional keys cuts/words/audio/summary -> parsed data"""
    stats = {"sources": {}, "errors": []}
    duration = None

    # Duration: prefer summary, then words, then audio, then last cut
    cuts = extract_cuts(inputs.get("cuts"))
    words, words_dur = extract_words(inputs.get("words"))
    audio = inputs.get("audio") if isinstance(inputs.get("audio"), dict) else None
    summary = inputs.get("summary") if isinstance(inputs.get("summary"), dict) else None

    for src in ("summary", "words", "audio"):
        d = None
        if src == "summary" and summary:
            d = summary.get("duration") or summary.get("total_duration") or (summary.get("window") or {}).get("duration")
        elif src == "words":
            d = words_dur
        elif src == "audio" and audio:
            d = audio.get("duration")
        if d:
            try:
                duration = float(d); break
            except (TypeError, ValueError):
                pass
    if duration is None and cuts:
        last = cuts[-1]
        if isinstance(last, dict):
            for k in ("time", "timestamp", "end", "start"):
                if last.get(k) is not None:
                    try:
                        duration = float(last[k]); break
                    except (TypeError, ValueError):
                        pass

    cut_count = len(cuts)
    stats["total_duration"] = round(duration, 3) if duration else None
    stats["cut_count"] = cut_count
    if duration and duration > 0:
        # shots = cuts + 1 (each cut starts a new shot)
        shots = cut_count + 1 if cut_count else 1
        stats["shot_count"] = shots
        stats["average_shot_length"] = round(duration / shots, 3)
        stats["shots_per_minute"] = round(shots / duration * 60, 2)
    else:
        stats["shot_count"] = None
        stats["average_shot_length"] = None
        stats["shots_per_minute"] = None

    # Words: list of dicts with 'word'/'text', or plain strings
    word_count = 0
    for w in words:
        if isinstance(w, str):
            word_count += len(w.split())
        elif isinstance(w, dict):
            word_count += len(str(w.get("word") or w.get("text") or "").split())
    stats["word_count"] = word_count
    if duration and duration > 0 and word_count:
        stats["words_per_second"] = round(word_count / duration, 3)
        stats["words_per_minute"] = round(word_count / duration * 60, 1)
    else:
        stats["words_per_second"] = None
        stats["words_per_minute"] = None

    # Caption words-per-cue: look for cues in summary/words payload
    cue_counts = []
    cues_data = None
    if isinstance(inputs.get("words"), dict):
        cues_data = inputs["words"].get("cues") or inputs["words"].get("segments")
    if cues_data:
        for c in cues_data:
            txt = c.get("text", "") if isinstance(c, dict) else str(c)
            cue_counts.append(len(txt.split()))
    if cue_counts:
        stats["caption_cues"] = len(cue_counts)
        stats["caption_words_per_cue_avg"] = round(sum(cue_counts) / len(cue_counts), 2)
        stats["caption_words_per_cue_min"] = min(cue_counts)
        stats["caption_words_per_cue_max"] = max(cue_counts)
    else:
        stats["caption_cues"] = None
        stats["caption_words_per_cue_avg"] = None

    # SFX events: from audio_profile or summary
    sfx = None
    for src in (audio, summary):
        if isinstance(src, dict):
            if src.get("sfx_events") is not None:
                v = src["sfx_events"]
                sfx = len(v) if isinstance(v, list) else int(v)
                break
            if src.get("sfx_event_count") is not None:
                sfx = int(src["sfx_event_count"]); break
            sil = src.get("silences")
            if sil is not None and sfx is None:
                stats["silence_count"] = len(sil) if isinstance(sil, list) else sil
    stats["sfx_event_count"] = sfx
    if audio:
        stats["audio"] = {k: audio.get(k) for k in ("mean_volume_db", "max_volume_db", "mean_volume", "max_volume") if audio.get(k) is not None}
    return stats

def to_markdown(stats, title):
    def v(x, suffix=""):
        return f"{x}{suffix}" if x is not None else "— (no data)"
    lines = [f"# Style Stats — {title}", ""]
    if stats.get("errors"):
        lines += ["## Warnings"] + [f"- {e}" for e in stats["errors"]] + [""]
    lines += [
        "## Pacing",
        f"- **Total duration:** {v(stats['total_duration'], ' s')}",
        f"- **Cut count:** {stats['cut_count']}",
        f"- **Shot count:** {v(stats['shot_count'])}",
        f"- **Average shot length:** {v(stats['average_shot_length'], ' s')}",
        f"- **Shots per minute:** {v(stats['shots_per_minute'])}",
        "",
        "## Speech",
        f"- **Word count:** {stats['word_count']}",
        f"- **Words per second:** {v(stats['words_per_second'])}",
        f"- **Words per minute:** {v(stats['words_per_minute'])}",
        "",
        "## Captions",
        f"- **Caption cues:** {v(stats.get('caption_cues'))}",
        f"- **Words per cue (avg):** {v(stats.get('caption_words_per_cue_avg'))}",
    ]
    if stats.get("caption_cues"):
        lines.append(f"- **Words per cue (min–max):** {stats['caption_words_per_cue_min']}–{stats['caption_words_per_cue_max']}")
    lines += ["", "## Audio / SFX", f"- **SFX events:** {v(stats.get('sfx_event_count'))}"]
    if stats.get("silence_count") is not None:
        lines.append(f"- **Silence segments:** {stats['silence_count']}")
    if stats.get("audio"):
        for k, val in stats["audio"].items():
            lines.append(f"- **{k}:** {val}")
    lines.append("")
    return "\n".join(lines)

def resolve_inputs(args):
    inputs = {}
    errors = []
    files = {}
    if args.input:
        p = Path(args.input)
        if p.is_dir():
            files = {"cuts": p / "cuts.json", "words": p / "words.json",
                     "audio": p / "audio_profile.json", "summary": p / "summary.json"}
        elif p.is_file():
            files = {"single": p}
        else:
            print(f"Error: input path does not exist: {p}", file=sys.stderr)
            sys.exit(2)
    for key in ("cuts", "words", "audio"):
        explicit = getattr(args, key, None)
        if explicit:
            files[key] = Path(explicit)
    if "single" in files:
        data, err = load_json(files["single"])
        if err:
            errors.append(err)
        else:
            # Heuristic: route by content shape / filename
            name = files["single"].name
            if "cut" in name: inputs["cuts"] = data
            elif "word" in name: inputs["words"] = data
            elif "audio" in name: inputs["audio"] = data
            elif "summar" in name: inputs["summary"] = data
            elif isinstance(data, dict) and "cuts" in data: inputs["cuts"] = data
            elif isinstance(data, dict) and "words" in data: inputs["words"] = data
            else: inputs["summary"] = data
    else:
        found_any = False
        for key, fp in files.items():
            if fp.is_file():
                found_any = True
                data, err = load_json(fp)
                if err: errors.append(err)
                else: inputs[key] = data
        if not found_any and not any(getattr(args, k, None) for k in ("cuts", "words", "audio")):
            errors.append("No cuts.json / words.json / audio_profile.json / summary.json found in directory.")
    return inputs, errors

def main(argv=None):
    p = argparse.ArgumentParser(description="Compute style statistics from a watch directory or JSON files.")
    p.add_argument("input", nargs="?", default=None, help="Watch directory OR a single JSON file")
    p.add_argument("--cuts", default=None, help="Path to cuts.json")
    p.add_argument("--words", default=None, help="Path to words.json")
    p.add_argument("--audio", default=None, help="Path to audio_profile.json")
    p.add_argument("--json", dest="json_out", default=None, metavar="FILE", help="Also write stats JSON to FILE")
    p.add_argument("-o", "--output", default=None, help="Write Markdown summary to FILE instead of stdout")
    args = p.parse_args(argv)
    if not args.input and not (args.cuts or args.words or args.audio):
        p.error("provide a watch directory / JSON file, or --cuts/--words/--audio")
    inputs, errors = resolve_inputs(args)
    if not inputs and errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        return 2
    stats = compute(inputs)
    stats["errors"] = errors
    title = Path(args.input).name if args.input else "custom files"
    md = to_markdown(stats, title)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        print(md)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
