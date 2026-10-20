"""vedic.py - deterministic Jyotish calculations (Parashari core, Jaimini, KP, Tajik).

Conventions are explicit and reported in the audit block: sidereal zodiac,
whole-sign houses for the main chart, Sripati/Porphyry for Bhava Chalit,
mean node by default. Nothing here interprets - it emits facts for the reader.
"""
import datetime as dt
import swisseph as swe
from common import (SIGNS, SIGN_LORD, NAK_SPAN, VIM_ORDER, WEEKDAY_LORD, n360,
                    sign_of, deg_in_sign, wrap180, dms, fmt_pos, nak_info,
                    jd_to_dt, dt_to_jd)

AYAN = {"lahiri": swe.SIDM_LAHIRI, "true_chitra": swe.SIDM_TRUE_CITRA,
        "krishnamurti": swe.SIDM_KRISHNAMURTI, "raman": swe.SIDM_RAMAN}
PLANETS7 = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
            ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
            ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]
ORDER9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

EXALT = {"Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
         "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20)}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10]}
MOOLA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 15, 20),
         "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
FRIENDS = {"Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
           "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
           "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
           "Saturn": ["Mercury", "Venus"]}
ENEMIES = {"Sun": ["Venus", "Saturn"], "Moon": [], "Mars": ["Mercury"],
           "Mercury": ["Moon"], "Jupiter": ["Mercury", "Venus"],
           "Venus": ["Sun", "Moon"], "Saturn": ["Sun", "Moon", "Mars"]}
COMBUST_ORB = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11, "Venus": 10, "Saturn": 15}
COMBUST_ORB_RETRO = {"Mercury": 12, "Venus": 8}


# ----------------------------------------------------------------- positions
def sidereal_positions(jd, ayan="lahiri", node="mean"):
    swe.set_sid_mode(AYAN[ayan])
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for name, pid in PLANETS7:
        xx, _ = swe.calc_ut(jd, pid, fl)
        out[name] = {"lon": xx[0], "lat": xx[1], "speed": xx[3]}
    xx, _ = swe.calc_ut(jd, swe.MEAN_NODE if node == "mean" else swe.TRUE_NODE, fl)
    out["Rahu"] = {"lon": xx[0], "lat": 0.0, "speed": xx[3]}
    out["Ketu"] = {"lon": n360(xx[0] + 180.0), "lat": 0.0, "speed": xx[3]}
    return out


def sidereal_angles(jd, lat, lon, ayan="lahiri", hsys=b"W"):
    swe.set_sid_mode(AYAN[ayan])
    cusps, ascmc = swe.houses_ex(jd, lat, lon, hsys, swe.FLG_SIDEREAL)
    return list(cusps), ascmc[0], ascmc[1]


def dignity(name, lon):
    if name not in EXALT:
        return "n/a"
    s, d = sign_of(lon), deg_in_sign(lon)
    es, _ = EXALT[name]
    if s == es:
        return "exalted"
    if s == (es + 6) % 12:
        return "debilitated"
    ms, a, b = MOOLA[name]
    if s == ms and a <= d < b:
        return "moolatrikona"
    if s in OWN[name]:
        return "own sign"
    lord = SIGN_LORD[s]
    if lord in FRIENDS[name]:
        return "friend's sign"
    if lord in ENEMIES[name]:
        return "enemy's sign"
    return "neutral sign"


