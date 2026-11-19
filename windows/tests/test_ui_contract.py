"""The fields the interface reads out of a chart.

JavaScript reading a key the engine does not have fails silently: the screen shows a dash, or an empty
range like "Ketu to", and nobody notices until a user asks why. Three such mistakes were in the first
draft of app.js - dasha dates were assumed to be `from`/`to` when they are `start`/`end`, sunrise was
looked for in `time_pipeline` when it lives in `vedic.panchang`, and the degree within a sign was being
recomputed when the engine already formats it.

So this file writes the contract down. If the engine renames one of these, CI fails here rather than the
app quietly going blank.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.bridge import Engine   # noqa: E402

FIXTURE = {"name": "Ravi Shankar Tiwari", "gender": "M", "date": "1988-07-14", "time": "14:35",
           "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata"}

WEB = Path(__file__).resolve().parent.parent / "web"


class ChartContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = Engine().chart(FIXTURE)

    def test_lagna(self):
        lagna = self.chart["vedic"]["lagna"]
        for key in ("sign", "dms", "lon"):
            self.assertIn(key, lagna)

    def test_every_planet_has_what_the_table_prints(self):
        for name, p in self.chart["vedic"]["planets"].items():
            for key in ("sign", "dms", "deg_in_sign", "retrograde"):
                self.assertIn(key, p, f"{name} has no {key}")

    def test_the_moon_carries_its_nakshatra_and_pada(self):
        moon = self.chart["vedic"]["planets"]["Moon"]
        self.assertIn("nakshatra", moon)
        self.assertIn("pada", moon)

    def test_panchang_fields_shown_on_the_chart_card(self):
        pan = self.chart["vedic"]["panchang"]
        for key in ("sunrise_local", "tithi", "paksha", "vara"):
            self.assertIn(key, pan)

    def test_dasha_periods_use_start_and_end(self):
        current = self.chart["vedic"]["dashas"]["vimshottari"]["current"]
        for period in ("mahadasha", "antardasha"):
            self.assertIn(period, current)
            for key in ("lord", "start", "end"):
                self.assertIn(key, current[period], f"{period} has no {key}")


class WebAssetsTest(unittest.TestCase):
    """The shell cannot be run in CI, so at least prove its pieces are present and refer to each other."""

    def test_the_three_files_exist(self):
        for name in ("index.html", "app.css", "app.js"):
            self.assertTrue((WEB / name).exists(), f"{name} is missing")

    def test_the_page_loads_its_script_and_styles(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertIn("app.css", html)
        self.assertIn("app.js", html)

    def test_every_api_method_the_interface_calls_exists_in_python(self):
        """The JavaScript calls api().something(); if Python has no such method it fails at runtime."""
        import re

        from jyotish_win.api import Api
        js = (WEB / "app.js").read_text(encoding="utf-8")
        called = set(re.findall(r"api\(\)\.(\w+)\(", js))
        self.assertTrue(called, "no API calls were found in app.js - has it been rewritten?")
        for name in sorted(called):
            self.assertTrue(hasattr(Api, name), f"app.js calls api().{name}(), which Api does not have")

    def test_every_screen_offers_a_way_out(self):
        """A person whose chart will not build must still be fixable or removable. The first build put
        delete only on the chart screen, so a profile with a bad time zone was stuck on screen with no
        way to edit or delete it - the one case where you most need both."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        error_branch = js[js.index("chart = await api().chart(id);"):js.index("const v = chart.vedic;")]
        self.assertIn("deleteButton(", error_branch, "the failed-chart screen offers no delete")
        self.assertIn("showAddPerson(who)", error_branch, "the failed-chart screen offers no way to edit")

    def test_deleting_does_not_depend_on_a_native_dialog(self):
        """window.confirm is at the embedded browser's discretion; if it silently answers no, the delete
        button looks broken. The confirmation is in the page instead."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("window.confirm(", js)   # the call, not the comment explaining its absence
        self.assertIn("Click again to delete", js)

    def test_the_add_button_does_not_hand_its_click_event_to_the_form(self):
        """showAddPerson takes an optional person to edit. Wiring it straight to addEventListener would
        pass the click Event as that person, and the Add screen would think it was editing one."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertNotIn('addEventListener("click", showAddPerson)', js)
        self.assertIn('() => showAddPerson()', js)

    def test_the_element_ids_the_script_needs_are_in_the_page(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        for element_id in ("people", "count", "main", "new-person"):
            self.assertIn(f'id="{element_id}"', html)


if __name__ == "__main__":
    unittest.main()
