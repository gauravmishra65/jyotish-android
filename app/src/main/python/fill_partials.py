"""fill_partials.py - v22: sections that complete features the app only partly showed.

Kundali details (build): birth time details (local mean and true solar time), calculation versions, Western house
systems side by side, lunations and eclipses, elements and modalities, midpoints, harmonics, sidereal presets, sect and
planetary condition, the four cardinal ingresses, BaZi elements with seasonal strength, BaZi combinations and clashes,
BaZi cycles (this year's months), hour-pillar options when the birth time is unknown, and numerology working with
pinnacles and challenges.  Milan (bazi_relations): every relation between the two BaZi charts.
Chinese screen (chinese_sections): the 24 solar terms of the year, a glossary of stems and branches, real and nominal age.
"""
import datetime as dt

import swisseph as swe

import chinese as CH
import hindi_shell as HS
import numerology as num
import western_more as WM
from app_details import bi, table, para, items

EL_HI = {"Wood": "काष्ठ", "Fire": "अग्नि", "Earth": "पृथ्वी", "Metal": "धातु", "Water": "जल", "Air": "वायु"}
MOD_HI = {"Cardinal": "चर", "Fixed": "स्थिर", "Mutable": "द्विस्वभाव"}
PILLAR_HI = {"Year": "वर्ष", "Month": "माह", "Day": "दिन", "Hour": "घड़ी", "Annual": "वार्षिक", "Luck": "दशा"}
SEASON = {"旺": ("strongest in this season", "इस ऋतु में सबसे बली"), "相": ("supported by the season", "ऋतु से सहारा"),
          "休": ("resting", "विश्राम में"), "囚": ("held back", "रुका हुआ"), "死": ("weakest in this season", "इस ऋतु में सबसे निर्बल")}
REL = [("six harmony", "छह सामंजस्य"), ("half three-harmony", "अर्ध त्रि-सामंजस्य"), ("three harmony", "त्रि-सामंजस्य"),
       ("three meeting", "त्रि-मिलन"), ("stem combination", "तना संयोग"), ("stem clash", "तना टकराव"), ("clash", "टकराव"),
       ("harm", "बाधा"), ("destruction", "विघ्न"), ("self-punishment", "स्व-दंड"), ("punishment", "दंड"), ("partial", "आंशिक"),
       ("three-branch", "त्रि-शाखा")]
STEM_HI = ["जिया", "यी", "बिंग", "डिंग", "वू", "जी", "गेंग", "शिन", "रेन", "गुई"]
BRANCH_HI = ["ज़ी", "चोउ", "यिन", "माओ", "चेन", "सी", "वू", "वेई", "शेन", "योउ", "शू", "हाई"]
ANIMAL_HI = ["चूहा", "बैल", "बाघ", "खरगोश", "ड्रैगन", "साँप", "घोड़ा", "बकरी", "बंदर", "मुर्गा", "कुत्ता", "सूअर"]
ELS = ["Wood", "Fire", "Earth", "Metal", "Water"]
TERMS = [("立春", "Li Chun", "Start of spring", "वसंत आरंभ"), ("雨水", "Yu Shui", "Rain water", "वर्षा जल"), ("惊蛰", "Jing Zhe", "Insects awaken", "कीट जागरण"),
         ("春分", "Chun Fen", "Spring equinox", "वसंत विषुव"), ("清明", "Qing Ming", "Clear and bright", "स्वच्छ और उज्ज्वल"), ("谷雨", "Gu Yu", "Grain rain", "अन्न वर्षा"),
         ("立夏", "Li Xia", "Start of summer", "ग्रीष्म आरंभ"), ("小满", "Xiao Man", "Grain buds", "अन्न कलियाँ"), ("芒种", "Mang Zhong", "Grain in ear", "बाली में अन्न"),
         ("夏至", "Xia Zhi", "Summer solstice", "ग्रीष्म संक्रांति"), ("小暑", "Xiao Shu", "Minor heat", "लघु ताप"), ("大暑", "Da Shu", "Major heat", "महा ताप"),
         ("立秋", "Li Qiu", "Start of autumn", "शरद आरंभ"), ("处暑", "Chu Shu", "End of heat", "ताप का अंत"), ("白露", "Bai Lu", "White dew", "श्वेत ओस"),
         ("秋分", "Qiu Fen", "Autumn equinox", "शरद विषुव"), ("寒露", "Han Lu", "Cold dew", "शीत ओस"), ("霜降", "Shuang Jiang", "Frost descends", "पाला"),
         ("立冬", "Li Dong", "Start of winter", "शीत आरंभ"), ("小雪", "Xiao Xue", "Minor snow", "लघु हिम"), ("大雪", "Da Xue", "Major snow", "महा हिम"),
         ("冬至", "Dong Zhi", "Winter solstice", "शीत संक्रांति"), ("小寒", "Xiao Han", "Minor cold", "लघु शीत"), ("大寒", "Da Han", "Major cold", "महा शीत")]
HSYS = [(b"P", "Placidus", "प्लेसिडस"), (b"W", "Whole sign", "पूर्ण राशि"), (b"K", "Koch", "कोख"), (b"E", "Equal", "समान"),
        (b"R", "Regiomontanus", "रेजियोमोंटेनस"), (b"C", "Campanus", "कैम्पेनस"), (b"O", "Porphyry", "पोर्फिरी")]
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _date(jd, tz=0.0):
    y, m, d, h = swe.revjul(jd + tz / 24.0)
    return dt.datetime(y, m, d) + dt.timedelta(hours=h)


def _d(t):
    return bi(t.strftime("%d %b %Y"), f"{t.day} {MONTH_HI[t.month - 1]} {t.year}")


def _rel_hi(s):
    out = s
    for en, hi in REL:
        out = out.replace(en, hi)
    for en, hi in list(EL_HI.items()) + [("uncivil", "अशिष्ट"), ("bullying", "दबाव"), ("ungrateful", "कृतघ्न"), ("frame", "ढाँचा")]:
        out = out.replace(en, hi).replace(en.lower(), hi)
    return out


def _where_hi(s):
    for en, hi in PILLAR_HI.items():
        s = s.replace(en, hi)
    return s


# ------------------------------------------------------------------ time and versions
TIME_SOURCE = {"certificate": ("Birth certificate", "जन्म प्रमाणपत्र"), "hospital": ("Hospital record", "अस्पताल का रिकॉर्ड"),
               "family": ("Family memory", "परिवार की याद"), "horoscope": ("Old horoscope", "पुरानी जन्मपत्री"), "rectified": ("Rectified", "संशोधित समय")}


