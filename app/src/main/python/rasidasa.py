"""rasidasa.py - Parashari/Jaimini sign dashas and helpers from P.V.R. Narasimha Rao, "Vedic Astrology: An
Integrated Approach" (cited as PVR with section numbers).

  special_lagnas   BL, HL, GL (PVR 5.2-5.4, upper-limb sunrise as PVR 5.5 recommends) and Sree Lagna (5.7)
  stronger_rasi    PVR 15.5.2 rules 1-6;  stronger co-lord of Sc/Aq: PVR 15.5.1 (in chara.pvr_stronger_colord)
  argala           PVR 10.5-10.6 (2nd/4th/11th primary, 5th secondary; 12/10/3/9 obstruct; Ketu reverses;
                   several malefics in the 3rd give argala instead of obstruction)
  narayana         PVR 18.2-18.3 and 18.5 (vargas); Table 40 progressions with Saturn and Ketu exceptions
  kendradi         Lagna Kendradi rasi dasa, PVR 19.2
  sudasa           Sree Lagna kendradi dasa, PVR 20.2 (first dasa balance from SL's advancement)
  drigdasa         PVR 21.2
  kalachakra       PVR 24.2, Tables 44-48
"""
import datetime as dt

import swisseph as swe

from common import SIGNS, NAK_SPAN, n360, sign_of, deg_in_sign, jd_to_dt, dt_to_jd
import chara

NINE = chara.NINE
LORD = chara.LORD
ODD_FOOTED = {0, 1, 2, 6, 7, 8}
EXALT_SIGN = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6,
              "Rahu": 1, "Ketu": 7}
DEBIL_SIGN = {p: (s + 6) % 12 for p, s in EXALT_SIGN.items()}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
YEAR = 365.25
KC_YEAR = 360.0   # savana years for Kalachakra: reproduces PVR Example 130 (Pi May 1995, Ar Apr 1997, Ta Aug 1998)


def _add_years(d, yrs):
    """Whole years by calendar anniversary (as PVR's dated examples), any fraction in 365.25-day years."""
    whole = int(yrs)
    try:
        d2 = d.replace(year=d.year + whole)
    except ValueError:
        d2 = d.replace(year=d.year + whole, day=28)
    return d2 + dt.timedelta(days=(yrs - whole) * YEAR)


