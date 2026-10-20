"""chara.py - K.N. Rao's Jaimini Chara dasha, plus the Jaimini helpers his method reads with it.

Rules (K.N. Rao, "Predicting through Jaimini's Chara Dasha", ch. 6; his Chara dasha articles; T.K. Bhowmik, Lesson 1):
  * Order: from the lagna sign, forward if the lagna is Ar, Le, Vi, Li, Aq, Pi; backward if Ta, Ge, Cn, Sc, Sg, Cp.
  * Length: count from the sign to its lord - forward for Ar Ta Ge Li Sc Sg, backward for Cn Le Vi Cp Aq Pi - minus one.
    Lord in its own sign = 12. No +1/-1 for exaltation or debilitation; whole years, no fractions.
  * Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu): one lord in the sign -> use the other; both in it -> 12;
    both outside -> the lord with more planets beside it, then the higher degree in its sign (then minutes, seconds).
  * Second cycle repeats the first. Sub-periods: 12 per period, same direction, starting from the next sign; the
    period sign's own sub-period comes last. Sub-sub-periods follow the same rule one level down.
  * Rao's published charts use the true node, so Rahu and Ketu are taken from the true node here.
Verified against Rao's own period lists for Elizabeth II, Rajiv Gandhi and Amitabh Bachchan (verify_engine.py).
"""
import datetime as dt

import swisseph as swe

from common import SIGNS, n360, sign_of, deg_in_sign, jd_to_dt

ORDER_FORWARD = {0, 4, 5, 6, 10, 11}      # lagna signs whose dasha sequence runs forward
COUNT_FORWARD = {0, 1, 2, 6, 7, 8}        # signs counted forward to their lord (savya)
LORD = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury", 6: "Venus",
        8: "Jupiter", 9: "Saturn", 11: "Jupiter"}
DUAL = {7: ("Mars", "Ketu"), 10: ("Saturn", "Rahu")}
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
STHIRA = {"Sun": "father (stronger of Sun and Venus in some texts)", "Moon": "mother (stronger of Moon and Mars in some texts)",
          "Mars": "siblings", "Mercury": "maternal relatives", "Jupiter": "children, teacher",
          "Venus": "spouse", "Saturn": "longevity, servants"}
STHIRA_HI = {"Sun": "पिता", "Moon": "माता", "Mars": "भाई-बहन", "Mercury": "मामा पक्ष", "Jupiter": "संतान, गुरु",
             "Venus": "जीवनसाथी", "Saturn": "आयु, सेवक"}


def true_node_positions(jd, ayan_mode):
    swe.set_sid_mode(ayan_mode)
    r = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
    return r, n360(r + 180)