def time_details(c):
    t = c["time_pipeline"]
    rows = [[bi("Clock time at birth", "जन्म का घड़ी समय"), bi(t["local_civil"][:16])],
            [bi("Time zone", "समय क्षेत्र"), bi(f"{t['timezone']} (UTC{t['utc_offset_hours']:+g})")],
            [bi("Daylight saving removed", "डेलाइट सेविंग हटाई"), bi(f"{t['dst_removed_hours']:g} h", f"{t['dst_removed_hours']:g} घंटे")],
            [bi("Universal time", "सार्वभौमिक समय"), bi(t["utc"][:16])],
            [bi("Local mean time", "स्थानीय माध्य समय"), bi(t["local_mean_time"][:19])],
            [bi("Equation of time", "समय समीकरण"), bi(f"{t['equation_of_time_min']:+.1f} min", f"{t['equation_of_time_min']:+.1f} मिनट")],
            [bi("True solar time", "वास्तविक सौर समय"), bi(t["true_solar_time"][:19])]]
    conf = {"certificate": ("from a certificate", "प्रमाणपत्र से"), "reliable": ("reliable", "विश्वसनीय"), "approximate": ("approximate", "अनुमानित"),
            "unknown": ("not known", "ज्ञात नहीं")}.get(c["meta"].get("birth_time_confidence"))
    if conf:
        rows.insert(0, [bi("How sure the time is", "समय कितना पक्का है"), bi(*conf)])
    if t.get("julian_date"):
        rows.insert(0, [bi("Date as recorded", "जैसी तिथि दर्ज थी"), bi(t["julian_date"], t["julian_date"].replace("(Julian calendar)", "(जूलियन पंचांग)"))])
    if any("happened twice" in w for w in (t.get("warnings") or [])):
        rows.append([bi("Clocks went back that day", "उस दिन घड़ी पीछे हुई"),
                     bi("the second occurrence was used", "दूसरी बार वाला समय लिया गया") if t.get("ambiguous_occurrence")
                     else bi("the first occurrence was used", "पहली बार वाला समय लिया गया")])
    src = TIME_SOURCE.get(c["meta"].get("time_source"))
    if src:
        rows.insert(0, [bi("Source of the time", "समय का स्रोत"), bi(*src)])
    return {"key": "time_details", "title": bi("Birth time in detail", "जन्म समय का विवरण"),
            "blocks": [table([bi("Step", "चरण"), bi("Value", "मान")], rows)],
            "note": bi("Local mean time shifts the clock by the birthplace's longitude; true solar time adds the equation of time. BaZi can use either (Settings).",
                       "स्थानीय माध्य समय घड़ी को जन्मस्थान के देशांतर से खिसकाता है; वास्तविक सौर समय में समय समीकरण जुड़ता है। बाज़ी दोनों में से कोई भी ले सकता है (सेटिंग्स)।")}


def versions(c):
    a = c.get("audit") or {}
    e, v, b = a.get("engine") or {}, a.get("vedic_conventions") or {}, a.get("bazi_conventions") or {}
    rows = [[bi("Swiss Ephemeris", "स्विस एफेमेरिस"), bi(str(e.get("swiss_ephemeris", swe.version)))],
            [bi("Ephemeris data", "एफेमेरिस डेटा"), bi("Swiss Ephemeris data files (JPL-derived)", "स्विस एफेमेरिस डेटा फ़ाइलें (JPL आधारित)")],
            [bi("Chart contents version", "कुंडली सामग्री संस्करण"), bi("12")]]
    if v:
        rows += [[bi("Ayanamsa", "अयनांश"), bi(f"{str(v.get('ayanamsa', '')).title()} {v.get('ayanamsa_deg', 0):.4f}°", f"{HS_AYAN.get(str(v.get('ayanamsa')), 'चयनित')} {v.get('ayanamsa_deg', 0):.4f}°")],
                 [bi("Lunar node", "चंद्र नोड"), bi("Mean node", "माध्य नोड") if "mean" in str(v.get("rahu")) else bi("True node", "वास्तविक नोड")],
                 [bi("Vedic houses", "वैदिक भाव"), bi("Whole sign; bhava chalit by Sripati midpoints", "पूर्ण राशि; भाव चलित श्रीपति मध्यबिंदुओं से")],
                 [bi("Vimshottari year", "विंशोत्तरी वर्ष"), bi(f"{v.get('vimshottari_year_days')} days", f"{v.get('vimshottari_year_days')} दिन")]]
    if b:
        rows += [[bi("BaZi time basis", "बाज़ी समय आधार"), bi("True solar time", "वास्तविक सौर समय") if "solar" in str(b.get("primary_time_basis")) else bi("Standard time", "मानक समय")],
                 [bi("Zi hour rule", "ज़ी घड़ी नियम"), bi("Day changes at 23:00", "दिन 23:00 पर बदलता है") if "23" in str(b.get("zi_hour_convention")) else bi("Day changes at midnight", "दिन मध्यरात्रि पर बदलता है")],
                 [bi("BaZi year and month", "बाज़ी वर्ष और माह"), bi("From Li Chun and the jie solar terms, exact instants", "ली चुन और जिए सौर पदों से, सटीक क्षण")]]
    return {"key": "calc_versions", "title": bi("Calculation versions and conventions", "गणना संस्करण और परंपराएँ"),
            "blocks": [table([bi("Part", "भाग"), bi("Value", "मान")], rows)],
            "note": bi("Quote these when comparing this chart with another program.", "किसी अन्य प्रोग्राम से तुलना करते समय ये बताएँ।")}


HS_AYAN = {"lahiri": "लाहिड़ी", "raman": "रमन", "krishnamurti": "कृष्णमूर्ति", "kp": "कृष्णमूर्ति", "fagan_bradley": "फ़ेगन-ब्रैडली", "yukteshwar": "युक्तेश्वर"}
NAK = 360 / 27


