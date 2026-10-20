"""name_correction.py - score spelling variants of a name by Chaldean compound and Mulank fit.

Name correction is a traditional Indian numerology practice: the spelling (not the sound) of a name is adjusted
so its Chaldean total falls on a compound number the tradition reads well, and its root agrees with the birth
numbers. This module only does the arithmetic and ranks the options. It makes no claim that a spelling change
alters anything in a person's life, and the report must not make one either.

Variants keep the name's sound: doubled letters, a/aa, i/ee, u/oo, v/w, f/ph, k/c/ck, a final y/i/ee/ey, a silent
final h after t or d, and a final schwa a (Ram/Rama). By default only the first name is changed; the surname is
kept. Ranking is lexicographic and stated, not a hidden weighted score:
  1. compound class (favourable > neutral > mixed > difficult),
  2. fit of the name root with the Mulank (same > friend > neutral > enemy),
  3. fit with the Bhagyank, 4. fewer edits.

Usage:
  python scripts/name_correction.py --name "Asha Verma" --dob 1990-04-12 [--gender F] [--change first|full] [--top 10] --out names.json
"""
import argparse
import itertools
import json
import re

from numerology import CHALDEAN, PYTH, clean_name, reduce

# Cheiro, Book of Numbers (1926), compound numbers 10-52 as commonly summarised. Practitioners differ; edit here.
COMPOUND = {
    10: ("favourable", "Wheel of Fortune: honour, faith, plans carried out"),
    11: ("mixed", "warning of hidden obstacles and trials; a master number in Pythagorean practice"),
    12: ("difficult", "sacrifice: being used for others' plans"),
    13: ("mixed", "change and upheaval; not unlucky in itself but asks for care"),
    14: ("mixed", "movement and trade, with risk from rash moves"),
    15: ("favourable", "magnetism and gifts from others"),
    16: ("difficult", "the Shattered Citadel: sudden reversals"),
    17: ("favourable", "the Star of the Magi: peace and lasting reputation"),
    18: ("difficult", "materialism, quarrels and deception"),
    19: ("favourable", "the Prince of Heaven: success and esteem"),
    20: ("favourable", "the Awakening: new purpose and resolve"),
    21: ("favourable", "the Crown of the Magi: advancement after effort"),
    22: ("mixed", "illusion: good intentions misled; a master number in Pythagorean practice"),
    23: ("favourable", "the Royal Star of the Lion: help from superiors, success"),
    24: ("favourable", "favour, love and money through association"),
    25: ("favourable", "strength gained through experience"),
    26: ("difficult", "warnings about partnerships and advice from others"),
    27: ("favourable", "the Sceptre: authority and creative work"),
    28: ("difficult", "promise followed by loss through trust in others"),
    29: ("difficult", "uncertainty, treachery and unexpected dangers"),
    30: ("neutral", "thoughtful deduction; strong or weak as the person wills"),
    31: ("neutral", "self-contained and solitary; better for inner than worldly aims"),
    32: ("favourable", "communication and influence over others"),
    33: ("favourable", "as 24: favour and support"),
    34: ("favourable", "as 25: strength through experience"),
    35: ("difficult", "as 26: warnings about partners"),
    36: ("favourable", "as 27: authority"),
    37: ("favourable", "good friendships and partnerships"),
    38: ("difficult", "as 29: uncertainty"),
    39: ("neutral", "as 30"),
    40: ("neutral", "as 31"),
    41: ("favourable", "as 32: influence"),
    42: ("favourable", "as 24"),
    43: ("difficult", "revolution and upheaval"),
    44: ("difficult", "as 26"),
    45: ("favourable", "as 27"),
    46: ("favourable", "as 37"),
    47: ("difficult", "as 29"),
    48: ("neutral", "as 30"),
    49: ("neutral", "as 31"),
    50: ("favourable", "as 32"),
    51: ("favourable", "the Warrior: sudden advancement, with enemies to watch"),
    52: ("difficult", "as 43"),
}
CLASS_RANK = {"favourable": 3, "neutral": 2, "mixed": 1, "difficult": 0, "root only": 1}

# Ruling planets of the roots, and Parashari natural friendship (Rahu treated as Saturn, Ketu as Mars:
# "Shanivat Rahu, Kujavat Ketu").
ROOT_PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
_PROXY = {"Rahu": "Saturn", "Ketu": "Mars"}
FRIENDS = {"Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"},
           "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
           "Saturn": {"Mercury", "Venus"}}
ENEMIES = {"Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"},
           "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"}}
FIT_RANK = {"same": 3, "friend": 2, "neutral": 1, "enemy": 0}


