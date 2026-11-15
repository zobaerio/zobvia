# Voiceover Workflow

## 1. Recording

- Quiet room, soft furnishings; mic 15–20 cm away, slightly off-axis; pop filter or foam cover.
- Record at 48 kHz / 24-bit WAV where possible. Phone recording is acceptable if close, quiet and consistent — consistency across a video matters more than gear.
- Record in one session per video; room tone changes between sessions are audible.
- Read from the final script (the same text that becomes the SRT). Mark emphasis words before recording.
- Leave 0.5 s silence at head/tail; record 10 s of room tone for edits.
- Slate each take ("take 2"), keep the best full take rather than stitching word-by-word.

## 2. Cleanup Chain (in order)

1. Trim silences/errors; keep natural breaths (removing all breaths sounds robotic).
2. High-pass filter 70–80 Hz (removes rumble/handling noise).
3. Noise reduction — light pass only; heavy NR creates watery artefacts. Fix the room before fixing in post.
4. De-ess 5–8 kHz if sibilance is harsh.
5. EQ: gentle presence lift 3–5 kHz for clarity on phone speakers; cut mud 250–400 Hz if boomy.
6. Compression 2:1–3:1, slow attack, for even level.
7. Loudness normalise last: **−14 LUFS integrated for YouTube/social video, −16 LUFS for podcast-style audio** (−19 LUFS mono podcast norm where a platform specifies it), true peak ≤ −1 dBTP.

## 3. TTS Options & Honesty

- TTS is allowed for drafts, accessibility versions and channels that openly use it. Options: platform/OS voices, Edge/Azure/Google neural voices, ElevenLabs-style services — check each service's licence for commercial use before a client job.
- **Disclosure:** never present TTS as a real human recording to a client; label AI voice where a platform requires it (YouTube altered/synthetic content disclosure for realistic voice). A client's own cloned voice requires their explicit consent.
- TTS in Bengali/Arabic: listen to the full render — conjunct, number and name pronunciation errors are common; fix via phonetic respelling in a *pronunciation copy*, never by editing the displayed captions.

## 4. Syncing VO to SRT

1. The SRT is the timing source of truth in CREATE mode. Generate/align SRT from the *final* VO, not the draft script.
2. If VO is recorded after SRT: retime captions to actual speech (word-level alignment tool or manual pass on emphasis words).
3. Caption in-time = when the word starts, not when the sentence was planned. Drift >200 ms is noticeable; >400 ms is a QC fail.
4. Speed changes: if VO is time-stretched, regenerate the SRT after stretching, never before.

## 5. PreviewAudio in Remotion

- Use a `PreviewAudio` composition: VO + SFX/music bed at delivery mix, with the caption track burned in, rendered at low resolution for fast review.
- Purpose: check sync, SFX masking and loudness *before* the full render. Listen on phone speaker + one headphone pass.
- Preview approval ≠ delivery: final render still runs the full QC checklist (`qc-checklist.md`).

## Common Mistakes

- Mixing voice under music at equal level — voice always wins; duck beds −12 to −18 dB.
- Normalising per-clip instead of per-programme (volume jumps between segments).
- Recording VO after captions are locked, then forcing captions onto mismatched speech.
- Peaking/clipping at record time — unfixable later. Keep peaks around −12 to −6 dB while recording.
- Different mic/room for a 10-second pickup line — re-record the whole paragraph instead.
