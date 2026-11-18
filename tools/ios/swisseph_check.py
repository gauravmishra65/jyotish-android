"""Does Swiss Ephemeris give the same answers on an iPhone as it does everywhere else?

cibuildwheel runs this inside an iOS simulator after cross-compiling pyswisseph, so a pass means the C extension
loaded from its framework and computed correctly on Apple's runtime. The expected values were taken from the same
library on Linux, where the 926-check verification suite already passes: if iOS disagrees, the port is not safe.

Run by CI as: python -m tools.ios.swisseph_check
"""
import sys

import swisseph as swe

PROBLEMS = []


def near(label, got, want, tol):
    if abs(got - want) > tol:
        PROBLEMS.append(f"{label}: got {got!r}, expected {want!r} (tolerance {tol})")
    else:
        print(f"  ok  {label}: {got:.6f}")


def main():
    print(f"pyswisseph {swe.version} on {sys.platform}")

    # The calendar: J2000 noon is Julian day 2451545.0 by definition.
    near("julday J2000", swe.julday(2000, 1, 1, 12.0), 2451545.0, 1e-9)
    jd = 2451545.0

    # Tropical Sun at J2000, from the Swiss ephemeris files bundled in the wheel.
    near("Sun tropical", swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0], 280.36891967534336, 1e-6)

    # Sidereal mode has to carry across: this is the value every Vedic reading in the app rests on.
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    near("Lahiri ayanamsa", swe.get_ayanamsa_ut(jd), 23.857092353708822, 1e-6)
    near("Moon sidereal", swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0], 199.47055295238047, 1e-6)

    # A real chart from the fixtures: Varanasi, 14 July 1988, 14:35 IST (09:05 UT). Houses exercise a different
    # code path from planet positions, and the app draws every chart through it.
    jd2 = swe.julday(1988, 7, 14, 9.0 + 5.0 / 60)
    _cusps, ascmc = swe.houses_ex(jd2, 25.3176, 82.9739, b"P")
    near("Ascendant (Placidus)", ascmc[0], 234.6891151731387, 1e-6)
    near("Sun sidereal 1988", swe.calc_ut(jd2, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0], 88.43683075643847, 1e-6)

    if PROBLEMS:
        print("\niOS does NOT match the reference values:")
        for p in PROBLEMS:
            print("  " + p)
        return 1
    print("\nSwiss Ephemeris agrees with the Linux reference on iOS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