def settings_compare(c):
    """What each calculation setting would change for this chart (the ayanamsa has its own table)."""
    jd = c["time_pipeline"]["jd_ut"]
    v = c["vedic"]["conventions"] if isinstance(c.get("vedic", {}).get("conventions"), dict) else {}
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ay = (c.get("audit") or {}).get("vedic_conventions", {}).get("ayanamsa_deg") or swe.get_ayanamsa_ut(jd)
    mean = (swe.calc_ut(jd, swe.MEAN_NODE)[0][0] - ay) % 360
    true = (swe.calc_ut(jd, swe.TRUE_NODE)[0][0] - ay) % 360
    same = int(mean // 30) == int(true // 30) and int(mean // NAK) == int(true // NAK)
    rows = [[bi("Rahu: mean or true node", "राहु: माध्य या वास्तविक नोड"), WM._s(mean), WM._s(true),
             bi("same sign and nakshatra", "राशि और नक्षत्र वही") if same else bi("sign or nakshatra changes", "राशि या नक्षत्र बदलता है")]]
    t = c["time_pipeline"]
    std, sol = dt.datetime.fromisoformat(t["local_standard_time"][:19]), dt.datetime.fromisoformat(t["true_solar_time"][:19])
    hb = lambda x: ((x.hour + 1) // 2) % 12              # noqa: E731
    rows.append([bi("BaZi hour: standard or solar time", "बाज़ी घड़ी: मानक या सौर समय"), bi(f"{CH.BRANCHES[hb(std)]} ({std:%H:%M})"), bi(f"{CH.BRANCHES[hb(sol)]} ({sol:%H:%M})"),
                 bi("same hour pillar", "घड़ी स्तंभ वही") if hb(std) == hb(sol) else bi("hour pillar changes", "घड़ी स्तंभ बदलता है")])
    late = sol.hour == 23
    rows.append([bi("Zi hour: day changes at 23:00 or midnight", "ज़ी घड़ी: दिन 23:00 या मध्यरात्रि पर"), bi("23:00"), bi("00:00"),
                 bi("day pillar differs (born 23:00–24:00)", "दिवस स्तंभ अलग (जन्म 23:00–24:00)") if late else bi("no effect on this chart", "इस कुंडली पर कोई प्रभाव नहीं")])
    age = c["vedic"].get("age_years_at_now") or 0
    shift = age * (365.25 - 360) / 365.25
    rows.append([bi("Western houses", "पाश्चात्य भाव"), bi(c["western"]["house_system"] if c.get("western") else "–"),
                 bi("seven systems", "सात पद्धतियाँ"), bi("changes which house each planet falls in", "बदलता है कि कौन सा ग्रह किस भाव में पड़ता है")])
    rows.append([bi("Dasha year: 365.25 or 360 days", "दशा वर्ष: 365.25 या 360 दिन"), bi("365.25"), bi("360"),
                 bi(f"dasha dates now fall about {shift * 12:.0f} months earlier with 360", f"360 के साथ दशा तिथियाँ अभी लगभग {shift * 12:.0f} माह पहले पड़ती हैं")])
    return {"key": "settings_compare", "title": bi("What the settings change", "सेटिंग्स से क्या बदलता है"),
            "blocks": [table([bi("Setting", "सेटिंग"), bi("Option 1", "विकल्प 1"), bi("Option 2", "विकल्प 2"), bi("Effect on this chart", "इस कुंडली पर प्रभाव")], rows)],
            "note": bi("The ayanamsa choices have their own table above. Change any of these in Settings.", "अयनांश विकल्पों की अलग तालिका ऊपर है। ये सब सेटिंग्स में बदले जा सकते हैं।")}


def relocation(c, pos):
    r = c["meta"].get("residence_place")
    if not r:
        return None
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]

    def angles(lat, lon):
        cusps, ascmc = swe.houses(jd, lat, lon, b"P")
        return cusps, ascmc[0], ascmc[1]

    def house(lon, cusps):
        for h in range(12):
            a, b_ = cusps[h], cusps[(h + 1) % 12]
            if (lon - a) % 360 < (b_ - a) % 360:
                return h + 1
        return 12
    c1, a1, m1 = angles(pl["lat"], pl["lon"])
    c2, a2, m2 = angles(r["lat"], r["lon"])
    rows = [[bi("Ascendant", "लग्न"), WM._s(a1), WM._s(a2)], [bi("Midheaven", "दशम"), WM._s(m1), WM._s(m2)]]
    moved = []
    for p in WM.TEN:
        h1, h2 = house(pos[p]["lon"], c1), house(pos[p]["lon"], c2)
        rows.append([WM._p(p), bi(f"house {h1}", f"भाव {h1}"), bi(f"house {h2}", f"भाव {h2}")])
        if h1 != h2:
            moved.append(p)
    name = r.get("label") or ""
    return {"key": "w_relocation", "title": bi("Western: relocated chart", "पाश्चात्य: स्थानांतरित कुंडली"),
            "intro": bi(f"{len(moved)} of 10 planets change house where you live now." if moved else "No planet changes house where you live now.",
                        f"जहाँ आप अभी रहते हैं वहाँ 10 में से {len(moved)} ग्रह भाव बदलते हैं।" if moved else "जहाँ आप अभी रहते हैं वहाँ कोई ग्रह भाव नहीं बदलता।"),
            "blocks": [table([bi("Point", "बिंदु"), bi("At the birthplace", "जन्मस्थान पर"), bi("Where you live" + (f" ({name})" if name else ""), "वर्तमान निवास पर")], rows)],
            "note": bi("The same birth moment cast for your current place: planets keep their signs; the angles and houses move. Placidus houses.",
                       "वही जन्म क्षण आपके वर्तमान स्थान के लिए: ग्रहों की राशियाँ वही रहती हैं; कोण और भाव बदलते हैं। प्लेसिडस भाव।")}


ASPECTS = ((0, "conjunct", "युति"), (60, "sextile", "त्रिएकादश"), (90, "square", "केंद्र"), (120, "trine", "त्रिकोण"), (180, "opposite", "सम्मुख"))


def election(c):
    """Western election screen for the next 30 days: the Moon's phase, speed, void of course and her next aspect."""
    tz = c["time_pipeline"]["utc_offset_hours"]
    now = dt.datetime.fromisoformat(c["meta"]["generated_for_date"])
    j0 = swe.julday(now.year, now.month, now.day, 12.0 - tz)
    bodies = {"Sun": swe.SUN, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN}
    days = []
    for k in range(1, 31):
        jd = j0 + k
        moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)[0]
        ml, ms = moon[0], moon[3]
        lon = {n: swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SPEED)[0] for n, b in bodies.items()}
        left = 30 - ml % 30                      # degrees the Moon still has in her sign
        nxt = None
        for n, x in lon.items():
            for ang, en, _ in ASPECTS:
                for target in ((x[0] + ang) % 360, (x[0] - ang) % 360):
                    gap = (target - ml) % 360
                    if gap < left and (nxt is None or gap < nxt[0]):
                        nxt = (gap, n, en)
        waxing = (ml - lon["Sun"][0]) % 360 < 180
        score, why, why_hi = 0, [], []
        if waxing:
            score += 1
            why.append("Moon waxing")
            why_hi.append("चंद्र बढ़ता हुआ")
        if nxt is None:
            score -= 2
            why.append("Moon void of course")
            why_hi.append("चंद्र शून्य मार्ग में")
        elif nxt[1] in ("Venus", "Jupiter") and nxt[2] in ("conjunct", "sextile", "trine"):
            score += 2
            why.append(f"Moon applies to {nxt[1]} by {nxt[2]}")
            why_hi.append(f"चंद्र {HS.PLANET.get(nxt[1], nxt[1])} की ओर शुभ दृष्टि से")
        elif nxt[1] in ("Mars", "Saturn") and nxt[2] in ("conjunct", "square", "opposite"):
            score -= 2
            why.append(f"Moon applies to {nxt[1]} by {nxt[2]}")
            why_hi.append(f"चंद्र {HS.PLANET.get(nxt[1], nxt[1])} की ओर कठिन दृष्टि से")
        if ms >= 13.0:
            score += 1
            why.append("Moon fast")
            why_hi.append("चंद्र तेज़")
        for n in ("Mercury", "Venus"):
            if lon[n][3] < 0:
                score -= 1
                why.append(f"{n} retrograde")
                why_hi.append(f"{HS.PLANET.get(n, n)} वक्री")
        days.append((score, k, _date(jd, tz), why, why_hi, ml))
    best = sorted(days, key=lambda x: (-x[0], x[1]))[:8]
    best.sort(key=lambda x: x[1])
    rows = [[_d(t), WM._s(ml), bi(str(sc)), bi("; ".join(w) or "–", "; ".join(wh) or "–")] for sc, _, t, w, wh, ml in best]
    return {"key": "w_election", "title": bi("Western election: better days in the next 30", "पाश्चात्य मुहूर्त: अगले 30 में बेहतर दिन"),
            "blocks": [table([bi("Date (noon)", "तिथि (दोपहर)"), bi("Moon", "चंद्र"), bi("Score", "अंक"), bi("Why", "कारण")], rows)],
            "note": bi("A general screen by the Moon: waxing, fast, not void of course, applying to Venus or Jupiter and not to Mars or Saturn, with Mercury and Venus direct. "
                       "It does not look at your chart or the purpose; for a wedding or a move use Muhurta as well.",
                       "चंद्र के आधार पर सामान्य छानबीन: बढ़ता हुआ, तेज़, शून्य मार्ग में नहीं, शुक्र या गुरु की ओर और मंगल या शनि की ओर नहीं, बुध और शुक्र मार्गी। "
                       "यह आपकी कुंडली या उद्देश्य नहीं देखता; विवाह या स्थानांतरण के लिए मुहूर्त भी देखें।")}


