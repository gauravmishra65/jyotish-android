"""shadbala.py - full Shadbala and Bhava bala in two named conventions.

Conventions (never mixed):
  "bphs"   - BPHS as taught by B.V. Raman ("Graha and Bhava Balas") and followed by most software:
             Cheshta from the seeghrochcha, Sun's Cheshta = its Ayana bala, Moon's = its Paksha bala,
             Ayana bala from true declination (24 deg, x1.25), special aspects of Mars/Jupiter/Saturn added
             as +15/+30/+45, Kendra bala by Sripati bhava, abda/masa lords from the Kali ahargana.
  "manual" - the scanned "Vedic Astrological Calculations" manual, Lesson XI (standard nativity,
             Madras 13 Dec 1871): Cheshta from the synodic arc of retrogression (Sun and Moon get 0),
             Ayana bala from the kranti (23.45 deg, x1.28), its own special-aspect curves, Placidus cusps
             as bhava madhyas, abda/masa lords from the Surya Siddhanta ahargana (epoch 24 Aug 1805).
Shared by both: Uchcha, Saptavargaja (MT 45 in the rasi only, own 30, compound relation 22.5/15/7.5/3.75/1.875),
Oja-yugma, Drekkana, Dik, Nathonnatha (apparent time), Paksha (Moon doubled), Tribhaga, vara/hora,
Naisargika, Drik bala = 1/4 of other planets' drishti with Mercury's and Jupiter's taken in full.

All values are shashtiamsas (virupas); 60 = 1 rupa.
"""
import math
import datetime as dt
import swisseph as swe
from common import SIGN_LORD, n360, sign_of, deg_in_sign, wrap180, jd_to_dt, dt_to_jd

P7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SWE_ID = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
          "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
EXALT_PT = {"Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165, "Jupiter": 95, "Venus": 357, "Saturn": 200}
DEB_PT = {p: (v + 180) % 360 for p, v in EXALT_PT.items()}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10]}
MOOLA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 15, 20),
         "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
NAT_FRIENDS = {"Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
               "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
               "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
               "Saturn": ["Mercury", "Venus"]}
NAT_ENEMIES = {"Sun": ["Venus", "Saturn"], "Moon": [], "Mars": ["Mercury"], "Mercury": ["Moon"],
               "Jupiter": ["Mercury", "Venus"], "Venus": ["Sun", "Moon"], "Saturn": ["Sun", "Moon", "Mars"]}
NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
REQUIRED = {"Sun": 390, "Moon": 360, "Mars": 300, "Mercury": 420, "Jupiter": 390, "Venus": 330, "Saturn": 300}
POWERLESS_MADHYA = {"Sun": 4, "Mars": 4, "Saturn": 1, "Mercury": 7, "Jupiter": 7, "Moon": 10, "Venus": 10}
REL_VALUE = {"great friend": 22.5, "friend": 15.0, "neutral": 7.5, "enemy": 3.75, "great enemy": 1.875}
SAPTA = [1, 2, 3, 7, 9, 12, 30]
HORA_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]  # descending distance
WEEKDAY_SUN0 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
DIAM = {"manual": {"Mars": 9.36, "Mercury": 6.68, "Jupiter": 191.72, "Venus": 16.80, "Saturn": 169.50},
        "bphs": {"Mars": 9.4, "Mercury": 6.6, "Jupiter": 190.4, "Venus": 16.6, "Saturn": 158.0}}
EPOCH = {"manual": dt.date(1805, 8, 24),          # a Surya Siddhanta year, month and week ended this day
         "bphs": None}                             # Kali ahargana (JD 588465.5 = start of Kali yuga)
KALI_JD0 = 588465.5


# ------------------------------------------------------------------ relationships
def natural_rel(p, q):
    if q in NAT_FRIENDS[p]:
        return 1
    if q in NAT_ENEMIES[p]:
        return -1
    return 0


def temporal_rel(si, p, q):
    d = (si[q] - si[p]) % 12 + 1
    return 1 if d in (2, 3, 4, 10, 11, 12) else -1


