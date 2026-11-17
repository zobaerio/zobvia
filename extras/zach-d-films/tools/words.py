#!/usr/bin/env python3
"""Word timings for the 3D explainer engine (Zobvia replacement for the
original kit's words.py, which was not part of the shared skill files).

    python3 words.py <voiceover.wav> [--model small] [--language bn]

Writes `<voiceover>.words.json` next to the audio: a JSON list of
{"w": word, "s": start_sec, "e": end_sec} — exactly the format
`engine/captions.py` consumes to build the CAPTIONS list for shots.js.

Uses faster-whisper (the same backend as Zobvia's scripts/transcribe.py).
Exit 2 on bad input, exit 3 when faster-whisper is not installed.
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description="Voiceover -> word timings JSON")
    p.add_argument("audio", help="Voiceover audio file (.wav/.mp3/...)")
    p.add_argument("--model", default="small",
                   help="faster-whisper model (default: small)")
    p.add_argument("--language", default=None,
                   help="Language code (default: auto-detect)")
    args = p.parse_args(argv)

    audio = Path(args.audio)
    if not audio.is_file():
        print(f"Error: audio file not found: {audio}", file=sys.stderr)
        return 2
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Error: faster-whisper is not installed. "
              "Install it with: pip install faster-whisper",
              file=sys.stderr)
        return 3

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        str(audio), language=args.language, word_timestamps=True)
    words = []
    for seg in segments:
        for w in (seg.words or []):
            text = (w.word or "").strip()
            if text:
                words.append({"w": text,
                              "s": round(float(w.start), 3),
                              "e": round(float(w.end), 3)})
    if not words:
        print("Error: no words recognised in the audio.", file=sys.stderr)
        return 2
    out = audio.with_suffix(".words.json")
    out.write_text(json.dumps(words, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"Wrote {out} ({len(words)} words, "
          f"last ends at {words[-1]['e']:.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
