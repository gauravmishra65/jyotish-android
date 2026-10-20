"""tajika.py - the Tajika layer of the annual chart (Varshaphal): Pancha-adhikari and Varsheshwara,
Pancha-vargiya bala, Tajika aspects and the core Tajika yogas, sahams, and Mudda dasha.

Conventions (returned with the result):
* The annual chart is cast for the sidereal solar return at the BIRTHPLACE (PVR 27.1), Lahiri, whole signs.
  Day or night = Sun above or below the horizon at the return.
* Pancha-adhikari (five office-bearers): Muntha lord; natal Lagna lord; Varsha Lagna lord; Tri-rashi pati (by the
  Varsha Lagna sign, day or night return; for Sagittarius to Pisces the same lord serves day and night);
  Dina-ratri pati (lord of the Sun's sign by day, of the Moon's sign by night).
* Varsheshwara (year lord): among the office-bearers that aspect the Varsha Lagna by Tajika aspect, the one with
  the highest Pancha-vargiya bala; if none aspects it, the strongest office-bearer. Some practitioners first prefer
  a candidate with a friendly (3/5/9/11) aspect; the result says whether that would change the choice.
* Tajika aspects by sign: 3rd/11th and 5th/9th friendly, 1st/7th and 4th/10th inimical, 2/6/8/12 none.
* Pancha-vargiya bala (PVR's figures): Kshetra 30 / 22.5 / 15 / 7.5 for own-or-exaltation / friend / neutral /
  enemy sign; Uchcha = distance from the deep debilitation point / 9 (0 to 20); Hadda (Egyptian terms) 15 / 7.5 /
  3.75 own / friend / enemy; Drekkana (D-3) 10 / 5 / 2.5 and Navamsa (D-9) 5 / 2.5 / 1.25 own / friend / enemy;
  a neutral term, drekkana or navamsa lord takes the mean of the friend and enemy values (PVR gives three grades).
  Sum / 4. Natural (Naisargika) friendship.
* Deeptamsa (orbs): Sun 15, Moon 12, Mars 8, Mercury 7, Jupiter 9, Venus 7, Saturn 9. Two planets are in a Tajika
  aspect by degree when the gap from the exact angle (0, 60, 90, 120, 180) is within half the sum of their orbs.
  Ithasala = applying; Ishrafa = separating. Nakta = a faster third planet in aspect with both of two planets that
  are not in aspect, separating from one and applying to the other; Yamaya = the same with a slower third planet.
  Kamboola = the Moon in Ithasala with one of a pair already in Ithasala.
* Sahams: A - B + C with 30 deg added when C is not on the arc from B to A (PVR 28.8.1); reversed by night where
  the texts reverse them. Sahams of disease, death, enemies and imprisonment are not computed.
* Mudda dasha: Vimshottari order, the first lord being the birth-star lord moved on by the completed years
  (equivalently (birth nakshatra number + years - 2) mod 9 counted from the Sun); the natal balance is kept, and
  the nine periods share the solar year in Vimshottari proportion (Sun 18 parts of 360, Venus 60...).
* Not computed: Harsha bala, Tajika yogas beyond the five above, Tri-pataki chakra, monthly (maasa pravesh) charts.
"""
import datetime as dt
import swisseph as swe
from common import SIGNS, SIGN_LORD, NAK_SPAN, VIM_ORDER, n360, fmt_pos, jd_to_dt, dt_to_jd
import vedic as V

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
DEEPTAMSA = {"Sun": 15, "Moon": 12, "Mars": 8, "Mercury": 7, "Jupiter": 9, "Venus": 7, "Saturn": 9}
TRI_RASHI_DAY = ["Sun", "Venus", "Saturn", "Venus", "Jupiter", "Moon", "Mercury", "Mars", "Saturn", "Mars", "Jupiter", "Moon"]
TRI_RASHI_NIGHT = ["Jupiter", "Moon", "Mercury", "Mars", "Sun", "Venus", "Saturn", "Venus", "Saturn", "Mars", "Jupiter", "Moon"]
# Egyptian terms (Hadda): (lord, upper degree) per sign
HADDA = [[("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
         [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
         [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
         [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
         [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
         [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
         [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
         [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
         [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
         [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
         [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
         [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)]]
FRIENDLY_ASPECT = (3, 5, 9, 11)
INIMICAL_ASPECT = (1, 4, 7, 10)
ANGLES = (0, 60, 90, 120, 180)
VIM_PARTS = {"Ketu": 21, "Venus": 60, "Sun": 18, "Moon": 30, "Mars": 21, "Rahu": 54, "Jupiter": 48, "Saturn": 57, "Mercury": 51}


def _rel(p, lord):
    if lord == p:
        return "own"
    if lord in V.FRIENDS.get(p, []):
        return "friend"
    if lord in V.ENEMIES.get(p, []):
        return "enemy"
    return "neutral"


def _graded(p, lord, own, fr, en):
    r = _rel(p, lord)
    return {"own": own, "friend": fr, "enemy": en, "neutral": (fr + en) / 2}[r]


def pancha_vargiya(pos):
    out = {}
    for p in SEVEN:
        lon = pos[p]
        s = int(lon // 30)
        d = lon % 30
        es, ed = V.EXALT[p]
        if s == es or s in V.OWN[p]:
            ks = 30.0
        else:
            ks = {"friend": 22.5, "neutral": 15.0, "enemy": 7.5}[_rel(p, SIGN_LORD[s])]
        deb = n360(es * 30 + ed + 180)
        dist = abs((lon - deb + 180) % 360 - 180)
        uc = dist / 9.0
        hl = next(lord for lord, up in HADDA[s] if d < up)
        hb = _graded(p, hl, 15, 7.5, 3.75)
        db = _graded(p, SIGN_LORD[V.varga_sign(lon, 3)], 10, 5, 2.5)
        nb = _graded(p, SIGN_LORD[V.varga_sign(lon, 9)], 5, 2.5, 1.25)
        out[p] = {"kshetra": ks, "uchcha": round(uc, 2), "hadda": hb, "hadda_lord": hl, "drekkana": db, "navamsa": nb,
                  "total": round((ks + uc + hb + db + nb) / 4, 2)}
    return out


def _house(a_sign, b_sign):
    return (b_sign - a_sign) % 12 + 1


def _aspect_by_degree(la, lb, sa, sb, oa, ob):
    sep = abs((lb - la + 180) % 360 - 180)
    best = min(ANGLES, key=lambda g: abs(sep - g))
    gap = abs(sep - best)
    if gap > (oa + ob) / 2:
        return None
    sep2 = abs(((lb + sb * 0.01) - (la + sa * 0.01) + 180) % 360 - 180)
    applying = abs(sep2 - best) < gap
    return {"angle": best, "gap": round(gap, 2), "applying": applying}


def tajika_yogas(pos, speed):
    pairs = {}
    for i, a in enumerate(SEVEN):
        for b in SEVEN[i + 1:]:
            asp = _aspect_by_degree(pos[a], pos[b], speed[a], speed[b], DEEPTAMSA[a], DEEPTAMSA[b])
            if asp:
                pairs[(a, b)] = asp
    yogas = []
    for (a, b), x in pairs.items():
        yogas.append({"yoga": "Ithasala" if x["applying"] else "Ishrafa", "planets": [a, b], "angle": x["angle"], "gap_deg": x["gap"],
                      "meaning": "applying: the matter the two planets rule moves toward completion" if x["applying"]
                      else "separating: the matter has passed its peak or slips away"})
    for (a, b) in [(a, b) for i, a in enumerate(SEVEN) for b in SEVEN[i + 1:] if (a, b) not in pairs]:
        for c in SEVEN:
            if c in (a, b):
                continue
            ka, kb = tuple(sorted((a, c), key=SEVEN.index)), tuple(sorted((b, c), key=SEVEN.index))
            if ka in pairs and kb in pairs:
                fast = abs(speed[c]) > max(abs(speed[a]), abs(speed[b]))
                slow = abs(speed[c]) < min(abs(speed[a]), abs(speed[b]))
                one_sep_one_app = pairs[ka]["applying"] != pairs[kb]["applying"]
                if fast and one_sep_one_app:
                    yogas.append({"yoga": "Nakta", "planets": [a, b], "via": c,
                                  "meaning": f"{c}, faster, carries the light between {a} and {b}: help through a third party"})
                elif slow and pairs[ka]["applying"] and pairs[kb]["applying"]:
                    yogas.append({"yoga": "Yamaya", "planets": [a, b], "via": c,
                                  "meaning": f"{c}, slower, collects the light of {a} and {b}: an older or senior person helps"})
    for (a, b), x in pairs.items():
        if x["applying"] and "Moon" not in (a, b):
            for z in (a, b):
                k = tuple(sorted(("Moon", z), key=SEVEN.index))
                if k in pairs and pairs[k]["applying"]:
                    yogas.append({"yoga": "Kamboola", "planets": [a, b], "via": "Moon",
                                  "meaning": f"the Moon applies to {z}, strengthening the {a}-{b} Ithasala"})
                    break
    return yogas


def _saham(a, b, c):
    r = n360(a - b + c)
    if not (n360(c - b) <= n360(a - b)):
        r = n360(r + 30)
    return r


def sahams(pos, asc, day):
    L = int(asc // 30)
    lord = lambda h: SIGN_LORD[(L + h - 1) % 12]  # noqa: E731
    rev = lambda a, b, c: _saham(a, b, c) if day else _saham(b, a, c)  # noqa: E731
    P = {}
    P["Punya (merit, fortune)"] = rev(pos["Moon"], pos["Sun"], asc)
    pu = P["Punya (merit, fortune)"]
    P["Vidya (learning)"] = rev(pos["Sun"], pos["Moon"], asc)
    P["Yasas (fame)"] = rev(pos["Jupiter"], pu, asc)
    P["Mitra (friends)"] = rev(pos["Jupiter"], pu, pos["Venus"])
    P["Mahatmya (greatness)"] = rev(pu, pos["Mars"], asc)
    P["Asha (hopes)"] = rev(pos["Saturn"], pos["Mars"], asc)
    if lord(1) == "Mars":
        P["Samartha (ability)"] = rev(pos["Jupiter"], pos["Mars"], asc)
    else:
        P["Samartha (ability)"] = rev(pos["Mars"], pos[lord(1)], asc)
    P["Bhratri (siblings)"] = _saham(pos["Jupiter"], pos["Saturn"], asc)
    P["Gaurava (respect)"] = rev(pos["Jupiter"], pos["Moon"], pos["Sun"])
    P["Pitri (father)"] = rev(pos["Saturn"], pos["Sun"], asc)
    P["Matri (mother)"] = rev(pos["Moon"], pos["Venus"], asc)
    P["Putra (children)"] = rev(pos["Jupiter"], pos["Moon"], asc)
    P["Karma (work)"] = rev(pos["Mars"], pos["Mercury"], asc)
    P["Vivaha (marriage)"] = rev(pos["Venus"], pos["Saturn"], asc)
    P["Paradesa (foreign lands)"] = _saham(n360(asc + 240), pos[lord(9)], asc)
    P["Artha (money)"] = _saham(n360(asc + 30), pos[lord(2)], asc)
    P["Labha (gains)"] = rev(n360(asc + 300), pos[lord(11)], asc)
    return {k: {"lon": round(v, 3), "position": fmt_pos(v), "sign": SIGNS[int(v // 30)], "house": (int(v // 30) - L) % 12 + 1}
            for k, v in P.items()}


def mudda(natal_moon_lon, years, sr_jd, next_sr_jd):
    ni = int(n360(natal_moon_lon) // NAK_SPAN)
    frac = (n360(natal_moon_lon) % NAK_SPAN) / NAK_SPAN
    order = [p for p, _ in VIM_ORDER]
    i0 = (ni % 9 + years) % 9
    year_days = next_sr_jd - sr_jd
    unit = year_days / 360.0
    first = order[i0]
    t = sr_jd - frac * VIM_PARTS[first] * unit
    out = []
    for k in range(10):
        p = order[(i0 + k) % 9]
        d = VIM_PARTS[p] * unit
        a, b = t, t + d
        if b > sr_jd and a < next_sr_jd:
            out.append({"lord": p, "from": jd_to_dt(max(a, sr_jd)).date().isoformat(), "to": jd_to_dt(min(b, next_sr_jd)).date().isoformat(),
                        "days": round(min(b, next_sr_jd) - max(a, sr_jd), 1)})
        t = b
        if t >= next_sr_jd:
            break
    return {"periods": out, "first_lord": first, "natal_balance_used": round(1 - frac, 4), "year_days": round(year_days, 3)}


def annual(natal_v, birth_utc, years, lat, lon, ayan="lahiri", node="mean"):
    """Tajika reading for the year that starts at the `years`-th solar return."""
    nat_sun = natal_v["planets"]["Sun"]["lon"]
    sr = V.return_utc(nat_sun, birth_utc, years, ayan)
    sr2 = V.return_utc(nat_sun, birth_utc, years + 1, ayan)
    jd, jd2 = dt_to_jd(sr), dt_to_jd(sr2)
    p = V.sidereal_positions(jd, ayan, node)
    pos = {k: v["lon"] for k, v in p.items()}
    spd = {k: v["speed"] for k, v in p.items()}
    _, asc, _ = V.sidereal_angles(jd, lat, lon, ayan)
    xx = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
    day = swe.azalt(jd, swe.EQU2HOR, (lon, lat, 0.0), 1013.25, 15.0, (xx[0], xx[1], xx[2]))[1] > -0.833
    vl = int(asc // 30)
    natal_lag = SIGNS.index(natal_v["lagna"]["sign"])
    muntha = (natal_lag + years) % 12
    offices = {"Muntha lord": SIGN_LORD[muntha], "Janma Lagna lord": SIGN_LORD[natal_lag], "Varsha Lagna lord": SIGN_LORD[vl],
               "Tri-rashi pati": (TRI_RASHI_DAY if day else TRI_RASHI_NIGHT)[vl],
               "Dina-ratri pati": SIGN_LORD[int(pos["Sun" if day else "Moon"] // 30)]}
    pvb = pancha_vargiya(pos)
    cand = []
    for role, pl in offices.items():
        h = _house(int(pos[pl] // 30), vl)
        kind = "friendly" if h in FRIENDLY_ASPECT else "inimical" if h in INIMICAL_ASPECT else None
        cand.append({"role": role, "planet": pl, "aspects_varsha_lagna": kind, "pancha_vargiya": pvb[pl]["total"]})
    asp = [c for c in cand if c["aspects_varsha_lagna"]]
    pool = asp or cand
    best = max(pool, key=lambda c: (c["pancha_vargiya"], -list(offices).index(c["role"])))
    fr = [c for c in cand if c["aspects_varsha_lagna"] == "friendly"]
    alt = max(fr, key=lambda c: c["pancha_vargiya"])["planet"] if fr else None
    houses = {k: (int(v // 30) - vl) % 12 + 1 for k, v in pos.items()}
    return {
        "year_index": years, "return_utc": sr.strftime("%Y-%m-%d %H:%M:%S"), "next_return_utc": sr2.strftime("%Y-%m-%d %H:%M:%S"),
        "day_return": day, "varsha_lagna": fmt_pos(asc), "varsha_lagna_sign": SIGNS[vl],
        "muntha_sign": SIGNS[muntha], "muntha_house": (muntha - vl) % 12 + 1, "muntha_lord": SIGN_LORD[muntha],
        "pancha_adhikari": cand,
        "varsheshwara": {"planet": best["planet"], "role": best["role"], "pancha_vargiya": best["pancha_vargiya"],
                         "house": houses[best["planet"]], "chosen_because": ("strongest office-bearer aspecting the Varsha Lagna" if asp
                                                                                  else "no office-bearer aspects the Varsha Lagna; strongest office-bearer"),
                         "friendly_aspect_preference_would_give": alt, "agrees_with_friendly_preference": alt in (None, best["planet"])},
        "pancha_vargiya_bala": pvb,
        "tajika_yogas": tajika_yogas({k: pos[k] for k in SEVEN}, {k: spd[k] for k in SEVEN}),
        "sahams": sahams(pos, asc, day),
        "mudda_dasha": mudda(natal_v["planets"]["Moon"]["lon"], years, jd, jd2),
        "planets_annual": {k: {"position": fmt_pos(v), "house": houses[k]} for k, v in pos.items()},
        "conventions": " ".join(__doc__.split("Conventions (returned with the result):")[1].split()),
    }