SOURCES = [("Parashari rules, dashas, vargas, shadbala", "पाराशरी नियम, दशाएँ, वर्ग, षड्बल", "Brihat Parashara Hora Shastra", "बृहत् पाराशर होरा शास्त्र"),
           ("Yogas and results", "योग और फल", "Phaladeepika (Mantreswara); Saravali (Kalyana Varma); Brihat Jataka (Varahamihira)", "फलदीपिका (मंत्रेश्वर); सारावली (कल्याण वर्मा); बृहज्जातक (वराहमिहिर)"),
           ("Chara karakas, arudhas, rashi dashas", "चर कारक, आरूढ़, राशि दशाएँ", "Jaimini Upadesa Sutras", "जैमिनी उपदेश सूत्र"),
           ("Varshaphal and Tajika yogas", "वर्षफल और ताजिक योग", "Tajika Neelakanthi (Neelakantha)", "ताजिक नीलकंठी (नीलकंठ)"),
           ("Muhurta", "मुहूर्त", "Muhurta Chintamani (Rama Daivajna)", "मुहूर्त चिंतामणि (राम दैवज्ञ)"),
           ("KP star and sub lords, horary numbers", "केपी नक्षत्र और उप स्वामी, प्रश्न अंक", "Krishnamurti Padhdhati readers (K. S. Krishnamurti)", "कृष्णमूर्ति पद्धति रीडर (के. एस. कृष्णमूर्ति)"),
           ("Lal Kitab", "लाल किताब", "Lal Kitab (Pt. Roop Chand Joshi, 1939–1952)", "लाल किताब (पं. रूप चंद जोशी, 1939–1952)"),
           ("Western dignities, sect, lots, profections, releasing", "पाश्चात्य ग्रह बल, पक्ष, लॉट, प्रोफ़ेक्शन, रिलीज़िंग", "Tetrabiblos (Ptolemy); Anthology (Vettius Valens); Introduction (Paulus Alexandrinus)", "टेट्राबिब्लोस (टॉलेमी); एंथोलॉजी (वेटियस वैलेन्स); इंट्रोडक्शन (पॉलस)"),
           ("Firdaria", "फ़िरदारिया", "Liber Astronomiae (Guido Bonatti)", "लिबर एस्ट्रोनोमिए (गुइडो बोनाटी)"),
           ("BaZi", "बाज़ी", "Yuan Hai Zi Ping (渊海子平); San Ming Tong Hui (三命通会)", "युआन हाई ज़ी पिंग (渊海子平); सान मिंग तोंग हुई (三命通会)"),
           ("Zi Wei Dou Shu", "ज़ी वेई दो शू", "Zi Wei Dou Shu Quan Shu (紫微斗数全书)", "ज़ी वेई दो शू चुआन शू (紫微斗数全书)"),
           ("Tong Shu day officers", "टोंग शू दिवस अधिकारी", "Xie Ji Bian Fang Shu (协纪辨方书)", "शिए जी बियान फ़ांग शू (协纪辨方书)"),
           ("Flying Stars", "उड़ते तारे", "Shen Shi Xuan Kong Xue (沈氏玄空学)", "शेन शी शुआन कोंग शुए (沈氏玄空学)"),
           ("Chaldean numerology", "कैल्डियन अंक ज्योतिष", "Cheiro's Book of Numbers", "कीरो की 'बुक ऑफ़ नंबर्स'")]


def sources(c):
    rows = [[bi(a, b), bi(x, y)] for a, b, x, y in SOURCES]
    return {"key": "sources", "title": bi("Classical sources", "शास्त्रीय स्रोत"),
            "blocks": [table([bi("Technique", "तकनीक"), bi("Main source", "मुख्य स्रोत")], rows)],
            "note": bi("The books each tradition's rules come from. The app applies the rules; it does not quote the texts.",
                       "वे ग्रंथ जिनसे हर परंपरा के नियम आते हैं। ऐप नियम लागू करता है; ग्रंथों के उद्धरण नहीं देता।")}


# ------------------------------------------------------------------ Western
def house_systems(c):
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    head = [bi("House", "भाव")]
    cols = []
    for code, en, hi in HSYS:
        try:
            cusps = swe.houses(jd, pl["lat"], pl["lon"], code)[0]
        except Exception:
            continue
        head.append(bi(en, hi))
        cols.append(cusps)
    rows = [[bi(str(h + 1))] + [WM._s(cu[h]) for cu in cols] for h in range(12)]
    return {"key": "w_houses", "title": bi("Western: house systems side by side", "पाश्चात्य: भाव पद्धतियाँ साथ-साथ"),
            "blocks": [table(head, rows)],
            "note": bi("Tropical cusps. The reports use Placidus, and Whole sign for the traditional techniques.",
                       "सायन भाव-संधियाँ। रिपोर्ट प्लेसिडस का, और पारंपरिक तकनीकों में पूर्ण राशि का उपयोग करती हैं।")}


def _syzygy(jd, direction):
    """Nearest new or full moon before (direction -1) or after (+1) jd: (jd, 'new'|'full')."""
    def elong(x):
        return (swe.calc_ut(x, swe.MOON)[0][0] - swe.calc_ut(x, swe.SUN)[0][0]) % 360
    e = elong(jd)
    if direction < 0:
        target = 0.0 if e < 180 else 180.0
        x = jd - ((e - target) % 360) / 12.19
    else:
        target = 180.0 if e < 180 else 0.0
        x = jd + ((target - e) % 360) / 12.19
    for _ in range(8):
        diff = (elong(x) - target + 180) % 360 - 180
        x -= diff / 12.19
    return x, ("new" if target == 0.0 else "full")


def lunations(c):
    jd = c["time_pipeline"]["jd_ut"]
    tz = c["time_pipeline"]["utc_offset_hours"]
    now = dt.datetime.fromisoformat(c["meta"]["generated_for_date"])
    jn = swe.julday(now.year, now.month, now.day, 12.0)
    kind = {"new": ("New Moon", "अमावस्या"), "full": ("Full Moon", "पूर्णिमा")}
    px, pk = _syzygy(jd, -1)
    rows = [[bi("Before birth: " + kind[pk][0], "जन्म से पहले: " + kind[pk][1]), _d(_date(px, tz)), WM._s(swe.calc_ut(px, swe.MOON)[0][0])]]
    x = jn
    for _ in range(4):
        x, k = _syzygy(x + 0.5, 1)
        rows.append([bi("Next " + kind[k][0], "अगली " + kind[k][1]), _d(_date(x, tz)), WM._s(swe.calc_ut(x, swe.MOON)[0][0])])
    try:
        se = swe.sol_eclipse_when_glob(jn, swe.FLG_SWIEPH)[1][0]
        le = swe.lun_eclipse_when(jn, swe.FLG_SWIEPH)[1][0]
        rows.append([bi("Next solar eclipse", "अगला सूर्य ग्रहण"), _d(_date(se, tz)), WM._s(swe.calc_ut(se, swe.SUN)[0][0])])
        rows.append([bi("Next lunar eclipse", "अगला चंद्र ग्रहण"), _d(_date(le, tz)), WM._s(swe.calc_ut(le, swe.MOON)[0][0])])
    except Exception:
        pass
    return {"key": "w_lunations", "title": bi("Lunations and eclipses", "अमावस्या, पूर्णिमा और ग्रहण"),
            "blocks": [table([bi("Event", "घटना"), bi("Date", "तिथि"), bi("Moon or Sun at", "चंद्र या सूर्य")], rows)],
            "note": bi("Dates in the birth time zone, tropical zodiac. Eclipses are the next ones anywhere on Earth; whether one is visible depends on where you are.",
                       "तिथियाँ जन्म के समय क्षेत्र में, सायन राशिचक्र। ग्रहण पृथ्वी पर कहीं भी होने वाले अगले ग्रहण हैं; दिखेगा या नहीं, यह स्थान पर निर्भर है।")}


