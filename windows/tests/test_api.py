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

NEHA = {"name": "Neha Agarwal", "gender": "F", "date": "1992-06-03", "time": "17:45",
        "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "place": "Lucknow"}

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

    def test_a_region_without_a_city_is_refused(self):
        """Found on a real machine: "Asia" reached zoneinfo, which on Windows tried to open a folder as
        a file and put a raw PermissionError with a Windows path in front of the user."""
        with self.assertRaises(ValidationError) as e:
            validate(dict(RAVI, tz="Asia"))
        self.assertIn("Asia/Kolkata", str(e.exception))

    def test_a_nonsense_time_zone_is_refused(self):
        for bad in ("Mars/Olympus", "IST", "GMT+5:30", "", "   "):
            with self.assertRaises(ValidationError):
                validate(dict(RAVI, tz=bad))

    def test_real_time_zones_pass(self):
        for good in ("Asia/Kolkata", "Asia/Singapore", "Europe/London", "UTC"):
            validate(dict(RAVI, tz=good))

    def test_the_time_zone_is_trimmed(self):
        self.assertEqual(validate(dict(RAVI, tz="  Asia/Kolkata  "))["tz"], "Asia/Kolkata")

    def test_the_offered_list_is_real_and_useful(self):
        from jyotish_win.api import time_zones
        zones = time_zones()
        self.assertGreater(len(zones), 300)
        self.assertEqual(zones[0], "Asia/Kolkata")      # the common ones lead
        self.assertIn("Asia/Singapore", zones)
        self.assertNotIn("Asia", zones)                 # the trap that caused this test

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

    def test_a_profile_saved_by_an_older_build_still_fails_readably(self):
        """Profiles written before the time zone was checked are already on disk. Asking for their chart
        must give the same sentence, not the raw error that prompted the check."""
        self.api.store.save_profiles([dict(RAVI, id="old", tz="Asia")])
        with self.assertRaises(ValidationError) as e:
            self.api.chart("old")
        self.assertIn("Asia/Kolkata", str(e.exception))

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

    # --- matching -------------------------------------------------------------------------------

    def test_matching_two_people(self):
        groom = self.api.add_person(RAVI)
        bride = self.api.add_person(dict(NEHA))
        m = self.api.match(groom["id"], bride["id"])
        total = m["ashtakoota"]["total_36"]
        self.assertEqual(total["out_of"], 36)
        self.assertTrue(0 <= total["score"] <= 36)
        self.assertEqual(m["people"], [groom["name"], bride["name"]])
        self.assertEqual(m["ashtakoota"]["bride_is"], "B")

    def test_the_bride_is_the_second_person_not_whichever_way_round(self):
        """Several kootas are counted from the bride's Moon to the groom's and not the other way round,
        so swapping the two has to be able to change the answer. If this ever comes out symmetrical,
        the bride flag has stopped reaching the engine."""
        groom = self.api.add_person(RAVI)
        bride = self.api.add_person(dict(NEHA))
        one = self.api.match(groom["id"], bride["id"])["ashtakoota"]
        other = self.api.match(bride["id"], groom["id"])["ashtakoota"]
        self.assertEqual(other["bride_is"], "B")
        self.assertNotEqual(one["kootas"]["tara"], other["kootas"]["tara"])

    def test_a_person_cannot_be_matched_with_themselves(self):
        saved = self.api.add_person(RAVI)
        with self.assertRaises(ValidationError):
            self.api.match(saved["id"], saved["id"])

    def test_matching_someone_who_is_not_saved(self):
        saved = self.api.add_person(RAVI)
        with self.assertRaises(ValidationError):
            self.api.match(saved["id"], "nobody")

    # --- reports --------------------------------------------------------------------------------

    def test_a_report_is_written_as_one_self_contained_page(self):
        """The file has to still work when it is emailed to somebody who does not have this app: one
        page, with nothing beside it to load."""
        import os
        folder = Path(self._tmp.name) / "reports"
        os.environ["JYOTISH_REPORTS_DIR"] = str(folder)
        try:
            saved = self.api.add_person(RAVI)
            made = self.api.make_report(saved["id"], "mangal")
            written = Path(made["path"])
            self.assertTrue(written.is_file())
            html = written.read_text(encoding="utf-8")
            self.assertIn("<html", html.lower())
            self.assertNotIn("<link", html.lower())        # no stylesheet beside it
            self.assertNotIn("<script src", html.lower())  # nothing fetched when it opens
            self.assertIn(made["file"], [r["file"] for r in self.api.reports()])
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_a_report_is_written_in_the_chosen_language(self):
        import os
        os.environ["JYOTISH_REPORTS_DIR"] = str(Path(self._tmp.name) / "reports")
        try:
            saved = self.api.add_person(RAVI)
            self.api.set_setting("language", "hi")
            html = Path(self.api.make_report(saved["id"], "chandra")["path"]).read_text(encoding="utf-8")
            self.assertTrue(any("\u0900" <= c <= "\u097f" for c in html),
                            "the Hindi report came out with no Devanagari in it")
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_an_unknown_report_is_refused(self):
        saved = self.api.add_person(RAVI)
        with self.assertRaises(ValidationError):
            self.api.make_report(saved["id"], "whatever")

    def test_only_saved_reports_can_be_opened(self):
        """open_path hands a file to the operating system. It must refuse anything this app did not
        write, so that a path arriving from somewhere unexpected cannot become a way to launch it."""
        import os
        folder = Path(self._tmp.name) / "reports"
        os.environ["JYOTISH_REPORTS_DIR"] = str(folder)
        try:
            outsider = Path(self._tmp.name) / "elsewhere.html"
            outsider.write_text("<html></html>", encoding="utf-8")
            for path in (str(outsider), str(folder / ".." / "elsewhere.html"), str(folder / "nothing.html")):
                with self.assertRaises(ValidationError, msg=f"{path} was not refused"):
                    self.api.open_path(path)
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_a_name_that_windows_would_reject_still_makes_a_file(self):
        from jyotish_win.api import _safe_filename
        self.assertEqual(_safe_filename('a/b:c*d?'), "a-b-c-d")
        self.assertEqual(_safe_filename("trailing. "), "trailing")
        self.assertEqual(_safe_filename("नेहा अग्रवाल"), "नेहा अग्रवाल")   # left as it is: NTFS is fine with it
        self.assertEqual(_safe_filename("///"), "Report")

    # --- backup through the API -------------------------------------------------------------------

    def test_backup_and_restore_through_the_api(self):
        import os
        os.environ["JYOTISH_REPORTS_DIR"] = str(Path(self._tmp.name) / "reports")
        try:
            self.api.add_person(RAVI)
            self.api.add_person(dict(NEHA))
            written = self.api.backup("a good password")
            self.assertEqual(written["count"], 2)

            empty = Api(store=Store(Path(self._tmp.name) / "other"), engine=self.engine)
            done = empty.restore(written["path"], "a good password")
            self.assertEqual((done["added"], done["updated"], done["skipped"]), (2, 0, 0))
            self.assertEqual(sorted(p["name"] for p in empty.people()),
                             sorted([RAVI["name"], NEHA["name"]]))
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_a_restore_adds_rather_than_replacing(self):
        """Somebody restoring an old phone backup onto a desktop they have been using must not lose the
        desktop's work to do it."""
        import os
        os.environ["JYOTISH_REPORTS_DIR"] = str(Path(self._tmp.name) / "reports")
        try:
            self.api.add_person(RAVI)
            written = self.api.backup("a good password")

            other = Api(store=Store(Path(self._tmp.name) / "other"), engine=self.engine)
            kept = other.add_person(dict(NEHA))
            done = other.restore(written["path"], "a good password")
            self.assertEqual(done["added"], 1)
            self.assertIn(kept["name"], [p["name"] for p in other.people()])
            self.assertEqual(len(other.people()), 2)
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_backing_up_nobody(self):
        with self.assertRaises(ValidationError):
            self.api.backup("a good password")

    def test_restoring_from_a_file_that_is_not_there(self):
        with self.assertRaises(ValidationError):
            self.api.restore(str(Path(self._tmp.name) / "nothing.gjb"), "a good password")

    # --- settings -------------------------------------------------------------------------------

    def test_a_setting_the_engine_would_reject_is_refused(self):
        """A bad ayanamsa saved to settings.json would break every chart from then on, including after
        a restart, with nothing on screen to say why."""
        for key, value in (("ayanamsa", "nonsense"), ("house_system", "vehlow"),
                           ("node", "neither"), ("language", "fr"), ("theme", "neon")):
            with self.assertRaises(ValidationError, msg=f"{key}={value} was accepted"):
                self.api.set_setting(key, value)

    def test_every_offered_setting_value_is_one_the_engine_takes(self):
        """The screen offers what this list holds, so the list has to be right."""
        saved = self.api.add_person(RAVI)
        for key in ("ayanamsa", "house_system", "node"):
            for value, _ in Api.CHOICES[key]:
                self.api.set_setting(key, value)
                self.assertTrue(self.api.chart(saved["id"])["vedic"]["lagna"]["sign"],
                                f"{key}={value} did not produce a chart")

    def test_the_report_credits_reach_the_report(self):
        import os
        os.environ["JYOTISH_REPORTS_DIR"] = str(Path(self._tmp.name) / "reports")
        try:
            saved = self.api.add_person(RAVI)
            self.api.set_setting("report_by", "Pandit Someone")
            self.api.set_setting("report_site", "example.test")
            html = Path(self.api.make_report(saved["id"], "chandra")["path"]).read_text(encoding="utf-8")
            self.assertIn("Pandit Someone", html)
            self.assertIn("example.test", html)
        finally:
            os.environ.pop("JYOTISH_REPORTS_DIR", None)

    def test_about(self):
        about = self.api.about()
        self.assertTrue(about["engine"])
        self.assertTrue(about["python"])
        self.assertEqual(about["people"], 0)


if __name__ == "__main__":
    unittest.main()
