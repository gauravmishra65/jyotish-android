"""chinese_calendar.py - Gregorian to Chinese lunisolar date (v17), from the Swiss Ephemeris.

Rules (the modern calendar, as published by the Purple Mountain Observatory and the Hong Kong Observatory):
* Days run midnight to midnight in China Standard Time (UTC+8); a month begins on the day of the new moon.
* Month 11 is the month that contains the winter solstice. A sui (solstice to solstice) with 13 months has one leap
  month: the first month in it that contains no principal solar term (zhongqi, a multiple of 30 degrees of the Sun's
  tropical longitude). It takes the number of the month before it.
* The year number (and its stem and branch) changes on the first day of month 1, Chinese New Year. BaZi uses the
  solar term Li Chun instead; the two are shown side by side by the screen, never mixed.

Verified against the Hong Kong Observatory tables (tools/verify/chinese_check.py): New Year dates and leap months.
"""
import datetime as dt
from functools import lru_cache

import swisseph as swe

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEMS_PY = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCHES_PY = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
ANIMALS_HI = ["चूहा", "बैल", "बाघ", "खरगोश", "ड्रैगन", "साँप", "घोड़ा", "बकरी", "बंदर", "मुर्गा", "कुत्ता", "सूअर"]
MONTH_ZH = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
DAY_ZH = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十", "十一", "十二", "十三", "十四", "十五",
          "十六", "十七", "十八", "十九", "二十", "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
TZ = 8 / 24


def bj_date(jd_ut):
    y, m, d, h = swe.revjul(jd_ut + TZ)
    return dt.date(y, m, d)


def _elong(jd):
    s = swe.calc_ut(jd, swe.SUN)[0][0]
    m = swe.calc_ut(jd, swe.MOON)[0][0]
    return (m - s + 180) % 360 - 180


def new_moons(jd0, jd1):
    """UT Julian days of the new moons in [jd0, jd1]."""
    out, j, prev = [], jd0, _elong(jd0)
    while j < jd1:
        j2 = j + 1.0
        cur = _elong(j2)
        if prev < 0 <= cur:
            a, b = j, j2
            for _ in range(40):
                mid = (a + b) / 2
                if _elong(mid) < 0:
                    a = mid
                else:
                    b = mid
            out.append((a + b) / 2)
        j, prev = j2, cur
    return out


def sun_cross(lon, jd_from):
    """UT Julian day when the Sun's tropical longitude next reaches lon (degrees) after jd_from."""
    return swe.solcross_ut(lon, jd_from, swe.FLG_SWIEPH)


@lru_cache(maxsize=256)
def winter_solstice_date(year):
    return bj_date(sun_cross(270.0, swe.julday(year, 12, 1, 0.0)))


@lru_cache(maxsize=256)
def _month11_start(year):
    """Date (CST) of the new moon that begins the month containing the winter solstice of this Gregorian year."""
    ws = winter_solstice_date(year)
    jws = swe.julday(ws.year, ws.month, ws.day, 0.0)
    nms = new_moons(jws - 32, jws + 2)
    best = None
    for n in nms:
        d = bj_date(n)
        if d <= ws:
            best = d
    return best


@lru_cache(maxsize=256)
def sui(year):
    """Months of the sui from month 11 of `year` to month 11 of `year`+1: [(start_date, number, leap)]."""
    a, b = _month11_start(year), _month11_start(year + 1)
    ja = swe.julday(a.year, a.month, a.day, 0.0)
    jb = swe.julday(b.year, b.month, b.day, 0.0)
    starts = sorted({bj_date(n) for n in new_moons(ja - 2, jb + 2) if a <= bj_date(n) < b})
    zq = []                        # principal-term dates in the sui
    j = ja - 1
    while True:
        lon_now = swe.calc_ut(j, swe.SUN)[0][0]
        target = (int(lon_now // 30) + 1) * 30 % 360
        j = sun_cross(target, j)
        d = bj_date(j)
        if d >= b:
            break
        zq.append(d)
        j += 1
    leap_needed = len(starts) == 13
    months, num, leap_used = [], 11, False
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else b
        has_zq = any(s <= z < e for z in zq)
        if i == 0:
            months.append((s, 11, False))
            continue
        if leap_needed and not leap_used and not has_zq:
            months.append((s, num, True))
            leap_used = True
            continue
        num = num % 12 + 1
        months.append((s, num, False))
    return months, b


def to_lunar(d):
    """Gregorian date -> {year, month, day, leap, stem_branch, animal, zh} (year = the year that began at New Year)."""
    s = d.year if d >= _month11_start(d.year) else d.year - 1
    months, end = sui(s)
    idx = max(i for i, (st, _, _) in enumerate(months) if st <= d)
    start, num, leap = months[idx]
    day = (d - start).days + 1
    passed_new_year = any(n == 1 and not lp for (st, n, lp) in months[:idx + 1])
    year = s + 1 if passed_new_year else s
    i60 = (year - 4) % 60
    nxt = months[idx + 1][0] if idx + 1 < len(months) else end
    return {"year": year, "month": num, "day": day, "leap": leap, "month_days": (nxt - start).days,
            "stem_branch": STEMS[i60 % 10] + BRANCHES[i60 % 12], "pinyin": f"{STEMS_PY[i60 % 10]}-{BRANCHES_PY[i60 % 12]}",
            "stem_index": i60 % 10, "branch_index": i60 % 12, "animal": ANIMALS[i60 % 12], "animal_hi": ANIMALS_HI[i60 % 12],
            "zh": f"{STEMS[i60 % 10]}{BRANCHES[i60 % 12]}年 {'闰' if leap else ''}{MONTH_ZH[num - 1]}月 {DAY_ZH[day - 1]}"}


def new_year(year):
    """Gregorian date of Chinese New Year (month 1, day 1) of this Gregorian year."""
    months, _ = sui(year - 1)
    return next(st for st, n, lp in months if n == 1 and not lp)
