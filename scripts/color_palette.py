#!/usr/bin/env python3
"""Tone-based colour palettes with WCAG contrast validation."""
import argparse
import json
import math
import sys

def sw(name, hex_, meaning):
    return {"name": name, "hex": hex_.upper(), "meaning": meaning}

PALETTES = {
    "tech": [
        sw("Deep Navy", "#0A1929", "Primary background / trust and depth"),
        sw("Sky", "#0EA5E9", "Primary accent / innovation and clarity"),
        sw("Royal Purple", "#4C1D95", "Secondary accent / intelligence"),
        sw("Electric Cyan", "#22D3EE", "Highlight / data and energy"),
        sw("Slate Text", "#E2E8F0", "Body text on dark"),
        sw("Charcoal", "#1F2937", "Surface / cards and panels"),
    ],
    "calm": [
        sw("Sage", "#87A878", "Primary / balance and ease"),
        sw("Soft Blue", "#7FB3D5", "Accent / serenity"),
        sw("Sand", "#E8DCC3", "Background warmth"),
        sw("Forest Green", "#064E3B", "Deep anchor / grounding"),
        sw("Mist", "#EAF2F8", "Light background"),
        sw("Charcoal", "#1F2937", "Text / readability"),
    ],
    "urgent": [
        sw("Crimson", "#991B1B", "Primary alert / danger and urgency"),
        sw("Alert Red", "#DC2626", "Call to action"),
        sw("Amber", "#B45309", "Warning / attention"),
        sw("Signal Orange", "#EA580C", "Highlight"),
        sw("Charcoal", "#1F2937", "Background contrast"),
        sw("White Heat", "#FEF2F2", "Light surface"),
    ],
    "playful": [
        sw("Coral", "#FB7185", "Primary / friendly energy"),
        sw("Sunny Amber", "#F59E0B", "Joy / highlights"),
        sw("Sky", "#0EA5E9", "Playful blue accent"),
        sw("Bubblegum", "#EC4899", "Fun accent"),
        sw("Mint", "#34D399", "Fresh secondary"),
        sw("Grape", "#8B5CF6", "Creative pop"),
    ],
    "premium": [
        sw("Charcoal", "#1F2937", "Primary / sophistication"),
        sw("Gold", "#B45309", "Luxury accent (amber family)"),
        sw("Deep Navy", "#0A1929", "Background / exclusivity"),
        sw("Royal Purple", "#4C1D95", "Regal accent"),
        sw("Ivory", "#FFFBEB", "Light surface / elegance"),
        sw("Bronze", "#92400E", "Warm metallic tone"),
    ],
    "growth": [
        sw("Forest Green", "#064E3B", "Primary / growth and stability"),
        sw("Emerald", "#059669", "Progress / success"),
        sw("Lime Spark", "#84CC16", "New growth highlight"),
        sw("Amber", "#B45309", "Harvest / value"),
        sw("Sky", "#0EA5E9", "Open opportunity"),
        sw("Cream", "#FEFCE8", "Light background"),
    ],
    "creative": [
        sw("Royal Purple", "#4C1D95", "Primary / imagination"),
        sw("Coral", "#FB7185", "Expressive accent"),
        sw("Electric Cyan", "#22D3EE", "Idea spark"),
        sw("Sunny Amber", "#F59E0B", "Warm creativity"),
        sw("Magenta", "#D946EF", "Bold statement"),
        sw("Deep Navy", "#0A1929", "Canvas background"),
    ],
    "minimal": [
        sw("Charcoal", "#1F2937", "Primary text"),
        sw("White", "#FFFFFF", "Background / space"),
        sw("Stone", "#78716C", "Muted secondary"),
        sw("Light Grey", "#F3F4F6", "Surface"),
        sw("Black", "#111827", "Strong contrast"),
        sw("Soft Accent", "#0EA5E9", "Single restrained accent (Sky)"),
    ],
    "dark": [
        sw("Deep Navy", "#0A1929", "Background"),
        sw("Charcoal", "#1F2937", "Surface"),
        sw("Slate", "#475569", "Muted elements"),
        sw("Sky", "#0EA5E9", "Accent on dark"),
        sw("Silver Text", "#E5E7EB", "Primary text on dark"),
        sw("Royal Purple", "#4C1D95", "Deep accent"),
    ],
    "warm": [
        sw("Amber", "#B45309", "Primary warmth"),
        sw("Terracotta", "#C2410C", "Earthy accent"),
        sw("Coral", "#FB7185", "Soft warmth"),
        sw("Cream", "#FFFBEB", "Light warm background"),
        sw("Crimson", "#991B1B", "Deep warm anchor"),
        sw("Charcoal", "#1F2937", "Text contrast"),
    ],
    "cool": [
        sw("Sky", "#0EA5E9", "Primary cool accent"),
        sw("Deep Navy", "#0A1929", "Background anchor"),
        sw("Teal", "#0F766E", "Cool secondary"),
        sw("Ice", "#E0F2FE", "Light cool surface"),
        sw("Royal Purple", "#4C1D95", "Cool deep accent"),
        sw("Slate", "#64748B", "Neutral cool grey"),
    ],
}

