# Export Matrix

## Aspect Ratio × Resolution Matrix

| Aspect | 1080p class | 1440p class | 4K class | Primary use |
|---|---|---|---|---|
| 16:9 | 1920×1080 | 2560×1440 | 3840×2160 | YouTube long-form, LinkedIn, FB feed |
| 9:16 | 1080×1920 | 1440×2560 | 2160×3840 | Shorts, Reels, TikTok |
| 1:1 | 1080×1080 | 1440×1440 | 2160×2160 | FB/LinkedIn feed |
| 4:5 | 1080×1350 | 1440×1800 | 2160×2700 | IG/FB feed portrait |
| 21:9 | 2560×1080 | 3440×1440 | 5120×2160 | Cinematic long-form, banners |

Remotion: set `width`/`height` on the Composition exactly; never render one aspect and crop to another — re-layout captions/safe zones per aspect (see `platform-specs.md`).

## Per-Platform Render Settings

| Platform | Codec | Bitrate (1080p) | Bitrate (4K) | FPS | Audio |
|---|---|---|---|---|---|
| YouTube long-form | H.264 (or VP9 via 1440p+ upload) | 12–20 Mbps VBR 2-pass | 45–68 Mbps | Match source 24/25/30/60 | AAC 320 kbps, 48 kHz |
| Shorts / Reels / TikTok | H.264 | 10–16 Mbps | — (1080×1920 is the norm) | 30 (60 gaming/sport) | AAC 320 kbps, 48 kHz |
| Facebook feed | H.264 | 10–16 Mbps | 30–45 Mbps | 30 | AAC 320 kbps |
| LinkedIn | H.264 | 10–16 Mbps | — | 30 | AAC 320 kbps |
| Archive / client master | H.265 (HEVC) or ProRes if requested | 20–30 Mbps (H.265) | 60–100 Mbps | Source fps | AAC 320 kbps + WAV if asked |

H.265 note: ~40% smaller at equal quality, but slower encode and weaker compatibility — delivery default stays H.264 unless the client asks for H.265.

## FPS Handling

- Never convert 30→60 by frame duplication and call it 60 fps; render at the source/project fps.
- Mixed sources: pick the timeline fps of the *main* footage; conform others, don't blend rates per clip.
- Slow motion needs real high-fps source; simulated slow-mo on 30 fps stutters — use speed ramps sparingly.

## Remotion Render Flags (typical)

```bash
# Full-quality delivery (H.264, CRF-based)
npx remotion render <CompositionId> out/video.mp4 \
  --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=320k \
  --concurrency=50%

# Fast preview (lower scale, for approval only — never deliver)
npx remotion render <CompositionId> out/preview.mp4 \
  --codec=h264 --crf=28 --scale=0.5
```

- CRF guide (H.264): 16–18 delivery quality, 23 default, 28 preview. Lower CRF = bigger file.
- Deterministic renders: seed all randomness (shake/noise); a re-render of the same commit must be frame-identical.
- Render the loudness/final mix into the video — don't deliver a separate audio file unless asked.
- File naming for exports: see `project-workflow.md` (`<slug>_<platform>_<aspect>_v<n>.mp4`).