def _add_years(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:
        return d.replace(year=d.year + n, day=28)


def period_lord(sign, si, deg):
    """Lord used for counting the dasha length of `sign`, with the reason (Rao's rules)."""
    if sign not in DUAL:
        return LORD[sign], ""
    a, b = DUAL[sign]
    ia, ib = si[a] == sign, si[b] == sign
    if ia and ib:
        return None, f"both {a} and {b} in {SIGNS[sign]}: 12 years"
    if ia:
        return b, f"{a} is in {SIGNS[sign]}, so count to {b}"
    if ib:
        return a, f"{b} is in {SIGNS[sign]}, so count to {a}"

    def company(p):
        return sum(1 for q in NINE if q != p and si[q] == si[p])
    ca, cb = company(a), company(b)
    if ca != cb:
        w = a if ca > cb else b
        return w, f"{w} has more planets beside it ({max(ca, cb)} against {min(ca, cb)})"
    w = a if deg[a] >= deg[b] else b
    return w, f"equal company ({ca}); {w} has the higher degree in its sign"


def dasha_years(sign, si, deg):
    lord, why = period_lord(sign, si, deg)
    if lord is None:
        return 12, None, why
    d = (si[lord] - sign) % 12 if sign in COUNT_FORWARD else (sign - si[lord]) % 12
    return (12 if d == 0 else d), lord, why


def _subs(sign, step):
    return [(sign + step * k) % 12 for k in range(1, 13)]   # next sign first, own sign last


def build_chara(planets, lag_sign, jd, birth_utc, now_utc, ayan_mode, horizon_years=5):
    si = {p: planets[p]["sign_index"] for p in NINE}
    deg = {p: planets[p]["deg_in_sign"] for p in NINE}
    rl, kl = true_node_positions(jd, ayan_mode)
    si["Rahu"], si["Ketu"] = sign_of(rl), sign_of(kl)
    deg["Rahu"], deg["Ketu"] = deg_in_sign(rl), deg_in_sign(kl)
    step = 1 if lag_sign in ORDER_FORWARD else -1
    seq = [(lag_sign + step * k) % 12 for k in range(12)]
    first = []
    for s in seq:
        yrs, lord, why = dasha_years(s, si, deg)
        own = lord is not None and si[lord] == s
        first.append({"sign": SIGNS[s], "sign_index": s, "years": yrs, "lord_used": lord, "lord_in_own_sign": own,
                      "counted": "forward" if s in COUNT_FORWARD else "backward", "note": why})
    mahas, start, cyc = [], birth_utc, 1
    while start < _add_years(birth_utc, 120):
        for f in first:
            end = _add_years(start, f["years"])
            mahas.append(dict(f, cycle=cyc, start=start, end=end))
            start = end
            if start >= _add_years(birth_utc, 120):
                break
        cyc += 1

    def split(s_idx, a, b):
        ln = (b - a) / 12
        return [(x, a + ln * i, a + ln * (i + 1)) for i, x in enumerate(_subs(s_idx, step))]

    current = {}
    for m in mahas:
        if m["start"] <= now_utc < m["end"]:
            current["mahadasha"] = {"sign": m["sign"], "start": m["start"].date().isoformat(), "end": m["end"].date().isoformat()}
            for x, a, b in split(m["sign_index"], m["start"], m["end"]):
                if a <= now_utc < b:
                    current["antardasha"] = {"sign": SIGNS[x], "start": a.date().isoformat(), "end": b.date().isoformat()}
                    for y, c, e in split(x, a, b):
                        if c <= now_utc < e:
                            current["pratyantar"] = {"sign": SIGNS[y], "start": c.date().isoformat(), "end": e.date().isoformat()}
                    break
    win_end = _add_years(now_utc, horizon_years)
    window = []
    for m in mahas:
        if m["end"] <= now_utc or m["start"] >= win_end:
            continue
        for x, a, b in split(m["sign_index"], m["start"], m["end"]):
            if b > now_utc and a < win_end:
                window.append({"maha": m["sign"], "antar": SIGNS[x], "start": a.date().isoformat(), "end": b.date().isoformat()})
    out_mahas = [{"sign": m["sign"], "years": m["years"], "cycle": m["cycle"], "lord_used": m["lord_used"],
                  "lord_in_own_sign": m["lord_in_own_sign"],
                  "counted": m["counted"], "note": m["note"], "start": m["start"].date().isoformat(),
                  "end": m["end"].date().isoformat()} for m in mahas]
    return {"system": "K.N. Rao Chara dasha", "direction": "forward" if step == 1 else "backward",
            "first_cycle": [{k: f[k] for k in ("sign", "years", "lord_used", "lord_in_own_sign", "counted", "note")} for f in first],
            "mahadashas": out_mahas, "current": current, "antardashas_in_window": window,
            "nodes_used": {"Rahu": f"{SIGNS[si['Rahu']]} {deg['Rahu']:.2f}", "Ketu": f"{SIGNS[si['Ketu']]} {deg['Ketu']:.2f}",
                           "node": "true"},
            "conventions": ("Lagna-group order; count to lord minus one; own sign 12; no exaltation adjustment; whole years from "
                            "the birth date; second cycle repeats the first; 12 equal sub-periods from the next sign, own sign "
                            "last; Scorpio/Aquarius by Rao's rules; true node (as in Rao's published charts).")}


# ---------------------------------------------------------------- Jaimini helpers
RASI_EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}


