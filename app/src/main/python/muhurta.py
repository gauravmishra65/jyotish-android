"""muhurta.py - electional search (Muhurta) for marriage, griha pravesh, vehicle purchase and business opening.

Scans a date range in fixed steps (default 10 minutes) and, for each moment, computes the panchang (tithi,
nakshatra, nitya yoga, karana, Vedic weekday), the sidereal Lagna and the Moon's sign. A moment is rejected if
any hard prohibition holds; otherwise it is scored on the event's preferences. Consecutive acceptable moments
with the same deciding factors are merged into windows.

Sources and conventions (stated in the output):
* Muhurta Chintamani (Vivaha and Griha prakaranas) as summarised by B.V. Raman, *Muhurtha*: the lagna is the most
  powerful corrective; combust Venus or Jupiter forbids a marriage outright.
* Common almanac lists are used for each event's nakshatras, tithis and weekdays. Almanacs differ in a few
  entries; the lists used are returned with the result so the reader can name them.
* Lahiri ayanamsa; the Vedic weekday runs sunrise to sunrise (centre of the disc, standard refraction).
* Rahu Kalam, Yamaganda and Gulika Kalam are the customary eighth-parts of daylight by weekday.
* Tarabala: count from the person's birth nakshatra to the day's; remainders 3, 5 and 7 (Vipat, Pratyari, Vadha) fail.
  Chandrabala: the transiting Moon in the 1st, 3rd, 6th, 7th, 10th or 11th from the birth Moon sign passes; in Shukla
  paksha the 2nd, 5th and 9th also pass (the waxing Moon's relaxation in the muhurta texts).
* Avoided weekdays (Tuesday and Saturday for marriage) are a penalty by default, because North Indian almanac
  lists use them freely; --weekday-rule hard rejects them outright for families who follow the stricter rule.
* Kharmas (Sun in sidereal Sagittarius or Pisces) is avoided for marriage and griha pravesh, as in North Indian
  practice. Chaturmas (lunar, Devshayani to Prabodhini Ekadashi) is NOT applied; mention it if the family follows it.
* Tithis in the event lists are counted within each paksha (1 to 15; 15 = Purnima). Rikta (4, 9, 14) and
  Amavasya are always rejected; the 8th and Purnima are rejected where the event list says so (B.V. Raman for marriage).
* Never promise an outcome. A good muhurta supports a beginning; it does not guarantee results.

Usage:
  python scripts/muhurta.py find --event marriage --from 2026-11-01 --to 2027-03-31 --lat 1.35 --lon 103.82 \
      [--tz Asia/Singapore] [--chart A.json --chart B.json] [--step 10] [--top 12] --out muhurta.json
"""
import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swisseph as swe  # noqa: E402
from common import SIGNS, NAKSHATRAS, NAK_SPAN, n360  # noqa: E402
import vedic  # noqa: E402
import upagraha  # noqa: E402

swe.set_ephe_path(os.path.join(HERE, "ephe"))
FL = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
WD = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
BAD_YOGAS = {"Vishkambha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vajra", "Vyatipata", "Parigha", "Vaidhriti"}
RIKTA = {4, 9, 14}
PANCHAKA_NAK = {"Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"}