def relation(from_root, to_root):
    """How the planet of to_root stands from the planet of from_root."""
    if from_root == to_root:
        return "same"
    a, b = (_PROXY.get(ROOT_PLANET[r], ROOT_PLANET[r]) for r in (from_root, to_root))
    if a == b:
        return "friend"  # e.g. Saturn (8) and Rahu (4): same proxy planet
    return "friend" if b in FRIENDS[a] else "enemy" if b in ENEMIES[a] else "neutral"


def compound_class(total):
    if total < 10:
        return "root only", "single digit; read by the root alone"
    if total in COMPOUND:
        return COMPOUND[total]
    return "root only", "beyond 52 Cheiro gives no compound reading; the root is used"


def word_variants(w, schwa=True):
    """Sound-preserving single edits of one upper-case word: list of (new_word, description).

    The final-a (schwa) edits suit names like Ram/Rama; they are switched off for women's names, where a final a
    is a long vowel (Asha, Sita), and they count as two edits because the change is easy to see."""
    out = []
    n = len(w)
    vow = "AEIOU"
    for i, c in enumerate(w):
        # double a consonant (not at the start), or undo a double
        # double a consonant that follows a vowel and is not the start of a digraph (sh, th, ch, ...)
        if (c not in vow and c not in "HWYXQJ" and i > 0 and w[i - 1] in vow
                and (i + 1 >= n or w[i + 1] in vow)):
            out.append((w[:i + 1] + c + w[i + 1:], f"double {c}"))
        if i + 1 < n and w[i + 1] == c:
            out.append((w[:i] + w[i + 1:], f"single {c}"))
    pairs = [("AA", "A"), ("EE", "I"), ("OO", "U"), ("W", "V"), ("PH", "F"), ("CK", "K")]
    for a, b in pairs:
        for x, y in ((a, b), (b, a)):
            for m in re.finditer(re.escape(x), w):
                j = m.start()
                if x == "A" and (w[j:j + 2] == "AA" or (j and w[j - 1] == "A")):
                    continue
                if x == "I" and (w[j:j + 2] in ("IE", "IA") and j == 0):
                    continue
                if x == "U" and j and w[j - 1] in "AO":  # keep AU, OU diphthongs
                    continue
                if x == "K" and j and w[j - 1] == "C":  # already ck
                    continue
                if x in ("F", "V") and j and w[j - 1] in "PW":
                    continue
                out.append((w[:j] + y + w[j + len(x):], f"{x.lower()} to {y.lower()}"))
    for m in re.finditer("K(?=[AOU])", w):
        out.append((w[:m.start()] + "C" + w[m.start() + 1:], "k to c"))
    for m in re.finditer("C(?=[AOU])", w):
        out.append((w[:m.start()] + "K" + w[m.start() + 1:], "c to k"))
    for end in ("Y", "I", "EE", "EY"):
        if w.endswith(end) and n > len(end) + 1:
            for alt in ("Y", "I", "EE", "EY"):
                if alt != end:
                    out.append((w[:-len(end)] + alt, f"final {end.lower()} to {alt.lower()}"))
    if w[-1] in "TD":
        out.append((w + "H", f"silent h after final {w[-1].lower()}"))
    if w.endswith(("TH", "DH")) and n > 3:
        out.append((w[:-1], "drop silent final h"))
    if schwa and w[-1] not in vow and n > 2:
        out.append((w + "A", "final a (schwa)"))
    if schwa and w.endswith("A") and not w.endswith("AA") and n > 3 and w[-2] not in vow:
        out.append((w[:-1], "drop final a (schwa)"))
    seen, res = set(), []
    for v, d in out:
        if v != w and v not in seen:
            seen.add(v)
            res.append((v, d))
    return res


def _direction(desc):
    """+1 for an edit that adds a letter, -1 for one that removes a letter, 0 otherwise."""
    if desc.startswith(("double", "silent h", "final a (")):
        return 1
    if desc.startswith(("single", "drop")):
        return -1
    m = re.match(r"(?:final )?([a-z]+) to ([a-z]+)$", desc)
    if m:
        d = len(m.group(2)) - len(m.group(1))
        return (d > 0) - (d < 0)
    return 0


def _score(full, mulank, bhagyank):
    letters = [c for c in full if c != " "]
    total = sum(CHALDEAN[c] for c in letters)
    root = reduce(total, False)[0]
    cls, meaning = compound_class(total)
    pt = sum(PYTH[c] for c in letters)
    return {"chaldean_compound": total, "chaldean_root": root, "compound_class": cls, "compound_reading": meaning,
            "fit_with_mulank": relation(mulank, root), "fit_with_bhagyank": relation(bhagyank, root),
            "root_planet": ROOT_PLANET[root], "pythagorean_expression": reduce(pt)[0]}


