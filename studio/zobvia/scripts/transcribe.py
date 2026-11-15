#!/usr/bin/env python3
"""transcribe.py — turn an audio/video file into an SRT subtitle file.

Usage:
    python3 scripts/transcribe.py --in <media> --out <file.srt> [--language bn] [--model small]

Backends, in order:
  1. faster-whisper (Python package) — preferred.
  2. the `whisper` CLI (openai-whisper) if it is on PATH.
  3. Neither: prints exactly what is missing and how to install it,
     then exits 3. Nothing is faked — no backend, no transcript.

Exit codes: 0 = SRT written, 2 = bad input / backend failure, 3 = no backend.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import srt_parse

INSTALL_HINT = (
    "No Whisper backend available. Install one of:\n"
    "  python3 -m pip install faster-whisper   (preferred)\n"
    "  python3 -m pip install openai-whisper    (provides the `whisper` CLI)\n"
    "Then re-run this command."
)


def have_faster_whisper():
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def format_srt(segments):
    """segments: iterable of (start_sec, end_sec, text). Returns SRT text."""
    blocks = []
    for i, (start, end, text) in enumerate(segments, 1):
        blocks.append(
            f"{i}\n{srt_parse.fmt_time(start)} --> {srt_parse.fmt_time(end)}\n"
            f"{text.strip()}\n")
    return "\n".join(blocks)


def transcribe_faster_whisper(media, language, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name)
    segments, _info = model.transcribe(
        str(media), language=language or None, beam_size=5)
    return [(s.start, s.end, s.text) for s in segments]


def transcribe_whisper_cli(media, language, model_name, out_path):
    """Run the openai-whisper CLI; it writes <stem>.srt next to the output."""
    with tempfile.TemporaryDirectory() as td:
        cmd = ["whisper", str(media), "--output_format", "srt",
               "--output_dir", td, "--model", model_name]
        if language:
            cmd += ["--language", language]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        produced = Path(td) / (media.stem + ".srt")
        if proc.returncode != 0 or not produced.is_file():
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
            print("Error: whisper CLI failed:\n" + "\n".join(tail),
                  file=sys.stderr)
            return False
        out_path.write_text(produced.read_text(encoding="utf-8"),
                            encoding="utf-8")
        return True


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Transcribe audio/video to SRT (faster-whisper or whisper CLI).")
    p.add_argument("--in", dest="media", required=True, help="Input audio/video file")
    p.add_argument("--out", required=True, help="Output .srt file")
    p.add_argument("--language", default="bn",
                   help="Language code (default: bn; empty string = auto-detect)")
    p.add_argument("--model", default="small",
                   help="Whisper model name (default: small)")
    args = p.parse_args(argv)

    media = Path(args.media)
    if not media.is_file():
        print(f"Error: input file not found: {media}", file=sys.stderr)
        return 2
    out_path = Path(args.out)
    language = args.language or None

    if have_faster_whisper():
        try:
            segments = transcribe_faster_whisper(media, language, args.model)
        except Exception as e:  # model download / decode failure etc.
            print(f"Error: faster-whisper failed: {e}", file=sys.stderr)
            return 2
        try:
            out_path.write_text(format_srt(segments), encoding="utf-8")
        except OSError as e:
            print(f"Error: cannot write {out_path}: {e}", file=sys.stderr)
            return 2
        print(f"Transcribed {len(segments)} segments -> {out_path} "
              f"(backend: faster-whisper, model: {args.model})")
        return 0

    if shutil.which("whisper"):
        if transcribe_whisper_cli(media, language, args.model, out_path):
            print(f"Transcribed -> {out_path} "
                  f"(backend: whisper CLI, model: {args.model})")
            return 0
        return 2

    print(INSTALL_HINT, file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())
