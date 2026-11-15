#!/usr/bin/env bash
# zobvia installer — checks tools and GUIDES; it does not hard-fail
# on optional pieces. Works on Linux, macOS, and Git-Bash/WSL on Windows.
set -uo pipefail
cd "$(dirname "$0")"

echo "🎬 zobvia — install check"
echo "================================"

# --- Access password gate (one time per machine) ---
# The access password is the author's GitHub username: zobaerio
# Only its SHA-256 hash is kept here / in scripts/access_check.py.
EXPECTED_SHA256="cf0910915f3943f6a17e7aab4271bce12afc303505ecc795b17a1bc8020def52"
MARKER="$HOME/.zobvia/access-ok"
if [ -f "$MARKER" ] && [ "$(tr -d ' \n' < "$MARKER")" = "$EXPECTED_SHA256" ]; then
  echo "🔓 Access: already unlocked on this machine."
else
  printf "🔐 Enter the Zobvia access password (hint: the author's GitHub username): "
  read -r -s ZOBVIA_PW </dev/tty || read -r -s ZOBVIA_PW
  echo
  if command -v sha256sum >/dev/null 2>&1; then
    GOT="$(printf '%s' "$ZOBVIA_PW" | sha256sum | awk '{print $1}')"
  elif command -v shasum >/dev/null 2>&1; then
    GOT="$(printf '%s' "$ZOBVIA_PW" | shasum -a 256 | awk '{print $1}')"
  elif command -v python3 >/dev/null 2>&1; then
    GOT="$(printf '%s' "$ZOBVIA_PW" | python3 -c "import sys,hashlib;print(hashlib.sha256(sys.stdin.read().strip().encode()).hexdigest())")"
  else
    GOT=""
    echo "⚠️  No SHA-256 tool found — cannot verify the password here."
    echo "   After installing python3, run: python3 scripts/access_check.py"
  fi
  if [ -n "$GOT" ] && [ "$GOT" != "$EXPECTED_SHA256" ]; then
    echo "❌ Wrong access password — install stopped."
    echo "   The password is the author's GitHub username (see the README)."
    exit 1
  fi
  if [ -n "$GOT" ]; then
    mkdir -p "$HOME/.zobvia" && printf '%s\n' "$EXPECTED_SHA256" > "$MARKER"
    echo "✅ Access granted. You will not be asked again on this machine."
  fi
  unset ZOBVIA_PW GOT
fi
echo

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
