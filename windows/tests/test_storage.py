"""The storage layer, tested where a window is not needed.

Everything here runs on any platform, so a mistake is caught in seconds on Linux rather than minutes on a
Windows runner. The one Windows-specific behaviour worth proving is that a save replaces an existing file:
os.rename refuses that on Windows, os.replace does not, and the difference only appears on the second save.
"""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.storage import Store, data_dir   # noqa: E402

PERSON = {"id": "a1", "name": "Ravi Shankar Tiwari", "date": "1988-07-14", "time": "14:35",
          "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata"}


class StoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.store = Store(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_empty_before_anything_is_saved(self):
        self.assertEqual(self.store.profiles(), [])
        self.assertEqual(self.store.settings(), {})

    def test_profiles_round_trip(self):
        self.store.save_profiles([PERSON])
        self.assertEqual(self.store.profiles(), [PERSON])

    def test_saving_twice_replaces_rather_than_failing(self):
        """On Windows this is the one that would break with os.rename instead of os.replace."""
        self.store.save_profiles([PERSON])
        self.store.save_profiles([PERSON, dict(PERSON, id="b2", name="Neha Agarwal")])
        self.assertEqual(len(self.store.profiles()), 2)

    def test_hindi_survives_the_round_trip(self):
        """The app is bilingual, so the store must not mangle Devanagari - which it would if a write
        ever fell back to the platform's default encoding instead of UTF-8."""
        self.store.save_profiles([dict(PERSON, name="रवि शंकर तिवारी")])
        self.assertEqual(self.store.profiles()[0]["name"], "रवि शंकर तिवारी")

    def test_a_damaged_file_reads_as_empty_rather_than_crashing(self):
        self.store.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        self.store.profiles_path.write_text("{ this is not json", encoding="utf-8")
        self.assertEqual(self.store.profiles(), [])

    def test_a_file_holding_the_wrong_shape_reads_as_empty(self):
        self.store.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        self.store.profiles_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
        self.assertEqual(self.store.profiles(), [])

    def test_settings(self):
        self.store.set_setting("language", "hi")
        self.store.set_setting("chart_style", "north")
        self.assertEqual(self.store.setting("language"), "hi")
        self.assertEqual(self.store.setting("chart_style"), "north")
        self.assertIsNone(self.store.setting("missing"))
        self.assertEqual(self.store.setting("missing", "fallback"), "fallback")

    def test_chart_cache(self):
        self.assertIsNone(self.store.cached_chart("abc"))
        self.store.cache_chart("abc", '{"vedic": {}}')
        self.assertEqual(self.store.cached_chart("abc"), '{"vedic": {}}')
        self.assertEqual(self.store.clear_charts(), 1)
        self.assertIsNone(self.store.cached_chart("abc"))

    def test_no_temporary_files_are_left_behind(self):
        self.store.save_profiles([PERSON])
        self.store.save_settings({"language": "en"})
        leftovers = [p.name for p in Path(self._tmp.name).iterdir() if p.name.endswith(".tmp")]
        self.assertEqual(leftovers, [])


class DataDirTest(unittest.TestCase):
    def test_the_override_wins(self):
        import os
        os.environ["JYOTISH_DATA_DIR"] = "/tmp/jyotish-test-dir"
        try:
            self.assertEqual(data_dir(), Path("/tmp/jyotish-test-dir"))
        finally:
            del os.environ["JYOTISH_DATA_DIR"]


if __name__ == "__main__":
    unittest.main()