def elements(c):
    w = c["western"]
    e, m = w["element_count"], w["modality_count"]
    top_e, top_m = max(e, key=e.get), max(m, key=m.get)
    low = [k for k, v in e.items() if v == 0]
    return {"key": "w_elements", "title": bi("Western: elements and modalities", "पाश्चात्य: तत्व और गुण"),
            "intro": bi(f"Strongest element {top_e}, strongest modality {top_m}." + (f" No planet in {', '.join(low)}." if low else ""),
                        f"सबसे प्रबल तत्व {EL_HI[top_e]}, सबसे प्रबल गुण {MOD_HI[top_m]}।" + (f" {', '.join(EL_HI[x] for x in low)} में कोई ग्रह नहीं।" if low else "")),
            "blocks": [table([bi("Element", "तत्व"), bi("Points", "अंक")], [[bi(k, EL_HI[k]), bi(str(v))] for k, v in e.items()]),
                       table([bi("Modality", "गुण"), bi("Points", "अंक")], [[bi(k, MOD_HI[k]), bi(str(v))] for k, v in m.items()])],
            "note": bi("Ten planets plus the Ascendant, one point each.", "दस ग्रह और लग्न, प्रत्येक का एक अंक।")}


def midpoints(c, pos, asc, mc):
    pts = {p: pos[p]["lon"] for p in WM.TEN}
    pts["ASC"], pts["MC"] = asc, mc
    hi = lambda n: HS.PLANET.get(n) or WM.WB_HI.get(n) or {"ASC": "लग्न", "MC": "दशम"}[n]   # noqa: E731
    en = lambda n: {"ASC": "Ascendant", "MC": "Midheaven"}.get(n, n)                         # noqa: E731
    names = list(pts)
    found = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = (pts[b] - pts[a]) % 360
            mid = (pts[a] + (d if d <= 180 else d - 360) / 2) % 360
            for p in names:
                if p in (a, b):
                    continue
                for ang, lab, lh in ((0, "on", "पर"), (180, "opposite", "के सामने")):
                    orb = abs((pts[p] - mid - ang + 180) % 360 - 180)
                    if orb <= 1.0:
                        found.append((orb, bi(f"{en(p)} {lab} {en(a)}/{en(b)}", f"{hi(p)}, {hi(a)}/{hi(b)} {lh}"), bi(f"{orb:.1f}°")))
    found.sort(key=lambda x: x[0])
    key = [("Sun", "Moon"), ("ASC", "MC"), ("Venus", "Mars"), ("Sun", "ASC"), ("Moon", "ASC"), ("Jupiter", "Saturn")]
    rows = []
    for a, b in key:
        d = (pts[b] - pts[a]) % 360
        rows.append([bi(f"{en(a)}/{en(b)}", f"{hi(a)}/{hi(b)}"), WM._s((pts[a] + (d if d <= 180 else d - 360) / 2) % 360)])
    return {"key": "w_midpoints", "title": bi("Western: midpoints", "पाश्चात्य: मध्यबिंदु"),
            "blocks": [table([bi("Midpoint", "मध्यबिंदु"), bi("At", "स्थान")], rows),
                       para(bi("Planets on a midpoint (within 1°):", "मध्यबिंदु पर ग्रह (1° के भीतर):")),
                       table([bi("Planet and midpoint", "ग्रह और मध्यबिंदु"), bi("Orb", "अंतर")], [[t, o] for _, t, o in found[:14]]) if found else
                       para(bi("None within 1°.", "1° के भीतर कोई नहीं।"))],
            "note": bi("The nearer midpoint of each pair; a planet on or opposite it within 1° is listed.", "हर जोड़ी का निकटतम मध्यबिंदु; 1° के भीतर उस पर या उसके सामने का ग्रह दिखाया गया है।")}


def harmonics(c, pos, jd):
    hs = (4, 5, 7, 9, 12)
    rows = [[WM._p(p)] + [WM._s(pos[p]["lon"] * h) for h in hs] for p in WM.TEN]
    out = [{"key": "w_harmonics", "title": bi("Western: harmonic charts", "पाश्चात्य: हार्मोनिक कुंडलियाँ"),
            "blocks": [table([bi("Planet", "ग्रह")] + [bi(f"H{h}") for h in hs], rows)],
            "note": bi("Each harmonic multiplies the tropical longitude by its number. H9 matches the navamsa idea; H5 and H7 are used for talent and inspiration.",
                       "हर हार्मोनिक सायन देशांतर को अपनी संख्या से गुणा करता है। H9 नवांश जैसा है; H5 और H7 प्रतिभा और प्रेरणा के लिए देखे जाते हैं।")}]
    modes = [("Fagan-Bradley", "फ़ेगन-ब्रैडली", swe.SIDM_FAGAN_BRADLEY), ("Lahiri", "लाहिड़ी", swe.SIDM_LAHIRI),
             ("Krishnamurti", "कृष्णमूर्ति", swe.SIDM_KRISHNAMURTI), ("Raman", "रमन", swe.SIDM_RAMAN), ("De Luce", "डी लूस", swe.SIDM_DELUCE)]
    ay = []
    for _, _, m in modes:
        swe.set_sid_mode(m)
        ay.append(swe.get_ayanamsa_ut(jd))
    rows = [[WM._p(p)] + [WM._s(pos[p]["lon"] - a) for a in ay] for p in WM.TEN]
    out.append({"key": "w_sidereal", "title": bi("Western: sidereal presets", "पाश्चात्य: निरयण विकल्प"),
                "blocks": [table([bi("Planet", "ग्रह")] + [bi(f"{e} ({a:.2f}°)", f"{h} ({a:.2f}°)") for (e, h, _), a in zip(modes, ay)], rows)],
                "note": bi("The same planets under five sidereal zodiacs; the number is each ayanamsa at birth.",
                           "वही ग्रह पाँच निरयण राशिचक्रों में; संख्या जन्म के समय का अयनांश है।")})
    return out


