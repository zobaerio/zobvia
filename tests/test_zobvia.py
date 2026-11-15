"""Test suite for zobvia scripts (stdlib unittest).

Run:  python3 -m unittest discover -s tests -v
Covers: srt_parse (normal, Bengali, malformed, empty), color_palette
(tones, anchors, contrast sanity), sfx_gen (WAV headers, durations, sizes).
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
    EXPECTED = {  # name -> approx duration seconds
        "pop": 0.12, "click": 0.06, "whoosh": 0.40, "pluck": 0.35,
        "chime": 0.40, "swipe": 0.30, "thud": 0.25,
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


if __name__ == "__main__":
    unittest.main()
