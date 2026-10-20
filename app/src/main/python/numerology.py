"""numerology.py - three numerology conventions, stated separately (they do not agree by design).

Pythagorean (Western), Chaldean (name vibration) and the Indian Mulank/Bhagyank/Loshu grid.
Arithmetic only; meanings are left to the reader.
"""
import datetime as dt
import re
import unicodedata

PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CHALDEAN = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 8, "G": 3, "H": 5, "I": 1, "J": 1, "K": 2, "L": 3,
            "M": 4, "N": 5, "O": 7, "P": 8, "Q": 1, "R": 2, "S": 3, "T": 4, "U": 6, "V": 6, "W": 6,
            "X": 5, "Y": 1, "Z": 7}
MASTER = (11, 22, 33)
LOSHU_LAYOUT = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
PLANES = {"mental (4-9-2)": (4, 9, 2), "emotional (3-5-7)": (3, 5, 7), "practical (8-1-6)": (8, 1, 6),
          "thought (4-3-8)": (4, 3, 8), "will (9-5-1)": (9, 5, 1), "action (2-7-6)": (2, 7, 6),
          "golden diagonal (4-5-6)": (4, 5, 6), "silver diagonal (2-5-8)": (2, 5, 8)}
LOSHU_PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
KARMIC_DEBT = (13, 14, 16, 19)
# Eight Mansions directions by Kua: Sheng Qi, Tian Yi, Yan Nian, Fu Wei (good); Huo Hai, Wu Gui, Liu Sha, Jue Ming (bad)
KUA_DIRS = {1: ["SE", "E", "S", "N", "W", "NE", "NW", "SW"], 2: ["NE", "W", "NW", "SW", "E", "SE", "S", "N"],
            3: ["S", "N", "SE", "E", "SW", "NW", "NE", "W"], 4: ["N", "S", "E", "SE", "NW", "SW", "W", "NE"],
            6: ["W", "NE", "SW", "NW", "SE", "E", "N", "S"], 7: ["NW", "SW", "NE", "W", "N", "S", "SE", "E"],
            8: ["SW", "NW", "W", "NE", "S", "N", "E", "SE"], 9: ["E", "SE", "N", "S", "NE", "W", "SW", "NW"]}
KUA_NAMES = ["Sheng Qi (growth)", "Tian Yi (health)", "Yan Nian (relationships)", "Fu Wei (stability)",
             "Huo Hai (mishaps)", "Wu Gui (quarrels)", "Liu Sha (setbacks)", "Jue Ming (severe loss)"]


def digit_sum(n):
    return sum(int(c) for c in str(abs(int(n))))


def reduce(n, keep_master=True):
    steps = [n]
    while n > 9 and not (keep_master and n in MASTER):
        n = digit_sum(n)
        steps.append(n)
    return n, steps


def clean_name(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z ]", "", s).upper()


def name_numbers(name, table):
    letters = [c for c in clean_name(name) if c != " "]
    total = sum(table[c] for c in letters)
    return total, reduce(total)[0]


def vowel_split(name):
    """Y counts as a vowel only when the word has no other vowel (common rule); reported so it can be reviewed."""
    vowels, cons, y_notes = [], [], []
    for word in clean_name(name).split():
        has_v = any(c in "AEIOU" for c in word)
        for i, c in enumerate(word):
            if c in "AEIOU":
                vowels.append(c)
            elif c == "Y" and not has_v:
                vowels.append(c)
                y_notes.append(f"Y treated as a vowel in '{word}'")
            else:
                cons.append(c)
    return vowels, cons, y_notes