def sect(c, pos, day):
    sun = pos["Sun"]["lon"]
    diurnal, nocturnal = ("Sun", "Jupiter", "Saturn"), ("Moon", "Venus", "Mars")
    rows = []
    for p in WM.SEVEN:
        lon = pos[p]["lon"]
        if p == "Mercury":
            team = "day" if (lon - sun) % 360 > 180 else "night"       # rising before the Sun = of the day sect
        else:
            team = "day" if p in diurnal else "night"
        insect = (team == "day") == day
        d = abs((lon - sun + 180) % 360 - 180)
        if p == "Sun":
            cond = bi("–")
        elif d <= 0.2833:
            cond = bi("in the heart of the Sun (within 17')", "सूर्य के हृदय में (17' के भीतर)")
        elif d <= 8.5:
            cond = bi("combust (within 8.5°)", "अस्त (8.5° के भीतर)")
        elif d <= 17:
            cond = bi("under the beams (within 17°)", "किरणों के नीचे (17° के भीतर)")
        else:
            cond = bi("clear of the Sun", "सूर्य से दूर")
        if p in ("Sun", "Moon"):
            phase = bi("–")
        else:
            phase = bi("rises before the Sun", "सूर्य से पहले उदय") if (lon - sun) % 360 > 180 else bi("sets after the Sun", "सूर्य के बाद अस्त")
        sp = pos[p]["speed"]
        motion = bi("retrograde", "वक्री") if sp < 0 else bi("direct", "मार्गी")
        rows.append([WM._p(p), bi("day", "दिन") if team == "day" else bi("night", "रात्रि"),
                     bi("in sect", "पक्ष में") if insect else bi("out of sect", "पक्ष से बाहर"), cond, phase, motion])
    return {"key": "w_sect", "title": bi("Western: sect and planetary condition", "पाश्चात्य: पक्ष और ग्रह स्थिति"),
            "intro": bi("This is a day chart: the Sun, Jupiter and Saturn lead." if day else "This is a night chart: the Moon, Venus and Mars lead.",
                        "यह दिन की कुंडली है: सूर्य, गुरु और शनि अग्रणी हैं।" if day else "यह रात्रि की कुंडली है: चंद्र, शुक्र और मंगल अग्रणी हैं।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Sect", "पक्ष"), bi("In this chart", "इस कुंडली में"), bi("Nearness to the Sun", "सूर्य से निकटता"),
                              bi("Phase", "अवस्था"), bi("Motion", "गति")], rows)],
            "note": bi("Hellenistic sect: Mercury joins the day sect when it rises before the Sun. Orbs for the Sun's beams follow the usual 17' / 8.5° / 17°.",
                       "हेलेनिस्टिक पक्ष: बुध सूर्य से पहले उदय हो तो दिन के पक्ष में। सूर्य की किरणों के अंतर सामान्य 17' / 8.5° / 17° हैं।")}


def ingresses(c):
    pl = c["meta"]["place"]
    tz = c["time_pipeline"]["utc_offset_hours"]
    year = dt.datetime.fromisoformat(c["meta"]["generated_for_date"]).year
    names = [("Aries (spring)", "मेष (वसंत)"), ("Cancer (summer)", "कर्क (ग्रीष्म)"), ("Libra (autumn)", "तुला (शरद)"), ("Capricorn (winter)", "मकर (शीत)")]
    rows = []
    for k, (en, hi) in enumerate(names):
        jd = swe.solcross_ut(90.0 * k, swe.julday(year, 1, 1, 0.0), swe.FLG_SWIEPH)
        asc = swe.houses(jd, pl["lat"], pl["lon"], b"P")[1][0]
        rows.append([bi(en, hi), _d(_date(jd, tz)), bi(_date(jd, tz).strftime("%H:%M")), WM._s(asc), WM._s(swe.calc_ut(jd, swe.MOON)[0][0])])
    return {"key": "w_ingresses", "title": bi(f"Mundane: the four ingresses of {year}", f"मुंडेन: {year} के चार प्रवेश"),
            "blocks": [table([bi("Sun enters", "सूर्य प्रवेश"), bi("Date", "तिथि"), bi("Time", "समय"), bi("Ascendant at the birthplace", "जन्मस्थान पर लग्न"),
                              bi("Moon", "चंद्र")], rows)],
            "note": bi("The seasonal charts used in mundane astrology, in the birth time zone. The Aries ingress has its own section with all planets.",
                       "मुंडेन ज्योतिष की ऋतु कुंडलियाँ, जन्म के समय क्षेत्र में। मेष प्रवेश का सभी ग्रहों वाला अलग खंड है।")}


# ------------------------------------------------------------------ BaZi
def bazi_elements(b):
    vis, hid = b["element_balance_visible_8"], b["element_balance_with_hidden_stems"]
    rows = [[bi(e, EL_HI[e]), bi(str(vis.get(e, 0))), bi(f"{hid.get(e, 0):g}")] for e in ELS]
    h = b["day_master_strength_heuristic"]
    ch = h["month_season_status"][:1]
    se, sh = SEASON.get(ch, ("–", "–"))
    dm = b["day_master"]
    miss = b.get("missing_elements_visible") or []
    blocks = [table([bi("Element", "तत्व"), bi("Visible in the 8 characters", "8 अक्षरों में दृश्य"), bi("With hidden stems (weighted)", "छिपे तनों सहित (भारित)")], rows),
              para(bi(f"Seasonal strength of the Day Master ({dm['stem']} {dm['element']}): {ch}, {se}. Support {h['supporters']:g} against drain {h['drainers']:g}.",
                      f"दिवस स्वामी ({dm['stem']} {EL_HI[dm['element']]}) का ऋतु बल: {ch}, {sh}। सहारा {h['supporters']:g}, खर्च {h['drainers']:g}।"))]
    if miss:
        blocks.append(para(bi("Not visible in the chart: " + ", ".join(miss) + ".", "कुंडली में दृश्य नहीं: " + ", ".join(EL_HI.get(x, x) for x in miss) + "।")))
    return {"key": "bazi_elements", "title": bi("BaZi: five elements and seasonal strength", "बाज़ी: पंचतत्व और ऋतु बल"), "blocks": blocks,
            "note": bi("Season by the five-state table (旺相休囚死) from the month branch; hidden stems weighted main 1, middle 0.5, residual 0.3. A screen, not a full structure judgement.",
                       "ऋतु माह शाखा से पाँच अवस्थाओं की तालिका (旺相休囚死) के अनुसार; छिपे तने मुख्य 1, मध्य 0.5, शेष 0.3 भार से। यह एक छानबीन है, पूर्ण संरचना निर्णय नहीं।")}


def _rel_rows(lst):
    return [[bi(r["type"], _rel_hi(r["type"])), bi(" – ".join(r["between"]), _where_hi(" – ".join(r["between"])))] for r in lst]


def bazi_relations_natal(b):
    it = b["interactions"]
    groups = (("Within the birth chart", "जन्म कुंडली के भीतर", it.get("natal_branches", []) + it.get("natal_stems", [])),
              ("Current luck pillar with the chart", "वर्तमान दशा स्तंभ और कुंडली", it.get("luck_pillar_vs_natal", [])),
              ("This year's pillar with the chart", "इस वर्ष का स्तंभ और कुंडली", it.get("annual_pillar_vs_natal", [])))
    blocks = []
    for en, hi, lst in groups:
        blocks.append(para(bi(en + ":", hi + ":")))
        blocks.append(table([bi("Relation", "संबंध"), bi("Between", "किनके बीच")], _rel_rows(lst)) if lst else para(bi("None.", "कोई नहीं।")))
    return {"key": "bazi_relations", "title": bi("BaZi: combinations and clashes", "बाज़ी: संयोग और टकराव"), "blocks": blocks,
            "note": bi("Six harmonies, three harmonies and meetings, clashes, harms, destructions, punishments and stem combinations.",
                       "छह सामंजस्य, त्रि-सामंजस्य और मिलन, टकराव, बाधा, विघ्न, दंड और तना संयोग।")}


