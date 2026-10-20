"""common.py - shared constants and the birth-time pipeline.

Everything here is deterministic. No interpretation lives in this package:
the model reads the JSON these modules emit and does the interpreting.
"""
import datetime as dt
from zoneinfo import ZoneInfo
import swisseph as swe

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]  # Parashari lords
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
              "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
              "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
              "Uttara Bhadrapada", "Revati"]
NAK_SPAN = 360.0 / 27.0
VIM_ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
             ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
WEEKDAY_LORD = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]  # Mon..Sun


def n360(x):
    return x % 360.0


def sign_of(lon):
    return int(n360(lon) // 30)


def deg_in_sign(lon):
    return n360(lon) % 30.0


def wrap180(x):
    return (x + 180.0) % 360.0 - 180.0


def dms(deg):
    """Format degrees-in-sign as 12°34'56\"."""
    d = int(deg)
    m_f = (deg - d) * 60
    m = int(m_f)
    s = int(round((m_f - m) * 60))
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d}\u00b0{m:02d}'{s:02d}\""


def fmt_pos(lon):
    return f"{dms(deg_in_sign(lon))} {SIGNS[sign_of(lon)]}"


def nak_info(lon):
    lon = n360(lon)
    i = int(lon // NAK_SPAN)
    pada = int((lon % NAK_SPAN) // (NAK_SPAN / 4)) + 1
    return {"index": i, "name": NAKSHATRAS[i], "pada": pada,
            "lord": VIM_ORDER[i % 9][0], "fraction": (lon % NAK_SPAN) / NAK_SPAN}


def resolve_time(date_str, time_str, lat, lon, tz_name=None, utc_offset=None):
    """Civil birth time -> UT, Julian day, standard time and true solar time.

    Uses the IANA tz database for the historical offset (including LMT eras,
    wartime clocks and DST). A manual utc_offset overrides it.
    """
    y, m, d = [int(v) for v in date_str.split("-")]
    parts = [int(v) for v in time_str.split(":")]
    hh, mm = parts[0], parts[1]
    ss = parts[2] if len(parts) > 2 else 0
    naive = dt.datetime(y, m, d, hh, mm, ss)
    warnings = []
    dst = dt.timedelta(0)
    abbr = None

    if utc_offset is not None:
        off = dt.timedelta(hours=float(utc_offset))
        utc = naive - off
        tz_label = f"manual UTC{float(utc_offset):+g}"
        warnings.append("Manual UTC offset used - the historical timezone/DST database was bypassed.")
    else:
        if not tz_name:
            from timezonefinder import TimezoneFinder
            tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon)
            if not tz_name:
                raise ValueError("Could not infer timezone from coordinates; pass --tz or --utc-offset")
        z = ZoneInfo(tz_name)
        aware = naive.replace(tzinfo=z)
        off = aware.utcoffset()
        dst = aware.dst() or dt.timedelta(0)
        abbr = aware.tzname()
        utc = aware.astimezone(dt.timezone.utc).replace(tzinfo=None)
        tz_label = tz_name
        if naive.replace(tzinfo=z, fold=1).utcoffset() != off:
            warnings.append("Ambiguous local time (clocks were turned back). Confirm which occurrence was meant.")
        back = utc.replace(tzinfo=dt.timezone.utc).astimezone(z).replace(tzinfo=None)
        if back != naive:
            warnings.append("This local time did not exist (clocks jumped forward). Confirm the recorded time.")
        if abbr == "LMT" or off.total_seconds() % 900 != 0:
            warnings.append(f"Local Mean Time / non-standard offset ({off}) applied for this date. Verify with the birth record.")
        if dst:
            warnings.append(f"Daylight/war-time of {dst} was in force and has been removed to reach UT.")

    jd_ut = swe.julday(utc.year, utc.month, utc.day,
                       utc.hour + utc.minute / 60.0 + utc.second / 3600.0)
    eot_min = swe.time_equ(jd_ut) * 1440.0
    lmt = utc + dt.timedelta(hours=lon / 15.0)
    tst = lmt + dt.timedelta(minutes=eot_min)
    std = naive - dst
    return {
        "local_civil": naive.isoformat(sep=" "),
        "timezone": tz_label, "tz_abbreviation": abbr,
        "utc_offset_hours": off.total_seconds() / 3600.0,
        "dst_removed_hours": dst.total_seconds() / 3600.0,
        "utc": utc.isoformat(sep=" "), "jd_ut": jd_ut,
        "local_standard_time": std.isoformat(sep=" "),
        "local_mean_time": lmt.isoformat(sep=" "),
        "equation_of_time_min": round(eot_min, 3),
        "true_solar_time": tst.isoformat(sep=" "),
        "_utc_dt": utc, "_naive": naive, "_std_dt": std, "_tst_dt": tst,
        "warnings": warnings,
    }


def ephemeris_mode(jd):
    _, ret = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    return "Moshier (built-in analytic theory)" if ret & swe.FLG_MOSEPH else "Swiss Ephemeris data files (JPL-derived)"


def jd_to_dt(jd):
    y, m, d, h = swe.revjul(jd)
    return dt.datetime(y, m, d) + dt.timedelta(hours=h)


def dt_to_jd(d):
    return swe.julday(d.year, d.month, d.day, d.hour + d.minute / 60.0 + d.second / 3600.0)
