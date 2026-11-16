#!/usr/bin/env python3
"""
Zobvia Studio — local prototype app for the Zobvia skill.

Upload a voice file + an SRT file, pick ONE colour, click Generate,
get a finished motion-graphics MP4. This server wraps the proven
zobvia CLI pipeline:

    create_video.py  ->  sync into shared render-app  ->  remotion render
    ->  ffmpeg loudnorm pass  ->  jobs/<id>/final.mp4

Python standard library ONLY (no pip installs). Binds 127.0.0.1:8770.
Jobs run strictly sequentially on one worker thread (renders are heavy).
"""

import json
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Queue
from urllib.parse import urlparse

# --------------------------------------------------------------------------
# Paths / config
# --------------------------------------------------------------------------
STUDIO = Path(__file__).resolve().parent
WORKSPACE = STUDIO.parent
SKILL_DIR = WORKSPACE / "zobvia"
CREATE_VIDEO = SKILL_DIR / "scripts" / "create_video.py"
TRANSCRIBE = SKILL_DIR / "scripts" / "transcribe.py"
MAKE_SRT = SKILL_DIR / "scripts" / "make_srt.py"


def _probe_whisper_python():
    """First python (this one, or a whisper-venv beside the app) that can
    import faster_whisper — used to run transcribe.py for voice-only jobs."""
    candidates = [sys.executable]
    for venv in (WORKSPACE / "whisper-venv", STUDIO / "whisper-venv"):
        candidates.append(str(venv / "bin" / "python"))
        candidates.append(str(venv / "Scripts" / "python.exe"))
    for cand in candidates:
        try:
            r = subprocess.run([cand, "-c", "import faster_whisper"],
                               capture_output=True, timeout=30)
            if r.returncode == 0:
                return cand
        except Exception:  # noqa: BLE001
            continue
    return None


WHISPER_PYTHON = _probe_whisper_python()
RENDER_APP = STUDIO / "render-app"
PATCHED_ROOT = STUDIO / "Root.patched.tsx"  # self-hosted-font Root.tsx
JOBS_DIR = STUDIO / "jobs"
INDEX_HTML = STUDIO / "index.html"

# --- Access gate -----------------------------------------------------------
# Same gate as the Zobvia skill: only a SHA-256 hash of the password is
# stored (in the skill's scripts/access_check.py); a correct entry writes
# the per-machine marker ~/.zobvia/access-ok and the app stays unlocked.
# If the access module is missing (partial copy), the gate is disabled
# with a warning instead of bricking the app.
ACCESS_CHECK = SKILL_DIR / "scripts" / "access_check.py"
_access = None
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("zobvia_access", ACCESS_CHECK)
    _access = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_access)
except Exception as _e:  # noqa: BLE001
    print(f"warning: access gate disabled ({_e})")

def access_unlocked() -> bool:
    return True if _access is None else _access.is_unlocked()

# Default: this machine only. ZOBVIA_LAN=1 (or the LAN launcher) also
# serves phones/tablets on the same Wi-Fi — the access-password gate
# still protects job creation in that mode.
import os as _os
LAN_MODE = _os.environ.get("ZOBVIA_LAN", "").strip() in ("1", "true", "yes")
HOST, PORT = ("0.0.0.0", 8770) if LAN_MODE else ("127.0.0.1", 8770)
MAX_UPLOAD_BYTES = 600 * 1024 * 1024  # 600 MB safety cap
RENDER_TIMEOUT_S = 25 * 60