def compound_rel(si, p, q):
    v = natural_rel(p, q) + temporal_rel(si, p, q)
    return {2: "great friend", 1: "friend", 0: "neutral", -1: "enemy", -2: "great enemy"}[v]


def relationship_tables(si):
    return {p: {q: {"natural": {1: "friend", 0: "neutral", -1: "enemy"}[natural_rel(p, q)],
                    "temporary": "friend" if temporal_rel(si, p, q) > 0 else "enemy",
                    "compound": compound_rel(si, p, q)} for q in P7 if q != p} for p in P7}


# ------------------------------------------------------------------ varga signs (local copy, Parashari)
def varga_sign(lon, n):
    s, d = sign_of(lon), deg_in_sign(lon)
    odd = s % 2 == 0
    if n == 1:
        return s
    if n == 2:
        return 4 if (odd and d < 15) or (not odd and d >= 15) else 3
    if n == 3:
        return (s + int(d // 10) * 4) % 12
    if n == 7:
        return ((s if odd else (s + 6) % 12) + int(d / (30 / 7))) % 12
    if n == 9:
        mode = s % 3
        start = s if mode == 0 else ((s + 8) % 12 if mode == 1 else (s + 4) % 12)
        return (start + int(d / (30 / 9))) % 12
    if n == 12:
        return (s + int(d // 2.5)) % 12
    if n == 30:
        table = ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)) if odd else ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7))
        for lim, sg in table:
            if d < lim:
                return sg
        return table[-1][1]
    raise ValueError(n)


# ------------------------------------------------------------------ drishti
def _base_drishti(a):
    if 30 <= a < 60:
        return (a - 30) / 2
    if 60 <= a < 90:
        return a - 60 + 15
    if 90 <= a < 120:
        return (120 - a) / 2 + 30
    if 120 <= a < 150:
        return 150 - a
    if 150 <= a < 180:
        return (a - 150) * 2
    if 180 <= a <= 300:
        return (300 - a) / 2
    return 0.0


def drishti_value(src, angle, convention):
    """Aspect value (0-60) cast by `src` on a point `angle` degrees ahead of it (anticlockwise)."""
    a = n360(angle)
    if convention == "bphs":
        v = _base_drishti(a)
        if src == "Mars" and (90 <= a < 120 or 210 <= a < 240):
            v += 15
        if src == "Jupiter" and (120 <= a < 150 or 240 <= a < 270):
            v += 30
        if src == "Saturn" and (60 <= a < 90 or 270 <= a < 300):
            v += 45
        return v
    # manual, Art. 95-96
    if src == "Mars":
        if 60 <= a < 90:
            return (a - 60) * 1.5 + 15
        if 90 <= a < 120:
            return 60 - (a - 90)
        if 180 <= a < 210:
            return 60.0
        if 210 <= a < 240:
            return 60 - (a - 210)
        if 240 <= a <= 300:
            return (300 - a) / 2
    if src == "Jupiter":
        if 90 <= a < 120:
            return 60 - (a - 90)
        if 180 <= a < 210:
            return (210 - a) / 2 + 45
        if 210 <= a < 240:
            return (a - 210) / 2 + 45
        if 240 <= a < 270:
            return (a - 240) * 1.5 + 15
        if 270 <= a <= 300:
            return (300 - a) / 2
    if src == "Saturn":
        if 60 <= a < 90:
            return 60 - (a - 60) / 2
        if 90 <= a < 120:
            return (120 - a) / 2 + 30
        if 180 <= a < 210:
            return 60 - (a - 180) / 2
        if 210 <= a < 240:
            return 60 - (a - 210) / 2
        if 240 <= a < 270:
            return (a - 240) + 30
        if 270 <= a <= 300:
            return (300 - a) * 2
    return _base_drishti(a)


def mercury_is_malefic(si):
    return any(si[q] == si["Mercury"] for q in ("Sun", "Mars", "Saturn"))