# ----------------------------------------------------------- divisional charts
def varga_sign(lon, n):
    """Parashari divisional-chart sign index for the sixteen Shodashavarga charts."""
    s, d = sign_of(lon), deg_in_sign(lon)
    odd = (s % 2 == 0)
    mode = s % 3  # 0 movable, 1 fixed, 2 dual
    elem = s % 4  # 0 fire, 1 earth, 2 air, 3 water
    if n == 1:
        return s
    if n == 2:  # Parashari hora: Sun's hora = Leo, Moon's hora = Cancer
        first = d < 15
        return 4 if (odd and first) or (not odd and not first) else 3
    if n == 3:
        return (s + int(d // 10) * 4) % 12
    if n == 4:
        return (s + int(d // 7.5) * 3) % 12
    if n == 7:
        start = s if odd else (s + 6) % 12
        return (start + int(d / (30 / 7))) % 12
    if n == 9:
        start = s if mode == 0 else ((s + 8) % 12 if mode == 1 else (s + 4) % 12)
        return (start + int(d / (30 / 9))) % 12
    if n == 10:
        start = s if odd else (s + 8) % 12
        return (start + int(d // 3)) % 12
    if n == 12:
        return (s + int(d // 2.5)) % 12
    if n == 16:
        start = (0, 4, 8)[mode]
        return (start + int(d / (30 / 16))) % 12
    if n == 20:
        start = (0, 8, 4)[mode]
        return (start + int(d // 1.5)) % 12
    if n == 24:
        start = 4 if odd else 3
        return (start + int(d // 1.25)) % 12
    if n == 27:
        start = (0, 3, 6, 9)[elem]
        return (start + int(d / (30 / 27))) % 12
    if n == 30:
        if odd:
            for lim, sg in ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)):
                if d < lim:
                    return sg
        else:
            for lim, sg in ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7)):
                if d < lim:
                    return sg
        return 6
    if n == 40:
        start = 0 if odd else 6
        return (start + int(d / 0.75)) % 12
    if n == 45:
        start = (0, 4, 8)[mode]
        return (start + int(d / (30 / 45))) % 12
    if n == 60:
        return (s + int(d * 2)) % 12
    raise ValueError(f"unsupported varga D{n}")


SHODASHAVARGA = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]


# ----------------------------------------------------------------- dashas
def subdivide(start, length_days, order, start_idx, total):
    out, t = [], start
    n = len(order)
    for k in range(n):
        i = (start_idx + k) % n
        ln = length_days * order[i][1] / total
        out.append((i, order[i][0], t, t + dt.timedelta(days=ln)))
        t = t + dt.timedelta(days=ln)
    return out


def generic_dasha(order, total, start_idx, elapsed_frac, birth, now, year_days, horizon=120, label=""):
    """Balance-aware dasha tree (maha -> antar) plus the active pratyantar at `now`."""
    n = len(order)
    virt = birth - dt.timedelta(days=order[start_idx][1] * elapsed_frac * year_days)
    limit = birth + dt.timedelta(days=horizon * year_days)
    mahas, t, i = [], virt, start_idx
    while t < limit:
        lord, yrs = order[i % n]
        t_end = t + dt.timedelta(days=yrs * year_days)
        antars = subdivide(t, yrs * year_days, order, i % n, total)
        mahas.append({"lord": lord, "years": yrs, "start": max(t, birth).date().isoformat(),
                      "end": t_end.date().isoformat(), "_s": t, "_e": t_end, "_i": i % n,
                      "antardashas": [{"lord": a[1], "start": max(a[2], birth).date().isoformat(),
                                       "end": a[3].date().isoformat()}
                                      for a in antars if a[3] > birth]})
        t, i = t_end, i + 1
    current = {"system": label}
    for m in mahas:
        if m["_s"] <= now < m["_e"]:
            current["mahadasha"] = {"lord": m["lord"], "start": m["start"], "end": m["end"]}
            for a in subdivide(m["_s"], m["years"] * year_days, order, m["_i"], total):
                if a[2] <= now < a[3]:
                    current["antardasha"] = {"lord": a[1], "start": a[2].date().isoformat(),
                                             "end": a[3].date().isoformat()}
                    ln = (a[3] - a[2]).total_seconds() / 86400.0
                    for p in subdivide(a[2], ln, order, a[0], total):
                        if p[2] <= now < p[3]:
                            current["pratyantar"] = {"lord": p[1], "start": p[2].date().isoformat(),
                                                     "end": p[3].date().isoformat()}
                            break
                    break
            break
    upcoming = [{"lord": m["lord"], "start": m["start"], "end": m["end"]}
                for m in mahas if m["_e"] > now][:4]
    for m in mahas:
        for k in ("_s", "_e", "_i"):
            m.pop(k)
    return {"system": label, "first_period_balance_years": round(order[start_idx][1] * (1 - elapsed_frac), 4),
            "current": current, "upcoming_mahadashas": upcoming, "mahadashas": mahas}


YOGINI_ORDER = [("Mangala", 1), ("Pingala", 2), ("Dhanya", 3), ("Bhramari", 4),
                ("Bhadrika", 5), ("Ulka", 6), ("Siddha", 7), ("Sankata", 8)]
YOGINI_PLANET = {"Mangala": "Moon", "Pingala": "Sun", "Dhanya": "Jupiter", "Bhramari": "Mars",
                 "Bhadrika": "Mercury", "Ulka": "Saturn", "Siddha": "Venus", "Sankata": "Rahu"}


def dashas(moon_lon, birth, now, year_days=365.25):
    ni = int(n360(moon_lon) // NAK_SPAN)
    frac = (n360(moon_lon) % NAK_SPAN) / NAK_SPAN
    vim = generic_dasha(VIM_ORDER, 120, ni % 9, frac, birth, now, year_days, label="Vimshottari")
    yog = generic_dasha(YOGINI_ORDER, 36, (ni + 3) % 8, frac, birth, now, year_days, horizon=108, label="Yogini")
    for blk in (yog["current"].get("mahadasha"), yog["current"].get("antardasha"), yog["current"].get("pratyantar")):
        if blk:
            blk["planet"] = YOGINI_PLANET[blk["lord"]]
    for m in yog["mahadashas"]:
        m["planet"] = YOGINI_PLANET[m["lord"]]
    return {"vimshottari": vim, "yogini": yog, "year_length_days": year_days}


# ----------------------------------------------------------- ashtakavarga
BAV_RULES = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "Mercury": [3, 5, 6, 9, 10, 11, 12], "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [2, 3, 5, 6, 9, 10, 11],
             "Mercury": [1, 3, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 4, 7, 8, 10, 11, 12],
             "Venus": [3, 4, 5, 7, 9, 10, 11], "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
             "Mercury": [3, 5, 6, 11], "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
             "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11]},
    "Mercury": {"Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [1, 3, 5, 6, 9, 10, 11, 12], "Jupiter": [6, 8, 11, 12],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11], "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
                "Lagna": [1, 2, 4, 6, 8, 10, 11]},
    "Jupiter": {"Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [1, 2, 4, 5, 6, 9, 10, 11], "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
                "Venus": [2, 5, 6, 9, 10, 11], "Saturn": [3, 5, 6, 12], "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    "Venus": {"Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12], "Mars": [3, 5, 6, 9, 11, 12],
              "Mercury": [3, 5, 6, 9, 11], "Jupiter": [5, 8, 9, 10, 11],
              "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11], "Saturn": [3, 4, 5, 8, 9, 10, 11],
              "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]},
    "Saturn": {"Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [3, 5, 6, 10, 11, 12],
               "Mercury": [6, 8, 9, 10, 11, 12], "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
               "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11]},
}
BAV_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}


def ashtakavarga(sign_idx):
    """sign_idx: dict with the 7 planets and 'Lagna' -> sign index. Returns BAV and SAV."""
    bav = {p: [0] * 12 for p in BAV_RULES}
    for target, contribs in BAV_RULES.items():
        for src, houses in contribs.items():
            for h in houses:
                bav[target][(sign_idx[src] + h - 1) % 12] += 1
    sav = [sum(bav[p][i] for p in BAV_RULES) for i in range(12)]
    return bav, sav


# ------------------------------------------------------- panchang / vara
TITHI_PAKSHA = ("Shukla", "Krishna")
KARANA_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)"]
YOGA_NAMES = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
              "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
              "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
              "Shukla", "Brahma", "Indra", "Vaidhriti"]


def karana_name(k):
    if k == 1:
        return "Kimstughna"
    if k == 58:
        return "Shakuni"
    if k == 59:
        return "Chatushpada"
    if k == 60:
        return "Naga"
    return KARANA_MOV[(k - 2) % 7]


def panchang(sun_lon, moon_lon, birth_local_naive, jd_ut, lat, lon, utc_offset_h):
    elong = n360(moon_lon - sun_lon)
    tithi = int(elong // 12) + 1
    k = int(elong // 6) + 1
    yoga_i = int(n360(sun_lon + moon_lon) // NAK_SPAN)
    # Vedic day runs sunrise to sunrise
    local_mid = dt.datetime(birth_local_naive.year, birth_local_naive.month, birth_local_naive.day)
    jd0 = dt_to_jd(local_mid - dt.timedelta(hours=utc_offset_h)) - 0.02
    res = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, (lon, lat, 0.0), 1013.25, 15.0)
    sunrise_local, before_sunrise, polar_note = None, None, None
    if res[0] >= 0 and res[1][0] > 1:
        cand = jd_to_dt(res[1][0]) + dt.timedelta(hours=utc_offset_h)
        if cand - local_mid < dt.timedelta(hours=30):
            sunrise_local = cand
    if sunrise_local is None:
        before_sunrise = False
        polar_note = "No sunrise on this date at this latitude (polar day or night); the civil weekday is used."
    else:
        before_sunrise = birth_local_naive < sunrise_local
    wd = birth_local_naive.weekday() - (1 if before_sunrise else 0)
    wd %= 7
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # second convention: disc centre without refraction (Prokerala / many panchangs), about 2-3 minutes later
    alt = None
    if sunrise_local is not None:
        r2 = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION,
                            (lon, lat, 0.0), 1013.25, 15.0)
        if r2[0] >= 0 and r2[1][0] > 1:
            sr2 = jd_to_dt(r2[1][0]) + dt.timedelta(hours=utc_offset_h)
            gap = min(abs((birth_local_naive - sunrise_local).total_seconds()), abs((birth_local_naive - sr2).total_seconds()))
            if gap <= 300:
                wd2 = (birth_local_naive.weekday() - (1 if birth_local_naive < sr2 else 0)) % 7
                alt = {"sunrise_no_refraction": sr2.strftime("%Y-%m-%d %H:%M:%S"), "vara": names[wd2],
                       "vara_lord": WEEKDAY_LORD[wd2], "differs": wd2 != wd,
                       "note": "Birth within 5 minutes of sunrise: the weekday under the no-refraction sunrise rule is shown too."}
    return {"tithi": tithi if tithi <= 15 else tithi - 15,
            "tithi_number_1_30": tithi, "paksha": TITHI_PAKSHA[0 if tithi <= 15 else 1],
            "karana": karana_name(k), "yoga": YOGA_NAMES[yoga_i],
            "vara": names[wd], "vara_lord": WEEKDAY_LORD[wd],
            "sunrise_local": sunrise_local.strftime("%Y-%m-%d %H:%M:%S") if sunrise_local else None,
            "born_before_sunrise": before_sunrise,
            "sunrise_convention": "centre of the Sun's disc with standard refraction (matches Leostar printouts within seconds; Prokerala uses no refraction)",
            "near_sunrise_alternative": alt,
            "note": polar_note or "Vedic weekday runs sunrise-to-sunrise; born before sunrise = previous weekday."}


# ------------------------------------------------------- Vedic aspects
ASPECT_HOUSES = {"Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7], "Mars": [4, 7, 8],
                 "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10], "Rahu": [5, 7, 9], "Ketu": [5, 7, 9]}


def sign_aspects(planets):
    """Full-sign graha drishti. Rahu/Ketu 5-7-9 is a school-dependent convention."""
    signs = {p: v["sign_index"] for p, v in planets.items()}
    aspected_by = {p: [] for p in planets}
    for src, hs in ASPECT_HOUSES.items():
        tgt = {(signs[src] + h - 1) % 12 for h in hs}
        for p in planets:
            if p != src and signs[p] in tgt:
                aspected_by[p].append(src)
    return aspected_by


# ------------------------------------------------------------ yoga engine
def kendra(h):
    return h in (1, 4, 7, 10)


def rel_house(a_sign, b_sign):
    return (b_sign - a_sign) % 12 + 1


def find_yogas(planets, lag_sign, houses):
    """Objective, rule-based *candidates*. Cancellation and strength are for the reader."""
    y = []
    S = {p: planets[p]["sign_index"] for p in planets}
    H = {p: planets[p]["house"] for p in planets}
    moon = S["Moon"]
    lord_of = {h: SIGN_LORD[(lag_sign + h - 1) % 12] for h in range(1, 13)}

    if kendra(rel_house(moon, S["Jupiter"])):
        y.append({"yoga": "Gaja Kesari", "rule": "Jupiter in a kendra (1/4/7/10) from the Moon"})
    if S["Sun"] == S["Mercury"]:
        y.append({"yoga": "Budha-Aditya", "rule": "Sun and Mercury in the same sign",
                  "caveat": "Weak if Mercury is combust within ~3 degrees"})
    if S["Moon"] == S["Mars"]:
        y.append({"yoga": "Chandra-Mangal", "rule": "Moon and Mars in the same sign"})
    if S["Jupiter"] == S["Rahu"]:
        y.append({"yoga": "Guru Chandal", "rule": "Jupiter conjunct Rahu (same sign)"})
    if S["Saturn"] == S["Rahu"]:
        y.append({"yoga": "Shrapit / Shani-Rahu", "rule": "Saturn conjunct Rahu (same sign)"})
    for p, nm, sgs in (("Mars", "Ruchaka", [0, 7, 9]), ("Mercury", "Bhadra", [2, 5]),
                       ("Jupiter", "Hamsa", [8, 11, 3]), ("Venus", "Malavya", [1, 6, 11]),
                       ("Saturn", "Sasha", [9, 10, 6])):
        if S[p] in sgs and kendra(H[p]):
            y.append({"yoga": f"{nm} (Pancha Mahapurusha)",
                      "rule": f"{p} in own/exaltation sign and in a kendra from Lagna"})
    # Kemadruma / Sunapha / Anapha / Durudhara (Moon-based, excluding Sun & nodes)
    others = [p for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")]
    second = [p for p in others if S[p] == (moon + 1) % 12]
    twelfth = [p for p in others if S[p] == (moon - 1) % 12]
    with_moon = [p for p in others if S[p] == moon]
    if not (second or twelfth or with_moon):
        y.append({"yoga": "Kemadruma", "rule": "No planet (excl. Sun/nodes) in 2nd, 12th or with the Moon",
                  "caveat": "Commonly cancelled if a planet is in a kendra from Lagna or Moon"})
    elif second and twelfth:
        y.append({"yoga": "Durudhara", "rule": "Planets on both sides of the Moon"})
    elif second:
        y.append({"yoga": "Sunapha", "rule": "Planet in 2nd from the Moon"})
    elif twelfth:
        y.append({"yoga": "Anapha", "rule": "Planet in 12th from the Moon"})
    # Lordship-based
    def linked(a, b):
        if a == b:
            return None
        if S[a] == S[b]:
            return "conjunction"
        if SIGN_LORD[S[a]] == b and SIGN_LORD[S[b]] == a:
            return "sign exchange"
        return None
    kend, tri = [1, 4, 7, 10], [1, 5, 9]
    seen = set()
    for kh in kend:
        for th in [5, 9]:
            a, b = lord_of[kh], lord_of[th]
            key = tuple(sorted((a, b)))
            if a != b and key not in seen:
                lk = linked(a, b)
                if lk:
                    seen.add(key)
                    y.append({"yoga": "Raja yoga (candidate)", "rule": f"Lord of {kh} ({a}) and lord of {th} ({b}) by {lk}"})
    a, b = lord_of[9], lord_of[10]
    if a != b and linked(a, b):
        y.append({"yoga": "Dharma-Karmadhipati (candidate)", "rule": f"Lords of 9 and 10 ({a}, {b}) by {linked(a, b)}"})
    for x, z in ((2, 11), (5, 9), (2, 9), (11, 9)):
        a, b = lord_of[x], lord_of[z]
        if a != b and linked(a, b):
            y.append({"yoga": "Dhana yoga (candidate)", "rule": f"Lords of {x} and {z} ({a}, {b}) by {linked(a, b)}"})
    for h in (6, 8, 12):
        l = lord_of[h]
        if H[l] in (6, 8, 12):
            y.append({"yoga": "Vipareeta Raja (candidate)", "rule": f"Lord of {h} ({l}) placed in house {H[l]}"})
    # Parivartana
    ps = list(S)
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            a, b = ps[i], ps[j]
            if a in ("Rahu", "Ketu") or b in ("Rahu", "Ketu"):
                continue
            if SIGN_LORD[S[a]] == b and SIGN_LORD[S[b]] == a:
                y.append({"yoga": "Parivartana (sign exchange)", "rule": f"{a} in {SIGNS[S[a]]} and {b} in {SIGNS[S[b]]}"})
    # Neecha Bhanga candidates
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        if planets[p]["dignity"] == "debilitated":
            deb_lord = SIGN_LORD[S[p]]
            exalt_lord = SIGN_LORD[EXALT[p][0]]
            reasons = []
            for who, nm in ((deb_lord, "lord of the debilitation sign"), (exalt_lord, "lord of the exaltation sign")):
                if kendra(H[who]) or kendra(rel_house(moon, S[who])):
                    reasons.append(f"{nm} ({who}) is in a kendra from Lagna or Moon")
            if any(planets[q]["dignity"] == "exalted" and S[q] == S[p] for q in planets if q != p):
                reasons.append("an exalted planet shares the sign")
            y.append({"yoga": f"Debilitated {p}", "rule": f"{p} in {SIGNS[S[p]]}",
                      "possible_neecha_bhanga": reasons or None})
    return y


# --------------------------------------------------------------- doshas
RAHU_SARPA = ["Anant", "Kulik", "Vasuki", "Shankhpal", "Padma", "Mahapadma", "Takshak",
              "Karkotak", "Shankhachud", "Ghatak", "Vishdhar", "Sheshnag"]


def find_doshas(planets, lag_sign):
    S = {p: v["sign_index"] for p, v in planets.items()}
    d = {}
    mars_h = {"from_lagna": planets["Mars"]["house"],
              "from_moon": rel_house(S["Moon"], S["Mars"]),
              "from_venus": rel_house(S["Venus"], S["Mars"])}
    bad = (1, 2, 4, 7, 8, 12)
    d["mangal_dosha"] = {"mars_house": mars_h,
                         "present_by_reference": {k: v in bad for k, v in mars_h.items()},
                         "convention": "Houses 1,2,4,7,8,12 (some South Indian schools omit the 2nd). Cancellations not applied."}
    rahu = planets["Rahu"]["lon"]
    seven = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    rel = [n360(planets[p]["lon"] - rahu) for p in seven]
    fwd = sum(1 for r in rel if r < 180)
    if fwd in (0, 7):
        d["kaal_sarp"] = {"present": True, "type": RAHU_SARPA[planets["Rahu"]["house"] - 1],
                          "rahu_house": planets["Rahu"]["house"], "complete": True}
    elif fwd in (1, 6):
        outside = [p for p, r in zip(seven, rel) if (r < 180) == (fwd == 1)]
        d["kaal_sarp"] = {"present": False, "partial": True, "planet_outside_axis": outside,
                          "note": "One planet outside the Rahu-Ketu axis - a partial pattern, not a full dosha."}
    else:
        d["kaal_sarp"] = {"present": False}
    d["guru_chandal"] = S["Jupiter"] == S["Rahu"]
    d["shani_rahu"] = S["Saturn"] == S["Rahu"]
    d["pitra_dosha_indicators"] = {
        "sun_with_rahu_or_ketu": S["Sun"] in (S["Rahu"], S["Ketu"]),
        "rahu_or_ketu_in_9th": planets["Rahu"]["house"] == 9 or planets["Ketu"]["house"] == 9,
        "sun_in_9th": planets["Sun"]["house"] == 9,
        "lord_of_9_house": planets[SIGN_LORD[(lag_sign + 8) % 12]]["house"],
        "note": "Raw indicators only; the reading decides whether they amount to a dosha."}
    ml = planets["Moon"]["lon"]
    d["gandanta_moon"] = any(abs(wrap180(ml - j)) <= 3 + 1 / 3 for j in (0, 120, 240))
    d["gandmool_nakshatra_moon"] = planets["Moon"]["nakshatra"] in (
        "Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati")
    return d


# ------------------------------------------------------------ Jaimini
def compute_arudhas(planets, lag_sign):
    S = {p: v["sign_index"] for p, v in planets.items()}
    res = {}
    for h in range(1, 13):
        hs = (lag_sign + h - 1) % 12
        lord = SIGN_LORD[hs]
        ls = S[lord]
        n = (ls - hs) % 12 + 1
        a = (ls + n - 1) % 12
        if a == hs:
            a = (a + 9) % 12
        elif a == (hs + 6) % 12:
            a = (a + 9) % 12
        res[f"A{h}"] = SIGNS[a]
    res["AL (Arudha Lagna)"] = res["A1"]
    res["UL (Upapada Lagna)"] = res["A12"]
    return res


def jaimini(planets, lag_sign):
    seven = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    names7 = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Putrakaraka",
              "Gnatikaraka", "Darakaraka"]
    ranked = sorted(seven, key=lambda p: -deg_in_sign(planets[p]["lon"]))
    k7 = {names7[i]: ranked[i] for i in range(7)}
    eight = seven + ["Rahu"]
    def dg(p):
        return 30 - deg_in_sign(planets[p]["lon"]) if p == "Rahu" else deg_in_sign(planets[p]["lon"])
    r8 = sorted(eight, key=lambda p: -dg(p))
    names8 = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Pitrikaraka",
              "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    k8 = {names8[i]: r8[i] for i in range(8)}
    ak = k7["Atmakaraka"]
    ak_nav = varga_sign(planets[ak]["lon"], 9)
    return {"chara_karakas_7": k7, "chara_karakas_8_with_rahu": k8,
            "atmakaraka": ak, "karakamsha_sign": SIGNS[ak_nav],
            "karakamsha_house_from_lagna": (ak_nav - lag_sign) % 12 + 1,
            "arudha_padas": compute_arudhas(planets, lag_sign),
            "conventions": "Dual lordship of Scorpio/Aquarius uses Mars/Saturn (Parashari). Jaimini schools may test Ketu/Rahu. "
                           "Chara Dasha is NOT computed here - variants differ; take it from a verified tool."}


def _jaimini_full(planets, lag_sign, jd, birth_utc, now_utc, ayan):
    import chara
    j = jaimini(planets, lag_sign)
    extra = chara.jaimini_extras(planets, lag_sign, j["chara_karakas_7"], varga_sign)
    j.update(extra)
    j["arudha_padas"] = extra["arudha_padas_pvr"]
    j["chara_dasha_rao"] = chara.build_chara(planets, lag_sign, jd, birth_utc, now_utc, AYAN[ayan])
    j["conventions"] = ("Arudha padas follow PVR (exception + stronger co-lord); arudha_padas_rao gives K.N. Rao's version "
                        "without the exception. Chara dasha follows K.N. Rao (see chara_dasha_rao.conventions).")
    return j


# ------------------------------------------------------- partial strength
DEB_POINT = {p: (EXALT[p][0] * 30 + EXALT[p][1] + 180) % 360 for p in EXALT}
NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
DIG_TARGET = {"Jupiter": "asc", "Mercury": "asc", "Sun": "mc", "Mars": "mc",
              "Saturn": "desc", "Moon": "ic", "Venus": "ic"}


def partial_strength(planets, asc, mc):
    pts = {"asc": asc, "mc": mc, "desc": n360(asc + 180), "ic": n360(mc + 180)}
    out = {}
    for p in NAISARGIKA:
        lon = planets[p]["lon"]
        uccha = abs(wrap180(lon - DEB_POINT[p])) / 3.0
        dig = (180.0 - abs(wrap180(lon - pts[DIG_TARGET[p]]))) / 3.0
        out[p] = {"uccha_bala": round(uccha, 2), "dig_bala": round(dig, 2),
                  "naisargika_bala": NAISARGIKA[p], "subtotal_virupa": round(uccha + dig + NAISARGIKA[p], 2)}
    out["_note"] = ("PARTIAL: 3 of the 6 Shadbala components (Uccha, Dig, Naisargika). Kala, Cheshta and the rest of Sthana "
                    "are not computed. Do not present this as Shadbala; take full Shadbala from a verified tool.")
    return out


# --------------------------------------------------------------------- KP
def kp_lords(lon):
    lon = n360(lon)
    ni = int(lon // NAK_SPAN)
    within = lon - ni * NAK_SPAN
    star = VIM_ORDER[ni % 9]

    def split(start_idx, span, offset):
        acc = 0.0
        for k in range(9):
            nm, yrs = VIM_ORDER[(start_idx + k) % 9]
            ln = span * yrs / 120.0
            if offset < acc + ln or k == 8:
                return (start_idx + k) % 9, offset - acc, ln
            acc += ln
    sub_i, off2, sub_len = split(ni % 9, NAK_SPAN, within)
    ssub_i, _, _ = split(sub_i, sub_len, off2)
    return {"sign_lord": SIGN_LORD[sign_of(lon)], "star_lord": star[0],
            "sub_lord": VIM_ORDER[sub_i][0], "sub_sub_lord": VIM_ORDER[ssub_i][0]}


def kp_block(jd, lat, lon):
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    pos = {}
    for name, pid in PLANETS7:
        xx, _ = swe.calc_ut(jd, pid, fl)
        pos[name] = xx[0]
    xx, _ = swe.calc_ut(jd, swe.MEAN_NODE, fl)
    pos["Rahu"], pos["Ketu"] = xx[0], n360(xx[0] + 180)
    warn = None
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
        system = "Placidus"
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"O", swe.FLG_SIDEREAL)
        system, warn = "Porphyry (Placidus undefined at this latitude)", "Placidus failed; Porphyry used"
    cusps = list(cusps)

    def house_of(l):
        for i in range(12):
            a, b = cusps[i], cusps[(i + 1) % 12]
            if n360(l - a) < n360(b - a):
                return i + 1
        return 1
    planets = {}
    for p, l in pos.items():
        planets[p] = {"lon": round(l, 4), "sign": SIGNS[sign_of(l)], "house": house_of(l), **kp_lords(l)}
    cusp_out = {f"C{i+1}": {"lon": round(c, 4), "sign": SIGNS[sign_of(c)], **kp_lords(c)} for i, c in enumerate(cusps)}
    # four-level significators
    sig = {}
    for h in range(1, 13):
        cusp_lord = cusp_out[f"C{h}"]["sign_lord"]
        occ = [p for p in planets if planets[p]["house"] == h]
        lvl_a = [p for p in planets if planets[p]["star_lord"] in occ]
        lvl_c = [p for p in planets if planets[p]["star_lord"] == cusp_lord]
        ordered, seen = [], set()
        for grp in (lvl_a, occ, lvl_c, [cusp_lord]):
            for p in grp:
                if p not in seen:
                    seen.add(p)
                    ordered.append(p)
        sig[f"H{h}"] = ordered
    return {"ayanamsa": "Krishnamurti", "house_system": system, "warning": warn,
            "planets": planets, "cusps": cusp_out, "significators_by_house": sig,
            "note": "Significator order: (1) planets in the star of occupants, (2) occupants, (3) planets in the star of the house lord, (4) house lord. "
                    "Ruling planets and event judgement are for the reader; this block only supplies the lord table."}


# --------------------------------------------------------- Sade Sati scan
def _sat_sign(jd, ayan="lahiri"):
    swe.set_sid_mode(AYAN[ayan])
    return sign_of(swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0])


def sade_sati(moon_sign, now_jd, ayan="lahiri", span_years=32):
    targets = {(moon_sign - 1) % 12: "12th from Moon (rising phase)",
               moon_sign: "over natal Moon (peak phase)",
               (moon_sign + 1) % 12: "2nd from Moon (setting phase)"}
    step = 3.0
    j0, j1 = now_jd - span_years * 365.25, now_jd + span_years * 365.25
    segs, cur, j = [], None, j0
    while j <= j1:
        s = _sat_sign(j, ayan)
        if s in targets:
            if cur and cur[2] == s:
                cur[1] = j
            else:
                if cur:
                    segs.append(cur)
                cur = [j, j, s]
        elif cur:
            segs.append(cur)
            cur = None
        j += step
    if cur:
        segs.append(cur)

    def edge(a, b, sign, inside_at_b):
        for _ in range(28):
            mid = (a + b) / 2
            if (_sat_sign(mid, ayan) == sign) == inside_at_b:
                b = mid
            else:
                a = mid
        return b if inside_at_b else a
    refined = []
    for a, b, s in segs:
        a2 = a if a - j0 < step else edge(a - step, a, s, True)
        b2 = b if j1 - b < step else edge(b, b + step, s, False)
        refined.append([a2, b2, s])
    # merge retrograde re-entries into the same sign (gap < ~1.3 years)
    merged = []
    for a, b, s in refined:
        if merged and merged[-1][2] == s and a - merged[-1][1] < 480:
            merged[-1][1] = b
        else:
            merged.append([a, b, s])
    cycles, grp = [], []
    for seg in merged:
        if grp and seg[0] - grp[-1][1] > 3 * 365.25:
            cycles.append(grp)
            grp = []
        grp.append(seg)
    if grp:
        cycles.append(grp)
    res = [{"start": jd_to_dt(c[0][0]).date().isoformat(), "end": jd_to_dt(c[-1][1]).date().isoformat(),
            "phases": [{"saturn_sign": SIGNS[s], "position": targets[s],
                        "from": jd_to_dt(a).date().isoformat(), "to": jd_to_dt(b).date().isoformat()}
                       for a, b, s in c]} for c in cycles]
    now_s = _sat_sign(now_jd, ayan)
    rel = (now_s - moon_sign) % 12 + 1
    return {"saturn_now_sign": SIGNS[now_s], "saturn_house_from_moon": rel,
            "sade_sati_now": targets.get(now_s), "ashtama_shani_now": rel == 8,
            "kantaka_shani_now": rel == 4, "cycles_in_window": res,
            "note": f"Phase edges are Saturn's sidereal ({ayan}) sign-ingress dates; retrograde re-entries are merged."}


# ------------------------------------------------------------- Varshaphal
def solar_return_jd(natal_sid_sun, year, birth_month_day_jd_guess, ayan="lahiri"):
    swe.set_sid_mode(AYAN[ayan])
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    jd = birth_month_day_jd_guess
    for _ in range(12):
        xx, _ = swe.calc_ut(jd, swe.SUN, fl)
        err = wrap180(xx[0] - natal_sid_sun)
        jd -= err / xx[3]
        if abs(err) < 1e-9:
            break
    return jd


def return_utc(natal_sun_lon, birth_utc, age, ayan="lahiri"):
    """UTC datetime of the sidereal solar return that starts year `age` (age 0 = birth)."""
    y = birth_utc.year + age
    try:
        g = dt.datetime(y, birth_utc.month, birth_utc.day, birth_utc.hour, birth_utc.minute)
    except ValueError:  # 29 Feb
        g = dt.datetime(y, 3, 1, birth_utc.hour, birth_utc.minute)
    return jd_to_dt(solar_return_jd(natal_sun_lon, y, dt_to_jd(g), ayan))


def completed_varsha_years(natal_sun_lon, birth_utc, when_utc, ayan="lahiri"):
    """Tajaka years completed at `when_utc`, counted by actual sidereal solar returns (not a 365.2425-day average)."""
    age = max(0, int((when_utc - birth_utc).days / 365.2425))
    while age > 0 and when_utc < return_utc(natal_sun_lon, birth_utc, age, ayan):
        age -= 1
    while when_utc >= return_utc(natal_sun_lon, birth_utc, age + 1, ayan):
        age += 1
    return age


def varshaphal(natal_sun_lon, natal_lag_sign, birth_utc, age_completed, lat, lon, ayan="lahiri"):
    guess_year = birth_utc.year + age_completed
    jd = dt_to_jd(return_utc(natal_sun_lon, birth_utc, age_completed, ayan))
    pos = sidereal_positions(jd, ayan)
    cusps, asc, mc = sidereal_angles(jd, lat, lon, ayan)
    vl = sign_of(asc)
    muntha = (natal_lag_sign + age_completed) % 12
    return {"year_of_return": guess_year, "age_at_return": age_completed,
            "return_utc": jd_to_dt(jd).strftime("%Y-%m-%d %H:%M:%S"),
            "varsha_lagna": fmt_pos(asc), "varsha_lagna_sign": SIGNS[vl],
            "muntha_sign": SIGNS[muntha], "muntha_house": (muntha - vl) % 12 + 1,
            "planets": {p: {"pos": fmt_pos(v["lon"]), "house": (sign_of(v["lon"]) - vl) % 12 + 1,
                            "retro": bool(v["speed"] < 0 and p not in ("Sun", "Moon"))} for p, v in pos.items()},
            "not_computed": "Varsheshwara (needs Pancha-vargiya bala), Mudda dasha and Tajik yoga scanning are left to a verified tool.",
            "convention": f"Sidereal solar return ({ayan}). Cast for the birthplace, as the Tajaka rule requires (PVR 27.1), wherever the person now lives."}


# ======================================================================
# Orchestrator
# ======================================================================
def _planet_records(pos, lag_sign):
    sun = pos["Sun"]["lon"]
    out = {}
    for name in ORDER9:
        v = pos[name]
        lon = v["lon"]
        s = sign_of(lon)
        nk = nak_info(lon)
        retro = bool(v["speed"] < 0) if name not in ("Sun", "Moon") else False
        rec = {"lon": round(lon, 5), "sign": SIGNS[s], "sign_index": s,
               "deg_in_sign": round(deg_in_sign(lon), 4), "dms": dms(deg_in_sign(lon)),
               "house": (s - lag_sign) % 12 + 1, "nakshatra": nk["name"], "pada": nk["pada"],
               "nakshatra_lord": nk["lord"], "retrograde": retro,
               "daily_motion": round(v["speed"], 4), "dignity": dignity(name, lon),
               "sign_lord": SIGN_LORD[s], "vargottama": varga_sign(lon, 9) == s}
        if name in COMBUST_ORB:
            sep = abs(wrap180(lon - sun))
            orb = COMBUST_ORB_RETRO.get(name, COMBUST_ORB[name]) if retro else COMBUST_ORB[name]
            rec["combust"] = bool(sep <= orb)
            rec["sun_separation"] = round(sep, 3)
        out[name] = rec
    return out


def _asc_at(jd, lat, lon, ayan):
    swe.set_sid_mode(AYAN[ayan])
    return swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)[1][0]


def lagna_sensitivity(jd, lat, lon, ayan, window_min=180):
    base = _asc_at(jd, lat, lon, ayan)
    s0, n0 = sign_of(base), varga_sign(base, 9)
    res = {"lagna_sign_changes": {}, "navamsa_lagna_changes": {}}
    for label, fn, base_v, key in (("sign", sign_of, s0, "lagna_sign_changes"),
                                   ("navamsa", lambda x: varga_sign(x, 9), n0, "navamsa_lagna_changes")):
        for direction in (-1, 1):
            found = None
            for m in range(1, window_min + 1):
                a = _asc_at(jd + direction * m / 1440.0, lat, lon, ayan)
                if fn(a) != base_v:
                    found = m
                    break
            res[key]["earlier" if direction < 0 else "later"] = found
    return res


def ayanamsa_sensitivity(jd, base="lahiri", node="mean", lat=None, lon=None):
    values, flags = {}, []
    base_pos = sidereal_positions(jd, base, node)
    for a in AYAN:
        swe.set_sid_mode(AYAN[a])
        values[a] = round(swe.get_ayanamsa_ut(jd), 5)
    base_asc = _asc_at(jd, lat, lon, base) if lat is not None else None
    for a in AYAN:
        if a == base:
            continue
        pos = sidereal_positions(jd, a, node)
        for p in ORDER9:
            b0, b1 = base_pos[p]["lon"], pos[p]["lon"]
            n0, n1 = nak_info(b0), nak_info(b1)
            ch = []
            if sign_of(b0) != sign_of(b1):
                ch.append(f"sign {SIGNS[sign_of(b0)]} -> {SIGNS[sign_of(b1)]}")
            if n0["name"] != n1["name"]:
                ch.append(f"nakshatra {n0['name']} -> {n1['name']}")
            elif n0["pada"] != n1["pada"]:
                ch.append(f"pada {n0['pada']} -> {n1['pada']}")
            if ch:
                flags.append({"planet": p, "ayanamsa": a, "changes": ch})
        if base_asc is not None:
            a1 = _asc_at(jd, lat, lon, a)
            if sign_of(base_asc) != sign_of(a1):
                flags.append({"planet": "Lagna", "ayanamsa": a,
                              "changes": [f"sign {SIGNS[sign_of(base_asc)]} -> {SIGNS[sign_of(a1)]}"]})
            elif nak_info(base_asc)["name"] != nak_info(a1)["name"]:
                flags.append({"planet": "Lagna", "ayanamsa": a,
                              "changes": [f"nakshatra {nak_info(base_asc)['name']} -> {nak_info(a1)['name']}"]})
    return {"ayanamsa_values_deg": values, "placements_that_change": flags}


def build_vedic(jd, birth_utc, now_utc, lat, lon, birth_local_naive, utc_offset_h,
                ayan="lahiri", node="mean", dasha_year=365.25):
    swe.set_sid_mode(AYAN[ayan])
    ayan_deg = round(swe.get_ayanamsa_ut(jd), 5)
    pos = sidereal_positions(jd, ayan, node)
    cusps_ws, asc, mc = sidereal_angles(jd, lat, lon, ayan, b"W")
    lag_sign = sign_of(asc)
    planets = _planet_records(pos, lag_sign)
    lagna = {"lon": round(asc, 5), "sign": SIGNS[lag_sign], "dms": dms(deg_in_sign(asc)),
             "nakshatra": nak_info(asc)["name"], "pada": nak_info(asc)["pada"],
             "nakshatra_lord": nak_info(asc)["lord"], "sign_lord": SIGN_LORD[lag_sign],
             "midheaven_sidereal": fmt_pos(mc)}
    houses = [{"house": h, "sign": SIGNS[(lag_sign + h - 1) % 12], "lord": SIGN_LORD[(lag_sign + h - 1) % 12],
               "lord_placed_in_house": planets[SIGN_LORD[(lag_sign + h - 1) % 12]]["house"],
               "occupants": [p for p in ORDER9 if planets[p]["house"] == h]} for h in range(1, 13)]
    # Bhava Chalit (Sripati style: Porphyry midpoints as bhava madhya)
    madhya, _, _ = sidereal_angles(jd, lat, lon, ayan, b"O")

    def chalit(l):
        for i in range(12):
            pm, cm, nm = madhya[(i - 1) % 12], madhya[i], madhya[(i + 1) % 12]
            st = pm + wrap180(cm - pm) / 2
            en = cm + wrap180(nm - cm) / 2
            if n360(l - st) < n360(en - st):
                return i + 1
        return 1
    chalit_moves = {p: {"rashi_house": planets[p]["house"], "chalit_house": chalit(v["lon"])}
                    for p, v in pos.items() if chalit(v["lon"]) != planets[p]["house"]}
    # vargas
    vargas = {}
    for n in SHODASHAVARGA:
        vargas[f"D{n}"] = {"Lagna": SIGNS[varga_sign(asc, n)],
                           **{p: SIGNS[varga_sign(pos[p]["lon"], n)] for p in ORDER9}}
    # ashtakavarga
    sidx = {p: planets[p]["sign_index"] for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")}
    sidx["Lagna"] = lag_sign
    bav, sav = ashtakavarga(sidx)
    for p, tot in BAV_TOTALS.items():
        assert sum(bav[p]) == tot, f"BAV total mismatch for {p}"
    assert sum(sav) == 337
    now_jd = dt_to_jd(now_utc)
    npos = sidereal_positions(now_jd, ayan, node)
    moon_sign = planets["Moon"]["sign_index"]
    transits = {}
    for p in ORDER9:
        s = sign_of(npos[p]["lon"])
        t = {"sign": SIGNS[s], "deg": round(deg_in_sign(npos[p]["lon"]), 3),
             "house_from_lagna": (s - lag_sign) % 12 + 1, "house_from_moon": (s - moon_sign) % 12 + 1,
             "retrograde": bool(npos[p]["speed"] < 0) if p not in ("Sun", "Moon") else False,
             "sarva_ashtakavarga_in_sign": sav[s]}
        if p in bav:
            t["own_bindus_in_sign"] = bav[p][s]
        transits[p] = t
    age = (now_utc - birth_utc).days / 365.2425
    dsh = dashas(pos["Moon"]["lon"], birth_utc, now_utc, dasha_year)
    core_yogas = find_yogas(planets, lag_sign, houses)
    result = {
        "conventions": {"ayanamsa": ayan, "ayanamsa_deg": ayan_deg,
                        "house_system_main": "whole sign", "bhava_chalit": "Porphyry midpoints (Sripati style)",
                        "rahu": f"{node} node", "vimshottari_year_days": dasha_year,
                        "graha_drishti": "full-sign aspects; Rahu/Ketu 5-7-9 is school-dependent"},
        "lagna": lagna, "planets": planets, "houses": houses,
        "bhava_chalit_shifts": chalit_moves,
        "panchang": panchang(pos["Sun"]["lon"], pos["Moon"]["lon"], birth_local_naive, jd, lat, lon, utc_offset_h),
        "aspects_received_by": sign_aspects(planets),
        "divisional_charts": vargas,
        "ashtakavarga": {"bhinna": {p: {SIGNS[i]: bav[p][i] for i in range(12)} for p in bav},
                         "sarva": {SIGNS[i]: sav[i] for i in range(12)}, "sarva_total": sum(sav),
                         "check": "Per-planet totals 48/49/39/54/56/52/39 and SAV 337 verified on every run."},
        "dashas": dsh,
        "yogas_candidates": core_yogas, "doshas": find_doshas(planets, lag_sign),
        "jaimini": _jaimini_full(planets, lag_sign, jd, birth_utc, now_utc, ayan),
        "partial_strength": partial_strength(planets, asc, mc),
        "kp": kp_block(jd, lat, lon),
        "sade_sati": sade_sati(moon_sign, now_jd, ayan),
        "transits_now": {"date": now_utc.date().isoformat(), "planets": transits},
        "varshaphal": varshaphal(pos["Sun"]["lon"], lag_sign, birth_utc,
                                 completed_varsha_years(pos["Sun"]["lon"], birth_utc, now_utc, ayan), lat, lon, ayan),
        "sensitivity": {
            "lagna_time_window_minutes": lagna_sensitivity(jd, lat, lon, ayan),
            "ayanamsa": ayanamsa_sensitivity(jd, ayan, node, lat, lon),
            "moon_nakshatra_boundary": None,
        },
    }
    m = pos["Moon"]
    fr = (n360(m["lon"]) % NAK_SPAN)
    result["sensitivity"]["moon_nakshatra_boundary"] = {
        "hours_since_entering_nakshatra": round(fr / abs(m["speed"]) * 24, 2),
        "hours_until_leaving_nakshatra": round((NAK_SPAN - fr) / abs(m["speed"]) * 24, 2),
        "why_it_matters": "A birth-time error larger than this shifts the Moon's nakshatra and the entire Vimshottari sequence."}
    edge = []
    for p in ORDER9:
        d = deg_in_sign(pos[p]["lon"])
        if d < 1.0 or d > 29.0:
            edge.append({"planet": p, "position": fmt_pos(pos[p]["lon"]), "note": "within 1 degree of a sign boundary"})
    result["sensitivity"]["planets_near_sign_boundary"] = edge
    wars = []
    fiv = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i in range(5):
        for j in range(i + 1, 5):
            if abs(wrap180(pos[fiv[i]]["lon"] - pos[fiv[j]]["lon"])) < 1.0:
                wars.append({"pair": [fiv[i], fiv[j]], "separation_deg": round(abs(wrap180(pos[fiv[i]]["lon"] - pos[fiv[j]]["lon"])), 3),
                             "note": "Graha yuddha candidate; winner rule is school-dependent"})
    result["graha_yuddha_candidates"] = wars
    try:
        import upagraha
        result["upagrahas"] = upagraha.compute(jd, lat, lon, utc_offset_h, birth_local_naive, AYAN[ayan], lag_sign, pos["Sun"]["lon"])
    except Exception as e:  # never let an optional layer break the chart
        result["upagrahas"] = {"status": f"not computed: {e}"}
    swe.set_sid_mode(AYAN[ayan])
    result["age_years_at_now"] = round(age, 3)
    result["_lag_sign"] = lag_sign
    return result
