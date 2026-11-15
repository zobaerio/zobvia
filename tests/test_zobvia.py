"""Test suite for zobvia scripts (stdlib unittest).

Run:  python3 -m unittest discover -s tests -v
Covers: srt_parse (normal, Bengali, malformed, empty), color_palette
(tones, anchors, contrast sanity), sfx_gen (WAV headers, durations, sizes),
access_check (password gate), create_video (SRT -> Remotion project),
transcribe (honest no-backend degradation), qc_check (ffprobe checks),
create_video v1.2 (family planner, transitions, captions, multi-aspect,
voiceover drift, honest --render failure, demo timeline registration),
v1.3 (12 SFX types + peak levels, --genre scenes + caption defaults,
--sfx-theme, 3D/genre pipeline registration).
"""
import json
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script, *args, expect=0):
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True,
    )
    if expect is not None:
        assert p.returncode == expect, f"{script} {args}: rc={p.returncode}\n{p.stderr}"
    return p


SRT_OK = """1
00:00:00,000 --> 00:00:02,500
Hello world, this is a test.

2
00:00:02,500 --> 00:00:05,000
এটি একটি বাংলা লাইন।

3
00:00:05,000 --> 00:00:08,250
Final cue with English words.
"""


class TestSrtParse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.srt = Path(self.tmp.name) / "in.srt"
        self.srt.write_text(SRT_OK, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_and_duration(self):
        out = Path(self.tmp.name) / "out.json"
        run("srt_parse.py", str(self.srt), "-o", str(out), "--pretty")
        d = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(d["cue_count"], 3)
        self.assertAlmostEqual(d["total_duration"], 8.25)
        self.assertEqual(d["warnings"], 0)

    def test_bengali_preserved(self):
        p = run("srt_parse.py", str(self.srt))
        d = json.loads(p.stdout)
        self.assertIn("বাংলা", d["cues"][1]["text"])

    def test_malformed_block_skipped_with_warning(self):
        bad = Path(self.tmp.name) / "bad.srt"
        bad.write_text(SRT_OK + "\n99\nnot-a-timestamp\nbroken block\n", encoding="utf-8")
        out = Path(self.tmp.name) / "bad.json"
        run("srt_parse.py", str(bad), "-o", str(out))
        d = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(d["cue_count"], 3)
        self.assertGreaterEqual(d["warnings"], 1)

    def test_empty_file_is_clean_error(self):
        empty = Path(self.tmp.name) / "empty.srt"
        empty.write_text("", encoding="utf-8")
        p = run("srt_parse.py", str(empty), expect=None)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue(p.stderr.strip())

    def test_missing_file_is_clean_error(self):
        p = run("srt_parse.py", str(Path(self.tmp.name) / "nope.srt"), expect=None)
        self.assertNotEqual(p.returncode, 0)

    def test_markdown_output(self):
        md = Path(self.tmp.name) / "t.md"
        run("srt_parse.py", str(self.srt), "--markdown", str(md))
        text = md.read_text(encoding="utf-8")
        self.assertIn("| # | Start | End | Duration | Text |", text)
        self.assertIn("8.250", text)


class TestColorPalette(unittest.TestCase):
    def palette(self, tone):
        p = run("color_palette.py", "--tone", tone, "--format", "json")
        return json.loads(p.stdout)

    def test_all_tones_have_six_swatches(self):
        for tone in ["tech", "calm", "urgent", "playful", "premium", "growth",
                     "creative", "minimal", "dark", "warm", "cool"]:
            d = self.palette(tone)
            sw = d["swatches"] if "swatches" in d else d["palette"]
            self.assertEqual(len(sw), 6, tone)

    def test_anchor_present_in_tech(self):
        d = self.palette("tech")
        sw = d["swatches"] if "swatches" in d else d["palette"]
        hexes = [s["hex"].upper() for s in sw]
        self.assertIn("#0A1929", hexes)

    def test_contrast_sanity(self):
        d = self.palette("tech")
        sw = d["swatches"] if "swatches" in d else d["palette"]
        navy = [s for s in sw if s["hex"].upper() == "#0A1929"][0]
        # near-black navy: ~1.0 against a dark bg, high against a light bg
        self.assertLess(navy["contrast_on_dark"], 2.0)
        self.assertGreater(navy["contrast_on_light"], 10.0)

    def test_unknown_tone_errors(self):
        p = run("color_palette.py", "--tone", "bogus", expect=None)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("tech", p.stderr)


class TestSfxGen(unittest.TestCase):
    EXPECTED = {  # name -> approx duration seconds (12 types, v1.3)
        "pop": 0.12, "click": 0.06, "whoosh": 0.40, "pluck": 0.35,
        "chime": 0.40, "swipe": 0.30, "thud": 0.25,
        "riser": 0.80, "sparkle": 0.50, "ding": 0.60,
        "shutter": 0.15, "boom-soft": 0.70,
    }

    def test_wav_headers_and_durations(self):
        with tempfile.TemporaryDirectory() as td:
            run("sfx_gen.py", "--out", td)
            for name, dur in self.EXPECTED.items():
                f = Path(td) / f"{name}.wav"
                self.assertTrue(f.exists(), name)
                self.assertGreater(f.stat().st_size, 1000, name)
                with wave.open(str(f)) as w:
                    self.assertEqual(w.getframerate(), 44100)
                    self.assertEqual(w.getnchannels(), 1)
                    self.assertEqual(w.getsampwidth(), 2)
                    got = w.getnframes() / w.getframerate()
                    self.assertAlmostEqual(got, dur, delta=0.02, msg=name)

    def test_only_flag(self):
        with tempfile.TemporaryDirectory() as td:
            run("sfx_gen.py", "--out", td, "--only", "pop")
            self.assertTrue((Path(td) / "pop.wav").exists())
            self.assertFalse((Path(td) / "click.wav").exists())

    def test_peak_levels_normalised_not_silent(self):
        # Sound v2: every WAV is peak-normalised to about -3 dBFS
        # (<= 0.75 with headroom) and none is near-silent (> 0.1).
        import struct
        with tempfile.TemporaryDirectory() as td:
            run("sfx_gen.py", "--out", td)
            for name in self.EXPECTED:
                f = Path(td) / f"{name}.wav"
                with wave.open(str(f)) as w:
                    raw = w.readframes(w.getnframes())
                samples = struct.unpack(f"<{len(raw) // 2}h", raw)
                peak = max(abs(s) for s in samples) / 32767
                self.assertLessEqual(peak, 0.75, f"{name} peak {peak:.3f}")
                self.assertGreater(peak, 0.1, f"{name} peak {peak:.3f}")


class TestAccessCheck(unittest.TestCase):
    def _load(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "access_check", SCRIPTS / "access_check.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_correct_password_matches(self):
        mod = self._load()
        self.assertTrue(mod.password_matches("zobaerio"))
        self.assertTrue(mod.password_matches("  zobaerio  "))  # stripped

    def test_wrong_password_rejected(self):
        mod = self._load()
        self.assertFalse(mod.password_matches("zobvia"))
        self.assertFalse(mod.password_matches(""))
        self.assertFalse(mod.password_matches("Zobaerio"))  # case-sensitive

    def test_cli_status_and_verify(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ, HOME=td)
            p = subprocess.run(
                [sys.executable, str(SCRIPTS / "access_check.py"), "--status"],
                capture_output=True, text=True, env=env)
            self.assertEqual(p.returncode, 3)  # locked in a fresh HOME
            env["ZOBVIA_PASSWORD"] = "zobaerio"
            p = subprocess.run(
                [sys.executable, str(SCRIPTS / "access_check.py")],
                capture_output=True, text=True, env=env)
            self.assertEqual(p.returncode, 0)
            self.assertTrue((Path(td) / ".zobvia" / "access-ok").exists())
            p = subprocess.run(
                [sys.executable, str(SCRIPTS / "access_check.py"), "--status"],
                capture_output=True, text=True, env=env)
            self.assertEqual(p.returncode, 0)  # now unlocked


class TestCreateVideo(unittest.TestCase):
    SRT = ROOT / "examples" / "example-bengali.srt"  # 10 cues, 45.0s

    def _tech_hexes(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            import color_palette
            return {s["hex"].upper() for s in color_palette.PALETTES["tech"]}
        finally:
            sys.path.remove(str(SCRIPTS))

    def test_full_run_bengali(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt", str(self.SRT),
                "--palette", "tech", "--out", str(out))
            timeline = json.loads(
                (out / "src" / "data" / "timeline.json").read_text(encoding="utf-8"))
            self.assertEqual(len(timeline["scenes"]), 10)
            self.assertEqual(timeline["width"], 1920)
            self.assertEqual(timeline["height"], 1080)
            self.assertAlmostEqual(timeline["totalDuration"], 45.0)
            self.assertEqual(timeline["scenes"][0]["pipeline"], "kinetic-hook")
            self.assertEqual(timeline["scenes"][-1]["pipeline"], "cta")
            theme = (out / "src" / "theme.ts").read_text(encoding="utf-8")
            self.assertTrue(any(h in theme for h in self._tech_hexes()),
                            "theme.ts must carry a hex from the tech palette")
            self.assertTrue((out / "timeline.md").is_file())
            wavs = list((out / "public" / "sfx").glob("*.wav"))
            self.assertGreaterEqual(len(wavs), 1)
            sfx = json.loads(
                (out / "src" / "data" / "sfx.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(sfx["events"]), 5)
            self.assertLessEqual(len(sfx["events"]), 7)
            for ev in sfx["events"]:
                self.assertLessEqual(ev["atSeconds"], timeline["totalDuration"])
                self.assertTrue((out / "public" / ev["file"]).is_file())
            readme = (out / "PROJECT_README.md").read_text(encoding="utf-8")
            for cmd in ("npm install", "npx remotion studio",
                        "npx remotion render Main out/video.mp4"):
                self.assertIn(cmd, readme)

    def test_bad_palette_errors(self):
        with tempfile.TemporaryDirectory() as td:
            p = run("create_video.py", "--srt", str(self.SRT),
                    "--palette", "bogus-tone", "--out", str(Path(td) / "x"),
                    expect=None)
            self.assertEqual(p.returncode, 2)
            self.assertIn("tech", p.stderr)  # lists valid tones

    def test_vertical_aspect(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "vert"
            run("create_video.py", "--srt", str(self.SRT),
                "--palette", "#0EA5E9", "--out", str(out), "--aspect", "9:16")
            timeline = json.loads(
                (out / "src" / "data" / "timeline.json").read_text(encoding="utf-8"))
            self.assertEqual(timeline["height"], 1920)
            self.assertEqual(timeline["width"], 1080)

    def test_empty_srt_errors(self):
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "empty.srt"
            empty.write_text("", encoding="utf-8")
            p = run("create_video.py", "--srt", str(empty),
                    "--palette", "tech", "--out", str(Path(td) / "x"),
                    expect=None)
            self.assertEqual(p.returncode, 2)


class TestTranscribe(unittest.TestCase):
    def test_no_backend_is_honest_error(self):
        import shutil as _shutil
        try:
            import faster_whisper  # noqa: F401
            has_backend = True
        except ImportError:
            has_backend = bool(_shutil.which("whisper"))
        if has_backend:
            self.skipTest("a whisper backend IS present on this machine")
        with tempfile.TemporaryDirectory() as td:
            media = Path(td) / "clip.wav"
            media.write_bytes(b"RIFF")  # existence is all that is checked
            p = run("transcribe.py", "--in", str(media),
                    "--out", str(Path(td) / "out.srt"), expect=None)
            self.assertEqual(p.returncode, 3)
            self.assertIn("pip install", p.stderr)


class TestQcCheck(unittest.TestCase):
    def _make_clip(self, td):
        import shutil as _shutil
        if not _shutil.which("ffmpeg"):
            self.skipTest("ffmpeg not available")
        clip = Path(td) / "clip.mp4"
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=30",
               "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
               "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-shortest", str(clip)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not clip.is_file():
            cmd[cmd.index("libx264")] = "mpeg4"
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0 or not clip.is_file():
                self.skipTest(f"could not generate test clip: {proc.stderr[-200:]}")
        return clip

    def test_report_mode_and_expectations(self):
        import shutil as _shutil
        if not _shutil.which("ffprobe"):
            self.skipTest("ffprobe not available")
        with tempfile.TemporaryDirectory() as td:
            clip = self._make_clip(td)
            p = run("qc_check.py", "--file", str(clip))
            self.assertIn("has_audio: True", p.stdout)
            self.assertIn("320x240", p.stdout)
            run("qc_check.py", "--file", str(clip),
                "--expect-width", "320", "--expect-height", "240",
                "--expect-fps", "30", "--expect-duration", "2")
            p = run("qc_check.py", "--file", str(clip),
                    "--expect-width", "999", expect=None)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("FAIL", p.stdout)


STAGE_MIDDLES = {"glossy-ui", "carousel-3d", "glass-cards",
                 "minimal-clean", "gradient-fluid"}

# 24 plain sentences: no digits, no step words (first/then/next/finally/
# step), no section keywords, no commas — a neutral SRT whose planner
# signals are all zero, so the default (stage) family must be chosen.
LONG_SRT_TEXTS = [
    "Morning light makes every colour look softer and warmer",
    "A good story always begins with a simple honest question",
    "People remember feelings much longer than they remember facts",
    "The camera loves small movements and quiet confidence",
    "Every frame should earn its place in the final cut",
    "Silence between words can carry more weight than sound",
    "A calm voice guides the viewer through busy pictures",
    "Colour sets the mood before a single word is spoken",
    "Simple shapes read clearly even on a tiny phone screen",
    "The eye follows contrast wherever it appears on screen",
    "Music shapes emotion while pictures carry the meaning",
    "A strong ending leaves one clear thought behind",
    "Viewers decide quickly whether a video respects their time",
    "Clean typography makes hard ideas feel friendly",
    "Movement should always point toward the message",
    "A pause gives the audience room to breathe and think",
    "Bright accents work best when they appear rarely",
    "Every scene answers one question and raises another",
    "The background should support the subject and never fight it",
    "Rhythm comes from pattern and surprise working together",
    "A clear promise at the start builds trust for the rest",
    "Details matter most when everything else stays simple",
    "What we covered today fits into one simple picture",
    "Try this on your own video and watch the difference",
]


def _srt_timestamp(sec):
    return f"00:{sec // 60:02d}:{sec % 60:02d},000"


def make_srt(texts, cue_seconds=3):
    blocks = []
    for i, text in enumerate(texts):
        blocks.append(
            f"{i + 1}\n{_srt_timestamp(i * cue_seconds)} --> "
            f"{_srt_timestamp((i + 1) * cue_seconds)}\n{text}\n")
    return "\n".join(blocks)


class TestCreateVideoV12(unittest.TestCase):
    def _long_srt(self, td):
        srt = Path(td) / "long.srt"
        srt.write_text(make_srt(LONG_SRT_TEXTS), encoding="utf-8")
        return srt

    def _timeline(self, out):
        return json.loads(
            (out / "src" / "data" / "timeline.json").read_text(encoding="utf-8"))

    def test_long_srt_family_rotation_transitions(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt", str(self._long_srt(td)),
                "--palette", "tech", "--out", str(out))
            timeline = self._timeline(out)
            scenes = timeline["scenes"]
            self.assertEqual(len(scenes), 24)
            self.assertEqual(timeline["family"], "stage")
            self.assertEqual(scenes[0]["pipeline"], "kinetic-hook")
            self.assertEqual([s["pipeline"] for s in scenes[-3:]],
                             ["statement", "recap", "cta"])
            middles = scenes[1:-3]
            distinct = {s["pipeline"] for s in middles}
            self.assertGreaterEqual(len(distinct), 4)
            self.assertLessEqual(distinct, STAGE_MIDDLES,
                                 "middle pipelines must stay in one family")
            for s in scenes:
                self.assertIn("transition", s)
            self.assertEqual(scenes[0]["transition"], "none")
            non_first = scenes[1:]
            cuts = sum(1 for s in non_first if s["transition"] == "cut")
            self.assertGreaterEqual(cuts / len(non_first), 0.7)

    def test_captions_flag_and_bad_preset(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt", str(self._long_srt(td)),
                "--palette", "tech", "--out", str(out),
                "--captions", "karaoke-highlight")
            self.assertEqual(self._timeline(out)["captions"],
                             "karaoke-highlight")
            p = run("create_video.py", "--srt", str(self._long_srt(td)),
                    "--palette", "tech", "--out", str(Path(td) / "x"),
                    "--captions", "bogus-preset", expect=None)
            self.assertEqual(p.returncode, 2)
            self.assertIn("karaoke-highlight", p.stderr)  # lists valid ids

    def test_multi_aspect_projects(self):
        with tempfile.TemporaryDirectory() as td:
            srt = Path(td) / "in.srt"
            srt.write_text(SRT_OK, encoding="utf-8")
            out = Path(td) / "multi"
            run("create_video.py", "--srt", str(srt),
                "--palette", "tech", "--out", str(out),
                "--aspects", "16:9,9:16")
            wide = self._timeline(out / "16x9")
            tall = self._timeline(out / "9x16")
            self.assertEqual((wide["width"], wide["height"]), (1920, 1080))
            self.assertEqual((tall["width"], tall["height"]), (1080, 1920))

    def test_voiceover_drift_warns_but_succeeds(self):
        import math
        import shutil as _shutil
        if not _shutil.which("ffprobe"):
            self.skipTest("ffprobe not available")
        with tempfile.TemporaryDirectory() as td:
            vo = Path(td) / "voice.wav"
            with wave.open(str(vo), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(8000)
                frames = b"".join(
                    int(8000 * 0.3 * math.sin(2 * math.pi * 440 * i / 8000)
                        ).to_bytes(2, "little", signed=True)
                    for i in range(8000 * 3))
                w.writeframes(frames)
            out = Path(td) / "proj"
            # example-bengali.srt totals 45.0s; the voiceover is 3s.
            p = run("create_video.py", "--srt",
                    str(ROOT / "examples" / "example-bengali.srt"),
                    "--palette", "tech", "--out", str(out),
                    "--voiceover", str(vo))
            self.assertIn("WARNING: voiceover duration", p.stdout)
            self.assertTrue((out / "public" / "voiceover.wav").is_file())
            info = self._timeline(out)["voiceover"]
            self.assertEqual(info["file"], "voiceover.wav")
            self.assertAlmostEqual(info["durationSeconds"], 3.0, delta=0.25)
            self.assertAlmostEqual(info["srtDurationSeconds"], 45.0)

    def test_render_failure_names_the_step(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "bin"
            stub.mkdir()
            (stub / "npm").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (stub / "npx").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            (stub / "npm").chmod(0o755)
            (stub / "npx").chmod(0o755)
            srt = Path(td) / "in.srt"
            srt.write_text(SRT_OK, encoding="utf-8")
            env = dict(os.environ,
                       PATH=str(stub) + os.pathsep + os.environ["PATH"])
            p = subprocess.run(
                [sys.executable, str(SCRIPTS / "create_video.py"),
                 "--srt", str(srt), "--palette", "tech",
                 "--out", str(Path(td) / "proj"), "--render"],
                capture_output=True, text=True, env=env)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("remotion render", p.stderr)
            self.assertFalse(
                (Path(td) / "proj" / "out" / "video.mp4").exists())

    def test_v13_pipelines_registered(self):
        starter = ROOT / "templates" / "remotion-starter"
        main_tsx = (starter / "src" / "Main.tsx").read_text(encoding="utf-8")
        for pid in ("cube-3d", "flip-3d", "parallax-3d",
                    "news", "podcast", "product", "slideshow", "quote",
                    "tutorial", "scoreboard", "lyrics"):
            self.assertRegex(
                main_tsx, rf'["\']?{pid}["\']?\s*:',
                f"v1.3 pipeline {pid} not in Main map")


class TestCreateVideoV13(unittest.TestCase):
    def _timeline(self, out):
        return json.loads(
            (out / "src" / "data" / "timeline.json").read_text(encoding="utf-8"))

    def _srt(self, td, text=SRT_OK):
        srt = Path(td) / "in.srt"
        srt.write_text(text, encoding="utf-8")
        return srt

    def test_genre_news_scenes_and_caption_default(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt", str(self._srt(td)),
                "--palette", "tech", "--out", str(out), "--genre", "news")
            timeline = self._timeline(out)
            self.assertEqual(timeline["genre"], "news")
            scenes = timeline["scenes"]
            self.assertEqual(scenes[0]["pipeline"], "kinetic-hook")
            self.assertEqual(scenes[1]["pipeline"], "news")
            self.assertEqual(scenes[-1]["pipeline"], "cta")
            # Genre default caption preset (news -> classic-bottom).
            self.assertEqual(timeline["captions"], "classic-bottom")
            readme = (out / "PROJECT_README.md").read_text(encoding="utf-8")
            self.assertIn("news", readme)

    def test_genre_invalid_errors(self):
        with tempfile.TemporaryDirectory() as td:
            p = run("create_video.py", "--srt", str(self._srt(td)),
                    "--palette", "tech", "--out", str(Path(td) / "x"),
                    "--genre", "bogus-genre", expect=None)
            self.assertEqual(p.returncode, 2)
            self.assertIn("news", p.stderr)  # lists valid genre ids

    def test_sfx_theme_cinematic(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt",
                str(ROOT / "examples" / "example-bengali.srt"),
                "--palette", "tech", "--out", str(out),
                "--sfx-theme", "cinematic")
            timeline = self._timeline(out)
            self.assertEqual(timeline["sfxTheme"], "cinematic")
            sfx = json.loads(
                (out / "src" / "data" / "sfx.json").read_text(encoding="utf-8"))
            sounds = {Path(e["file"]).stem for e in sfx["events"]}
            self.assertTrue(sounds & {"riser", "boom-soft"},
                            f"cinematic set missing from {sounds}")
            for name in sounds:
                self.assertTrue(
                    (out / "public" / "sfx" / f"{name}.wav").is_file())

    def test_sfx_theme_invalid_errors(self):
        with tempfile.TemporaryDirectory() as td:
            p = run("create_video.py", "--srt", str(self._srt(td)),
                    "--palette", "tech", "--out", str(Path(td) / "x"),
                    "--sfx-theme", "loud", expect=None)
            self.assertEqual(p.returncode, 2)
            self.assertIn("cinematic", p.stderr)  # lists valid themes

    def test_defaults_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "proj"
            run("create_video.py", "--srt", str(self._srt(td)),
                "--palette", "tech", "--out", str(out))
            timeline = self._timeline(out)
            self.assertEqual(timeline["genre"], "general")
            self.assertEqual(timeline["sfxTheme"], "soft")
            self.assertEqual(timeline["captions"], "word-by-word")


    def test_demo_timeline_pipelines_registered(self):
        starter = ROOT / "templates" / "remotion-starter"
        demo = json.loads((starter / "src" / "data" / "timeline.json"
                           ).read_text(encoding="utf-8"))
        main_tsx = (starter / "src" / "Main.tsx").read_text(encoding="utf-8")
        for scene in demo["scenes"]:
            pid = scene["pipeline"]
            # Keys may be quoted ("hub-spoke":) or bare identifiers (bento:).
            self.assertRegex(
                main_tsx, rf'["\']?{pid}["\']?\s*:',
                f"demo pipeline {pid} not in Main map")


if __name__ == "__main__":
    unittest.main()
