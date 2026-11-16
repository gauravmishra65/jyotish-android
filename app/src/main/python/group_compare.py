"""group_compare.py - v26: several saved people side by side (F045).

One table of the facts that identify each chart (lagna, Moon, nakshatra, Sun, Western big three, BaZi day master, Life
Path), then what the group shares and where it differs, and the transits that reach everyone at once. Facts only; no
group reading is attempted.
"""
import json

import engine_api as EA
import hindi_shell as HS
from app_details import bi, items, para, table

EL_HI = {"Wood": "काष्ठ", "Fire": "अग्नि", "Earth": "पृथ्वी", "Metal": "धातु", "Water": "जल"}
SIGNS_HI = HS.SIGN


def _sign(s):
    return bi(s, SIGNS_HI.get(s, s))


def _rows(charts):
    head = [bi("", "")] + [bi(c["meta"]["name"].split()[0]) for c in charts]
    out = []

    def row(lab_en, lab_hi, f):
        cells = []
        for c in charts:
            try:
                cells.append(f(c))
            except Exception:
                cells.append(bi("–"))
        out.append([bi(lab_en, lab_hi)] + cells)
    row("Lagna", "लग्न", lambda c: _sign(c["vedic"]["lagna"]["sign"]))
    row("Moon sign", "चंद्र राशि", lambda c: _sign(c["vedic"]["planets"]["Moon"]["sign"]))
    row("Moon nakshatra", "चंद्र नक्षत्र", lambda c: bi(c["vedic"]["planets"]["Moon"]["nakshatra"],
                                                        HS.NAK.get(c["vedic"]["planets"]["Moon"]["nakshatra"], c["vedic"]["planets"]["Moon"]["nakshatra"])))
    row("Sun sign (sidereal)", "सूर्य राशि (निरयण)", lambda c: _sign(c["vedic"]["planets"]["Sun"]["sign"]))
    row("Current mahadasha", "वर्तमान महादशा", lambda c: bi(c["vedic"]["dashas"]["vimshottari"]["current"]["mahadasha"]["lord"],
                                                              HS.PLANET.get(c["vedic"]["dashas"]["vimshottari"]["current"]["mahadasha"]["lord"], "")))
    row("Western Sun", "पाश्चात्य सूर्य", lambda c: _sign(c["western"]["big_three"]["sun"]))
    row("Western Moon", "पाश्चात्य चंद्र", lambda c: _sign(c["western"]["big_three"]["moon"]))
    row("Western rising", "पाश्चात्य उदय", lambda c: _sign(c["western"]["big_three"]["rising"]))
    row("BaZi Day Master", "बाज़ी दिवस स्वामी", lambda c: bi(f"{c['bazi']['day_master']['stem']} {c['bazi']['day_master']['element']}",
                                                              f"{c['bazi']['day_master']['stem']} {EL_HI.get(c['bazi']['day_master']['element'], '')}"))
    row("Chinese year animal", "चीनी वर्ष पशु", lambda c: bi(c["bazi"]["pillars"]["year"]["animal"],
                                                               c["bazi"]["pillars"]["year"].get("animal_hi") or c["bazi"]["pillars"]["year"]["animal"]))
    row("Life Path", "जीवन पथ", lambda c: bi(str(c["numerology"]["life_path"]["value"])))
    row("Personal year now", "अभी व्यक्तिगत वर्ष", lambda c: bi(str(c["numerology"]["personal_cycles"]["personal_year"])))
    return head, out


def _shared(charts):
    out = []

    def same(lab_en, lab_hi, f):
        vals = []
        for c in charts:
            try:
                vals.append(f(c))
            except Exception:
                return
        if len(set(vals)) == 1:
            out.append(bi(f"Everyone shares {lab_en}: {vals[0]}", f"सबका {lab_hi} एक ही है: {SIGNS_HI.get(vals[0], vals[0])}"))
    same("the lagna", "लग्न", lambda c: c["vedic"]["lagna"]["sign"])
    same("the Moon sign", "चंद्र राशि", lambda c: c["vedic"]["planets"]["Moon"]["sign"])
    same("the Western Sun sign", "पाश्चात्य सूर्य राशि", lambda c: c["western"]["big_three"]["sun"])
    same("the Chinese year animal", "चीनी वर्ष पशु", lambda c: c["bazi"]["pillars"]["year"]["animal"])
    same("the Life Path number", "जीवन पथ अंक", lambda c: str(c["numerology"]["life_path"]["value"]))
    # a transit that touches every chart's Moon sign at once
    try:
        signs = {c["vedic"]["planets"]["Moon"]["sign_index"] for c in charts}
        tr = charts[0]["vedic"]["transits_now"]["positions"]
        for p, r in tr.items():
            if p in ("Saturn", "Jupiter", "Rahu", "Ketu") and r["sign_index"] in signs and len(signs) == 1:
                out.append(bi(f"{p} is transiting the Moon sign everyone shares.",
                              f"{HS.PLANET.get(p, p)} उस चंद्र राशि से गोचर कर रहा है जो सबकी एक ही है।"))
    except Exception:
        pass
    return out


def compare(request_json):
    """{"people": [chart request, ...]} -> {"sections": [...]}: up to six people side by side."""
    r = json.loads(request_json)
    people = (r.get("people") or [])[:6]
    charts = []
    for p in people:
        q = dict(p)
        q["modules"] = "all"
        charts.append(EA.chart_obj(q))
    if len(charts) < 2:
        return json.dumps({"sections": []}, ensure_ascii=False)
    head, rows = _rows(charts)
    shared = _shared(charts)
    secs = [{"key": "group_facts", "title": bi(f"{len(charts)} people side by side", f"{len(charts)} लोग साथ-साथ"),
             "blocks": [table(head, rows)],
             "note": bi("Facts from each chart, nothing read into them. Use Milan for a two-person comparison.",
                        "हर कुंडली के तथ्य, कोई फलादेश नहीं। दो लोगों की तुलना के लिए मिलान देखें।")},
            {"key": "group_shared", "title": bi("What this group shares", "इस समूह में क्या साझा है"),
             "blocks": [items(shared) if shared else para(bi("Nothing in the list above is the same for everyone.",
                                                             "ऊपर की सूची में कुछ भी सबके लिए एक जैसा नहीं है।"))]}]
    return json.dumps({"sections": secs}, ensure_ascii=False)
