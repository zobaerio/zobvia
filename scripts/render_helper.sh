#!/usr/bin/env bash
# render_helper.sh — preview / render / zip a Remotion project.
# Usage: render_helper.sh <project-dir> [preview|render|zip]
set -euo pipefail

usage() {
  echo "Usage: $0 <project-dir> [preview|render|zip]" >&2
  echo "  preview  Render a single still frame (npx remotion still)" >&2
  echo "  render   Render the full video to out/video.mp4 (default)" >&2
  echo "  zip      Create project.zip excluding node_modules and .env" >&2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 2
fi

PROJECT_DIR="$1"
ACTION="${2:-render}"

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Error: project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/package.json" ]]; then
  echo "Error: no package.json in $PROJECT_DIR — is this a Remotion/Node project?" >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx not found. Install Node.js (https://nodejs.org) and try again." >&2
  exit 1
fi

cd "$PROJECT_DIR"

case "$ACTION" in
  preview)
    mkdir -p out
    echo "Rendering preview still..."
    npx remotion still Main out/preview.png
    echo "Preview written to $PROJECT_DIR/out/preview.png"
    ;;
  render)
    mkdir -p out
    echo "Rendering video..."
    npx remotion render Main out/video.mp4
    echo "Video written to $PROJECT_DIR/out/video.mp4"
    ;;
  zip)
    if ! command -v zip >/dev/null 2>&1; then
      echo "Error: 'zip' command not found. Install it (apt install zip / brew install zip)." >&2
      exit 1
    fi
    rm -f project.zip
    echo "Creating project.zip (excluding node_modules, .env)..."
    zip -r project.zip . \
      -x "node_modules/*" "./node_modules/*" \
      -x ".env" "./.env" ".env.*" \
      -x "project.zip"
    echo "Archive written to $PROJECT_DIR/project.zip"
    ;;
  *)
    echo "Error: unknown action '$ACTION' (expected preview, render or zip)" >&2
    usage
    exit 2
    ;;
esac
