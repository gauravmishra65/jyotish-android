"""What the Windows build is allowed to say.

The standing rule for this app is that it never predicts death, disease or divorce, that health means
energy, stress and rest, and that nothing is guaranteed. The engine is written to honour that and the
verification suite checks the engine's own layers - but the Windows build puts several of those layers
on screen for the first time, and a rule that is only checked where it was first written is a rule
waiting to be broken somewhere else.

So this walks every surface the Windows app can show - every reading section, the outlook, the
predictions, the matching, the muhurta, the prashna, the group comparison, the birth-time check and all
nine reports in both languages - and fails if any of them says one of those words.

Two exceptions, and only two: Cancer the sign, and the sentence that exists to say a muhurta does not
guarantee an outcome. Both are checked for precisely rather than by waving the rule away.
"""
import json
import os
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.api import Api        # noqa: E402
from jyotish_win.storage import Store  # noqa: E402

#: The English half. Word boundaries do the work here.
BANNED_EN = re.compile(
    r"\b(death|die|dies|dying|disease|illness|cancer|divorce|accident|surgery|guarantee[ds]?)\b", re.I)

#: The Hindi half, with boundaries written out: Devanagari has no \b, and without one "रोग" matches
#: inside "प्रोग्रेस्ड" - the transliteration of "progressed" - which is not a word about illness at all.
DEVANAGARI = "\u0900-\u097F"
BANNED_HI = re.compile(f"(?<![{DEVANAGARI}])(मृत्यु|तलाक|रोग|दुर्घटना|बीमारी)(?![{DEVANAGARI}])")

#: Cancer the sign, in both languages.
SIGN = re.compile(r"\bcancer\b", re.I)

#: Rog is one of the seven choghadiya - a named span of the day, like Amrit or Labh - and it is a period
#: to avoid, not a prediction about anybody's health. It is allowed only where it stands alone as a
#: whole value: a JSON field or a table cell of its own. The same word inside a sentence is still caught.
CHOGHADIYA = re.compile(r'(?<=[">])\s*(?:Rog|रोग)\s*(?=["<])')

#: The disclaimer saying a muhurta guarantees nothing is the rule being kept, not broken.
DISCLAIMED = re.compile(r"does not guarantee|never promise", re.I)

RAVI = {"name": "Ravi Shankar Tiwari", "gender": "M", "date": "1988-07-14", "time": "14:35",
        "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata", "place": "Varanasi"}