def build_numerology(name, dob, now, name_in_use=None, gender=None, birth_jd_ut=None):
    y, m, d = [int(v) for v in dob.split("-")]
    warnings = []
    # Life path (component method, master numbers kept) and the total-digit method for comparison
    ry, _ = reduce(y)
    rm, _ = reduce(m)
    rd, _ = reduce(d)
    lp, lp_steps = reduce(ry + rm + rd)
    lp_alt, _ = reduce(digit_sum(y) + digit_sum(m) + digit_sum(d))
    if lp != lp_alt:
        warnings.append(f"Life Path differs by method: component method {lp}, total-digit method {lp_alt}. State which is used.")
    out = {"life_path": {"value": lp, "method": "month, day, year each reduced (master numbers kept), then summed",
                         "alternate_method_value": lp_alt},
           "birthday_number": {"value": d if d in MASTER else reduce(d)[0], "raw_day": d}}
    # Pythagorean
    tp_, dest = name_numbers(name, PYTH)
    vs, cs, ynotes = vowel_split(name)
    soul = reduce(sum(PYTH[c] for c in vs))[0]
    pers = reduce(sum(PYTH[c] for c in cs))[0]
    out["pythagorean"] = {"name_used": name, "destiny_expression": dest, "destiny_raw_total": tp_,
                          "soul_urge": soul, "personality": pers, "notes": ynotes}
    # Personal cycles
    py, _ = reduce(rd + rm + reduce(now.year)[0])
    pm, _ = reduce(py + now.month)
    out["personal_cycles"] = {"as_of": now.date().isoformat(), "personal_year": py, "personal_month": pm,
                              "base_digit": py if py <= 9 else reduce(py, False)[0]}
    # Chaldean
    ch_total, ch_red = name_numbers(name, CHALDEAN)
    out["chaldean"] = {"name_used": name, "compound_number": ch_total, "single_digit": ch_red,
                       "note": "Chaldean reads the compound number (e.g. 23/5) as well as the root; letters are not mapped 1-9 in order."}
    if name_in_use and clean_name(name_in_use) != clean_name(name):
        u_total, u_red = name_numbers(name_in_use, CHALDEAN)
        pu_total, pu_dest = name_numbers(name_in_use, PYTH)
        out["name_in_use"] = {"name": name_in_use, "pythagorean_destiny": pu_dest, "chaldean_compound": u_total,
                              "chaldean_single": u_red,
                              "shift_from_birth_name": {"pythagorean": f"{dest} -> {pu_dest}", "chaldean": f"{ch_red} -> {u_red}"}}
    # Indian
    mulank = reduce(d, False)[0]
    bhagyank = reduce(digit_sum(y) + digit_sum(m) + digit_sum(d), False)[0]
    digits = [int(c) for c in f"{d:02d}{m:02d}{y}" if c != "0"]
    counts = {n: digits.count(n) for n in range(1, 10)}
    with_extra = dict(counts)
    with_extra[mulank] += 1
    with_extra[bhagyank] += 1
    present = [n for n in range(1, 10) if with_extra[n] > 0]
    missing = [n for n in range(1, 10) if with_extra[n] == 0]
    plane_status = {}
    for nm, trio in PLANES.items():
        have = [n for n in trio if with_extra[n] > 0]
        plane_status[nm] = "complete" if len(have) == 3 else ("empty" if not have else f"partial ({len(have)}/3)")
    grid = [[(str(n) * with_extra[n]) if with_extra[n] else "-" for n in row] for row in LOSHU_LAYOUT]
    indian = {"mulank_driver": mulank, "bhagyank_conductor": bhagyank,
              "mulank_planet": LOSHU_PLANET[mulank], "bhagyank_planet": LOSHU_PLANET[bhagyank],
              "loshu_grid": grid, "digit_counts_including_mulank_bhagyank": with_extra,
              "missing_numbers": missing, "missing_planets": [LOSHU_PLANET[n] for n in missing],
              "repeated_numbers": {n: c for n, c in with_extra.items() if c >= 3},
              "planes": plane_status,
              "conventions": "Grid built from DD MM YYYY digits (zeros ignored) plus Mulank and Bhagyank, as in common Indian practice. "
                             "Some teachers omit the century digits or add a Kua number; state the choice."}
    if mulank == bhagyank:
        indian["note"] = "Mulank equals Bhagyank."
    out["indian"] = indian
    # ---- karmic debt, karmic lessons, hidden passion, maturity (Pythagorean)
    letters = [c for c in clean_name(name) if c != " "]
    lcount = {n: sum(1 for c in letters if PYTH[c] == n) for n in range(1, 10)}
    debts = {}
    chains = {"life_path": reduce(ry + rm + rd)[1], "destiny": reduce(tp_)[1],
              "soul_urge": reduce(sum(PYTH[c] for c in vs))[1], "personality": reduce(sum(PYTH[c] for c in cs))[1],
              "birthday": [d]}
    for k, ch in chains.items():
        hit = [x for x in ch if x in KARMIC_DEBT]
        if hit:
            debts[k] = hit[0]
    top = max(lcount.values()) if letters else 0
    mat = reduce(lp + dest)
    out["pythagorean"].update({
        "karmic_debt": debts,
        "karmic_lessons": [n for n in range(1, 10) if lcount[n] == 0],
        "hidden_passion": [n for n in range(1, 10) if lcount[n] == top and top > 0],
        "letter_counts": lcount,
        "maturity_number": mat[0],
        "extras_conventions": "Karmic debt = 13, 14, 16 or 19 appearing in a number's reduction chain (or as the birth day). "
                              "Karmic lessons = digits 1-9 with no letter in the full birth name. Hidden passion = the most frequent digit. "
                              "Maturity = Life Path + Destiny, reduced (masters kept)."})
    # ---- Kua number (Eight Mansions), with the Chinese solar year (Li Chun)
    if gender in ("M", "F"):
        kyear, note = y, "calendar year (birth time not given)"
        if birth_jd_ut is not None:
            try:
                import swisseph as swe
                lc = swe.solcross_ut(315.0, swe.julday(y, 1, 20, 0.0), swe.FLG_SWIEPH)
                if birth_jd_ut < lc:
                    kyear = y - 1
                yy, mm, dd, hh = swe.revjul(lc)
                note = f"Chinese solar year: Li Chun {yy:04d}-{mm:02d}-{dd:02d} {int(hh):02d}:{int(hh % 1 * 60):02d} UT"
                note += "; born before it, so the previous year is used" if kyear != y else "; born after it"
            except Exception as e:  # pragma: no cover
                note = f"calendar year used (Li Chun not computed: {e})"
        r = reduce(digit_sum(kyear), False)[0]
        kua = reduce(11 - r if gender == "M" else 4 + r, False)[0] if (11 - r if gender == "M" else 4 + r) > 0 else 9
        if kua == 5:
            kua = 2 if gender == "M" else 8
        dirs = KUA_DIRS[kua]
        out["kua"] = {"value": kua, "year_used": kyear, "year_basis": note, "gender": gender,
                      "group": "East" if kua in (1, 3, 4, 9) else "West",
                      "favourable": {KUA_NAMES[i]: dirs[i] for i in range(4)},
                      "unfavourable": {KUA_NAMES[i]: dirs[i] for i in range(4, 8)},
                      "conventions": "Eight Mansions: male 11 minus the reduced year, female 4 plus it, reduced; 5 becomes 2 (male) or 8 (female)."}
    out["warnings"] = warnings
    return out
