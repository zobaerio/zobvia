# Bengali Text Rules

Binding for any CREATE job whose SRT is Bengali or mixed
Bengali/Latin, and for caption analysis of Bengali videos in LEARN.
Bengali is a conjunct-heavy abugida: shaping happens at the grapheme
cluster, not the letter. Breaking a cluster breaks the word visually.

## Font

- **Default: Hind Siliguri** — load with
  `@remotion/google-fonts/HindSiliguri`. Clean, neutral, full conjunct
  support, weights 300–700.
- Alternatives (pick one, only if the style demands it):
  - **Anek Bangla** — wider, more contemporary; good for bold headlines.
  - **Baloo Da 2** — rounded, friendly; good for education/kids topics.
  - **Noto Sans Bengali** — safest fallback for rare conjuncts; neutral.
- **One font family per video** (Hard Rule 9). Weight variation within
  the family is allowed; a second family is not.
- Always load the weights actually used (400/600/700 typical) and wait
  for font load before rendering (`delayRender` / `continueRender`
  pattern from `@remotion/google-fonts`).

## Segmentation — the core rule

- Segment text with the grapheme cluster API:

  ```ts
  const seg = new Intl.Segmenter("bn", { granularity: "grapheme" });
  const clusters = [...seg.segment(text)].map((s) => s.segment);
  ```

- **Animate syllables (grapheme clusters), never letters.** Splitting
  by code point, code unit, or `.split("")` tears conjuncts and vowel
  signs off their base consonant and produces broken glyphs on screen.
- Word-by-word animation splits on word boundaries first, then treats
  each word as an indivisible cluster sequence. A word is never split
  mid-cluster for a stagger effect; stagger whole words instead.

## Layout

- **`letterSpacing: 0` — always.** Any non-zero tracking disconnects
  vowel signs and conjuncts visually. This includes "just a little"
  values like `0.02em`. Zero, no exceptions.
- **Line breaks only at word boundaries.** Never break inside a word,
  never hyphenate Bengali. If a word does not fit, reduce font size or
  rebalance lines — do not split the word.
- Keep dependent vowel signs and the hasant (্) attached by relying on
  the browser/Remotion text shaper: pass whole words as single text
  nodes; never wrap individual clusters in separate `<span>`s with
  margins or transforms that break shaping. For per-word animation,
  transform the whole word's wrapper only.
- Line height: 1.25–1.45 for Bengali body text — conjuncts stack
  vertically (e.g. স্ত্র) and clip at tighter leading.
- Text alignment: left for multi-line body, centre for single-line
  statements. Bengali has no justification tradition on screen; do not
  use `text-align: justify`.

## Conjunct test set

Render these seven clusters and eyeball them before any render. If any
renders as separated pieces or with a visible hasant where the
conjunct should fuse, the font/shaping path is broken — stop and fix
(font or segmentation), do not ship around it.

| Cluster | Example word | Note |
|---|---|---|
| ক্ষ | ক্ষমতা | ক + ্ + ষ fused |
| জ্ঞ | জ্ঞান | জ + ্ + ঞ fused |
| ষ্ণ | কৃষ্ণ | ষ + ্ + ণ |
| জ্র | বজ্র | জ + ্ + র (ra-phala below) |
| ন্দ্র | কেন্দ্র | ন + ্ + দ + ্ + র, double conjunct |
| স্ত্র | স্ত্রী | স + ্ + ত + ্ + র, triple stack |
| ষ্ট্র | রাষ্ট্র | four-part stack, tallest glyph |

## Mixed Latin inside Bengali

- Latin words (app names, English terms, brand names) render in the
  same font family — Hind Siliguri includes Latin glyphs. Do not switch
  families for Latin words.
- **Latin words get +4–6% font size** relative to surrounding Bengali
  text: Latin glyphs sit visually smaller at equal point size. Apply
  per word via a wrapper with `fontSize: "1.05em"` (use 1.04–1.06).
- Numbers: keep the numeral system of the SRT. If the SRT uses Bengali
  digits (০১২৩৪৫৬৭৮৯), keep them; if it uses Latin digits, keep those.
  Never convert silently.
- Acronyms and URLs stay LTR inside the RTL-free Bengali line; Bengali
  is LTR, so no bidi handling is needed — do not set `dir="rtl"`.

## Emphasis

- Emphasise with **weight (700) + colour (accent) + scale** — the same
  mechanisms as Latin text, applied to whole words.
- Never emphasise by letter-spacing, stretching, or splitting a word.
- Underlines are acceptable but must sit below the full cluster stack:
  use `textUnderlineOffset` generous enough (≥ 0.18em) not to strike
  through descending conjunct parts.
- Italics: do not use synthetic oblique on Bengali — it distorts
  conjuncts. Use weight/colour instead.

## Punctuation

- The Bengali sentence terminator is the **danda `।`**, not the Latin
  full stop. Preserve the SRT's punctuation exactly — if the SRT uses
  `।`, render `।`; do not normalise it to `.` or vice versa.
- Question `?` and exclamation `!` are shared and kept as written.
- Bengali quotation marks follow the SRT; do not convert quotes.
- Ellipsis and dashes are kept as written. Never add punctuation the
  SRT does not contain (Hard Rule 5: no invented content).

## Do-not list

- Do not animate letter by letter (typewriter is forbidden for Bengali
  — see `animation-library.md`).
- Do not set any `letterSpacing` other than 0.
- Do not split words across lines, spans with gaps, or animation units.
- Do not use `.split("")`, code-point iteration, or regex character
  classes to segment Bengali text — `Intl.Segmenter("bn")` only.
- Do not mix two Bengali font families in one video.
- Do not apply synthetic italics/oblique or horizontal scaling.
- Do not convert digits, danda, or punctuation away from the SRT.
- Do not ship a render that has not passed the conjunct test set.
