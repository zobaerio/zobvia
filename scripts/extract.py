#!/usr/bin/env python3
"""extract.py — LEARN engine for zobvia.

Downloads or loads a video, cuts a window, samples frames, detects scene
cuts, builds side-by-side frame pairs, transcribes speech (word timestamps)
and profiles the audio. Every step records success / skip + reason in
summary.json. It NEVER fabricates output: missing tools produce an honest
error or a recorded skip, never fake data.

Usage:
    extract.py <video URL or local file> --name <slug>
               [--start S] [--end S] [--fps 2] [--model MODEL]
               [--out-root references/watch]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def run(cmd, timeout=1800):
    """Run a command, return (returncode, stdout, stderr). Never raises."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"command timed out after {timeout}s: {' '.join(map(str, cmd))}"


def is_url(s):
    return s.startswith("http://") or s.startswith("https://")


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip()).strip("-").lower()
    return s or "watch"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe_duration(path):
    rc, out, err = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "json", str(path)], timeout=120)
    if rc != 0:
        return None, f"ffprobe failed: {err.strip()[:400]}"
    try:
        dur = float(json.loads(out)["format"]["duration"])
        return dur, None
    except Exception as e:
        return None, f"could not parse ffprobe duration: {e}"


INSTALL_HELP = """\
Error: required tools are missing: {missing}

Install instructions:
  ffmpeg / ffprobe:
    Ubuntu/Debian : sudo apt install ffmpeg
    macOS         : brew install ffmpeg
    Windows       : https://ffmpeg.org/download.html  (add to PATH)
  yt-dlp (only needed for URL inputs):
    pip install yt-dlp

Re-run this command after installing. No output was generated, because
extract.py never fabricates watch data.
"""

# --------------------------------------------------------------------------
# Pipeline steps — each returns (status_dict, data_or_None)
# --------------------------------------------------------------------------

def download_url(url, dest_dir):
    """Download with yt-dlp. Returns (path_or_None, note)."""
    if not shutil.which("yt-dlp"):
        return None, ("yt-dlp is not installed, so the URL could not be downloaded. "
                      "Install it with: pip install yt-dlp — or download the video "
                      "yourself and pass the local file path instead.")
    dest_dir.mkdir(parents=True, exist_ok=True)
    tmpl = str(dest_dir / "source.%(ext)s")
    rc, out, err = run(["yt-dlp", "--no-playlist", "-o", tmpl, url], timeout=1800)
    if rc != 0:
        return None, f"yt-dlp failed (exit {rc}): {(err or out).strip()[:500]}"
    candidates = sorted(dest_dir.glob("source.*"))
    candidates = [c for c in candidates if c.suffix not in (".json", ".part")]
    if not candidates:
        return None, "yt-dlp reported success but no source file was found."
    return candidates[0], "downloaded with yt-dlp"


def cut_window(src, start, end, dest):
    """Cut [start, end] with ffmpeg (re-encode for frame accuracy)."""
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(src)]
    if end is not None:
        dur = float(end) - float(start or 0)
        if dur <= 0:
            return False, "--end must be greater than --start"
        cmd += ["-t", str(dur)]
    cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "160k", str(dest)]
    rc, out, err = run(cmd)
    if rc != 0 or not dest.is_file():
        return False, f"ffmpeg cut failed (exit {rc}): {err.strip()[:500]}"
    return True, "window cut with ffmpeg (libx264/aac re-encode)"


def sample_frames(video, fps, frames_dir):
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "frame_%05d.jpg")
    rc, out, err = run(["ffmpeg", "-y", "-v", "error", "-i", str(video),
                        "-vf", f"fps={fps}", "-q:v", "3", pattern])
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if rc != 0:
        return False, [], f"ffmpeg frame sampling failed (exit {rc}): {err.strip()[:400]}"
    if not frames:
        return False, [], "ffmpeg produced no frames (video too short or unreadable?)"
    return True, frames, f"sampled {len(frames)} frames at {fps} fps"


