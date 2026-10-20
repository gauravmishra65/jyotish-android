#!/usr/bin/env python3
"""rectify_windows.py - narrow an uncertain birth time using life events.

Scans a window around the recorded time minute by minute and reports the time segments in which the
lagna, Navamsa lagna and Dashamsa lagna stay constant, then shows the running Vimshottari mahadasha /
antardasha (and the houses those planets rule for that lagna) on each dated life event.
This is deterministic groundwork: judging which segment best fits the events is the astrologer's call,
and the more independent events supplied, the stronger the result. It does not pick a winner.

  python rectify_windows.py --date 1990-05-17 --time 14:30 --lat 28.6139 --lon 77.2090 \
     --window-min 90 --events "2015-06-12:marriage,2019-03-01:first child,2021-09-15:job loss"
"""
import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swisseph as swe  # noqa: E402
if os.path.isdir(os.path.join(HERE, "ephe")):
    swe.set_ephe_path(os.path.join(HERE, "ephe"))
import common  # noqa: E402
import vedic  # noqa: E402
import calibration  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", required=True)
    p.add_argument("--time", required=True)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--tz")
    p.add_argument("--utc-offset", type=float)
    p.add_argument("--window-min", type=int, default=60, help="minutes either side of the recorded time")
    p.add_argument("--events", default="", help="YYYY-MM-DD:label,YYYY-MM-DD:label")
    p.add_argument("--ayanamsa", default="lahiri")
    p.add_argument("--vargas", default="9,10", help="vargas whose lagna defines a segment, in PVR's order (D-9 or D-10 first, then finer)")
    p.add_argument("--score", action="store_true", help="score each segment by the chance probability of its past-event hits")
    p.add_argument("--gender", default="M")
    p.add_argument("--out", default="rectify.json")
    a = p.parse_args()
    VARGAS = [int(x) for x in a.vargas.split(",") if x.strip()]
    t = common.resolve_time(a.date, a.time, a.lat, a.lon, a.tz, a.utc_offset)
    base_jd, base_utc, naive = t["jd_ut"], t["_utc_dt"], t["_naive"]
    events = []
    for chunk in [c for c in a.events.split(",") if c.strip()]:
        d, _, lab = chunk.partition(":")
        events.append((dt.datetime.strptime(d.strip(), "%Y-%m-%d").replace(hour=12), lab.strip() or d.strip()))

    def state(m):
        jd = base_jd + m / 1440.0
        asc = vedic._asc_at(jd, a.lat, a.lon, a.ayanamsa)
        return jd, asc, tuple([common.sign_of(asc)] + [vedic.varga_sign(asc, n) for n in VARGAS])

    segs, cur = [], None
    for m in range(-a.window_min, a.window_min + 1):
        jd, asc, key = state(m)
        if cur and cur["key"] == key:
            cur["to"], cur["asc_to"] = m, asc
        else:
            if cur:
                segs.append(cur)
            cur = {"key": key, "from": m, "to": m, "asc_from": asc, "asc_to": asc}
    segs.append(cur)
    out = {"recorded_local_time": t["local_civil"], "window_minutes": a.window_min, "warnings": t["warnings"], "segments": []}
    for s in segs:
        mid = (s["from"] + s["to"]) // 2
        jd = base_jd + mid / 1440.0
        utc_mid = base_utc + dt.timedelta(minutes=mid)
        moon = vedic.sidereal_positions(jd, a.ayanamsa)["Moon"]["lon"]
        lag = s["key"][0]
        rec = {"from_local": (naive + dt.timedelta(minutes=s["from"])).strftime("%H:%M"),
               "to_local": (naive + dt.timedelta(minutes=s["to"] + 1)).strftime("%H:%M"),
               "minutes_from_recorded": [s["from"], s["to"]],
               "lagna": common.fmt_pos(s["asc_from"]) + " to " + common.fmt_pos(s["asc_to"]),
               "lagna_sign": common.SIGNS[lag], **{f"D{n}_lagna": common.SIGNS[s["key"][i + 1]] for i, n in enumerate(VARGAS)},
               "moon_nakshatra": common.nak_info(moon)["name"], "events": []}
        for ev_dt, lab in events:
            cur_d = vedic.dashas(moon, utc_mid, ev_dt)["vimshottari"]["current"]
            md, ad = cur_d["mahadasha"]["lord"], cur_d["antardasha"]["lord"]
            rules = lambda pl: [((i - lag) % 12) + 1 for i in range(12) if vedic.SIGN_LORD[i] == pl]  # noqa: E731
            rec["events"].append({"event": lab, "date": ev_dt.date().isoformat(), "mahadasha": md, "antardasha": ad,
                                  "mahadasha_rules_houses": rules(md), "antardasha_rules_houses": rules(ad)})
        out["segments"].append(rec)
    if a.score and events:
        evl = calibration._parse_events(a.events)
        out["scored_segments"] = calibration.score_segments(base_jd, base_utc, naive, t["utc_offset_hours"], a.lat, a.lon,
                                                            out["segments"], evl, a.gender, a.ayanamsa)
        out["scoring_note"] = ("Lower chance probability = the segment explains the dated events better than chance. Fix the "
                               "D-9/D-10 segment first, then finer vargas (PVR 32.3); never present one time as certain.")
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"{len(out['segments'])} lagna segment(s) in the window; wrote {a.out}")
    for r in out.get("scored_segments", []):
        print(f"  score {r['from_local']}-{r['to_local']}: hits {r['hits']} vs {r['expected_by_chance']} by chance, p={r['chance_of_at_least_these_hits']}")
    for r in out["segments"]:
        print(f"  {r['from_local']}-{r['to_local']}  lagna {r['lagna_sign']}  " + "  ".join(f"D{n} {r[f'D{n}_lagna']}" for n in VARGAS))
        for e in r["events"]:
            print(f"      {e['date']} {e['event']}: {e['mahadasha']}-{e['antardasha']} (rules {e['mahadasha_rules_houses']}/{e['antardasha_rules_houses']})")


if __name__ == "__main__":
    main()
