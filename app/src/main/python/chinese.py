"""chinese.py - BaZi (Four Pillars) from astronomical solar terms, plus a Zi Wei Dou Shu wrapper.

Year/Month pillars use the exact instant of the solar term (UT), never the lunar new year.
Day/Hour pillars use true solar time (longitude + equation of time) with the standard-time
result computed alongside, so any disagreement is flagged instead of hidden.
"""
import datetime as dt
import swisseph as swe
from common import jd_to_dt, dt_to_jd, n360

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEM_PY = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCH_PY = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ANIMAL = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
EL = ["Wood", "Fire", "Earth", "Metal", "Water"]
STEM_EL = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
BRANCH_EL = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]
HIDDEN = {0: [9], 1: [5, 9, 7], 2: [0, 2, 4], 3: [1], 4: [4, 1, 9], 5: [2, 6, 4], 6: [3, 5],
          7: [5, 3, 1], 8: [6, 8, 4], 9: [7], 10: [4, 7, 3], 11: [8, 0]}
JIE_DEG = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]  # month-starting terms, Yin..Chou
JIE_NAMES = ["Li Chun", "Jing Zhe", "Qing Ming", "Li Xia", "Mang Zhong", "Xiao Shu",
             "Li Qiu", "Bai Lu", "Han Lu", "Li Dong", "Da Xue", "Xiao Han"]
TEN_GODS = {(0, 0): "Friend (比肩)", (0, 1): "Rob Wealth (劫财)", (1, 0): "Eating God (食神)",
            (1, 1): "Hurting Officer (伤官)", (2, 0): "Indirect Wealth (偏财)", (2, 1): "Direct Wealth (正财)",
            (3, 0): "Seven Killings (七杀)", (3, 1): "Direct Officer (正官)",
            (4, 0): "Indirect Resource (偏印)", (4, 1): "Direct Resource (正印)"}
SIX_HARMONY = {frozenset(p) for p in [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]}
SIX_CLASH = {frozenset((i, i + 6)) for i in range(6)}
HARM = {frozenset(p) for p in [(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)]}
DESTRUCTION = {frozenset(p) for p in [(0, 9), (1, 4), (2, 11), (3, 6), (5, 8), (7, 10)]}
THREE_HARMONY = [((8, 0, 4), "Water"), ((11, 3, 7), "Wood"), ((2, 6, 10), "Fire"), ((5, 9, 1), "Metal")]
THREE_MEETING = [((2, 3, 4), "Wood"), ((5, 6, 7), "Fire"), ((8, 9, 10), "Metal"), ((11, 0, 1), "Water")]
PUNISH_TRIPLE = [((2, 5, 8), "ungrateful punishment"), ((1, 10, 7), "bullying punishment")]
SELF_PUNISH = {4, 6, 9, 11}
STEM_COMBINE = {frozenset((0, 5)): "Earth", frozenset((1, 6)): "Metal", frozenset((2, 7)): "Water",
                frozenset((3, 8)): "Wood", frozenset((4, 9)): "Fire"}
STEM_CLASH = {frozenset(p) for p in [(0, 6), (1, 7), (2, 8), (3, 9)]}
PEACH = {frozenset((8, 0, 4)): 9, frozenset((2, 6, 10)): 3, frozenset((11, 3, 7)): 0, frozenset((5, 9, 1)): 6}
TRAVEL = {frozenset((8, 0, 4)): 2, frozenset((2, 6, 10)): 8, frozenset((11, 3, 7)): 5, frozenset((5, 9, 1)): 11}


def gz(i):
    return {"stem": STEMS[i % 10], "branch": BRANCHES[i % 12], "text": STEMS[i % 10] + BRANCHES[i % 12],
            "pinyin": f"{STEM_PY[i % 10]}-{BRANCH_PY[i % 12]}", "animal": ANIMAL[i % 12],
            "stem_element": EL[STEM_EL[i % 10]], "branch_element": EL[BRANCH_EL[i % 12]],
            "polarity": "Yang" if i % 10 % 2 == 0 else "Yin", "index60": i % 60}


