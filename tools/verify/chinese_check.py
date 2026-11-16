"""Chinese calendar, Zi Wei Dou Shu and Nine Star Ki checks (v17).

* Chinese New Year and leap months against the Hong Kong Observatory's published calendar.
* Zi Wei: every main star placed once; the Zi Wei position table for the five bureaus (day 1-6) against the classical
  table; the 'Zi Wei in Wu' pattern (Lian Zhen and Tian Fu together in Xu, Wu Qu and Tian Xiang in Yin).
* Nine Star Ki year stars (1965 -> 8, 2024 -> 3, 2025 -> 2, 2026 -> 1) and the month sequence.
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main", "python"))
import chinese_calendar as C
import chinese_more as M
import ziwei as Z

problems = []
NY = {1965: "1965-02-02", 1988: "1988-02-17", 1991: "1991-02-15", 2000: "2000-02-05", 2012: "2012-01-23", 2017: "2017-01-28",
      2020: "2020-01-25", 2023: "2023-01-22", 2024: "2024-02-10", 2025: "2025-01-29", 2026: "2026-02-17", 2027: "2027-02-06", 2033: "2033-01-31"}
for y, v in NY.items():
    if C.new_year(y).isoformat() != v:
        problems.append(f"New Year {y}: {C.new_year(y)} != {v}")
LEAP = {2012: 4, 2014: 9, 2017: 6, 2020: 4, 2023: 2, 2025: 6, 2028: 5, 1987: 6}
for y, m in LEAP.items():
    got = [n for _, n, lp in C.sui(y - 1)[0] + C.sui(y)[0] if lp]
    if got != [m]:
        problems.append(f"leap month {y}: {got} != {m}")
if C.to_lunar(dt.date(2000, 8, 16))["zh"] != "庚辰年 七月 十七":
    problems.append("2000-08-16 lunar date")
# Zi Wei position table, days 1-6 (Water 2, Wood 3, Metal 4, Earth 5, Fire 6), branch indices
TABLE = {2: [1, 2, 2, 3, 3, 4], 3: [4, 1, 2, 5, 2, 3], 4: [11, 4, 1, 2, 0, 5], 5: [6, 11, 4, 1, 2, 7], 6: [9, 6, 11, 4, 1, 2]}
for b, row in TABLE.items():
    got = [Z.ziwei_position(b, d) for d in range(1, 7)]
    if got != row:
        problems.append(f"Zi Wei table bureau {b}: {got} != {row}")
for date, time, g in (("1988-07-14", "14:35", "M"), ("1991-03-02", "09:10", "F"), ("1979-11-23", "23:50", "F"), ("2000-08-16", "04:00", "F")):
    c = Z.chart(date, time, g)
    names = [s["zh"] for p in c["palaces"] for s in p["major"]]
    if sorted(names) != sorted(Z.MAJOR):
        problems.append(f"{date}: main stars {names}")
    if len({p["branch"] for p in c["palaces"]}) != 12:
        problems.append(f"{date}: palaces do not cover the twelve branches")
c = Z.chart("2000-08-16", "04:00", "F")
by = {p["branch"]: [s["zh"] for s in p["major"]] for p in c["palaces"]}
if by[6] != ["紫微"] or sorted(by[10]) != sorted(["廉贞", "天府"]) or sorted(by[2]) != sorted(["武曲", "天相"]):
    problems.append(f"Zi Wei in Wu pattern: {by}")
for y, s in ((1965, 8), (2024, 3), (2025, 2), (2026, 1)):
    if M.nine_star_year(y) != s:
        problems.append(f"Nine Star Ki {y}")
months = [M.nine_star(dt.date(1965, m, 20), 5.5)["month_star"] for m in range(3, 13)]
if months != [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
    problems.append(f"Nine Star Ki months 1965: {months}")
# Flying Stars: 2026 annual chart (5 Yellow in the South, 2 Black in the North-west); Period 8 facing Wu (子山午向) has
# 4-3 in the centre and the double 8 at the facing side (双星会向)
import fengshui as F
y26 = F.year_month(dt.date(2026, 6, 1))["year"]
if y26["S"] != 5 or y26["NW"] != 2 or y26["C"] != 1:
    problems.append(f"2026 flying stars: {y26}")
h = F.house_chart(180, 2010)
if (h["mountain"]["C"], h["water"]["C"]) != (4, 3) or (h["mountain"]["S"], h["water"]["S"]) != (8, 8):
    problems.append(f"Period 8 facing Wu: centre {h['mountain']['C']}-{h['water']['C']}, south {h['mountain']['S']}-{h['water']['S']}")
if F.period_of(2010) != 8 or F.period_of(2030) != 9:
    problems.append("periods")
# BaZi depth: growth phases (壬 born in 申, peaks in 子; 乙 born in 午, runs backward), Na Yin, Nobleman by Day Master
import chinese_depth as D
if D.phase(8, 8)[0] != "长生" or D.phase(8, 0)[0] != "帝旺" or D.phase(1, 6)[0] != "长生" or D.phase(1, 3)[0] != "临官" or D.phase(0, 7)[0] != "墓":
    problems.append("growth phases")
if D.NAYIN[D._idx(0, 0) // 2] != "海中金" or D.NAYIN[D._idx(9, 11) // 2] != "大海水" or D.NAYIN[D._idx(2, 6) // 2] != "天河水":
    problems.append("na yin")
if set(D.NOBLE[0]) != {1, 7} or set(D.NOBLE[7]) != {6, 2} or set(D.NOBLE[9]) != {3, 5}:
    problems.append("nobleman")
# Maya calendar (GMT 584283): 21 Dec 2012 = 13.0.0.0.0 4 Ajaw 3 K'ank'in G9; 1 Jan 2000 = 12.19.6.15.2 11 Ik' 10 K'ank'in
import maya as MY
for d, want in ((dt.date(2012, 12, 21), ("13.0.0.0.0", 4, 19, 3, 13)), (dt.date(2000, 1, 1), ("12.19.6.15.2", 11, 1, 10, 13))):
    m = MY.maya(d)
    if (m["long_count"], m["tz_num"], m["tz_sign"], m["haab_day"], m["haab_month"]) != want:
        problems.append(f"maya {d}: {m}")
# v22 fills: month stems (five tigers), hour stems (five rats), 24 solar terms inside the year, syzygy and age
import fill_partials as FP
import engine_api as EA
_c = EA.chart_obj({"name": "Ravi Shankar Tiwari", "date": "1985-03-14", "time": "06:45", "lat": 25.32, "lon": 82.97, "tz": "Asia/Kolkata", "gender": "M", "now": "2026-11-16"})
_m = FP.bazi_cycles(_c["bazi"], _c)["blocks"][0]["rows"]
if [_m[0][1]["en"], _m[11][1]["en"]] != ["庚寅", "辛丑"]:
    problems.append(f"2026 month pillars: {_m[0][1]['en']} {_m[11][1]['en']}")
_h = FP.bazi_hours(_c["bazi"])["blocks"][0]["rows"]
if _h[0][1]["en"] != "庚子" or _h[3][1]["en"] != _c["bazi"]["pillars"]["hour"]["text"]:
    problems.append("hour pillar options do not contain the chart's own hour pillar")
_t = FP.chinese_sections("1985-03-14", "2026-11-16", 8.0)
_rows = _t[0]["blocks"][0]["rows"]
if len(_rows) != 24 or not all(r[2]["en"].endswith("2026") for r in _rows) or _rows[2][2]["en"] != "04 Feb 2026" or _rows[23][2]["en"] != "22 Dec 2026":
    problems.append("solar terms 2026")
if [r[1]["en"] for r in _t[2]["blocks"][0]["rows"]] != ["41", "42"]:
    problems.append("age conventions")
_l = FP.lunations(_c)["blocks"][0]["rows"]
if _l[1][1]["en"] != "24 Nov 2026" or _l[5][1]["en"] != "06 Feb 2027":
    problems.append(f"lunations: {_l[1][1]['en']} {_l[5][1]['en']}")
# v25 input options: Julian calendar conversion, the ambiguous-hour choice, house systems and orb scale
import common as _CM
_j = _CM.resolve_time("1582-10-05", "09:30", 25.32, 82.97, "Asia/Kolkata", calendar="julian")
if _j["local_civil"][:10] != "1582-10-15" or _j["julian_date"] != "1582-10-05 (Julian calendar)":
    problems.append(f"julian calendar: {_j['local_civil']}")
_a = _CM.resolve_time("2020-11-01", "01:30", 40.7, -74.0, "America/New_York", fold=0)["utc"]
_b = _CM.resolve_time("2020-11-01", "01:30", 40.7, -74.0, "America/New_York", fold=1)["utc"]
if (_a[11:16], _b[11:16]) != ("05:30", "06:30"):
    problems.append(f"ambiguous hour: {_a} {_b}")
_p = EA.chart_obj({"name": "R", "date": "1985-03-14", "time": "06:45", "lat": 25.32, "lon": 82.97, "tz": "Asia/Kolkata", "gender": "M"})
_k = EA.chart_obj({"name": "R", "date": "1985-03-14", "time": "06:45", "lat": 25.32, "lon": 82.97, "tz": "Asia/Kolkata", "gender": "M",
                   "house_system": "koch", "orb_scale": 0.5})
if _p["western"]["house_system"] != "Placidus" or _k["western"]["house_system"] != "Koch":
    problems.append("house systems")
if len(_k["western"]["natal_aspects"]) >= len(_p["western"]["natal_aspects"]):
    problems.append("orb scale does not tighten the aspect list")
# v26 astronomy: the compass direction of the Sun at sunrise, topocentric vs geocentric Moon, and the Uranian points
import western_adv as _WA
_sky = _WA.sky_view(_p)["blocks"][0]["rows"]
if _sky[0][3]["en"] != "E" or float(_sky[0][1]["en"].rstrip("\u00b0")) <= 0:
    problems.append(f"sky at birth: Sun {_sky[0][1]['en']} {_sky[0][3]['en']} (born just after sunrise, so the Sun must be low in the east)")
if _sky[1][3]["en"] != "S":
    problems.append(f"sky at birth: Moon {_sky[1][3]['en']}")
_pe = _WA.perspectives(_p)["blocks"][0]["rows"]
if float(_pe[1][3]["en"].rstrip("'")) < 1.0 or float(_pe[0][3]["en"].rstrip("'")) > 0.5:
    problems.append("topocentric shift: the Moon should move by minutes and the Sun barely at all")
if len(_WA.hypothetical(_p)["blocks"][1]["rows"]) != 8:
    problems.append("uranian points")
# v26 group comparison: two people side by side, every row filled
import group_compare as _GC
import json as _json
_g = _json.loads(_GC.compare(_json.dumps({"people": [
    {"name": "Ravi Shankar Tiwari", "date": "1985-03-14", "time": "06:45", "lat": 25.32, "lon": 82.97, "tz": "Asia/Kolkata", "gender": "M", "now": "2026-11-16"},
    {"name": "Neha Agarwal", "date": "1988-11-02", "time": "14:20", "lat": 28.61, "lon": 77.21, "tz": "Asia/Kolkata", "gender": "F", "now": "2026-11-16"}]})))
_rows = _g["sections"][0]["blocks"][0]["rows"]
if len(_rows) != 12 or any(cell["en"] in ("", "-", "\u2013") for r in _rows for cell in r[1:]):
    problems.append("group comparison has empty cells: " + str([r[0]["en"] for r in _rows if any(c["en"] == "\u2013" for c in r[1:])]))
# v27 judgement layer and regional almanacs, checked against known values
import chinese_schools as _CSch
import regional as _RG
_st = _CSch.structure(_p["bazi"])["blocks"][0]["rows"]
if "\u4f24\u5b98" not in _st[3][1]["en"]:
    problems.append(f"bazi structure: {_st[3][1]['en']}")
_uf = _CSch.useful_elements(_p["bazi"])["blocks"][0]["rows"]
if [r[2]["en"] for r in _uf][:2] != ["favourable", "favourable"]:
    problems.append("useful elements for a weak Water Day Master should be Metal and Water")
for _d, _want in (("1985-03-14", ["Raktakshi (1984\u201385)", "Maasi", "ME 1160", "Kumbham", "BS 1391", "Falgun", "BS 2041"]),
                  ("2024-08-20", ["Krodhi (2024\u201325)", "Aavani", "ME 1200", "Chingam", "BS 1431", "Bhadro", "BS 2081"]),
                  ("2026-11-16", ["Parabhava (2026\u201327)", "Aippasi", "ME 1202", "Thulam", "BS 1433", "Kartik", "BS 2083"])):
    _c = EA.chart_obj({"name": "X", "date": _d, "time": "06:45", "lat": 25.32, "lon": 82.97, "tz": "Asia/Kolkata", "gender": "M"})
    _got = [r[1]["en"] for r in _RG.eras(_c)["blocks"][0]["rows"]]
    if _got != _want:
        problems.append(f"regional eras {_d}: {_got}")
if _RG.katapayadi("\u0930\u0935\u093f")["total"] != 6:
    problems.append("katapayadi")
for p in problems:
    print("ISSUE", p)
print(f"chinese checks: {len(problems)} problems")
sys.exit(1 if problems else 0)
