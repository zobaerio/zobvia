# Music & SFX Sourcing — Licensing-Safe Only

**Skill policy:** CREATE mode is **SFX-only by default** — no background music track unless the user supplies a licensed track or explicitly asks for a library track from a source below. SFX carry the energy; this avoids most copyright claims entirely.

## Source & Licence Table

| Source | Licence / terms | Attribution | Commercial use | Notes |
|---|---|---|---|---|
| YouTube Audio Library | Royalty-free per YouTube terms; some tracks CC-BY (marked) | Only where the track listing requires it | Yes, on YouTube; check per-track for off-platform | Safest for YouTube uploads; download from Studio, keep the listing screenshot |
| Pixabay Music / SFX | Pixabay Content Licence (free, no attribution required) | Not required (appreciated) | Yes | Don't redistribute standalone; don't use where a recognisable person/brand is implied |
| Freesound — CC0 sounds | CC0 (public domain dedication) | Not required | Yes | Filter by licence on the sound page — Freesound hosts mixed licences |
| Freesound — CC-BY sounds | CC-BY | **Required**: sound name, author, link, licence | Yes, with attribution | Keep attribution in description + credits file |
| Freesound — CC-BY-NC | CC-BY NonCommercial | Required | **No** — not for monetised/client work | Skip for any paid/monetised video |
| Openverse | Aggregates CC0 / CC-BY / CC-BY-SA etc. | Per-item licence | Per-item | Verify on the original source page, not just the aggregator listing |
| Uppbeat | Free tier licence with attribution/credit link; paid tiers broaden rights | Required on free tier | Yes within tier terms | Terms change — re-check the licence page at download time |
| Incompetech (Kevin MacLeod) | Mostly CC-BY | Required | Yes, with attribution | Classic source; attribution text is provided per track |
| User-supplied track | User's responsibility + licence proof | Per their licence | Only as licensed | Ask for the licence/receipt; file it in the project folder |

Licence terms change. At download time, save a screenshot/PDF of the licence page into the project folder (`03_assets/licences/`).

## Attribution Templates

Description block:

```
Music: "[Track Title]" by [Artist] — [Source URL]
Licence: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/

Sound effects from Freesound.org:
"[Sound Name]" by [Author] ([sound page URL]) — CC BY 4.0
```

Credits file (`credits.txt` in the delivery ZIP): one line per asset — `filename | title | author | source URL | licence`.

## Red Flags — Never Do These

- **Never rip commercial music** (no downloading a song from YouTube/Spotify/streaming and laying it under a video) — Content ID claim/strike risk and a licence violation, for the client too.
- Never trust "no copyright" in a random re-upload's title/description — only the original rights-holder's licence counts.
- Never use CC-BY-NC or "personal use only" assets in monetised or client work.
- Never remove a required attribution because the video is short.
- AI-generated music: check the generator's plan terms for commercial rights and keep the generation receipt; disclose synthetic content where a platform requires it.
- A client saying "just use this song, everyone does" is not a licence — offer a library alternative and note the refusal in the project notes if they insist on supplying it themselves.

## SFX-First Working Method

1. Build the SFX pass from the skill's SFX library (`sfx-library.md`): whooshes, pops, impacts, risers, UI clicks.
2. Source any missing SFX CC0-first (Freesound CC0 filter, Pixabay).
3. Log every external asset in `credits.txt` as you add it — not at delivery time from memory.
4. If music is requested: pick from the table above, file the licence proof, mix at −18 to −25 dB under voice-led content.
