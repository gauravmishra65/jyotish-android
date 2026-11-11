"""app_match_more.py - the Western side of Kundli Milan as bilingual sections (v16): synastry contacts, house overlays,
and the composite and Davison relationship charts. The match engine (chart_engine.match_charts) already computes all
of it; this only words it. Contacts are described as themes to talk about, never as verdicts on the relationship.
"""
import hindi_shell as HS
from app_details import bi, P, table, para, items, pos, house_word

BODY_HI = {"Uranus": "यूरेनस", "Neptune": "नेप्च्यून", "Pluto": "प्लूटो", "North Node": "उत्तर नोड", "Ascendant": "लग्न (असेंडेंट)",
           "Midheaven": "मध्याकाश (MC)"}
TAG = {"Venus-Mars (attraction)": ("Venus–Mars: attraction and warmth", "शुक्र–मंगल: आकर्षण और गर्मजोशी"),
       "Moon-Moon (emotional fit)": ("Moon–Moon: how your feelings fit", "चंद्र–चंद्र: भावनाओं का मेल"),
       "Sun-Moon (core compatibility)": ("Sun–Moon: core compatibility", "सूर्य–चंद्र: मूल अनुकूलता"),
       "Saturn contact (commitment / restriction)": ("Saturn contact: commitment, and room each needs", "शनि संपर्क: प्रतिबद्धता, और दोनों को अपना स्थान"),
       "Venus-Venus (values)": ("Venus–Venus: shared values and tastes", "शुक्र–शुक्र: साझा मूल्य और रुचियाँ")}
EASY = {"trine", "sextile"}


def _b(name):
    return bi(name, HS.PLANET.get(name) or BODY_HI.get(name, name))


def _asp(a):
    return bi(a, HS.ASPECT.get(a, a))


def synastry(m, na, nb):
    s = m.get("western_synastry") or {}
    blocks = []
    key = s.get("key_aspects") or []
    if key:
        rows = [[bi(f"{na}'s {x['a']}", f"{na} का {HS.PLANET.get(x['a']) or BODY_HI.get(x['a'], x['a'])}"), _asp(x["aspect"]),
                 bi(f"{nb}'s {x['b']}", f"{nb} का {HS.PLANET.get(x['b']) or BODY_HI.get(x['b'], x['b'])}"),
                 bi(f"{x['orb']:.1f}°"), bi(*TAG.get(x["significance"], (x["significance"], x["significance"])))] for x in key]
        blocks.append(table([bi(na), bi("Aspect", "दृष्टि"), bi(nb), bi("Orb", "अंतर"), bi("Theme", "विषय")], rows))
    close = [x for x in (s.get("all_interaspects") or []) if x["orb"] <= 2.0][:10]
    if close:
        blocks.append(para(bi("The closest contacts between the two charts (within 2°):", "दोनों कुंडलियों के सबसे निकट संपर्क (2° के भीतर):")))
        blocks.append(items([bi(f"{na}'s {x['a']} {x['aspect']} {nb}'s {x['b']} ({x['orb']:.1f}°)" + (", easy flow" if x["aspect"] in EASY else ""),
                                f"{na} का {HS.PLANET.get(x['a']) or BODY_HI.get(x['a'], x['a'])} – {nb} का {HS.PLANET.get(x['b']) or BODY_HI.get(x['b'], x['b'])}: "
                                f"{HS.ASPECT.get(x['aspect'], x['aspect'])} ({x['orb']:.1f}°)" + (", सहज प्रवाह" if x["aspect"] in EASY else ""))
                             for x in close]))
    ov = s.get("house_overlay_A_in_B_whole_sign") or {}
    ov2 = s.get("house_overlay_B_in_A_whole_sign") or {}
    if ov and ov2:
        main = ("Sun", "Moon", "Venus", "Mars")
        rows = [[_b(p), house_word(ov[p]) if p in ov else bi("–"), house_word(ov2[p]) if p in ov2 else bi("–")] for p in main]
        blocks.append(para(bi("House overlays: where each person's planets fall in the other's chart (whole-sign houses).",
                              "भाव ओवरले: हर व्यक्ति के ग्रह दूसरे की कुंडली के किस भाव में पड़ते हैं (पूर्ण राशि भाव)।")))
        blocks.append(table([bi("Planet", "ग्रह"), bi(f"{na}'s in {nb}'s chart", f"{na} के, {nb} की कुंडली में"),
                             bi(f"{nb}'s in {na}'s chart", f"{nb} के, {na} की कुंडली में")], rows))
    if not blocks:
        return None
    return {"key": "synastry", "title": bi("Western synastry", "पाश्चात्य सिनेस्ट्री"),
            "intro": bi("Synastry compares the two tropical charts planet by planet. Easy contacts (trine, sextile) flow; hard ones (square, opposition) "
                        "are where the couple learns to adjust.",
                        "सिनेस्ट्री दोनों सायन कुंडलियों की ग्रह-दर-ग्रह तुलना है। सहज संपर्क (त्रिकोण, सेक्स्टाइल) सरलता से बहते हैं; कठिन संपर्क "
                        "(चतुष्कोण, प्रतियोग) वहाँ हैं जहाँ जोड़ा तालमेल सीखता है।"),
            "blocks": blocks}


