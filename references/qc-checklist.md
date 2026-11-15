# Pre-Delivery QC Checklist

Run every box, in order, on the **final export file** — not the timeline. Any fail = fix, re-render, re-check that section.

## Text & Language
- [ ] Every caption spell-checked in its own language (BN/EN/AR/HI), names and numbers verified against the brief/script
- [ ] Bengali conjuncts / Devanagari ligatures / Arabic shaping render intact — no broken clusters, no tofu boxes (□)
- [ ] No caption splits a word or grapheme cluster across lines; breaks fall at phrase boundaries
- [ ] No more than 2 caption lines; reading speed ≤20 cps (≤16 cps BN/AR)
- [ ] On-screen text (titles, cards, prices) matches the brief exactly — no invented handles, prices or offers

## Timing & Sync
- [ ] Captions sync to speech within ~200 ms throughout (spot-check start, middle, end + every scene change)
- [ ] Hook lands in frame 1–90 (first 3 s): no intro/logo/fade-in before it
- [ ] SFX hit their visual moments (impacts on cuts/reveals, pops on words) — none early/late by >2 frames
- [ ] No dead air >1.5 s except deliberate pauses; no clipped word starts/ends
- [ ] CTA present, timed as planned; end screen / loop point clean

## Audio
- [ ] Loudness −14 LUFS integrated, true peak ≤ −1 dBTP (podcast variant: −16 LUFS)
- [ ] Voice always intelligible over SFX/music; beds ducked; no SFX masks a key word
- [ ] No clipping, plosive blasts or unremoved mistakes in the VO
- [ ] Checked on a phone speaker AND headphones

## Visual
- [ ] All text/logos inside the platform safe zone; nothing under UI rails or progress bars
- [ ] Contrast passes on the brightest frame; captions readable at phone size
- [ ] No black frames, frozen frames, placeholder images or watermarked stock in the export
- [ ] Camera moves don't expose frame edges; no accidental letterbox/aspect mismatch
- [ ] Brand colours match the brief; one caption preset used consistently

## Export & Files
- [ ] Resolution / aspect / fps / codec / bitrate match `export-matrix.md` for the target platform
- [ ] File name follows `<slug>_<platform>_<aspect>_v<n>.mp4`
- [ ] SRT sidecar included where the platform uses it (YouTube long-form, LinkedIn, FB feed) and timed to this version
- [ ] `credits.txt` lists every music/SFX/image asset with licence + attribution; licence proofs in the project folder
- [ ] ZIP contains exactly: final video(s), SRT (if any), credits.txt, thumbnail (if in scope) — and the ZIP test-extracts cleanly
- [ ] Preview file was NOT delivered as the final (check resolution/CRF of the delivered file)
