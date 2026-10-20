"""western.py - tropical astrology: natal, aspects, transits, returns, progressions,
Hellenistic time-lord techniques, and two-chart synastry. Deterministic only."""
import datetime as dt
import swisseph as swe
from common import (SIGNS, SIGN_LORD, n360, sign_of, deg_in_sign, wrap180, dms,
                    fmt_pos, jd_to_dt, dt_to_jd)

WPLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY), ("Venus", swe.VENUS),
            ("Mars", swe.MARS), ("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN),
            ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO)]
ELEMENTS = ["Fire", "Earth", "Air", "Water"]
MODES = ["Cardinal", "Fixed", "Mutable"]
ASPECTS = [("conjunction", 0, 8.0), ("opposition", 180, 8.0), ("trine", 120, 8.0),
           ("square", 90, 7.0), ("sextile", 60, 5.0), ("quincunx", 150, 3.0)]
ZR_YEARS = [15, 8, 20, 25, 19, 20, 8, 15, 12, 27, 30, 12]  # Aries..Pisces (Valens), total 211


def tropical_positions(jd):
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED
    out = {}
    for name, pid in WPLANETS:
        xx, _ = swe.calc_ut(jd, pid, fl)
        out[name] = {"lon": xx[0], "lat": xx[1], "speed": xx[3]}
    xx, _ = swe.calc_ut(jd, swe.TRUE_NODE, fl)
    out["North Node"] = {"lon": xx[0], "lat": 0.0, "speed": xx[3]}
    return out


def tropical_angles(jd, lat, lon):
    warn = None
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P")
        system = "Placidus"
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"O")
        system, warn = "Porphyry", "Placidus is undefined at this latitude; Porphyry used"
    tropical_angles.vertex = ascmc[3]
    return list(cusps), ascmc[0], ascmc[1], system, warn


