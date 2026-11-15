# Project Workflow

## Folder Structure (per client job)

```
<client>-<project-slug>/
  00_brief/         brief form, brand assets, references, licence proofs
  01_script/        script-v1.md, script-final.md
  02_srt/           captions.srt (final, timed to final VO)
  03_assets/        footage/, images/, fonts/, licences/
  04_audio/         vo-final.wav, sfx/, music/ (licensed only)
  05_remotion/      the Remotion project (src/, public/)
  06_previews/      preview-v1.mp4, preview-v2.mp4
  07_delivery/      final exports + credits.txt
  08_archive/       zips of delivered versions
  notes.md          decisions, client feedback log, style-skill name used
```

## Naming Conventions

- Files: lowercase kebab-case, no spaces: `hook-intro-v2.mp4`, `captions-final.srt`.
- Exports: `<slug>_<platform>_<aspect>_v<n>.mp4` — e.g. `boq-basics_yt_16x9_v1.mp4`, `boq-basics_shorts_9x16_v1.mp4`.
- Versions: `v1, v2, v3…` — increment on every client-visible change. Never `final-final`, never overwrite a sent file.
- Learned style skills: named, versioned files (`styles/<creator>-style-v1.md`) — a re-learn creates `v2`; **never overwrite a style skill**, so any past video stays reproducible.

## Flow: Brief → Delivery

1. **Brief** — complete `client-brief-template.md`; no brief, no start. Confirm platform, duration, language, ONE colour question per CREATE mode rules.
2. **Script** — draft → client approval of words before any timing work.
3. **SRT** — time captions to the final VO/script; SRT is the timeline source of truth.
4. **Timeline build** — Remotion composition: hook → body (SFX pass, captions, moves) → CTA/outro.
5. **Preview** — low-res PreviewAudio render → client review. Log feedback in `notes.md` with timestamps.
6. **Revision** — apply the agreed rounds (see `freelancer-pricing.md` revision policy); each round = new version number.
7. **QC** — full pass of `qc-checklist.md`. No checklist, no delivery.
8. **Delivery** — exports per `export-matrix.md` + SRT sidecar where applicable + `credits.txt`, zipped per `delivery-protocol` (core reference).

## Backup Rules

- The Remotion project + SRT + final VO are the irreplaceable trio — back them up off-machine (cloud or second drive) at every version.
- Keep delivered ZIPs in `08_archive/` at least 90 days (or the period agreed with the client).
- Never delete source footage until the client confirms delivery *and* the archive ZIP opens cleanly (test-extract it).
- Style skills and fonts are reusable assets — they live outside the job folder and are backed up with the skill itself.
