"""custom_rules.py - v27: the two things the app computed only from its own fixed lists.

A divisional chart for any division the user asks for (F070), by either of the two common rules, and a yoga the user
defines themselves (F081), tested against one chart or against every saved person.

Nothing here is interpreted: a custom varga is drawn, and a custom rule says only whether it holds.
"""
import json

import engine_api as EA
import hindi_shell as HS
from app_details import bi, items, para, table

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
BODIES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
RULE_TEXT = {"cyclic": ("Count from Aries: the first part of every sign goes to Aries, then on round the zodiac.",
                        "मेष से गिनें: हर राशि का पहला भाग मेष को जाता है, फिर आगे राशिचक्र में।"),
             "from_sign": ("Count from the sign itself: the first part stays in its own sign, then on round the zodiac.",
                           "उसी राशि से गिनें: पहला भाग अपनी ही राशि में रहता है, फिर आगे राशिचक्र में।")}


def _sign_hi(s):
    return HS.SIGN.get(s, s)


def varga(c, n, rule="cyclic"):
    """The D-n chart of a chart dict: every planet and the lagna placed by the chosen counting rule."""
    n = max(2, min(60, int(n)))
    v = c["vedic"]
    part = 30.0 / n

    def place(lon):
        sign = int(lon // 30)
        k = int((lon % 30) // part)
        return (k if rule == "cyclic" else sign + k) % 12
    lag = SIGNS[place(v["lagna"]["lon"])]
    rows = [[bi("Lagna", "लग्न"), bi(lag, _sign_hi(lag))]]
    signs = {}
    for p in BODIES:
        r = v["planets"].get(p)
        if not r:
            continue
        s = SIGNS[place(r["lon"])]
        signs[p] = s
        rows.append([bi(p, HS.PLANET.get(p, p)), bi(s, _sign_hi(s))])
    te, th = RULE_TEXT[rule if rule in RULE_TEXT else "cyclic"]
    return signs, {"key": "custom_varga", "title": bi(f"D{n} by your own rule", f"आपके नियम से D{n}"),
                   "intro": bi(te, th),
                   "blocks": [table([bi("Body", "पिंड"), bi(f"Sign in D{n}", f"D{n} में राशि")], rows)],
                   "note": bi("The sixteen classical vargas in the Kundali screen use the rules each one is defined with; this chart uses the simple "
                              "rule you picked, so it will not match a classical D9 or D10.",
                              "कुंडली स्क्रीन के सोलह शास्त्रीय वर्ग अपनी-अपनी परिभाषा के नियमों से बनते हैं; यह कुंडली आपके चुने सरल नियम से बनी है, "
                              "इसलिए यह शास्त्रीय D9 या D10 से मेल नहीं खाएगी।")}


def _holds(c, cond):
    """One condition: {"planet", "in": "house"|"sign"|"with", "value"}."""
    v = c["vedic"]
    p = v["planets"].get(cond.get("planet"))
    if not p:
        return False
    kind, val = cond.get("in"), cond.get("value")
    if kind == "house":
        return str(p["house"]) == str(val)
    if kind == "sign":
        return p["sign"] == val
    if kind == "with":
        q = v["planets"].get(val)
        return bool(q) and q["sign_index"] == p["sign_index"]
    if kind == "aspects":
        q = v["planets"].get(val)
        if not q:
            return False
        return ((q["house"] - p["house"]) % 12) + 1 in (7,)
    return False


def _cond_text(cond):
    p = cond.get("planet", "")
    kind, val = cond.get("in"), cond.get("value")
    ph = HS.PLANET.get(p, p)
    if kind == "house":
        return f"{p} in house {val}", f"{ph} भाव {val} में"
    if kind == "sign":
        return f"{p} in {val}", f"{ph} {_sign_hi(val)} में"
    if kind == "with":
        return f"{p} with {val}", f"{ph} {HS.PLANET.get(val, val)} के साथ"
    if kind == "aspects":
        return f"{p} opposite {val}", f"{ph} {HS.PLANET.get(val, val)} के सम्मुख"
    return p, ph


def check(request_json):
    """{"rule": {"name", "conditions": [...], "all": true}, "people": [chart request, ...]} -> {"sections": [...]}."""
    r = json.loads(request_json)
    rule = r.get("rule") or {}
    conds = rule.get("conditions") or []
    need_all = rule.get("all", True)
    people = (r.get("people") or [])[:12]
    if not conds or not people:
        return json.dumps({"sections": []}, ensure_ascii=False)
    rows = []
    for q in people:
        c = EA.chart_obj(dict(q, modules="vedic"))
        res = [_holds(c, x) for x in conds]
        ok = all(res) if need_all else any(res)
        rows.append([bi(c["meta"]["name"]),
                     bi(", ".join(_cond_text(x)[0] for x, y in zip(conds, res) if y) or "none",
                        ", ".join(_cond_text(x)[1] for x, y in zip(conds, res) if y) or "कोई नहीं"),
                     bi("holds", "लागू") if ok else bi("does not hold", "लागू नहीं")])
    said = [bi(*_cond_text(x)) for x in conds]
    join = ("every condition must hold", "हर शर्त पूरी होनी चाहिए") if need_all else ("any one condition is enough", "कोई एक शर्त पर्याप्त है")
    secs = [{"key": "custom_rule", "title": bi(rule.get("name") or "Your rule", rule.get("name") or "आपका नियम"),
             "intro": bi(*join),
             "blocks": [items(said), table([bi("Person", "व्यक्ति"), bi("What matches", "क्या मिलता है"), bi("Result", "परिणाम")], rows)],
             "note": bi("Your own rule, tested as written. The app does not read anything into it, and a yoga usually needs more than placement: "
                        "strength, aspects and the dasha all matter.",
                        "आपका अपना नियम, जैसा लिखा गया वैसा जाँचा गया। ऐप इसमें कोई फल नहीं जोड़ता, और किसी योग के लिए केवल स्थिति पर्याप्त नहीं होती: "
                        "बल, दृष्टि और दशा सब मायने रखते हैं।")}]
    return json.dumps({"sections": secs}, ensure_ascii=False)


def varga_json(request_json):
    """{"n", "rule", plus a chart request} -> {"signs": {...}, "sections": [...]}."""
    r = json.loads(request_json)
    c = EA.chart_obj(dict(r, modules="vedic"))
    signs, sec = varga(c, r.get("n", 9), r.get("rule", "cyclic"))
    signs["Lagna"] = sec["blocks"][0]["rows"][0][1]["en"]
    return json.dumps({"signs": signs, "sections": [sec]}, ensure_ascii=False)
