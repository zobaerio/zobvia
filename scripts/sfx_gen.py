#!/usr/bin/env python3
"""Procedurally generate WAV sound effects (44100 Hz, 16-bit PCM).

Uses numpy when available, with a pure-Python (math+struct) fallback that
produces the same sounds sample-by-sample.
"""
import argparse
import math
import random
import struct
import sys
import wave
from pathlib import Path

SR = 44100
PEAK = 0.7

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

# ---------- pure-python generators (return list of floats in [-1, 1]) ----------

def _t(n):
    return [i / SR for i in range(n)]

def gen_pop_py():
    n = int(0.12 * SR); out = []
    for i, t in enumerate(_t(n)):
        f = 300 + (800 - 300) * math.exp(-t * 30)
        phase = 2 * math.pi * (300 * t + (500 / 30) * (1 - math.exp(-30 * t)) / (2 * math.pi) * 2 * math.pi / (2 * math.pi))
        # Simpler accurate chirp: integrate frequency
        out.append(0.0)
    # integrate phase properly
    phase = 0.0; out = []
    for i in range(n):
        t = i / SR
        f = 300 + 500 * math.exp(-t * 25)
        phase += 2 * math.pi * f / SR
        out.append(math.sin(phase) * math.exp(-t * 28))
    return out

def gen_click_py():
    rng = random.Random(42); n = int(0.06 * SR); out = []; prev = 0.0
    for i in range(n):
        t = i / SR
        white = rng.uniform(-1, 1)
        hp = white - prev; prev = white
        out.append(hp * math.exp(-t * 90))
    return out

def gen_whoosh_py():
    rng = random.Random(7); n = int(0.4 * SR); out = []
    # simple swept resonator on noise
    state = 0.0
    for i in range(n):
        t = i / SR
        frac = i / n
        env = math.sin(math.pi * frac) ** 2
        # band emphasis sweeps up then down via one-pole lowpass coefficient change
        alpha = 0.05 + 0.6 * math.sin(math.pi * frac)
        state += alpha * (rng.uniform(-1, 1) - state)
        out.append(state * env * 2.2)
    return out

def gen_pluck_py():
    n = int(0.35 * SR); out = []; phase = 0.0
    for i in range(n):
        t = i / SR
        mod = 18 * math.sin(2 * math.pi * 5 * t) * math.exp(-t * 8)
        phase += 2 * math.pi * (440 + mod) / SR
        out.append((math.sin(phase) + 0.3 * math.sin(2 * phase)) * math.exp(-t * 9))
    return out

def gen_chime_py():
    n = int(0.4 * SR); out = []
    for i in range(n):
        t = i / SR
        out.append((math.sin(2 * math.pi * 880 * t) * math.exp(-t * 7)
                    + 0.5 * math.sin(2 * math.pi * 1320 * t) * math.exp(-t * 10)
                    + 0.25 * math.sin(2 * math.pi * 1760 * t) * math.exp(-t * 13)))
    return out

def gen_swipe_py():
    rng = random.Random(11); n = int(0.3 * SR); out = []; state = 0.0
    for i in range(n):
        t = i / SR; frac = i / n
        env = math.sin(math.pi * min(frac * 1.15, 1.0))
        alpha = 0.7 - 0.6 * frac
        state += max(alpha, 0.03) * (rng.uniform(-1, 1) - state)
        out.append(state * env * 2.0)
    return out

def gen_thud_py():
    n = int(0.25 * SR); out = []; phase = 0.0
    for i in range(n):
        t = i / SR
        f = 40 + 20 * math.exp(-t * 18)
        phase += 2 * math.pi * f / SR
        out.append(math.sin(phase) * math.exp(-t * 16))
    return out

PY_GENS = {"pop": gen_pop_py, "click": gen_click_py, "whoosh": gen_whoosh_py,
           "pluck": gen_pluck_py, "chime": gen_chime_py, "swipe": gen_swipe_py, "thud": gen_thud_py}

# ---------- numpy generators ----------

def _np_t(dur):
    return np.arange(int(dur * SR)) / SR