def drik_bala(lon, si, convention, target_lon=None, exclude=None):
    """Drik bala on each planet (or on `target_lon` when given). Returns (value, detail)."""
    benefic = {"Moon": True, "Jupiter": True, "Venus": True, "Sun": False, "Mars": False, "Saturn": False,
               "Mercury": not mercury_is_malefic(si)}
    if convention == "manual":
        benefic["Mercury"] = True           # the manual's Problem 48 adds Mercury's drishti in full, as saumya
    targets = {"_point": target_lon} if target_lon is not None else {p: lon[p] for p in P7}
    out = {}
    for t, tl in targets.items():
        tot, det = 0.0, {}
        for s in P7:
            if s == t or s == exclude:
                continue
            v = drishti_value(s, tl - lon[s], convention)
            sign = 1 if benefic[s] else -1
            share = v if s in ("Mercury", "Jupiter") else v / 4
            det[s] = round(sign * v, 3)
            tot += sign * share
        out[t] = (tot, det)
    return out


# ------------------------------------------------------------------ inputs from the ephemeris
def _mean_lon_trop(jd):
    """Mean heliocentric longitudes of date (Meeus, Table 31.A, leading terms) and the mean Sun."""
    T = (jd - 2451545.0) / 36525.0
    L = {"Mercury": 252.250906 + 149472.6746358 * T, "Venus": 181.979801 + 58517.8156760 * T,
         "Mars": 355.433000 + 19140.2993039 * T, "Jupiter": 34.351519 + 3034.9056606 * T,
         "Saturn": 50.077444 + 1222.1137943 * T, "Sun": 280.466457 + 35999.3728565 * T}
    return {k: n360(v) for k, v in L.items()}


def _trop(jd, p):
    xx, _ = swe.calc_ut(jd, SWE_ID[p], swe.FLG_SWIEPH | swe.FLG_SPEED)
    return xx


def _find_zero(f, a, b, it=50):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        fm = f(m)
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def _scan(f, jd, direction, limit=900, step=1.0, accept=None):
    t0, f0 = jd, f(jd)
    for i in range(1, int(limit / step) + 1):
        t1 = jd + direction * i * step
        f1 = f(t1)
        if (f0 < 0) != (f1 < 0) and abs(f0 - f1) < 180:
            z = _find_zero(f, min(t0, t1), max(t0, t1))
            if accept is None or accept(z):
                return z
        t0, f0 = t1, f1
    return None


def synodic_cheshta(jd, p):
    """Manual Art. 121-125: arc of retrogression of planet p at jd (tropical longitudes)."""
    sun = lambda t: _trop(t, "Sun")[0]
    pl = lambda t: _trop(t, p)[0]
    P = pl(jd)
    inferior = p in ("Mercury", "Venus")
    elong = n360(P - sun(jd))
    phase1 = (elong < 180) if inferior else (elong > 180)   # SC->IC or C->O
    conj = lambda t: wrap180(pl(t) - sun(t))
    opp = lambda t: wrap180(pl(t) - sun(t) - 180)
    speed = lambda t: _trop(t, p)[3]
    dist = lambda t: _trop(t, p)[2] - _trop(t, "Sun")[2]
    if inferior:
        A_f, A_ok = conj, (lambda t: dist(t) > 0)      # superior conjunction: planet beyond the Sun
        Z_f, Z_ok = conj, (lambda t: dist(t) < 0)      # inferior conjunction
    else:
        A_f, A_ok, Z_f, Z_ok = conj, None, opp, None
    if phase1:
        tA = _scan(A_f, jd, -1, accept=A_ok)
        tS = _scan(speed, jd, +1)
        tZ = _scan(Z_f, jd, +1, accept=Z_ok)
        if tS is not None and tZ is not None and tS > tZ:   # already retrograde: station lies behind
            tS = _scan(speed, jd, -1)
        A, S, Z = pl(tA), pl(tS), pl(tZ)
        mx = n360(S - A) + n360(S - Z)
        retro = speed(jd) < 0
        ck = n360(S - A) + n360(S - P) if retro else n360(P - A)
        kind = ("superior conjunction to inferior conjunction" if inferior else "conjunction to opposition")
    else:
        tZ = _scan(Z_f, jd, -1, accept=Z_ok)
        tS = _scan(speed, jd, -1)
        tA = _scan(A_f, jd, +1, accept=A_ok)
        if tS is not None and tZ is not None and tS < tZ:   # still retrograde: station lies ahead
            tS = _scan(speed, jd, +1)
        A, S, Z = pl(tA), pl(tS), pl(tZ)
        mx = n360(A - S) + n360(Z - S)
        retro = speed(jd) < 0
        ck = n360(A - S) + n360(P - S) if retro else n360(A - P)
        kind = ("inferior conjunction to superior conjunction" if inferior else "opposition to conjunction")
    vck = ck * 180.0 / mx if mx else 0.0
    return {"phase": kind, "conjunction_point": round(A, 3), "station_point": round(S, 3),
            "opposition_or_inferior_point": round(Z, 3), "planet": round(P, 3),
            "max_cheshta_kendra": round(mx, 3), "cheshta_kendra": round(ck, 3),
            "vedic_cheshta_kendra": round(vck, 3), "bala": vck / 3.0}