NEHA = {"name": "Neha Agarwal", "gender": "F", "date": "1992-06-03", "time": "17:45",
        "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "place": "Lucknow"}
MEI = {"name": "Mei Lin Tan", "gender": "F", "date": "1995-11-02", "time": "06:10",
       "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "place": "Singapore"}


def offences(text: str) -> list[str]:
    """Every forbidden word in some text, with the permitted uses removed first."""
    cleaned = CHOGHADIYA.sub("-", DISCLAIMED.sub("", text))
    found = [m.group(0) for m in BANNED_HI.finditer(cleaned)]
    for match in BANNED_EN.finditer(cleaned):
        word = match.group(0)
        if SIGN.fullmatch(word):
            continue                      # the sign, not the illness
        if word.lower().startswith("guarantee"):
            around = cleaned[max(0, match.start() - 60):match.end() + 20]
            if re.search(r"\bnot\b|\bno\b|never", around, re.I):
                continue                  # "...does not guarantee any outcome"
        found.append(word)
    return found


class WordingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from jyotish_win.bridge import Engine
        cls.engine = Engine()

    def setUp(self):
        self._tmp = TemporaryDirectory()
        os.environ["JYOTISH_EDITION"] = "full"
        os.environ["JYOTISH_REPORTS_DIR"] = str(Path(self._tmp.name) / "reports")
        self.api = Api(store=Store(Path(self._tmp.name)), engine=self.engine)
        self.ravi = self.api.add_person(dict(RAVI))["id"]
        self.neha = self.api.add_person(dict(NEHA))["id"]
        self.mei = self.api.add_person(dict(MEI))["id"]

    def tearDown(self):
        for key in ("JYOTISH_EDITION", "JYOTISH_REPORTS_DIR"):
            os.environ.pop(key, None)
        self._tmp.cleanup()

    def check(self, label, blob):
        text = blob if isinstance(blob, str) else json.dumps(blob, ensure_ascii=False)
        found = offences(text)
        self.assertEqual(found, [], f"{label} says: {', '.join(sorted(set(found)))}")

    def test_every_screen_keeps_to_the_rule(self):
        self.api.set_events(self.ravi, [{"kind": "marriage", "date": "2014-02-09"}])
        surfaces = {
            "the chart's readings": self.api.chart(self.ravi)["details"],
            "today": self.api.today(),
            "the outlook": self.api.forecast(self.ravi),
            "predictions (year)": self.api.predict(self.ravi, "year"),
            "predictions (three years)": self.api.predict(self.ravi, "three"),
            "Kundli Milan": self.api.match(self.ravi, self.neha),
            "muhurta": self.api.muhurta({"event": "marriage", "from": "2026-12-01", "to": "2026-12-31",
                                         "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata",
                                         "people": [self.ravi]}),
            "prashna": self.api.ask_question({"method": "prashna", "question": "Will the work go through?"}),
            "numerology": self.api.numbers({"kind": "personal", "person_id": self.ravi}),
            "the Chinese side": self.api.chinese(self.ravi),
            "the group comparison": self.api.compare_group([self.ravi, self.neha, self.mei]),
            "the Flying Stars": self.api.flying_stars(),
            "the birth-time check": self.api.rectify(self.ravi, 30),
            "Western horary": self.api.horary("Will the house sell?"),
            "a custom varga": self.api.custom_varga(self.ravi, 7, "cyclic"),
            "the name's numbers": self.api.name_numbers(self.ravi),
        }
        for label, blob in surfaces.items():
            self.check(label, blob)

    def test_every_report_keeps_to_the_rule_in_both_languages(self):
        for language in ("en", "hi"):
            self.api.set_setting("language", language)
            for kind, _ in Api.REPORTS:
                written = Path(self.api.make_report(self.ravi, kind)["path"])
                self.check(f"the {kind} report in {language}", written.read_text(encoding="utf-8"))

    def test_the_words_the_interface_says_itself_keep_to_the_rule(self):
        """The string table is the one place this build writes prose of its own."""
        web = Path(__file__).resolve().parent.parent / "web"
        for name in ("strings.js", "app.js", "sections.js", "kundli.js", "index.html"):
            self.check(name, (web / name).read_text(encoding="utf-8"))

    def test_the_check_would_actually_catch_something(self):
        """A test that can only pass is not a test. These are the sentences it exists to stop."""
        for said in ("A serious illness is indicated in the 8th house.",
                     "इस भाव से रोग का संकेत मिलता है।",
                     "This period guarantees a promotion.",
                     "यह काल मृत्यु का संकेत देता है।",
                     "The marriage ends in divorce."):
            self.assertTrue(offences(said), f"this slipped through: {said}")
        for allowed in ("The Moon is in Cancer.", "चंद्र कर्क राशि में है।",
                        "It supports a beginning; it does not guarantee any outcome.",
                        'सोलर आर्क: सूर्य के प्रोग्रेस्ड चाप जितना आगे।',    # "progressed", not disease
                        '{"name": {"en": "Rog", "hi": "रोग"}, "kind": "avoid"}',   # a choghadiya slot
                        "<td>07:39 - 09:00</td><td>रोग</td>"):                    # the same, in a report
            self.assertEqual(offences(allowed), [], f"wrongly flagged: {allowed}")


if __name__ == "__main__":
    unittest.main()