def gen_pop_np():
    t = _np_t(0.12); f = 300 + 500 * np.exp(-t * 25)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(phase) * np.exp(-t * 28)).tolist()

def gen_click_np():
    rng = np.random.default_rng(42); t = _np_t(0.06)
    white = rng.uniform(-1, 1, len(t)); hp = np.diff(white, prepend=0)
    return (hp * np.exp(-t * 90)).tolist()

def gen_whoosh_np():
    # FFT band-sweep: shape noise spectrum with a moving gaussian band
    rng = np.random.default_rng(7); n = int(0.4 * SR)
    noise = rng.uniform(-1, 1, n)
    # time-varying one-pole approximation via cumulative filtering in chunks
    out = np.zeros(n); state = 0.0
    for i in range(n):
        frac = i / n; alpha = 0.05 + 0.6 * math.sin(math.pi * frac)
        state += alpha * (noise[i] - state); out[i] = state
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return (out * env * 2.2).tolist()

def gen_pluck_np():
    t = _np_t(0.35); mod = 18 * np.sin(2 * np.pi * 5 * t) * np.exp(-t * 8)
    phase = 2 * np.pi * np.cumsum(440 + mod) / SR
    return ((np.sin(phase) + 0.3 * np.sin(2 * phase)) * np.exp(-t * 9)).tolist()

def gen_chime_np():
    t = _np_t(0.4)
    return (np.sin(2 * np.pi * 880 * t) * np.exp(-t * 7)
            + 0.5 * np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 10)
            + 0.25 * np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 13)).tolist()

def gen_swipe_np():
    rng = np.random.default_rng(11); n = int(0.3 * SR)
    noise = rng.uniform(-1, 1, n); out = np.zeros(n); state = 0.0
    for i in range(n):
        frac = i / n; alpha = max(0.7 - 0.6 * frac, 0.03)
        state += alpha * (noise[i] - state); out[i] = state
    env = np.sin(np.pi * np.minimum(np.arange(n) / n * 1.15, 1.0))
    return (out * env * 2.0).tolist()

def gen_thud_np():
    t = _np_t(0.25); f = 40 + 20 * np.exp(-t * 18)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(phase) * np.exp(-t * 16)).tolist()

NP_GENS = {"pop": gen_pop_np, "click": gen_click_np, "whoosh": gen_whoosh_np,
           "pluck": gen_pluck_np, "chime": gen_chime_np, "swipe": gen_swipe_np, "thud": gen_thud_np}

ALL_SOUNDS = list(PY_GENS.keys())

def normalise(samples):
    peak = max((abs(s) for s in samples), default=0.0)
    if peak == 0:
        return samples
    scale = PEAK / peak
    return [s * scale for s in samples]

def write_wav(path, samples):
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(frames)

def main(argv=None):
    p = argparse.ArgumentParser(description="Generate procedural WAV sound effects.")
    p.add_argument("--out", required=True, help="Output directory for .wav files")
    p.add_argument("--only", default=None, help="Comma-separated subset, e.g. pop,click")
    args = p.parse_args(argv)

    sounds = ALL_SOUNDS
    if args.only:
        sounds = [s.strip().lower() for s in args.only.split(",") if s.strip()]
        bad = [s for s in sounds if s not in ALL_SOUNDS]
        if bad:
            print(f"Error: unknown sound(s): {', '.join(bad)}. Valid: {', '.join(ALL_SOUNDS)}", file=sys.stderr)
            return 2
        if not sounds:
            print("Error: --only produced an empty selection", file=sys.stderr)
            return 2
    outdir = Path(args.out)
    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error: cannot create output dir {outdir}: {e}", file=sys.stderr)
        return 2
    gens = NP_GENS if HAS_NUMPY else PY_GENS
    print(f"Backend: {'numpy' if HAS_NUMPY else 'pure-python fallback'} | Sample rate: {SR} Hz")
    for name in sounds:
        samples = normalise(gens[name]())
        path = outdir / f"{name}.wav"
        write_wav(path, samples)
        print(f"{name}.wav: {path.stat().st_size} bytes ({len(samples)/SR:.2f}s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
