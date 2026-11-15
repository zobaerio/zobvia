# Style Skill Template

Copy this file to `.claude/skills/style-<slug>/SKILL.md` in LEARN step
A7 and fill every field from measured analysis. Rules:

- Every field is a number, a frame count, a hex value, or `not measured`.
  Adjectives alone ("fast", "clean") are not valid values.
- Do not delete sections. An unmeasured section stays, marked
  `not measured`, so CREATE knows the gap is real.
- `<slug>`: kebab-case, from the creator name or dominant look.

---

```markdown
---
name: style-<slug>
description: "Editing style learned from <source: creator/channel + video title or file name>. Use when the user says 'edit in <slug> style' or asks for a video like <source>. Median shot <X>s, <N> cuts/min, <caption style>, <SFX density> SFX/min."
---

# Style: <Name>

Source: <URL or file path> · Duration: <sec> · Analysed: <date>
Full analysis: references/watch/<slug>/ (frames, pairs, cuts.json,
words.json, audio_profile.json, analysis/timeline.md, analysis/sfx-map.json)

## 1. Pacing

- Median shot length: <sec> · Mean: <sec> · Shortest/longest: <sec>/<sec>
- Cuts per minute: <n>
- Shot-length pattern: <e.g. hook shots 40% shorter than body; steady / accelerating / burst-pause>
- Pause usage: <silence or hold length in sec, where it occurs>
- Speed ramps: <present? factor, e.g. 1.25× on B-roll / not measured>

## 2. Framing

- Canvas: <WxH, aspect> · Subject scale: <% of frame height>
- Subject position: <centre / rule-of-thirds left / right, eye-line height %>
- Zoom: <frequency per min, magnitude e.g. 100%→115%, duration in frames, easing>
- Punch-ins: <trigger — emphasis word / cut / beat>
- Background treatment: <solid / blurred / gradient / set, hex if solid>
- Safe margins: <px or % on each side>

## 3. Transitions

- Hard cuts: <% of all cuts>
- Other types, each with share and duration in frames:
  <e.g. slide-push 20%, 8f · zoom-through 10%, 6f · mask wipe 5%, 10f>
- Transition triggers: <what earns a non-cut transition — topic change / list item / reveal>
- First transition at: <sec>

## 4. Captions

- Style: <word-by-word / phrase / full-line>
- Words per line: <n> · Lines per block: <n> · Max words on screen: <n>
- Position: <% from bottom> · Alignment: <centre / left>
- Font: <family resemblance, weight> · Size: <% of frame height>
- Colour: text <#hex> · Highlight <#hex> · Background box: <none / #hex at opacity>
- Highlight mechanism: <colour swap / scale <factor> / karaoke fill / box>
- Word onset offset: <frames between spoken word and highlight>
- Capitalisation / punctuation: <as spoken / stripped / added>

## 5. Overlays

- Lower thirds / name tags: <present? style, duration sec>
- Arrows, circles, highlights: <frequency per min, colour #hex, stroke px>
- Progress bar / chapter markers: <present? position, colour #hex>
- Logos / watermarks: <position, size %, opacity — note only, never copied>
- Emoji / stickers: <frequency per min, size %> (style note only)
- Screen recordings / B-roll inserts: <share of runtime, framing treatment>

## 6. Color

- Background: <#hex> · Text: <#hex> · Accent 1: <#hex> · Accent 2: <#hex>
- Palette sampled from frames at: <timestamps used>
- Contrast text/background: <ratio>:1
- Grade feel in numbers: <saturation ±%, exposure ±EV, temperature K shift — or not measured>
- Colour changes: <per section / constant through video>

## 7. Audio

- Voice loudness: <LUFS or dBFS peak> · Music relative to voice: <dB, or no music>
- Music: <present? feel, BPM if measured, drops out at <events>>
- SFX density: <events per 60 s>
- SFX map: analysis/sfx-map.json — top locks:
  <e.g. soft pop → word highlight · whoosh → slide transition · click → list item>
- Silence: <gap length sec before key lines / none>

## 8. Hook (0–3 s)

- Hook type: <question / bold claim / result-first / pattern interrupt / contradiction>
- First frame: <what is on screen at 0.0 s>
- First text on screen at: <sec> · Text size: <% of frame height>
- First cut at: <sec> · Cuts in first 3 s: <n>
- Spoken hook line (transcribed, for structure only — never reused): "<…>"
- Face/voice/text order: <which arrives first>

## 9. Ending (last 5 s)

- Ending type: <loop-back / CTA / recap / cliffhanger / abrupt>
- Last spoken line ends at: <sec> · Video ends at: <sec>
- CTA: <present? form — verbal / on-screen text / both>
- Loop connection: <last frame vs first frame — same / different / not measured>
- End card: <present? duration sec, contents>

## 10. Recipe

The ordered formula CREATE follows to reproduce this style:

1. Open: <hook construction, durations>
2. Body loop: <per-point pattern — shot length, caption behaviour, overlay rhythm>
3. Emphasis moments: <what changes — zoom, SFX, scale — and how often per min>
4. Section changes: <transition, sound, visual reset>
5. Close: <ending construction per §9>
- Pipelines (from style-pipelines.md) that best approximate this look:
  <1–3 names>
- Rhythm summary in one line of numbers:
  <e.g. 1.8 s shots · 3-word captions · 6 SFX/min · punch-in every ~9 s>

## 11. Do Not

- <Style-specific prohibitions, each tied to an observation —
  e.g. "Never hold a shot longer than 4 s", "No transitions other than
  hard cut and slide-push", "Captions never exceed 4 words",
  "No music under the hook", "Never centre the subject">
- Never reuse the source's footage, voice, music, or exact wording.

## 12. References

- Source video: <URL or path>
- Analysis folder: references/watch/<slug>/
- Representative frames: <3–5 file names copied into this skill folder>
- SFX map: analysis/sfx-map.json
- Sampled palette: §6 above
- Confidence: <which sections are measured vs not measured — list them>
```

## Filling notes for LEARN

- §1–§3 come from `cuts.json` + frame-pair analysis (A2).
- §4 comes from `words.json` + caption frames (A3).
- §6 hex values are sampled from actual frames with a colour picker on
  the extracted PNGs — never estimated from viewing.
- §7 comes from `audio_profile.json` + the SFX map (A4).
- §8–§9 come from the dedicated hook/ending pass (A5).
- §10 is written last: it must be consistent with §1–§9, and every
  instruction in it must trace to a measured field above it.
