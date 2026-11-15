# Multilingual Typography

**Universal law: never split a grapheme cluster in any script.** No per-letter animation, no character-by-character typewriter, no line-break inside a cluster, conjunct or shaped letterform — for Bengali, Arabic, Urdu, Devanagari, and Latin combining marks alike. Animate words or whole lines instead.

## Bengali (BN)

- Fonts: Hind Siliguri (bold display), Noto Sans Bengali, Baloo Da 2 (playful). See core `bengali-text-rules.md` for full rules.
- Conjuncts (যুক্তাক্ষর) must render as one unit — verify the font actually contains the conjunct; a broken conjunct shows separated letters with a visible hasant.
- Line-height ≥1.4; matra (headline stroke) must not be clipped by tight leading or overflow hidden boxes.

## Arabic (AR) — RTL

- Direction: `direction: rtl`, text-align right (or centre for captions). Numbers/prices inside Arabic lines: confirm order visually — bidi reordering is the #1 bug.
- Fonts: Amiri (classical/Quranic), Cairo (modern/UI), Noto Naskh Arabic (body), Noto Kufi Arabic (headlines).
- Letters shape contextually (initial/medial/final forms) — the shaping engine must see the whole word. Never isolate letters, never letter-space Arabic (tracking disconnects the joins — this is a hard ban, not a style choice).
- No per-letter animation, no typewriter effect. Fade/slide whole words or lines.
- Line-height 1.6–1.8 — vowel marks (tashkeel) need vertical room; never clip.
- Punctuation mirrors: ؟ ، ؛ belong to the Arabic set; don't mix Latin `?` into Arabic lines unless the creator's style does.

## Urdu (UR) — RTL, Nastaliq

- Font: **Noto Nastaliq Urdu** is the default. Amiri/Cairo (Naskh) only if the creator's style specifies Naskh.
- Nastaliq is diagonal and tall: line-height **1.9–2.2**, generous box height, and never force Nastaliq into a tight single-line pop preset — use a calm fade/slide.
- Same RTL rules as Arabic: no letter animation, no tracking, whole-word animation only.
- Mixed Urdu + English brand names: keep the Latin fragment as one LTR run; check the rendered order, don't trust the source string order.

## Hindi / Devanagari (HI)

- Fonts: Noto Sans Devanagari (safe default), Poppins/Hind family Devanagari subsets (the "Hind" family is Devanagari-designed — Hind, Hind Vadodara etc.; Hind Siliguri is the Bengali sibling, don't cross them).
- Shirorekha (the headline stroke) joins letters — conjuncts like क्ष, त्र, ज्ञ must render as ligatures; a font missing them shows a visible virama (halant) — switch font, don't accept the broken render.
- Line-height ≥1.5; matras above/below the line (ि, ु, ू) clip easily in overflow-hidden animation masks — add padding.
- No per-character animation on conjunct words; animate whole words.

## English (EN)

- Fonts: bold condensed sans for pop captions (Archivo/Anton style), clean sans for body (Inter/Manrope style). ALL CAPS only for short pop lines, never paragraphs.
- Tracking: slight negative on big headlines (−1 to −2%), normal on captions.
- Per-word highlight and word-scale animation are safe in Latin script.

## Mixed-Script Lines

- One line = one primary script. Bilingual captions stack vertically (see Bilingual Stack preset), they don't interleave word-by-word.
- Brand names, URLs and numbers stay in their original script as a single run.
- Font fallback stack (CSS/Remotion): `"Hind Siliguri", "Noto Sans Bengali", "Noto Sans Devanagari", "Noto Nastaliq Urdu", "Noto Naskh Arabic", "Inter", sans-serif` — order by the video's primary language first, and load every font the SRT actually uses.
- Always render-test one line containing the hardest cluster in the script (BN conjunct, AR tashkeel, HI क्ष) before the full render.

## Universal Do-Nots

- Never split grapheme clusters — in animation, line-breaking, counting characters, or karaoke timing.
- Never letter-space (tracking) Arabic/Urdu.
- Never use a font that lacks the script — tofu boxes (□) are a QC fail, caught in preview, not delivery.
- Never auto-shrink mixed-script lines until the smallest script is unreadable; shorten the text instead.
- Never trust string length for layout in RTL/complex scripts — measure the rendered line.
