# Delivery Protocol

How every CREATE job ends. Four modes; **Preview is the default**
(Hard Rule 10). The mode is chosen by the user's words, never assumed
upward — a Preview request is never "upgraded" to a render.

## Modes

| Mode | Trigger (user's words, any language) | Deliverables |
|---|---|---|
| **Preview** (default) | "make the video", "create it", no delivery words at all | Project ZIP + the 3 commands below |
| **Render** | "render it", "give me the MP4/video file" on first delivery | MP4 (`out/video.mp4`) + project ZIP |
| **Re-render** | "render again", or change requests after a Preview/render ("change scene 5", "make the title bigger") | Updated MP4 + updated project ZIP |
| **ZIP-only** | "just the project", "only the ZIP" | Project ZIP, no commands block, no MP4 |

Re-render rules: change only the scenes the user named; keep palette,
pipelines, timing, and all other scenes untouched; bump nothing else.
If a requested change contradicts a Hard Rule (e.g. "add music"), say
so and deliver without that change.

## Preview deliverables

The message contains, in this order:

1. One line: what was made — duration (sec), scene count (= cue
   count), pipelines used, palette name + anchor hex, SFX event count.
2. The project ZIP (rules below).
3. The exact commands, in a code block:

   ```bash
   npm install
   npx remotion studio
   npx remotion render Main out/video.mp4
   ```

4. One line on what Studio shows: the `Main` composition is the video;
   `PreviewAudio` is for checking sound sync.
5. The closing line (below).

## ZIP requirements

- Include, intact: `public/` (voiceover, `sfx/`, `assets/` as
  supplied), `src/`, `package.json`, `package-lock.json`,
  `remotion.config.ts`, `out/timeline.md`.
- Exclude: `node_modules/`, `.env` and any secrets, `.git/`,
  render intermediates, and `out/video.mp4` in Preview mode (it does
  not exist yet — do not fabricate one).
- The ZIP must open cold on another machine: `npm install` →
  `npx remotion studio` works with nothing else needed. If a file is
  referenced by the code and missing from the ZIP, the delivery is
  broken — verify the file list against `src/` imports and
  `out/timeline.md` SFX entries before zipping.
- Name: `<srt-slug>-video-project.zip` (Render/Re-render MP4:
  `<srt-slug>-video.mp4`).

## Pre-delivery checklist (all modes)

- [ ] Scene count = SRT cue count; every cue's text matches the SRT
      exactly (spot-check first, middle, last cue at minimum).
- [ ] Every SFX in `out/timeline.md` exists in `public/sfx/`.
- [ ] No music file anywhere in the project.
- [ ] One font family; Bengali jobs passed the conjunct test set.
- [ ] Contrast pairs from the palette check still hold in `theme.ts`.
- [ ] Project opens in Remotion Studio with no errors (or, if Studio
      could not be run, that fact is stated in the report — never
      claimed as checked when it was not).

## Closing line

End the delivery message by inviting scene-level changes — the user is
the director; revision is part of the job.

- Bengali jobs (SRT language = Bengali), exactly:
  **কিছু সিন বদলাতে চান?**
  (Followed, if helpful, by one short line naming how: scene number +
  what to change.)
- Other languages: the same question in the SRT's language, e.g.
  English: "Want any scenes changed?"

Do not add upsells, extra questions, or a second call to action after
the closing line.