# ------------------------------------------------------------------ special lagnas
def special_lagnas(jd_birth, lat, lon, asc_lon, moon_lon, ayan_mode):
    """BL, HL, GL from the Sun at the preceding sunrise (upper limb, refraction); SL from lagna + Moon's nakshatra fraction."""
    swe.set_sid_mode(ayan_mode)
    start = jd_birth - 1.2
    sr = None
    for k in range(3):
        r = swe.rise_trans(start + k * 0.5, swe.SUN, swe.CALC_RISE, (lon, lat, 0.0), 1013.25, 15.0)
        if r[0] >= 0 and r[1][0] <= jd_birth:
            sr = r[1][0] if sr is None or r[1][0] > sr else sr
    if sr is None:
        return {"note": "No sunrise found (polar latitude); BL, HL and GL not computed.",
                "SL": _fmt(n360(asc_lon + ((moon_lon % NAK_SPAN) / NAK_SPAN) * 360))}
    sun_sr = swe.calc_ut(sr, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
    mins = (jd_birth - sr) * 1440.0
    bl, hl, gl = n360(sun_sr + mins), n360(sun_sr + mins / 2), n360(sun_sr + mins * 5 / 4)
    sl = n360(asc_lon + ((moon_lon % NAK_SPAN) / NAK_SPAN) * 360)
    return {"sunrise_utc": jd_to_dt(sr).strftime("%Y-%m-%d %H:%M:%S"), "sun_at_sunrise": _fmt(sun_sr),
            "BL": _fmt(bl), "HL": _fmt(hl), "GL": _fmt(gl), "SL": _fmt(sl),
            "_lon": {"BL": bl, "HL": hl, "GL": gl, "SL": sl},
            "note": "GL moves 1.25 degrees per minute of birth time and HL 0.5; use them only with a reliable time."}


def _fmt(l):
    d = deg_in_sign(l)
    return {"sign": SIGNS[sign_of(l)], "deg": round(d, 3), "lon": round(l, 4)}


# ------------------------------------------------------------------ strength
def rasi_aspected_by(sign):
    return chara.rasi_aspects(sign)          # rasi drishti is mutual


def _lord(sign, si, deg, purpose="dasa"):
    if sign in chara.DUAL:
        return chara.pvr_stronger_colord(sign, si, deg)
    return LORD[sign]


def stronger_rasi(a, b, si, deg):
    """PVR 15.5.2. Returns the stronger sign index and the rule that decided."""
    occ = {s: [p for p in NINE if si[p] == s] for s in (a, b)}
    if len(occ[a]) != len(occ[b]):
        return (a if len(occ[a]) > len(occ[b]) else b), "more planets in the sign (rule 1)"

    def cnt(s):
        lord = _lord(s, si, deg)
        n = 0
        for p in ("Jupiter", "Mercury", lord):
            if si[p] == s or s in rasi_aspected_by(si[p]):
                n += 1
        return n
    ca, cb = cnt(a), cnt(b)
    if ca != cb:
        return (a if ca > cb else b), "more of Jupiter, Mercury and its lord occupy or aspect it (rule 2)"
    ea = any(EXALT_SIGN[p] == a for p in occ[a])
    eb = any(EXALT_SIGN[p] == b for p in occ[b])
    if ea != eb:
        return (a if ea else b), "contains an exalted planet (rule 3)"
    la, lb = _lord(a, si, deg), _lord(b, si, deg)
    da, db = (si[la] % 2) != (a % 2), (si[lb] % 2) != (b % 2)
    if da != db:
        return (a if da else b), "its lord sits in a sign of different oddity (rule 4)"
    if a % 3 != b % 3:
        return (a if a % 3 > b % 3 else b), "natural strength: dual > fixed > movable (rule 5)"

    def adv(p):
        return 30 - deg[p] if p in ("Rahu", "Ketu") else deg[p]
    return (a if adv(la) >= adv(lb) else b), "its lord is more advanced in its sign (rule 6)"


# ------------------------------------------------------------------ argala
def argala(si, lag_sign):
    """Argala and virodhargala on each house (sign) from planets, PVR 10.5-10.6."""
    out = {}
    for h in range(1, 13):
        s = (lag_sign + h - 1) % 12
        step = -1 if si["Ketu"] == s else 1

        def at(n):
            t = (s + step * (n - 1)) % 12
            return [p for p in NINE if si[p] == t]
        rows = []
        for n, obs, kind in ((2, 12, "primary"), (4, 10, "primary"), (11, 3, "primary"), (5, 9, "secondary")):
            a_pl, o_pl = at(n), at(obs)
            if n == 11:
                mal3 = [p for p in o_pl if p not in BENEFICS]
                if len(mal3) >= 2:          # several malefics in the 3rd cause argala instead of obstruction
                    a_pl = a_pl + mal3
                    o_pl = [p for p in o_pl if p in BENEFICS]
            if not a_pl:
                continue
            state = "unobstructed" if not o_pl else ("obstructed" if len(o_pl) >= len(a_pl) else "stronger than its obstruction")
            rows.append({"from_house": n, "kind": kind, "planets": a_pl,
                         "nature": "benefic" if all(p in BENEFICS for p in a_pl) else (
                             "malefic" if not any(p in BENEFICS for p in a_pl) else "mixed"),
                         "obstructed_by": o_pl, "obstruction_from_house": obs, "state": state})
        out[f"H{h}"] = {"sign": SIGNS[s], "counted": "backward (Ketu in the sign)" if step < 0 else "forward",
                        "argalas": rows}
    return out


# ------------------------------------------------------------------ Narayana-style lengths
def nara_years(sign, si, deg):
    """Narayana dasa length of `sign` (PVR 18.2.2), with the lord used (Sc/Aq: stronger co-lord, 15.5.1 with 5a)."""
    if sign in chara.DUAL:
        lord = chara.pvr_stronger_colord(sign, si, deg,
                                         tiebreak=lambda a, b: a if _len(sign, a, si) >= _len(sign, b, si) else b)
    else:
        lord = LORD[sign]
    return _len(sign, lord, si), lord


def _len(sign, lord, si):
    d = (si[lord] - sign) % 12 if sign in ODD_FOOTED else (sign - si[lord]) % 12
    if d == 0:
        return 12
    yrs = d
    if si[lord] == EXALT_SIGN.get(lord):
        yrs += 1
    elif si[lord] == DEBIL_SIGN.get(lord):
        yrs -= 1
    return max(yrs, 1)


# ------------------------------------------------------------------ Narayana
def narayana_sequence(seed, si):
    sat, ket = si["Saturn"] == seed, si["Ketu"] == seed
    if sat:
        return [(seed + k) % 12 for k in range(12)], "Saturn in the seed: forward, one sign at a time"
    fwd = ((seed + 8) % 12) in ODD_FOOTED
    if ket:
        fwd = not fwd
    st = 1 if fwd else -1
    mode = seed % 3
    if mode == 0:
        seq = [(seed + st * k) % 12 for k in range(12)]
    elif mode == 1:
        seq = [(seed + st * 5 * k) % 12 for k in range(12)]
    else:
        seq = []
        for q in (0, 9, 6, 3):                 # trines of the seed, then of the 10th, 7th and 4th from it
            base = (seed + st * q) % 12
            seq += [(base + st * t) % 12 for t in (0, 4, 8)]
    note = ("forward" if fwd else "backward") + (" (Ketu in the seed reverses it)" if ket else "")
    return seq, note


def _antar_seq(dasa_sign, si, deg):
    seed, why = stronger_rasi(dasa_sign, (dasa_sign + 6) % 12, si, deg)
    start = si[_lord(seed, si, deg)]
    fwd = start % 2 == 0          # sign index even = odd sign (Ar=0)
    if si["Saturn"] == seed:
        fwd = True
    elif si["Ketu"] == seed:
        fwd = not fwd
    st = 1 if fwd else -1
    return [(start + st * k) % 12 for k in range(12)]


def _periods(seq, years, birth, first_fraction=1.0, two_cycles=True, si=None, deg=None, antars=True):
    out, t = [], birth
    cycles = [(1, years)]
    if two_cycles:
        cycles.append((2, [12 - y if 12 - y > 0 else 12 for y in years]))
    for cyc, ys in cycles:
        for i, (s, y) in enumerate(zip(seq, ys)):
            ln = y * (first_fraction if (cyc == 1 and i == 0) else 1.0)
            end = _add_years(t, ln)
            rec = {"sign": SIGNS[s], "years": y, "cycle": cyc, "start": t, "end": end}
            if antars and si is not None:
                rec["_antar"] = _antar_seq(s, si, deg)
            out.append(rec)
            t = end
    return out


def _current(periods, now, full_len):
    cur = {}
    for p in periods:
        if p["start"] <= now < p["end"]:
            cur["dasa"] = {"sign": p["sign"], "start": p["start"].date().isoformat(), "end": p["end"].date().isoformat()}
            if "_antar" in p:
                full = dt.timedelta(days=p["years"] * YEAR)
                a0 = p["end"] - full          # antardashas span the full dasa even when the first is partly elapsed
                ln = full / 12
                for k, s in enumerate(p["_antar"]):
                    a, b = a0 + ln * k, a0 + ln * (k + 1)
                    if a <= now < b:
                        cur["antardasa"] = {"sign": SIGNS[s], "start": a.date().isoformat(), "end": b.date().isoformat()}
            break
    return cur


def _public(periods):
    return [{"sign": p["sign"], "years": p["years"], "cycle": p["cycle"],
             "start": p["start"].date().isoformat(), "end": p["end"].date().isoformat()} for p in periods]


def narayana(si, deg, lag_sign, birth, now, label="D-1"):
    seed, why = stronger_rasi(lag_sign, (lag_sign + 6) % 12, si, deg)
    seq, note = narayana_sequence(seed, si)
    yl = [nara_years(s, si, deg) for s in seq]
    per = _periods(seq, [y for y, _ in yl], birth, si=si, deg=deg)
    return {"chart": label, "seed": SIGNS[seed], "seed_reason": why, "direction": note,
            "first_cycle": [{"sign": SIGNS[s], "years": y, "lord_used": l} for s, (y, l) in zip(seq, yl)],
            "dasas": _public(per), "current": _current(per, now, None)}


def narayana_varga(planets_varga_si, deg, rasi_si, rasi_lag, n, birth, now):
    """PVR 18.5: lagna for D-n = sign occupied in D-n by the lord of the nth house of the rasi chart."""
    seed_house_sign = (rasi_lag + (n - 1) % 12) % 12
    lord = chara.pvr_stronger_colord(seed_house_sign, rasi_si, deg) if seed_house_sign in chara.DUAL else LORD[seed_house_sign]
    vlag = planets_varga_si[lord]
    r = narayana(planets_varga_si, deg, vlag, birth, now, label=f"D-{n}")
    r["varga_lagna_used"] = f"{SIGNS[vlag]} ({lord}, lord of rasi house {(n - 1) % 12 + 1}, in D-{n})"
    return r


# ------------------------------------------------------------------ kendradi family
def _kendradi_seq(seed, fwd):
    st = 1 if fwd else -1
    return [(seed + st * k) % 12 for grp in ((0, 3, 6, 9), (1, 4, 7, 10), (2, 5, 8, 11)) for k in grp]


def lagna_kendradi(si, deg, lag_sign, birth, now):
    seed, why = stronger_rasi(lag_sign, (lag_sign + 6) % 12, si, deg)
    fwd = lag_sign % 2 == 0
    if si["Saturn"] == seed:
        fwd = True
    elif si["Ketu"] == seed:
        fwd = not fwd
    seq = _kendradi_seq(seed, fwd)
    yl = [nara_years(s, si, deg) for s in seq]
    per = _periods(seq, [y for y, _ in yl], birth, antars=False)
    return {"seed": SIGNS[seed], "seed_reason": why, "direction": "forward" if fwd else "backward",
            "first_cycle": [{"sign": SIGNS[s], "years": y, "lord_used": l} for s, (y, l) in zip(seq, yl)],
            "dasas": _public(per), "current": _current(per, now, None)}


def sudasa(si, deg, sl_lon, birth, now):
    s0 = sign_of(sl_lon)
    fwd = s0 % 2 == 0
    seq = _kendradi_seq(s0, fwd)
    yl = [nara_years(s, si, deg) for s in seq]
    frac = (30 - deg_in_sign(sl_lon)) / 30.0
    per = _periods(seq, [y for y, _ in yl], birth, first_fraction=frac, antars=False)
    return {"start_sign": SIGNS[s0], "sree_lagna_deg": round(deg_in_sign(sl_lon), 3), "direction": "forward" if fwd else "backward",
            "first_dasa_balance_fraction": round(frac, 4),
            "first_cycle": [{"sign": SIGNS[s], "years": y, "lord_used": l} for s, (y, l) in zip(seq, yl)],
            "dasas": _public(per), "current": _current(per, now, None)}


def drigdasa(si, deg, lag_sign, birth, now):
    seq = []
    for h in (9, 10, 11):
        s = (lag_sign + h - 1) % 12
        st = 1 if s in ODD_FOOTED else -1
        asp = set(chara.rasi_aspects(s))
        seq.append(s)
        seq += [(s + st * k) % 12 for k in range(1, 12) if (s + st * k) % 12 in asp]
    yl = [nara_years(s, si, deg) for s in seq]
    per = _periods(seq, [y for y, _ in yl], birth, antars=False)
    return {"first_cycle": [{"sign": SIGNS[s], "years": y, "lord_used": l} for s, (y, l) in zip(seq, yl)],
            "dasas": _public(per), "current": _current(per, now, None)}


# ------------------------------------------------------------------ Kalachakra
KC_YEARS = {"Sun": 5, "Moon": 21, "Mars": 7, "Mercury": 9, "Jupiter": 10, "Venus": 16, "Saturn": 4}
_S = {n: i for i, n in enumerate(["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"])}
KC = {
    "S1": ["Ar Ta Ge Cn Le Vi Li Sc Sg", "Cp Aq Pi Sc Li Vi Cn Le Ge", "Ta Ar Pi Aq Cp Sg Ar Ta Ge", "Cn Le Vi Li Sc Sg Cp Aq Pi"],
    "S2": ["Sc Li Vi Cn Le Ge Ta Ar Pi", "Aq Cp Sg Ar Ta Ge Cn Le Vi", "Li Sc Sg Cp Aq Pi Sc Li Vi", "Cn Le Ge Ta Ar Pi Aq Cp Sg"],
    "A1": ["Sg Cp Aq Pi Ar Ta Ge Le Cn", "Vi Li Sc Pi Aq Cp Sg Sc Li", "Vi Le Cn Ge Ta Ar Sg Cp Aq", "Pi Ar Ta Ge Le Cn Vi Li Sc"],
    "A2": ["Pi Aq Cp Sg Sc Li Vi Le Cn", "Ge Ta Ar Sg Cp Aq Pi Ar Ta", "Ge Le Cn Vi Li Sc Pi Aq Cp", "Sg Sc Li Vi Le Cn Ge Ta Ar"],
}
KC_PARAMAYUSH = {"S1": [100, 85, 83, 86], "S2": [100, 85, 83, 86], "A1": [86, 83, 85, 100], "A2": [86, 83, 85, 100]}
# 27 nakshatras: S1 = Ashwini, Krittika, Punarvasu, Ashlesha, Hasta, Swati, Mula, U.Ashadha, P.Bhadra;
# S2 = Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (PVR's Table 45 prints Revati here and omits U.Bhadrapada;
# the wheel's pattern - the middle star of each savya triple starts the mirrored half - puts U.Bhadra in S2, Revati in S1); A1 = Rohini, Magha, Vishakha, Shravana;
# A2 = Mrigashira, Ardra, P.Phalguni, U.Phalguni, Anuradha, Jyeshtha, Dhanishta, Shatabhisha.
KC_GROUP = {0: "S1", 1: "S2", 2: "S1", 3: "A1", 4: "A2", 5: "A2", 6: "S1", 7: "S2", 8: "S1", 9: "A1", 10: "A2", 11: "A2",
            12: "S1", 13: "S2", 14: "S1", 15: "A1", 16: "A2", 17: "A2", 18: "S1", 19: "S2", 20: "S1", 21: "A1",
            22: "A2", 23: "A2", 24: "S1", 25: "S2", 26: "S1"}


def _kc_years(s):
    return KC_YEARS[LORD.get(s) or {7: "Mars", 10: "Saturn"}[s]]


def _kc_stream(group):
    """Continuous 72-sign stream for a savya or apasavya family (pada 4 of one sub-group leads to pada 1 of the other)."""
    order = ["S1", "S2"] if group[0] == "S" else ["A1", "A2"]
    out = []
    for g in order:
        for p in range(4):
            out += [(_S[x], g, p) for x in KC[g][p].split()]
    return out


def kalachakra(moon_lon, birth, now, horizon_years=5):
    ni = int(n360(moon_lon) // NAK_SPAN)
    pada = int((n360(moon_lon) % NAK_SPAN) // (NAK_SPAN / 4))
    frac = ((n360(moon_lon) % NAK_SPAN) % (NAK_SPAN / 4)) / (NAK_SPAN / 4)
    g = KC_GROUP[ni]
    block = [_S[x] for x in KC[g][pada].split()]
    para = sum(_kc_years(s) for s in block)
    assert para == KC_PARAMAYUSH[g][pada], (g, pada, para)
    elapsed = frac * para
    stream = _kc_stream(g)
    base = next(i for i, (s, gg, pp) in enumerate(stream) if gg == g and pp == pada)
    acc, idx = 0.0, 0
    while acc + _kc_years(block[idx]) <= elapsed:
        acc += _kc_years(block[idx])
        idx += 1
    pos = base + idx
    done_in_first = elapsed - acc
    t = birth - dt.timedelta(days=done_in_first * KC_YEAR)
    dasas = []
    k = 0
    while t < birth + dt.timedelta(days=110 * KC_YEAR):
        s = stream[(pos + k) % len(stream)][0]
        y = _kc_years(s)
        end = t + dt.timedelta(days=y * KC_YEAR)
        ants, a = [], t
        nine = [stream[(pos + k + j) % len(stream)][0] for j in range(9)]
        tot = sum(_kc_years(x) for x in nine)
        for x in nine:
            b = a + dt.timedelta(days=y * KC_YEAR * _kc_years(x) / tot)
            ants.append({"sign": SIGNS[x], "start": max(a, birth).date().isoformat(), "end": b.date().isoformat(), "_a": a, "_b": b})
            a = b
        dasas.append({"sign": SIGNS[s], "years": y, "start": max(t, birth).date().isoformat(), "end": end.date().isoformat(),
                      "_s": t, "_e": end, "antardasas": ants})
        t = end
        k += 1
    first9 = [stream[(pos + j) % len(stream)][0] for j in range(9)]
    savya = g[0] == "S"
    cur = {}
    for d in dasas:
        if d["_s"] <= now < d["_e"]:
            cur["dasa"] = {"sign": d["sign"], "start": d["start"], "end": d["end"]}
            for a in d["antardasas"]:
                if a["_a"] <= now < a["_b"]:
                    cur["antardasa"] = {"sign": a["sign"], "start": a["start"], "end": a["end"]}
    win_end = _add_years(now, horizon_years)
    for d in dasas:
        for a in d["antardasas"]:
            a.pop("_a"), a.pop("_b")
        d["antardasas"] = [a for a in d["antardasas"] if a["end"] > now.date().isoformat() and a["start"] < win_end.date().isoformat()] \
            if d["_e"] > now and d["_s"] < win_end else []
        d.pop("_s"), d.pop("_e")
    return {"moon_nakshatra_pada": f"{ni + 1}:{pada + 1}", "group": {"S1": "Savya-1", "S2": "Savya-2", "A1": "Apasavya-1",
                                                                     "A2": "Apasavya-2"}[g],
            "paramayush": para, "elapsed_at_birth_years": round(elapsed, 3),
            "deha_rasi": SIGNS[first9[0] if savya else first9[8]], "jeeva_rasi": SIGNS[first9[8] if savya else first9[0]],
            "dasas": dasas, "current": cur,
            "conventions": "PVR 24.2, Tables 44-48; 360-day savana years, as in PVR's dated examples (Example 130 reproduced).",
            "reliability": "Each minute of birth-time error moves these dates by about as many days as the paramayush in years."}


# ------------------------------------------------------------------ orchestrator
def build(planets, vargas_si, lag_sign, asc_lon, jd, birth_utc, now_utc, lat, lon, ayan_mode, time_confidence="reliable"):
    si = {p: planets[p]["sign_index"] for p in NINE}
    deg = {p: planets[p]["deg_in_sign"] for p in NINE}
    spl = special_lagnas(jd, lat, lon, asc_lon, planets["Moon"]["lon"], ayan_mode)
    out = {"special_lagnas": {k: v for k, v in spl.items() if k != "_lon"},
           "argala": argala(si, lag_sign),
           "narayana": {"D-1": narayana(si, deg, lag_sign, birth_utc, now_utc)},
           "lagna_kendradi": lagna_kendradi(si, deg, lag_sign, birth_utc, now_utc),
           "sudasa": sudasa(si, deg, spl["_lon"]["SL"] if "_lon" in spl else spl["SL"]["lon"], birth_utc, now_utc),
           "drigdasa": drigdasa(si, deg, lag_sign, birth_utc, now_utc),
           "kalachakra": kalachakra(planets["Moon"]["lon"], birth_utc, now_utc)}
    for n in (9, 10, 4):
        vs = vargas_si.get(n)
        if vs:
            out["narayana"][f"D-{n}"] = narayana_varga(vs, deg, si, lag_sign, n, birth_utc, now_utc)
    out["conventions"] = ("Sign dashas follow PVR: Narayana (18.2-18.5) with Saturn/Ketu exceptions, exaltation +1, "
                          "debilitation -1 and second cycle = 12 - first; Kendradi, Sudasa and Drigdasa lengths as Narayana; "
                          "stronger sign and co-lord by PVR 15.5. Dasa years of 365.25 days.")
    if time_confidence in ("unknown", "approximate"):
        out["reliability_warning"] = ("Birth time is " + time_confidence + ": the seeds of Narayana, Kendradi and Drigdasa depend on "
                                      "the lagna, Sudasa on Sree Lagna, and Kalachakra dates on the Moon's exact position.")
    return out
