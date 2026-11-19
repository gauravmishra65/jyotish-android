"""Does the astrology engine give the same answers on Windows?

This is the Windows counterpart of tools/ios/swisseph_check.py, and it asks a wider question. The iOS check
only had to prove that Swiss Ephemeris loaded and computed; here the whole engine runs, so the check goes
through engine_api exactly as the app will - a real person, a real chart - and compares against values the
Linux verification suite already stands behind.

Run by CI as: python windows/check_engine.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jyotish_win.bridge import Engine, chart_key   # noqa: E402

PROBLEMS: list[str] = []

# Ravi Shankar Tiwari, one of the fixtures the verification suite uses. No real person's birth details
# appear in this repository.
FIXTURE = {
    "name": "Ravi Shankar Tiwari", "gender": "M",
    "date": "1988-07-14", "time": "14:35",
    "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata",
    "place": "Varanasi, India", "time_confidence": "reliable",
}


def check(label, got, want):
    if got != want:
        PROBLEMS.append(f"{label}: got {got!r}, expected {want!r}")
    else:
        print(f"  ok  {label}: {got}")


def near(label, got, want, tol):
    if got is None or abs(got - want) > tol:
        PROBLEMS.append(f"{label}: got {got!r}, expected {want!r} (tolerance {tol})")
    else:
        print(f"  ok  {label}: {got:.6f}")


def main() -> int:
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    engine = Engine()
    print(f"engine: {engine.path}")

    print(f"engine version: {engine.version()}")

    c = engine.chart(FIXTURE)
    vedic = c["vedic"]

    # The chart the whole app is built on. Every expected value below was produced by this same engine on
    # Linux, where the 926-check verification suite passes. The tolerance is 1e-4 because the engine rounds
    # longitudes to five decimals before it hands them over - far finer than any reading uses.
    check("lagna sign", vedic["lagna"]["sign"], "Scorpio")
    near("Sun sidereal", vedic["planets"]["Sun"]["lon"], 88.43684, 1e-4)
    near("Moon sidereal", vedic["planets"]["Moon"]["lon"], 93.70968, 1e-4)
    check("Moon nakshatra", vedic["planets"]["Moon"]["nakshatra"], "Pushya")

    # Sidereal time handling and the dasha arithmetic are the two places a platform difference would show.
    check("current mahadasha", vedic["dashas"]["vimshottari"]["current"]["mahadasha"]["lord"], "Ketu")

    # zoneinfo comes from the tzdata package on Windows; a missing database shows up here first, because
    # 14:35 in Asia/Kolkata would silently become something else.
    check("local civil time", c["time_pipeline"]["local_civil"][:16], "1988-07-14 14:35")

    # The cache key must not drift between platforms, or a backup restored from a phone would recompute
    # every chart it carries.
    check("chart cache key", chart_key(FIXTURE), "7d082332f83c69dc101bb21e5c9ca63c")

    if PROBLEMS:
        print("\nWindows does NOT match the reference values:")
        for p in PROBLEMS:
            print("  " + p)
        return 1
    print("\nThe engine behaves on Windows as it does on Linux.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