TONES = {
    "tech", "calm", "urgent", "playful", "premium", "growth",
    "creative", "minimal", "dark", "warm", "cool",
}
CAPTION_PRESETS = {
    "word-by-word", "karaoke-highlight", "bilingual-stack",
    "classic-bottom", "boxed-bold", "minimal-line",
}
ASPECTS = {"16:9", "9:16", "1:1"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

# --------------------------------------------------------------------------
# Job state
# --------------------------------------------------------------------------
JOBS = {}
JOBS_LOCK = threading.Lock()
JOB_QUEUE = Queue()


def new_job(params):
    job = {
        "id": uuid.uuid4().hex[:12],
        "stage": "queued",          # queued|preparing|rendering|done|failed
        "progress": 0,              # 0..100
        "message": "Queued — waiting for the render worker.",
        "error": None,
        "detail": None,
        "video_url": None,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "params": params,
    }
    with JOBS_LOCK:
        JOBS[job["id"]] = job
    return job


def update_job(job, **kw):
    with JOBS_LOCK:
        job.update(kw)
    job_dir = JOBS_DIR / job["id"]
    try:
        job_dir.mkdir(parents=True, exist_ok=True)
        snapshot = {k: v for k, v in job.items()}
        (job_dir / "job.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def public_job(job):
    return {
        "id": job["id"],
        "stage": job["stage"],
        "progress": job["progress"],
        "message": job["message"],
        "error": job["error"],
        "detail": job["detail"],
        "video_url": job["video_url"],
        "created_at": job["created_at"],
        "params": job["params"],
    }


# --------------------------------------------------------------------------
# Multipart parsing (stdlib only — hand-rolled, binary safe)
# --------------------------------------------------------------------------
def parse_multipart(body, content_type):
    """Return (fields: dict[str,str], files: dict[str,(filename, bytes)])."""
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type or "")
    if not m:
        raise ValueError("No multipart boundary in Content-Type")
    boundary = (m.group(1) or m.group(2)).strip().encode()
    delimiter = b"--" + boundary
    fields, files = {}, {}
    for part in body.split(delimiter):
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):  # closing delimiter fragment
            part = part[:-2]
            if part.endswith(b"\r\n"):
                part = part[:-2]
        header_blob, sep, content = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        headers = header_blob.decode("utf-8", "replace")
        name_m = re.search(r'name="([^"]+)"', headers)
        if not name_m:
            continue
        name = name_m.group(1)
        file_m = re.search(r'filename="([^"]*)"', headers)
        if file_m is not None:
            filename = file_m.group(1)
            if filename:
                files[name] = (filename, content)
        else:
            fields[name] = content.decode("utf-8", "replace")
    return fields, files


# --------------------------------------------------------------------------
# Pipeline steps
# --------------------------------------------------------------------------
def run_cmd(cmd, timeout, cwd=None):
    """Run a command, return (exit_code, combined_output_tail)."""
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=timeout)
    out = proc.stdout or ""
    return proc.returncode, out[-4000:]


def sync_into_render_app(project_dir):
    """Copy the generated project's src/ + public/ into the shared
    render-app, restoring the self-hosted-font Root.tsx and keeping
    render-app's public/fonts (the generated starter has no fonts dir
    and its Root.tsx points at Google Fonts, which is unreachable
    from headless Chromium on this machine)."""
    # src/: wholesale replace, then restore patched Root.tsx
    dest_src = RENDER_APP / "src"
    if dest_src.exists():
        shutil.rmtree(dest_src)
    shutil.copytree(project_dir / "src", dest_src)
    shutil.copyfile(PATCHED_ROOT, dest_src / "Root.tsx")

    # Compatibility shim: v1.4 scene components import `sceneAccent`
    # from theme.ts, but create_video.py's generated theme.ts may not
    # export it yet (it already provides accent/accent2/accent3).
    # Append the starter's own helper, derived from those very fields.
    # No-op once the generator emits the export itself.
    theme_path = dest_src / "theme.ts"
    if theme_path.exists():
        theme_src = theme_path.read_text(encoding="utf-8")
        if "export const sceneAccent" not in theme_src:
            theme_path.write_text(theme_src.rstrip() + "\n\n" + r'''
/**
 * Appended by Zobvia Studio at sync time (compatibility shim):
 * per-scene accent rotation, identical to the starter theme's helper.
 * Rotates through the theme's three accents by scene position.
 */
export const SCENE_ACCENTS: string[] = [
  theme.accent,
  theme.accent2,
  theme.accent3,
];

export const sceneAccent = (index: number): string =>
  SCENE_ACCENTS[((index % SCENE_ACCENTS.length) + SCENE_ACCENTS.length) %
    SCENE_ACCENTS.length];
''', encoding="utf-8")

    # public/: replace everything the generator produced, keep fonts/
    dest_public = RENDER_APP / "public"
    dest_public.mkdir(exist_ok=True)
    for stale in ("voiceover.mp3", "voiceover.wav"):
        p = dest_public / stale
        if p.exists():
            p.unlink()
    for item in (project_dir / "public").iterdir():
        if item.name == "fonts":
            continue
        dest = dest_public / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copyfile(item, dest)

    # out/: clear previous renders
    out_dir = RENDER_APP / "out"
    out_dir.mkdir(exist_ok=True)
    for f in out_dir.iterdir():
        if f.is_file():
            f.unlink()


