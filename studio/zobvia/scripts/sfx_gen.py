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
PEAK = 0.708

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
        out.append(math.sin(phase) * math.exp(-t * 28)
                   + 0.3 * math.sin(2 * phase) * math.exp(-t * 40))
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

def gen_riser_py():
    dur = 0.80; n = int(dur * SR); out = []; phase = 0.0
    for i in range(n):
        t = i / SR; frac = t / dur
        f = 180 * ((1400 / 180) ** frac)
        phase += 2 * math.pi * f / SR
        env = frac ** 1.5
        out.append((math.sin(phase) + 0.25 * math.sin(2 * phase)) * env)
    return out

def gen_sparkle_py():
    dur = 0.50; n = int(dur * SR); out = []
    notes = [1568, 2093, 2637, 3136]
    starts = [0.0, 0.09, 0.18, 0.27]
    for i in range(n):
        t = i / SR; total = 0.0
        for freq, start in zip(notes, starts):
            if t >= start:
                dt = t - start
                total += (math.sin(2 * math.pi * freq * dt)
                          + 0.3 * math.sin(2 * math.pi * freq * 2 * dt)) * math.exp(-dt * 14)
        out.append(total)
    return out

def gen_ding_py():
    n = int(0.60 * SR); out = []
    f0 = 1046.5
    for i in range(n):
        t = i / SR
        out.append((math.sin(2 * math.pi * f0 * t)
                    + 0.4 * math.sin(2 * math.pi * f0 * 2.76 * t)
                    + 0.15 * math.sin(2 * math.pi * f0 * 5.4 * t)) * math.exp(-t * 6))
    return out

def gen_shutter_py():
    rng = random.Random(23); n = int(0.15 * SR); out = []; prev = 0.0
    for i in range(n):
        t = i / SR
        white = rng.uniform(-1, 1)
        hp = white - prev; prev = white
        in_burst = (0.0 <= t < 0.02) or (0.07 <= t < 0.095)
        out.append(hp if in_burst else 0.0)
    return out

def gen_boom_soft_py():
    rng = random.Random(31); dur = 0.70; n = int(dur * SR); out = []; phase = 0.0; state = 0.0
    for i in range(n):
        t = i / SR; frac = t / dur
        f = 60 + (34 - 60) * frac
        phase += 2 * math.pi * f / SR
        attack = min(t / 0.03, 1.0) if t < 0.03 else 1.0
        env = attack * math.exp(-t * 4.5)
        # lowpassed noise swell
        state += 0.05 * (rng.uniform(-1, 1) - state)
        noise = state * 3.0
        out.append((math.sin(phase) + 0.25 * noise) * env)
    return out

PY_GENS = {"pop": gen_pop_py, "click": gen_click_py, "whoosh": gen_whoosh_py,
           "pluck": gen_pluck_py, "chime": gen_chime_py, "swipe": gen_swipe_py, "thud": gen_thud_py,
           "riser": gen_riser_py, "sparkle": gen_sparkle_py, "ding": gen_ding_py,
           "shutter": gen_shutter_py, "boom-soft": gen_boom_soft_py}

# ---------- numpy generators ----------

def _np_t(dur):
    return np.arange(int(dur * SR)) / SR

def gen_pop_np():
    t = _np_t(0.12); f = 300 + 500 * np.exp(-t * 25)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(phase) * np.exp(-t * 28)
            + 0.3 * np.sin(2 * phase) * np.exp(-t * 40)).tolist()

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

def gen_riser_np():
    dur = 0.80; t = _np_t(dur); frac = t / dur
    f = 180 * ((1400 / 180) ** frac)
    phase = 2 * np.pi * np.cumsum(f) / SR
    env = frac ** 1.5
    return ((np.sin(phase) + 0.25 * np.sin(2 * phase)) * env).tolist()

def gen_sparkle_np():
    dur = 0.50; t = _np_t(dur); out = np.zeros(len(t))
    notes = [1568, 2093, 2637, 3136]
    starts = [0.0, 0.09, 0.18, 0.27]
    for freq, start in zip(notes, starts):
        dt = t - start
        mask = dt >= 0
        term = np.zeros(len(t))
        term[mask] = (np.sin(2 * np.pi * freq * dt[mask])
                      + 0.3 * np.sin(2 * np.pi * freq * 2 * dt[mask])) * np.exp(-dt[mask] * 14)
        out = out + term
    return out.tolist()

def gen_ding_np():
    t = _np_t(0.60); f0 = 1046.5
    return ((np.sin(2 * np.pi * f0 * t)
             + 0.4 * np.sin(2 * np.pi * f0 * 2.76 * t)
             + 0.15 * np.sin(2 * np.pi * f0 * 5.4 * t)) * np.exp(-t * 6)).tolist()

def gen_shutter_np():
    rng = np.random.default_rng(23); n = int(0.15 * SR); t = _np_t(0.15)
    white = rng.uniform(-1, 1, n); hp = np.diff(white, prepend=0)
    env = np.zeros(n)
    env[(t >= 0.0) & (t < 0.02)] = 1.0
    env[(t >= 0.07) & (t < 0.095)] = 1.0
    return (hp * env).tolist()

def gen_boom_soft_np():
    rng = np.random.default_rng(31); dur = 0.70; n = int(dur * SR); t = _np_t(dur)
    f = 60 + (34 - 60) * (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    attack = np.minimum(t / 0.03, 1.0)
    env = attack * np.exp(-t * 4.5)
    noise = rng.uniform(-1, 1, n); lp = np.zeros(n); state = 0.0
    for i in range(n):
        state += 0.05 * (noise[i] - state); lp[i] = state
    noise_term = lp * 3.0
    return ((np.sin(phase) + 0.25 * noise_term) * env).tolist()

NP_GENS = {"pop": gen_pop_np, "click": gen_click_np, "whoosh": gen_whoosh_np,
           "pluck": gen_pluck_np, "chime": gen_chime_np, "swipe": gen_swipe_np, "thud": gen_thud_np,
           "riser": gen_riser_np, "sparkle": gen_sparkle_np, "ding": gen_ding_np,
           "shutter": gen_shutter_np, "boom-soft": gen_boom_soft_np}

ALL_SOUNDS = list(PY_GENS.keys())

def normalise(samples):
    peak = max((abs(s) for s in samples), default=0.0)
    if peak == 0:
        return samples
    scale = PEAK / peak
    scaled = [s * scale for s in samples]
    # Micro fade (raised ramp) over first and last ~64 samples to
    # remove boundary clicks.
    n = len(scaled)
    fade = min(64, n // 2)
    if fade > 0:
        for i in range(fade):
            factor = 0.5 * (1 - math.cos(math.pi * i / fade))
            scaled[i] = scaled[i] * factor
            scaled[n - 1 - i] = scaled[n - 1 - i] * factor
    return scaled

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