def detect_cuts(video, threshold=0.3):
    """Scene-cut detection via ffmpeg select/showinfo. Returns list of times."""
    cmd = ["ffmpeg", "-i", str(video), "-filter:v",
           f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"]
    rc, out, err = run(cmd)
    log = err + "\n" + out
    times = []
    for m in re.finditer(r"pts_time:\s*([0-9.]+)", log):
        try:
            times.append(round(float(m.group(1)), 3))
        except ValueError:
            continue
    # First showinfo line is frame 0 in many builds; drop an exact 0.0 opener
    # only when there are further cuts, to avoid a phantom cut at t=0.
    if len(times) > 1 and times[0] == 0.0:
        times = times[1:]
    return times, f"ffmpeg scene detection (threshold {threshold}), {len(times)} cuts"


def build_pairs(frames, pairs_dir):
    """Side-by-side pairs of consecutive frames with PIL."""
    try:
        from PIL import Image
    except ImportError:
        return "skipped", "Pillow (PIL) is not installed — install: pip install Pillow"
    if len(frames) < 2:
        return "skipped", "fewer than 2 frames sampled, nothing to pair"
    pairs_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for i in range(len(frames) - 1):
        try:
            a = Image.open(frames[i]).convert("RGB")
            b = Image.open(frames[i + 1]).convert("RGB")
            h = min(a.height, b.height)
            def fit(im):
                if im.height != h:
                    w = int(im.width * h / im.height)
                    return im.resize((w, h))
                return im
            a, b = fit(a), fit(b)
            canvas = Image.new("RGB", (a.width + b.width + 8, h), (24, 24, 24))
            canvas.paste(a, (0, 0))
            canvas.paste(b, (a.width + 8, 0))
            canvas.save(pairs_dir / f"pair_{i+1:04d}.jpg", quality=88)
            made += 1
        except Exception as e:
            return "partial", f"pair building stopped at frame {i}: {e} ({made} pairs made)"
    return "ok", f"built {made} side-by-side pairs"


def transcribe_faster_whisper(video, model):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="auto", compute_type="auto")
    segments, info = m.transcribe(str(video), word_timestamps=True, vad_filter=True)
    words = []
    segs = []
    for seg in segments:
        segs.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                     "text": seg.text.strip()})
        for w in (seg.words or []):
            words.append({"word": w.word.strip(), "start": round(w.start, 3),
                          "end": round(w.end, 3),
                          "probability": round(float(w.probability), 3) if w.probability is not None else None})
    return words, segs, getattr(info, "language", None)


def transcribe_whisper_cli(video, model, work_dir):
    """Fallback: openai-whisper CLI with word_timestamps via --word_timestamps True."""
    out_dir = work_dir / "whisper_cli"
    out_dir.mkdir(parents=True, exist_ok=True)
    rc, out, err = run(["whisper", str(video), "--model", model,
                        "--word_timestamps", "True", "--output_format", "json",
                        "--output_dir", str(out_dir)], timeout=3600)
    if rc != 0:
        raise RuntimeError(f"whisper CLI failed (exit {rc}): {err.strip()[:400]}")
    jf = out_dir / (Path(video).stem + ".json")
    if not jf.is_file():
        raise RuntimeError("whisper CLI produced no JSON output")
    data = json.loads(jf.read_text(encoding="utf-8"))
    words, segs = [], []
    for seg in data.get("segments", []):
        segs.append({"start": round(seg.get("start", 0), 3), "end": round(seg.get("end", 0), 3),
                     "text": (seg.get("text") or "").strip()})
        for w in seg.get("words", []):
            words.append({"word": (w.get("word") or "").strip(),
                          "start": round(w.get("start", 0), 3), "end": round(w.get("end", 0), 3),
                          "probability": None})
    return words, segs, data.get("language")


def transcribe(video, model, work_dir):
    """Try faster-whisper, then whisper CLI, else record an honest skip."""
    try:
        import faster_whisper  # noqa: F401
        words, segs, lang = transcribe_faster_whisper(video, model)
        return "ok", {"engine": "faster-whisper", "language": lang,
                      "words": words, "segments": segs}, "transcribed with faster-whisper"
    except ImportError:
        pass
    except Exception as e:
        return "failed", None, f"faster-whisper error: {e}"
    if shutil.which("whisper"):
        try:
            words, segs, lang = transcribe_whisper_cli(video, model, work_dir)
            return "ok", {"engine": "openai-whisper-cli", "language": lang,
                          "words": words, "segments": segs}, "transcribed with openai-whisper CLI"
        except Exception as e:
            return "failed", None, str(e)
    return "skipped", None, ("no transcription engine available: faster-whisper is not "
                             "importable and the `whisper` CLI is not on PATH. "
                             "Install one: pip install faster-whisper  OR  pip install openai-whisper")