EVENTS = {
    "marriage": {
        "label": "Marriage (vivaha)",
        "nakshatras": ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta", "Swati", "Anuradha", "Mula",
                       "Uttara Ashadha", "Uttara Bhadrapada", "Revati"],
        "weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "avoid_weekdays": ["Tuesday", "Saturday"],
        "tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "avoid_tithis": [8, 15],
        "lagnas_best": [2, 5, 6], "lagnas_avoid": [0, 7],
        "shukla_preferred": True, "kharmas": True, "panchaka": False,
        "combust_forbid": ["Venus", "Jupiter"],
        "empty_houses": [7, 8],
    },
    "griha_pravesh": {
        "label": "Entering a new home (griha pravesh)",
        "nakshatras": ["Rohini", "Mrigashira", "Uttara Phalguni", "Chitra", "Anuradha", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"],
        "weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "avoid_weekdays": ["Tuesday", "Sunday"],
        "tithis": [2, 3, 5, 7, 10, 11, 13],
        "avoid_tithis": [8, 15],
        "lagnas_best": [1, 4, 7, 10], "lagnas_avoid": [],
        "shukla_preferred": True, "kharmas": True, "panchaka": True,
        "combust_forbid": ["Jupiter"],
        "empty_houses": [8],
    },
    "vehicle": {
        "label": "Buying or taking delivery of a vehicle",
        "nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Chitra", "Swati", "Anuradha",
                       "Shravana", "Dhanishta", "Revati"],
        "weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "avoid_weekdays": ["Tuesday", "Saturday"],
        "tithis": [2, 3, 5, 6, 7, 10, 11, 12, 13],
        "avoid_tithis": [8],
        "lagnas_best": [0, 3, 6, 9, 2, 5, 8, 11], "lagnas_avoid": [],
        "shukla_preferred": False, "kharmas": False, "panchaka": False,
        "combust_forbid": [],
        "empty_houses": [8],
    },
    "business": {
        "label": "Opening a business or shop",
        "nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Uttara Phalguni", "Hasta", "Chitra",
                       "Anuradha", "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati"],
        "weekdays": ["Monday", "Wednesday", "Thursday", "Friday"],
        "avoid_weekdays": ["Tuesday"],
        "tithis": [2, 3, 5, 7, 10, 11, 13],
        "avoid_tithis": [8, 15],
        "lagnas_best": [1, 4, 7, 10, 2, 5, 8, 11], "lagnas_avoid": [],
        "shukla_preferred": True, "kharmas": False, "panchaka": False,
        "combust_forbid": [],
        "empty_houses": [8],
    },
}
BENEFICS = ("Jupiter", "Venus", "Mercury")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")


def _sid(jd):
    out = {}
    for name, pid in (("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS), ("Mercury", swe.MERCURY),
                      ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)):
        out[name] = n360(swe.calc_ut(jd, pid, FL)[0][0])
    out["Ketu"] = n360(out["Rahu"] + 180)
    return out


def _asc(jd, lat, lon):
    return n360(swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)[1][0])


def _combust(pos, p):
    orb = vedic.COMBUST_ORB.get(p)
    return orb is not None and abs((pos[p] - pos["Sun"] + 180) % 360 - 180) <= orb


def _person(path):
    return person_from_chart(json.load(open(path)))


def person_from_chart(c):
    """Tarabala and Chandrabala inputs from a chart dict (the output of chart_engine.build_chart)."""
    pl = c["vedic"]["planets"]["Moon"]
    return {"name": c["meta"].get("name"), "nak_i": NAKSHATRAS.index(pl["nakshatra"]), "moon_sign": pl["sign_index"]}


