"""forecast.py - five-year (configurable) timing layer, starting on the report date.

Every date here is computed from the Swiss Ephemeris or from exact period arithmetic. Nothing is estimated.
The life-area tagging at the end is a fixed, published screening rule (references/forecast_method.md),
not a prediction score.
"""
import datetime as dt

import swisseph as swe

import chinese
import numerology as num
import vedic
import western
from common import SIGNS, SIGN_LORD, VIM_ORDER, NAK_SPAN, n360, sign_of, wrap180, jd_to_dt, dt_to_jd, fmt_pos

ISO = lambda d: d.date().isoformat()  # noqa: E731


# ------------------------------------------------------------------ window
def add_years(d, k):
    try:
        return d.replace(year=d.year + k)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + k, day=28)


def make_window(start, years):
    slices = []
    for k in range(years):
        a, b = add_years(start, k), add_years(start, k + 1)
        slices.append({"id": f"Y{k + 1}", "from": ISO(a), "to": ISO(b - dt.timedelta(days=1)), "_a": a, "_b": b})
    return {"start": ISO(start), "end": ISO(add_years(start, years) - dt.timedelta(days=1)), "years": years}, slices


def overlaps(a_from, a_to, s):
    """ISO strings or datetimes; s is a slice dict."""
    sa, sb = s["from"], s["to"]
    return str(a_from)[:10] <= sb and str(a_to)[:10] >= sa


def in_slice(d, s):
    return s["from"] <= str(d)[:10] <= s["to"]


# ------------------------------------------------------------- root finder
def _refine(f, a, b, it=40):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


def sign_segments(lon_fn, j0, j1, step):
    """Contiguous segments of constant sign for a body whose longitude is lon_fn(jd). Retrograde re-entries are kept as separate segments."""
    segs, j, s = [], j0, sign_of(lon_fn(j0))
    start = j0
    while j < j1:
        j2 = min(j + step, j1)
        s2 = sign_of(lon_fn(j2))
        if s2 != s:
            a, b = j, j2
            for _ in range(40):
                m = (a + b) / 2
                if sign_of(lon_fn(m)) == s:
                    a = m
                else:
                    b = m
            edge = (a + b) / 2
            segs.append((start, edge, s))
            start, s = edge, sign_of(lon_fn(b))
        j = j2
    segs.append((start, j1, s))
    return segs


# ================================================================== VEDIC
VIM_LEN = dict(VIM_ORDER)
JUP_GOOD = {2: 12, 5: 4, 7: 3, 9: 10, 11: 8}          # favourable house from Moon -> vedha house (Phaladeepika)
SAT_GOOD = {3: 12, 6: 9, 11: 5}
NODE_GOOD = {3: 12, 6: 9, 11: 5}
ASPECT_OFFS = {"Jupiter": (4, 6, 8), "Saturn": (2, 6, 9), "Rahu": (), "Ketu": ()}
KENDRA_TRIKONA = {1, 4, 5, 7, 9, 10}
DUSTHANA = {6, 8, 12}


def _owned_houses(planet, lag):
    return [h for h in range(1, 13) if SIGN_LORD[(lag + h - 1) % 12] == planet]


def dasha_window(order, total, start_idx, frac, birth, ws, we, year_days, planet_of=None):
    n = len(order)
    virt = birth - dt.timedelta(days=order[start_idx][1] * frac * year_days)
    t, i, rows = virt, start_idx, []
    while t < we:
        lord, yrs = order[i % n]
        ln = yrs * year_days
        t_end = t + dt.timedelta(days=ln)
        if t_end > ws:
            for ai, alord, a0, a1 in vedic.subdivide(t, ln, order, i % n, total):
                if a1 <= ws or a0 >= we:
                    continue
                row = {"maha": lord, "antar": alord, "from": ISO(max(a0, birth)), "to": ISO(a1),
                       "_maha_from": ISO(max(t, birth)), "_maha_to": ISO(t_end)}
                if planet_of:
                    row["maha_planet"], row["antar_planet"] = planet_of[lord], planet_of[alord]
                else:
                    plen = (a1 - a0).total_seconds() / 86400.0
                    row["pratyantars"] = [{"lord": p[1], "from": ISO(p[2]), "to": ISO(p[3])}
                                          for p in vedic.subdivide(a0, plen, order, ai, total) if p[3] > ws and p[2] < we]
                rows.append(row)
        t, i = t_end, i + 1
    return rows


def _lord_info(p, planets, lag, bav, sav):
    """Strength of a dasha lord by its own Bhinna bindus in the sign it occupies (4+ supports) and that sign's Sarva total.
    (A planet's Bhinna total is a constant - 48/49/39/54/56/52/39 - so it cannot rate a chart and is not used.)"""
    if p not in planets:
        return None
    sg = planets[p]["sign"]
    own = bav[p][sg] if p in bav else None
    sv = sav[sg]
    if own is None:
        band = "strong" if sv >= 30 else "good" if sv >= 28 else "moderate" if sv >= 25 else "weak"
    else:
        band = "strong" if own >= 5 and sv >= 28 else "good" if own >= 4 else "moderate" if own == 3 or sv >= 28 else "weak"
    return {"house": planets[p]["house"], "sign": sg, "owns": _owned_houses(p, lag),
            "dignity": planets[p].get("dignity"), "own_bindus_in_sign": own, "sarva_of_sign": sv, "strength_band": band}