def _rt(jd0, lat, lon, kind):
    try:
        r = swe.rise_trans(jd0, swe.SUN, kind | swe.BIT_DISC_CENTER, (lon, lat, 0.0), 1013.25, 15.0)
    except swe.Error:
        return None
    t = r[1][0]
    return t if r[0] >= 0 and jd0 < t < jd0 + 1.5 else None


def _day_frame(jd, lat, lon, lat_h=None):
    """(sunrise before jd, following sunset, next sunrise, polar_fallback)."""
    sr = _rt(jd - 1.0, lat, lon, swe.CALC_RISE)
    if sr is not None and sr > jd:
        sr = _rt(jd - 2.0, lat, lon, swe.CALC_RISE)
    ss = _rt(sr, lat, lon, swe.CALC_SET) if sr is not None else None
    nxt = _rt(sr + 0.01, lat, lon, swe.CALC_RISE) if sr is not None else None
    if sr is None or ss is None or nxt is None:
        if lat_h is None:
            _e = swe.time_equ(jd)
            eot = _e[1] if isinstance(_e, (tuple, list)) else _e
            lat_h = ((((jd + 0.5 + lon / 360.0) % 1.0) * 24.0) + eot * 24.0) % 24.0
        day0 = jd - lat_h / 24.0                      # local apparent midnight
        sr = day0 + 0.25 if lat_h >= 6 else day0 - 0.75
        return sr, sr + 0.5, sr + 1.0, True
    return sr, ss, nxt, False


def sunrise_before(jd, lat, lon):
    return _day_frame(jd, lat, lon)[0]