def _key(s, edits):
    return (CLASS_RANK[s["compound_class"]], FIT_RANK[s["fit_with_mulank"]], FIT_RANK[s["fit_with_bhagyank"]], -edits)


def suggest(name, dob, change="first", top=10, max_edits=2, gender=None):
    y, m, d = (int(v) for v in dob.split("-"))
    mulank = reduce(d, False)[0]
    bhagyank = reduce(sum(int(c) for c in f"{y:04d}{m:02d}{d:02d}"), False)[0]
    words = clean_name(name).split()
    if not words:
        raise ValueError("name has no letters")
    idx = [0] if change == "first" else list(range(len(words)))
    orig = _score(" ".join(words), mulank, bhagyank)
    found = {}
    frontier = [(tuple(words), ())]
    for depth in range(max_edits):
        nxt = []
        for ws, descs in frontier:
            for i in idx:
                for nw, dsc in word_variants(ws[i], schwa=(str(gender or "").upper()[:1] != "F")):
                    if descs and _direction(dsc) and any(_direction(x) == -_direction(dsc) for x in descs):
                        continue  # lengthening then shortening (Ravi -> Ravee -> Rave) changes the sound
                    cand = ws[:i] + (nw,) + ws[i + 1:]
                    if cand == tuple(words) or cand in found:
                        continue
                    ds = descs + (dsc,)
                    found[cand] = ds
                    nxt.append((cand, ds))
        frontier = nxt
    rows = []
    for ws, ds in found.items():
        s = _score(" ".join(ws), mulank, bhagyank)
        s.update({"spelling": " ".join(w.capitalize() for w in ws), "changes": list(ds),
                  "edits": len(ds) + sum("schwa" in x for x in ds)})
        rows.append(s)
    rows.sort(key=lambda s: _key(s, s["edits"]), reverse=True)
    best, seen = [], {orig["chaldean_compound"]}
    for r in rows:  # one row per compound number (and none on the original's), so the list shows real choices
        if r["chaldean_compound"] in seen:
            continue
        seen.add(r["chaldean_compound"])
        best.append(r)
        if len(best) >= top:
            break
    orig_ok = orig["compound_class"] == "favourable" and orig["fit_with_mulank"] in ("same", "friend")
    better = [r for r in best if _key(r, 0) > _key(orig, 0)]
    return {
        "name": " ".join(w.capitalize() for w in words), "dob": dob, "mulank": mulank, "bhagyank": bhagyank,
        "mulank_planet": ROOT_PLANET[mulank], "bhagyank_planet": ROOT_PLANET[bhagyank],
        "changed_part": "first name only" if change == "first" else "whole name",
        "original": orig, "original_already_fits": orig_ok,
        "variants_considered": len(rows), "suggestions": best, "suggestions_better_than_original": len(better),
        "ranking": "compound class, then root fit with Mulank, then with Bhagyank, then fewer edits",
        "conventions": "Chaldean letter values (no 9). Compound readings follow Cheiro (1926) as commonly summarised for 10-52; "
                       "root friendship uses Parashari natural friendship of the ruling planets, with Rahu treated as Saturn and "
                       "Ketu as Mars. Only sound-preserving spelling changes are generated.",
        "disclaimer": "Name correction is a traditional practice. Its effect has not been shown, and no spelling is promised to "
                      "change events. Choose a spelling only if you would be happy to use it every day, on documents as well "
                      "as in conversation; changing legal documents is a separate decision with its own costs.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--dob", required=True, help="YYYY-MM-DD")
    ap.add_argument("--change", default="first", choices=["first", "full"])
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--gender", default=None, help="F switches off the final-a edits")
    ap.add_argument("--out", default="names.json")
    a = ap.parse_args()
    r = suggest(a.name, a.dob, a.change, a.top, gender=a.gender)
    json.dump(r, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    o = r["original"]
    print(f"{r['name']}: compound {o['chaldean_compound']} ({o['compound_class']}), root {o['chaldean_root']} "
          f"{o['fit_with_mulank']} with Mulank {r['mulank']}; {r['suggestions_better_than_original']} better-ranked spellings shown")
    for s in r["suggestions"][:5]:
        print(f"  {s['spelling']:<24} {s['chaldean_compound']:>3} {s['compound_class']:<10} mulank:{s['fit_with_mulank']:<8} {', '.join(s['changes'])}")


if __name__ == "__main__":
    main()