def _chart_rows(planets, house_key):
    out = []
    for p in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        o = planets.get(p)
        if o:
            out.append([_b(p), pos(o.get("position")), house_word(o.get(house_key) or o.get("house_whole_sign"))])
    return out


def composite(m):
    c, d = m.get("western_composite") or {}, m.get("western_davison") or {}
    blocks = []
    if c.get("planets"):
        blocks += [para(bi(f"Composite chart (midpoints of the two charts). Ascendant {pos(c.get('ascendant'))['en']}.",
                           f"कंपोज़िट कुंडली (दोनों कुंडलियों के मध्यबिंदु)। लग्न {pos(c.get('ascendant'))['hi']}।")),
                   table([bi("Planet", "ग्रह"), bi("Position", "स्थिति"), bi("House", "भाव")], _chart_rows(c["planets"], "house_whole_sign"))]
    if d.get("planets"):
        blocks += [para(bi(f"Davison chart (a real chart for the midpoint in time and place, {d.get('moment_utc', '')} UT). Ascendant {pos(d.get('ascendant'))['en']}.",
                           f"डेविसन कुंडली (समय और स्थान के मध्यबिंदु की वास्तविक कुंडली, {d.get('moment_utc', '')} UT)। लग्न {pos(d.get('ascendant'))['hi']}।")),
                   table([bi("Planet", "ग्रह"), bi("Position", "स्थिति"), bi("House", "भाव")], _chart_rows(d["planets"], "house_placidus"))]
    if not blocks:
        return None
    warn = c.get("warning") or d.get("warning")
    return {"key": "composite", "title": bi("Composite and Davison charts", "कंपोज़िट और डेविसन कुंडली"),
            "intro": bi("Both describe the relationship itself as a third chart. Planets in houses 5 and 7 colour romance and partnership.",
                        "दोनों संबंध को एक तीसरी कुंडली के रूप में बताती हैं। 5वें और 7वें भाव के ग्रह प्रेम और साझेदारी का रंग बताते हैं।"),
            "blocks": blocks,
            "note": bi("One birth time is unknown, so the Ascendant, houses and the Moon's degree are not reliable." if warn else
                       "Tropical zodiac; composite houses are whole-sign from the composite Ascendant, Davison houses are Placidus.",
                       "एक जन्म समय अज्ञात है, इसलिए लग्न, भाव और चंद्र का अंश विश्वसनीय नहीं।" if warn else
                       "सायन राशिचक्र; कंपोज़िट के भाव कंपोज़िट लग्न से पूर्ण राशि, डेविसन के भाव प्लेसिडस।")}


def build(m):
    people = m.get("people") or ["A", "B"]
    na, nb = (people + ["A", "B"])[:2]
    out = []
    for f in ((lambda: synastry(m, na.split()[0], nb.split()[0])), (lambda: composite(m))):
        try:
            s = f()
        except (KeyError, TypeError, ValueError, IndexError):
            s = None
        if s:
            out.append(s)
    try:
        import chinese_depth as CD
        if m.get("_bazi_a") and m.get("_bazi_b"):
            out.append(CD.bazi_match(m["_bazi_a"], m["_bazi_b"], na.split()[0], nb.split()[0]))
    except (KeyError, TypeError, ValueError, IndexError):
        pass
    return out
