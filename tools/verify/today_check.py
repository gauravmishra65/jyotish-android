"""Checks the Today dashboard engine (app_today.py) against dates and times published by almanacs.

Festival dates for 2026 (New Delhi) as Drik Panchang and other almanacs print them; panchang end times and
day periods for New Delhi on 18 November 2026 and the day Choghadiya for 10 November 2026 from published
almanac pages. Times may differ by a minute because of rounding; the check allows 2 minutes.
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = os.path.join(ROOT, "app", "src", "main", "python")
sys.path.insert(0, PY)
import swisseph as swe  # noqa: E402
swe.set_ephe_path(os.path.join(PY, "ephe"))
import app_today  # noqa: E402

DELHI = dict(lat=28.6139, lon=77.2090, tz="Asia/Kolkata")
problems = []


def mins(hm):
    h, m = hm[:5].split(":")
    return int(h) * 60 + int(m)


def near(label, got, want, tol=2):
    if got is None or abs(mins(got) - mins(want)) > tol:
        problems.append(f"{label}: got {got}, expected {want}")


FESTIVALS_2026 = {
    "makar_sankranti": "2026-01-15", "vasant_panchami": "2026-01-23", "maha_shivaratri": "2026-02-15",
    "chaitra_navratri": "2026-03-19", "ram_navami": "2026-03-26", "hanuman_jayanti": "2026-04-02",
    "guru_purnima": "2026-07-29", "raksha_bandhan": "2026-08-28", "janmashtami": "2026-09-04",
    "ganesh_chaturthi": "2026-09-14", "navratri": "2026-10-11", "dussehra": "2026-10-20", "karva_chauth": "2026-10-29",
    "dhanteras": "2026-11-06", "diwali": "2026-11-08", "govardhan": "2026-11-10", "bhai_dooj": "2026-11-11",
    "chhath": "2026-11-15", "dev_uthani": "2026-11-20",
}
fest = app_today.festivals(dt.date(2026, 1, 1), 364, DELHI["lat"], DELHI["lon"], ZoneInfo(DELHI["tz"]))
by_key = {}
for f in fest:
    k = "makar_sankranti" if f["key"] == "sankranti" and f["name"]["en"] == "Makar Sankranti" else f["key"]
    by_key.setdefault(k, f["date"])
for k, want in FESTIVALS_2026.items():
    if by_key.get(k) != want:
        problems.append(f"festival {k}: got {by_key.get(k)}, expected {want}")

o = json.loads(app_today.today(json.dumps(dict(date="2026-11-18", festival_days=1, **DELHI))))
p, pr = o["panchang"], o["periods"]
near("sunrise 18 Nov", o["sun"]["rise"], "06:46")
near("sunset 18 Nov", o["sun"]["set"], "17:26")
near("tithi end", p["tithi"]["ends"], "07:07")
near("nakshatra end", p["nakshatra"]["ends"], "06:10")
near("yoga end", p["yoga"]["ends"], "08:05")
for k, (a, b) in {"rahu_kalam": ("12:06", "13:26"), "yamaganda": ("08:06", "09:26"), "gulika_kalam": ("10:46", "12:06"),
                  "abhijit": ("11:45", "12:28"), "brahma_muhurta": ("05:10", "05:58")}.items():
    near(k + " from", pr[k]["from"], a)
    near(k + " to", pr[k]["to"], b)
if p["tithi"]["name"]["en"] != "Navami" or p["nakshatra"]["name"]["en"] != "Shatabhisha" or p["yoga"]["name"]["en"] != "Dhruva":
    problems.append("panchang names for 18 Nov 2026 do not match")

o = json.loads(app_today.today(json.dumps(dict(date="2026-11-10", festival_days=1, **DELHI))))
want = [("Rog", "06:39"), ("Udveg", "08:01"), ("Chal", "09:22"), ("Labh", "10:44"), ("Amrit", "12:05"), ("Kaal", "13:27"),
        ("Shubh", "14:48"), ("Rog", "16:10")]
for c, (name, t) in zip(o["periods"]["choghadiya_day"], want):
    if c["name"]["en"] != name:
        problems.append(f"choghadiya {t}: got {c['name']['en']}, expected {name}")
    near(f"choghadiya {name}", c["from"], t)

if json.loads(app_today.today(json.dumps(dict(date="2026-06-01", festival_days=1, **DELHI))))["panchang"]["month_amanta"]["en"] != "Adhika Jyeshtha":
    problems.append("1 June 2026 should be in Adhika Jyeshtha")

print("\n".join(problems) if problems else "today: all checks passed")
sys.exit(1 if problems else 0)
