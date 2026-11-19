"""Birthplace search.

The behaviour here is the Android app's, deliberately: someone who has learned that "sitapur up" finds
the right Sitapur should not have to learn something else on Windows. These tests pin the habits, not
just the mechanism.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.places import fold, places   # noqa: E402


class FoldTest(unittest.TestCase):
    def test_case_and_accents(self):
        self.assertEqual(fold("São Paulo"), "sao paulo")
        self.assertEqual(fold("VARANASI"), "varanasi")


class SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = places()

    def first(self, query):
        found = self.p.search(query, 5)
        self.assertTrue(found, f"nothing found for {query!r}")
        return found[0]

    def test_the_list_is_actually_loaded(self):
        self.assertGreater(len(self.p.places), 50000)

    def test_a_plain_city(self):
        got = self.first("Varanasi")
        self.assertEqual(got["name"], "Varanasi")
        self.assertEqual(got["tz"], "Asia/Kolkata")
        self.assertAlmostEqual(got["lat"], 25.3, places=0)

    def test_every_result_carries_what_the_form_fills_in(self):
        for place in self.p.search("Delhi", 5):
            for key in ("label", "lat", "lon", "tz"):
                self.assertIn(key, place)
            self.assertIsInstance(place["lat"], float)
            self.assertTrue(place["tz"])

    def test_an_old_name_finds_the_current_one(self):
        self.assertEqual(self.first("Bombay")["name"], "Mumbai")

    def test_a_state_short_form_narrows(self):
        got = self.first("sitapur up")
        self.assertEqual(got["name"], "Sitapur")
        self.assertIn("Uttar Pradesh", got["label"])

    def test_commas_narrow_too(self):
        self.assertIn("Uttar Pradesh", self.first("Meerut, UP")["label"])

    def test_hindi(self):
        self.assertEqual(self.first("वाराणसी")["name"], "Varanasi")

    def test_a_single_letter_finds_nothing(self):
        self.assertEqual(self.p.search("V"), [])

    def test_an_empty_query_is_not_an_error(self):
        self.assertEqual(self.p.search(""), [])
        self.assertEqual(self.p.search("   "), [])

    def test_time_zones_outside_india(self):
        self.assertEqual(self.first("Singapore")["tz"], "Asia/Singapore")
        self.assertEqual(self.first("London")["tz"], "Europe/London")

    def test_the_bigger_place_wins_a_tie(self):
        """Rows are sorted by population, so the London people mean comes first."""
        self.assertIn("United Kingdom", self.first("London")["label"])

    def test_nearest_names_a_zone_for_typed_coordinates(self):
        near = self.p.nearest(25.3176, 82.9739)
        self.assertEqual(near["name"], "Varanasi")
        self.assertEqual(near["tz"], "Asia/Kolkata")
        self.assertLess(near["distance_km"], 50)


class PlacesReachTheEngineTest(unittest.TestCase):
    def test_a_chosen_place_builds_a_chart(self):
        """The point of the search: what it returns must be enough to compute with."""
        from tempfile import TemporaryDirectory

        from jyotish_win.api import Api
        from jyotish_win.storage import Store
        with TemporaryDirectory() as d:
            api = Api(store=Store(Path(d)))
            place = api.search_places("Varanasi", 1)[0]
            saved = api.add_person({"name": "From the list", "date": "1988-07-14", "time": "14:35",
                                    "lat": place["lat"], "lon": place["lon"], "tz": place["tz"],
                                    "place": place["label"]})
            self.assertEqual(api.chart(saved["id"])["vedic"]["lagna"]["sign"], "Scorpio")


if __name__ == "__main__":
    unittest.main()
