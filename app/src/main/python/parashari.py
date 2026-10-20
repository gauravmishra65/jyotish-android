"""parashari.py - Parashari views (Phase 3): functional nature and baadhakas (PVR Tables 30-31),
amsabala in the four varga groups (PVR 6.6), avasthas (PVR 15.4), raja yogas with their magnitude
(PVR 11.7.1-11.7.2), jeeva and sharira (Rayudu ch. 15), the dasha-lord views (lagna, Moon, dasha lord,
navamsa house, event vargas, MD-AD relation) and a varga reading rubric (Rayudu ch. 9).

Facts only; the reader interprets. Nothing here predicts death, illness or loss of a person.
"""
from common import SIGNS, SIGN_LORD, NAK_SPAN, n360, sign_of, deg_in_sign, wrap180, nak_info
import shadbala as SB
import rasidasa

P7 = SB.P7
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
ASPECT_HOUSES = {"Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7], "Mars": [4, 7, 8],
                 "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10], "Rahu": [5, 7, 9], "Ketu": [5, 7, 9]}
EXACT = {7: 180, 4: 90, 8: 210, 5: 120, 9: 240, 3: 60, 10: 270}
EXALT_SIGN = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# PVR Table 30 (Moon omitted for movable lagnas: its nature follows the paksha)
FUNCTIONAL = {
    0: ("", ["Sun", "Mars", "Jupiter"], [], ["Mercury", "Venus", "Saturn"]),
    1: ("Saturn", ["Sun", "Mercury", "Saturn"], ["Mars"], ["Moon", "Jupiter", "Venus"]),
    2: ("", ["Venus"], ["Moon", "Mercury", "Saturn"], ["Sun", "Mars", "Jupiter"]),
    3: ("Mars", ["Moon", "Mars", "Jupiter"], ["Sun", "Saturn"], ["Mercury", "Venus"]),
    4: ("Mars", ["Sun", "Mars", "Jupiter"], ["Moon"], ["Mercury", "Venus", "Saturn"]),
    5: ("", ["Mercury", "Venus"], ["Sun", "Saturn"], ["Moon", "Mars", "Jupiter"]),
    6: ("Saturn", ["Mercury", "Venus", "Saturn"], [], ["Sun", "Mars", "Jupiter"]),
    7: ("", ["Moon", "Jupiter"], ["Sun", "Mars"], ["Mercury", "Venus", "Saturn"]),
    8: ("", ["Sun", "Mars"], ["Moon", "Mercury", "Jupiter"], ["Venus", "Saturn"]),
    9: ("Venus", ["Venus", "Mercury", "Saturn"], ["Sun"], ["Mars", "Jupiter"]),
    10: ("Venus", ["Venus", "Saturn"], ["Sun", "Mercury"], ["Moon", "Mars", "Jupiter"]),
    11: ("", ["Moon", "Mars"], ["Jupiter"], ["Sun", "Mercury", "Venus", "Saturn"]),
}
BAADHAKA_LORDS = {0: ["Saturn", "Rahu"], 1: ["Saturn"], 2: ["Jupiter"], 3: ["Venus"], 4: ["Mars"], 5: ["Jupiter"],
                  6: ["Sun"], 7: ["Moon"], 8: ["Mercury"], 9: ["Mars", "Ketu"], 10: ["Venus"], 11: ["Mercury"]}
AMSA_GROUPS = {
    "shadvarga": ([1, 2, 3, 9, 12, 30], {2: "Kimsuka", 3: "Vyanjana", 4: "Chaamara", 5: "Chatra", 6: "Kundala"}),
    "saptavarga": ([1, 2, 3, 7, 9, 12, 30], {2: "Kimsuka", 3: "Vyanjana", 4: "Chaamara", 5: "Chatra", 6: "Kundala",
                                             7: "Mukuta"}),
    "dasavarga": ([1, 2, 3, 7, 9, 10, 12, 16, 30, 60], {2: "Paarijaata", 3: "Uttama", 4: "Gopura", 5: "Simhaasana",
                                                       6: "Paaraavata", 7: "Devaloka", 8: "Brahmaloka",
                                                       9: "Airaavata", 10: "Sreedhaama"}),
    "shodasavarga": ([1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60],
                     {2: "Bhedaka", 3: "Kusuma", 4: "Nagapurusha", 5: "Kanduka", 6: "Kerala", 7: "Kalpavriksha",
                      8: "Chandanavana", 9: "Poornachandra", 10: "Uchchaisrava", 11: "Dhanvantari",
                      12: "Sooryakaanta", 13: "Vidruma", 14: "Indraasana", 15: "Goloka", 16: "Sree Vallabha"}),
}
BAALADI = ["Saisava (child, a quarter of its results)", "Kumaara (adolescent, half)", "Yuva (youth, full)",
           "Vriddha (old, some)", "Mrita (dead, none)"]
SAYANAADI = ["Nidraa (sleeping)", "Sayana (lying down)", "Upavesana (sitting)", "Netrapaani (eyes and hands)",
             "Prakaasana (shining)", "Gamana (going)", "Aagamana (returning)", "Sabhaa (at an assembly)",
             "Aagama (acquiring)", "Bhojana (eating)", "Nriyalipsaa (longing to dance)", "Kautuka (eager)"]
SAYANA_PLANET_NO = {"Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4, "Jupiter": 5, "Venus": 6, "Saturn": 7,
                    "Rahu": 8, "Ketu": 9}
SOUND_ADJ = {"Sun": 5, "Jupiter": 5, "Moon": 2, "Mars": 2, "Mercury": 3, "Venus": 3, "Saturn": 3, "Rahu": 4, "Ketu": 4}
CHATTERJEE_D9 = {1: "good", 4: "good", 5: "good", 7: "good", 9: "good", 10: "good", 2: "indifferent",
                 3: "bad", 6: "bad", 8: "bad", 12: "bad"}
EVENT_VARGAS = {"D9": "marriage and dharma", "D10": "career", "D7": "children", "D4": "home and property",
                "D24": "learning", "D20": "spiritual practice"}


def _vs(v, n):
    return {p: SIGNS.index(s) for p, s in v["divisional_charts"][f"D{n}"].items()}


def functional_nature(lag_sign, moon_waxing):
    yk, fb, fn, fm = FUNCTIONAL[lag_sign]
    fb, fn, fm = list(fb), list(fn), list(fm)
    note = None
    if lag_sign in (0, 6, 9):           # movable lagnas where PVR leaves the Moon out
        kendra_lord = True
        (fm if moon_waxing else fn).append("Moon")
        note = ("Moon owns a quadrant here; PVR leaves it out of Table 30. Waxing Moon (natural benefic) is treated as a "
                "functional malefic, waning Moon as functionally neutral (PVR 13.2).")
    out = {"lagna": SIGNS[lag_sign], "yogakaraka": yk or None, "functional_benefics": fb,
           "functional_neutrals": fn, "functional_malefics": fm, "source": "PVR Table 30"}
    if note:
        out["moon_note"] = note
    return out


def baadhakas(lag_sign):
    out = {}
    for h in range(1, 13):
        s = (lag_sign + h - 1) % 12
        bs = (s + (10 if s % 3 == 0 else 8 if s % 3 == 1 else 6)) % 12
        out[f"H{h}"] = {"sign": SIGNS[s], "baadhaka_sthaana": SIGNS[bs], "baadhaka": BAADHAKA_LORDS[s]}
    return out


def _good_sign(p, s, lon=None):
    if p not in EXALT_SIGN:
        return False
    return s == EXALT_SIGN[p] or s in SB.OWN[p] or s == SB.MOOLA[p][0]


def amsabala(v):
    out = {}
    for p in P7:
        row = {}
        for g, (charts, names) in AMSA_GROUPS.items():
            good = [f"D{n}" for n in charts if _good_sign(p, SIGNS.index(v["divisional_charts"][f"D{n}"][p]))]
            row[g] = {"count": len(good), "amsa": names.get(len(good)), "charts": good}
        out[p] = row
    return out


def _sign_aspects(src, s_src, s_tgt):
    return ((s_tgt - s_src) % 12 + 1) in ASPECT_HOUSES[src]


def _aspect_orb(a, la, b, lb):
    """How far b is from a's exact graha drishti (degrees), or None if no sign aspect."""
    h = (sign_of(lb) - sign_of(la)) % 12 + 1
    if h not in ASPECT_HOUSES[a]:
        return None
    return abs(wrap180(n360(lb - la) - EXACT[h]))


def avasthas(v, jd_birth, sunrise_jd, lag_sign):
    pl = v["planets"]
    si = {p: pl[p]["sign_index"] for p in NINE}
    lon = {p: pl[p]["lon"] for p in NINE}
    moon_nak = int(n360(lon["Moon"]) // NAK_SPAN) + 1
    hrs = (jd_birth - sunrise_jd) * 24.0
    ghati = int(hrs * 2.5) + 1                     # running ghati since sunrise (PVR fn. 52)
    out = {"inputs": {"moon_nakshatra_no": moon_nak, "ghati_running": ghati, "lagna_no": lag_sign + 1,
                       "sunrise_rule": "centre of disc with refraction"}}
    for p in NINE:
        d = deg_in_sign(lon[p])
        band = int(d // 6)
        if si[p] % 2 == 1:
            band = 4 - band
        row = {"baaladi": BAALADI[band]} if p in P7 else {}
        if p in P7:
            s = si[p]
            dig = pl[p]["dignity"]
            if dig == "exalted" or s in SB.OWN[p] or dig == "moolatrikona":
                jag = "Jaagrita (awake, full results)"
            elif dig == "debilitated" or SIGN_LORD[s] in SB.NAT_ENEMIES[p]:
                jag = "Sushupta (asleep, little result)"
            else:
                jag = "Swapna (dreaming, medium results)"
            row["jaagradaadi"] = jag
            # deeptaadi: primary mood from dignity / compound relation
            if dig == "exalted":
                mood = "Deepta (bright)"
            elif s in SB.OWN[p] or dig == "moolatrikona":
                mood = "Swastha (content)"
            else:
                rel = SB.compound_rel({q: si[q] for q in P7}, p, SIGN_LORD[s])
                mood = {"great friend": "Mudita (delighted)", "friend": "Saanta (peaceful)",
                        "neutral": "Deena (sad)", "enemy": "Duhkhita (distressed)",
                        "great enemy": "Duhkhita (distressed)"}[rel]
            flags = []
            joined = [q for q in NINE if q != p and si[q] == s]
            if any(q in MALEFICS for q in joined):
                flags.append("Vikala (joined by malefics)")
            if SIGN_LORD[s] in MALEFICS:
                flags.append("Khala (in a malefic's sign)")
            if p != "Sun" and pl[p].get("combust"):
                flags.append("Kopita (joined closely by the Sun)")
            asp_by = [q for q in NINE if q != p and _sign_aspects(q, si[q], s)]
            enemies = SB.NAT_ENEMIES[p]
            if pl[p]["house"] == 5 and any(q in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") for q in joined):
                flags.append("Lajjita (ashamed)")
            if dig in ("exalted", "moolatrikona"):
                flags.append("Garvita (proud)")
            if (SIGN_LORD[s] in enemies or any(q in enemies for q in joined + asp_by) or "Saturn" in joined):
                flags.append("Kshudhita (hungry)")
            if s in (3, 7, 11) and any(q in enemies for q in asp_by) and not any(
                    q in ("Jupiter", "Venus") for q in asp_by):
                flags.append("Trishita (thirsty)")
            if ("Sun" in joined and p != "Sun") and any(q in MALEFICS or q in enemies for q in asp_by):
                flags.append("Kshobhita (agitated)")
            row["deeptaadi"] = mood
            row["mood_flags"] = flags
        C = int(n360(lon[p]) // NAK_SPAN) + 1
        A = int(d // (30 / 9)) + 1
        idx = (C * SAYANA_PLANET_NO[p] * A + moon_nak + ghati + lag_sign + 1) % 12
        row["sayanaadi"] = SAYANAADI[idx]
        row["sayanaadi_index"] = idx if idx else 12
        row["sayanaadi_terms"] = {"C": C, "P": SAYANA_PLANET_NO[p], "A": A}
        out[p] = row
    out["note"] = ("Sayanaadi needs the ghati of birth, so it depends on an accurate birth time. Its cheshta/drishti "
                    "strength also needs the first sound of the given name (PVR Table 37); pass the name sound to "
                    "sayanaadi_strength() if wanted.")
    return out


def sayanaadi_strength(index, planet, sound_number):
    r = (index * index + sound_number) % 12 + SOUND_ADJ[planet]
    return {1: "drishti (medium results)", 2: "cheshta (full results)", 0: "vicheshta (little result)"}[r % 3]


def raja_yogas(v, fn, amsas, avs):
    pl = v["planets"]
    lag = v["_lag_sign"] if "_lag_sign" in v else SIGNS.index(v["lagna"]["sign"])
    lord = {h: SIGN_LORD[(lag + h - 1) % 12] for h in range(1, 13)}
    si = {p: pl[p]["sign_index"] for p in NINE}
    lon = {p: pl[p]["lon"] for p in NINE}
    kend, tri = [1, 4, 7, 10], [1, 5, 9]
    seen, out = set(), []
    for kh in kend:
        for th in tri:
            if kh == th:
                continue
            a, b = lord[kh], lord[th]
            if a == b:
                if kh != 1 and th != 1:
                    out.append({"planets": [a], "houses": [kh, th], "kind": "yogakaraka (owns a quadrant and a trine)"})
                continue
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            assoc, orb = None, None
            if si[a] == si[b]:
                assoc, orb = "conjunction", abs(wrap180(lon[a] - lon[b]))
            elif SIGN_LORD[si[a]] == b and SIGN_LORD[si[b]] == a:
                assoc = "parivartana (exchange)"
            else:
                o1, o2 = _aspect_orb(a, lon[a], b, lon[b]), _aspect_orb(b, lon[b], a, lon[a])
                if o1 is not None and o2 is not None:
                    assoc, orb = "mutual aspect", min(o1, o2)
            if not assoc:
                continue
            seen.add(key)
            houses = sorted({h for h in range(1, 13) if lord[h] in key and (h in kend or h in tri)})
            blem = []
            fm = set(fn["functional_malefics"])
            for p in key:
                if pl[p].get("combust"):
                    blem.append(f"{p} combust")
                if pl[p]["dignity"] == "debilitated":
                    blem.append(f"{p} debilitated")
                if pl[p]["dignity"] == "enemy's sign":
                    blem.append(f"{p} in an enemy's sign")
                if "Mrita" in avs[p]["baaladi"]:
                    blem.append(f"{p} in Mrita avastha")
                aff = [q for q in NINE if q not in key and q in fm and (si[q] == si[p] or _sign_aspects(q, si[q], si[p]))]
                if aff:
                    blem.append(f"{p} afflicted by functional malefic(s) {', '.join(aff)}")
            counts = [amsas[p]["dasavarga"]["count"] for p in key]
            low = min(counts)
            name = AMSA_GROUPS["dasavarga"][1].get(low)
            level = {0: "ordinary", 1: "ordinary", 2: "Paarijaata level: rules well", 3: "Uttama level: good, with assets",
                     4: "Gopura level: great, respected by peers", 5: "Simhaasana level: very high"}.get(
                         low, "exceptional (count 6+)")
            close = orb is not None and orb <= 6
            out.append({"planets": list(key), "houses": houses,
                        "kind": "Dharma-Karmadhipati" if set(houses) >= {9, 10} else "Raaja yoga",
                        "association": assoc, "orb_deg": None if orb is None else round(orb, 2),
                        "close_within_6_deg": close if orb is not None else None,
                        "blemishes": blem,
                        "dasavarga_counts": dict(zip(key, counts)),
                        "dasavarga_amsa_of_weaker": name,
                        "magnitude": level + ("" if (close or orb is None) and not blem else
                                              "; reduced by " + ("a wide orb" if orb is not None and not close else "") +
                                              ("; " if (orb is not None and not close) and blem else "") +
                                              ("blemishes" if blem else ""))})
    return {"yogas": out, "rule": ("PVR 11.7.1-11.7.2: quadrant lord with trine lord by conjunction, mutual graha "
                                   "drishti or exchange (lagna is both). Full results need a close link (about 6 deg), "
                                   "no combustion, debilitation, enemy sign or functional-malefic affliction; the "
                                   "Dasavarga count of the weaker planet sets the level (2 Paarijaata ... 5 Simhaasana).")}


def jeeva_sharira(v):
    pl = v["planets"]
    out = {}
    for p in NINE:
        j = pl[p]["nakshatra_lord"]
        jl = pl[j]["nakshatra_lord"]
        sh = pl[j]["sign_lord"] if jl == j else jl
        out[p] = {"jeeva": j, "sharira": sh}
    return out


def _sambandha(a, b, si):
    out = []
    if si[a] == si[b]:
        out.append("conjunction")
    if SIGN_LORD[si[a]] == b and SIGN_LORD[si[b]] == a:
        out.append("exchange")
    ab, ba = _sign_aspects(a, si[a], si[b]), _sign_aspects(b, si[b], si[a])
    if ab and ba:
        out.append("mutual aspect")
    elif ab:
        out.append(f"{a} aspects {b}")
    elif ba:
        out.append(f"{b} aspects {a}")
    return out


def _lord_view(p, v, lag, moon_sign, js, fn, sb, avs):
    pl = v["planets"]
    s = pl[p]["sign_index"]
    d9 = _vs(v, 9)
    h9 = (d9[p] - d9["Lagna"]) % 12 + 1
    row = {"house_from_lagna": pl[p]["house"], "house_from_moon": (s - moon_sign) % 12 + 1,
           "navamsa_house": h9, "navamsa_house_grade": CHATTERJEE_D9.get(h9, "not graded"),
           "jeeva": js[p]["jeeva"], "sharira": js[p]["sharira"],
           "jeeva_houses_from_lagna": pl[js[p]["jeeva"]]["house"],
           "owns_houses": [h for h in range(1, 13) if SIGN_LORD[(lag + h - 1) % 12] == p],
           "functional_nature": ("yogakaraka" if fn["yogakaraka"] == p else
                                 "functional benefic" if p in fn["functional_benefics"] else
                                 "functional malefic" if p in fn["functional_malefics"] else
                                 "functional neutral" if p in fn["functional_neutrals"] else "node"),
           "baadhaka_for_lagna": p in BAADHAKA_LORDS[lag]}
    if p in sb:
        row["shadbala_ratio"] = sb[p]["ratio"]
    if p in avs and "baaladi" in avs[p]:
        row["avastha"] = {"baaladi": avs[p]["baaladi"], "mood": avs[p]["deeptaadi"], "flags": avs[p]["mood_flags"]}
    vg = {}
    for key in EVENT_VARGAS:
        vs = _vs(v, int(key[1:]))
        h = (vs[p] - vs["Lagna"]) % 12 + 1
        vg[key] = {"house": h, "in_lagna_or_10th": h in (1, 10), "sign": SIGNS[vs[p]]}
    row["vargas"] = vg
    return row


def dasha_views(v, js, fn, sb, avs, upcoming=3):
    pl = v["planets"]
    lag = SIGNS.index(v["lagna"]["sign"])
    moon_sign = pl["Moon"]["sign_index"]
    cur = v["dashas"]["vimshottari"]["current"]
    md, ad = cur["mahadasha"]["lord"], cur["antardasha"]["lord"]
    out = {"mahadasha": {"lord": md, **_lord_view(md, v, lag, moon_sign, js, fn, sb, avs)}}

    def pair(a, b):
        rel = (pl[b]["sign_index"] - pl[a]["sign_index"]) % 12 + 1
        lab = "same lord" if a == b else "6/8 (strained)" if rel in (6, 8) else "2/12 (separating)" if rel in (2, 12) else (
            "1/7 (opposite or together)" if rel in (1, 7) else "kendra/trikona (supportive)" if rel in (4, 10, 5, 9) else
            "3/11 (effort brings gains)")
        vgs = {}
        for key in EVENT_VARGAS:
            vs = _vs(v, int(key[1:]))
            vgs[key] = _sambandha(a, b, vs)
        return {"antardasha_from_mahadasha_lord": rel, "label": lab, "sambandha_by_varga": vgs}
    out["antardasha"] = {"lord": ad, **_lord_view(ad, v, lag, moon_sign, js, fn, sb, avs), **pair(md, ad)}
    out["antardasha"]["house_from_mahadasha_lord"] = (pl[ad]["sign_index"] - pl[md]["sign_index"]) % 12 + 1
    nxt = []
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        for a in m["antardashas"]:
            if a["start"] > cur["antardasha"]["start"] and len(nxt) < upcoming:
                nxt.append({"maha": m["lord"], "antar": a["lord"], "start": a["start"], "end": a["end"],
                            **{k: vv for k, vv in pair(m["lord"], a["lord"]).items() if k != "sambandha_by_varga"}})
    out["next_antardashas"] = nxt
    out["rule"] = ("Antardasha lord 6/8 or 2/12 from the mahadasha lord tones the sub-period down (Chatterjee; Trivedi "
                   "uses 2/12 as separating). Navamsa house of a dasha lord: 1, 4, 5, 7, 9, 10 good; 2 indifferent; "
                   "3, 6, 8, 12 bad (Chatterjee rule b). Event vargas: lord in the varga lagna or 10th, and sambandha "
                   "between the two lords there (Boney).")
    return out


KARAKA_TRAPS = [("D24", "Mercury", 4), ("D7", "Jupiter", 1), ("D9", "Venus", 7), ("D12", "Sun", 12), ("D12", "Moon", 12)]


def varga_rubric(v, avs):
    pl = v["planets"]
    out = {}
    for key in ("D9", "D10", "D7", "D4", "D24", "D12"):
        n = int(key[1:])
        vs = _vs(v, n)
        vl = vs["Lagna"]
        lord = SIGN_LORD[vl]
        h = (vs[lord] - vl) % 12 + 1
        notes = []
        if _good_sign(lord, vs[lord]):
            notes.append(f"varga lagna lord {lord} in own/exaltation/moolatrikona sign")
        if lord in EXALT_SIGN and vs[lord] == (EXALT_SIGN[lord] + 6) % 12:
            notes.append(f"varga lagna lord {lord} debilitated in {key}: needs cancellation before it counts")
        if h in (6, 8, 12):
            notes.append(f"varga lagna lord in house {h} of {key}")
        if pl.get(lord, {}).get("combust"):
            notes.append(f"{lord} is combust in the birth chart: a good {key} placement does not rescue it")
        if pl.get(lord, {}).get("dignity") == "debilitated":
            notes.append(f"{lord} is debilitated in the birth chart: needs cancellation")
        for k2, kar, hh in KARAKA_TRAPS:
            if k2 == key and (vs[kar] - vl) % 12 + 1 == hh:
                notes.append(f"{kar} in house {hh} of {key}: karaka in its own house in its varga hurts that matter (Rayudu)")
        si = {p: vs[p] for p in NINE}
        arg = rasidasa.argala(si, vl)["H1"]["argalas"]
        out[key] = {"varga_lagna": SIGNS[vl], "lagna_lord": lord, "lagna_lord_house": h, "notes": notes,
                    "argala_on_varga_lagna": [{"from_house": a["from_house"], "planets": a["planets"],
                                               "state": a["state"]} for a in arg],
                    "matter": EVENT_VARGAS.get(key, "parents")}
    out["rule"] = ("Rayudu ch. 9: judge a varga by its own lagna lord, not D-1 house lords; combust or war-defeated "
                    "planets are not rescued by a good varga; debilitation needs cancellation; argala on the varga "
                    "lagna shows which dasha delivers the result.")
    return out


def build(v, jd_birth, sunrise_jd, sb_bphs):
    lag = SIGNS.index(v["lagna"]["sign"])
    waxing = v["panchang"]["paksha"].lower().startswith("shukla")
    fn = functional_nature(lag, waxing)
    am = amsabala(v)
    avs = avasthas(v, jd_birth, sunrise_jd, lag)
    js = jeeva_sharira(v)
    out = {"functional_nature": fn, "baadhakas": baadhakas(lag), "amsabala": am, "avasthas": avs,
           "raja_yogas": raja_yogas(v, fn, am, avs), "jeeva_sharira": js,
           "dasha_views": dasha_views(v, js, fn, sb_bphs, avs), "varga_rubric": varga_rubric(v, avs)}
    return out