def bazi_cycles(b, c):
    dm = CH.STEMS.index(b["day_master"]["stem"])
    year = b.get("current_annual_year") or dt.datetime.fromisoformat(c["meta"]["generated_for_date"]).year
    ys = (year - 4) % 10
    tz = c["time_pipeline"]["utc_offset_hours"]
    rows = []
    first = (ys % 5) * 2 + 2                     # stem of the Yin month (five tigers rule)
    for k in range(12):
        jd = swe.solcross_ut((315 + 30 * k) % 360, swe.julday(year, 1, 20, 0.0) + 30.4 * k - 5, swe.FLG_SWIEPH)
        s, br = (first + k) % 10, (2 + k) % 12
        tg = CH.ten_god(dm, s)
        rows.append([_d(_date(jd, tz)), bi(CH.STEMS[s] + CH.BRANCHES[br]), bi(f"{CH.STEM_PY[s]}-{CH.BRANCH_PY[br]}", f"{STEM_HI[s]}-{BRANCH_HI[br]}"),
                     bi(ELS[CH.STEM_EL[s]], EL_HI[ELS[CH.STEM_EL[s]]]), bi(tg, tg.split("(")[-1].rstrip(")") if "(" in tg else tg)])
    ap = next((x for x in b.get("annual_pillars", []) if x.get("year") == year), None)
    intro = bi(f"Year pillar {year}: {ap['text']} ({ap['pinyin']}).", f"{year} का वर्ष स्तंभ: {ap['text']}।") if ap else None
    s = {"key": "bazi_cycles", "title": bi(f"BaZi: the months of {year}", f"बाज़ी: {year} के माह"),
         "blocks": [table([bi("Starts", "आरंभ"), bi("Pillar", "स्तंभ"), bi("Reading", "उच्चारण"), bi("Stem element", "तना तत्व"), bi("Ten God to you", "आपके लिए दश देव")], rows)],
         "note": bi("Each month starts at its solar term (jie); stems by the five tigers rule.", "हर माह अपने सौर पद (जिए) से आरंभ होता है; तने 'पाँच बाघ' नियम से।")}
    if intro:
        s["intro"] = intro
    return s


def bazi_hours(b):
    """All twelve possible hour pillars, for a chart whose birth time is unknown."""
    ds = CH.STEMS.index(b["pillars"]["day"]["stem"])
    first = (ds % 5) * 2                          # stem of the Zi hour (five rats rule)
    dm = ds
    rows = []
    for k in range(12):
        s = (first + k) % 10
        tg = CH.ten_god(dm, s)
        rows.append([bi(f"{(23 + 2 * k) % 24:02d}:00–{(1 + 2 * k) % 24:02d}:00"), bi(CH.STEMS[s] + CH.BRANCHES[k]),
                     bi(f"{CH.STEM_PY[s]}-{CH.BRANCH_PY[k]}", f"{STEM_HI[s]}-{BRANCH_HI[k]}"), bi(tg, tg.split("(")[-1].rstrip(")") if "(" in tg else tg)])
    return {"key": "bazi_hours", "title": bi("BaZi: possible hour pillars", "बाज़ी: संभावित घड़ी स्तंभ"),
            "intro": bi("The birth time is not known, so the hour pillar is left out of the reading. These are the twelve it could be.",
                        "जन्म समय ज्ञात नहीं, इसलिए घड़ी स्तंभ फलादेश में नहीं लिया गया। ये बारह संभावित स्तंभ हैं।"),
            "blocks": [table([bi("Solar time", "सौर समय"), bi("Pillar", "स्तंभ"), bi("Reading", "उच्चारण"), bi("Ten God", "दश देव")], rows)],
            "note": bi("Hour stems by the five rats rule from the day stem.", "घड़ी के तने दिवस तने से 'पाँच चूहे' नियम द्वारा।")}


def bazi_cross(m):
    """Milan: every relation between the two people's pillars (from chart_engine's bazi_cross)."""
    x = m.get("bazi_cross")
    if not x:
        return None
    people = (m.get("people") or ["A", "B"]) + ["A", "B"]
    na, nb = people[0].split()[0], people[1].split()[0]

    def who(s):
        return s.replace("A-", na + " ").replace("B-", nb + " ")
    lst = x.get("branch_relations", []) + x.get("stem_relations", [])
    rows = [[bi(r["type"], _rel_hi(r["type"])), bi(who(" – ".join(r["between"])), _where_hi(who(" – ".join(r["between"]))))] for r in lst]
    ya = x.get("year_animals") or {}
    blocks = []
    if ya:
        blocks.append(para(bi(f"Year animals: {na} {ya.get('A')}, {nb} {ya.get('B')}.",
                              f"वर्ष पशु: {na} {HS_ANIMAL.get(ya.get('A'), ya.get('A'))}, {nb} {HS_ANIMAL.get(ya.get('B'), ya.get('B'))}।")))
    blocks.append(table([bi("Relation", "संबंध"), bi("Between", "किनके बीच")], rows) if rows else
                  para(bi("No direct combinations or clashes between the two charts.", "दोनों कुंडलियों के बीच कोई सीधा संयोग या टकराव नहीं।")))
    return {"key": "bazi_cross", "title": bi("BaZi: relations between the two charts", "बाज़ी: दोनों कुंडलियों के बीच संबंध"), "blocks": blocks,
            "note": bi("All pillars of one chart against all pillars of the other.", "एक कुंडली के सभी स्तंभ दूसरी के सभी स्तंभों के साथ।")}


HS_ANIMAL = dict(zip(["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"], ANIMAL_HI))


