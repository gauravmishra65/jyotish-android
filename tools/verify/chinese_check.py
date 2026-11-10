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
for p in problems:
    print("ISSUE", p)
print(f"chinese checks: {len(problems)} problems")
sys.exit(1 if problems else 0)