def idx60(stem, branch):
    for n in range(60):
        if n % 10 == stem and n % 12 == branch:
            return n
    raise ValueError("invalid stem/branch pair")


def term_jd(year, deg):
    """Exact UT Julian day when the Sun's apparent longitude reaches `deg` within Gregorian `year`."""
    return swe.solcross_ut(float(deg), dt_to_jd(dt.datetime(year, 1, 1)), swe.FLG_SWIEPH)


def day_index(d):
    """Sexagenary day index. Anchor: 2000-01-01 = 戊午 (index 54); also 1949-10-01 = 甲子, 2024-02-10 = 甲辰."""
    return (d.toordinal() - dt.date(2000, 1, 1).toordinal() + 54) % 60


def ten_god(dm, other_stem):
    e, f = STEM_EL[dm], STEM_EL[other_stem]
    same_pol = (dm % 2) == (other_stem % 2)
    rel = (f - e) % 5
    rel_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}  # 0 peer, 1 output, 2 wealth, 3 officer, 4 resource
    return TEN_GODS[(rel_map[rel], 0 if same_pol else 1)]


def hour_branch(hdec):
    return int(((hdec + 1) % 24) // 2)


def branch_relations(labelled):
    """labelled: list of (label, branch). Returns relation records among the branches."""
    out = []
    n = len(labelled)
    for i in range(n):
        for j in range(i + 1, n):
            (la, a), (lb, b) = labelled[i], labelled[j]
            pair = frozenset((a, b))
            for name, table in (("six harmony (六合)", SIX_HARMONY), ("clash (冲)", SIX_CLASH),
                                ("harm (害)", HARM), ("destruction (破)", DESTRUCTION)):
                if a != b and pair in table:
                    out.append({"type": name, "between": [f"{la} {BRANCHES[a]}", f"{lb} {BRANCHES[b]}"]})
            if a == b and a in SELF_PUNISH:
                out.append({"type": "self-punishment (自刑)", "between": [f"{la} {BRANCHES[a]}", f"{lb} {BRANCHES[b]}"]})
            if pair == frozenset((0, 3)):
                out.append({"type": "uncivil punishment (子卯刑)", "between": [f"{la} {BRANCHES[a]}", f"{lb} {BRANCHES[b]}"]})
    bs = {b for _, b in labelled}
    for trio, elem in THREE_HARMONY:
        have = [x for x in trio if x in bs]
        if len(have) == 3:
            out.append({"type": f"three harmony (三合) - {elem}", "between": [BRANCHES[x] for x in trio]})
        elif len(have) == 2:
            out.append({"type": f"half three-harmony - {elem}", "between": [BRANCHES[x] for x in have]})
    for trio, elem in THREE_MEETING:
        if all(x in bs for x in trio):
            out.append({"type": f"three meeting (三会) - {elem}", "between": [BRANCHES[x] for x in trio]})
    for trio, nm in PUNISH_TRIPLE:
        have = [x for x in trio if x in bs]
        if len(have) == 3:
            out.append({"type": f"three-branch {nm} (三刑)", "between": [BRANCHES[x] for x in trio]})
        elif len(have) == 2:
            out.append({"type": f"partial {nm} (two of three)", "between": [BRANCHES[x] for x in have]})
    return out


def stem_relations(labelled):
    out = []
    for i in range(len(labelled)):
        for j in range(i + 1, len(labelled)):
            (la, a), (lb, b) = labelled[i], labelled[j]
            p = frozenset((a, b))
            if p in STEM_COMBINE:
                out.append({"type": f"stem combination (合) -> {STEM_COMBINE[p]}", "between": [f"{la} {STEMS[a]}", f"{lb} {STEMS[b]}"]})
            if p in STEM_CLASH:
                out.append({"type": "stem clash (冲)", "between": [f"{la} {STEMS[a]}", f"{lb} {STEMS[b]}"]})
    return out


def pillars(jd_ut, civil_date, clock_dt, mode="23"):
    """Compute the four pillars. clock_dt is the time basis for day/hour (true solar or standard).
    mode '23': day changes at 23:00 (default). mode '00': late-Zi convention (day unchanged; hour stem from next day)."""
    sun = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
    y = jd_to_dt(jd_ut).year
    li = term_jd(y, 315)
    by = y if jd_ut >= li else y - 1
    ys, yb = (by - 4) % 10, (by - 4) % 12
    m = int(n360(sun - 315) // 30)
    yin_stem = ((ys % 5) * 2 + 2) % 10
    ms, mb = (yin_stem + m) % 10, (2 + m) % 12
    d0 = clock_dt.date()
    hdec = clock_dt.hour + clock_dt.minute / 60 + clock_dt.second / 3600
    late_zi = hdec >= 23
    if mode == "23":
        d_used = d0 + dt.timedelta(days=1) if late_zi else d0
        di = day_index(d_used)
        hb = hour_branch(hdec)
        hs = ((di % 10 % 5) * 2 + hb) % 10
    else:
        di = day_index(d0)
        hb = hour_branch(hdec)
        stem_for_hour = day_index(d0 + dt.timedelta(days=1)) % 10 if late_zi else di % 10
        hs = ((stem_for_hour % 5) * 2 + hb) % 10
    return {"year": idx60(ys, yb), "month": idx60(ms, mb), "day": di, "hour": idx60(hs, hb),
            "bazi_year": by, "month_index": m, "late_zi": late_zi}


def void_branches(i):
    start_b = ((i // 10) * 10) % 12
    return [(start_b + 10) % 12, (start_b + 11) % 12]


def build_bazi(tp, gender, now_utc, tst_default=True, zi_mode="23"):
    """tp: resolve_time() result. gender: 'M' or 'F'."""
    jd = tp["jd_ut"]
    tst_dt, std_dt = tp["_tst_dt"], tp["_std_dt"]
    primary_dt = tst_dt if tst_default else std_dt
    P = pillars(jd, primary_dt.date(), primary_dt, zi_mode)
    P_std = pillars(jd, std_dt.date(), std_dt, zi_mode)
    P_tst = pillars(jd, tst_dt.date(), tst_dt, zi_mode)
    P_alt = pillars(jd, primary_dt.date(), primary_dt, "00" if zi_mode == "23" else "23")
    warnings = []
    for k, lab in (("day", "Day"), ("hour", "Hour")):
        if P_std[k] != P_tst[k]:
            warnings.append(f"{lab} pillar differs between standard time ({gz(P_std[k])['text']}) and true solar time "
                            f"({gz(P_tst[k])['text']}). Confirm which convention the client's tradition uses.")
    if P["late_zi"]:
        warnings.append("Born in the 23:00-24:00 late-Zi hour. Day pillar depends on convention: "
                        f"{gz(P['day'])['text']} (23:00 rollover) vs {gz(P_alt['day'])['text']} (midnight rollover).")
    # boundary distances
    sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
    nxt = JIE_DEG[(P["month_index"] + 1) % 12]
    cur = JIE_DEG[P["month_index"]]
    yr = jd_to_dt(jd).year
    cand_next = [term_jd(yr + k, nxt) for k in (-1, 0, 1)]
    cand_cur = [term_jd(yr + k, cur) for k in (-1, 0, 1)]
    next_jd = min((c for c in cand_next if c > jd), default=None)
    prev_jd = max((c for c in cand_cur if c <= jd), default=None)
    hrs_to_next = (next_jd - jd) * 24 if next_jd else None
    hrs_since = (jd - prev_jd) * 24 if prev_jd else None
    if hrs_to_next is not None and hrs_to_next < 24 or hrs_since is not None and hrs_since < 24:
        warnings.append("Birth is within 24 hours of a solar-term boundary; the Month (and possibly Year) pillar is sensitive to time and place errors.")
    hb_min = ((primary_dt.hour * 60 + primary_dt.minute + 60) % 120)
    if hb_min < 15 or hb_min > 105:
        warnings.append("Birth is within 15 minutes of a two-hour boundary; the Hour pillar is sensitive to a small time error.")
    chars = [("Year", P["year"]), ("Month", P["month"]), ("Day", P["day"]), ("Hour", P["hour"])]
    pill = {k.lower(): {**gz(v), "hidden_stems": [STEMS[h] for h in HIDDEN[v % 12]]} for k, v in chars}
    dm = P["day"] % 10
    for k, v in chars:
        pill[k.lower()]["ten_god_stem"] = "Day Master" if k == "Day" else ten_god(dm, v % 10)
        pill[k.lower()]["ten_god_branch_main"] = ten_god(dm, HIDDEN[v % 12][0])
        pill[k.lower()]["hidden_ten_gods"] = [ten_god(dm, h) for h in HIDDEN[v % 12]]
    # element counts
    raw = {e: 0.0 for e in EL}
    hid = {e: 0.0 for e in EL}
    for _, v in chars:
        raw[EL[STEM_EL[v % 10]]] += 1
        raw[EL[BRANCH_EL[v % 12]]] += 1
        hid[EL[STEM_EL[v % 10]]] += 1
        for w, h in zip((1.0, 0.5, 0.3), HIDDEN[v % 12]):
            hid[EL[STEM_EL[h]]] += w
    # Day Master strength (heuristic)
    m_el = BRANCH_EL[P["month"] % 12]
    dm_el = STEM_EL[dm]
    rel = (dm_el - m_el) % 5
    season = {0: "旺 prosperous", 1: "相 assisting", 4: "休 resting", 3: "囚 confined", 2: "死 dead"}
    # rel = DM element relative to the month's element: 0 same=旺; 1 produced by month=相; 4 produces month=休;
    # 3 controls month=囚; 2 controlled by month=死  (standard 旺相休囚死 table, checked: summer/Fire -> Water 囚, Metal 死)
    status = season[rel] if rel in season else "?"
    sup = drn = 0.0
    for k, v in chars:
        items = []
        if k != "Day":
            items.append((STEM_EL[v % 10], 1.0))
        items.append((STEM_EL[HIDDEN[v % 12][0]], 1.5 if k == "Month" else 1.0))
        for e, wt in items:
            if (e - dm_el) % 5 in (0, 4):   # same element or the element that produces the Day Master
                sup += wt
            else:
                drn += wt
    if status.startswith(("旺", "相")) and sup >= drn:
        verdict = "leans strong"
    elif status.startswith(("囚", "死")) and sup < drn:
        verdict = "leans weak"
    else:
        verdict = "balanced or mixed - needs a full structural judgement (成格/从格 not tested)"
    # Luck pillars
    male = gender.upper().startswith("M")
    yang_year = (P["year"] % 10) % 2 == 0
    forward = (yang_year and male) or (not yang_year and not male)
    cur_i = P["month_index"]
    yrs_near = [term_jd(yr + k, JIE_DEG[(cur_i + 1) % 12]) for k in (-1, 0, 1)]
    yrs_prev = [term_jd(yr + k, JIE_DEG[cur_i]) for k in (-1, 0, 1)]
    if forward:
        target = min(c for c in yrs_near if c > jd)
        days = target - jd
    else:
        target = max(c for c in yrs_prev if c <= jd)
        days = jd - target
    start_age = days / 3.0
    birth_utc = tp["_utc_dt"]
    base = P["month"]
    lp = []
    for k in range(10):
        i = (base + (k + 1) * (1 if forward else -1)) % 60
        a0 = start_age + 10 * k
        lp.append({**gz(i), "start_age": round(a0, 2), "end_age": round(a0 + 10, 2),
                   "from": (birth_utc + dt.timedelta(days=a0 * 365.2425)).date().isoformat(),
                   "to": (birth_utc + dt.timedelta(days=(a0 + 10) * 365.2425)).date().isoformat(),
                   "ten_god_stem": ten_god(dm, i % 10)})
    age_now = (now_utc - birth_utc).days / 365.2425
    cur_lp = next((x for x in lp if x["start_age"] <= age_now < x["end_age"]), None)
    # annual pillars (BaZi year runs Li Chun to Li Chun)
    ny = now_utc.year
    li_now = jd_to_dt(term_jd(ny, 315))
    bazi_now = ny if now_utc >= li_now else ny - 1
    annual = []
    for Y in range(bazi_now - 1, bazi_now + 6):
        i = idx60((Y - 4) % 10, (Y - 4) % 12)
        annual.append({"year": Y, **gz(i), "ten_god_stem": ten_god(dm, i % 10)})
    natal_b = [(k, v % 12) for k, v in chars]
    natal_s = [(k, v % 10) for k, v in chars]
    interactions = {"natal_branches": branch_relations(natal_b), "natal_stems": stem_relations(natal_s)}
    if cur_lp:
        li_ = idx60(STEMS.index(cur_lp["stem"]), BRANCHES.index(cur_lp["branch"]))
        interactions["luck_pillar_vs_natal"] = [r for r in branch_relations(natal_b + [("LuckPillar", li_ % 12)])
                                                if any("LuckPillar" in b for b in r["between"])]
    cur_annual = next(a for a in annual if a["year"] == bazi_now)
    ai = idx60(STEMS.index(cur_annual["stem"]), BRANCHES.index(cur_annual["branch"]))
    interactions["annual_pillar_vs_natal"] = [r for r in branch_relations(natal_b + [("Annual", ai % 12)])
                                              if any("Annual" in b for b in r["between"])]
    vd = void_branches(P["day"])
    vy = void_branches(P["year"])
    yr_b, day_b = P["year"] % 12, P["day"] % 12

    def key_of(b):
        return next((k for k in PEACH if b in k), None)
    shen = {"void_branches_day_xun": [BRANCHES[x] for x in vd],
            "void_present_in_chart": [f"{k} {BRANCHES[v % 12]}" for k, v in chars if v % 12 in vd and k != "Day"],
            "void_branches_year_xun": [BRANCHES[x] for x in vy],
            "peach_blossom": sorted({BRANCHES[PEACH[key_of(b)]] for b in (yr_b, day_b) if key_of(b)}),
            "travelling_horse": sorted({BRANCHES[TRAVEL[key_of(b)]] for b in (yr_b, day_b) if key_of(b)}),
            "note": "Subset of Shen Sha with stable definitions. Nobleman stars vary by school and are not computed."}
    out = {
        "basis": {"primary_time_basis": "true solar time" if tst_default else "standard time",
                  "true_solar_time": tp["true_solar_time"], "standard_time": tp["local_standard_time"],
                  "equation_of_time_min": tp["equation_of_time_min"], "zi_hour_convention": f"day rolls at {'23:00' if zi_mode == '23' else '00:00'}",
                  "year_boundary": "Li Chun (Sun at 315 degrees), astronomical instant",
                  "month_boundary": "Jie solar terms, astronomical instant"},
        "pillars": pill, "day_master": {"stem": STEMS[dm], "element": EL[dm_el], "polarity": "Yang" if dm % 2 == 0 else "Yin"},
        "day_master_strength_heuristic": {"month_season_status": status, "supporters": round(sup, 1), "drainers": round(drn, 1),
                                          "verdict": verdict,
                                          "note": "Heuristic screen (season + weighted support/drain). Special structures and Useful God selection are for the reader."},
        "element_balance_visible_8": {k: int(v) for k, v in raw.items()},
        "element_balance_with_hidden_stems": {k: round(v, 1) for k, v in hid.items()},
        "missing_elements_visible": [k for k, v in raw.items() if v == 0],
        "luck_pillars": {"direction": "forward" if forward else "backward", "start_age_years": round(start_age, 2),
                         "start_age_readable": f"{int(start_age)}y {int((start_age % 1) * 12)}m", "pillars": lp,
                         "current": cur_lp, "rule": "3 days = 1 year from birth to the nearest Jie in the direction of travel"},
        "annual_pillars": annual, "current_annual_year": bazi_now,
        "interactions": interactions, "shen_sha_subset": shen,
        "alternatives": {"pillars_standard_time": {k: gz(P_std[k])["text"] for k in ("year", "month", "day", "hour")},
                         "pillars_true_solar_time": {k: gz(P_tst[k])["text"] for k in ("year", "month", "day", "hour")},
                         "pillars_other_zi_convention": {k: gz(P_alt[k])["text"] for k in ("year", "month", "day", "hour")}},
        "boundaries": {"hours_since_last_jie": None if hrs_since is None else round(hrs_since, 2),
                       "hours_until_next_jie": None if hrs_to_next is None else round(hrs_to_next, 2),
                       "current_month_term": JIE_NAMES[P["month_index"]]},
        "warnings": warnings,
        "_dm": dm, "_branches": natal_b, "_stems": natal_s,
    }
    out["cross_check"] = cross_check(tp, out, gender, zi_mode)
    return out


def cross_check(tp, bz, gender, zi_mode="23"):
    """Independent second implementation (lunar-python) for the same pillars."""
    try:
        from lunar_python import Solar
    except Exception:
        return {"status": "skipped", "reason": "lunar-python not installed"}
    try:
        bj = tp["_utc_dt"] + dt.timedelta(hours=8)
        ec1 = Solar.fromYmdHms(bj.year, bj.month, bj.day, bj.hour, bj.minute, bj.second).getLunar().getEightChar()
        basis = tp["_tst_dt"] if bz["basis"]["primary_time_basis"] == "true solar time" else tp["_std_dt"]
        ec2 = Solar.fromYmdHms(basis.year, basis.month, basis.day, basis.hour, basis.minute, basis.second).getLunar().getEightChar()
        ec2.setSect(1 if zi_mode == "23" else 2)   # 1: late-Zi day rolls at 23:00; 2: day unchanged
        theirs = {"year": ec1.getYear(), "month": ec1.getMonth(), "day": ec2.getDay(), "hour": ec2.getTime()}
        mine = {k: bz["pillars"][k]["text"] for k in ("year", "month", "day", "hour")}
        diff = {k: {"engine": mine[k], "lunar_python": theirs[k]} for k in mine if mine[k] != theirs[k]}
        yun = ec1.getYun(1 if gender.upper().startswith("M") else 0)
        dir_ok = yun.isForward() == (bz["luck_pillars"]["direction"] == "forward")
        their_start = yun.getStartYear() + yun.getStartMonth() / 12 + yun.getStartDay() / 365.25
        return {"status": "match" if not diff and dir_ok and abs(their_start - bz["luck_pillars"]["start_age_years"]) < 0.1 else "MISMATCH", "pillar_differences": diff,
                "luck_direction_agrees": dir_ok,
                "luck_start_age_engine": bz["luck_pillars"]["start_age_years"],
                "luck_start_age_lunar_python": round(their_start, 2),
                "note": "Year/Month compared at the Beijing-time equivalent of the birth instant; Day/Hour compared on the chosen local time basis."}
    except Exception as e:  # never let the check break the chart
        return {"status": "error", "reason": repr(e)[:200]}


def bazi_cross(a, b):
    """Two-person BaZi comparison from two build_bazi() outputs."""
    out = {"branch_relations": [], "stem_relations": [], "day_master_relationship": {}}
    A = [(f"A-{k}", v) for k, v in a["_branches"]]
    B = [(f"B-{k}", v) for k, v in b["_branches"]]
    for r in branch_relations(A + B):
        if any(x.startswith("A-") for x in r["between"]) and any(x.startswith("B-") for x in r["between"]):
            out["branch_relations"].append(r)
    for r in stem_relations([(f"A-{k}", v) for k, v in a["_stems"]] + [(f"B-{k}", v) for k, v in b["_stems"]]):
        if any(x.startswith("A-") for x in r["between"]) and any(x.startswith("B-") for x in r["between"]):
            out["stem_relations"].append(r)
    out["day_master_relationship"] = {
        "B_day_master_is_to_A": ten_god(a["_dm"], b["_dm"]),
        "A_day_master_is_to_B": ten_god(b["_dm"], a["_dm"])}
    ya = dict(a["_branches"])["Year"]
    yb = dict(b["_branches"])["Year"]
    out["year_animals"] = {"A": ANIMAL[ya], "B": ANIMAL[yb]}
    da, db = dict(a["_branches"])["Day"], dict(b["_branches"])["Day"]
    out["spouse_palace_pair"] = {"A_day_branch": BRANCHES[da], "B_day_branch": BRANCHES[db],
                                 "relation": [r["type"] for r in branch_relations([("A", da), ("B", db)])]}
    return out


def build_zwds(tp, gender):
    """Zi Wei Dou Shu via the py-iztro library (third-party implementation, not re-derived here).
    Returns Chinese names with the library's English rendering alongside."""
    try:
        from py_iztro import Astro
    except Exception:
        return {"status": "skipped", "reason": "py-iztro not installed (pip install py-iztro)"}
    try:
        std = tp["_std_dt"]
        h = std.hour + std.minute / 60
        idx = 0 if h < 1 else (12 if h >= 23 else 1 + int((h - 1) // 2))
        g = "男" if gender.upper().startswith("M") else "女"
        ds = f"{std.year}-{std.month}-{std.day}"
        zh = Astro().by_solar(ds, idx, g, language="zh-CN")
        en = Astro().by_solar(ds, idx, g, language="en-US")
        palaces = []
        for pz, pe in zip(zh.palaces, en.palaces):
            palaces.append({
                "palace": f"{pz.name} / {pe.name}", "stem_branch": f"{pz.heavenly_stem}{pz.earthly_branch}",
                "is_body_palace": pz.is_body_palace,
                "major_stars": [{"star": f"{a.name} / {b.name}", "brightness": a.brightness or None,
                                 "birth_year_transformation": a.mutagen or None}
                                for a, b in zip(pz.major_stars, pe.major_stars)],
                "minor_stars": [a.name for a in pz.minor_stars],
                "decadal_ages": list(pz.decadal.range) if pz.decadal else None})
        edge = ((h + 1) % 2 < 0.25) or ((h + 1) % 2 > 1.75)
        return {"status": "ok",
                "summary": {"lunar_date": zh.lunar_date, "chinese_date": zh.chinese_date, "hour": f"{zh.time} {zh.time_range}",
                            "five_elements_class": zh.five_elements_class,
                            "life_palace_branch": zh.earthly_branch_of_soul_palace,
                            "body_palace_branch": zh.earthly_branch_of_body_palace,
                            "soul_star": zh.soul, "body_star": zh.body},
                "palaces": palaces,
                "time_basis": f"standard clock time (DST removed); shichen index {idx}",
                "warnings": (["Zi Wei Dou Shu is sensitive to the shichen (two-hour) boundary; confirm the birth hour."] if edge else []),
                "not_computed": "Annual/monthly flowing stars and Zi Wei interpretation are left to the reader."}
    except Exception as e:
        return {"status": "error", "reason": repr(e)[:300]}