# ------------------------------------------------------------------ numerology
def numerology_working(c):
    d0 = c["time_pipeline"]["local_civil"][:10]
    y, m, d = [int(x) for x in d0.split("-")]
    n = c["numerology"]

    def chain(v):
        steps = [str(v)]
        while v > 9 and v not in (11, 22, 33):
            v = sum(int(ch) for ch in str(v))
            steps.append(str(v))
        return " → ".join(steps), v
    cd, rd = chain(d)
    cm, rm = chain(m)
    cy, ry = chain(sum(int(ch) for ch in str(y)))
    cl, lp = chain(rd + rm + ry)
    py = n["pythagorean"]
    ce, _ = chain(py["destiny_raw_total"])
    rows = [[bi("Day", "दिन"), bi(f"{d}: {cd}")], [bi("Month", "माह"), bi(f"{m}: {cm}")],
            [bi("Year", "वर्ष"), bi(f"{y}: {'+'.join(str(y))} = {cy}")],
            [bi("Life Path", "जीवन पथ"), bi(f"{rd} + {rm} + {ry} = {cl}")],
            [bi("Name total (Pythagorean)", "नाम योग (पाइथागोरस)"), bi(ce)],
            [bi("Name compound (Chaldean)", "नाम यौगिक (कैल्डियन)"), bi(f"{n['chaldean']['compound_number']} → {n['chaldean']['single_digit']}")]]
    s = lambda v: num.reduce(v, False)[0]        # noqa: E731
    r = lambda v: num.reduce(v)[0]               # noqa: E731
    a, b_, yy = r(m), r(d), r(y)
    p = [r(a + b_), r(b_ + yy)]
    p += [r(p[0] + p[1]), r(a + yy)]
    ch = [abs(s(a) - s(b_)), abs(s(b_) - s(yy))]
    ch += [abs(ch[0] - ch[1]), abs(s(a) - s(yy))]
    e1 = 36 - s(r(a + b_ + yy))
    ages = [(0, e1), (e1 + 1, e1 + 9), (e1 + 10, e1 + 18), (e1 + 19, None)]
    prow = [[bi(str(k + 1)), bi(f"{x}–{z}" if z is not None else f"{x}+"), bi(str(p[k])), bi(str(ch[k]))] for k, (x, z) in enumerate(ages)]
    return {"key": "num_working", "title": bi("Numerology: working, pinnacles and challenges", "अंक ज्योतिष: गणना, शिखर और चुनौतियाँ"),
            "blocks": [table([bi("Number", "अंक"), bi("Working", "गणना")], rows),
                       para(bi("Pinnacles and challenges by age:", "आयु के अनुसार शिखर और चुनौतियाँ:")),
                       table([bi("Stage", "चरण"), bi("Age", "आयु"), bi("Pinnacle", "शिखर"), bi("Challenge", "चुनौती")], prow)],
            "note": bi("Each number is reduced by adding its digits; 11, 22 and 33 are kept. The first pinnacle ends at 36 minus the Life Path, then 9-year stages.",
                       "हर संख्या अंकों को जोड़कर घटाई जाती है; 11, 22 और 33 रखे जाते हैं। पहला शिखर 36 में से जीवन पथ घटाकर समाप्त होता है, फिर 9-9 वर्ष के चरण।")}


# ------------------------------------------------------------------ Chinese screen
def chinese_sections(date_iso, today_iso, tz_hours):
    today = dt.date.fromisoformat(today_iso)
    birth = dt.date.fromisoformat(date_iso)
    rows = []
    for k, (zh, py, en, hi) in enumerate(TERMS):
        deg = (315 + 15 * k) % 360
        jd = swe.solcross_ut(deg, swe.julday(today.year, 1, 1, 0.0) + (0 if k < 22 else -30), swe.FLG_SWIEPH)
        if k >= 22 and _date(jd, tz_hours).year < today.year:
            jd = swe.solcross_ut(deg, swe.julday(today.year, 12, 25, 0.0), swe.FLG_SWIEPH)
        t = _date(jd, tz_hours)
        rows.append((t, [bi(f"{zh} {py}", f"{zh}"), bi(en, hi), _d(t), bi("month start (jie)", "माह आरंभ (जिए)") if k % 2 == 0 else bi("mid-month (qi)", "मध्य माह (ची)")]))
    rows.sort(key=lambda x: x[0])
    secs = [{"key": "cn_terms", "title": bi(f"The 24 solar terms of {today.year}", f"{today.year} के 24 सौर पद"),
             "blocks": [table([bi("Term", "पद"), bi("Meaning", "अर्थ"), bi("Date", "तिथि"), bi("Role", "भूमिका")], [r for _, r in rows])],
             "note": bi("Each term is the instant the Sun reaches a multiple of 15°. BaZi months start at the jie terms; the year starts at Li Chun.",
                        "हर पद वह क्षण है जब सूर्य 15° के गुणज पर पहुँचता है। बाज़ी के माह जिए पदों से और वर्ष ली चुन से शुरू होता है।")}]
    stems = [[bi(CH.STEMS[i]), bi(CH.STEM_PY[i], STEM_HI[i]), bi(ELS[CH.STEM_EL[i]], EL_HI[ELS[CH.STEM_EL[i]]]),
              bi("Yang" if i % 2 == 0 else "Yin", "यांग" if i % 2 == 0 else "यिन")] for i in range(10)]
    animals = list(HS_ANIMAL)
    branches = [[bi(CH.BRANCHES[i]), bi(CH.BRANCH_PY[i], BRANCH_HI[i]), bi(animals[i], ANIMAL_HI[i]), bi(ELS[CH.BRANCH_EL[i]], EL_HI[ELS[CH.BRANCH_EL[i]]]),
                 bi(f"{(23 + 2 * i) % 24:02d}–{(1 + 2 * i) % 24:02d}")] for i in range(12)]
    secs.append({"key": "cn_glossary", "title": bi("Glossary: stems and branches", "शब्दावली: तने और शाखाएँ"),
                 "blocks": [table([bi("Stem", "तना"), bi("Reading", "उच्चारण"), bi("Element", "तत्व"), bi("Polarity", "ध्रुवता")], stems),
                            table([bi("Branch", "शाखा"), bi("Reading", "उच्चारण"), bi("Animal", "पशु"), bi("Element", "तत्व"), bi("Hours", "घंटे")], branches)],
                 "note": bi("Ten heavenly stems and twelve earthly branches pair into the cycle of sixty.", "दस स्वर्गीय तने और बारह पार्थिव शाखाएँ मिलकर साठ का चक्र बनाते हैं।")})
    real = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    secs.append({"key": "cn_age", "title": bi("Age conventions", "आयु की परंपराएँ"),
                 "blocks": [table([bi("Convention", "परंपरा"), bi("Age now", "अभी आयु")],
                                  [[bi("Real age (周岁): full years since birth", "वास्तविक आयु (周岁): जन्म से पूरे वर्ष"), bi(str(real))],
                                   [bi("Nominal age (虚岁): 1 at birth, one more at each New Year", "पारंपरिक आयु (虚岁): जन्म पर 1, हर नववर्ष पर एक और"),
                                    bi(str(_nominal(birth, today)))]])],
                 "note": bi("Luck pillars and Zi Wei periods count in nominal age; modern readings often quote real age.",
                            "दशा स्तंभ और ज़ी वेई की अवधियाँ पारंपरिक आयु में गिनी जाती हैं; आधुनिक फलादेश प्रायः वास्तविक आयु बताते हैं।")})
    return secs


def _nominal(birth, today):
    import chinese_calendar as CC
    return CC.to_lunar(today)["year"] - CC.to_lunar(birth)["year"] + 1


# ------------------------------------------------------------------ entry points
def build(c):
    secs = []

    def add(f, *a):
        try:
            r = f(*a)
        except Exception:
            return
        if isinstance(r, list):
            secs.extend(r)
        elif r:
            secs.append(r)
    add(time_details, c)
    if c.get("western"):
        jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
        pos = WM._positions(jd)
        ascmc = swe.houses(jd, pl["lat"], pl["lon"], b"P")[1]
        asc, mc = ascmc[0], ascmc[1]
        day = ((pos["Sun"]["lon"] - asc) % 360) > 180
        add(elements, c)
        add(sect, c, pos, day)
        add(midpoints, c, pos, asc, mc)
        add(harmonics, c, pos, jd)
        add(house_systems, c)
        add(lunations, c)
        add(ingresses, c)
        add(election, c)
        add(relocation, c, pos)
    b = c.get("bazi")
    if b:
        add(bazi_elements, b)
        add(bazi_relations_natal, b)
        add(bazi_cycles, b, c)
        if c["meta"].get("birth_time_confidence") == "unknown":
            add(bazi_hours, b)
    if c.get("numerology"):
        add(numerology_working, c)
    if c.get("vedic"):
        add(settings_compare, c)
    add(sources, c)
    add(versions, c)
    return secs
