# Zobvia Studio — Windows Package

Turn an **SRT subtitle file + a voice recording** into a finished motion-graphics
video. Upload the files, pick a colour, click **Generate** — done.

## Install (one time)

1. Unzip this folder anywhere (e.g. `C:\ZobviaStudio`).
2. Right-click **INSTALL.bat** → **Run as administrator**.
   It installs Python, Node.js and ffmpeg if they are missing (via Windows
   winget), downloads the video-engine packages, and creates a
   **Zobvia Studio** shortcut on your Desktop. Internet is needed this once.
3. Double-click the **Zobvia Studio** Desktop shortcut (or `ZobviaStudio.bat`).
   Your browser opens at http://localhost:8770 — that is the app.

## Access password

Zobvia Studio is password-protected, like the Zobvia skill itself.
**The access password is `zobaerio`** — the author's GitHub username.
It is shown on the app's lock screen too, so you cannot get stuck.
INSTALL.bat offers the password step at the end of setup; otherwise the
app asks the first time it opens on a machine. A correct entry is
remembered on that machine (marker file `~/.zobvia/access-ok`) — the
password itself is never stored, only its SHA-256 hash is checked.

## Use

1. Drag in your **SRT** file (required) and your **voice** file (optional).
2. Pick a colour — swatches or your own hex. Aspect and captions if you like.
3. Click **Generate**. A 45-second video takes roughly 3–5 minutes to render.
4. Watch the preview in the page and click **Download MP4**.

Notes: jobs run one at a time. Voice without an SRT needs Whisper transcription,
which is not bundled — the app will tell you an SRT is needed.

## Want a real ZobviaStudio-Setup.exe?

This package is the complete app in folder form. To ship a single-file
installer that users can download and double-click:

1. On a Windows PC, install **Inno Setup 6** (free, jrsoftware.org).
2. Put this folder on that PC and run **build-setup-exe.bat**.
3. You get **dist\ZobviaStudio-Setup.exe** — upload that file anywhere
   (GitHub Releases is a good home) and users install from it directly.

## What is inside

- `zobvia-studio/` — the app (server.py + index.html + render engine)
- `zobvia/` — the Zobvia video engine (scripts + Remotion starter template)
- `INSTALL.bat` — one-time prerequisite + engine setup
- `ZobviaStudio.bat` — the launcher the Desktop shortcut points to


## Note for people cloning from GitHub

A few binary files are in the downloadable ZIP package but cannot be stored
in this git repo through the publishing connector:

- `zobvia-studio/render-app/public/fonts/HindSiliguri-*.ttf` (3 font files) —
  fetch them once:
  `curl -LO https://github.com/google/fonts/raw/main/ofl/hindsiliguri/HindSiliguri-Regular.ttf`
  (same for `HindSiliguri-SemiBold.ttf` and `HindSiliguri-Bold.ttf`),
  and put them in `zobvia-studio/render-app/public/fonts/`.
- The render-app's sample SFX `.wav` files — these are regenerated
  automatically on the first job, nothing to download.
