"""upagraha.py - Gulika, Mandi and the other time-based upagrahas, the Dhuma group, and the
day periods of the Vedic day of birth (Rahu Kalam, Yamaganda, Gulika Kalam, Abhijit muhurta).

Conventions (stated in the output):
* Sunrise and sunset: centre of the Sun's disc with standard refraction, the same rule as the panchang.
* The Vedic day runs sunrise to sunrise. Day (sunrise to sunset) and night (sunset to next sunrise) are each
  cut into eight equal parts. Day parts are ruled in weekday order starting from the weekday lord; night parts
  start from the lord of the fifth weekday counted from it. The eighth part has no lord.
* Gulika = sidereal ascendant at the START of Saturn's part; Mandi = ascendant at the MIDDLE of Saturn's part.
  This follows Jagannatha Hora's defaults. Some texts reverse the two (BPHS as read by some translators gives
  Mandi at the start); both moments are reported so the reader can name the one used.
* Kaala (Sun), Mrityu (Mars), Artha Prahara (Mercury) and Yama Ghantaka (Jupiter) rise at the middle of their
  planet's part (P.V.R. Narasimha Rao).
* Dhuma group (BPHS ch. 3): Dhuma = Sun + 133d20m; Vyatipata = 360 - Dhuma; Parivesha = Vyatipata + 180;
  Indrachapa = 360 - Parivesha; Upaketu = Indrachapa + 16d40m (= Sun - 30).
* Rahu Kalam, Yamaganda and Gulika Kalam are the customary eighth-parts of the day by weekday; Abhijit is the
  8th of 15 day muhurtas (traditionally not used on Wednesdays).
"""
import datetime as dt
import swisseph as swe
from common import SIGNS, n360, fmt_pos, nak_info, jd_to_dt, dt_to_jd, sign_of

PART_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]          # weekday order
PY_WD_LORD = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]          # python weekday 0=Mon
WD_NAME = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# eighth-part of the day (1-8) by python weekday (0=Mon .. 6=Sun)
RAHU_KALAM = [2, 7, 5, 6, 4, 3, 8]
YAMAGANDA = [4, 3, 2, 1, 7, 6, 5]
GULIKA_KALAM = [6, 5, 4, 3, 2, 1, 7]
_FLAGS = swe.CALC_RISE | swe.BIT_DISC_CENTER


def _event(jd_start, lat, lon, rise=True):
    fl = (swe.CALC_RISE if rise else swe.CALC_SET) | swe.BIT_DISC_CENTER
    r = swe.rise_trans(jd_start, swe.SUN, fl, (lon, lat, 0.0), 1013.25, 15.0)
    if r[0] < 0 or r[1][0] <= 1:
        return None
    return r[1][0]


def _asc(jd, lat, lon, ayan_mode):
    swe.set_sid_mode(ayan_mode)
    _, ascmc = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
    return n360(ascmc[0])


def _point(l, lag_sign):
    s = sign_of(l)
    ni = nak_info(l)
    return {"lon": round(l, 4), "position": fmt_pos(l), "sign": SIGNS[s], "house": (s - lag_sign) % 12 + 1,
            "nakshatra": ni["name"], "pada": ni["pada"]}


