"""yoga_library.py - evaluates the data-driven yoga rules in yoga_rules.py against a computed chart.

Each rule is data: a condition written in a small expression language, optional cancellations, the
planets that carry the yoga, a source, and a flag saying whether the yoga may be reported at all.
The interpreter below knows the primitives; adding a yoga means adding an entry to yoga_rules.py.

Conventions (also returned in the output):
* Rasi chart, whole-sign houses from the Lagna. "Planets" in Nabhasa yogas means the seven grahas Sun..Saturn.
* Graha drishti by sign: every graha aspects the 7th; Mars also the 4th and 8th, Jupiter the 5th and 9th,
  Saturn the 3rd and 10th; Rahu and Ketu the 5th, 7th and 9th (school-dependent, as in the engine).
* Natural benefics: Jupiter, Venus, Mercury unless it shares a sign with a malefic, and the Moon in Shukla paksha.
  Natural malefics: Sun, Mars, Saturn, Rahu, Ketu, the Moon in Krishna paksha, Mercury with a malefic.
* "Strong" = Shadbala ratio of at least 1 (BPHS minimum) and not debilitated or combust.
* Strength grade (heuristic, stated as such): mean Shadbala ratio of the planets that carry the yoga, adjusted
  for debility, combustion, a 6/8/12 placement, and navamsa dignity. Grades: strong >= 1.2, moderate >= 0.9.

Expression language (lists, first item is the operator):
  ["and", e, ...] ["or", e, ...] ["not", e]
  ["in_house", P, [houses], REF]      P in one of these houses counted from REF (default Lagna)
  ["in_sign", P, [sign indexes]]      ["sign_type", P, "movable|fixed|dual|odd|even|watery|dry"]
  ["dignity", P, [names]]             names: exalted, debilitated, moolatrikona, own, friend, enemy, neutral
  ["strong_sign", P]                  exalted, moolatrikona or own sign
  ["deep_exalt", P, deg]              exalted and within deg of the exact exaltation degree
  ["nav_dignity", P, [names]]         same names, in the navamsa
  ["conj", P, Q] ["aspects", P, Q] ["assoc", P, Q] ["exchange", P, Q]
  ["mutual_kendra", P, Q] ["mutual_trine", P, Q] ["rel_house", P, Q, [houses]]  (Q counted from P)
  ["occupied", [houses], WHO, REF]    every listed house holds at least one planet of class WHO
  ["any_in", [houses], WHO, REF]      at least one planet of class WHO in any listed house
  ["only", [houses], WHO, REF]        the listed houses hold at least one planet, and all of them are WHO
  ["none_in", [houses], WHO, REF]     no planet of class WHO in the listed houses
  ["all_in", [houses], WHO, REF]      every planet of class WHO is in the listed houses
  ["seven_exact", [houses], REF]      the seven grahas fill exactly these houses (each occupied, none outside)
  ["seven_signtype", "movable|fixed|dual"]   ["seven_distinct", n]
  ["seven_run", start_houses, length] the seven fill a run of `length` consecutive houses starting at one of start_houses
  ["strong", P] ["combust", P] ["retro", P] ["waxing"] ["day_birth"] ["male"] ["female"]
  ["assoc_with_kind", P, WHO]         P conjoined with or aspected by a planet of class WHO
  ["count_in", [houses], WHO, REF, op, n]
  ["each_seven_from_any", house, [REFs]]   each of the seven is in `house` from at least one REF
  ["conj_with_kind", P, WHO] ["aspected_by_kind", P, WHO] ["temp_friends", P, Q] ["nav_in_sign", P, [signs]]
  ["houses_count", [houses], WHO, REF, op, n]   (how many of the listed houses hold a WHO)
  ["is", P, Q or [Qs]]  ["friends", P, Q] (natural friends both ways)  ["aspects_house", P, h, REF]  ["true"]
Planet tokens: Sun..Ketu, Lagna, Gulika (sign only, when the birth time is known), L1..L12 (house lords), "disp:X" (lord of the sign X occupies),
  "nav:X" (lord of the sign X occupies in the navamsa), "navlord:X" (planet ruling X's navamsa sign, same as nav:X).
Classes (WHO): any, seven, nine, benefic, malefic, natural_benefic3, a planet name, or a list of tokens;
  "not:X" excludes token X from "seven".
"""
from common import SIGN_LORD
import vedic as V

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NINE = SEVEN + ["Rahu", "Ketu"]
SPECIAL = {"Mars": (4, 7, 8), "Jupiter": (5, 7, 9), "Saturn": (3, 7, 10), "Rahu": (5, 7, 9), "Ketu": (5, 7, 9)}
SIGN_TYPES = {"movable": (0, 3, 6, 9), "fixed": (1, 4, 7, 10), "dual": (2, 5, 8, 11), "odd": (0, 2, 4, 6, 8, 10),
              "even": (1, 3, 5, 7, 9, 11), "watery": (3, 7, 11, 9), "dry": (0, 4, 8, 1, 5)}