def chart_inputs(jd, lat, lon, ayan_mode, convention):
    """Everything the pure computation needs, taken from Swiss Ephemeris."""
    swe.set_sid_mode(ayan_mode)
    ay = swe.get_ayanamsa_ut(jd)
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    sid, lat_e, decl, trop = {}, {}, {}, {}
    eps = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
    for p in P7:
        xx = swe.calc_ut(jd, SWE_ID[p], fl)[0]
        sid[p], lat_e[p] = xx[0], xx[1]
        eq = swe.calc_ut(jd, SWE_ID[p], swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
        decl[p] = eq[1]
        trop[p] = n360(sid[p] + ay)
    hs = b"P" if convention == "manual" else b"O"
    placidus_failed = False
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, hs, swe.FLG_SIDEREAL)
    except swe.Error:                      # Placidus is undefined inside the polar circles
        placidus_failed = True
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"O", swe.FLG_SIDEREAL)
    madhya = list(cusps)[:12]
    # time: apparent solar time from apparent midnight
    _e = swe.time_equ(jd)
    eot = _e[1] if isinstance(_e, (tuple, list)) else _e    # days (LAT - LMT)
    lmt_h = ((jd + 0.5 + lon / 360.0) % 1.0) * 24.0
    lat_h = (lmt_h + eot * 24.0) % 24.0
    # sunrise before birth, next sunset / sunrise (6:00/18:00 local apparent time where the Sun does not rise or set)
    sr, ss, nxt, polar = _day_frame(jd, lat, lon, lat_h)
    if convention == "manual":
        kranti = {p: math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(trop[p])))) for p in P7}
    else:
        kranti = decl
    # Hindu day: civil date of the sunrise that began it (local mean date)
    local_sr = jd_to_dt(sr) + dt.timedelta(hours=lon / 15.0)
    inp = {"lon": sid, "lat": lat_e, "kranti": kranti, "madhya": madhya, "asc": ascmc[0],
           "apparent_hours_from_midnight": lat_h,
           "birth_jd": jd, "sunrise_jd": sr, "sunset_jd": ss, "next_sunrise_jd": nxt,
           "hindu_date": local_sr.date(), "weekday": WEEKDAY_SUN0[(local_sr.date().isoweekday()) % 7],
           "polar_fallback": polar, "placidus_failed": placidus_failed}
    if convention == "manual":
        inp["cheshta"] = {}
        for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            try:
                inp["cheshta"][p] = synodic_cheshta(jd, p)
            except Exception as e:          # pragma: no cover - search failure is reported, not hidden
                inp["cheshta"][p] = {"error": str(e), "bala": None}
    else:
        m = _mean_lon_trop(jd)
        msid = {k: n360(v - ay) for k, v in m.items()}
        ch = {}
        for p in ("Mars", "Jupiter", "Saturn"):
            ch[p] = _ck(msid["Sun"], msid[p], sid[p])
        for p in ("Mercury", "Venus"):
            ch[p] = _ck(msid[p], msid["Sun"], sid[p])
        inp["cheshta"] = ch
    return inp


def _avg(a, b):
    return n360(a + wrap180(b - a) / 2.0)


def _ck(seeg, mean, true):
    ck = n360(seeg - _avg(mean, true))
    if ck > 180:
        ck = 360 - ck
    return {"seeghrochcha": round(seeg, 3), "mean_longitude": round(mean, 3), "true_longitude": round(true, 3),
            "cheshta_kendra": round(ck, 3), "bala": ck / 3.0}


# ------------------------------------------------------------------ the computation
def _bhava_of(l, madhya):
    for i in range(12):
        pm, cm, nm = madhya[(i - 1) % 12], madhya[i], madhya[(i + 1) % 12]
        st = pm + wrap180(cm - pm) / 2
        en = cm + wrap180(nm - cm) / 2
        if n360(l - st) < n360(en - st):
            return i + 1
    return 1