def render_with_progress(job, composition, out_name):
    """Run remotion render, streaming lines to update job progress."""
    cmd = ["npx", "remotion", "render", composition, f"out/{out_name}"]
    proc = subprocess.Popen(
        cmd, cwd=str(RENDER_APP),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        bufsize=1)
    tail = []
    started = time.time()
    rendered_re = re.compile(r"Rendered (\d+)/(\d+)")
    encoded_re = re.compile(r"Encoded (\d+)/(\d+)")
    try:
        for line in proc.stdout:
            tail.append(line.rstrip())
            tail = tail[-30:]
            if time.time() - started > RENDER_TIMEOUT_S:
                proc.kill()
                raise TimeoutError(f"Render exceeded {RENDER_TIMEOUT_S}s")
            m = rendered_re.search(line)
            if m:
                done, total = int(m.group(1)), int(m.group(2))
                if total:
                    pct = 30 + int(55 * done / total)
                    update_job(job, progress=min(pct, 85),
                               message=f"Rendering frames… {done}/{total}")
                continue
            m = encoded_re.search(line)
            if m:
                done, total = int(m.group(1)), int(m.group(2))
                if total:
                    pct = 85 + int(10 * done / total)
                    update_job(job, progress=min(pct, 95),
                               message=f"Encoding video… {done}/{total}")
        proc.wait(timeout=60)
    finally:
        if proc.poll() is None:
            proc.kill()
    return proc.returncode, "\n".join(tail)[-4000:]


def process_job(job):
    job_dir = JOBS_DIR / job["id"]
    params = job["params"]
    try:
        update_job(job, stage="preparing", progress=3,
                   message="Preparing project…")

        srt_path = job_dir / "input.srt"
        voice_raw = job_dir / "input_voice.bin"
        has_srt = srt_path.exists() and srt_path.stat().st_size > 0
        has_voice = voice_raw.exists() and voice_raw.stat().st_size > 0

        # --- No SRT but a typed script: build the SRT from the script ---
        script_path = job_dir / "script.txt"
        if not has_srt and script_path.exists() and script_path.stat().st_size > 0:
            update_job(job, message="Building subtitles from your script…")
            cmd = [sys.executable, str(MAKE_SRT), "--text", str(script_path),
                   "--out", str(srt_path)]
            if has_voice:
                cmd += ["--audio", str(voice_raw)]
            elif params.get("duration"):
                cmd += ["--duration", str(params["duration"])]
            else:
                update_job(
                    job, stage="failed", progress=0,
                    error=("Script received, but its length is unknown: "
                           "upload the voice file too, or give the duration "
                           "in seconds, so timings can be calculated."))
                return
            code, out = run_cmd(cmd, timeout=120)
            if code == 0 and srt_path.exists() and srt_path.stat().st_size > 0:
                has_srt = True
            else:
                update_job(job, stage="failed", progress=0,
                           error="Could not build subtitles from the script.",
                           detail=out or None)
                return

        # --- No SRT: try transcription (honest failure without Whisper) ---
        if not has_srt:
            if has_voice and WHISPER_PYTHON:
                update_job(job, message="No SRT — transcribing your voice "
                                         "(first time downloads the model)…")
                code, out = run_cmd(
                    [WHISPER_PYTHON, str(TRANSCRIBE),
                     "--in", str(voice_raw), "--out", str(job_dir / "auto.srt"),
                     "--language", params.get("language", "bn"),
                     "--model", params.get("model", "small")],
                    timeout=1800)
                auto = job_dir / "auto.srt"
                if code == 0 and auto.exists() and auto.stat().st_size > 0:
                    shutil.copyfile(auto, srt_path)
                    has_srt = True
                else:
                    update_job(
                        job, stage="failed", progress=0,
                        error=("Transcription failed on this machine. "
                               "Alternatives: upload an .srt file, or paste "
                               "your script in the Script box and Zobvia "
                               "will build the subtitles from it."),
                        detail=out or None)
                    return
            elif has_voice:
                update_job(
                    job, stage="failed", progress=0,
                    error=("SRT needed — voice-to-subtitle transcription "
                           "(Whisper) is not installed on this machine. "
                           "Two ways forward: upload an .srt file with your "
                           "voice, or paste your script in the Script box "
                           "and Zobvia builds the subtitles from it."))
                return
            else:
                update_job(
                    job, stage="failed", progress=0,
                    error="Nothing to work with. Upload an .srt file, or a "
                          "voice file, or paste your script in the Script "
                          "box (with a duration).")
                return

        # --- Voice: normalise to MP3 so create_video flips HAS_VOICEOVER
        # and the PreviewAudio composition picks it up as voiceover.mp3 ---
        voice_mp3 = None
        if has_voice:
            update_job(job, message="Converting voice audio…", progress=8)
            voice_mp3 = job_dir / "voice.mp3"
            try:
                code, out = run_cmd(
                    ["ffmpeg", "-y", "-v", "error", "-i", str(voice_raw),
                     "-vn", "-codec:a", "libmp3lame", "-q:a", "3",
                     str(voice_mp3)],
                    timeout=600)
                if code != 0 or not voice_mp3.exists():
                    raise RuntimeError(out or "ffmpeg failed")
            except Exception as e:  # noqa: BLE001
                update_job(job, stage="failed", progress=0,
                           error=f"Could not read the voice audio file: {e}")
                return

        # --- Generate the Remotion project with the skill CLI ---
        palette = params["palette"]
        cmd = [sys.executable, str(CREATE_VIDEO),
               "--srt", str(srt_path),
               "--palette", palette,
               "--captions", params["captions"],
               "--sfx-theme", "cinematic",
               "--aspect", params["aspect"],
               "--out", str(job_dir / "project")]
        if voice_mp3 is not None:
            cmd += ["--voiceover", str(voice_mp3)]
        update_job(job, message="Generating scenes from SRT (zobvia)…",
                   progress=12)
        code, out = run_cmd(cmd, timeout=900)
        if code != 0:
            update_job(job, stage="failed", progress=0,
                       error="zobvia create_video.py failed.",
                       detail=out or None)
            return
        update_job(job, progress=25, message="Project generated. Syncing "
                                             "into the render app…")

        # --- Sync + render ---
        sync_into_render_app(job_dir / "project")
        composition = "PreviewAudio" if voice_mp3 is not None else "Main"
        out_name = f"render-{job['id']}.mp4"
        update_job(job, stage="rendering", progress=30,
                   message=f"Rendering ({composition})…")
        code, out = render_with_progress(job, composition, out_name)
        rendered = RENDER_APP / "out" / out_name
        if code != 0 or not rendered.exists():
            update_job(job, stage="failed", progress=0,
                       error="Remotion render failed.", detail=out or None)
            return

        # --- Loudness polish pass ---
        update_job(job, progress=96, message="Polishing audio (loudnorm)…")
        final = job_dir / "final.mp4"
        note = None
        try:
            code, out = run_cmd(
                ["ffmpeg", "-y", "-v", "error", "-i", str(rendered),
                 "-c:v", "copy",
                 "-af", "extrastereo=m=2.0,loudnorm=I=-14:TP=-1.5:LRA=11",
                 "-c:a", "aac", "-b:a", "192k", str(final)],
                timeout=900)
            if code != 0 or not final.exists():
                raise RuntimeError(out or "ffmpeg loudnorm failed")
        except Exception as e:  # noqa: BLE001
            shutil.copyfile(rendered, final)
            note = f"Audio polish skipped ({e}); raw render delivered."
        update_job(job, stage="done", progress=100,
                   message="Done — your video is ready.",
                   detail=note, video_url=f"/api/jobs/{job['id']}/video")
    except Exception as e:  # noqa: BLE001
        update_job(job, stage="failed", progress=0,
                   error=f"Unexpected error: {e}")


