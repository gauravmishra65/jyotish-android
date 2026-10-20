"""ashtakoota.py - Guna Milan (Ashtakoota, /36) and the South Indian ten Porutham.

Varna(1), Tara(3), Graha Maitri(5), Gana(6), Bhakoot(7), Nadi(8) follow rules that agree across sources.
Vashya(2) and Yoni(4) are scored from NAMED published tables, because the tables differ:
  * Vashya: three tables are carried (onlinejyotish.com default, AstroYogi, Saravali.de). The /36 total uses the
    default; the report also gives the lowest and highest total the other tables would produce.
  * Yoni: the common North Indian 14x14 table (symmetric; sworn enemies 0, same animal 4).
The six-koota /30 subtotal is kept so older readings stay comparable.
"""
from common import SIGNS, SIGN_LORD, NAKSHATRAS, NAK_SPAN
from vedic import FRIENDS, ENEMIES

VARNA = {3: 4, 7: 4, 11: 4, 0: 3, 4: 3, 8: 3, 1: 2, 5: 2, 9: 2, 2: 1, 6: 1, 10: 1}  # sign -> rank
VARNA_NAME = {4: "Brahmin", 3: "Kshatriya", 2: "Vaishya", 1: "Shudra"}
GANA = {}
for n in ("Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Revati"):
    GANA[n] = "Deva"
for n in ("Bharani", "Rohini", "Ardra", "Purva Phalguni", "Uttara Phalguni", "Purva Ashadha", "Uttara Ashadha",
          "Purva Bhadrapada", "Uttara Bhadrapada"):
    GANA[n] = "Manushya"
for n in ("Krittika", "Ashlesha", "Magha", "Chitra", "Vishakha", "Jyeshtha", "Mula", "Dhanishta", "Shatabhisha"):
    GANA[n] = "Rakshasa"
GANA_SCORE = {("Deva", "Deva"): 6, ("Deva", "Manushya"): 6, ("Deva", "Rakshasa"): 1,
              ("Manushya", "Deva"): 5, ("Manushya", "Manushya"): 6, ("Manushya", "Rakshasa"): 0,
              ("Rakshasa", "Deva"): 1, ("Rakshasa", "Manushya"): 0, ("Rakshasa", "Rakshasa"): 6}  # (groom, bride)
NADI_PATTERN = ["Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi"]
YONI = ["Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow",
        "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion",
        "Horse", "Lion", "Cow", "Elephant"]
YONI_ENEMY = {frozenset(p) for p in [("Cow", "Tiger"), ("Elephant", "Lion"), ("Horse", "Buffalo"),
                                     ("Dog", "Deer"), ("Serpent", "Mongoose"), ("Monkey", "Sheep"), ("Cat", "Rat")]}

# ---- Yoni 14x14 (common North Indian table; symmetric, so bride/groom order does not matter)
YONI_ORDER = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer",
              "Monkey", "Mongoose", "Lion"]
YONI_MATRIX = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 1, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [1, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4]]
YONI_TABLE_NAME = "common North Indian 14x14 Yoni table"

# ---- Vashya: group order and three published tables, all indexed [bride group][groom group]
VASHYA_ORDER = ["Chatushpad (quadruped)", "Dwipad (human)", "Jalachar (water)", "Vanachar (wild)", "Keeta (insect)"]
VASHYA_TABLES = {
    "onlinejyotish.com": [[2, 1, 1, 0, 1], [1, 2, 0.5, 0, 1], [1, 0.5, 2, 1, 1], [0, 0, 1, 2, 0], [1, 0, 1, 0, 2]],
    "AstroYogi": [[2, 1, 1, 1.5, 1], [1, 2, 1.5, 0, 1], [1, 1.5, 2, 1, 1], [0, 0, 0, 2, 0], [1, 1, 1, 0, 2]],
    "Saravali.de": [[2, 0.5, 1, 0, 2], [0.5, 2, 0, 0, 0], [1, 0, 2, 2, 2], [0, 0, 2, 2, 0], [1, 0, 1, 0, 2]],
}
VASHYA_DEFAULT = "onlinejyotish.com"

# ---- South Indian (Porutham) data
SOUTH_VASYA = [[4, 7], [3, 6], [5], [7, 8], [6], [2, 11], [5, 9], [3], [11], [0, 10], [0], [9]]   # sign -> signs under its control
DINA_GOOD = (2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26)