def _house_by_cusps(l, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if n360(l - a) < n360(b - a):
            return i + 1
    return 1


def aspects_between(A, B, same=False, use_motion=True, max_orb_scale=1.0):
    """A/B: lists of (name, lon, speed). Returns aspects sorted by orb."""
    out = []
    for i, (na, la, sa) in enumerate(A):
        for j, (nb, lb, sb) in enumerate(B):
            if same and j <= i:
                continue
            sep = abs(wrap180(lb - la))
            for an, ang, orb in ASPECTS:
                o = abs(sep - ang)
                if o <= orb * max_orb_scale:
                    rec = {"a": na, "b": nb, "aspect": an, "orb": round(o, 3)}
                    if use_motion and (sa or sb):
                        sep2 = abs(wrap180((lb + sb * 0.05) - (la + sa * 0.05)))
                        rec["applying"] = abs(sep2 - ang) < o
                    out.append(rec)
    return sorted(out, key=lambda r: r["orb"])


def _find_crossings(natal_lon, pid, start_jd, end_jd, step, min_age_years=0.0):
    swe.set_sid_mode(0)
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED

    def d(j):
        return wrap180(swe.calc_ut(j, pid, fl)[0][0] - natal_lon)
    scan_from = start_jd + min_age_years * 365.25
    hits, j, prev = [], scan_from, d(scan_from)
    while j < end_jd:
        j2 = j + step
        cur = d(j2)
        if prev * cur < 0 and abs(prev) < 30 and abs(cur) < 30:
            a, b = j, j2
            for _ in range(30):
                m = (a + b) / 2
                if d(m) * prev > 0:
                    a = m
                else:
                    b = m
            hits.append((a + b) / 2)
        prev, j = cur, j2
    # cluster retrograde triple passes (within ~1.6 years)
    clusters = []
    for h in hits:
        if clusters and h - clusters[-1][-1] < 600:
            clusters[-1].append(h)
        else:
            clusters.append([h])
    return [{"first": jd_to_dt(c[0]).date().isoformat(), "last": jd_to_dt(c[-1]).date().isoformat(),
             "exact_dates": [jd_to_dt(x).date().isoformat() for x in c]} for c in clusters]



def exact_transit_dates(pid, natal_lon, aspect_deg, now_jd, cur_lon):
    """Dates when transiting body `pid` makes the exact aspect to a natal longitude, from ~1.2 years ago to ~2.5 years ahead.
    Retrograde loops give up to three dates. Also returns the entry/exit of the 1-degree orb around the first exact hit."""
    targets = {n360(natal_lon + aspect_deg), n360(natal_lon - aspect_deg)}
    target = min(targets, key=lambda t: abs(wrap180(cur_lon - t)))
    step = {swe.MARS: 0.5, swe.JUPITER: 2.0, swe.SATURN: 3.0}.get(pid, 5.0)
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED

    def d(j):
        return wrap180(swe.calc_ut(j, pid, fl)[0][0] - target)
    j0, j1 = now_jd - 440, now_jd + 900
    hits, j, prev = [], j0, d(j0)
    while j < j1:
        cur = d(j + step)
        if prev * cur < 0 and abs(prev) < 20 and abs(cur) < 20:
            a, b = j, j + step
            for _ in range(28):
                m = (a + b) / 2
                if d(m) * prev > 0:
                    a = m
                else:
                    b = m
            hits.append((a + b) / 2)
        prev, j = cur, j + step
    return [jd_to_dt(h).date().isoformat() for h in hits]


def hellenistic(pos, asc, birth_utc, now_utc):
    sun, moon = pos["Sun"]["lon"], pos["Moon"]["lon"]
    is_day = n360(sun - asc) >= 180
    if is_day:
        fortune, spirit = n360(asc + moon - sun), n360(asc + sun - moon)
    else:
        fortune, spirit = n360(asc + sun - moon), n360(asc + moon - sun)
    age = int((now_utc - birth_utc).days // 365.2425)
    pr_sign = (sign_of(asc) + age) % 12

    def zr(start):
        out, t, s = [], birth_utc, sign_of(start)
        total = 0
        while total < 100:
            yrs = ZR_YEARS[s]
            e = t + dt.timedelta(days=yrs * 360)
            out.append({"sign": SIGNS[s], "ruler": SIGN_LORD[s], "years": yrs,
                         "from": t.date().isoformat(), "to": e.date().isoformat()})
            t, s, total = e, (s + 1) % 12, total + yrs
        cur = next((x for x in out if x["from"] <= now_utc.date().isoformat() < x["to"]), None)
        return {"level1_current": cur, "level1_sequence": out[:8]}
    return {"sect": "day chart" if is_day else "night chart",
            "lot_of_fortune": fmt_pos(fortune), "lot_of_spirit": fmt_pos(spirit),
            "annual_profection": {"age": age, "profected_house": age % 12 + 1,
                                  "profected_sign": SIGNS[pr_sign], "year_lord": SIGN_LORD[pr_sign]},
            "zodiacal_releasing_from_spirit": zr(spirit), "zodiacal_releasing_from_fortune": zr(fortune),
            "notes": "Whole-sign houses from the tropical Ascendant; traditional rulers; Valens 360-day years. "
                     "Zodiacal releasing is computed here at Level 1; Level 2, peaks and loosing of the bond for the forecast window are in forecast.western.zodiacal_releasing."}


def solar_return_tropical(natal_sun, birth_utc, age, lat, lon):
    guess = dt_to_jd(dt.datetime(birth_utc.year + age, birth_utc.month, 1) + dt.timedelta(days=birth_utc.day - 1 - 5))   # leap-day safe
    jd = swe.solcross_ut(natal_sun, guess, swe.FLG_SWIEPH)
    pos = tropical_positions(jd)
    cusps, asc, mc, hs, _ = tropical_angles(jd, lat, lon)
    return {"age": age, "return_utc": jd_to_dt(jd).strftime("%Y-%m-%d %H:%M:%S"),
            "ascendant": fmt_pos(asc), "midheaven": fmt_pos(mc), "house_system": hs,
            "planets": {p: {"pos": fmt_pos(v["lon"]), "house": _house_by_cusps(v["lon"], cusps)} for p, v in pos.items()},
            "note": "Cast for the location supplied (relocated returns differ from birthplace returns)."}


def build_western(jd, birth_utc, now_utc, lat, lon, cur_lat=None, cur_lon=None):
    pos = tropical_positions(jd)
    cusps, asc, mc, hsys, warn = tropical_angles(jd, lat, lon)
    vertex = tropical_angles.vertex
    asc_sign = sign_of(asc)
    planets = {}
    for p, v in pos.items():
        s = sign_of(v["lon"])
        planets[p] = {"lon": round(v["lon"], 5), "sign": SIGNS[s], "dms": dms(deg_in_sign(v["lon"])),
                      "house_placidus": _house_by_cusps(v["lon"], cusps),
                      "house_whole_sign": (s - asc_sign) % 12 + 1,
                      "retrograde": bool(v["speed"] < 0) if p not in ("Sun", "Moon") else False,
                      "element": ELEMENTS[s % 4], "modality": MODES[s % 3]}
    big3 = {"sun": planets["Sun"]["sign"], "moon": planets["Moon"]["sign"], "rising": SIGNS[asc_sign]}
    pts = [(p, v["lon"], v["speed"]) for p, v in pos.items()] + [("Ascendant", asc, 0.0), ("Midheaven", mc, 0.0)]
    natal_aspects = aspects_between(pts, pts, same=True)
    count_el, count_mo = {e: 0 for e in ELEMENTS}, {m: 0 for m in MODES}
    for p in [n for n, _ in WPLANETS] + []:
        s = sign_of(pos[p]["lon"])
        count_el[ELEMENTS[s % 4]] += 1
        count_mo[MODES[s % 3]] += 1
    count_el[ELEMENTS[asc_sign % 4]] += 1
    count_mo[MODES[asc_sign % 3]] += 1
    now_jd = dt_to_jd(now_utc)
    tp = tropical_positions(now_jd)
    natal_targets = [(n, pos[n]["lon"], 0.0) for n in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")] \
        + [("Ascendant", asc, 0.0), ("Midheaven", mc, 0.0)]
    hits = []
    for tn in ("Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
        scale = 0.375 if tn == "Mars" else 0.4375  # ~3 deg (2 deg for Mars) on the 8-deg base orb
        for r in aspects_between([(tn, tp[tn]["lon"], tp[tn]["speed"])], natal_targets, use_motion=True, max_orb_scale=scale):
            if r["aspect"] == "quincunx":
                continue
            ang = {"conjunction": 0, "opposition": 180, "trine": 120, "square": 90, "sextile": 60}[r["aspect"]]
            nat = next(l for n_, l, _ in natal_targets if n_ == r["b"])
            pid = dict(WPLANETS)[tn]
            hits.append({"transit": r["a"], "natal": r["b"], "aspect": r["aspect"], "orb": r["orb"],
                         "applying": r.get("applying"),
                         "exact_dates": exact_transit_dates(pid, nat, ang, now_jd, tp[tn]["lon"])})
    age = (now_utc - birth_utc).days / 365.2425
    prog_jd = jd + age
    pp = tropical_positions(prog_jd)
    arc = wrap180(pp["Sun"]["lon"] - pos["Sun"]["lon"])
    directed = {"Ascendant": n360(asc + arc), "Midheaven": n360(mc + arc)}
    arc_hits = []
    for dn, dl in directed.items():
        for n, l, _ in natal_targets:
            o = abs(wrap180(dl - l))
            for an, ang, _ in ASPECTS[:5]:
                if abs(o - ang) <= 1.0:
                    arc_hits.append({"directed": dn, "natal": n, "aspect": an, "orb": round(abs(o - ang), 3)})
    out = {
        "house_system": hsys, "warning": warn,
        "ascendant": {"dms": fmt_pos(asc), "sign": SIGNS[asc_sign]}, "midheaven": fmt_pos(mc),
        "planets": planets, "big_three": big3,
        "natal_aspects": natal_aspects[:40],
        "element_count": count_el, "modality_count": count_mo,
        "counts_note": "Ten planets plus the Ascendant, one point each.",
        "transits_now": {"date": now_utc.date().isoformat(),
                         "positions": {p: {"pos": fmt_pos(v["lon"]), "retrograde": bool(v["speed"] < 0) if p not in ("Sun", "Moon") else False}
                                       for p, v in tp.items()},
                         "hits_to_natal": sorted(hits, key=lambda h: h["orb"])},
        "returns": {
            "saturn_returns": _find_crossings(pos["Saturn"]["lon"], swe.SATURN, jd, jd + 90 * 365.25, 5.0, min_age_years=20),
            "jupiter_returns": _find_crossings(pos["Jupiter"]["lon"], swe.JUPITER, jd, jd + 96 * 365.25, 4.0, min_age_years=8),
        },
        "secondary_progressions": {
            "progressed_date_utc": jd_to_dt(prog_jd).strftime("%Y-%m-%d %H:%M"),
            "planets": {p: fmt_pos(pp[p]["lon"]) for p in ("Sun", "Moon", "Mercury", "Venus", "Mars")},
            "note": "Progressed angles are not computed; see solar arc below."},
        "solar_arc": {"arc_degrees": round(arc, 3), "directed_angles": {k: fmt_pos(v) for k, v in directed.items()},
                      "hits_within_1_degree": arc_hits},
        "extra_points": extra_points(jd, pos, cusps, asc, mc, vertex, asc_sign),
        "lunar_returns": lunar_returns(pos["Moon"]["lon"], dt_to_jd(now_utc), 13,
                                       cur_lat if cur_lat is not None else lat, cur_lon if cur_lon is not None else lon),
        "hellenistic": hellenistic(pos, asc, birth_utc, now_utc),
        "solar_return": solar_return_tropical(pos["Sun"]["lon"], birth_utc, int(age),
                                              cur_lat if cur_lat is not None else lat,
                                              cur_lon if cur_lon is not None else lon),
    }
    out["_points"] = [(p, v["lon"], v["speed"]) for p, v in pos.items()]
    out["_angles"] = {"Ascendant": asc, "Midheaven": mc}
    out["_asc_sign"] = asc_sign
    return out


# ------------------------------------------------------------------ extra points and fixed stars
EXTRA_BODIES = [("Chiron", swe.CHIRON, 5.0), ("Ceres", swe.CERES, 2.0), ("Pallas", swe.PALLAS, 2.0),
                ("Juno", swe.JUNO, 2.0), ("Vesta", swe.VESTA, 2.0), ("Black Moon Lilith", swe.MEAN_APOG, 3.0)]
MAJOR = [a for a in ASPECTS if a[0] != "quincunx"]
STARS = ["Regulus", "Spica", "Aldebaran", "Antares", "Fomalhaut", "Algol", "Sirius", "Arcturus", "Vega", "Capella",
         "Pollux", "Castor", "Procyon", "Betelgeuse", "Rigel", "Deneb Algedi", "Alcyone", "Achernar", "Canopus", "Zuben Elgenubi"]
STAR_ORB = 1.0


def extra_points(jd, pos, cusps, asc, mc, vertex, asc_sign):
    """Chiron, Ceres, Pallas, Juno, Vesta, Black Moon Lilith (mean apogee), South Node, Part of Fortune (sect-aware)
    and Vertex, with their aspects to the planets and angles, plus fixed-star conjunctions (ecliptic longitude, 1 deg)."""
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED
    pts, orbs, missing = {}, {}, []

    def rec(l, speed=None):
        sgn = sign_of(l)
        return {"lon": round(l, 5), "sign": SIGNS[sgn], "dms": dms(deg_in_sign(l)),
                "house_placidus": _house_by_cusps(l, cusps), "house_whole_sign": (sgn - asc_sign) % 12 + 1,
                "retrograde": bool(speed < 0) if speed is not None else None}
    for name, pid, orb in EXTRA_BODIES:
        try:
            xx, rf = swe.calc_ut(jd, pid, fl)
            if pid != swe.MEAN_APOG and not (rf & swe.FLG_SWIEPH):
                raise RuntimeError("asteroid file not loaded")
            pts[name], orbs[name] = rec(xx[0], xx[3] if pid != swe.MEAN_APOG else None), orb
        except Exception as e:  # e.g. seas_*.se1 missing: say so rather than fall back silently
            missing.append(f"{name}: {e}")
    nn = pos["North Node"]["lon"]
    pts["South Node"], orbs["South Node"] = rec(n360(nn + 180)), 3.0
    sun, moon = pos["Sun"]["lon"], pos["Moon"]["lon"]
    day = n360(sun - asc) >= 180
    pof = n360(asc + moon - sun) if day else n360(asc + sun - moon)
    pts["Part of Fortune"], orbs["Part of Fortune"] = rec(pof), 3.0
    pts["Vertex"], orbs["Vertex"] = rec(vertex), 2.0
    targets = [(n, pos[n]["lon"]) for n, _ in WPLANETS] + [("Ascendant", asc), ("Midheaven", mc)]
    asp = []
    for name, p in pts.items():
        for tn, tl in targets:
            sep = abs(wrap180(tl - p["lon"]))
            for an, ang, _ in (MAJOR if name != "South Node" else MAJOR[:1]):
                o = abs(sep - ang)
                if o <= orbs[name]:
                    asp.append({"point": name, "to": tn, "aspect": an, "orb": round(o, 3)})
    stars, star_missing = [], None
    natal = targets + [(n, v["lon"]) for n, v in pts.items() if n in ("Part of Fortune",)]
    for st in STARS:
        try:
            xx, nm, _ = swe.fixstar2_ut(st, jd, swe.FLG_SWIEPH)
        except Exception as e:
            star_missing = f"fixed stars not computed: {e}"
            break
        for tn, tl in natal:
            o = abs(wrap180(tl - xx[0]))
            if o <= STAR_ORB:
                stars.append({"star": nm.split(",")[0], "star_position": fmt_pos(xx[0]), "conjunct": tn, "orb": round(o, 3),
                              "magnitude": round(swe.fixstar2_mag(st)[0], 2)})
    return {"points": pts, "aspects": sorted(asp, key=lambda r: r["orb"]),
            "fixed_star_conjunctions": sorted(stars, key=lambda r: r["orb"]),
            "conventions": {"lilith": "mean lunar apogee (Black Moon Lilith)", "part_of_fortune": "sect-aware (day: Asc + Moon - Sun; night: reversed)",
                            "orbs_deg": orbs, "aspects": "conjunction, opposition, trine, square, sextile (South Node: conjunction only)",
                            "fixed_stars": f"{len(STARS)} classic stars, ecliptic-longitude conjunction within {STAR_ORB} deg; parans not computed"},
            "not_computed": missing + ([star_missing] if star_missing else [])}


# ------------------------------------------------------------------ relationship charts and lunar returns
def _mid(a, b):
    """Nearer midpoint of two longitudes."""
    d = wrap180(b - a)
    return n360(a + d / 2)


def composite(a_pts, b_pts, a_angles, b_angles):
    """Midpoint composite: each point at the nearer midpoint of the two natal positions. The composite
    Ascendant here is the midpoint of the two Ascendants (stated; the derived-Ascendant method is not used)."""
    A = {n: l for n, l, _ in a_pts}
    B = {n: l for n, l, _ in b_pts}
    pts = {n: _mid(A[n], B[n]) for n in A if n in B}
    asc = _mid(a_angles["Ascendant"], b_angles["Ascendant"])
    mc = _mid(a_angles["Midheaven"], b_angles["Midheaven"])
    asc_sign = sign_of(asc)
    planets = {n: {"lon": round(l, 4), "position": fmt_pos(l), "house_whole_sign": (sign_of(l) - asc_sign) % 12 + 1} for n, l in pts.items()}
    lst = [(n, l, 0.0) for n, l in pts.items()] + [("Ascendant", asc, 0.0), ("Midheaven", mc, 0.0)]
    asp = aspects_between(lst, lst, same=True, use_motion=False, max_orb_scale=0.75)
    el = {e: 0 for e in ELEMENTS}
    for n, l in pts.items():
        if n != "North Node":
            el[ELEMENTS[sign_of(l) % 4]] += 1
    return {"method": "midpoint composite (nearer midpoints); Ascendant and Midheaven as midpoints of the natal angles",
            "ascendant": fmt_pos(asc), "midheaven": fmt_pos(mc), "planets": planets,
            "aspects": [a for a in asp if not (a["a"] in ("Ascendant", "Midheaven") and a["b"] in ("Ascendant", "Midheaven"))][:20],
            "element_count": el}


def davison(jd_a, lat_a, lon_a, jd_b, lat_b, lon_b):
    """Davison relationship chart: a real chart for the midpoint in time and the midpoint in space."""
    import math
    jd = (jd_a + jd_b) / 2
    lat = (lat_a + lat_b) / 2
    x = math.cos(math.radians(lon_a)) + math.cos(math.radians(lon_b))
    y = math.sin(math.radians(lon_a)) + math.sin(math.radians(lon_b))
    lon = math.degrees(math.atan2(y, x))
    pos = tropical_positions(jd)
    cusps, asc, mc, hsys, warn = tropical_angles(jd, lat, lon)
    asc_sign = sign_of(asc)
    planets = {p: {"position": fmt_pos(v["lon"]), "house_placidus": _house_by_cusps(v["lon"], cusps),
                   "house_whole_sign": (sign_of(v["lon"]) - asc_sign) % 12 + 1} for p, v in pos.items()}
    pts = [(p, v["lon"], v["speed"]) for p, v in pos.items()] + [("Ascendant", asc, 0.0), ("Midheaven", mc, 0.0)]
    asp = aspects_between(pts, pts, same=True)
    return {"method": "Davison: midpoint of the two birth moments (UT) and of the two birthplaces (mean latitude, circular mean longitude)",
            "moment_utc": jd_to_dt(jd).strftime("%Y-%m-%d %H:%M"), "place": {"lat": round(lat, 4), "lon": round(lon, 4)},
            "house_system": hsys, "warning": warn, "ascendant": fmt_pos(asc), "midheaven": fmt_pos(mc), "planets": planets,
            "aspects": [a for a in asp if not (a["a"] in ("Ascendant", "Midheaven") and a["b"] in ("Ascendant", "Midheaven"))][:20]}


def lunar_returns(natal_moon, start_jd, n, lat, lon):
    """The next n tropical lunar returns from start_jd, each cast for the given place."""
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED
    out, j = [], start_jd
    for _ in range(n):
        # step to the next crossing of the natal Moon longitude
        d = lambda t: wrap180(swe.calc_ut(t, swe.MOON, fl)[0][0] - natal_moon)  # noqa: E731
        t, prev = j, d(j)
        while True:
            t2 = t + 0.5
            cur = d(t2)
            if prev < 0 <= cur:
                break
            t, prev = t2, cur
        a, b = t, t2
        for _ in range(40):
            m = (a + b) / 2
            if d(m) < 0:
                a = m
            else:
                b = m
        jr = (a + b) / 2
        cusps, asc, mc, hsys, _ = tropical_angles(jr, lat, lon)
        moon_l = swe.calc_ut(jr, swe.MOON, fl)[0][0]
        out.append({"utc": jd_to_dt(jr).strftime("%Y-%m-%d %H:%M"), "ascendant": fmt_pos(asc), "ascendant_sign": SIGNS[sign_of(asc)],
                    "moon_house_placidus": _house_by_cusps(moon_l, cusps), "house_system": hsys})
        j = jr + 20
    return {"method": "tropical lunar returns (Moon back at its natal longitude), cast for the place given", "returns": out}


KEY_PAIRS = {frozenset(("Venus", "Mars")), frozenset(("Sun", "Moon")), frozenset(("Moon",)),
             frozenset(("Sun",)), frozenset(("Venus",)), frozenset(("Mars",))}


def synastry(a_pts, b_pts, a_angles, b_angles, a_asc_sign, b_asc_sign):
    A = list(a_pts) + [(k, v, 0.0) for k, v in a_angles.items()]
    B = list(b_pts) + [(k, v, 0.0) for k, v in b_angles.items()]
    inter = aspects_between(A, B, use_motion=False, max_orb_scale=0.75)
    keyed = []
    for r in inter:
        pair = {r["a"], r["b"]}
        tag = None
        if pair == {"Venus", "Mars"}:
            tag = "Venus-Mars (attraction)"
        elif r["a"] == "Moon" and r["b"] == "Moon":
            tag = "Moon-Moon (emotional fit)"
        elif pair == {"Sun", "Moon"}:
            tag = "Sun-Moon (core compatibility)"
        elif "Saturn" in pair and pair & {"Sun", "Moon", "Venus", "Mars", "Ascendant"}:
            tag = "Saturn contact (commitment / restriction)"
        elif r["a"] == "Venus" and r["b"] == "Venus":
            tag = "Venus-Venus (values)"
        if tag:
            keyed.append({**r, "significance": tag})
    overlay_a_in_b = {p: (sign_of(l) - b_asc_sign) % 12 + 1 for p, l, _ in a_pts}
    overlay_b_in_a = {p: (sign_of(l) - a_asc_sign) % 12 + 1 for p, l, _ in b_pts}
    return {"key_aspects": keyed, "all_interaspects": inter[:60],
            "house_overlay_A_in_B_whole_sign": overlay_a_in_b,
            "house_overlay_B_in_A_whole_sign": overlay_b_in_a}
