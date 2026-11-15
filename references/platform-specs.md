# Platform Specs

Render targets. When the user names a platform, use its row; when they don't, default to YouTube long-form 1920×1080.

## Master Table

| Platform | Resolution | Aspect | FPS | Typical / Max Length | Loudness | Captions |
|---|---|---|---|---|---|---|
| YouTube long-form | 1920×1080 (min) / 3840×2160 | 16:9 | 24/25/30 (match source) | 8–20 min typical; 12 h max | −14 LUFS-I, −1 dBTP | SRT sidecar preferred + optional burn-in for styled words only |
| YouTube Shorts | 1080×1920 | 9:16 | 30 (60 if source is 60) | ≤3 min; sweet spot 25–50 s | −14 LUFS-I | Burn-in mandatory (auto-captions unreliable for BN/AR) |
| Instagram Reels | 1080×1920 | 9:16 | 30 | ≤3 min; sweet spot 15–45 s | −14 LUFS-I | Burn-in mandatory |
| TikTok | 1080×1920 | 9:16 | 30 (60 for gaming) | ≤10 min upload; sweet spot 21–45 s | −14 LUFS-I | Burn-in mandatory |
| Facebook Feed | 1920×1080 or 1080×1080 | 16:9 or 1:1 | 30 | 3–10 min; 240 min max | −14 LUFS-I | SRT sidecar (FB renders it) + burn-in for hook line only |
| Facebook Reels | 1080×1920 | 9:16 | 30 | ≤90 s norm | −14 LUFS-I | Burn-in mandatory |
| LinkedIn | 1920×1080 / 1080×1080 | 16:9 or 1:1 | 30 | 3–10 min; 15 min max (10 GB) | −14 LUFS-I | SRT sidecar strongly recommended; 85%+ watch muted |

## Safe Zones (vertical 1080×1920)

Keep all text, logos and faces inside the central safe area. UI overlays differ per app and change — these are conservative working values.

| Platform | Top avoid | Bottom avoid | Right avoid | Keep text within |
|---|---|---|---|---|
| Shorts | 220 px (title/search) | 480 px (title, channel, CTA) | 140 px (like/comment rail) | x 40–940, y 220–1440 |
| Reels | 220 px | 420 px (caption + audio credit) | 120 px (action rail) | x 40–960, y 220–1500 |
| TikTok | 180 px | 480 px (caption, username, music) | 140 px (action rail) | x 40–940, y 180–1440 |
| FB Reels | 200 px | 400 px | 120 px | x 40–960, y 200–1520 |

Horizontal 1920×1080: keep titles ≥60 px from all edges; lower-third captions above y=950 so progress bars never cover them. Centre-cut check: anything essential must survive a 4:5 centre crop for feed previews.

## Caption Rules

- **Burn-in** when: vertical short-form, stylised/karaoke captions, Bengali/Arabic (platform auto-captions garble conjuncts/RTL), muted-first platforms.
- **SRT sidecar** when: YouTube long-form, LinkedIn, Facebook feed — gives search indexing, translation and accessibility. Deliver both: burned preview + clean video + `.srt`.
- Never burn-in *and* upload the same SRT on YouTube long-form — double captions. Choose one primary.
- Max 2 lines, ≤42 characters/line (Latin), ≤7 words/line for vertical. See `captions-library.md`.
- Captions must never sit in a bottom-avoid zone; raise the caption block, don't shrink the font below 48 px at 1080 wide.

## Per-Platform Notes

- **YouTube long-form:** upload highest quality you have (1440p/4K upload triggers VP9 and better bitrate even for 1080p viewing). Chapters need ≥3 timestamps, first at 0:00. End screens only in last 5–20 s — keep that area visually calm.
- **Shorts:** loop-friendly endings re-earn watch time. First frame = thumbnail; no black/fade-in starts. `#Shorts` not required but harmless.
- **Reels:** avoid TikTok watermarks (reach penalty). Leave the bottom for the caption text Instagram adds.
- **TikTok:** first 1 s decides; no logos/intros. Native text is fine, but burned captions travel when reposted.
- **Facebook:** 1:1 feed posts often out-reach 16:9 on mobile. SRT must be named `filename.en_US.srt` style for auto-detection on upload.
- **LinkedIn:** professional tone, no karaoke/emoji presets. 1:1 performs well in feed. Always attach SRT — muted autoplay is the norm.

## Loudness & Audio

- All platforms normalise near −14 LUFS integrated; deliver at −14 LUFS-I, true peak ≤ −1 dBTP, so your mix isn't turned down unpredictably.
- Voice must sit clearly above SFX/music: duck beds −12 to −18 dB under speech.
- Mono-compatibility check: phone speakers are the primary playback device.