def vashya_group(sign_idx, moon_lon):
    d = moon_lon % 30
    if sign_idx in (2, 5, 6, 10):
        return "Dwipad (human)"
    if sign_idx == 8:
        return "Dwipad (human)" if d < 15 else "Chatushpad (quadruped)"
    if sign_idx in (0, 1):
        return "Chatushpad (quadruped)"
    if sign_idx == 9:
        return "Chatushpad (quadruped)" if d < 15 else "Jalachar (water)"
    if sign_idx in (3, 11):
        return "Jalachar (water)"
    if sign_idx == 4:
        return "Vanachar (wild)"
    return "Keeta (insect)"


def _rel(a, b):
    if a == b:
        return "same"
    if b in FRIENDS.get(a, []):
        return "friend"
    if b in ENEMIES.get(a, []):
        return "enemy"
    return "neutral"


def _person(v):
    ni = int((v["moon_lon"] % 360) // NAK_SPAN)
    s = v["moon_sign_index"]
    return {"nak_i": ni, "nak": NAKSHATRAS[ni], "sign": s, "lord": SIGN_LORD[s], "lon": v["moon_lon"]}


def match(A, B, bride="B"):
    a, b = _person(A), _person(B)
    groom, brd = (a, b) if bride == "B" else (b, a)
    res = {"groom_is": "A" if bride == "B" else "B", "bride_is": bride, "kootas": {}}
    K = res["kootas"]
    # Varna
    gv, bv = VARNA[groom["sign"]], VARNA[brd["sign"]]
    K["varna"] = {"max": 1, "score": 1 if gv >= bv else 0, "groom": VARNA_NAME[gv], "bride": VARNA_NAME[bv]}
    # Vashya (classification; score only if identical group)
    vg, vb = vashya_group(groom["sign"], groom["lon"]), vashya_group(brd["sign"], brd["lon"])
    vi, vj = VASHYA_ORDER.index(vb), VASHYA_ORDER.index(vg)
    by_table = {name: float(t[vi][vj]) for name, t in VASHYA_TABLES.items()}
    K["vashya"] = {"max": 2, "score": by_table[VASHYA_DEFAULT], "groom": vg, "bride": vb,
                   "table": VASHYA_DEFAULT, "score_by_table": by_table,
                   "status": "same group = 2 in every table" if vg == vb else
                             ("all tables agree" if len(set(by_table.values())) == 1 else "tables differ for this pair")}
    # Tara
    def tara(from_n, to_n):
        r = ((to_n - from_n) % 27 + 1) % 9
        return 9 if r == 0 else r
    t1, t2 = tara(brd["nak_i"], groom["nak_i"]), tara(groom["nak_i"], brd["nak_i"])
    bad = (3, 5, 7)
    n_bad = (t1 in bad) + (t2 in bad)
    K["tara"] = {"max": 3, "score": {0: 3.0, 1: 1.5, 2: 0.0}[n_bad], "bride_to_groom_remainder": t1,
                 "groom_to_bride_remainder": t2, "unfavourable_remainders": [3, 5, 7]}
    # Yoni
    yg, yb = YONI[groom["nak_i"]], YONI[brd["nak_i"]]
    ysc = float(YONI_MATRIX[YONI_ORDER.index(yb)][YONI_ORDER.index(yg)])
    ystat = ("same yoni" if yg == yb else "sworn enemies" if frozenset((yg, yb)) in YONI_ENEMY else
             {3: "friendly", 2: "neutral", 1: "unfriendly"}.get(int(ysc), "graded"))
    K["yoni"] = {"max": 4, "score": ysc, "groom": yg, "bride": yb, "status": ystat, "table": YONI_TABLE_NAME}
    # Graha Maitri
    r1, r2 = _rel(groom["lord"], brd["lord"]), _rel(brd["lord"], groom["lord"])
    pair = sorted([r1, r2])
    if "same" in pair or pair == ["friend", "friend"]:
        gm = 5.0
    elif pair == ["friend", "neutral"]:
        gm = 4.0
    elif pair == ["neutral", "neutral"]:
        gm = 3.0
    elif pair == ["enemy", "friend"]:
        gm = 1.0
    elif pair == ["enemy", "neutral"]:
        gm = 0.5
    else:
        gm = 0.0
    K["graha_maitri"] = {"max": 5, "score": gm, "groom_moon_sign_lord": groom["lord"], "bride_moon_sign_lord": brd["lord"],
                         "relations": [r1, r2], "note": "0.5 for neutral+enemy is used by some tables and 0 by others."}
    # Gana
    gg, gb = GANA[groom["nak"]], GANA[brd["nak"]]
    K["gana"] = {"max": 6, "score": GANA_SCORE[(gg, gb)], "groom": gg, "bride": gb,
                 "note": "Common (groom, bride) matrix; Deva-Manushya values differ between publishers (5 or 6)."}
    # Bhakoot
    rel = (brd["sign"] - groom["sign"]) % 12 + 1
    pair_rel = tuple(sorted((rel, ((groom["sign"] - brd["sign"]) % 12) + 1)))
    dosha = pair_rel in ((2, 12), (5, 9), (6, 8))
    K["bhakoot"] = {"max": 7, "score": 0 if dosha else 7, "moon_signs": [SIGNS[groom["sign"]], SIGNS[brd["sign"]]],
                    "relative_positions": list(pair_rel), "dosha": dosha,
                    "note": "Bhakoot dosha is commonly softened when the two Moon-sign lords are the same or mutual friends - a judgement for the reader."}
    # Nadi
    ng, nb = NADI_PATTERN[groom["nak_i"] % 6], NADI_PATTERN[brd["nak_i"] % 6]
    K["nadi"] = {"max": 8, "score": 0 if ng == nb else 8, "groom": ng, "bride": nb, "dosha": ng == nb,
                 "note": "Same Nadi is scored 0; traditional exceptions (e.g. same nakshatra with different pada, or different rashi with same nakshatra) are for the reader."}
    six = ["varna", "tara", "graha_maitri", "gana", "bhakoot", "nadi"]
    res["subtotal_six_kootas"] = {"score": sum(K[k]["score"] for k in six), "out_of": 30}
    total = sum(K[k]["score"] for k in K)
    others = [res["subtotal_six_kootas"]["score"] + K["yoni"]["score"] + v for v in K["vashya"]["score_by_table"].values()]
    res["total_36"] = {"score": total, "out_of": 36, "vashya_table": VASHYA_DEFAULT, "yoni_table": YONI_TABLE_NAME,
                       "range_across_vashya_tables": [min(others), max(others)],
                       "band": ("below 18: commonly not recommended without strong other factors" if total < 18 else
                                "18 to 24: acceptable" if total <= 24 else
                                "25 to 32: good" if total <= 32 else "above 32: excellent"),
                       "band_note": "Bands are the customary ones (18 is the usual minimum). They describe the Moon-based score only."}
    res["not_scored"] = []
    res["method_note"] = ("The /36 total uses the named Vashya and Yoni tables; Vashya tables disagree, so the range is shown. "
                          "If the client's tradition uses another table, say so and quote that total. Nadi and Bhakoot exceptions are "
                          "not applied to the total (see further_kootas_and_melapak). Moon-based matching is one layer; Mangal comparison "
                          "and 7th-house/Navamsa analysis are separate.")
    res["porutham"] = porutham(groom, brd)
    res["moon_positions"] = {"A": {"nakshatra": a["nak"], "sign": SIGNS[a["sign"]]}, "B": {"nakshatra": b["nak"], "sign": SIGNS[b["sign"]]}}
    return res


# ------------------------------------------------------------------ Trivedi's further kootas and melapak
RAJJU = {"Pada (foot)": ["Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"],
         "Kati (waist)": ["Bharani", "Pushya", "Purva Phalguni", "Anuradha", "Purva Ashadha", "Uttara Bhadrapada"],
         "Nabhi (navel)": ["Krittika", "Punarvasu", "Uttara Phalguni", "Vishakha", "Uttara Ashadha", "Purva Bhadrapada"],
         "Kantha (neck)": ["Rohini", "Ardra", "Hasta", "Swati", "Shravana", "Shatabhisha"],
         "Siro (head)": ["Mrigashira", "Chitra", "Dhanishta"]}
VEDHA_TRIVEDI = [("Ashwini", "Jyeshtha"), ("Bharani", "Anuradha"), ("Krittika", "Vishakha"), ("Rohini", "Swati"),
                 ("Ardra", "Shravana"), ("Punarvasu", "Uttara Ashadha"), ("Purva Phalguni", "Uttara Bhadrapada"),
                 ("Uttara Phalguni", "Purva Bhadrapada"), ("Hasta", "Shatabhisha"), ("Mrigashira", "Dhanishta")]
VEDHA_OTHERS = [("Pushya", "Purva Ashadha"), ("Ashlesha", "Mula"), ("Magha", "Revati"),
                ("Chitra", "Mrigashira"), ("Chitra", "Dhanishta")]
MALEFIC_HOUSES = (1, 2, 4, 7, 8, 12)


def _rajju_of(nak):
    for k, v in RAJJU.items():
        if nak in v:
            return k
    return None


def extra_kootas(A, B, bride="B"):
    """Rajju, Vedha, Mahendra, Stree-deergha (classified, unscored), Nadi exceptions, graha and bhava melapak
    (Trivedi, 'Matching of Horoscopes'; Raman's lagna rule)."""
    a, b = _person(A), _person(B)
    groom, brd = (a, b) if bride == "B" else (b, a)
    G, Bv = (A, B) if bride == "B" else (B, A)
    out = {}
    rg, rb = _rajju_of(groom["nak"]), _rajju_of(brd["nak"])
    out["rajju"] = {"groom": rg, "bride": rb, "same_rajju": rg == rb,
                    "note": "Classical texts want different rajjus. Trivedi's text attaches dire readings to each same rajju; "
                            "this report never repeats those as predictions."}
    pair = {groom["nak"], brd["nak"]}
    tv = any(pair == {x, y} for x, y in VEDHA_TRIVEDI)
    ov = any(pair == {x, y} for x, y in VEDHA_OTHERS)
    out["vedha"] = {"in_trivedi_list": tv, "in_other_common_lists": ov,
                    "note": "Trivedi lists ten pairs; many tables add Pushya-Purva Ashadha, Ashlesha-Mula, Magha-Revati and "
                            "the Chitra-Mrigashira-Dhanishta triad."}
    cnt = (groom["nak_i"] - brd["nak_i"]) % 27 + 1          # groom counted from bride
    out["mahendra"] = {"groom_count_from_bride": cnt, "present": cnt in (4, 7, 10, 13, 16, 19, 22, 25),
                       "note": "Trivedi gives it little weight."}
    out["stree_deergha"] = {"groom_count_from_bride": cnt, "beyond_7": cnt > 7, "beyond_9": cnt > 9, "beyond_13": cnt > 13,
                            "note": "Authorities disagree (beyond 7, 9 or 13); Trivedi says to ignore it. Classified, not scored."}
    same_nadi = NADI_PATTERN[groom["nak_i"] % 6] == NADI_PATTERN[brd["nak_i"] % 6]
    exc = None
    if same_nadi:
        if groom["sign"] == brd["sign"] and groom["nak_i"] != brd["nak_i"]:
            exc = "same Moon sign, different nakshatras"
        elif groom["nak_i"] == brd["nak_i"] and G.get("moon_pada") != Bv.get("moon_pada"):
            exc = "same nakshatra, different padas"
    out["nadi_exception"] = {"same_nadi": same_nadi, "exception": exc,
                             "treated_as_cancelled": bool(exc), "note": "Trivedi: these two exceptions cancel Nadi dosha."}

    def afflictions(P):
        ph = P.get("planet_houses") or {}
        hit = {p: ph[p] for p in ("Mars", "Saturn", "Sun", "Rahu", "Ketu") if ph.get(p) in MALEFIC_HOUSES}
        vm = ph.get("Venus") == ph.get("Mars") and ph.get("Venus") in (1, 7)
        return {"malefics_in_1_2_4_7_8_12": hit, "count": len(hit), "venus_mars_together_in_1_or_7": vm}
    ga, gb = afflictions(G), afflictions(Bv)
    out["graha_melapak"] = {"groom": ga, "bride": gb, "balanced": abs(ga["count"] - gb["count"]) <= 1,
                            "rule": "Trivedi: a partner with marked malefic placements should marry one with similar placements."}
    lg, lb = G.get("lagna_sign_index"), Bv.get("lagna_sign_index")
    bm = []
    if lg is not None and lb is not None:
        if (lg + 6) % 12 == lb:
            bm.append("groom's 7th sign is the bride's lagna")
        if (lb + 6) % 12 == lg:
            bm.append("bride's 7th sign is the groom's lagna")
        if groom["sign"] in (lb, (lb + 6) % 12):
            bm.append("groom's Moon sign is the bride's lagna or 7th")
        if brd["sign"] in (lg, (lg + 6) % 12):
            bm.append("bride's Moon sign is the groom's lagna or 7th")
    five = {"groom": G.get("fifth_lord_ratio"), "bride": Bv.get("fifth_lord_ratio")}
    out["bhava_melapak"] = {"lagna_links": bm, "fifth_lord_shadbala_ratio": five,
                            "rule": "Raman: one's 7th sign as the other's lagna, or one's Moon sign as the other's lagna or 7th, "
                                    "helps; one partner's strong 5th lord and Jupiter can offset the other's weak 5th (Trivedi)."}
    return out


# ------------------------------------------------------------------ South Indian ten Porutham
def porutham(groom, brd):
    """Ten Porutham (Tamil / South Indian practice), basic rules only. Each item is a yes / partial / no
    agreement, not a score. Counts run from the bride's star (or sign) to the groom's, inclusive.
    Exceptions some panchangams apply (same-star rules, pada exceptions) are not applied; say so if asked."""
    cnt = (groom["nak_i"] - brd["nak_i"]) % 27 + 1
    sign_cnt = (groom["sign"] - brd["sign"]) % 12 + 1
    P = {}
    P["dina"] = {"ok": cnt in DINA_GOOD, "count": cnt,
                 "rule": "groom's star counted from the bride's is 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24 or 26"}
    gg, gb = GANA[groom["nak"]], GANA[brd["nak"]]
    P["gana"] = {"ok": gg == gb or {gg, gb} == {"Deva", "Manushya"}, "groom": gg, "bride": gb,
                 "rule": "same gana, or Deva with Manushya"}
    P["mahendra"] = {"ok": cnt in (4, 7, 10, 13, 16, 19, 22, 25), "count": cnt,
                     "rule": "count is 4, 7, 10, 13, 16, 19, 22 or 25"}
    P["stree_deergha"] = {"ok": cnt > 13, "partial": 7 < cnt <= 13, "count": cnt,
                          "rule": "count above 13 agrees; 8 to 13 is accepted by some panchangams"}
    yg, yb = YONI[groom["nak_i"]], YONI[brd["nak_i"]]
    south_enemy = YONI_ENEMY | {frozenset(("Serpent", "Rat"))}
    P["yoni"] = {"ok": frozenset((yg, yb)) not in south_enemy, "groom": yg, "bride": yb,
                 "rule": "not an enemy pair (South Indian practice adds Serpent and Rat to the seven North Indian pairs)"}
    P["rasi"] = {"ok": sign_cnt > 6 or sign_cnt == 1, "count": sign_cnt,
                 "rule": "groom's Moon sign counted from the bride's is 7 or more, or the same sign"}
    r1, r2 = _rel(groom["lord"], brd["lord"]), _rel(brd["lord"], groom["lord"])
    P["rasi_adhipati"] = {"ok": "enemy" not in (r1, r2), "partial": "enemy" in (r1, r2) and ("friend" in (r1, r2) or "same" in (r1, r2)),
                          "groom_lord": groom["lord"], "bride_lord": brd["lord"], "relations": [r1, r2],
                          "rule": "neither Moon-sign lord is the other's natural enemy"}
    P["vasya"] = {"ok": groom["sign"] in SOUTH_VASYA[brd["sign"]] or brd["sign"] in SOUTH_VASYA[groom["sign"]],
                  "rule": "one Moon sign is vasya (under the control) of the other, by the classical sign list"}
    rg, rb = _rajju_of(groom["nak"]), _rajju_of(brd["nak"])
    P["rajju"] = {"ok": rg != rb, "groom": rg, "bride": rb, "rule": "the two stars fall in different rajjus"}
    pair = {groom["nak"], brd["nak"]}
    vedha = any(pair == {x, y} for x, y in VEDHA_TRIVEDI + VEDHA_OTHERS)
    P["vedha"] = {"ok": not vedha, "rule": "the two stars are not a vedha pair"}
    agree = sum(1 for v in P.values() if v["ok"])
    return {"items": P, "agree": agree, "out_of": 10,
            "essential": {k: P[k]["ok"] for k in ("rajju", "vedha", "dina", "gana", "yoni", "rasi")},
            "note": ("Most Tamil practice treats Rajju and Vedha as essential and wants Dina, Gana, Yoni and Rasi too. "
                     "Report agreement plainly; never read a missing Rajju as a prediction about a spouse's life.")}