DARK_BG = "#0A1929"
LIGHT_BG = "#FFFFFF"

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def _linear(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def luminance(rgb):
    r, g, b = [_linear(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(hex1, hex2):
    l1 = luminance(hex_to_rgb(hex1))
    l2 = luminance(hex_to_rgb(hex2))
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)

def build(tone, subject=None):
    items = []
    for s in PALETTES[tone]:
        items.append({
            **s,
            "contrast_on_dark": contrast(s["hex"], DARK_BG),
            "contrast_on_light": contrast(s["hex"], LIGHT_BG),
            "wcag_aa_on_dark": contrast(s["hex"], DARK_BG) >= 4.5,
            "wcag_aa_on_light": contrast(s["hex"], LIGHT_BG) >= 4.5,
        })
    return {"tone": tone, "subject": subject, "dark_background": DARK_BG, "light_background": LIGHT_BG, "swatches": items}

def to_markdown(data):
    lines = [f"# Colour Palette — {data['tone'].title()}", ""]
    if data.get("subject"):
        lines += [f"**Subject:** {data['subject']}", ""]
    lines += ["| Name | Hex | Meaning | Contrast on dark | Contrast on light |",
              "|------|-----|---------|------------------|-------------------|"]
    for s in data["swatches"]:
        lines.append(f"| {s['name']} | `{s['hex']}` | {s['meaning']} | {s['contrast_on_dark']}:1 | {s['contrast_on_light']}:1 |")
    lines.append("")
    return "\n".join(lines)

def to_text(data):
    lines = [f"Palette: {data['tone']}" + (f" — {data['subject']}" if data.get("subject") else "")]
    for s in data["swatches"]:
        lines.append(f"  {s['name']:<16} {s['hex']}  dark {s['contrast_on_dark']}:1  light {s['contrast_on_light']}:1  — {s['meaning']}")
    return "\n".join(lines)

def main(argv=None):
    p = argparse.ArgumentParser(description="Generate a tone-based colour palette with WCAG contrast ratios.")
    p.add_argument("--tone", required=True, help="Palette tone, e.g. tech")
    p.add_argument("--subject", default=None, help="Optional subject the palette is for")
    p.add_argument("--format", choices=["json", "markdown", "text"], default="json", help="Output format")
    args = p.parse_args(argv)
    tone = args.tone.lower().strip()
    if tone not in PALETTES:
        print(f"Error: unknown tone '{args.tone}'. Valid tones: {', '.join(sorted(PALETTES))}", file=sys.stderr)
        return 2
    data = build(tone, args.subject)
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        print(to_markdown(data))
    else:
        print(to_text(data))
    return 0

if __name__ == "__main__":
    sys.exit(main())