def compute(jd_birth, lat, lon, utc_offset_h, birth_local_naive, ayan_mode, lag_sign, sun_lon):
    loc = lambda jd: (jd_to_dt(jd) + dt.timedelta(hours=utc_offset_h))  # noqa: E731
    fmt = lambda jd: loc(jd).strftime("%Y-%m-%d %H:%M:%S")  # noqa: E731
    local_mid = dt.datetime(birth_local_naive.year, birth_local_naive.month, birth_local_naive.day)
    jd_mid = dt_to_jd(local_mid - dt.timedelta(hours=utc_offset_h))
    sr = _event(jd_mid - 0.02, lat, lon, True)
    out = {"conventions": __doc__.split("Conventions (stated in the output):")[1].strip()}
    # Dhuma group needs no sunrise
    dh = n360(sun_lon + 133 + 20 / 60)
    vy = n360(360 - dh)
    pv = n360(vy + 180)
    ic = n360(360 - pv)
    uk = n360(ic + 16 + 40 / 60)
    out["dhuma_group"] = {n: _point(v, lag_sign) for n, v in
                          (("Dhuma", dh), ("Vyatipata", vy), ("Parivesha", pv), ("Indrachapa", ic), ("Upaketu", uk))}
    if sr is None:
        out["status"] = "no sunrise on this date at this latitude; time-based upagrahas and day periods not computed"
        return out
    if jd_birth < sr:                                   # born before sunrise: Vedic day began the previous morning
        sr = _event(jd_mid - 1.02, lat, lon, True)
        vd_date = local_mid - dt.timedelta(days=1)
    else:
        vd_date = local_mid
    ss = _event(sr + 0.001, lat, lon, False)
    sr2 = _event(ss + 0.001, lat, lon, True) if ss else None
    if ss is None or sr2 is None:
        out["status"] = "sunset or next sunrise not found (polar latitude); time-based upagrahas not computed"
        return out
    wd = vd_date.weekday()
    wl = PY_WD_LORD[wd]
    day = jd_birth < ss
    start, end = (sr, ss) if day else (ss, sr2)
    part = (end - start) / 8
    first = PART_ORDER.index(wl) if day else (PART_ORDER.index(wl) + 4) % 7
    lords = [PART_ORDER[(first + i) % 7] for i in range(7)] + [None]
    parts = [{"part": i + 1, "lord": lords[i], "from": fmt(start + i * part), "to": fmt(start + (i + 1) * part)} for i in range(8)]

    def at(planet, where):
        i = lords.index(planet)
        return start + (i + (0.5 if where == "middle" else 0.0)) * part

    tb = {}
    for name, planet, where in (("Gulika", "Saturn", "start"), ("Mandi", "Saturn", "middle"), ("Kaala", "Sun", "middle"),
                                ("Mrityu", "Mars", "middle"), ("Artha Prahara", "Mercury", "middle"),
                                ("Yama Ghantaka", "Jupiter", "middle")):
        jd = at(planet, where)
        tb[name] = {**_point(_asc(jd, lat, lon, ayan_mode), lag_sign), "rises_at_local": fmt(jd),
                    "rule": f"ascendant at the {where} of {planet}'s {'day' if day else 'night'} part"}
    out["time_based"] = tb
    out["born_in"] = "day" if day else "night"
    out["vedic_day"] = {"weekday": WD_NAME[wd], "weekday_lord": wl, "sunrise_local": fmt(sr), "sunset_local": fmt(ss),
                        "next_sunrise_local": fmt(sr2), "parts_used": parts,
                        "birth_part": int((jd_birth - start) // part) + 1}
    # day periods of that Vedic day
    dl = (ss - sr) / 8

    def span(k):
        return {"from": fmt(sr + (k - 1) * dl), "to": fmt(sr + k * dl), "_a": sr + (k - 1) * dl, "_b": sr + k * dl}
    periods = {"Rahu Kalam": span(RAHU_KALAM[wd]), "Yamaganda": span(YAMAGANDA[wd]), "Gulika Kalam": span(GULIKA_KALAM[wd])}
    m = (ss - sr) / 15
    periods["Abhijit muhurta"] = {"from": fmt(sr + 7 * m), "to": fmt(sr + 8 * m), "_a": sr + 7 * m, "_b": sr + 8 * m,
                                  "note": "traditionally not used on Wednesdays" if wd == 2 else None}
    for v in periods.values():
        v["birth_inside"] = v.pop("_a") <= jd_birth < v.pop("_b")
    out["day_periods"] = periods
    out["birth_in_period"] = [k for k, v in periods.items() if v["birth_inside"]]
    out["status"] = "ok"
    return out