def _lord_of_day_start(day, period, convention):
    """Weekday lord of the first day of the running astrological year (360) or month (30)."""
    if convention == "manual":
        ah = (day - EPOCH["manual"]).days
        first = EPOCH["manual"] + dt.timedelta(days=(ah // period) * period + 1)
    else:
        jd_day = swe.julday(day.year, day.month, day.day, 12.0)
        ah = int(jd_day - (KALI_JD0 + 0.5))
        first_jd = KALI_JD0 + 0.5 + (ah // period) * period
        y, m, d, _ = swe.revjul(first_jd)
        first = dt.date(y, m, d)
    return WEEKDAY_SUN0[first.isoweekday() % 7], first


def compute(inp, convention="bphs"):
    lon, madhya = inp["lon"], inp["madhya"]
    si = {p: sign_of(lon[p]) for p in P7}
    res = {p: {} for p in P7}
    # ---- Sthana
    for p in P7:
        u = abs(wrap180(lon[p] - DEB_PT[p])) / 3.0
        sv, svd = 0.0, {}
        for n in SAPTA:
            s = varga_sign(lon[p], n)
            ms, a, b = MOOLA[p]
            if n == 1 and s == ms and a <= deg_in_sign(lon[p]) < b:
                v, why = 45.0, "moolatrikona"
            elif s in OWN[p]:
                v, why = 30.0, "own"
            else:
                lord = SIGN_LORD[s]
                why = compound_rel(si, p, lord)
                v = REL_VALUE[why]
            sv += v
            svd[f"D{n}"] = why
        rs, ns = si[p], varga_sign(lon[p], 9)
        fem = p in ("Moon", "Venus")
        oj = (15 if (rs % 2 == 1) == fem else 0) + (15 if (ns % 2 == 1) == fem else 0)
        h = _bhava_of(lon[p], madhya)
        ke = 60 if h in (1, 4, 7, 10) else 30 if h in (2, 5, 8, 11) else 15
        dk = int(deg_in_sign(lon[p]) // 10)
        dr = 15 if ((p in ("Sun", "Mars", "Jupiter") and dk == 0) or (p in ("Mercury", "Saturn") and dk == 1)
                    or (p in ("Moon", "Venus") and dk == 2)) else 0
        res[p]["sthana"] = {"uchcha": u, "saptavargaja": sv, "ojayugma": oj, "kendra": ke, "drekkana": dr,
                            "total": u + sv + oj + ke + dr, "_varga_relations": svd, "_bhava": h}
    # ---- Dik
    for p in P7:
        pt = madhya[POWERLESS_MADHYA[p] - 1]
        res[p]["dik"] = abs(wrap180(lon[p] - pt)) / 3.0
    # ---- Kala
    th = inp["apparent_hours_from_midnight"] * 15.0
    unnata = th if th <= 180 else 360 - th
    diva = unnata / 3.0
    sun, moon = lon["Sun"], lon["Moon"]
    pk = abs(wrap180(moon - sun)) / 3.0          # saumya paksha
    mer_mal = mercury_is_malefic(si)
    jd, sr, ss, nsr = inp["birth_jd"], inp["sunrise_jd"], inp["sunset_jd"], inp["next_sunrise_jd"]
    if jd < ss:
        part = int((jd - sr) / ((ss - sr) / 3.0))
        tri_lord = ["Mercury", "Sun", "Saturn"][min(part, 2)]
    else:
        part = int((jd - ss) / ((nsr - ss) / 3.0))
        tri_lord = ["Moon", "Venus", "Mars"][min(part, 2)]
    vara = inp["weekday"]
    hours = int((jd - sr) * 24.0)
    hora_lord = HORA_ORDER[(HORA_ORDER.index(vara) + hours) % 7]
    abda, abda_first = _lord_of_day_start(inp["hindu_date"], 360, convention)
    masa, masa_first = _lord_of_day_start(inp["hindu_date"], 30, convention)
    for p in P7:
        nat = 60.0 if p == "Mercury" else (diva if p in ("Sun", "Jupiter", "Venus") else 60.0 - diva)
        saumya = p in ("Moon", "Jupiter", "Venus") or (p == "Mercury" and not mer_mal)
        pak = pk if saumya else 60.0 - pk
        if p == "Moon":
            pak *= 2
        tri = 60.0 if p in ("Jupiter", tri_lord) else 0.0
        amvh = (15 if p == abda else 0) + (30 if p == masa else 0) + (45 if p == vara else 0) + (60 if p == hora_lord else 0)
        k = inp["kranti"][p]
        north = k > 0
        if convention == "manual":
            base, mult = 23.45, 1.28
        else:
            base, mult = 24.0, 60.0 / 48.0
        if p == "Mercury":
            ay = (base + abs(k)) * mult
        elif p in ("Moon", "Saturn"):
            ay = (base - k) * mult
        else:
            ay = (base + k) * mult
        if p == "Sun":
            ay *= 2
        res[p]["kala"] = {"nathonnatha": nat, "paksha": pak, "tribhaga": tri, "abda_masa_vara_hora": amvh,
                          "ayana": ay, "yuddha": 0.0}
    # ---- Yuddha (Mars..Saturn within 1 degree; the northern planet wins)
    five = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    wars = []
    orb = 1.0 if convention == "bphs" else 1.0 / 60.0   # manual Art. 119: same longitude correct to a minute
    for i in range(5):
        for j in range(i + 1, 5):
            a, b = five[i], five[j]
            if abs(wrap180(lon[a] - lon[b])) < orb:
                def pre(x):
                    kk = res[x]["kala"]
                    return (res[x]["sthana"]["total"] + res[x]["dik"] + kk["nathonnatha"] + kk["paksha"]
                            + kk["tribhaga"] + kk["abda_masa_vara_hora"] + kk["ayana"])
                win, lose = (a, b) if inp["lat"][a] >= inp["lat"][b] else (b, a)
                yb = abs(pre(win) - pre(lose)) / abs(DIAM[convention][a] - DIAM[convention][b])
                res[win]["kala"]["yuddha"] += yb
                res[lose]["kala"]["yuddha"] -= yb
                wars.append({"winner": win, "loser": lose, "yuddha_bala": round(yb, 2)})
    for p in P7:
        res[p]["kala"]["total"] = sum(v for k, v in res[p]["kala"].items() if k != "total")
    # ---- Cheshta
    for p in P7:
        if p == "Sun":
            c = res["Sun"]["kala"]["ayana"] if convention == "bphs" else 0.0
        elif p == "Moon":
            c = res["Moon"]["kala"]["paksha"] if convention == "bphs" else 0.0
        else:
            c = inp["cheshta"][p]["bala"]
        res[p]["cheshta"] = c
        res[p]["naisargika"] = NAISARGIKA[p]
    # ---- Drik
    dk = drik_bala(lon, si, convention)
    for p in P7:
        res[p]["drik"] = dk[p][0]
        res[p]["_drishti_received"] = dk[p][1]
    # ---- totals
    for p in P7:
        r = res[p]
        tot = r["sthana"]["total"] + r["dik"] + r["kala"]["total"] + r["cheshta"] + r["naisargika"] + r["drik"]
        r["total"] = tot
        r["rupas"] = tot / 60.0
        r["required_rupas"] = REQUIRED[p] / 60.0
        r["ratio"] = tot / REQUIRED[p]
        u, c = r["sthana"]["uchcha"], min(r["cheshta"], 60.0)   # Sun/Moon Cheshta can exceed 60 (doubled Ayana/Paksha)
        r["ishta_phala"] = math.sqrt(max(u, 0) * max(c, 0))
        r["kashta_phala"] = math.sqrt(max(60 - u, 0) * max(60 - c, 0))
    order = sorted(P7, key=lambda p: -res[p]["ratio"])
    for i, p in enumerate(order):
        res[p]["rank_by_ratio"] = i + 1
    meta = {"convention": convention, "tribhaga_lord": tri_lord, "vara_lord": vara, "hora_lord": hora_lord,
            "abda_lord": abda, "abda_year_began": abda_first.isoformat(), "masa_lord": masa,
            "masa_began": masa_first.isoformat(), "mercury_treated_as": "malefic" if mer_mal else "benefic",
            "graha_yuddha": wars}
    if inp.get("placidus_failed"):
        meta["house_note"] = "Placidus cusps do not exist at this latitude; Sripati (Porphyry) madhyas were used."
    if inp.get("polar_fallback"):
        meta["polar_note"] = ("The Sun does not rise or set on this date here; day and night were taken as 6:00-18:00 local "
                              "apparent time for Tribhaga and Hora bala.")
    return res, meta


# ------------------------------------------------------------------ Bhava bala (BPHS / Raman, three parts)
NARA = "nara"


def _bhava_sign_class(l):
    s, d = sign_of(l), deg_in_sign(l)
    if s in (2, 5, 6, 10) or (s == 8 and d < 15):
        return "nara", 7           # powerless at the 7th
    if s in (0, 1, 4) or (s == 8 and d >= 15) or (s == 9 and d < 15):
        return "chatushpada", 4
    if s in (3, 11) or (s == 9 and d >= 15):
        return "jalachara", 10
    return "keeta", 1              # Scorpio


def bhava_bala(inp, graha, convention="bphs"):
    lon, madhya = inp["lon"], inp["madhya"]
    si = {p: sign_of(lon[p]) for p in P7}
    out = {}
    for i in range(12):
        m = madhya[i]
        lord = SIGN_LORD[sign_of(m)]
        adhi = graha[lord]["total"]
        cls, weak = _bhava_sign_class(m)
        diff = abs((i + 1) - weak)
        if diff > 6:
            diff = 12 - diff
        dig = 10.0 * diff
        dr = drik_bala(lon, si, convention, target_lon=m)["_point"]
        tot = adhi + dig + dr[0]
        out[f"H{i + 1}"] = {"madhya": round(m, 3), "lord": lord, "bhavadhipati": round(adhi, 2),
                            "dig": dig, "sign_class": cls, "drishti": round(dr[0], 2),
                            "total": round(tot, 2), "rupas": round(tot / 60.0, 3)}
    order = sorted(out, key=lambda h: -out[h]["total"])
    for r, h in enumerate(order):
        out[h]["rank"] = r + 1
    return out


def _r(x, k=2):
    return round(x, k) if isinstance(x, (int, float)) else x


def public(res, meta):
    rows = {}
    for p in P7:
        r = res[p]
        rows[p] = {"sthana": {k: _r(v) for k, v in r["sthana"].items() if not k.startswith("_")},
                   "saptavargaja_relations": r["sthana"]["_varga_relations"],
                   "kendra_bala_bhava": r["sthana"]["_bhava"],
                   "dik": _r(r["dik"]), "kala": {k: _r(v) for k, v in r["kala"].items()},
                   "cheshta": _r(r["cheshta"]), "naisargika": r["naisargika"], "drik": _r(r["drik"]),
                   "total_virupa": _r(r["total"]), "rupas": _r(r["rupas"], 3),
                   "required_rupas": _r(r["required_rupas"], 2), "ratio": _r(r["ratio"], 3),
                   "rank_by_ratio": r["rank_by_ratio"], "ishta_phala": _r(r["ishta_phala"]),
                   "kashta_phala": _r(r["kashta_phala"]),
                   "verdict": "strong" if r["ratio"] >= 1 else "below the required minimum"}
    return {"planets": rows, "meta": meta}


def build(jd, lat, lon, ayan_mode):
    out = {}
    for conv in ("bphs", "manual"):
        inp = chart_inputs(jd, lat, lon, ayan_mode, conv)
        res, meta = compute(inp, conv)
        pub = public(res, meta)
        if conv == "manual":
            pub["cheshta_arcs"] = {p: {k: v for k, v in d.items() if k != "bala"} for p, d in inp["cheshta"].items()}
        else:
            pub["cheshta_inputs"] = {p: {k: v for k, v in d.items() if k != "bala"} for p, d in inp["cheshta"].items()}
            pub["bhava_bala"] = bhava_bala(inp, res, conv)
        out[conv] = pub
    out["conventions"] = ("Two named conventions, never mixed. 'bphs' (default, B.V. Raman / BPHS as most software) "
                          "and 'manual' (Vedic Astrological Calculations, Lesson XI). Bhava bala is given in the BPHS "
                          "convention with three parts (lord's Shadbala, dig bala by sign class, drishti on the "
                          "bhava madhya); the manual's scan stops before its own Bhava bala table, so that part is "
                          "untested. Required minimums (rupas): Sun 6.5, Moon 6, Mars 5, Mercury 7, Jupiter 6.5, "
                          "Venus 5.5, Saturn 5 (BPHS and the manual agree).")
    return out
