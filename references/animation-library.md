# Animation Library

The complete motion vocabulary for CREATE, and the naming vocabulary
LEARN uses when describing a source video. All durations are frames at
30 fps. Easing default is ease-out cubic unless a row says otherwise.
Motion is applied to whole words/cards — for Bengali, always per
`bengali-text-rules.md` (syllables/words, never letters).

## Text animations (8)

| # | Name | Behaviour | Timing | Use for |
|---|---|---|---|---|
| 1 | **Word scale** (default) | Each word scales 0.85→1.0 with a 1-frame overshoot to 1.04, opacity 0→1 | 6f per word, **onset offset 3–6f** between words | Default word-by-word treatment for all narration text |
| 2 | Bounce pop | Word drops in from +18 px with spring overshoot, settles | 9f, spring (damping 12) | Playful/education topics, single emphasis words |
| 3 | Line mask reveal | Whole line revealed by a clip mask sweeping left→right (LTR) | 10–14f per line | Headlines, section titles, quotes |
| 4 | Highlight sweep | Background colour box sweeps behind an already-visible word/phrase | 8f sweep | Marking the key phrase after it is read |
| 5 | Gradient shift | Text fill gradient animates position/hue across the word | 20–30f loop or one pass | Single hero word, logo-like statements |
| 6 | Typewriter | Characters appear one by one with a caret | 2f per character | **Chat/code/terminal scenes only. Never for Bengali** (breaks conjuncts) and never for narration captions |
| 7 | Counter roll | Digits roll vertically to the final number | 18–24f, ease-out | Statistics, prices, counts — pair with soft pluck SFX at landing |
| 8 | Kinetic emphasis | One word scales to 1.35×, shifts to accent colour, slight −2° rotation, then settles at 1.1× | 8f in, hold, no exit anim | The 1–2 emphasis words per cue: numbers, names, negations |

Rules for text: one primary text animation per scene; word scale is the
fallback whenever a scene's choice is unclear; emphasis (8) is layered
on top of the scene's base animation, never a replacement for it.

## Card / UI animations (6)

| # | Name | Behaviour | Timing |
|---|---|---|---|
| 1 | Card rise | Card translates +40 px → 0, opacity 0→1, shadow grows in | 12f |
| 2 | Card flip-in | RotateX 18° → 0 with perspective, opacity in | 14f |
| 3 | Stagger stack | List of cards/items enter one by one, card-rise each | 5f offset per item |
| 4 | Draw-on | SVG path stroke draws itself (`strokeDashoffset`) | Length-dependent, ~20–30f |
| 5 | Bar grow | Bar/scale fills from 0 to value width, label counts up | 20f, synced |
| 6 | Pulse ring | Ring expands from an element and fades; draws the eye once | 15f, max 2 per scene |

## Transitions (6)

Frame counts are total transition length; both scenes are visible
during non-cut transitions.

| # | Name | Frames | Use |
|---|---|---|---|
| 1 | Hard cut | 0f | Default. Topic continues, next point, most cuts |
| 2 | Slide push | 8f | Next item in a sequence, carousel advance |
| 3 | Zoom through | 10f | Diving into a detail, subject scale change |
| 4 | Mask wipe | 10f | Before/after, section change with a shape motif |
| 5 | Cross dissolve | 8f | Mood shift only — rare in motion-graphics explainers |
| 6 | Whip pan | 7f | High-energy section change, with swipe SFX |

## Usage rules

- **~80% of transitions are hard cuts.** In a typical explainer: hard
  cut 80%, slide push 10%, everything else 10% combined. If a timeline
  has more than 1 in 4 non-cut transitions, simplify it.
- A transition must be earned by a meaning change (new section, new
  item, reveal). Same-topic continuation = hard cut.
- Never use two different non-cut transitions back to back.
- Every non-cut transition gets its mapped SFX (`sfx-library.md`);
  hard cuts get SFX only when the landing element itself has an event.
- Exit animations are usually skipped: elements leave by cut or by the
  next transition. An element that animates in *and* out doubles the
  motion budget — allow it for hero elements only.
- Hold still: after an entrance completes, the scene holds static for
  at least 40% of its duration. Constant motion reads as noise.
- Learned styles override these proportions: if a style skill's §3
  says 100% hard cuts, the video uses 100% hard cuts.
