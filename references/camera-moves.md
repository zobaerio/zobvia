# Camera Moves (Simulated in Remotion) — 14 Moves

All moves are transforms on stills/clips: `scale`, `translate`, rotation, blur. Ease in/out unless stated. Percentages are of frame width/height.

| # | Move | Parameters | Usage rules |
|---|---|---|---|
| 1 | Punch-In | Scale 100%→115% in 6 f, hard ease-out; or instant cut 100%→130% | Emphasis word, punchline, hook. Max 3–4 per minute. |
| 2 | Slow Zoom In | Scale 100%→108–112% over 90–180 f, linear/ease-in-out | Talking head / explainer default life; invisible but alive. |
| 3 | Slow Zoom Out | Scale 115%→100% over 120–240 f | Reveal context, endings, reflective beats. |
| 4 | Pan | Translate X ±5–10% over 90–150 f, scale pre-set 110% (headroom) | Wide photos, group shots, documents. Never pan beyond source edges. |
| 5 | Ken Burns | Combined pan + zoom: scale 100%→112%, translate ±4% over the full clip duration | Photos in documentary/wedding/travel. One direction per photo; alternate directions. |
| 6 | Parallax Layers | BG scale 105% slow, FG scale 115% faster, opposite translate 1–3% | Layered graphics, product, titles. Needs separated layers; subtle or it looks fake. |
| 7 | Dolly-Sim (scale+translate) | Scale 100%→120% + translate toward subject 3–5% over 60–120 f | Simulates push-in on stills; centre the subject or drift looks accidental. |
| 8 | Handheld Shake (subtle) | Translate ±0.3–0.6%, rotation ±0.3°, noise-driven, continuous | Vlog/UGC realism on locked graphics. Subtle only — if viewers notice it, halve it. Never on text-heavy frames. |
| 9 | Orbit (3D carousel) | rotateY −18°→+18° or full card carousel, perspective 1000–1400 px, 45–90 f per item | Product cards, portfolio, app features. Keep text faces front-on at rest. |
| 10 | Tilt Reveal | Translate Y +8%→0 + scale 105%→100%, 20–30 f, ease-out | Revealing lists, lower-thirds, locations (tilt up = reveal). |
| 11 | Rack-Focus Blur Shift | Layer A blur 12→0 px while layer B blur 0→12 px, 15–25 f | Shift attention between foreground/background graphics or two products. |
| 12 | Static Lock-Off | No movement at all | Data, charts, captions-heavy teaching, legal/corporate. Stillness = authority; don't move everything. |
| 13 | Snap Zoom | Scale 100%→140% in 4–5 f, ease-in, + tiny overshoot 142%→140% | Pattern interrupt, hook, surprise reveal. Pair with impact SFX. Max 2 per video. |
| 14 | Vertical Rise / Crane-Sim | Translate Y −6%→+2% with scale 110%→104% over 120–180 f | Real-estate, buildings, monuments; slow and smooth only. |

## Rules

- **Headroom:** any move needs source overscan — start scaled ≥ the maximum travel, or edges show black.
- **Text safety:** never move a frame while small text must be read, except Slow Zoom ≤108%.
- **One move per shot.** Stacking pan + shake + zoom reads as amateur.
- **Easing:** ease-out for entrances/reveals, ease-in-out for continuous moves, linear only for Ken Burns on photos.
- **Match the energy:** move speed follows genre pacing (see `genre-recipes.md`) — documentary slow, gaming/shorts fast.
- In Remotion: drive everything from `useCurrentFrame()` + `interpolate()` with `extrapolateLeft/Right: 'clamp'`; use a seeded noise/pseudo-random function for shake so renders are deterministic.
