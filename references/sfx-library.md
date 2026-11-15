# SFX Library

CREATE output is **SFX only — no music track, ever** (Hard Rule 8).
Sound exists to punctuate visual events, not to fill silence. Voice
( if supplied as `public/voiceover.mp3`) and SFX are the whole mix.

## The 12 sound types

Durations are targets for the trimmed file; volumes are peak levels in
the final mix relative to full scale, assuming voice peaks near
−6 dBFS. Generated sounds come from `scripts/sfx_gen.py`; sourced
sounds must be trimmed/normalised to the same targets.

| # | Type | Character | Duration | Peak volume |
|---|---|---|---|---|
| 1 | Soft whoosh | Filtered noise sweep, airy, no pitch centre | 0.25–0.45 s | −20 to −16 dBFS |
| 2 | Light pop | Short sine burst with fast decay, playful | 0.06–0.12 s | −18 to −14 dBFS |
| 3 | Crisp click | High-passed transient, UI-like, dry | 0.03–0.06 s | −16 to −12 dBFS |
| 4 | Soft pluck | Single muted string/note, warm, pitched | 0.15–0.30 s | −20 to −16 dBFS |
| 5 | Chime | Two-note bell (fifth), bright, sparse use | 0.40–0.80 s | −20 to −17 dBFS |
| 6 | Swipe | Faster, narrower whoosh, directional feel | 0.15–0.25 s | −19 to −15 dBFS |
| 7 | Soft thud | Low sine + noise thump, grounded, no boom | 0.12–0.25 s | −17 to −13 dBFS |
| 8 | Riser | Rising pitch sweep, tension builder, builds anticipation | 0.80 s | −20 to −16 dBFS |
| 9 | Sparkle | Four bright notes cascading, magical twinkle | 0.50 s | −20 to −16 dBFS |
| 10 | Ding | Clear bell tone, clean partials, notification-like | 0.60 s | −20 to −17 dBFS |
| 11 | Shutter | Two crisp high-passed noise bursts, camera-like | 0.15 s | −18 to −14 dBFS |
| 12 | Soft boom | Low sine drop with soft noise swell, cinematic weight, never harsh | 0.70 s | −17 to −13 dBFS |

## Event mapping

One sound family per event type, used consistently through the video:

| Visual event | Sound |
|---|---|
| Word highlight / emphasis word lands | Light pop |
| New scene, hard cut with scale change | Soft whoosh |
| Slide / push transition | Swipe |
| Card or panel enters | Soft whoosh (large) or light pop (small) |
| List item ticks in, bullet appears | Crisp click |
| Number counter finishes, stat lands | Soft pluck |
| Checklist item completes | Soft pluck |
| Key reveal, final answer, section payoff | Chime |
| Statement card slams in, before/after lands | Soft thud |
| Button-like UI element activates | Crisp click |
| Section change / big transition | Riser |
| Light reveal / magic moment | Sparkle |
| Notification / CTA button / reminder | Ding |
| Photo change in a slideshow | Shutter |
| Cinematic statement landing | Soft boom |

If an event is not in this table, map it to the nearest row and record
the choice in `out/timeline.md`. Do not introduce a 13th sound type
mid-video — stick to the 12-type library above.

## Rules

- **No music.** No background track, no bed, no loop — even at low
  volume. If the user supplies music, decline that asset and note it;
  the rule has no exceptions.
- **Density: 5–7 SFX events per 60 s.** Fewer feels empty; more feels
  like a cartoon. Count events in the timeline before rendering.
- **Same sound = same event.** A pop always means the same class of
  thing. Variation is allowed only as ±10% playback-rate/volume jitter
  so repeats do not sound machine-identical.
- **Lock to the frame.** The SFX onset sits on the exact frame the
  visual event lands — not a frame early for "anticipation" unless the
  learned style's SFX map says so.
- **No clipping.** Master peak ≤ **−1 dBFS**. Check the rendered audio;
  stacked SFX + voice peaks are the usual cause (see
  `troubleshooting.md`).
- **One SFX at a time** except a deliberate transition+landing pair
  (swipe into thud). Overlapping tails of long sounds (chime) must be
  faded before the next event if they mask speech.
- **Silence is allowed.** Not every cut needs a sound; un-scored cuts
  are what make scored moments register.

## Sound design

- **Peak-normalised generation.** Generated WAVs are peak-normalised
  to −3 dBFS (peak 0.708) for consistent loudness across types, with
  no clipping. The final mix master stays ≤ −1 dBFS.
- **Voice-first rule.** SFX sit under the voice — they punctuate, they
  never compete. Keep density at 5–7 events per 60 s, duck SFX under
  speech where needed, and avoid masking speech frequencies or placing
  a loud event over a key spoken word.
- **Converter themes.** `scripts/create_video.py --sfx-theme` selects
  one of three themes: **soft** (the default UI set — whoosh, thud,
  pluck, chime with pop/click/swipe middles), **cinematic** (riser /
  boom-soft / whoosh / thud weight for hooks and statements), and
  **playful** (pop / sparkle / ding / pluck for light, energetic
  videos).

## Sourcing free sounds

Prefer generation (`scripts/sfx_gen.py`) for the synthetic types
(pop, click, pluck, thud, whoosh, swipe) — they are parameterised and
licence-clean. Source a chime (or any sound generation cannot produce
convincingly) from free libraries only, and record the source URL and
licence in `public/sfx/SOURCES.md`.

Search keywords that reliably find usable, licence-clear material:

| Type | Search keywords |
|---|---|
| Soft whoosh | `whoosh transition` on Openverse / Pixabay Sound Effects |
| Light pop | `pop ui` on Freesound (CC0 filter) / Pixabay |
| Crisp click | `click ui button` on Freesound (CC0 filter) |
| Soft pluck | `pluck string single note` on Openverse |
| Chime | `chime notification bell` on Pixabay / Freesound (CC0) |
| Swipe | `swipe fast` on Openverse / Pixabay |
| Soft thud | `soft thud impact` on Freesound (CC0 filter) |

Licence rules: CC0 or Pixabay/Openverse licence only; no
attribution-required sounds unless the attribution is written into
`public/sfx/SOURCES.md` and the delivery report; never lift a sound
from the LEARN source video or any creator's content.

## Code generation recipes

`scripts/sfx_gen.py` synthesises each type from parameters — call it
per sound rather than hand-writing synthesis code:

```bash
python3 scripts/sfx_gen.py --out public/sfx
python3 scripts/sfx_gen.py --out public/sfx --only pop,riser
python3 scripts/sfx_gen.py --out public/sfx --only pop,click,whoosh,pluck,chime,swipe,thud,riser,sparkle,ding,shutter,boom-soft
```

In Remotion, place sounds with `<Audio>` inside a `<Sequence>` whose
`from` is the event frame, and set `volume` from the table above
(convert dBFS to a 0–1 gain: −18 dBFS ≈ 0.126). Keep every SFX file
referenced by `out/timeline.md` present in `public/sfx/` before
rendering (CREATE step B8).