def find(event, start, end, lat, lon, tzname, people=(), step_min=10, top=12, weekday_rule="soft"):
    E = EVENTS[event]
    swe.set_sid_mode(vedic.AYAN["lahiri"])
    tz = ZoneInfo(tzname)
    day = dt.date.fromisoformat(start)
    last = dt.date.fromisoformat(end)
    if (last - day).days > 400:
        raise ValueError("search range is limited to about 13 months")
    slots, rejected = [], {}
    while day <= last:
        local_mid = dt.datetime(day.year, day.month, day.day, tzinfo=tz)
        jd_mid = swe.julday(*local_mid.astimezone(dt.timezone.utc).timetuple()[:3],
                            local_mid.astimezone(dt.timezone.utc).hour + local_mid.astimezone(dt.timezone.utc).minute / 60)
        off = local_mid.utcoffset().total_seconds() / 3600
        naive_noon = dt.datetime(day.year, day.month, day.day, 12, 0)
        up = upagraha.compute(jd_mid + 0.5, lat, lon, off, naive_noon, vedic.AYAN["lahiri"], 0, 0.0)
        vd = up.get("vedic_day")
        if not vd:
            day += dt.timedelta(days=1)
            continue
        sr_local = dt.datetime.fromisoformat(vd["sunrise_local"]).replace(tzinfo=tz)
        nsr_local = dt.datetime.fromisoformat(vd["next_sunrise_local"]).replace(tzinfo=tz)
        kalams = {k: (dt.datetime.fromisoformat(v["from"]).replace(tzinfo=tz), dt.datetime.fromisoformat(v["to"]).replace(tzinfo=tz))
                  for k, v in up["day_periods"].items() if k != "Abhijit muhurta"}
        ab = up["day_periods"]["Abhijit muhurta"]
        abhijit = (dt.datetime.fromisoformat(ab["from"]).replace(tzinfo=tz), dt.datetime.fromisoformat(ab["to"]).replace(tzinfo=tz))
        weekday = vd["weekday"]
        t = sr_local
        while t < nsr_local:
            tu = t.astimezone(dt.timezone.utc)
            jd = swe.julday(tu.year, tu.month, tu.day, tu.hour + tu.minute / 60 + tu.second / 3600)
            pos = _sid(jd)
            el = n360(pos["Moon"] - pos["Sun"])
            tithi = int(el // 12) + 1
            nak = NAKSHATRAS[int(pos["Moon"] // NAK_SPAN)]
            yoga = vedic.YOGA_NAMES[int(n360(pos["Sun"] + pos["Moon"]) // NAK_SPAN)]
            karana = vedic.karana_name(int(el // 6) + 1)
            lag = int(_asc(jd, lat, lon) // 30)
            moon_sign = int(pos["Moon"] // 30)
            sun_sign = int(pos["Sun"] // 30)
            why_not = []
            t15 = tithi if tithi <= 15 else tithi - 15          # tithi number within its paksha (15 = Purnima)
            if t15 in RIKTA:
                why_not.append("Rikta tithi")
            if tithi == 30:
                why_not.append("Amavasya")
            elif tithi == 15 and 15 in E["avoid_tithis"]:
                why_not.append("Purnima avoided for this event")
            elif t15 in E["avoid_tithis"] and t15 != 15:
                why_not.append(f"tithi {t15} avoided for this event")
            if karana.startswith("Vishti"):
                why_not.append("Vishti (Bhadra) karana")
            if yoga in BAD_YOGAS:
                why_not.append(f"{yoga} yoga")
            if weekday in E["avoid_weekdays"] and weekday_rule == "hard":
                why_not.append(f"{weekday} avoided for this event")
            if any(a <= t < b for a, b in kalams.values()):
                why_not.append(next(k for k, (a, b) in kalams.items() if a <= t < b))
            for p in E["combust_forbid"]:
                if _combust(pos, p):
                    why_not.append(f"{p} combust")
            if E["kharmas"] and sun_sign in (8, 11):
                why_not.append("Kharmas (Sun in Sagittarius or Pisces)")
            if E["panchaka"] and nak in PANCHAKA_NAK:
                why_not.append("Panchaka")
            if lag in E["lagnas_avoid"]:
                why_not.append(f"{SIGNS[lag]} lagna avoided for this event")
            if nak not in E["nakshatras"]:
                why_not.append("nakshatra not in the event's list")
            for pp in people:
                r = ((NAKSHATRAS.index(nak) - pp["nak_i"]) % 27 + 1) % 9
                if r in (3, 5, 7):
                    why_not.append(f"Tarabala fails for {pp['name']}")
                if (moon_sign - pp["moon_sign"]) % 12 + 1 not in ((1, 2, 3, 5, 6, 7, 9, 10, 11) if tithi <= 15 else (1, 3, 6, 7, 10, 11)):
                    why_not.append(f"Chandrabala fails for {pp['name']}")
            if why_not:
                for w in set(why_not):
                    rejected[w] = rejected.get(w, 0) + step_min
                t += dt.timedelta(minutes=step_min)
                continue
            # scoring
            score, good, weak = 0, [], []
            if t15 in E["tithis"]:
                score += 2
                good.append(f"tithi {t15} ({'Shukla' if tithi <= 15 else 'Krishna'})")
            if E["shukla_preferred"] and tithi > 15:
                score -= 1
                weak.append("Krishna paksha (Shukla preferred)")
            if weekday in E["weekdays"]:
                score += 1
                good.append(weekday)
            elif weekday in E["avoid_weekdays"]:
                score -= 2
                weak.append(f"{weekday} (traditionally avoided for this event)")
            if lag in E["lagnas_best"]:
                score += 3
                good.append(f"{SIGNS[lag]} lagna")
            houses = {p: (int(pos[p] // 30) - lag) % 12 + 1 for p in pos}
            ben_k = [p for p in BENEFICS if houses[p] in (1, 4, 5, 7, 9, 10)]
            if ben_k:
                score += len(ben_k)
                good.append("benefics in kendra or trine from the lagna: " + ", ".join(ben_k))
            occupied_bad = [h for h in E["empty_houses"] if any(houses[p] == h for p in pos)]
            if occupied_bad:
                score -= 2 * len(occupied_bad)
                weak.append("occupied: " + ", ".join(f"{h}th from the lagna" for h in occupied_bad))
            mal_l = [p for p in MALEFICS if houses[p] == 1]
            if mal_l:
                score -= 2
                weak.append("malefic in the lagna: " + ", ".join(mal_l))
            if houses["Moon"] in (6, 8, 12):
                score -= 2
                weak.append(f"Moon in the {houses['Moon']}th from the lagna")
            if abhijit[0] <= t < abhijit[1] and weekday != "Wednesday":
                score += 1
                good.append("Abhijit muhurta")
            slots.append({"t": t, "score": score, "good": good, "weak": weak, "tithi": tithi, "nakshatra": nak, "yoga": yoga,
                          "karana": karana, "lagna": SIGNS[lag], "weekday": weekday, "moon_sign": SIGNS[moon_sign]})
            t += dt.timedelta(minutes=step_min)
        day += dt.timedelta(days=1)
    # merge consecutive slots with the same lagna, nakshatra, tithi and Vedic weekday (a window never spans sunrise)
    windows = []
    for s in slots:
        w = windows[-1] if windows else None
        if w and (s["t"] - w["_end"]) <= dt.timedelta(minutes=step_min) and all(s[k] == w[k] for k in ("lagna", "nakshatra", "tithi", "weekday")):
            w["_end"] = s["t"]
            w["score"] = max(w["score"], s["score"])
            for k in ("good", "weak"):
                for x in s[k]:
                    if x not in w[k]:
                        w[k].append(x)
        else:
            windows.append({**s, "_start": s["t"], "_end": s["t"], "good": list(s["good"]), "weak": list(s["weak"])})
    out_w = []
    for w in windows:
        w_end = w["_end"] + dt.timedelta(minutes=step_min)
        mins = int((w_end - w["_start"]).total_seconds() // 60)
        if mins < 20:
            continue
        out_w.append({"date": w["_start"].date().isoformat(), "start_local": w["_start"].strftime("%Y-%m-%d %H:%M"),
                      "end_local": w_end.strftime("%Y-%m-%d %H:%M"), "minutes": mins, "score": w["score"], "weekday": w["weekday"],
                      "tithi": w["tithi"], "paksha": "Shukla" if w["tithi"] <= 15 else "Krishna", "nakshatra": w["nakshatra"],
                      "yoga": w["yoga"], "karana": w["karana"], "lagna": w["lagna"], "moon_sign": w["moon_sign"],
                      "supports": w["good"], "weaknesses": w["weak"]})
    best = sorted(out_w, key=lambda w: (-w["score"], w["start_local"]))[:top]
    return {"event": event, "event_label": E["label"], "range": [start, end], "place": {"lat": lat, "lon": lon, "tz": tzname},
            "people": [p["name"] for p in people], "step_minutes": step_min,
            "windows_found": len(out_w), "best_windows": sorted(best, key=lambda w: w["start_local"]),
            "all_windows": out_w, "time_rejected_minutes_by_reason": dict(sorted(rejected.items(), key=lambda kv: -kv[1])),
            "rules_used": {k: v for k, v in E.items() if k != "label"} | {"forbidden_nitya_yogas": sorted(BAD_YOGAS), "rikta_tithis": sorted(RIKTA),
                                                                         "weekday_rule": weekday_rule},
            "conventions": " ".join(__doc__.split("Sources and conventions (stated in the output):")[1].split("Usage:")[0].split()),
            "disclaimer": "Traditional electional guidance. It supports a beginning; it does not guarantee any outcome."}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("--event", required=True, choices=list(EVENTS))
    f.add_argument("--from", dest="start", required=True)
    f.add_argument("--to", dest="end", required=True)
    f.add_argument("--lat", type=float, required=True)
    f.add_argument("--lon", type=float, required=True)
    f.add_argument("--tz", default=None)
    f.add_argument("--weekday-rule", default="soft", choices=["soft", "hard"], help="hard: reject the event's avoided weekdays outright")
    f.add_argument("--chart", action="append", default=[], help="chart.json of a person (for Tarabala and Chandrabala); repeat for two")
    f.add_argument("--step", type=int, default=10)
    f.add_argument("--top", type=int, default=12)
    f.add_argument("--out", default="muhurta.json")
    a = ap.parse_args()
    tzname = a.tz
    if not tzname:
        from timezonefinder import TimezoneFinder
        tzname = TimezoneFinder().timezone_at(lat=a.lat, lng=a.lon)
    res = find(a.event, a.start, a.end, a.lat, a.lon, tzname, [_person(p) for p in a.chart], a.step, a.top, a.weekday_rule)
    json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {a.out}: {res['windows_found']} windows, best {len(res['best_windows'])}")


if __name__ == "__main__":
    main()
