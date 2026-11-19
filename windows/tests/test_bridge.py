"""The engine bridge.

These tests load the real engine, because a bridge that is only tested against a stub proves nothing about
the thing it bridges to. They stay deliberately few: the engine's own correctness is the verification
suite's job, and check_engine.py covers the values. What is tested here is the carrying.
"""
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.bridge import CHART_VERSION, Engine, chart_key   # noqa: E402

FIXTURE = {"name": "Neha Agarwal", "gender": "F", "date": "1992-03-02", "time": "08:10",
           "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "place": "Delhi, India"}


class ChartKeyTest(unittest.TestCase):
    def test_same_request_same_key(self):
        self.assertEqual(chart_key(FIXTURE), chart_key(dict(FIXTURE)))

    def test_key_ignores_the_order_fields_were_written_in(self):
        reordered = {k: FIXTURE[k] for k in reversed(list(FIXTURE))}
        self.assertEqual(chart_key(FIXTURE), chart_key(reordered))

    def test_a_different_person_gets_a_different_key(self):
        self.assertNotEqual(chart_key(FIXTURE), chart_key(dict(FIXTURE, time="08:11")))

    def test_the_version_is_part_of_the_key(self):
        """Bumping CHART_VERSION must retire every cached chart, which only works if it is in the key."""
        import jyotish_win.bridge as bridge
        before = chart_key(FIXTURE)
        bridge.CHART_VERSION = CHART_VERSION + 1
        try:
            self.assertNotEqual(before, chart_key(FIXTURE))
        finally:
            bridge.CHART_VERSION = CHART_VERSION


class EngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()

    def test_version_is_a_string_not_json(self):
        v = self.engine.version()
        self.assertIsInstance(v, str)
        self.assertTrue(v)

    def test_chart_comes_back_as_a_dict(self):
        c = self.engine.chart(FIXTURE)
        self.assertIn("vedic", c)
        self.assertIn("lagna", c["vedic"])

    def test_two_threads_do_not_corrupt_each_other(self):
        """The engine keeps module-level state - the ayanamsa mode, the ephemeris path - so without the
        lock two charts computed at once could read each other's settings. The interface calls this from
        a worker thread, so the case is real, not theoretical."""
        results, errors = [], []

        def run(req):
            try:
                results.append(self.engine.chart(req)["vedic"]["lagna"]["sign"])
            except Exception as e:                      # noqa: BLE001 - the test wants any failure
                errors.append(e)

        threads = [threading.Thread(target=run, args=(dict(FIXTURE, ayanamsa=a),))
                   for a in ("lahiri", "raman", "lahiri", "raman")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 4)

    def test_a_bad_request_raises_rather_than_returning_nonsense(self):
        with self.assertRaises(Exception):
            self.engine.chart({"name": "No Date"})


if __name__ == "__main__":
    unittest.main()
