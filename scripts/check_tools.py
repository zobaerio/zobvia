#!/usr/bin/env python3
"""Check availability of external tools and Python packages for zobvia."""
import argparse
import importlib
import json
import shutil
import subprocess
import sys

def check_binary(name, version_args, hint):
    path = shutil.which(name)
    if not path:
        return {"name": name, "status": "MISSING", "path": None, "version": None, "hint": hint}
    version = None
    try:
        r = subprocess.run([path] + version_args, capture_output=True, text=True, timeout=10)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        version = out[0].strip() if out else None
    except Exception:
        version = None
    return {"name": name, "status": "FOUND", "path": path, "version": version, "hint": hint}

def check_package(mod, hint):
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "installed")
        return {"name": mod, "status": "FOUND", "path": getattr(m, "__file__", None), "version": str(ver), "hint": hint}
    except Exception:
        return {"name": mod, "status": "MISSING", "path": None, "version": None, "hint": hint}

def main(argv=None):
    p = argparse.ArgumentParser(description="Check zobvia tool dependencies.")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    args = p.parse_args(argv)

    binaries = [
        check_binary("ffmpeg", ["-version"], "Install: apt install ffmpeg / brew install ffmpeg / https://ffmpeg.org/download.html"),
        check_binary("ffprobe", ["-version"], "Install: ships with ffmpeg — apt install ffmpeg / brew install ffmpeg"),
        check_binary("yt-dlp", ["--version"], "Install: pip install yt-dlp"),
        check_binary("whisper", ["--version"], "Install: pip install openai-whisper (optional; faster-whisper preferred)"),
    ]
    packages = [
        check_package("PIL", "Install: pip install Pillow"),
        check_package("numpy", "Install: pip install numpy"),
        check_package("faster_whisper", "Install: pip install faster-whisper (module name: faster-whisper)"),
    ]
    # faster_whisper import name check above is correct; also record display name
    for pkg in packages:
        if pkg["name"] == "faster_whisper":
            pkg["name"] = "faster-whisper"
        if pkg["name"] == "PIL":
            pkg["name"] = "PIL (Pillow)"

    all_items = binaries + packages
    core_ok = all(b["status"] == "FOUND" for b in binaries if b["name"] in ("ffmpeg", "ffprobe"))

    if args.json:
        print(json.dumps({"core_ok": core_ok, "tools": binaries, "packages": packages}, indent=2))
    else:
        print("zobvia tool check")
        print("=" * 56)
        print("-- External tools --")
        for b in binaries:
            line = f"{b['name']:<12} {b['status']}"
            if b["version"]:
                line += f"  ({b['version']})"
            print(line)
            if b["status"] == "MISSING":
                print(f"             hint: {b['hint']}")
        print("-- Python packages --")
        for pkg in packages:
            line = f"{pkg['name']:<18} {pkg['status']}"
            if pkg["version"]:
                line += f"  ({pkg['version']})"
            print(line)
            if pkg["status"] == "MISSING":
                print(f"             hint: {pkg['hint']}")
        print("=" * 56)
        found = sum(1 for i in all_items if i["status"] == "FOUND")
        print(f"Summary: {found}/{len(all_items)} found. Core tools (ffmpeg, ffprobe): {'OK' if core_ok else 'MISSING'}")
    return 0 if core_ok else 1

if __name__ == "__main__":
    sys.exit(main())