def vedic_forecast(v, birth_utc, jd_birth, ws, we, slices, lat, lon, ayan, node):
    planets, lag = v["planets"], v["_lag_sign"]
    moon_sign = planets["Moon"]["sign_index"]
    bav = v["ashtakavarga"]["bhinna"]
    sav = v["ashtakavarga"]["sarva"]
    yd = v["conventions"]["vimshottari_year_days"]
    pos = vedic.sidereal_positions(jd_birth, ayan, node)
    mlon = pos["Moon"]["lon"]
    ni = int(n360(mlon) // NAK_SPAN)
    frac = (n360(mlon) % NAK_SPAN) / NAK_SPAN
    vim = dasha_window(VIM_ORDER, 120, ni % 9, frac, birth_utc, ws, we, yd)
    for r in vim:
        mi, ai = _lord_info(r["maha"], planets, lag, bav, sav), _lord_info(r["antar"], planets, lag, bav, sav)
        r["maha_lord"], r["antar_lord"] = mi, ai
        r["antar_from_maha"] = (planets[r["antar"]]["sign_index"] - planets[r["maha"]]["sign_index"]) % 12 + 1
    yog = dasha_window(vedic.YOGINI_ORDER, 36, (ni + 3) % 8, frac, birth_utc, ws, we, yd, vedic.YOGINI_PLANET)

    # gochar ingress segments (sidereal), from slightly before the window so the starting sign is known
    swe.set_sid_mode(vedic.AYAN[ayan])
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    node_id = swe.MEAN_NODE if node == "mean" else swe.TRUE_NODE
    j0, j1 = dt_to_jd(ws), dt_to_jd(we)
    fns = {"Jupiter": lambda j: (swe.set_sid_mode(vedic.AYAN[ayan]), swe.calc_ut(j, swe.JUPITER, fl)[0][0])[1],
           "Saturn": lambda j: (swe.set_sid_mode(vedic.AYAN[ayan]), swe.calc_ut(j, swe.SATURN, fl)[0][0])[1],
           "Rahu": lambda j: (swe.set_sid_mode(vedic.AYAN[ayan]), swe.calc_ut(j, node_id, fl)[0][0])[1]}
    fns["Ketu"] = lambda j: n360(fns["Rahu"](j) + 180)
    raw = {p: sign_segments(f, j0, j1, 1.0) for p, f in fns.items()}
    good = {"Jupiter": JUP_GOOD, "Saturn": SAT_GOOD, "Rahu": NODE_GOOD, "Ketu": NODE_GOOD}

    def sign_at(p, j):
        for a, b, s in raw[p]:
            if a <= j <= b:
                return s
        return sign_of(fns[p](j))
    gochar = {}
    for p, segs in raw.items():
        out = []
        for a, b, s in segs:
            hm = (s - moon_sign) % 12 + 1
            rec = {"sign": SIGNS[s], "from": ISO(jd_to_dt(a)), "to": ISO(jd_to_dt(b)),
                   "starts_before_window": a <= j0 + 1e-6, "runs_past_window": b >= j1 - 1e-6,
                   "house_from_lagna": (s - lag) % 12 + 1, "house_from_moon": hm,
                   "sarva_bindus": sav[SIGNS[s]],
                   "aspects_houses_from_lagna": sorted(((s + o - lag) % 12) + 1 for o in ASPECT_OFFS[p]),
                   "aspects_houses_from_moon": sorted(((s + o - moon_sign) % 12) + 1 for o in ASPECT_OFFS[p]),
                   "classically_favourable_from_moon": hm in good[p]}
            if p in bav:
                rec["own_bindus"] = bav[p][SIGNS[s]]
            if hm in good[p]:
                vh = good[p][hm]
                mid = (a + b) / 2
                blockers = [q for q in fns if q != p and {p, q} != {"Rahu", "Ketu"}
                            and (sign_at(q, mid) - moon_sign) % 12 + 1 == vh]
                rec["vedha_house_from_moon"] = vh
                rec["vedha_by_slow_planet_at_midpoint"] = blockers
            out.append(rec)
        gochar[p] = out

    # double transit: exact, from the Jupiter and Saturn segment boundaries
    cuts = sorted({j0, j1} | {a for a, _, _ in raw["Jupiter"] + raw["Saturn"]} | {b for _, b, _ in raw["Jupiter"] + raw["Saturn"]})
    dt_runs = {"from_moon": {}, "from_lagna": {}}
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-6:
            continue
        mid = (a + b) / 2
        J, S = sign_at("Jupiter", mid), sign_at("Saturn", mid)
        act = {J, (J + 4) % 12, (J + 6) % 12, (J + 8) % 12} & {S, (S + 2) % 12, (S + 6) % 12, (S + 9) % 12}
        for ref, base in (("from_moon", moon_sign), ("from_lagna", lag)):
            for sg in act:
                h = (sg - base) % 12 + 1
                runs = dt_runs[ref].setdefault(h, [])
                if runs and abs(runs[-1][1] - a) < 1e-6:
                    runs[-1][1] = b
                else:
                    runs.append([a, b])
    double_transit = {ref: {str(h): [{"from": ISO(jd_to_dt(a)), "to": ISO(jd_to_dt(b))} for a, b in runs]
                            for h, runs in sorted(d.items())} for ref, d in dt_runs.items()}

    # Saturn pressure periods from Moon
    shani = []
    for r in gochar["Saturn"]:
        h = r["house_from_moon"]
        kind = {12: "Sade Sati - rising phase", 1: "Sade Sati - peak phase", 2: "Sade Sati - setting phase",
                8: "Ashtama Shani", 4: "Kantaka Shani (4th)", 7: "Kantaka Shani (7th)", 10: "Kantaka Shani (10th)"}.get(h)
        if kind:
            shani.append({"kind": kind, "from": r["from"], "to": r["to"], "own_bindus": r.get("own_bindus")})

    # Varshaphal for every birthday year touching the window
    age0 = vedic.completed_varsha_years(pos["Sun"]["lon"], birth_utc, ws, ayan)
    age1 = vedic.completed_varsha_years(pos["Sun"]["lon"], birth_utc, we, ayan)
    varsha = []
    for age in range(age0, age1 + 1):
        vp = vedic.varshaphal(pos["Sun"]["lon"], lag, birth_utc, age, lat, lon, ayan)
        jd_r = dt_to_jd(dt.datetime.strptime(vp["return_utc"], "%Y-%m-%d %H:%M:%S"))
        vl = SIGNS.index(vp["varsha_lagna_sign"])
        mh = vp["muntha_house"]
        swe.set_sid_mode(vedic.AYAN[ayan])
        sun_trop = swe.calc_ut(jd_r, swe.SUN, swe.FLG_SWIEPH)[0]
        alt = swe.azalt(jd_r, swe.ECL2HOR, (lon, lat, 0), 0, 10, (sun_trop[0], sun_trop[1], sun_trop[2]))[1]
        is_day = alt > -0.833
        rs = vedic.sidereal_positions(jd_r, ayan, node)
        dr = SIGN_LORD[sign_of(rs["Sun"]["lon"])] if is_day else SIGN_LORD[sign_of(rs["Moon"]["lon"])]
        nxt = vedic.varshaphal(pos["Sun"]["lon"], lag, birth_utc, age + 1, lat, lon, ayan)["return_utc"][:10]
        varsha.append({"age": age, "from": vp["return_utc"][:10], "to": nxt, "return_utc": vp["return_utc"],
                       "varsha_lagna": vp["varsha_lagna"], "varsha_lagna_sign": vp["varsha_lagna_sign"],
                       "muntha_sign": vp["muntha_sign"], "muntha_house": mh,
                       "muntha_tone": "favourable" if mh in (1, 2, 3, 5, 9, 10, 11) else "difficult",
                       "day_or_night_return": "day" if is_day else "night",
                       "varshesha_candidates": {"muntha_lord": SIGN_LORD[SIGNS.index(vp["muntha_sign"])],
                                                "natal_lagna_lord": SIGN_LORD[lag], "varsha_lagna_lord": SIGN_LORD[vl],
                                                "dina_ratri_pati": dr},
                       "planets": vp["planets"]})
    return {"vimshottari_antardashas": vim, "yogini_antardashas": yog, "gochar_segments": gochar,
            "double_transit": double_transit, "saturn_from_moon": shani, "varshaphal_years": varsha,
            "conventions": {"gochar": f"sidereal {ayan}, {node} node; segments split at every sign change incl. retrograde re-entries",
                            "aspects": "Jupiter 5/7/9, Saturn 3/7/10 (whole sign); node aspects not used",
                            "vedha": "Phaladeepika table; only obstruction by Jupiter, Saturn, Rahu or Ketu at segment midpoint is checked",
                            "double_transit": "house occupied or aspected by both Jupiter and Saturn, judged from Moon and from Lagna",
                            "varshaphal": "sidereal solar return cast for the birthplace (PVR 27.1), even when a current city is supplied; Tri-rashi pati and Varshesha selection not computed",
                            "dasha_lord_strength": "own Bhinna bindus in the occupied sign (4+ supports) with that sign's Sarva total; Rahu and Ketu by Sarva only"}}


def _zr_peak(sg, fsign):
    h = (sg - fsign) % 12 + 1
    return {1: "major peak", 10: "major peak", 7: "moderate peak", 4: "minor peak"}.get(h)


def zr_periods(lot, fsign, birth_utc, ws, we):
    """Zodiacal releasing L1 and L2 (Valens): L1 in 360-day years, L2 in 30-day months, loosing of the bond after
    twelve L2 periods jumps to the sign opposite the L1 sign. Returns L1 periods overlapping [ws, we) with their L2 periods."""
    out, t, s = [], birth_utc, sign_of(lot)
    while t < we:
        yrs = western.ZR_YEARS[s]
        t_end = t + dt.timedelta(days=yrs * 360)
        if t_end > ws:
            sub, u, k, cnt, lb_done = [], t, s, 0, False
            while u < t_end:
                lb = False
                if cnt == 12 and not lb_done:
                    k, lb_done, lb = (s + 6) % 12, True, True
                u_end = min(u + dt.timedelta(days=western.ZR_YEARS[k] * 30), t_end)
                if u_end > ws and u < we:
                    sub.append({"sign": SIGNS[k], "ruler": SIGN_LORD[k], "from": ISO(u), "to": ISO(u_end),
                                "peak": _zr_peak(k, fsign), "loosing_of_the_bond": lb})
                u, k, cnt = u_end, (k + 1) % 12, cnt + 1
            out.append({"level1_sign": SIGNS[s], "level1_ruler": SIGN_LORD[s], "level1_from": ISO(t), "level1_to": ISO(t_end),
                        "level1_peak": _zr_peak(s, fsign), "level2": sub})
        t, s = t_end, (s + 1) % 12
    return out


# ================================================================ WESTERN
OUTERS = [("Jupiter", swe.JUPITER, 1.0), ("Saturn", swe.SATURN, 2.0), ("Uranus", swe.URANUS, 3.0),
          ("Neptune", swe.NEPTUNE, 4.0), ("Pluto", swe.PLUTO, 4.0)]
W_ASPECTS = [("conjunction", 0), ("opposition", 180), ("square", 90), ("square", 270),
             ("trine", 120), ("trine", 240), ("sextile", 60), ("sextile", 300)]


def _trop(pid):
    fl = swe.FLG_SWIEPH | swe.FLG_SPEED
    return lambda j: swe.calc_ut(j, pid, fl)[0][0]


def western_forecast(w, jd_birth, birth_utc, ws, we, lat, lon):
    pts = {n: l for n, l, _ in w["_points"]}
    natal = {k: pts[k] for k in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")}
    natal["Ascendant"], natal["Midheaven"] = w["_angles"]["Ascendant"], w["_angles"]["Midheaven"]
    asc_sign = w["_asc_sign"]
    j0, j1 = dt_to_jd(ws), dt_to_jd(we)
    hits, ingresses = [], []
    for name, pid, step in OUTERS:
        f = _trop(pid)
        grid = []
        j = j0 - step
        while j <= j1 + step:
            grid.append((j, f(j)))
            j += step
        for tname, tl in natal.items():
            if tname in ("Uranus", "Neptune", "Pluto") and name in ("Uranus", "Neptune", "Pluto"):
                continue  # generational contacts
            for asp, ang in W_ASPECTS:
                if asp == "sextile" and name not in ("Jupiter", "Saturn"):
                    continue
                target = n360(tl + ang)
                d = lambda jj: wrap180(f(jj) - target)  # noqa: E731
                found = []
                for (ja, la), (jb, lb) in zip(grid, grid[1:]):
                    da, db = wrap180(la - target), wrap180(lb - target)
                    if da == 0:
                        found.append(ja)
                    elif da * db < 0 and abs(da) < 20 and abs(db) < 20:
                        found.append(_refine(d, ja, jb))
                found = [x for x in found if j0 <= x <= j1]
                if not found:
                    continue
                groups = []
                for x in found:
                    if groups and x - groups[-1][-1] < 600:
                        groups[-1].append(x)
                    else:
                        groups.append([x])
                for g in groups:
                    hits.append({"transit": name, "natal": tname, "aspect": asp,
                                 "exact_dates": [ISO(jd_to_dt(x)) for x in g],
                                 "passes": len(g)})
        for a, b, s in sign_segments(f, j0, j1, step):
            ingresses.append({"planet": name, "sign": SIGNS[s], "house_whole_sign": (s - asc_sign) % 12 + 1,
                              "from": ISO(jd_to_dt(a)), "to": ISO(jd_to_dt(b)),
                              "starts_before_window": a <= j0 + 1e-6})
    hits.sort(key=lambda h: h["exact_dates"][0])

    # profections and solar returns per birthday year
    age0 = int((ws - birth_utc).days // 365.2425)
    age1 = int((we - birth_utc).days // 365.2425)
    years = []
    for age in range(age0, age1 + 1):
        s = (asc_sign + age) % 12
        sr = western.solar_return_tropical(pts["Sun"], birth_utc, age, lat, lon)
        nxt = western.solar_return_tropical(pts["Sun"], birth_utc, age + 1, lat, lon)["return_utc"][:10]
        angular = sorted(p for p, r in sr["planets"].items() if r["house"] in (1, 4, 7, 10))
        years.append({"age": age, "from": sr["return_utc"][:10], "to": nxt,
                      "profected_house": age % 12 + 1, "profected_sign": SIGNS[s], "year_lord": SIGN_LORD[s],
                      "solar_return": {"return_utc": sr["return_utc"], "ascendant": sr["ascendant"], "midheaven": sr["midheaven"],
                                       "sun_house": sr["planets"]["Sun"]["house"], "angular_planets": angular,
                                       "house_system": sr["house_system"]}})

    # progressed Moon (secondary progressions: 1 day = 1 year)
    yr = 365.2425
    pj = lambda real_jd: jd_birth + (real_jd - jd_birth) / yr  # noqa: E731
    pm = lambda real_jd: swe.calc_ut(pj(real_jd), swe.MOON, swe.FLG_SWIEPH)[0][0]  # noqa: E731
    psun = lambda real_jd: swe.calc_ut(pj(real_jd), swe.SUN, swe.FLG_SWIEPH)[0][0]  # noqa: E731
    pmoon = [{"sign": SIGNS[s], "house_whole_sign": (s - asc_sign) % 12 + 1, "from": ISO(jd_to_dt(a)), "to": ISO(jd_to_dt(b))}
             for a, b, s in sign_segments(pm, j0, j1, 5.0)]
    lunations = []
    for phase, ang in (("progressed New Moon", 0), ("progressed First Quarter", 90),
                       ("progressed Full Moon", 180), ("progressed Last Quarter", 270)):
        e = lambda jj, ang=ang: wrap180(pm(jj) - psun(jj) - ang)  # noqa: E731
        j, prev = j0 - 8 * 365.25, e(j0 - 8 * 365.25)
        while j < j1:
            cur = e(j + 5)
            if prev * cur < 0 and abs(prev) < 30:
                lunations.append({"phase": phase, "date": ISO(jd_to_dt(_refine(e, j, j + 5)))})
            prev, j = cur, j + 5

    # zodiacal releasing L1 + L2
    pos = western.tropical_positions(jd_birth)
    asc = w["_angles"]["Ascendant"]
    sun, moon = pos["Sun"]["lon"], pos["Moon"]["lon"]
    is_day = n360(sun - asc) >= 180
    fortune = n360(asc + moon - sun) if is_day else n360(asc + sun - moon)
    spirit = n360(asc + sun - moon) if is_day else n360(asc + moon - sun)
    fsign = sign_of(fortune)

    def zr(lot):
        return zr_periods(lot, fsign, birth_utc, ws, we)

    # eclipses
    ecl = []
    natal_nodes = {**natal, "North Node": pts["North Node"], "South Node": n360(pts["North Node"] + 180)}
    j = j0
    while True:
        r, tret = swe.sol_eclipse_when_glob(j, swe.FLG_SWIEPH, 0)
        if tret[0] > j1:
            break
        ecl.append(("solar", tret[0], r))
        j = tret[0] + 20
    j = j0
    while True:
        r, tret = swe.lun_eclipse_when(j, swe.FLG_SWIEPH, 0)
        if tret[0] > j1:
            break
        ecl.append(("lunar", tret[0], r))
        j = tret[0] + 20
    eclipses = []
    for kind, jj, r in sorted(ecl, key=lambda x: x[1]):
        lon_e = _trop(swe.SUN if kind == "solar" else swe.MOON)(jj)
        typ = ("total" if r & swe.ECL_TOTAL else "annular" if r & getattr(swe, "ECL_ANNULAR", 0)
               else "hybrid" if r & getattr(swe, "ECL_ANNULAR_TOTAL", 0) else "partial" if r & swe.ECL_PARTIAL
               else "penumbral" if r & getattr(swe, "ECL_PENUMBRAL", 0) else "other")
        contacts = []
        for n_, l_ in natal_nodes.items():
            for an, ang in (("conjunction", 0), ("opposition", 180)):
                o = abs(wrap180(lon_e - l_ - ang))
                if o <= 3.0:
                    contacts.append({"natal": n_, "aspect": an, "orb": round(o, 2)})
        eclipses.append({"kind": kind, "type": typ, "max_utc": jd_to_dt(jj).strftime("%Y-%m-%d %H:%M"),
                         "date": ISO(jd_to_dt(jj)), "position_tropical": fmt_pos(lon_e),
                         "house_whole_sign": (sign_of(lon_e) - asc_sign) % 12 + 1,
                         "contacts_within_3deg": contacts})
    return {"transit_hits": hits, "outer_ingresses": ingresses, "birthday_years": years,
            "progressed_moon": {"segments": pmoon,
                                "lunations": sorted([x for x in lunations if x["date"] >= ISO(ws)], key=lambda x: x["date"]),
                                "last_lunation_before_window": max((x for x in lunations if x["date"] < ISO(ws)), key=lambda x: x["date"], default=None)},
            "zodiacal_releasing": {"from_spirit": zr(spirit), "from_fortune": zr(fortune),
                                   "lot_of_fortune_sign": SIGNS[fsign], "lot_of_spirit_sign": SIGNS[sign_of(spirit)],
                                   "sect": "day" if is_day else "night"},
            "eclipses": eclipses,
            "conventions": {"transits": "tropical; Jupiter-Pluto to natal Sun-Pluto, Ascendant and Midheaven; conjunction, square, opposition, trine "
                                        "(sextile for Jupiter and Saturn only); outer-to-outer generational contacts skipped; passes within 600 days grouped",
                            "houses": "whole-sign from the tropical Ascendant",
                            "progressions": "secondary, 1 day = 1 tropical year (365.2425 d)",
                            "zodiacal_releasing": "Valens minor years; L1 in 360-day years, L2 in 30-day months; loosing of the bond = jump to the sign "
                                                  "opposite the L1 sign after twelve L2 periods; peaks = signs angular to the Lot of Fortune",
                            "eclipses": "Swiss Ephemeris global eclipse search; contacts = conjunction or opposition within 3 degrees"}}


# =================================================================== BAZI
def bazi_forecast(b, birth_utc, ws, we):
    dm = b["_dm"]
    natal_b = [tuple(x) for x in b["_branches"]]
    natal_s = [tuple(x) for x in b["_stems"]]
    lps = b["luck_pillars"]["pillars"]
    shen = b["shen_sha_subset"]
    y0 = ws.year if ws >= jd_to_dt(chinese.term_jd(ws.year, 315)) else ws.year - 1
    y1 = we.year if we >= jd_to_dt(chinese.term_jd(we.year, 315)) else we.year - 1
    rows = []
    for Y in range(y0, y1 + 1):
        i = chinese.idx60((Y - 4) % 10, (Y - 4) % 12)
        li = jd_to_dt(chinese.term_jd(Y, 315))
        li_next = jd_to_dt(chinese.term_jd(Y + 1, 315))
        lp = next((x for x in lps if x["from"] <= ISO(li + dt.timedelta(days=180)) < x["to"]), None)
        base_b = list(natal_b)
        base_s = list(natal_s)
        if lp:
            lpi = chinese.idx60(chinese.STEMS.index(lp["stem"]), chinese.BRANCHES.index(lp["branch"]))
            base_b.append(("LuckPillar", lpi % 12))
            base_s.append(("LuckPillar", lpi % 10))

        def key(r):
            return (r["type"], tuple(r["between"]))
        before_b = {key(r) for r in chinese.branch_relations(base_b)}
        before_s = {key(r) for r in chinese.stem_relations(base_s)}
        br = [r for r in chinese.branch_relations(base_b + [("Annual", i % 12)]) if key(r) not in before_b]
        sr = [r for r in chinese.stem_relations(base_s + [("Annual", i % 10)]) if key(r) not in before_s]
        bch = chinese.BRANCHES[i % 12]
        rows.append({"bazi_year": Y, "from": ISO(li), "to": ISO(li_next - dt.timedelta(days=1)),
                     **chinese.gz(i), "ten_god_stem": chinese.ten_god(dm, i % 10),
                     "ten_god_branch_main": chinese.ten_god(dm, chinese.HIDDEN[i % 12][0]),
                     "luck_pillar": None if not lp else {"text": lp["text"], "from": lp["from"], "to": lp["to"], "ten_god_stem": lp["ten_god_stem"]},
                     "new_branch_relations": br, "new_stem_relations": sr,
                     "peach_blossom_year": bch in shen["peach_blossom"], "travelling_horse_year": bch in shen["travelling_horse"],
                     "void_branch_year": bch in shen["void_branches_day_xun"]})
    changes = [{"text": x["text"], "from": x["from"], "ten_god_stem": x["ten_god_stem"]} for x in lps if ISO(ws) < x["from"] <= ISO(we)]
    return {"annual": rows, "luck_pillar_changes_in_window": changes,
            "conventions": {"year": "Li Chun to Li Chun (astronomical instant, UTC date shown)",
                            "relations": "only relations that the annual pillar adds to natal + current luck pillar are listed",
                            "luck_pillar_for_year": "the luck pillar running at mid-year (Li Chun + 180 days)"}}


# ============================================================ NUMEROLOGY
def numerology_forecast(dob, ws, we):
    y, m, d = [int(x) for x in dob.split("-")]
    rd, rm, ry = num.reduce(d)[0], num.reduce(m)[0], num.reduce(y)[0]
    rows = []
    for Y in range(ws.year, we.year + 1):
        py = num.reduce(rd + rm + num.reduce(Y)[0])[0]
        rows.append({"year": Y, "from": f"{Y}-01-01", "to": f"{Y}-12-31", "personal_year": py,
                     "universal_year": num.reduce(Y)[0]})
    lp = num.reduce(rm + rd + ry)[0]
    lp1 = num.reduce(lp, False)[0]
    s = lambda n: num.reduce(n, False)[0]  # noqa: E731
    p1, p2 = num.reduce(rm + rd)[0], num.reduce(rd + ry)[0]
    p3, p4 = num.reduce(p1 + p2)[0], num.reduce(rm + ry)[0]
    c1, c2 = abs(s(rm) - s(rd)), abs(s(rd) - s(ry))
    c3, c4 = abs(c1 - c2), abs(s(rm) - s(ry))
    e1 = 36 - lp1
    ages = [(0, e1), (e1 + 1, e1 + 9), (e1 + 10, e1 + 18), (e1 + 19, None)]
    pinn = [{"n": k + 1, "pinnacle": p, "challenge": c, "from_age": a, "to_age": b,
             "from": f"{y + a}-{m:02d}-{d:02d}" if a else dob, "to": f"{y + b + 1}-{m:02d}-{d:02d}" if b is not None else None}
            for k, (p, c, (a, b)) in enumerate(zip((p1, p2, p3, p4), (c1, c2, c3, c4), ages))]
    return {"personal_years": rows, "pinnacles_and_challenges": pinn,
            "conventions": {"personal_year": "reduced birth day + reduced birth month + reduced calendar year; runs 1 Jan - 31 Dec; 11 and 22 kept",
                            "pinnacles": f"first pinnacle ends at age 36 - Life Path ({lp1}); then 9-year spans; ages are in completed years"}}


# ======================================================= life-area tags
AREAS = {
    "career": {"label": "Career and status", "houses": [10, 6, 11], "natal": ["Midheaven", "Sun", "Saturn"],
               "ten_gods": ["Direct Officer", "Seven Killings"], "palaces": ["Month"], "py": [1, 4, 8, 22], "zr": "spirit"},
    "money": {"label": "Money and assets", "houses": [2, 11], "natal": ["Jupiter", "Venus"],
              "ten_gods": ["Direct Wealth", "Indirect Wealth"], "palaces": [], "py": [8, 4], "zr": "fortune"},
    "love": {"label": "Love and marriage", "houses": [7, 5], "natal": ["Venus", "Ascendant"],
             "ten_gods": [], "palaces": ["Day"], "py": [2, 6], "zr": None},
    "family": {"label": "Family and home", "houses": [4, 2], "natal": ["Moon", "Midheaven"],
               "ten_gods": [], "palaces": ["Year", "Day"], "py": [6], "zr": None},
    "children": {"label": "Children and creativity", "houses": [5], "natal": ["Jupiter"],
                 "ten_gods": ["Eating God", "Hurting Officer"], "palaces": ["Hour"], "py": [3], "zr": None},
    "health": {"label": "Health and vitality", "houses": [1, 6, 8], "natal": ["Ascendant", "Sun", "Moon"],
               "ten_gods": [], "palaces": ["Day"], "py": [7], "zr": "fortune"},
    "travel": {"label": "Travel and relocation", "houses": [9, 12, 3], "natal": [],
               "ten_gods": [], "palaces": [], "py": [5], "zr": None},
    "learning": {"label": "Learning and spirituality", "houses": [9, 12, 5], "natal": ["Jupiter"],
                 "ten_gods": ["Direct Resource", "Indirect Resource"], "palaces": [], "py": [7, 9, 11], "zr": None},
}


def _step_down(t):
    return {"+": "~", "~": "-", "-": "-"}[t]


def tag_areas(F, v, w, gender, slices):
    planets, lag = v["planets"], v["_lag_sign"]
    asc_sign = w["_asc_sign"]
    out = {}
    for key, A in AREAS.items():
        hs = set(A["houses"])
        natal_targets = set(A["natal"]) | {SIGN_LORD[(asc_sign + h - 1) % 12] for h in A["houses"]}
        tg = list(A["ten_gods"])
        if key == "love":
            tg += ["Direct Officer", "Seven Killings"] if gender.upper().startswith("F") else ["Direct Wealth", "Indirect Wealth"]
        per = []
        for s in slices:
            ind = []
            # --- Vedic
            for r in F["vedic"]["vimshottari_antardashas"]:
                if not overlaps(r["from"], r["to"], s):
                    continue
                for role in ("maha", "antar"):
                    li = r[f"{role}_lord"]
                    if li and (hs & set(li["owns"]) or li["house"] in hs):
                        t = "+" if li["house"] in KENDRA_TRIKONA else "-" if li["house"] in DUSTHANA else "~"
                        if role == "antar" and r["antar_from_maha"] in DUSTHANA:
                            t = _step_down(t)
                        frm, to_ = (r["from"], r["to"]) if role == "antar" else (r["_maha_from"], r["_maha_to"])
                        lab = f"{r['maha']} mahadasha" if role == "maha" else f"{r['maha']}-{r['antar']} antardasha"
                        ind.append({"system": "Vedic", "tone": t, "from": frm, "to": to_,
                                    "text": f"{lab}: lord {r[role]} in H{li['house']}, owns {', '.join(map(str, li['owns'])) or '-'}"
                                            f" ({'BAV ' + str(li['own_bindus_in_sign']) + ', ' if li['own_bindus_in_sign'] is not None else ''}SAV {li['sarva_of_sign']}, {li['strength_band']})"})
            for p in ("Jupiter", "Saturn", "Rahu", "Ketu"):
                for g in F["vedic"]["gochar_segments"][p]:
                    if not overlaps(g["from"], g["to"], s):
                        continue
                    on = g["house_from_lagna"] in hs or g["house_from_moon"] in hs
                    asp = bool(hs & set(g["aspects_houses_from_lagna"]) or hs & set(g["aspects_houses_from_moon"]))
                    if not (on or asp):
                        continue
                    ob = g.get("own_bindus")
                    if p == "Jupiter":
                        t = "+" if (ob or 0) >= 4 else "~"
                    elif p == "Saturn":
                        t = "~" if (ob or 0) >= 4 else "-"
                    else:
                        t = "~"
                    if p in ("Rahu", "Ketu") and not on:
                        continue
                    hit = [f"H{h} from Lagna" for h in sorted(hs & set(g["aspects_houses_from_lagna"]))] + \
                          [f"H{h} from Moon" for h in sorted(hs & set(g["aspects_houses_from_moon"]))]
                    ind.append({"system": "Vedic", "tone": t, "from": g["from"], "to": g["to"],
                                "text": f"{p} in {g['sign']} (H{g['house_from_lagna']} from Lagna, H{g['house_from_moon']} from Moon)"
                                        + ("" if on or not hit else f", aspecting {' and '.join(hit)}")
                                        + f" ({'own bindus ' + str(ob) + ', ' if ob is not None else ''}SAV {g['sarva_bindus']})"})
            for ref in ("from_moon", "from_lagna"):
                for h in hs:
                    for run in F["vedic"]["double_transit"][ref].get(str(h), []):
                        if overlaps(run["from"], run["to"], s):
                            ind.append({"system": "Vedic", "tone": "*", "from": run["from"], "to": run["to"],
                                        "text": f"Double transit (Jupiter + Saturn) on H{h} {ref.replace('_', ' ')}"})
            if key in ("health", "career", "family"):
                for sh in F["vedic"]["saturn_from_moon"]:
                    if overlaps(sh["from"], sh["to"], s) and (key != "family" or "4th" in sh["kind"]) and (key != "career" or "Sade" in sh["kind"] or "10th" in sh["kind"]):
                        ind.append({"system": "Vedic", "tone": "-" if key == "health" else "~", "from": sh["from"], "to": sh["to"],
                                    "text": sh["kind"]})
            for vy in F["vedic"]["varshaphal_years"]:
                if overlaps(vy["from"], vy["to"], s) and vy["muntha_house"] in hs:
                    ind.append({"system": "Vedic", "tone": "+" if vy["muntha_tone"] == "favourable" else "-", "from": vy["from"], "to": vy["to"],
                                "text": f"Varshaphal age {vy['age']}: Muntha in H{vy['muntha_house']} of the year chart"})
            # --- Western
            for h in F["western"]["transit_hits"]:
                ds = [d for d in h["exact_dates"] if in_slice(d, s)]
                if not ds or h["natal"] not in natal_targets:
                    continue
                if h["transit"] == "Jupiter":
                    t = "+" if h["aspect"] in ("conjunction", "trine", "sextile") else "~"
                else:
                    t = "-" if h["aspect"] in ("conjunction", "square", "opposition") else "+"
                if h["natal"] == "Ascendant" and key == "love" and h["aspect"] != "opposition":
                    continue
                if h["natal"] == "Midheaven" and key == "family" and h["aspect"] != "opposition":
                    continue
                ind.append({"system": "Western", "tone": t, "from": ds[0], "to": ds[-1],
                            "text": f"{h['transit']} {h['aspect']} natal {h['natal']} ({', '.join(ds)})"})
            for y in F["western"]["birthday_years"]:
                if overlaps(y["from"], y["to"], s) and y["profected_house"] in hs:
                    ind.append({"system": "Western", "tone": "*", "from": y["from"], "to": y["to"],
                                "text": f"Profection to H{y['profected_house']} ({y['profected_sign']}), year lord {y['year_lord']}"})
            if A["zr"]:
                for l1 in F["western"]["zodiacal_releasing"][f"from_{A['zr']}"]:
                    for l2 in l1["level2"]:
                        if overlaps(l2["from"], l2["to"], s) and (l2["peak"] or l2["loosing_of_the_bond"]):
                            ind.append({"system": "Western", "tone": "*" if l2["loosing_of_the_bond"] else "+", "from": l2["from"], "to": l2["to"],
                                        "text": f"ZR from {A['zr'].title()}: L2 {l2['sign']}"
                                                f"{' - ' + l2['peak'] if l2['peak'] else ''}{' - loosing of the bond' if l2['loosing_of_the_bond'] else ''}"
                                                f" (L1 {l1['level1_sign']})"})
            for e in F["western"]["eclipses"]:
                if in_slice(e["date"], s) and (e["house_whole_sign"] in hs or any(c["natal"] in natal_targets for c in e["contacts_within_3deg"])):
                    ind.append({"system": "Western", "tone": "*", "from": e["date"], "to": e["date"],
                                "text": f"{e['type'].title()} {e['kind']} eclipse in H{e['house_whole_sign']}"
                                        + (f", on natal {', '.join(c['natal'] for c in e['contacts_within_3deg'])}" if e["contacts_within_3deg"] else "")})
            # --- BaZi
            for yr in F["bazi"]["annual"]:
                if not overlaps(yr["from"], yr["to"], s):
                    continue
                if any(yr["ten_god_stem"].startswith(t) for t in tg):
                    ind.append({"system": "BaZi", "tone": "*", "from": yr["from"], "to": yr["to"],
                                "text": f"{yr['text']} year stem is {yr['ten_god_stem']}"})
                for r in yr["new_branch_relations"]:
                    pal = [p for p in A["palaces"] if any(x.startswith(p + " ") for x in r["between"])]
                    if pal:
                        typ = r["type"]
                        t = "+" if ("harmony" in typ and "half" not in typ) else "-" if any(k in typ for k in ("clash", "punish", "harm")) else "~"
                        ind.append({"system": "BaZi", "tone": t, "from": yr["from"], "to": yr["to"],
                                    "text": f"{yr['text']} year: {typ} with {pal[0]} pillar"})
                if key == "love" and yr["peach_blossom_year"]:
                    ind.append({"system": "BaZi", "tone": "*", "from": yr["from"], "to": yr["to"], "text": f"{yr['text']} is a Peach Blossom year"})
                if key == "travel" and yr["travelling_horse_year"]:
                    ind.append({"system": "BaZi", "tone": "*", "from": yr["from"], "to": yr["to"], "text": f"{yr['text']} is a Travelling Horse year"})
            # --- Numerology
            for py in F["numerology"]["personal_years"]:
                if overlaps(py["from"], py["to"], s) and py["personal_year"] in A["py"]:
                    ind.append({"system": "Numerology", "tone": "*", "from": py["from"], "to": py["to"],
                                "text": f"Personal Year {py['personal_year']} ({py['year']})"})
            merged = {}
            for i_ in ind:
                k_ = (i_["system"], i_["text"])
                if k_ in merged:
                    m_ = merged[k_]
                    if (i_["from"], i_["to"]) not in m_["ranges"]:
                        m_["ranges"].append((i_["from"], i_["to"]))
                else:
                    merged[k_] = {**i_, "ranges": [(i_["from"], i_["to"])]}
            ind = []
            for m_ in merged.values():
                m_["ranges"] = sorted(m_["ranges"])
                m_["from"], m_["to"] = m_["ranges"][0][0], max(r_[1] for r_ in m_["ranges"])
                m_["ranges"] = [{"from": a_, "to": b_} for a_, b_ in m_["ranges"]]
                ind.append(m_)
            systems = {}
            for i_ in ind:
                systems.setdefault(i_["system"], {"+": 0, "-": 0, "~": 0, "*": 0})[i_["tone"]] += 1
            plus = sum(1 for c in systems.values() if c["+"] > c["-"])
            minus = sum(1 for c in systems.values() if c["-"] > c["+"])
            act = len(systems)
            lean = "supportive" if plus > minus else "demanding" if minus > plus else "mixed" if act else "quiet"
            conv = "strong" if max(plus, minus) >= 3 else "moderate" if max(plus, minus) == 2 else "weak"
            per.append({"slice": s["id"], "from": s["from"], "to": s["to"], "systems_active": act,
                        "systems_supportive": plus, "systems_demanding": minus, "lean": lean, "convergence": conv,
                        "indicators": ind})
        out[key] = {"label": A["label"], "houses": A["houses"], "by_slice": per}
    return out


# ============================================================= assemble
def key_dates(F, limit=40):
    ev = []
    for p, segs in F["vedic"]["gochar_segments"].items():
        for g in segs:
            if not g["starts_before_window"]:
                ev.append({"date": g["from"], "system": "Vedic", "event": f"{p} enters {g['sign']} (H{g['house_from_lagna']} from Lagna, H{g['house_from_moon']} from Moon)"})
    for r in F["vedic"]["vimshottari_antardashas"]:
        if r["from"] > F["window"]["start"]:
            ev.append({"date": r["from"], "system": "Vedic", "event": f"Vimshottari {r['maha']}-{r['antar']} begins"})
    for vy in F["vedic"]["varshaphal_years"]:
        if vy["from"] >= F["window"]["start"]:
            ev.append({"date": vy["from"], "system": "Vedic", "event": f"Varshaphal age {vy['age']}: Varsha Lagna {vy['varsha_lagna_sign']}, Muntha H{vy['muntha_house']}"})
    for h in F["western"]["transit_hits"]:
        if h["transit"] in ("Saturn", "Uranus", "Neptune", "Pluto", "Jupiter") and h["natal"] in ("Sun", "Moon", "Ascendant", "Midheaven"):
            ev.append({"date": h["exact_dates"][0], "system": "Western", "event": f"{h['transit']} {h['aspect']} natal {h['natal']}"
                                                                                  + (f" ({h['passes']} passes, last {h['exact_dates'][-1]})" if h["passes"] > 1 else "")})
    for e in F["western"]["eclipses"]:
        if e["contacts_within_3deg"]:
            ev.append({"date": e["date"], "system": "Western", "event": f"{e['type'].title()} {e['kind']} eclipse on natal "
                                                                        + ", ".join(c["natal"] for c in e["contacts_within_3deg"])})
    for lc in F["bazi"]["luck_pillar_changes_in_window"]:
        ev.append({"date": lc["from"], "system": "BaZi", "event": f"Luck pillar changes to {lc['text']} ({lc['ten_god_stem']})"})
    for l1 in F["western"]["zodiacal_releasing"]["from_spirit"]:
        for l2 in l1["level2"]:
            if l2["loosing_of_the_bond"] and l2["from"] >= F["window"]["start"]:
                ev.append({"date": l2["from"], "system": "Western", "event": f"ZR from Spirit: loosing of the bond into {l2['sign']}"})
    ev.sort(key=lambda x: x["date"])
    return ev[:limit] if limit else ev


def build_forecast(v, w, b, birth_utc, jd_birth, now, lat, lon, gender, dob, years=5, ayan="lahiri", node="mean",
                   birth_lat=None, birth_lon=None):
    ws = now
    we = add_years(now, years)
    window, slices = make_window(ws, years)
    F = {"window": window,
         "slices": [{k: s[k] for k in ("id", "from", "to")} for s in slices]}
    blat = lat if birth_lat is None else birth_lat
    blon = lon if birth_lon is None else birth_lon
    F["vedic"] = vedic_forecast(v, birth_utc, jd_birth, ws, we, slices, blat, blon, ayan, node) if v else None
    F["western"] = western_forecast(w, jd_birth, birth_utc, ws, we, lat, lon) if w else None
    F["bazi"] = bazi_forecast(b, birth_utc, ws, we) if b else None
    F["numerology"] = numerology_forecast(dob, ws, we)
    if v and w and b:
        F["life_areas"] = tag_areas(F, v, w, gender, slices)
        F["key_dates"] = key_dates(F)
    F["method"] = ("See references/forecast_method.md. Tones: + supportive, - demanding, ~ mixed, * activation without tone. "
                   "Tags are a fixed screening rule for the writer, not a prediction or probability.")
    return F
