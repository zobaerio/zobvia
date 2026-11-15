#!/usr/bin/env bash
# zobvia installer — checks tools and GUIDES; it does not hard-fail
# on optional pieces. Works on Linux, macOS, and Git-Bash/WSL on Windows.
set -uo pipefail
cd "$(dirname "$0")"

echo "🎬 zobvia — install check"
echo "================================"

OS="$(uname -s 2>/dev/null || echo Windows)"
echo "Platform: $OS"
echo

# --- Python ---
if command -v python3 >/dev/null 2>&1; then
  echo "✅ python3: $(python3 --version 2>&1)"
  echo "   Installing Python dependencies (numpy, Pillow, faster-whisper)…"
  python3 -m pip install -r requirements.txt || \
    echo "⚠️  pip install had problems — you can retry: python3 -m pip install -r requirements.txt"
else
  echo "❌ python3 not found."
  echo "   Linux:   sudo apt install python3 python3-pip"
  echo "   macOS:   brew install python"
  echo "   Windows: https://www.python.org/downloads/ (tick 'Add to PATH')"
fi
echo

# --- ffmpeg (core requirement for LEARN mode) ---
if command -v ffmpeg >/dev/null 2>&1; then
  echo "✅ ffmpeg: $(ffmpeg -version 2>/dev/null | head -1)"
else
  echo "❌ ffmpeg not found (needed for LEARN mode; CREATE mode works without it)."
  echo "   Linux:   sudo apt install ffmpeg"
  echo "   macOS:   brew install ffmpeg"
  echo "   Windows: winget install Gyan.FFmpeg"
fi

# --- yt-dlp (downloading videos in LEARN mode) ---
if command -v yt-dlp >/dev/null 2>&1; then
  echo "✅ yt-dlp found"
else
  echo "ℹ️  yt-dlp not found — LEARN mode can still use local files."
  echo "   Install: python3 -m pip install yt-dlp  (or brew install yt-dlp)"
fi

# --- Node (CREATE mode / Remotion) ---
if command -v node >/dev/null 2>&1; then
  echo "✅ node: $(node --version)"
else
  echo "ℹ️  Node.js not found — needed to preview/render Remotion projects."
  echo "   Get LTS from https://nodejs.org/ (or: brew install node / winget install OpenJS.NodeJS.LTS)"
fi
echo

# --- Full report from the skill's own checker ---
if command -v python3 >/dev/null 2>&1; then
  echo "Full tool report:"
  python3 scripts/check_tools.py || true
  echo
fi

echo "Done. Next step: copy this folder into your Claude skills directory, e.g."
echo "  cp -r . ~/.claude/skills/zobvia"
echo "Then say:  Watch <a video link> and save it as style-my-style"
echo "      or:  Make a motion graphics video from this SRT"
exit 0
