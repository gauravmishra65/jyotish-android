"""events.py - Phase 4 event engine.

What it adds (all facts, no verdicts):
  * natal reference points: arudhas, sahams (both Vivaha definitions, Paradesa, Jalapatana, Putra, Karma),
    Indu lagna, Beeja/Kshetra sphuta, paaka lagna (PVR 25.3, 28.8; Boney; Trivedi)
  * nakshatra transit tools (PVR ch. 26): taras, special nakshatras, nakshatra aspects, latta, murthis
  * stations of the event planets, kakshya windows with Prastaara Ashtakavarga (PVR 25.5.2)
  * transits of Jupiter, Saturn and Rahu over the natal reference points
  * K.N. Rao's three-step marriage timing (via Trivedi) and area windows for children, career, money,
    property, abroad, education and spiritual turns: Parashari dasha eligibility + Jaimini sign
    eligibility + transit confirmation, each with its base rate in this chart
  * KP event layer: cusp sub-lord promise, dasha-lord significations, ruling planets
  * service-or-business screen (Kapoor) and the abroad dasha rule (Chatterjee)
Base rates: every rule reports the share of months in the person's own life (ages 18-70, or 18-45 for
marriage) on which it is true, so a rule that is almost always true is visibly weak.
"""
import datetime as dt
import math
import swisseph as swe
from common import SIGNS, SIGN_LORD, NAKSHATRAS, NAK_SPAN, VIM_ORDER, n360, sign_of, deg_in_sign, wrap180, jd_to_dt, dt_to_jd
import vedic

SLOW = ["Jupiter", "Saturn", "Rahu", "Ketu"]
ASP = {"Sun": [1, 7], "Moon": [1, 7], "Mercury": [1, 7], "Venus": [1, 7], "Mars": [1, 4, 7, 8],
       "Jupiter": [1, 5, 7, 9], "Saturn": [1, 3, 7, 10], "Rahu": [1], "Ketu": [1]}
SID_ID = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
          "Venus": swe.VENUS, "Saturn": swe.SATURN}
MURTHI = {1: "Swarna (golden, highly favourable)", 6: "Swarna (golden, highly favourable)",
          11: "Swarna (golden, highly favourable)", 2: "Rajata (silver, favourable)", 5: "Rajata (silver, favourable)",
          9: "Rajata (silver, favourable)", 3: "Taamra (copper, unfavourable)", 7: "Taamra (copper, unfavourable)",
          10: "Taamra (copper, unfavourable)", 4: "Loha (iron, highly unfavourable)",
          8: "Loha (iron, highly unfavourable)", 12: "Loha (iron, highly unfavourable)"}
TARA = ["Janma (birth, mixed)", "Sampat (wealth, good)", "Vipat (danger, bad)", "Kshema (well-being, good)",
        "Pratyak (obstacles, bad)", "Saadhana (achievement, good)", "Naidhana (strain, bad)",
        "Mitra (friend, good)", "Parama Mitra (best friend, good)"]
SPECIAL = {1: "Janma (well-being)", 4: "Jaati (community)", 7: "Naidhana (strain)", 10: "Karma (work)",
           12: "Desa (country)", 13: "Abhisheka (power)", 16: "Saanghaatika (groups)",
           18: "Saamudaayika (crowds)", 19: "Aadhaana (family)", 22: "Vainaasika (setbacks)", 25: "Maanasa (mind)"}
NAK_ASPECT = {"Sun": [14, 15], "Moon": [14, 15], "Mars": [1, 3, 7, 8, 15], "Mercury": [1, 15], "Venus": [1, 15],
              "Jupiter": [10, 15, 19], "Saturn": [3, 5, 15, 19]}
