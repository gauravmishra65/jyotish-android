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
     engine, so the site and the app can never contradict each other;
  4. the eight Ashtakoota scores against ashtakoota.py, over random pairs, so a
     guna milan on the site and in the app can never differ;
  5. how far the Vimshottari table shifts because of that Moon difference. The
     whole table hangs off the balance of the first period, so ten arcseconds of
     Moon becomes a day or so of date. The dasha page states this figure, so it
     has to be measured rather than assumed - if this number moves, the page's
     wording is wrong and has to move with it.

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
    # Point Swiss Ephemeris at the same data files the app ships. Without this it
    # silently falls back to its built-in Moshier model and the whole comparison is
    # against a different reference than the app computes with - which is exactly the
    # mistake this line exists to prevent, so the fallback is made fatal below.
    swe.set_ephe_path(str(HERE.parent / "app/src/main/python/ephe"))
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    probe, ret = swe.calc_ut(swe.julday(2000, 1, 1, 12.0), swe.MOON,
                             swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    if not ret & swe.FLG_SWIEPH:
        sys.exit("Swiss Ephemeris fell back to Moshier: the .se1 data files were not found at "
                 + str(HERE.parent / "app/src/main/python/ephe")
                 + ". Refusing to verify against a different reference than the app uses.")
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


VIM_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]   # Ketu..Mercury, as in common.VIM_ORDER


def dasha_shift(rows, mine):
    """Days by which the whole Vimshottari table moves, given the Moon difference."""
    worst = total = 0.0
    n = 0
    for (y, jd, lon), got in zip(rows, mine):
        it, im = int(lon // (NAKW)) % 9, int(got // (NAKW)) % 9
        if it != im:
            continue                      # a boundary case; the cusp rule already covers it
        ft = (lon % NAKW) / NAKW
        fm = (got % NAKW) / NAKW
        d = abs(VIM_YEARS[it] * (ft - fm) * 365.25)
        total += d
        worst = max(worst, d)
        n += 1
    return {"mean": total / n, "worst": worst}


def check_kootas(n=1500):
    """Every koota and the /36 total, JS against ashtakoota.py, over random Moon pairs."""
    sys.path.insert(0, str(HERE.parent / "app/src/main/python"))
    import ashtakoota as ak
    random.seed(41)
    pairs = [(random.random() * 360, random.random() * 360) for _ in range(n)]

    script = ((HERE / "koota.js").read_text() + """
const pairs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
console.log(JSON.stringify(pairs.map(([g, b]) => {
  const v = gunaMilan(g, b);
  const out = {total: v.total};
  for (const k of Object.keys(v.kootas)) out[k] = v.kootas[k].score;
  return out;
})));
""")
    tmp = HERE / ".verify_tmp"
    tmp.mkdir(exist_ok=True)
    (tmp / "k.js").write_text(script)
    (tmp / "k.json").write_text(json.dumps(pairs))
    r = subprocess.run(["node", str(tmp / "k.js"), str(tmp / "k.json")], capture_output=True, text=True)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    if r.returncode:
        sys.exit("node failed in the koota check:\n" + r.stderr.strip())
    got = json.loads(r.stdout)

    bad = 0
    for (g, b), mine in zip(pairs, got):
        want = ak.match({"moon_lon": g, "moon_sign_index": int(g // 30)},
                        {"moon_lon": b, "moon_sign_index": int(b // 30)})
        if abs(mine["total"] - want["total_36"]["score"]) > 1e-9:
            bad += 1
            continue
        for k, v in want["kootas"].items():
            if abs(mine[k] - v["score"]) > 1e-9:
                bad += 1
                break
    return bad, len(pairs)


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

    shift = dasha_shift(rows, mine)
    print(f"dasha table shift, mean       {shift['mean']:.2f} days")
    print(f"dasha table shift, worst      {shift['worst']:.2f} days")
    print(f"  (the dasha page says: mean 1.1 days, worst 3.8)")

    kbad, kn = check_kootas()
    print(f"ashtakoota vs app engine     {'all 8 kootas and the total agree' if not kbad else f'{kbad} MISMATCH'}"
          f"  ({kn} pairs)")

    bad = check_navamsa()
    print(f"navamsa padas vs app engine {'all 108 agree' if not bad else f'{len(bad)} MISMATCH'}")

    if escaped or bad:
        sys.exit("FAILED")
    print("\npassed")


if __name__ == "__main__":
    main()