DIG = {"exalted": "exalted", "debilitated": "debilitated", "moolatrikona": "moolatrikona", "own": "own sign",
       "friend": "friend's sign", "enemy": "enemy's sign", "neutral": "neutral sign"}


class MissingPoint(KeyError):
    """A rule needs a point this chart does not have (e.g. Gulika without a birth time)."""


class Chart:
    def __init__(self, v, gender=None):
        self.v = v
        self.lag = v["_lag_sign"] if "_lag_sign" in v else _lag_index(v)
        self.S = {p: v["planets"][p]["sign_index"] for p in NINE}
        self.S["Lagna"] = self.lag
        self.lon = {p: v["planets"][p]["lon"] for p in NINE}
        self.dig = {p: v["planets"][p]["dignity"] for p in NINE}
        self.comb = {p: bool(v["planets"][p].get("combust")) for p in NINE}
        self.retro = {p: bool(v["planets"][p].get("retrograde")) for p in NINE}
        d9 = v["divisional_charts"]["D9"]
        from common import SIGNS
        self.N = {p: SIGNS.index(d9[p]) for p in NINE}
        self.N["Lagna"] = SIGNS.index(d9["Lagna"])
        sb = (v.get("shadbala") or {}).get("bphs", {}).get("planets", {})
        self.ratio = {p: sb.get(p, {}).get("ratio") for p in SEVEN}
        self.waxing_moon = (v.get("panchang") or {}).get("paksha") == "Shukla"
        up = v.get("upagrahas") or {}
        self.day = up.get("born_in") == "day" if up.get("born_in") else None
        self.gender = gender
        gl = ((v.get("upagrahas") or {}).get("time_based") or {}).get("Gulika")
        if gl:                       # Gulika as a point (sign only), for the few combinations that use it
            self.S["Gulika"] = int(gl["lon"] // 30)
        self.malefic_set = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"} | (set() if self.waxing_moon else {"Moon"})
        if any(self.S[m] == self.S["Mercury"] for m in self.malefic_set if m != "Mercury"):
            self.malefic_set.add("Mercury")
        self.benefic_set = {p for p in ("Jupiter", "Venus", "Mercury", "Moon") if p not in self.malefic_set}

    # ---- tokens
    def tok(self, t):
        if t in self.S:
            return t
        if t == "Gulika":
            raise MissingPoint(t)
        if t.startswith("L") and t[1:].isdigit():
            return SIGN_LORD[(self.lag + int(t[1:]) - 1) % 12]
        if t.startswith("disp:"):
            return SIGN_LORD[self.S[self.tok(t[5:])]]
        if t.startswith("nav:") or t.startswith("navlord:"):
            return SIGN_LORD[self.N[self.tok(t.split(":", 1)[1])]]
        raise KeyError(t)

    def sign(self, t):
        return self.S[self.tok(t)]

    def house(self, t, ref="Lagna"):
        return (self.sign(t) - self.sign(ref)) % 12 + 1

    def cls(self, who):
        if isinstance(who, list):
            out = set()
            for w in who:
                out |= self.cls(w)
            return out
        if who == "any" or who == "nine":
            return set(NINE)
        if who == "seven":
            return set(SEVEN)
        if who == "benefic":
            return set(self.benefic_set)
        if who == "malefic":
            return set(self.malefic_set)
        if who == "natural_benefic3":
            return {"Jupiter", "Venus", "Mercury"}
        if who.startswith("not:"):
            return set(SEVEN) - {self.tok(x) for x in who[4:].split(",")}
        return {self.tok(who)}

    def in_houses(self, hs, ref):
        return {p for p in NINE if self.house(p, ref) in hs}

    def aspects(self, p, q):
        p, q = self.tok(p), self.tok(q)
        if p not in NINE:
            return False
        h = (self.sign(q) - self.sign(p)) % 12 + 1
        return h in SPECIAL.get(p, (7,))

    def strong(self, p):
        p = self.tok(p)
        r = self.ratio.get(p)
        return (r is not None and r >= 1.0) and self.dig[p] != "debilitated" and not self.comb[p]


def _lag_index(v):
    from common import SIGNS
    return SIGNS.index(v["lagna"]["sign"])


def ev(c, e):
    op, a = e[0], e[1:]
    if op == "true":
        return True
    if op == "conj_with_kind":
        p = c.tok(a[0])
        return any(c.S[x] == c.S[p] for x in c.cls(a[1]) - {p})
    if op == "aspected_by_kind":
        p = c.tok(a[0])
        return any(c.aspects(x, p) for x in c.cls(a[1]) - {p})
    if op == "temp_friends":
        p, q = c.tok(a[0]), c.tok(a[1])
        return (c.S[q] - c.S[p]) % 12 + 1 in (2, 3, 4, 10, 11, 12)
    if op == "nav_in_sign":
        return c.N[c.tok(a[0])] in a[1]
    if op == "houses_count":
        hs, who = a[0], c.cls(a[1])
        rf = a[2] if len(a) > 2 else "Lagna"
        n = sum(1 for h in hs if any(c.house(p, rf) == h for p in who))
        return {">=": n >= a[4], "==": n == a[4]}[a[3]]
    if op == "is":
        targets = a[1] if isinstance(a[1], list) else [a[1]]
        return c.tok(a[0]) in {c.tok(x) for x in targets}
    if op == "friends":
        p, q = c.tok(a[0]), c.tok(a[1])
        return q in V.FRIENDS.get(p, []) and p in V.FRIENDS.get(q, [])
    if op == "aspects_house":
        p = c.tok(a[0])
        rf = a[2] if len(a) > 2 else "Lagna"
        target = (c.sign(rf) + a[1] - 1) % 12
        return (target - c.S[p]) % 12 + 1 in SPECIAL.get(p, (7,))
    if op == "and":
        return all(ev(c, x) for x in a)
    if op == "or":
        for x in a:
            try:
                if ev(c, x):
                    return True
            except MissingPoint:
                continue
        return False
    if op == "not":
        return not ev(c, a[0])
    ref = lambda i: a[i] if len(a) > i else "Lagna"  # noqa: E731
    if op == "in_house":
        return c.house(a[0], ref(2)) in a[1]
    if op == "in_sign":
        return c.sign(a[0]) in a[1]
    if op == "sign_type":
        return c.sign(a[0]) in SIGN_TYPES[a[1]]
    if op == "dignity":
        return c.dig.get(c.tok(a[0])) in {DIG[x] for x in a[1]}
    if op == "strong_sign":
        return c.dig.get(c.tok(a[0])) in ("exalted", "moolatrikona", "own sign")
    if op == "deep_exalt":
        p = c.tok(a[0])
        if c.dig.get(p) != "exalted":
            return False
        es, ed = V.EXALT[p]
        return abs((c.lon[p] % 30) - ed) <= a[1]
    if op == "nav_dignity":
        p = c.tok(a[0])
        if p not in V.EXALT:
            return False
        lon = c.N[p] * 30 + 15.0          # sign-level dignity in the navamsa (moolatrikona not used there)
        d = V.dignity(p, lon)
        names = {DIG[x] for x in a[1]}
        if "own sign" in names and d == "moolatrikona":
            return True
        return d in names
    if op == "conj":
        return c.sign(a[0]) == c.sign(a[1]) and c.tok(a[0]) != c.tok(a[1])
    if op == "aspects":
        return c.aspects(a[0], a[1])
    if op == "assoc":
        return (c.sign(a[0]) == c.sign(a[1]) and c.tok(a[0]) != c.tok(a[1])) or c.aspects(a[0], a[1]) or c.aspects(a[1], a[0])
    if op == "exchange":
        p, q = c.tok(a[0]), c.tok(a[1])
        return p != q and p in V.OWN and q in V.OWN and c.S[p] in V.OWN[q] and c.S[q] in V.OWN[p]
    if op == "mutual_kendra":
        return c.house(a[1], a[0]) in (1, 4, 7, 10)
    if op == "mutual_trine":
        return c.house(a[1], a[0]) in (1, 5, 9)
    if op == "rel_house":
        return c.house(a[1], a[0]) in a[2]
    if op in ("occupied", "any_in", "only", "none_in", "all_in", "count_in"):
        hs, who = a[0], c.cls(a[1])
        rf = a[2] if len(a) > 2 else "Lagna"
        if op == "occupied":
            return all(any(c.house(p, rf) == h for p in who) for h in hs)
        if op == "any_in":
            return any(c.house(p, rf) in hs for p in who)
        if op == "none_in":
            return not any(c.house(p, rf) in hs for p in who)
        if op == "all_in":
            return all(c.house(p, rf) in hs for p in who)
        if op == "only":
            occ = c.in_houses(hs, rf) - {"Rahu", "Ketu"}
            return bool(occ) and occ <= who
        n = sum(1 for p in who if c.house(p, rf) in hs)
        return {">=": n >= a[4], "==": n == a[4], "<=": n <= a[4]}[a[3]]
    if op == "seven_exact":
        rf = a[1] if len(a) > 1 else "Lagna"
        hs = {c.house(p, rf) for p in SEVEN}
        return hs == set(a[0])
    if op == "seven_signtype":
        return all(c.S[p] in SIGN_TYPES[a[0]] for p in SEVEN)
    if op == "seven_distinct":
        return len({c.S[p] for p in SEVEN}) == a[0]
    if op == "seven_run":
        hs = {c.house(p) for p in SEVEN}
        for st in a[0]:
            run = {((st - 1 + i) % 12) + 1 for i in range(a[1])}
            if hs == run:
                return True
        return False
    if op == "strong":
        return c.strong(a[0])
    if op == "combust":
        return c.comb[c.tok(a[0])]
    if op == "retro":
        return c.retro[c.tok(a[0])]
    if op == "waxing":
        return c.waxing_moon
    if op == "day_birth":
        return bool(c.day)
    if op == "male":
        return c.gender == "M"
    if op == "female":
        return c.gender == "F"
    if op == "assoc_with_kind":
        p, who = c.tok(a[0]), c.cls(a[1]) - {c.tok(a[0])}
        return any(c.S[q] == c.S[p] or c.aspects(q, p) for q in who)
    if op == "each_seven_from_any":
        return all(any(c.house(p, r) == a[0] for r in a[1]) for p in SEVEN)
    raise ValueError(f"unknown operator {op}")


def _grade(c, keys):
    vals = []
    for k in keys:
        p = c.tok(k)
        r = c.ratio.get(p)
        if r is None:
            continue
        s = r
        if c.dig[p] == "debilitated":
            s -= 0.3
        if c.comb[p]:
            s -= 0.25
        if c.house(p) in (6, 8, 12):
            s -= 0.15
        nd = V.dignity(p, c.N[p] * 30 + 15.0)
        if nd in ("exalted", "own sign", "moolatrikona"):
            s += 0.1
        elif nd == "debilitated":
            s -= 0.15
        vals.append(s)
    if not vals:
        return None, None
    m = sum(vals) / len(vals)
    return round(m, 2), ("strong" if m >= 1.2 else "moderate" if m >= 0.9 else "weak")


def evaluate(vedic, gender=None, rules=None):
    from yoga_rules import RULES, EXCLUDED
    rules = rules or RULES
    c = Chart(vedic, gender)
    found, errors = [], []
    for r in rules:
        try:
            if not ev(c, r["if"]):
                continue
            cancels = [x["reason"] for x in r.get("cancel", []) if ev(c, x["if"])]
            score, grade = _grade(c, r.get("key", []))
            found.append({"id": r["id"], "name": r["name"], "category": r["category"], "source": r["source"],
                          "rule": r["text"], "status": "cancelled" if cancels else "present",
                          "cancelled_by": cancels, "key_planets": [c.tok(k) for k in r.get("key", [])],
                          "strength_score": score, "strength": grade, "tone": r.get("tone", "supportive"),
                          "report": r.get("report", True), "note": r.get("note")})
        except MissingPoint:
            continue
        except Exception as e:  # a broken rule must never break the chart
            errors.append(f"{r.get('id')}: {e}")
    present = [f for f in found if f["status"] == "present" and f["report"]]
    return {"count_rules": len(rules), "found": found, "present_reportable": len(present),
            "by_category": {k: [f["name"] for f in present if f["category"] == k] for k in sorted({f["category"] for f in present})},
            "excluded_by_design": EXCLUDED, "errors": errors,
            "conventions": __doc__.split("Conventions (also returned in the output):")[1].split("Expression language")[0].strip()}