LATTA = {"Sun": 12, "Mars": 3, "Jupiter": 6, "Saturn": 8, "Moon": -22, "Mercury": -7, "Venus": -5, "Rahu": -9}
KAKSHYA = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
INDU_UNITS = {"Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8, "Jupiter": 10, "Venus": 12, "Saturn": 1}
KP_EVENTS = {"marriage": (7, {2, 7, 11}, {1, 6, 10}), "career": (10, {2, 6, 10, 11}, {1, 5, 9}),
             "children": (5, {2, 5, 11}, {1, 4, 10}), "property": (4, {4, 11, 12}, {3, 10}),
             "abroad": (12, {3, 9, 12}, {2, 4, 11}), "education": (4, {4, 9, 11}, {3, 8, 10})}
WEEKDAY_LORD_SUN0 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


# ------------------------------------------------------------------ positions
class Eph:
    def __init__(self, ayan, node):
        self.ayan, self.node, self.cache = ayan, node, {}

    def pos(self, jd):
        k = round(jd, 4)
        if k not in self.cache:
            p = vedic.sidereal_positions(jd, self.ayan, self.node)
            self.cache[k] = {n: (v["lon"], v["speed"]) for n, v in p.items()}
        return self.cache[k]

    def lon(self, jd, p):
        return self.pos(jd)[p][0]


def covers(p, lon):
    s = sign_of(lon)
    return {(s + h - 1) % 12 for h in ASP[p]}


def _iso(jd):
    return jd_to_dt(jd).date().isoformat()


def _jd(d):
    return swe.julday(d.year, d.month, d.day, 6.0)


def _edge(f, a, b, it=30):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        if f(m) == fa:
            a = m
        else:
            b = m
    return (a + b) / 2


def segments(fn, j0, j1, step=1.0):
    """Runs of constant fn(jd) between j0 and j1: [(start, end, value)]."""
    out, j, v = [], j0, fn(j0)
    start = j0
    while j < j1:
        j2 = min(j + step, j1)
        v2 = fn(j2)
        if v2 != v:
            e = _edge(fn, j, j2)
            out.append((start, e, v))
            start, v = e, fn(min(e + 1e-4, j2))
        j = j2
    out.append((start, j1, v))
    return out


# ------------------------------------------------------------------ sahams and points
def saham(a, b, c):
    """PVR 28.8.1: A - B + C, plus 30 deg when C is not on the zodiacal arc from B to A."""
    r = n360(a - b + c)
    if not (n360(c - b) <= n360(a - b)):
        r = n360(r + 30)
    return r


def is_day(jd, lat, lon):
    xx = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
    alt = swe.azalt(jd, swe.EQU2HOR, (lon, lat, 0.0), 1013.25, 15.0, (xx[0], xx[1], xx[2]))[1]
    return alt > -0.833


def reference_points(v, jd, lat, lon, gender):
    pl = v["planets"]
    L = SIGNS.index(v["lagna"]["sign"])
    asc = v["lagna"]["lon"]
    lon_ = {p: pl[p]["lon"] for p in pl}
    lord = lambda h: SIGN_LORD[(L + h - 1) % 12]
    day = is_day(jd, lat, lon)
    rev = lambda a, b, c: saham(a, b, c) if day else saham(b, a, c)
    pts = {}
    pts["Lagna"] = {"lon": asc, "kind": "degree"}
    pts["Vivaha saham (Tajaka: Venus - Saturn + Lagna)"] = {"lon": rev(lon_["Venus"], lon_["Saturn"], asc), "kind": "degree"}
    pts["Vivaha point (Boney/Raman: Lagna lord + 7th lord)"] = {"lon": n360(lon_[lord(1)] + lon_[lord(7)]), "kind": "degree"}
    pts["Paradesa saham (9th house - 9th lord + Lagna)"] = {"lon": saham(n360(asc + 240), lon_[lord(9)], asc), "kind": "degree"}
    pts["Jalapatana saham (Cancer 15 - Saturn + Lagna)"] = {"lon": rev(105.0, lon_["Saturn"], asc), "kind": "degree"}
    pts["Putra saham (Jupiter - Moon + Lagna)"] = {"lon": rev(lon_["Jupiter"], lon_["Moon"], asc), "kind": "degree"}
    pts["Karma saham (Mars - Mercury + Lagna)"] = {"lon": rev(lon_["Mars"], lon_["Mercury"], asc), "kind": "degree"}
    ms = pl["Moon"]["sign_index"]
    u = INDU_UNITS[SIGN_LORD[(L + 8) % 12]] + INDU_UNITS[SIGN_LORD[(ms + 8) % 12]]
    r = u % 12 or 12
    pts["Indu lagna"] = {"sign": (ms + r - 1) % 12, "kind": "sign", "units": u}
    if gender.upper().startswith("M"):
        b = n360(lon_["Sun"] + lon_["Venus"] + lon_["Jupiter"])
        nm, want_odd = "Beeja sphuta (Sun + Venus + Jupiter)", True
    else:
        b = n360(lon_["Moon"] + lon_["Mars"] + lon_["Jupiter"])
        nm, want_odd = "Kshetra sphuta (Moon + Mars + Jupiter)", False
    s9 = vedic.varga_sign(b, 9)
    pts[nm] = {"lon": b, "kind": "degree", "sign_odd": sign_of(b) % 2 == 0, "navamsa_odd": s9 % 2 == 0,
               "classically_favourable": ((sign_of(b) % 2 == 0) == want_odd) and ((s9 % 2 == 0) == want_odd)}
    pts["Paaka lagna (sign of the lagna lord)"] = {"sign": pl[lord(1)]["sign_index"], "kind": "sign"}
    ar = v["jaimini"].get("arudha_padas_pvr") or v["jaimini"]["arudha_padas"]
    for k, lab in (("AL (Arudha Lagna)", "AL"), ("A10", "A10"), ("A9", "A9"), ("A7", "A7 (darapada)"),
                   ("UL (Upapada Lagna)", "UL"), ("A4", "A4"), ("A5", "A5")):
        if k in ar:
            pts[lab] = {"sign": SIGNS.index(ar[k]), "kind": "sign"}
    for k, p in pts.items():
        if "lon" in p:
            p["sign"] = sign_of(p["lon"])
    return pts, day


def points_public(pts):
    out = {}
    for k, p in pts.items():
        r = {kk: vv for kk, vv in p.items() if kk not in ("lon", "sign")}
        r["sign"] = SIGNS[p["sign"]]
        if "lon" in p:
            r["deg"] = round(deg_in_sign(p["lon"]), 2)
        out[k] = r
    return out


# ------------------------------------------------------------------ nakshatra tools
def nak_of(lon):
    return int(n360(lon) // NAK_SPAN)


def count_from(a, b):
    """Inclusive count from nakshatra a to b (1..27)."""
    return (b - a) % 27 + 1


def latta_target(p, nak):
    k = LATTA[p]
    return (nak + k - 1) % 27 if k > 0 else (nak - (-k - 1)) % 27


def nakshatra_tools(v, E, j0, j1, lag_nak):
    J = nak_of(v["planets"]["Moon"]["lon"])
    special = {SPECIAL[c]: NAKSHATRAS[(J + c - 1) % 27] for c in SPECIAL}
    special_idx = {(J + c - 1) % 27: SPECIAL[c] for c in SPECIAL}
    rows = []
    for p in SLOW:
        for a, b, nk in segments(lambda j: nak_of(E.lon(j, p)), j0, j1, 1.0):
            c = count_from(J, nk)
            r = {"planet": p, "from": _iso(a), "to": _iso(b), "nakshatra": NAKSHATRAS[nk],
                 "tara": TARA[(c - 1) % 9], "count_from_janma": c}
            if nk in special_idx:
                r["special_nakshatra"] = special_idx[nk]
            if p in NAK_ASPECT:
                asp = [special_idx[(nk + x - 1) % 27] for x in NAK_ASPECT[p] if (nk + x - 1) % 27 in special_idx]
                if asp:
                    r["aspects_special"] = asp
            if p in LATTA:
                t = latta_target(p, nk)
                if t in (J, lag_nak):
                    r["latta_on"] = "janma nakshatra" if t == J else "lagna nakshatra"
            rows.append(r)
    kicks = []
    for p in ("Sun", "Mars", "Mercury", "Venus"):
        for a, b, nk in segments(lambda j: nak_of(E.lon(j, p)), j0, j1, 0.5):
            t = latta_target(p, nk)
            if t in (J, lag_nak):
                kicks.append({"planet": p, "from": _iso(a), "to": _iso(b), "from_nakshatra": NAKSHATRAS[nk],
                              "latta_on": "janma nakshatra" if t == J else "lagna nakshatra"})
    return {"janma_nakshatra": NAKSHATRAS[J], "lagna_nakshatra": NAKSHATRAS[lag_nak], "special_nakshatras": special,
            "slow_planet_nakshatra_transits": rows, "fast_planet_latta_on_janma_or_lagna": kicks,
            "rule": ("PVR 26.4-26.7. Bad taras 3, 5, 7 (and 12, 14, 16, 21, 23, 25). A latta on the janma or lagna "
                     "nakshatra marks a setback in what that planet rules natally; wording stays neutral.")}


def murthis(v, E, j0, j1):
    moon_n = v["planets"]["Moon"]["sign_index"]
    out = []
    for p in SLOW:
        segs = segments(lambda j: sign_of(E.lon(j, p)), j0, j1, 1.0)
        for a, b, s in segs[1:]:
            mo = sign_of(E.lon(a, "Moon"))
            h = (mo - moon_n) % 12 + 1
            out.append({"planet": p, "enters": SIGNS[s], "at": jd_to_dt(a).strftime("%Y-%m-%d %H:%M UTC"),
                        "moon_house_from_natal_moon": h, "murthi": MURTHI[h]})
    return out


def stations(E, j0, j1):
    out = []
    for p in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        for a, b, retro in segments(lambda j: E.pos(j)[p][1] < 0, j0, j1, 1.0)[1:]:
            out.append({"planet": p, "date": _iso(a), "turns": "retrograde" if retro else "direct",
                        "sign": SIGNS[sign_of(E.lon(a, p))]})
    return sorted(out, key=lambda r: r["date"])


def prastara(v):
    sidx = {p: v["planets"][p]["sign_index"] for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")}
    sidx["Lagna"] = SIGNS.index(v["lagna"]["sign"])
    pav = {t: {s: [] for s in range(12)} for t in vedic.BAV_RULES}
    for t, contribs in vedic.BAV_RULES.items():
        for src, houses in contribs.items():
            for h in houses:
                pav[t][(sidx[src] + h - 1) % 12].append(src)
    return pav


def kakshyas(E, pav, j0, j1):
    out = []
    for p in ("Jupiter", "Saturn"):
        for a, b, (s, k) in segments(lambda j: (sign_of(E.lon(j, p)), int(deg_in_sign(E.lon(j, p)) // 3.75)), j0, j1, 1.0):
            lordk = KAKSHYA[k]
            out.append({"planet": p, "from": _iso(a), "to": _iso(b), "sign": SIGNS[s], "kakshya_lord": lordk,
                        "rekha": lordk in pav[p][s]})
    return out


# ------------------------------------------------------------------ transits over reference points
def transits_over_points(pts, E, j0, j1):
    out = []
    for p in ("Jupiter", "Saturn", "Rahu"):
        for name, pt in pts.items():
            tgt = pt["sign"]
            f = (lambda j, p=p: tgt in covers(p, E.lon(j, p))) if p != "Rahu" else (lambda j, p=p: sign_of(E.lon(j, p)) == tgt)
            for a, b, on in segments(f, j0, j1, 2.0):
                if on:
                    rr = {"planet": p, "point": name, "from": _iso(a), "to": _iso(b),
                          "how": "occupies" if sign_of(E.lon((a + b) / 2, p)) == tgt else "aspects"}
                    if "lon" in pt:
                        best, bj = 99.0, None
                        j = a
                        while j <= b:
                            d = abs(wrap180(E.lon(j, p) - pt["lon"]))
                            if d < best:
                                best, bj = d, j
                            j += 2.0
                        if best <= 3.0:
                            rr["closest_deg"] = round(best, 2)
                            rr["closest_on"] = _iso(bj)
                    out.append(rr)
    return sorted(out, key=lambda r: (r["from"], r["planet"]))


# ------------------------------------------------------------------ dasha helpers
def _lords_at(v, d):
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        if m["start"] <= d < m["end"]:
            for a in m["antardashas"]:
                if a["start"] <= d < a["end"]:
                    return m["lord"], a["lord"]
            return m["lord"], None
    return None, None


def _sign_at(periods, d):
    for x in periods:
        if x["start"] <= d < x["end"]:
            return SIGNS.index(x["sign"])
    return None


def _rasi_aspect(a, b):
    """Jaimini rasi drishti: does sign a aspect sign b."""
    if a == b:
        return False
    ma, mb = a % 3, b % 3
    if ma == 0:
        return mb == 1 and b != (a + 1) % 12
    if ma == 1:
        return mb == 0 and b != (a - 1) % 12
    return mb == 2


# ------------------------------------------------------------------ area definitions
def _ctx(v, vo):
    pl = v["planets"]
    L = SIGNS.index(v["lagna"]["sign"])
    S = {p: pl[p]["sign_index"] for p in pl}
    H = {p: pl[p]["house"] for p in pl}
    lord = lambda h, base=L: SIGN_LORD[(base + h - 1) % 12]
    d = lambda n: {p: SIGNS.index(s) for p, s in v["divisional_charts"][f"D{n}"].items()}
    jm = v["jaimini"]["chara_karakas_7"]
    ar = v["jaimini"].get("arudha_padas_pvr") or v["jaimini"]["arudha_padas"]
    return dict(pl=pl, L=L, S=S, H=H, lord=lord, d=d, jm=jm, ar=ar, M=S["Moon"])


def area_rules(v, vo):
    c = _ctx(v, vo)
    pl, L, S, H, lord, d, jm, ar, M = (c[k] for k in ("pl", "L", "S", "H", "lord", "d", "jm", "ar", "M"))
    in_h = lambda hs: {p for p in H if H[p] in hs}
    d9, d10, d7, d4, d24 = d(9), d(10), d(7), d(4), d(24)
    vl = lambda dd, h: SIGN_LORD[(dd["Lagna"] + h - 1) % 12]
    in_v = lambda dd, hs: {p for p in dd if p != "Lagna" and (dd[p] - dd["Lagna"]) % 12 + 1 in hs}
    sgn = lambda h: (L + h - 1) % 12
    ls = lambda h: S[lord(h)]
    ry = set()
    for y in vo.get("parashari", {}).get("raja_yogas", {}).get("yogas", []):
        ry |= set(y["planets"])
    vip = {lord(h) for h in (6, 8, 12) if H[lord(h)] in (6, 8, 12)}
    rahu10 = {p for p in S if p not in ("Rahu", "Ketu") and (S["Rahu"] - S[p]) % 12 + 1 == 10}
    karaka = lambda k: jm.get(k)
    A = {}
    A["marriage"] = {
        "dasha": {lord(1), lord(7)} | in_h({1, 7}) | {vl(d9, 1), vl(d9, 7)} | in_v(d9, {1, 7}) | {"Venus", "Rahu"}
                 | {karaka("Darakaraka"), SIGN_LORD[S[lord(7)]]},
        "dasha_note": "lords of 1 and 7, planets in 1 and 7 (D-1 and D-9), Venus, Rahu, DK, dispositor of the 7th lord (Boney; Trivedi; ICAS)",
        "transit": lambda jl, jj, js: (_covers_axis(c, "Jupiter", jj) and _covers_axis(c, "Saturn", js)),
        "transit_note": ("Jupiter and Saturn cover the 1/7 axis (K.N. Rao step 1) within Rao's stated slack: Saturn within about "
                         "2.5 years, Jupiter within 12-15 months; on the exact date both together almost never hold"),
        "sign": lambda s: (s in (S["Venus"], S[karaka("Darakaraka")], sgn(7), (S["Venus"] + 6) % 12,
                                    (S[karaka("Darakaraka")] + 6) % 12, SIGNS.index(ar["A7"]), SIGNS.index(ar["UL (Upapada Lagna)"]))
                           or _rasi_aspect(S["Venus"], s) or _rasi_aspect(S[karaka("Darakaraka")], s)),
        "sign_note": "period sign holds, is aspected by or is 7th from Venus or the DK; the 7th sign; A7 or UL (Boney)",
        "grade": "A (K.N. Rao transit steps) / B (dasha lists)"}
    A["children"] = {
        "dasha": {"Jupiter", lord(5), lord(9), lord(5, M), lord(9, M), vl(d7, 1), vl(d7, 5), karaka("Putrakaraka")} | in_h({5}),
        "dasha_note": "Jupiter; lords of 5 and 9 from lagna and Moon; planets in 5; D-7 lagna and 5th lords; PK (Boney)",
        "transit": lambda jl, jj, js: (bool(covers("Jupiter", jj) & {sgn(5), ls(5), sgn(9), ls(9)})
                                       and bool(covers("Saturn", js) & {sgn(5), ls(5), sgn(9), ls(9)})),
        "transit_note": "Jupiter and Saturn both on 5, the 5th lord, 9 or the 9th lord (K.N. Rao rules 1-2)",
        "sign": lambda s: s in (S[karaka("Putrakaraka")], S["Jupiter"], (S[karaka("Putrakaraka")] + 4) % 12,
                                (S["Jupiter"] + 4) % 12, SIGNS.index(ar["A5"])),
        "sign_note": "period sign holds the PK or Jupiter, is 5th from them, or holds A5 (Boney)", "grade": "A/B"}
    A["career"] = {
        "dasha": {lord(10)} | in_h({10}) | ry | vip | {vl(d10, 1), vl(d10, 10)} | in_v(d10, {1, 10}) | {karaka("Amatyakaraka"), "Sun"},
        "dasha_note": "10th lord, planets in 10, raja and viparita yoga planets, D-10 lagna and 10th lords and occupants, AmK, Sun (Boney)",
        "transit": lambda jl, jj, js: ((sgn(10) in covers("Jupiter", jj) or ls(10) in covers("Jupiter", jj))
                                       and (sgn(10) in covers("Saturn", js) or ls(10) in covers("Saturn", js)))
                                      or S["Saturn"] in covers("Jupiter", jj),
        "transit_note": "Jupiter and Saturn both on the 10th or its lord, or Jupiter over natal Saturn (Rayudu; Chatterjee rule 19)",
        "sign": lambda s: s in (S[karaka("Amatyakaraka")], S["Sun"]) or (S[karaka("Amatyakaraka")] - s) % 12 + 1 in (7, 10)
                          or (S["Sun"] - s) % 12 + 1 in (7, 10),
        "sign_note": "period sign holds the AmK or Sun, or they are 7th or 10th from it (Boney; ICAS)", "grade": "B"}
    A["money"] = {
        "dasha": {lord(2), lord(11), lord(5), lord(9), "Jupiter", "Venus"},
        "dasha_note": "lords of 2, 11, 5, 9; Jupiter, Venus (Boney)",
        "transit": lambda jl, jj, js: (bool(covers("Jupiter", jj) & {sgn(2), sgn(11), ls(2), ls(11)})
                                       and bool(covers("Saturn", js) & {sgn(2), sgn(11), ls(2), ls(11)})),
        "transit_note": "Jupiter and Saturn on 2, 11 or their lords",
        "sign": lambda s: s in (S["Moon"], S["Venus"], S["Jupiter"]),
        "sign_note": "period sign holds the Moon, Venus or Jupiter (simplified from Boney)", "grade": "B/C"}
    A["property"] = {
        "dasha": {lord(4), "Moon", "Mars", vl(d4, 1), vl(d4, 4)} | in_h({4}) | in_v(d4, {1}),
        "dasha_note": "4th lord, planets in 4, Moon and Mars, D-4 lagna and 4th lords (Boney)",
        "transit": lambda jl, jj, js: ((sgn(4) in covers("Jupiter", jj) or ls(4) in covers("Jupiter", jj))
                                       and (sgn(4) in covers("Saturn", js) or ls(4) in covers("Saturn", js))),
        "transit_note": "Jupiter and Saturn both on the 4th or its lord",
        "sign": lambda s: s in (S[karaka("Matrikaraka")], (S[karaka("Matrikaraka")] + 3) % 12, SIGNS.index(ar["A4"]))
                          or _rasi_aspect(S[karaka("Matrikaraka")], s),
        "sign_note": "period sign holds or is aspected by the MK, is 4th from it, or holds A4 (Boney)", "grade": "B"}
    A["abroad"] = {
        "dasha": {"Rahu", lord(12), vl(d10, 12)} | in_h({12}) | rahu10 | in_v(d10, {12}),
        "dasha_note": "Rahu, 12th lord, planets in 12, the planet whose 10th holds Rahu, D-10 12th lord and occupants (Boney 19/20; Chatterjee)",
        "transit": None,   # filled from the saham points
        "transit_note": "Saturn or Rahu on the Paradesa or Jalapatana saham sign (PVR 28.8.2)",
        "sign": lambda s: S["Rahu"] in (s, (s + 3) % 12),
        "sign_note": "Rahu in the period sign or its 4th (Boney, exploratory)", "grade": "C"}
    A["education"] = {
        "dasha": {"Jupiter", "Mercury", lord(5), vl(d24, 1)} | in_h({5}),
        "dasha_note": "Jupiter, Mercury, 5th lord, planets in 5, D-24 lagna lord (Boney)",
        "transit": lambda jl, jj, js: bool(covers("Jupiter", jj) & {sgn(5), sgn(9)}),
        "transit_note": "Jupiter on or aspecting the 5th or 9th",
        "sign": lambda s: (s - L) % 12 + 1 in (5, 9),
        "sign_note": "period sign is 5th or 9th from lagna (Boney)", "grade": "B"}
    A["spiritual"] = {
        "dasha": {lord(5), lord(9), "Jupiter", "Ketu"},
        "dasha_note": "5th and 9th lords, Jupiter, Ketu (Boney)",
        "transit": lambda jl, jj, js: S["Ketu"] in covers("Jupiter", jj) or S["Ketu"] in covers("Saturn", js),
        "transit_note": "Jupiter or Saturn over natal Ketu",
        "sign": lambda s: (s - L) % 12 + 1 in (5, 9) or (S["Jupiter"] == S["Ketu"] == s),
        "sign_note": "period sign 5th or 9th from lagna, or holds Jupiter with Ketu (Boney)", "grade": "B"}
    for k in A:
        A[k]["dasha"] = {x for x in A[k]["dasha"] if x}
    return A, c


def _axis_set(c):
    L, S, lord = c["L"], c["S"], c["lord"]
    return [(L, (L + 6) % 12), (S[lord(1)], S[lord(7)]), (S[lord(1)], (L + 6) % 12), (L, S[lord(7)])]


def _covers_axis(c, p, lon_):
    cv = covers(p, lon_)
    return any(a in cv and b in cv for a, b in _axis_set(c))


def _fifth_factors(c, p, lon_, with9=True):
    L, S, lord = c["L"], c["S"], c["lord"]
    cv = covers(p, lon_)
    h5, l5, h9, l9 = (L + 4) % 12, S[lord(5)], (L + 8) % 12, S[lord(9)]
    ok = any(a in cv and b in cv for a, b in ((S["Venus"], h5), (S["Venus"], l5), (h5, l5)))
    return ok or (with9 and all(x in cv for x in (h5, l5, h9, l9)))


# ------------------------------------------------------------------ evaluation over time
def _months(d0, d1, step_days=30):
    d = d0
    while d < d1:
        yield d
        d += dt.timedelta(days=step_days)


def _axis_on(c, E, planet, d):
    memo = c.setdefault("_axis_memo", {})
    k = (planet, d.toordinal() // 5)
    if k not in memo:
        dd = dt.date.fromordinal(k[1] * 5)
        memo[k] = _covers_axis(c, planet, E.lon(_jd(dd), planet))
    return memo[k]


def kn_rao_axis_slack(c, E, d, sat_days=912, jup_days=456):
    """K.N. Rao step 1 with his stated slack: Saturn within ~2.5 years and Jupiter within ~15 months."""
    ok_s = any(_axis_on(c, E, "Saturn", d + dt.timedelta(days=x)) for x in range(-sat_days, sat_days + 1, 5))
    if not ok_s:
        return False
    return any(_axis_on(c, E, "Jupiter", d + dt.timedelta(days=x)) for x in range(-jup_days, jup_days + 1, 5))


def evaluate_area(key, A, c, v, vo, E, pts, d):
    """Truth of the three layers on date d (date object)."""
    jd = _jd(d)
    iso = d.isoformat()
    md, ad = _lords_at(v, iso)
    das = md in A["dasha"] or ad in A["dasha"]
    rd = vo.get("rasi_dashas", {}).get("narayana", {}).get("D-1", {})
    cr = vo.get("jaimini", {}).get("chara_dasha_rao", {})
    nar = _sign_at(rd.get("dasas", []), iso) if rd else None
    chs = _sign_at(cr.get("mahadashas", []), iso) if cr else None
    sign_ok = any(s is not None and A["sign"](s) for s in (nar, chs))
    jj, js = E.lon(jd, "Jupiter"), E.lon(jd, "Saturn")
    if key == "marriage":
        tr = kn_rao_axis_slack(c, E, d)
    elif key == "abroad":
        tg = {pts[k]["sign"] for k in pts if k.startswith("Paradesa") or k.startswith("Jalapatana")}
        tr = sign_of(js) in tg or sign_of(E.lon(jd, "Rahu")) in tg
    else:
        tr = A["transit"](None, jj, js)
    return {"dasha": das, "sign": sign_ok, "transit": tr, "md": md, "ad": ad, "narayana": nar, "chara": chs}


def area_windows(v, vo, E, pts, ws, we, birth):
    A, c = area_rules(v, vo)
    out = {}
    for key, rule in A.items():
        months = []
        for d in _months(ws, we):
            r = evaluate_area(key, rule, c, v, vo, E, pts, d)
            months.append((d, r))
        # base rates over ages 18-70
        b0 = max(birth + dt.timedelta(days=int(18 * 365.25)), birth)
        b1 = birth + dt.timedelta(days=int(70 * 365.25))
        cnt = {"dasha": 0, "sign": 0, "transit": 0, "dasha+transit": 0, "all_three": 0}
        n = 0
        for d in _months(b0, b1, 61):
            r = evaluate_area(key, rule, c, v, vo, E, pts, d)
            n += 1
            for k in ("dasha", "sign", "transit"):
                cnt[k] += r[k]
            cnt["dasha+transit"] += r["dasha"] and r["transit"]
            cnt["all_three"] += r["dasha"] and r["transit"] and r["sign"]
        base = {k: round(x / n, 2) for k, x in cnt.items()}
        wins, cur = [], None
        for d, r in months:
            ok = r["dasha"] and r["transit"]
            if ok:
                if cur is None:
                    cur = {"from": d.isoformat(), "to": d.isoformat(), "with_sign_dasha": r["sign"], "lords": set()}
                cur["to"] = (d + dt.timedelta(days=30)).isoformat()
                cur["with_sign_dasha"] = cur["with_sign_dasha"] or r["sign"]
                cur["lords"].add(f"{r['md']}-{r['ad']}")
            elif cur is not None:
                wins.append(cur)
                cur = None
        if cur:
            wins.append(cur)
        sbp = vo.get("shadbala", {}).get("bphs", {}).get("planets", {})

        def _ratio(p):
            if p in ("Rahu", "Ketu"):
                p = SIGN_LORD[v["planets"][p]["sign_index"]]
            return sbp.get(p, {}).get("ratio")
        for w in wins:
            w["dasha_periods"] = sorted(w.pop("lords"))
            rs = [_ratio(x) for pr in w["dasha_periods"] for x in pr.split("-") if x != "None"]
            rs = [x for x in rs if x is not None]
            w["lord_strength"] = round(sum(rs) / len(rs), 2) if rs else None
            w["counts_toward_strength"] = not rule["grade"].startswith("C")   # grades C/D never raise a window
        for i, w in enumerate(sorted(wins, key=lambda w: -(w["lord_strength"] or 0))):
            w["rank_by_strength"] = i + 1
        out[key] = {"windows": wins, "base_rate_ages_18_70": base,
                    "dasha_lords": sorted(rule["dasha"]), "dasha_rule": rule["dasha_note"],
                    "transit_rule": rule["transit_note"], "sign_rule": rule["sign_note"], "grade": rule["grade"],
                    "strength_rule": "PVR: prefer the window whose dasha lords are strongest (mean Shadbala ratio; nodes by their dispositor)"}
    return out, c


def kn_rao_marriage(c, v, E, ws, we, birth):
    """Trivedi's account of K.N. Rao's three steps, month by month."""
    def flags(d):
        jd = _jd(d)
        s_ax = _covers_axis(c, "Saturn", E.lon(jd, "Saturn"))
        j_ax = _covers_axis(c, "Jupiter", E.lon(jd, "Jupiter"))
        j5 = _fifth_factors(c, "Jupiter", E.lon(jd, "Jupiter"))
        m_ax = m5 = False
        for k in range(0, 181, 5):
            lm = E.lon(jd - k, "Mars")
            m_ax = m_ax or _covers_axis(c, "Mars", lm)
            m5 = m5 or _fifth_factors(c, "Mars", lm, with9=False)
        return s_ax, j_ax, j5, m_ax, m5
    rows = []
    for d in _months(ws, we):
        s_ax, j_ax, j5, m_ax, m5 = flags(d)
        rows.append({"month": d.isoformat()[:7], "saturn_on_1_7_axis": s_ax, "jupiter_on_1_7_axis": j_ax,
                     "jupiter_on_venus_5th_factors": j5, "mars_axis_last_6_months": m_ax, "mars_5th_last_6_months": m5,
                     "all_steps": s_ax and j_ax and j5 and m_ax and m5})
    n = 0
    cnt = [0] * 6
    for d in _months(birth + dt.timedelta(days=int(18 * 365.25)), birth + dt.timedelta(days=int(45 * 365.25)), 45):
        f = flags(d)
        n += 1
        for i, x in enumerate(f):
            cnt[i] += x
        cnt[5] += all(f)
    names = ["saturn_on_1_7_axis", "jupiter_on_1_7_axis", "jupiter_on_venus_5th_factors", "mars_axis_last_6_months",
             "mars_5th_last_6_months", "all_steps"]
    return {"months": rows, "base_rate_ages_18_45": {k: round(x / n, 2) for k, x in zip(names, cnt)},
            "rule": ("K.N. Rao (Astrological Magazine 1986-87, as given by Trivedi): (1) Jupiter and Saturn each cover the "
                     "1/7 axis - lagna and 7th, their lords, or one of each - by occupation or aspect; Rao allows about "
                     "2.5 years of slack for Saturn and 12-15 months for Jupiter; (2) in the year itself Jupiter covers "
                     "Venus and the 5th, Venus and the 5th lord, the 5th and its lord, or the 5th, 9th and their lords; "
                     "(3) within 6 months Mars covers the 1/7 axis and Venus or the 5th. Needs a natal promise and a "
                     "supporting dasha; on its own each step is true on many months (see the base rates)."),
            "grade": "A"}


# ------------------------------------------------------------------ KP
def kp_events(kp, v, now_jd, lat, lon):
    planets, cusps = kp["planets"], kp["cusps"]
    owns = {p: [] for p in planets}
    for h in range(1, 13):
        owns.setdefault(cusps[f"C{h}"]["sign_lord"], []).append(h)

    def sig(p):
        st = planets[p]["star_lord"]
        hs = {planets[st]["house"]} | set(owns.get(st, [])) | {planets[p]["house"]} | set(owns.get(p, []))
        if p in ("Rahu", "Ketu"):
            disp = planets[p]["sign_lord"]
            hs |= {planets[disp]["house"]} | set(owns.get(disp, []))
        return sorted(hs)
    sigs = {p: sig(p) for p in planets}
    cur = v["dashas"]["vimshottari"]["current"]
    lords = {"mahadasha": cur["mahadasha"]["lord"], "antardasha": cur["antardasha"]["lord"],
             "pratyantar": cur.get("pratyantar", {}).get("lord")}
    ev = {}
    for name, (cusp, pos, neg) in KP_EVENTS.items():
        sl = cusps[f"C{cusp}"]["sub_lord"]
        s = set(sigs[sl])
        promise = "promised" if (s & pos) and len(s & pos) >= len(s & neg) else ("weak or mixed" if s & pos else "not shown")
        ev[name] = {"cusp": cusp, "cusp_sub_lord": sl, "sub_lord_signifies": sorted(s), "event_houses": sorted(pos),
                    "negating_houses": sorted(neg), "promise": promise,
                    "dasha_lords_signify": {k: sorted(set(sigs[x]) & (pos | neg)) for k, x in lords.items() if x}}
    # ruling planets at the moment of judgement (report date, 12:00 UT, birthplace)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    mo = swe.calc_ut(now_jd, swe.MOON, fl)[0][0]
    asc = swe.houses_ex(now_jd, lat, lon, b"P", swe.FLG_SIDEREAL)[1][0] if abs(lat) < 66 else \
        swe.houses_ex(now_jd, lat, lon, b"O", swe.FLG_SIDEREAL)[1][0]
    local = jd_to_dt(now_jd) + dt.timedelta(hours=lon / 15.0)
    kl = vedic.kp_lords
    rp = {"day_lord": WEEKDAY_LORD_SUN0[local.isoweekday() % 7], "moon_sign_lord": kl(mo)["sign_lord"],
          "moon_star_lord": kl(mo)["star_lord"], "lagna_sign_lord": kl(asc)["sign_lord"],
          "lagna_star_lord": kl(asc)["star_lord"], "moment": local.strftime("%Y-%m-%d %H:%M local mean time")}
    return {"planet_significations": sigs, "events": ev, "ruling_planets_now": rp,
            "rule": ("KP: the sub-lord of the event's primary cusp must signify the event houses (promise); the dasha, "
                     "bhukti and antara lords must signify them through their star lord, own houses and sub-lord; a "
                     "sub-lord tied to the negating houses delays. Ruling planets confirm the dasha lords. Reuses the "
                     "Vimshottari periods, so it is a separate line, never an extra vote.")}


# ------------------------------------------------------------------ screens
def career_style(v, fn):
    pl = v["planets"]
    H = {p: pl[p]["house"] for p in pl}
    west = sum(1 for p in H if H[p] in (7, 8, 9, 10, 11, 12))
    upper = sum(1 for p in H if H[p] in (10, 11, 12, 1, 2, 3))
    L = SIGNS.index(v["lagna"]["sign"])
    sat_fm = "Saturn" in fn.get("functional_malefics", [])
    S = {p: pl[p]["sign_index"] for p in pl}
    tgts = {S["Moon"], (L + 9) % 12, S[SIGN_LORD[(L + 9) % 12]], L, S[SIGN_LORD[L]]}
    sat_inf = bool(covers("Saturn", pl["Saturn"]["lon"]) & tgts)
    lean = "self-employment / business" if (west >= 5 or upper >= 5) and not (sat_fm and sat_inf) else "service / salaried"
    return {"planets_in_7_to_12": west, "planets_in_10_to_3": upper, "functional_malefic_saturn_influences": sat_fm and sat_inf,
            "lean": lean, "rule": "Five or more planets in houses 7-12 or 10-3 lean to self-employment unless functionally "
                                  "malefic Saturn influences the Moon, 10th, 10th lord, lagna or lagna lord (ICAS, S.N. Kapoor; "
                                  "tested on 20 charts, 9/10 and 8/10)", "grade": "C"}


# ------------------------------------------------------------------ build
def build(v, vo, F, jd_birth, birth_utc, now, lat, lon, gender, ayan="lahiri", node="mean", years=5):
    E = Eph(ayan, node)
    ws = now.date() if hasattr(now, "date") else now
    we = ws + dt.timedelta(days=int(years * 365.25))
    j0, j1 = _jd(ws), _jd(we)
    pts, day = reference_points(v, jd_birth, lat, lon, gender)
    lag_nak = nak_of(v["lagna"]["lon"])
    pav = prastara(v)
    for t, tot in vedic.BAV_TOTALS.items():
        assert sum(len(pav[t][s]) for s in range(12)) == tot
    areas, c = area_windows(v, vo, E, pts, ws, we, birth_utc.date())
    fn = vo.get("parashari", {}).get("functional_nature", {})
    out = {
        "window": {"from": ws.isoformat(), "to": we.isoformat()},
        "reference_points": points_public(pts), "birth_is_day": day,
        "nakshatra_tools": nakshatra_tools(v, E, j0, j1, lag_nak),
        "murthis": murthis(v, E, j0, j1),
        "stations": stations(E, j0, j1),
        "kakshyas": kakshyas(E, pav, j0, j1),
        "prastara_ashtakavarga": {t: {SIGNS[s]: pav[t][s] for s in range(12)} for t in pav},
        "transits_over_points": transits_over_points(pts, E, j0, j1),
        "marriage_kn_rao": kn_rao_marriage(c, v, E, ws, we, birth_utc.date()),
        "area_windows": areas,
        "career_style": career_style(v, fn),
        "method": ("Each window needs a Parashari dasha that is eligible for the matter AND the transit confirmation; a "
                   "Jaimini (Narayana or Chara) period sign that also fits is noted. Base rates are this chart's own share of "
                   "months (ages 18-70; 18-45 for marriage) on which each layer is true: a window whose layers are each true "
                   "most of the time is weak evidence. No window promises an event."),
    }
    if "kp" in v:
        out["kp"] = kp_events(v["kp"], v, _jd(ws) + 0.25, lat, lon)
    return out


def tag_life_areas(F, ev):
    """Add the event windows to forecast.life_areas as Vedic '*' indicators."""
    if not F or not F.get("life_areas"):
        return
    amap = {"marriage": "love", "children": "children", "career": "career", "money": "money", "property": "family",
            "abroad": "travel", "education": "learning", "spiritual": "learning"}
    for key, aw in ev["area_windows"].items():
        la = F["life_areas"].get(amap[key])
        if not la:
            continue
        for w in aw["windows"]:
            for s in la["by_slice"]:
                if w["from"] < s["to"] and w["to"] > s["from"]:
                    s["indicators"].append({"system": "Vedic", "tone": "*", "from": w["from"], "to": w["to"],
                                            "text": f"Event window ({key}): eligible dasha {', '.join(w['dasha_periods'])} with "
                                                    f"transit confirmation{' and a fitting Jaimini sign' if w['with_sign_dasha'] else ''}"
                                                    f" (base rate {aw['base_rate_ages_18_70']['dasha+transit']:.0%})",
                                            "ranges": [{"from": w["from"], "to": w["to"]}]})