def audio_profile(video, duration):
    profile = {"duration": duration}
    notes = []
    # volumedetect for mean / max volume
    rc, out, err = run(["ffmpeg", "-i", str(video), "-af", "volumedetect", "-f", "null", "-"], timeout=600)
    log = err + out
    m = re.search(r"mean_volume:\s*(-?[0-9.]+) dB", log)
    if m:
        profile["mean_volume_db"] = float(m.group(1))
    m = re.search(r"max_volume:\s*(-?[0-9.]+) dB", log)
    if m:
        profile["max_volume_db"] = float(m.group(1))
    if "mean_volume_db" not in profile:
        notes.append("volumedetect produced no mean_volume (silent or audio-less video?)")
    # astats overall RMS / peak as a second source
    rc, out, err = run(["ffmpeg", "-i", str(video), "-af", "astats=metadata=1", "-f", "null", "-"], timeout=600)
    log = err + out
    m = re.findall(r"RMS level dB:\s*(-?[0-9.]+|-\u221e|-inf)", log)
    if m:
        try:
            profile["astats_rms_db_last"] = float(m[-1])
        except ValueError:
            profile["astats_rms_db_last"] = None
    # silence detection
    rc, out, err = run(["ffmpeg", "-i", str(video), "-af",
                        "silencedetect=noise=-35dB:d=0.4", "-f", "null", "-"], timeout=600)
    log = err + out
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", log)]
    silences = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration
        silences.append({"start": round(s, 3), "end": round(e, 3) if e else None,
                         "duration": round(e - s, 3) if e else None})
    profile["silences"] = silences
    profile["silence_count"] = len(silences)
    if notes:
        profile["notes"] = notes
    status = "ok" if "mean_volume_db" in profile else "partial"
    return status, profile, (f"mean {profile.get('mean_volume_db')} dB, max {profile.get('max_volume_db')} dB, "
                             f"{len(silences)} silence segments")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(
        description="LEARN engine: analyse a reference video into frames, cuts, words and audio profile.")
    p.add_argument("input", help="Video URL (https://...) or local video file path")
    p.add_argument("--name", required=True, help="Slug/name for this watch (output folder name)")
    p.add_argument("--start", type=float, default=0.0, help="Window start in seconds (default 0)")
    p.add_argument("--end", type=float, default=None, help="Window end in seconds (default: full video)")
    p.add_argument("--fps", type=float, default=2.0, help="Frame sampling rate (default 2)")
    p.add_argument("--model", default="small", help="Whisper model name (default: small)")
    p.add_argument("--out-root", default="references/watch", help="Root folder for watch output")
    p.add_argument("--scene-threshold", type=float, default=0.3, help="Scene-cut threshold (default 0.3)")
    args = p.parse_args(argv)

    if args.end is not None and args.start and args.end <= args.start:
        print("Error: --end must be greater than --start", file=sys.stderr)
        return 2
    if args.fps <= 0:
        print("Error: --fps must be positive", file=sys.stderr)
        return 2

    # (a) verify core tools — never fake output
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        print(INSTALL_HELP.format(missing=", ".join(missing)), file=sys.stderr)
        return 3

    slug = slugify(args.name)
    out_dir = Path(args.out_root) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    steps = {}

    # (b) obtain source
    src = None
    if is_url(args.input):
        src, note = download_url(args.input, out_dir / "_download")
        steps["download"] = {"status": "ok" if src else "failed", "note": note, "input": args.input}
        if src is None:
            print(f"Error: {note}", file=sys.stderr)
            write_json(out_dir / "summary.json",
                       {"slug": slug, "input": args.input, "steps": steps,
                        "error": note})
            return 4
    else:
        src = Path(args.input)
        if not src.is_file():
            print(f"Error: input file not found: {src}\n"
                  f"Check the path and try again. No output was generated.", file=sys.stderr)
            return 2
        steps["download"] = {"status": "skipped", "note": "local file input, no download needed"}

    # (c) probe duration
    duration, err = probe_duration(src)
    if duration is None:
        print(f"Error: could not probe video: {err}", file=sys.stderr)
        steps["probe"] = {"status": "failed", "note": err}
        write_json(out_dir / "summary.json", {"slug": slug, "input": str(src), "steps": steps, "error": err})
        return 5
    steps["probe"] = {"status": "ok", "note": f"duration {duration:.3f}s", "duration": round(duration, 3)}
    print(f"Source: {src}  ({duration:.1f}s)")

    start = float(args.start or 0)
    end = float(args.end) if args.end is not None else duration
    end = min(end, duration)
    window_dur = max(end - start, 0)

    # (d) cut window (skip re-encode when window is the whole file)
    work = out_dir / "clip.mp4"
    if start == 0 and end >= duration:
        # still normalise through ffmpeg cut for consistent downstream handling
        ok, note = cut_window(src, 0, None, work)
    else:
        ok, note = cut_window(src, start, end, work)
    steps["cut"] = {"status": "ok" if ok else "failed", "note": note,
                    "window": {"start": start, "end": end, "duration": round(window_dur, 3)}}
    if not ok:
        print(f"Error: {note}", file=sys.stderr)
        write_json(out_dir / "summary.json", {"slug": slug, "input": str(src), "steps": steps, "error": note})
        return 6
    print(f"Window: {start:.1f}s → {end:.1f}s  ({window_dur:.1f}s)")

    # (e) sample frames
    ok, frames, note = sample_frames(work, args.fps, out_dir / "frames")
    steps["frames"] = {"status": "ok" if ok else "failed", "note": note,
                       "fps": args.fps, "frame_count": len(frames)}
    if not ok:
        print(f"Warning: {note}", file=sys.stderr)

    # (f) scene cuts
    cut_times, cut_note = detect_cuts(work, args.scene_threshold)
    cuts_data = {"threshold": args.scene_threshold, "duration": round(window_dur, 3),
                 "cut_count": len(cut_times),
                 "cuts": [{"time": t, "index": i + 1} for i, t in enumerate(cut_times)]}
    write_json(out_dir / "cuts.json", cuts_data)
    steps["cuts"] = {"status": "ok", "note": cut_note}

    # (g) side-by-side pairs
    if ok and frames:
        status, note = build_pairs(frames, out_dir / "pairs")
    else:
        status, note = "skipped", "no frames available to pair"
    steps["pairs"] = {"status": status, "note": note}

    # (h) transcription
    t_status, t_data, t_note = transcribe(work, args.model, out_dir)
    if t_data is not None:
        write_json(out_dir / "words.json",
                   {"engine": t_data["engine"], "language": t_data["language"],
                    "duration": round(window_dur, 3), "word_count": len(t_data["words"]),
                    "words": t_data["words"], "segments": t_data["segments"]})
    else:
        write_json(out_dir / "words.json",
                   {"engine": None, "language": None, "duration": round(window_dur, 3),
                    "word_count": 0, "words": [], "segments": [], "note": t_note})
    steps["transcription"] = {"status": t_status, "note": t_note,
                              "word_count": len(t_data["words"]) if t_data else 0}

    # (i) audio profile
    a_status, a_data, a_note = audio_profile(work, round(window_dur, 3))
    write_json(out_dir / "audio_profile.json", a_data)
    steps["audio"] = {"status": a_status, "note": a_note}

    # (j) summary
    summary = {
        "slug": slug,
        "input": args.input,
        "source_file": str(src),
        "duration": round(duration, 3),
        "window": {"start": start, "end": round(end, 3), "duration": round(window_dur, 3)},
        "fps": args.fps,
        "model": args.model,
        "cut_count": len(cut_times),
        "frame_count": len(frames) if ok else 0,
        "word_count": steps["transcription"]["word_count"],
        "steps": steps,
        "outputs": {
            "clip": "clip.mp4", "frames": "frames/", "pairs": "pairs/",
            "cuts": "cuts.json", "words": "words.json",
            "audio_profile": "audio_profile.json", "summary": "summary.json",
        },
    }
    write_json(out_dir / "summary.json", summary)
    print(f"Done. Watch written to {out_dir}")
    print(f"  cuts: {len(cut_times)} | frames: {summary['frame_count']} | "
          f"words: {summary['word_count']} | transcription: {t_status} | audio: {a_status}")
    for name, s in steps.items():
        if s["status"] in ("skipped", "failed", "partial"):
            print(f"  NOTE [{name}] {s['status']}: {s['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
