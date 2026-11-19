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

    def test_the_lagna_carries_what_the_drawing_needs_to_place_it(self):
        """The drawing needs the lagna's sign as a number. The engine gives planets a sign_index but gives
        the lagna only a name and a longitude, so the drawing works it out - and must keep being able to."""
        lagna = self.chart["vedic"]["lagna"]
        self.assertNotIn("sign_index", lagna)       # if this ever appears, kundli.js will prefer it
        self.assertIsInstance(lagna["lon"], (int, float))
        self.assertEqual(int(lagna["lon"] // 30), 7)   # Scorpio, for the fixture

    def test_every_planet_carries_what_the_drawing_needs(self):
        for name, p in self.chart["vedic"]["planets"].items():
            self.assertIsInstance(p["house"], int, f"{name} has no house number")
            self.assertTrue(1 <= p["house"] <= 12, f"{name} is in house {p['house']}")
            self.assertTrue(0 <= p["sign_index"] <= 11, f"{name} has sign_index {p['sign_index']}")

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

    # --- the readings ---------------------------------------------------------------------------

    def test_the_readings_are_there_and_bilingual(self):
        """66 sections of ready-made reading come with every chart. The Windows build lays them out; it
        does not write them. If the engine ever stops shipping them, this is where it shows."""
        sections = self.chart["details"]["sections"]
        self.assertGreaterEqual(len(sections), 60)
        for s in sections:
            self.assertIn("title", s)
            for lang in ("en", "hi"):
                self.assertTrue(str(s["title"].get(lang, "")).strip(),
                                f"section {s.get('key')} has no {lang} title")

    def test_a_reading_is_made_of_only_the_three_shapes_the_page_can_draw(self):
        """sections.js draws a table, a list or a paragraph. A fourth shape would render as nothing."""
        for s in self.chart["details"]["sections"]:
            for block in s.get("blocks", []):
                self.assertIn(block["type"], ("table", "list", "para"),
                              f"{s.get('key')} has a {block['type']} block, which the page cannot draw")
                if block["type"] == "table":
                    self.assertIn("head", block)
                    self.assertIn("rows", block)
                    width = len(block["head"])
                    for row in block["rows"]:
                        self.assertEqual(len(row), width,
                                         f"{s.get('key')} has a row of {len(row)} under {width} headings")
                elif block["type"] == "list":
                    self.assertIn("items", block)
                else:
                    self.assertIn("text", block)

    def test_every_cell_of_a_reading_carries_both_languages(self):
        """bi() falls back to English, which would silently half-translate the Hindi screen."""
        def both(value, where):
            self.assertIsInstance(value, dict, f"{where} is not bilingual: {value!r}")
            for lang in ("en", "hi"):
                self.assertIn(lang, value, f"{where} has no {lang}")

        for s in self.chart["details"]["sections"]:
            for i, block in enumerate(s.get("blocks", [])):
                where = f"{s.get('key')} block {i}"
                if block["type"] == "table":
                    for h in block["head"]:
                        both(h, f"{where} heading")
                    for row in block["rows"]:
                        for cell in row:
                            both(cell, f"{where} cell")
                elif block["type"] == "list":
                    for item in block["items"]:
                        both(item, f"{where} item")
                else:
                    both(block["text"], f"{where} text")

    def test_the_divisional_charts_come_with_their_names(self):
        """Every varga the app can show has a name and a one-line use, in both languages."""
        details = self.chart["details"]
        self.assertEqual(len(details["vargas"]), len(details["varga_meta"]))
        for meta in details["varga_meta"]:
            self.assertIn(meta["key"], details["vargas"], f"{meta['key']} has no chart")
            for field in ("name", "use"):
                for lang in ("en", "hi"):
                    self.assertTrue(str(meta[field].get(lang, "")).strip(),
                                    f"{meta['key']} has no {lang} {field}")

    def test_a_divisional_chart_places_every_body_in_a_named_sign(self):
        signs = {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
                 "Sagittarius", "Capricorn", "Aquarius", "Pisces"}
        for key, varga in self.chart["details"]["vargas"].items():
            self.assertIn("Lagna", varga, f"{key} has no Lagna")
            for body, sign in varga.items():
                self.assertIn(sign, signs, f"{key} puts {body} in {sign!r}")


    # --- the lists the interface keeps of its own ------------------------------------------------

    def test_every_koota_and_porutham_the_engine_scores_has_a_label(self):
        """The screen keeps its own list of the eight kootas and the ten poruthams, and renders only
        what is on that list. An extra one from the engine would not fail - it would silently not be
        shown, which is how a missing Rajju would quietly disappear from a matching screen."""
        import re
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from jyotish_win.bridge import Engine as _Engine

        engine = _Engine()
        bride = dict(FIXTURE, name="Neha Agarwal", gender="F", date="1992-06-03", time="17:45",
                     lat=26.8467, lon=80.9462)
        ashtakoota = engine.match(engine.chart(FIXTURE), engine.chart(bride))["ashtakoota"]

        js = (WEB / "app.js").read_text(encoding="utf-8")
        listed = set(re.search(r"const KOOTAS = \[(.*?)\]", js, re.S).group(1).replace('"', "").split(", "))
        listed = {k.strip() for k in listed if k.strip()}
        self.assertEqual(set(ashtakoota["kootas"]), listed,
                         "the engine's kootas and the screen's list have drifted apart")

        strings = (WEB / "strings.js").read_text(encoding="utf-8")
        for koota in ashtakoota["kootas"]:
            self.assertIn(f"  koota_{koota}:", strings, f"{koota} has no label")
        for name in ashtakoota["porutham"]["items"]:
            self.assertIn(f"  p_{name}:", strings, f"the {name} porutham has no label")

    def test_every_body_a_chart_draws_has_an_abbreviation(self):
        """The kundli draws two-letter abbreviations. A body without one would be drawn under its full
        English name, across the lines of a house."""
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from jyotish_win.bridge import Engine as _Engine

        kundli = (WEB / "kundli.js").read_text(encoding="utf-8")
        for name in _Engine().chart(FIXTURE)["vedic"]["planets"]:
            self.assertIn(f"{name}:", kundli, f"{name} has no abbreviation to draw with")

    # --- the Hindi names -------------------------------------------------------------------------

    def test_the_glossary_covers_every_name_a_chart_prints(self):
        """The engine answers a chart in English names whatever the language, because those are the keys
        the rest of it counts on. The tables the desktop draws itself translate through this glossary, so
        a name missing from it would silently print in English on a Hindi screen."""
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from jyotish_win.bridge import Engine as _Engine

        engine = _Engine()
        words = engine.glossary()
        chart = engine.chart(FIXTURE)
        vedic = chart["vedic"]

        self.assertIn(vedic["lagna"]["sign"], words["signs"])
        for name, planet in vedic["planets"].items():
            self.assertIn(name, words["planets"], f"{name} has no Hindi name")
            self.assertIn(planet["sign"], words["signs"])
        self.assertIn(vedic["planets"]["Moon"]["nakshatra"], words["nakshatras"])
        self.assertIn(vedic["panchang"]["vara"], words["weekdays"])
        self.assertIn(vedic["panchang"]["paksha"], words["paksha"])
        # Fourteen names for both halves; the fifteenth is named for the moon, not numbered.
        self.assertEqual(len(words["tithis"]), 14)
        self.assertEqual(set(words["full_moon"]), {"Shukla", "Krishna"})
        self.assertEqual(len(words["signs"]), 12)
        self.assertEqual(len(words["nakshatras"]), 27)

        for table in ("signs", "planets", "nakshatras", "weekdays"):
            for english, hindi in words[table].items():
                self.assertTrue(any("\u0900" <= c <= "\u097f" for c in hindi),
                                f"{table}[{english}] is not in Devanagari: {hindi!r}")

    def test_a_dasha_lord_is_a_planet_the_glossary_knows(self):
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from jyotish_win.bridge import Engine as _Engine

        engine = _Engine()
        words = engine.glossary()["planets"]
        current = engine.chart(FIXTURE)["vedic"]["dashas"]["vimshottari"]["current"]
        for period in ("mahadasha", "antardasha"):
            self.assertIn(current[period]["lord"], words)

    # --- today ------------------------------------------------------------------------------------

    def test_the_panchang_limbs_keep_the_two_shapes_the_screen_reads(self):
        """Some limbs are {en, hi} and the ones that change during the day are {name: {en, hi}, ends}.
        The screen reads both. When it read only the first, Yoga and Karana silently showed a dash -
        which is what this test exists to catch next time."""
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from jyotish_win.bridge import Engine as _Engine
        day = _Engine().today({"date": "2026-11-20", "lat": 25.3176, "lon": 82.9739,
                               "tz": "Asia/Kolkata", "place": "Varanasi"})
        panchang = day["panchang"]

        for key in ("weekday", "weekday_lord", "moon_sign", "sun_sign", "month_amanta"):
            self.assertIn("en", panchang[key], f"{key} is no longer a plain bilingual pair")
            self.assertIn("hi", panchang[key])

        for key in ("tithi", "nakshatra", "yoga", "karana"):
            self.assertIn("name", panchang[key], f"{key} no longer carries a name")
            self.assertIn("en", panchang[key]["name"], f"{key}'s name is not bilingual")
            self.assertIn("hi", panchang[key]["name"])

        for key in ("rahu_kalam", "yamaganda", "gulika_kalam", "abhijit", "brahma_muhurta"):
            for edge in ("from", "to"):
                self.assertIn(edge, day["periods"][key], f"{key} has no {edge}")

        for which in ("choghadiya_day", "choghadiya_night"):
            self.assertEqual(len(day["periods"][which]), 8, f"{which} is not eight slots")
            for slot in day["periods"][which]:
                for field in ("from", "to", "name"):
                    self.assertIn(field, slot)


class WebAssetsTest(unittest.TestCase):
    """The shell cannot be run in CI, so at least prove its pieces are present and refer to each other."""

    def test_the_three_files_exist(self):
        for name in ("index.html", "app.css", "app.js", "strings.js", "sections.js", "kundli.js"):
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
        self.assertIn('t("delete_again")', js)
        self.assertIn("Click again to delete",
                      (WEB / "strings.js").read_text(encoding="utf-8"))

    def test_the_add_button_does_not_hand_its_click_event_to_the_form(self):
        """showAddPerson takes an optional person to edit. Wiring it straight to addEventListener would
        pass the click Event as that person, and the Add screen would think it was editing one."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertNotIn('addEventListener("click", showAddPerson)', js)
        self.assertIn('() => showAddPerson()', js)

    def test_the_drawing_is_loaded_before_the_script_that_uses_it(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertIn("kundli.js", html)
        self.assertLess(html.index("kundli.js"), html.index("app.js"))

    def test_choosing_a_place_fills_the_three_fields_it_should(self):
        """The whole point of the place search is that nobody looks up coordinates by hand."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        picker = js[js.index("function placeField("):js.index("/* One form for both jobs.")]
        for field in ("-lat`).value", "-lon`).value", "-tz`).value"):
            self.assertIn(field, picker, f"picking a place does not set the {field.split('`')[0]} field")
        # The same picker serves the birth form and the muhurta form, which is why it takes a prefix.
        self.assertIn('function placeField(existing, prefix = "f"', js)
        self.assertIn('placeField(null, "mu"', js)

    # --- both languages -------------------------------------------------------------------------

    def test_every_word_the_interface_says_exists_in_both_languages(self):
        """The engine answers in English and Hindi. A shell that only spoke English would leave a Hindi
        reader with Hindi readings under English headings, which is worse than either."""
        import re

        table = (WEB / "strings.js").read_text(encoding="utf-8")
        body = table[table.index("const STRINGS = {"):table.index("\nlet LANG")]
        entries = re.findall(r"^\s{2}(\w+):\s*\{(.*?)\n?\s*\},?$", body, re.S | re.M)
        self.assertGreater(len(entries), 30, "the string table looks truncated")
        for key, value in entries:
            self.assertIn("en:", value, f"{key} has no English")
            self.assertIn("hi:", value, f"{key} has no Hindi")
            self.assertRegex(value, r'hi:\s*"[^"]*[\u0900-\u097F]',
                             f"{key}'s Hindi is not written in Devanagari")

    def test_every_string_the_scripts_ask_for_is_in_the_table(self):
        """t("nope") throws. Catching it here is better than catching it when a screen goes blank."""
        import re

        table = (WEB / "strings.js").read_text(encoding="utf-8")
        known = set(re.findall(r"^\s{2}(\w+):\s*\{", table, re.M))
        for name in ("app.js", "sections.js", "kundli.js"):
            for key in re.findall(r'\bt\("(\w+)"', (WEB / name).read_text(encoding="utf-8")):
                self.assertIn(key, known, f"{name} asks for t({key!r}), which strings.js does not have")

    def test_the_words_are_loaded_before_the_scripts_that_say_them(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index("strings.js"), html.index("app.js"))
        self.assertLess(html.index("strings.js"), html.index("sections.js"))

    def test_the_divisional_charts_are_drawn_from_their_own_lagna(self):
        """A varga arrives as sign names only; counting its houses from the birth Lagna would put every
        planet in the wrong house of every varga, and the drawing would still look plausible."""
        kundli = (WEB / "kundli.js").read_text(encoding="utf-8")
        self.assertIn("function vargaVedic(", kundli)
        self.assertIn("SIGNS.indexOf(varga.Lagna)", kundli)
        self.assertIn("vargaSvg(", (WEB / "app.js").read_text(encoding="utf-8"))

    def test_matching_names_the_bride_rather_than_asking_for_two_people(self):
        """Who is the bride changes the answer, so the screen must label the two fields rather than
        taking them in whatever order they were chosen."""
        js = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertIn('t("groom")', js)
        self.assertIn('t("bride")', js)
        self.assertIn("api().match(groom, bride)", js)

    def test_the_element_ids_the_script_needs_are_in_the_page(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        for element_id in ("people", "count", "main", "new-person", "language", "tools"):
            self.assertIn(f'id="{element_id}"', html)


if __name__ == "__main__":
    unittest.main()
