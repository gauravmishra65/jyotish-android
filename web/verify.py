#!/usr/bin/env python3
"""Check the browser engine against Swiss Ephemeris.

    python3 web/verify.py

The site's whole claim is that a calculation run in the visitor's browser is as
good as one run against the real ephemeris. This is what backs that claim, and
it must pass before the pages go anywhere.

It checks three things:
  1. the Moon's sidereal longitude from moon.js against pyswisseph, over
     thousands of random dates;
  2. that no disagreement about a nakshatra or pada ever escapes the cusp band
     the pages use to flag an uncertain answer - the number that must be zero;
  3. the navamsa rule the pada tables are built on, against the app's own
     engine, so the site and the app can never contradict each other.

Needs: pip install pyswisseph, and node on the PATH.
"""
import json, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).parent
NAKW, PADAW, CUSP = 360 / 27, 360 / 108, 0.02
SAMPLES, YEAR_LO, YEAR_HI = 5000, 1900, 2050

try:
    import swisseph as swe
except ImportError:
    sys.exit("pyswisseph is not installed: pip install pyswisseph")


def truth():
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    random.seed(7)
    rows = []
    for _ in range(SAMPLES):
        y = random.randint(YEAR_LO, YEAR_HI)
        jd = swe.julday(y, random.randint(1, 12), random.randint(1, 28), random.random() * 24)
        lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        rows.append([y, jd, lon])
    return rows


def ours(rows):
    script = (HERE / "moon.js").read_text().replace("export function", "function")
    script += """
const rows = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
console.log(JSON.stringify(rows.map(([y, jd]) => moonSidereal(jd, y, 1))));
"""
    tmp = HERE / ".verify_tmp"
    tmp.mkdir(exist_ok=True)
    (tmp / "run.js").write_text(script)
    (tmp / "in.json").write_text(json.dumps(rows))
    r = subprocess.run(["node", str(tmp / "run.js"), str(tmp / "in.json")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("node failed:\n" + r.stderr.strip())
    out = r.stdout
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return json.loads(out)


def check_navamsa():
    sys.path.insert(0, str(HERE.parent / "app/src/main/python"))
    from vedic import varga_sign
    bad = [i for i in range(108)
           if int((i * PADAW + 0.5) * 9 // 30) % 12 != varga_sign(i * PADAW + 0.5, 9) % 12]
    return bad


def main():
    rows, mine = truth(), None
    mine = ours(rows)
    worst = total = 0.0
    disagree, escaped = 0, 0
    for (y, jd, lon), got in zip(rows, mine):
        e = abs(got - lon)
        if e > 180:
            e = 360 - e
        total += e
        worst = max(worst, e)
        nak = int(lon // NAKW) != int(got // NAKW)
        pada = int(lon // PADAW) != int(got // PADAW)
        if nak or pada:
            disagree += 1
            edge = got % PADAW
            if min(edge, PADAW - edge) >= CUSP:
                escaped += 1
                print(f"  SILENT ERROR  {y}  swisseph {lon:.5f}  ours {got:.5f}")

    print(f"samples                     {len(rows)}  ({YEAR_LO}-{YEAR_HI})")
    print(f"mean difference             {total / len(rows) * 3600:.1f} arcsec")
    print(f"worst difference            {worst * 3600:.1f} arcsec")
    print(f"nakshatra or pada differs   {disagree}")
    print(f"NOT flagged as on the cusp  {escaped}")

    bad = check_navamsa()
    print(f"navamsa padas vs app engine {'all 108 agree' if not bad else f'{len(bad)} MISMATCH'}")

    if escaped or bad:
        sys.exit("FAILED")
    print("\npassed")


if __name__ == "__main__":
    main()