def rasi_aspects(sign):
    """Signs a sign aspects by Jaimini rasi drishti."""
    mode = sign % 3
    if mode == 0:   # movable -> fixed except the adjacent one
        return [s for s in range(12) if s % 3 == 1 and s != (sign + 1) % 12]
    if mode == 1:   # fixed -> movable except the adjacent one
        return [s for s in range(12) if s % 3 == 0 and s != (sign - 1) % 12]
    return [s for s in range(12) if s % 3 == 2 and s != sign]


def pvr_stronger_colord(sign, si, deg, tiebreak=None):
    """PVR 15.5.1 stronger co-lord (steps 1-4; step 5b advancement, or `tiebreak(a, b)` for 5a when given)."""
    a, b = DUAL[sign]
    if si[a] == sign and si[b] != sign:
        return b
    if si[b] == sign and si[a] != sign:
        return a
    comp = {p: sum(1 for q in NINE if q != p and si[q] == si[p]) for p in (a, b)}
    if comp[a] != comp[b]:
        return max((a, b), key=lambda p: comp[p])

    def helpers(p):
        disp = LORD.get(si[p]) or DUAL[si[p]][0]
        n = 0
        for h in ("Jupiter", "Mercury", disp):
            if h == p:
                continue
            if si[h] == si[p] or si[p] in rasi_aspects(si[h]):
                n += 1
        return n
    ha, hb = helpers(a), helpers(b)
    if ha != hb:
        return a if ha > hb else b
    ea, eb = si[a] == RASI_EXALT[a], si[b] == RASI_EXALT[b]
    if ea != eb:
        return a if ea else b
    ra, rb = si[a] % 3, si[b] % 3   # 2 dual > 1 fixed > 0 movable
    if ra != rb:
        return a if ra > rb else b

    if tiebreak is not None:
        return tiebreak(a, b)

    def adv(p):
        return 30 - deg[p] if p in ("Rahu", "Ketu") else deg[p]
    return a if adv(a) >= adv(b) else b


def arudhas(si, deg, lag_sign, school):
    res = {}
    for h in range(1, 13):
        hs = (lag_sign + h - 1) % 12
        if hs in DUAL:
            lord = pvr_stronger_colord(hs, si, deg) if school == "pvr" else (period_lord(hs, si, deg)[0] or DUAL[hs][0])
        else:
            lord = LORD[hs]
        n = (si[lord] - hs) % 12 + 1
        a = (si[lord] + n - 1) % 12
        if school == "pvr" and (a == hs or a == (hs + 6) % 12):
            a = (a + 9) % 12
        res[f"A{h}"] = SIGNS[a]
    res["AL (Arudha Lagna)"], res["UL (Upapada Lagna)"] = res["A1"], res["A12"]
    return res


def jaimini_extras(planets, lag_sign, k7, varga_sign):
    si = {p: planets[p]["sign_index"] for p in NINE}
    deg = {p: planets[p]["deg_in_sign"] for p in NINE}
    dk, pk, ak = k7["Darakaraka"], k7["Putrakaraka"], k7["Atmakaraka"]
    dkn = varga_sign(planets[dk]["lon"], 9)
    kl = varga_sign(planets[ak]["lon"], 9)
    return {
        "sthira_karakas": {p: {"signifies": STHIRA[p], "signifies_hi": STHIRA_HI[p], "sign": planets[p]["sign"],
                               "house": planets[p]["house"]} for p in STHIRA},
        "karakamsha_in_rasi": {"sign": SIGNS[kl], "house_from_lagna": (kl - lag_sign) % 12 + 1},
        "darakaraka_navamsa_DKN": {"darakaraka": dk, "sign": SIGNS[dkn], "house_from_lagna": (dkn - lag_sign) % 12 + 1},
        "putrakaraka": {"planet": pk, "sign": planets[pk]["sign"], "house": planets[pk]["house"]},
        "arudha_padas_pvr": arudhas(si, deg, lag_sign, "pvr"),
        "arudha_padas_rao": arudhas(si, deg, lag_sign, "rao"),
        "pada_conventions": ("PVR: a pada in the house or the 7th from it moves to the 10th from there; Scorpio/Aquarius use the "
                             "stronger co-lord (PVR 15.5.1). Rao: no exception ('For padas I decided not to use any exception'); "
                             "Scorpio/Aquarius use his Chara dasha co-lord rule. Mean-node degrees are used here."),
    }