def worker_loop():
    while True:
        job = JOB_QUEUE.get()
        try:
            process_job(job)
        finally:
            JOB_QUEUE.task_done()


# --------------------------------------------------------------------------
# HTTP handler
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("[studio] %s\n" % (fmt % args))

    # -- helpers -----------------------------------------------------------
    def send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file_with_range(self, path, content_type):
        size = path.stat().st_size
        range_header = self.headers.get("Range")
        start, end = 0, size - 1
        status = 200
        if range_header:
            m = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                if m.group(2):
                    end = min(int(m.group(2)), size - 1)
                status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(1024 * 256, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    # -- routes ------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            body = INDEX_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/access":
            self.send_json(200, {"unlocked": access_unlocked()})
            return
        if path == "/api/capabilities":
            self.send_json(200, {"whisper": WHISPER_PYTHON is not None})
            return
        m = re.match(r"^/api/jobs/([0-9a-f]+)$", path)
        if m:
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
            if not job:
                self.send_json(404, {"error": "job not found"})
            else:
                self.send_json(200, public_job(job))
            return
        m = re.match(r"^/api/jobs/([0-9a-f]+)/video$", path)
        if m:
            final = JOBS_DIR / m.group(1) / "final.mp4"
            if not final.exists():
                self.send_json(404, {"error": "video not ready"})
            else:
                self.send_file_with_range(final, "video/mp4")
            return
        if path == "/api/jobs":
            with JOBS_LOCK:
                jobs = [public_job(j) for j in JOBS.values()]
            self.send_json(200, {"jobs": jobs})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/access/unlock":
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b""
            password = ""
            try:
                password = (json.loads(raw or b"{}").get("password") or "")
            except Exception:  # noqa: BLE001
                from urllib.parse import parse_qs
                password = (parse_qs(raw.decode("utf-8", "replace"))
                            .get("password", [""])[0])
            if _access is None or _access.verify(password):
                self.send_json(200, {"unlocked": True})
            else:
                self.send_json(403, {"error": "Wrong password — "
                                              "সঠিক পাসওয়ার্ড দাও।"})
            return
        if parsed.path != "/api/jobs":
            self.send_json(404, {"error": "not found"})
            return
        if not access_unlocked():
            self.send_json(403, {"error": "locked",
                                 "message": "Access password required — "
                                            "আগে পাসওয়ার্ড দিয়ে unlock করো।"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_UPLOAD_BYTES:
            self.send_json(413, {"error": "Upload missing or too large "
                                          f"(cap {MAX_UPLOAD_BYTES} bytes)."})
            return
        body = self.rfile.read(length)
        try:
            fields, files = parse_multipart(
                body, self.headers.get("Content-Type", ""))
        except Exception as e:  # noqa: BLE001
            self.send_json(400, {"error": f"Bad upload: {e}"})
            return

        # Resolve the ONE question: colour (custom hex beats tone chip).
        hex_value = (fields.get("hex") or "").strip()
        tone = (fields.get("tone") or "creative").strip().lower()
        if HEX_RE.match(hex_value):
            palette = hex_value
        elif tone in TONES:
            palette = tone
        else:
            palette = "creative"
        captions = (fields.get("captions") or "karaoke-highlight").strip()
        if captions not in CAPTION_PRESETS:
            captions = "karaoke-highlight"
        aspect = (fields.get("aspect") or "16:9").strip()
        if aspect not in ASPECTS:
            aspect = "16:9"

        language = (fields.get("language") or "bn").strip().lower()
        if language not in ("bn", "en"):
            language = "bn"
        model = (fields.get("model") or "small").strip().lower()
        if model not in ("tiny", "base", "small", "medium"):
            model = "small"
        script_text = (fields.get("script") or "").strip()
        duration_raw = (fields.get("duration") or "").strip()

        params = {"palette": palette, "captions": captions, "aspect": aspect,
                  "language": language, "model": model}
        job = new_job(params)
        job_dir = JOBS_DIR / job["id"]
        job_dir.mkdir(parents=True, exist_ok=True)

        if "srt" in files:
            (job_dir / "input.srt").write_bytes(files["srt"][1])
        if "voice" in files:
            (job_dir / "input_voice.bin").write_bytes(files["voice"][1])
        if script_text:
            (job_dir / "script.txt").write_text(script_text, encoding="utf-8")
            params["has_script"] = True
        if duration_raw:
            params["duration"] = duration_raw
        params["has_srt"] = "srt" in files
        params["has_voice"] = "voice" in files
        params["srt_name"] = files.get("srt", (None,))[0]
        params["voice_name"] = files.get("voice", (None,))[0]
        update_job(job, message="Queued — waiting for the render worker.")
        JOB_QUEUE.put(job)
        self.send_json(201, public_job(job))


def main():
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    if not CREATE_VIDEO.exists():
        sys.exit(f"zobvia skill not found at {CREATE_VIDEO}")
    if not (RENDER_APP / "node_modules").exists():
        sys.exit(f"render-app incomplete: {RENDER_APP}")
    threading.Thread(target=worker_loop, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Zobvia Studio → http://{HOST}:{PORT}  (Ctrl+C to stop)")
    if LAN_MODE:
        import socket as _socket
        ips = set()
        try:
            infos = _socket.getaddrinfo(_socket.gethostname(), None,
                                        _socket.AF_INET)
            ips = {i[4][0] for i in infos if not i[4][0].startswith("127.")}
        except Exception:  # noqa: BLE001
            pass
        for ip in sorted(ips):
            print(f"Phone/Tablet (same Wi-Fi): http://{ip}:{PORT}")
        print("LAN mode: anyone on this Wi-Fi can open the page; "
              "the access password still protects video creation.")
    print("Voice→SRT transcription (Whisper):",
          f"ready via {WHISPER_PYTHON}" if WHISPER_PYTHON else
          "not installed — SRT upload and Script box still work")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
