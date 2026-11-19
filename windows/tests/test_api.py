"""The API the window talks to.

This is the layer where a mistake becomes a bug someone sees, so it carries the most tests. None of them
need a window, which is the point of putting the behaviour here instead of in the shell.
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.api import Api, ValidationError, validate   # noqa: E402
from jyotish_win.storage import Store                        # noqa: E402

RAVI = {"name": "Ravi Shankar Tiwari", "gender": "M", "date": "1988-07-14", "time": "14:35",
        "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata", "place": "Varanasi, India"}


class ValidateTest(unittest.TestCase):
    def test_a_good_person_passes_and_gets_defaults(self):
        clean = validate(RAVI)
        self.assertEqual(clean["gender"], "M")
        self.assertEqual(clean["time_confidence"], "reliable")

    def test_missing_fields_are_listed_together(self):
        with self.assertRaises(ValidationError) as e:
            validate({"name": "No Birth Details"})
        message = str(e.exception)
        for field in ("date", "time", "lat", "lon", "tz"):
            self.assertIn(field, message)

    def test_a_date_that_does_not_exist(self):
        with self.assertRaises(ValidationError):
            validate(dict(RAVI, date="1988-02-31"))

    def test_a_date_in_the_wrong_shape(self):
        with self.assertRaises(ValidationError):
            validate(dict(RAVI, date="14/07/1988"))

    def test_an_impossible_clock_time(self):
        with self.assertRaises(ValidationError):
            validate(dict(RAVI, time="25:00"))

    def test_coordinates_off_the_globe(self):
        with self.assertRaises(ValidationError):
            validate(dict(RAVI, lat=91))
        with self.assertRaises(ValidationError):
            validate(dict(RAVI, lon=-200))

    def test_coordinates_arriving_as_text_from_a_form(self):
        """The web form hands back strings; the engine wants numbers."""
        clean = validate(dict(RAVI, lat="25.3176", lon="82.9739"))
        self.assertIsInstance(clean["lat"], float)
        self.assertIsInstance(clean["lon"], float)

    def test_a_leap_day_is_a_real_birthday(self):
        validate(dict(RAVI, date="1992-02-29"))

    def test_whitespace_around_a_name_is_trimmed(self):
        self.assertEqual(validate(dict(RAVI, name="  Ravi  "))["name"], "Ravi")


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from jyotish_win.bridge import Engine
        cls.engine = Engine()          # loading the engine is slow; one instance for the class

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.api = Api(store=Store(Path(self._tmp.name)), engine=self.engine)

    def tearDown(self):
        self._tmp.cleanup()

    def test_starts_with_nobody(self):
        self.assertEqual(self.api.people(), [])

    def test_add_and_list(self):
        saved = self.api.add_person(RAVI)
        self.assertTrue(saved["id"])
        self.assertEqual([p["name"] for p in self.api.people()], ["Ravi Shankar Tiwari"])

    def test_adding_the_same_id_twice_edits_rather_than_duplicates(self):
        saved = self.api.add_person(RAVI)
        self.api.add_person(dict(saved, time="14:40"))
        self.assertEqual(len(self.api.people()), 1)
        self.assertEqual(self.api.people()[0]["time"], "14:40")

    def test_delete(self):
        saved = self.api.add_person(RAVI)
        self.assertTrue(self.api.delete_person(saved["id"]))
        self.assertEqual(self.api.people(), [])
        self.assertFalse(self.api.delete_person(saved["id"]))

    def test_chart_for_a_saved_person(self):
        saved = self.api.add_person(RAVI)
        chart = self.api.chart(saved["id"])
        self.assertEqual(chart["vedic"]["lagna"]["sign"], "Scorpio")

    def test_the_second_request_is_served_from_the_cache(self):
        saved = self.api.add_person(RAVI)
        self.api.chart(saved["id"])
        cached = list(self.api.store.charts_dir.glob("*.json"))
        self.assertEqual(len(cached), 1)
        self.assertEqual(self.api.chart(saved["id"])["vedic"]["lagna"]["sign"], "Scorpio")

    def test_editing_the_birth_time_does_not_serve_the_old_chart(self):
        saved = self.api.add_person(RAVI)
        before = self.api.chart(saved["id"])["vedic"]["lagna"]["lon"]
        self.api.add_person(dict(saved, time="04:35"))
        after = self.api.chart(saved["id"])["vedic"]["lagna"]["lon"]
        self.assertNotAlmostEqual(before, after, places=3)

    def test_a_chart_for_nobody(self):
        with self.assertRaises(ValidationError):
            self.api.chart("not-a-real-id")

    def test_settings_have_sensible_defaults(self):
        s = self.api.settings()
        self.assertEqual(s["language"], "en")
        self.assertEqual(s["chart_style"], "north")

    def test_a_setting_survives(self):
        self.api.set_setting("language", "hi")
        self.assertEqual(self.api.settings()["language"], "hi")

    def test_the_ayanamsa_setting_reaches_the_engine(self):
        """A setting that does not change the chart is a setting that does nothing."""
        saved = self.api.add_person(RAVI)
        lahiri = self.api.chart(saved["id"])["vedic"]["lagna"]["lon"]
        self.api.set_setting("ayanamsa", "raman")
        raman = self.api.chart(saved["id"])["vedic"]["lagna"]["lon"]
        self.assertNotAlmostEqual(lahiri, raman, places=3)

    def test_the_engine_is_not_loaded_until_something_needs_it(self):
        """Startup must not pay for the engine. A fresh Api holds no engine until a chart is asked for."""
        fresh = Api(store=Store(Path(self._tmp.name)))
        self.assertIsNone(fresh._engine)
        self.assertEqual(fresh.people(), [])
        self.assertIsNone(fresh._engine)

    def test_about(self):
        about = self.api.about()
        self.assertTrue(about["engine"])
        self.assertTrue(about["python"])
        self.assertEqual(about["people"], 0)


if __name__ == "__main__":
    unittest.main()
