# Color System

Colour is the one decision the user makes in CREATE (step B2). This
reference defines the palettes offered, the rules every palette obeys,
and how `scripts/color_palette.py` is used.

## Palette rules

- **Structure: primary + neutral + 1 accent.** The primary carries
  backgrounds/surfaces, the neutral carries text and quiet elements,
  the single accent carries highlights, emphasis words, and SFX-synced
  flashes. A second accent is not allowed.
- **Max 3 hues per video.** Shades/tints of the three hues are free;
  a fourth hue is not.
- **Contrast ≥ 4.5:1** for all text against its background (WCAG AA for
  normal text). Check every text/background pair in the chosen palette
  before building scenes; if a pair fails, darken/lighten within the
  same hue until it passes — do not swap in a new hue.
- **60 / 30 / 10 distribution:** ~60% neutral/primary ground, ~30%
  primary surfaces, ~10% accent. If the accent covers more than ~15%
  of a frame, it stops reading as emphasis.
- **Background discipline:** dark themes keep backgrounds at the
  anchor's dark value or darker; light themes keep text at the
  neutral's dark value. Never put accent-coloured body text on a
  mid-tone background.
- Learned styles override: a style skill's §6 palette replaces the
  anchor system for that job, but the contrast rule still applies —
  flag any failing pair in the delivery report rather than silently
  shipping it.

## The 11 tones

The 6 options offered in B2 are drawn from these tones, matched to the
SRT's topic. Each tone = an anchor primary, a neutral pairing, and an
accent behaviour.

| Tone | Feel | Anchor |
|---|---|---|
| Trust / Corporate | serious, reliable | Deep Navy |
| Creative / Premium | bold, high-end | Royal Purple |
| Nature / Health | calm, grounded | Forest Green |
| Urgent / Drama | intense, alert | Crimson |
| Energy / Optimism | warm, driven | Amber |
| Neutral / Serious | understated, editorial | Charcoal |
| Fresh / Tech | light, open | Sky |
| Playful / Social | friendly, warm | Coral |
| Earthy / Heritage | traditional, crafted | Sand |
| Calm / Analytical | cool, measured | Slate |
| Dark Stage | any topic, dark-mode pipelines (Dark Tech, Kinetic) | Charcoal as ground + topic accent |

## Anchor colours

| Name | Hex | Role in palette |
|---|---|---|
| Deep Navy | `#0A1929` | Primary (dark ground / surfaces) |
| Royal Purple | `#4C1D95` | Primary |
| Forest Green | `#064E3B` | Primary |
| Crimson | `#991B1B` | Primary or strong accent |
| Amber | `#B45309` | Primary or accent (dark enough for AA on white) |
| Charcoal | `#1F2937` | Neutral-dark (text on light, ground on dark) |
| Sky | `#0EA5E9` | Accent (on dark grounds; on white use only large/bold text — check contrast) |
| Coral | `#FB7185` | Accent on dark grounds only |
| Sand | `#D4A574` | Accent/surface on dark or charcoal grounds |
| Slate | `#475569` | Neutral-mid (secondary text, dividers) |

Standard neutrals paired with every anchor: background light
`#F8FAFC`, text dark `#1F2937` (Charcoal), text light `#F8FAFC`,
divider Slate at 40% opacity. These neutrals do not count against the
3-hue limit.

Contrast notes: Sky `#0EA5E9` on white is ~3.0:1 — fails for body text;
use it on Deep Navy/Charcoal grounds (~5.9:1) or darken it within-hue
for light grounds. Coral `#FB7185` on white fails similarly; dark
grounds only. Amber `#B45309` on white passes (~4.6:1).

## Using `scripts/color_palette.py`

```bash
# 6 topic-matched options for the B2 question (name + hex + meaning)
python scripts/color_palette.py --topic "personal finance" --lang bn

# Full palette (primary/neutral/accent + checked contrast pairs)
# for a chosen anchor, written into theme.ts values
python scripts/color_palette.py --anchor "#0A1929" --format json
```

- B2 always presents exactly 6 options from the script — never invent
  additional options or hex values in chat.
- After the user picks, re-run with `--anchor` to get the full derived
  palette and paste those exact values into `theme.ts`
  (`remotion-structure.md`). Hand-adjusting a hex after this point
  breaks the contrast verification — if a value must change, re-run
  the script.
- Meanings in the B2 question are one line each, in the SRT's language,
  describing what the colour signals (trust, energy, calm…) — not
  design instructions.
