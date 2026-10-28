"""app_details.py - the chart details the engine computes but the main screens do not show, as display-ready sections.

Each section is {"key", "title", "intro"?, "blocks": [...], "note"?}; every text is {"en": ..., "hi": ...}; a block is a
table {"type": "table", "head": [...], "rows": [[...]]}, a paragraph {"type": "para", "text": ...} or a list
{"type": "list", "items": [...]}. The app draws them with one generic renderer and the full reading reuses them.

Sections: birth panchang, divisional charts (D9, D10: data for drawing), Ashtakavarga, Yogini dasha, Jaimini,
Varshaphal (Tajika year chart), Lal Kitab, KP, Western timing (progressions, solar return, lots, profection,
zodiacal releasing).

Lal Kitab's book texts sometimes describe death, illness and the like for a placement; the app never shows those
(house rule), so every Lal Kitab sentence passes safe() and any sentence with such a word is left out.
"""
import re

import hindi_shell as HS

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN = NINE[:7]
MON_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MON_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
TITHI = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
         "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi"]
TITHI_HI = ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी",
            "त्रयोदशी", "चतुर्दशी"]
YOGA_HI = {"Vishkambha": "विष्कुंभ", "Priti": "प्रीति", "Ayushman": "आयुष्मान", "Saubhagya": "सौभाग्य", "Shobhana": "शोभन",
           "Atiganda": "अतिगंड", "Sukarma": "सुकर्मा", "Dhriti": "धृति", "Shula": "शूल", "Ganda": "गंड", "Vriddhi": "वृद्धि",
           "Dhruva": "ध्रुव", "Vyaghata": "व्याघात", "Harshana": "हर्षण", "Vajra": "वज्र", "Siddhi": "सिद्धि", "Vyatipata": "व्यतीपात",
           "Variyana": "वरीयान", "Parigha": "परिघ", "Shiva": "शिव", "Siddha": "सिद्ध", "Sadhya": "साध्य", "Shubha": "शुभ",
           "Shukla": "शुक्ल", "Brahma": "ब्रह्म", "Indra": "इंद्र", "Vaidhriti": "वैधृति"}
KARANA_HI = {"Bava": "बव", "Balava": "बालव", "Kaulava": "कौलव", "Taitila": "तैतिल", "Gara": "गर", "Vanija": "वणिज",
             "Vishti (Bhadra)": "विष्टि (भद्रा)", "Kimstughna": "किंस्तुघ्न", "Shakuni": "शकुनि", "Chatushpada": "चतुष्पद", "Naga": "नाग"}
WEEKDAY_HI = {"Sunday": "रविवार", "Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार", "Thursday": "गुरुवार",
              "Friday": "शुक्रवार", "Saturday": "शनिवार"}
KARAKA = {"Atmakaraka": ("Atmakaraka", "आत्मकारक", "the self and the soul's aim", "आत्मा और जीवन का लक्ष्य"),
          "Amatyakaraka": ("Amatyakaraka", "अमात्यकारक", "career and advisers", "करियर और सलाहकार"),
          "Bhratrikaraka": ("Bhratrikaraka", "भ्रातृकारक", "siblings and courage", "भाई-बहन और साहस"),
          "Matrikaraka": ("Matrikaraka", "मातृकारक", "mother and home", "माता और घर"),
          "Putrakaraka": ("Putrakaraka", "पुत्रकारक", "children and creativity", "संतान और रचनात्मकता"),
          "Gnatikaraka": ("Gnatikaraka", "ज्ञातिकारक", "rivals and obstacles", "प्रतिद्वंद्वी और बाधाएँ"),
          "Darakaraka": ("Darakaraka", "दारकारक", "the spouse", "जीवनसाथी")}
YOGINI_HI = getattr(HS, "YOGINI", {})
W_HI = {"Uranus": "यूरेनस", "Neptune": "नेप्च्यून", "Pluto": "प्लूटो", "North Node": "उत्तर नोड"}
_EN_BAD = (r"death|die[sd]?|dying|dead|disease[sd]?|ill|illness|sick|sickness|divorce[sd]?|accident[s]?|surgery|widow(?:ed|hood)?|"
           r"childless|barren|poverty|ruin(?:ed|s)?|jail|prison|blind(?:ness)?|suicide|murder|poison(?:ed)?|lep(?:er|ers|rosy)|insan(?:e|ity)|mad")
_HI_BAD = r"मृत्यु|मौत|मरना|मर जा|तलाक|रोग|बीमार|विधवा|अंधा|अंधे|कोढ़|ज़हर|जहर|कैद|जेल|पागल|बर्बाद|निःसंतान|बे-औलाद|बेऔलाद"
# English: whole words, any case, but "cancer" only in lower case so the sign Cancer passes.
# Hindi: the word must start a word (so प्रोग्रेस्ड, which contains the letters of रोग, passes).
UNSAFE = re.compile(r"(?i:\b(?:" + _EN_BAD + r")\b)|\bcancer\b|(?<![\u0900-\u097F])(?:" + _HI_BAD + r")")


def bi(en, hi=None):
    return {"en": str(en), "hi": str(en if hi is None else hi)}


def P(p):
    return bi(p, HS.PLANET.get(p, W_HI.get(p, p)))


def S(s):
    return bi(s, HS.SIGN.get(s, s))


def date(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return bi(f"{d} {MON_EN[m - 1]} {y}", f"{d} {MON_HI[m - 1]} {y}")


def month(iso):
    y, m = int(iso[:4]), int(iso[5:7])
    return bi(f"{MON_EN[m - 1]} {y}", f"{MON_HI[m - 1]} {y}")


def span(a, b):
    x, y = month(a), month(b)
    return bi(f"{x['en']} – {y['en']}", f"{x['hi']} – {y['hi']}")


def pos(text):
    """'7°35'13" Leo' -> bi('Leo 7°35′', 'सिंह 7°35′')."""
    m = re.match(r"(\d+)°(\d+)'[^ ]*\s+(\w+)", text or "")
    if not m:
        return bi(text or "–")
    d, mi, sg = m.groups()
    return bi(f"{sg} {d}°{mi}′", f"{HS.SIGN.get(sg, sg)} {d}°{mi}′")


def join(items, sep=", "):
    return bi(sep.join(i["en"] for i in items), sep.join(i["hi"] for i in items))


def table(head, rows):
    return {"type": "table", "head": head, "rows": rows}


def para(text):
    return {"type": "para", "text": text}


def items(lst):
    return {"type": "list", "items": lst}


def safe(text):
    """Drop every sentence that names death, illness, divorce or similar (house rule for anything the app shows)."""
    parts = re.split(r"(?<=[.;!?।])\s+", text or "")
    return " ".join(p for p in parts if p and not UNSAFE.search(p)).strip()


def house_word(h):
    return bi(f"house {h}", f"भाव {h}")


# ------------------------------------------------------------------ sections
def panchang(v):
    pc = v["panchang"]
    t = pc["tithi_number_1_30"]
    pk = "Shukla" if t <= 15 else "Krishna"
    n = t if t <= 15 else t - 15
    if n == 15:
        tn = bi("Purnima" if pk == "Shukla" else "Amavasya", "पूर्णिमा" if pk == "Shukla" else "अमावस्या")
    else:
        tn = bi(TITHI[n - 1], TITHI_HI[n - 1])
    pk_b = bi(f"{pk} paksha", "शुक्ल पक्ष" if pk == "Shukla" else "कृष्ण पक्ष")
    moon = v["planets"]["Moon"]
    rows = [[bi("Tithi", "तिथि"), bi(f"{tn['en']} ({pk_b['en']}, tithi {t} of 30)", f"{tn['hi']} ({pk_b['hi']}, 30 में से {t}वीं तिथि)")],
            [bi("Nakshatra (Moon)", "नक्षत्र (चंद्र)"), bi(f"{moon['nakshatra']}, pada {moon['pada']}", f"{HS.NAK.get(moon['nakshatra'], moon['nakshatra'])}, पद {moon['pada']}")],
            [bi("Yoga", "योग"), bi(pc["yoga"], YOGA_HI.get(pc["yoga"], pc["yoga"]))],
            [bi("Karana", "करण"), bi(pc["karana"], KARANA_HI.get(pc["karana"], pc["karana"]))],
            [bi("Weekday (vara)", "वार"), bi(f"{pc['vara']} (lord {pc['vara_lord']})", f"{WEEKDAY_HI.get(pc['vara'], pc['vara'])} (स्वामी {HS.PLANET.get(pc['vara_lord'], pc['vara_lord'])})")],
            [bi("Sunrise", "सूर्योदय"), bi(pc["sunrise_local"][11:16])]]
    note = bi("The Vedic day runs from sunrise to sunrise" + ("; this birth was before sunrise, so the previous weekday applies." if pc.get("born_before_sunrise") else "."),
              "वैदिक दिन सूर्योदय से सूर्योदय तक चलता है" + ("; यह जन्म सूर्योदय से पहले हुआ, इसलिए पिछला वार लागू है।" if pc.get("born_before_sunrise") else "।"))
    return {"key": "panchang", "title": bi("Birth panchang", "जन्म पंचांग"), "blocks": [table([bi("Element", "अंग"), bi("At birth", "जन्म के समय")], rows)], "note": note}


def ashtakavarga(v):
    av = v["ashtakavarga"]
    lag = SIGNS.index(v["lagna"]["sign"])
    order = [SIGNS[(lag + h) % 12] for h in range(12)]
    head = [bi("Planet", "ग्रह")] + [bi(str(h + 1)) for h in range(12)]
    rows = [[P(p)] + [bi(str(av["bhinna"][p][s])) for s in order] for p in SEVEN if p in av["bhinna"]]
    rows.append([bi("Total (SAV)", "कुल (सर्व)")] + [bi(str(av["sarva"][s])) for s in order])
    strong = [str(h + 1) for h, s in enumerate(order) if av["sarva"][s] >= 28]
    weak = [str(h + 1) for h, s in enumerate(order) if av["sarva"][s] < 25]
    intro = bi("Points each planet gives to each house (columns are houses from the lagna). A house total of 28 or more is above average; under 25 asks for more effort.",
               "हर ग्रह हर भाव को कितने अंक देता है (स्तंभ लग्न से भाव हैं)। किसी भाव का कुल 28 या अधिक औसत से ऊपर है; 25 से कम अधिक प्रयास माँगता है।")
    summ = bi(f"Strong houses: {', '.join(strong) or 'none'}. Houses needing effort: {', '.join(weak) or 'none'}. Grand total {av['sarva_total']} (always 337).",
              f"बलवान भाव: {', '.join(strong) or 'कोई नहीं'}। प्रयास माँगने वाले भाव: {', '.join(weak) or 'कोई नहीं'}। कुल योग {av['sarva_total']} (सदा 337)।")
    return {"key": "ashtakavarga", "title": bi("Ashtakavarga", "अष्टकवर्ग"), "intro": intro, "blocks": [table(head, rows), para(summ)]}


def yogini(v, now):
    y = v["dashas"]["yogini"]
    cur = y["current"]
    def nm(d):
        return bi(f"{d['lord']} ({d.get('planet', '')})", f"{YOGINI_HI.get(d['lord'], d['lord'])} ({HS.PLANET.get(d.get('planet', ''), d.get('planet', ''))})")
    rows = []
    for m in y["mahadashas"]:
        if m["end"] < now[:4] + "-01-01" and m["end"] < now:
            continue
        if len(rows) >= 8:
            break
        isnow = m["start"] <= now < m["end"]
        lab = nm(m)
        rows.append([span(m["start"], m["end"]), bi(lab["en"] + (" (current)" if isnow else ""), lab["hi"] + (" (चालू)" if isnow else "")),
                     bi(f"{m['years']} years", f"{m['years']} वर्ष")])
    curtext = bi(f"Now: {nm(cur['mahadasha'])['en']} to {month(cur['mahadasha']['end'])['en']}; sub-period {nm(cur['antardasha'])['en']} to {month(cur['antardasha']['end'])['en']}.",
                 f"अभी: {nm(cur['mahadasha'])['hi']} {month(cur['mahadasha']['end'])['hi']} तक; अंतर्दशा {nm(cur['antardasha'])['hi']} {month(cur['antardasha']['end'])['hi']} तक।")
    intro = bi("A 36-year cycle of eight Yoginis, each tied to a planet. It is read beside Vimshottari as a cross-check.",
               "आठ योगिनियों का 36 वर्ष का चक्र, हर योगिनी एक ग्रह से जुड़ी। इसे विंशोत्तरी के साथ पुष्टि के लिए पढ़ा जाता है।")
    return {"key": "yogini", "title": bi("Yogini dasha", "योगिनी दशा"), "intro": intro,
            "blocks": [para(curtext), table([bi("Period", "अवधि"), bi("Yogini (planet)", "योगिनी (ग्रह)"), bi("Length", "अवधि (वर्ष)")], rows)]}


def jaimini(v):
    j = v["jaimini"]
    rows = []
    for k, p in j["chara_karakas_7"].items():
        e, h, me, mh = KARAKA[k]
        rows.append([bi(e, h), P(p), bi(me, mh)])
    ar = j.get("arudha_padas", {})
    lines = [bi(f"Atmakaraka {j['atmakaraka']}; its navamsa sign (Karakamsha) is {j['karakamsha_sign']}, house {j['karakamsha_house_from_lagna']} from the lagna.",
                f"आत्मकारक {HS.PLANET.get(j['atmakaraka'], j['atmakaraka'])}; इसकी नवमांश राशि (कारकांश) {HS.SIGN.get(j['karakamsha_sign'], j['karakamsha_sign'])} है, लग्न से भाव {j['karakamsha_house_from_lagna']}।")]
    if ar.get("AL (Arudha Lagna)"):
        lines.append(bi(f"Arudha Lagna (how the world sees you): {ar['AL (Arudha Lagna)']}. Upapada (marriage): {ar.get('UL (Upapada Lagna)', '–')}.",
                        f"आरूढ़ लग्न (दुनिया आपको कैसे देखती है): {HS.SIGN.get(ar['AL (Arudha Lagna)'], ar['AL (Arudha Lagna)'])}। उपपद (विवाह): {HS.SIGN.get(ar.get('UL (Upapada Lagna)', ''), ar.get('UL (Upapada Lagna)', '–'))}।"))
    intro = bi("Jaimini ranks the planets by degree into seven karakas (significators); the highest is the Atmakaraka.",
               "जैमिनी पद्धति ग्रहों को अंशों के क्रम से सात कारकों में बाँटती है; सबसे अधिक अंश वाला आत्मकारक है।")
    return {"key": "jaimini", "title": bi("Jaimini karakas", "जैमिनी कारक"), "intro": intro,
            "blocks": [table([bi("Karaka", "कारक"), bi("Planet", "ग्रह"), bi("Signifies", "कारकत्व")], rows), items(lines)]}


MUNTHA_GOOD = {1, 2, 3, 5, 9, 10, 11}
TAJIKA_HI = {"Ithasala": "इत्थशाल", "Ishrafa": "इशराफ़", "Nakta": "नक्त", "Yamaya": "यमया", "Kamboola": "कंबूल", "Manahu": "मणऊ"}
TIME_HI = {"dawn": "भोर", "morning": "सुबह", "evening": "शाम", "night": "रात", "noon": "दोपहर", "sunrise": "सूर्योदय", "sunset": "सूर्यास्त"}


def day_hi(d):
    """'Thursday evening' -> 'गुरुवार शाम'."""
    out = d or ""
    for en, hi_ in {**WEEKDAY_HI, **TIME_HI}.items():
        out = re.sub(rf"\b{en}\b", hi_, out, flags=re.I)
    return out


def varshaphal(v):
    vp = v["varshaphal"]
    tj = vp.get("tajika") or {}
    mh = vp["muntha_house"]
    tone = bi("favourable", "अनुकूल") if mh in MUNTHA_GOOD else bi("asks for care", "सावधानी माँगता है")
    rows = [[bi("Year (age)", "वर्ष (आयु)"), bi(f"{vp['year_of_return']}–{vp['year_of_return'] + 1} (age {vp['age_at_return']})", f"{vp['year_of_return']}–{vp['year_of_return'] + 1} (आयु {vp['age_at_return']})")],
            [bi("Year begins", "वर्ष आरंभ"), date(vp["return_utc"][:10])],
            [bi("Varsha lagna", "वर्ष लग्न"), pos(vp["varsha_lagna"])],
            [bi("Muntha", "मुंथा"), bi(f"{vp['muntha_sign']}, house {mh} ({tone['en']})", f"{HS.SIGN.get(vp['muntha_sign'], vp['muntha_sign'])}, भाव {mh} ({tone['hi']})")]]
    if tj.get("muntha_lord"):
        rows.append([bi("Muntha lord", "मुंथेश"), P(tj["muntha_lord"])])
    vw = tj.get("varsheshwara") or {}
    if vw.get("planet"):
        rows.append([bi("Lord of the year (Varsheshwara)", "वर्षेश"), bi(f"{vw['planet']}, house {vw.get('house', '–')}", f"{HS.PLANET.get(vw['planet'], vw['planet'])}, भाव {vw.get('house', '–')}")])
    blocks = [table([bi("Item", "विषय"), bi("This year", "इस वर्ष")], rows)]
    yl = []
    for y in (tj.get("tajika_yogas") or [])[:6]:
        good = y["yoga"] == "Ithasala"
        yl.append(bi(f"{y['yoga']}: {' and '.join(y['planets'])} — " + ("applying, the matters they rule move toward completion" if good else "separating, the matter has passed its peak"),
                     f"{TAJIKA_HI.get(y['yoga'], y['yoga'])}: {' और '.join(HS.PLANET.get(p, p) for p in y['planets'])} — "
                     + ("निकट आते हुए, उनके विषय पूर्णता की ओर" if good else "दूर होते हुए, विषय अपने शिखर से आगे निकल चुका")))
    if yl:
        blocks.append(items(yl))
    intro = bi("The Tajika year chart is cast for the moment the Sun returns to its birth position each year, at the birthplace.",
               "ताजिक वर्ष कुंडली हर वर्ष उस क्षण की बनती है जब सूर्य अपनी जन्म-स्थिति पर लौटता है, जन्म-स्थान के लिए।")
    return {"key": "varshaphal", "title": bi("Varshaphal (this year's chart)", "वर्षफल (इस वर्ष की कुंडली)"), "intro": intro, "blocks": blocks}


def lalkitab(c):
    L = c.get("lalkitab")
    if not L:
        return None
    blocks = []
    occ = []
    for h in range(1, 13):
        ps = L["kundli"].get(str(h), [])
        occ.append([house_word(h), join([P(p) for p in ps]) if ps else bi("–")])
    blocks.append(table([bi("House (Aries = 1)", "खाना (मेष = 1)"), bi("Planets", "ग्रह")], occ))
    pl = []
    for p in NINE:
        x = L["planets"].get(p)
        if not x:
            continue
        en, hi_ = safe(x.get("title_en", "")), safe(x.get("title_hi", ""))
        state = bi("awake", "जागृत") if x.get("awake") else bi("asleep", "सोया हुआ")
        if en and hi_:   # both languages or neither: never an English line inside the Hindi reading
            pl.append(bi(f"{p} in house {x['house']} ({state['en']}): {en}", f"{HS.PLANET.get(p, p)} खाना {x['house']} ({state['hi']}): {hi_ or en}"))
    if pl:
        blocks.append(items(pl))
    for t in L.get("teva", []):
        u_en, u_hi = safe(t.get("upay", "")), safe(t.get("upay_hi", ""))
        blocks.append(para(bi(f"{t['label']} ({t['why']})" + (f": {u_en}" if u_en else "."), f"{t['label_hi']} ({t['why_hi']})" + (f": {u_hi}" if u_hi else "।"))))
    rin = []
    for r in L.get("rin", []):
        u_en, u_hi = safe(r.get("upay", "")), safe(r.get("upay_hi", ""))
        rin.append(bi(f"{r['rin']} — remedy: {u_en or 'see an expert'}", f"{r['rin_hi']} — उपाय: {u_hi or 'किसी जानकार से पूछें'}"))
    if rin:
        blocks.append(para(bi("Debts (rin) the chart shows:", "कुंडली में दिखने वाले ऋण:")))
        blocks.append(items(rin))
    vp = (L.get("varshphal") or [None])[0]
    if vp:
        rows = [[P(p), house_word(h)] for p, h in vp["positions"].items()]
        blocks.append(para(bi(f"Lal Kitab varshphal, year of life {vp['year_of_life']} ({span(vp['from'], vp['to'])['en']}); peak month {month(vp['peak_month'] + '-01')['en']}:",
                              f"लाल किताब वर्षफल, जीवन का {vp['year_of_life']}वाँ वर्ष ({span(vp['from'], vp['to'])['hi']}); मुख्य महीना {month(vp['peak_month'] + '-01')['hi']}:")))
        blocks.append(table([bi("Planet", "ग्रह"), bi("House this year", "इस वर्ष खाना")], rows))
    aff = (L.get("remedy_order_hint") or {}).get("afflicted", [])
    up = []
    gu = L.get("general_upay", {})
    info = L.get("planet_info", {})
    for p in aff:
        g = gu.get(p) or gu.get(f"{p}_bad")
        if not g:
            continue
        en, hi_ = safe(g["en"]), safe(g["hi"])
        if not en:
            continue
        i = info.get(p, {})
        up.append(bi(f"{p}: {en}" + (f" (day {i['day']}, colour {i['colour']})" if i.get("day") else ""),
                     f"{HS.PLANET.get(p, p)}: {hi_ or en}" + (f" ({day_hi(i['day'])}, रंग {i.get('colour_hi', i.get('colour', ''))})" if i.get("day") else "")))
    if up:
        blocks.append(para(bi("Remedies (upay) for the planets that need support, as the book gives them:", "सहारा माँगने वाले ग्रहों के उपाय, जैसे पुस्तक में दिए हैं:")))
        blocks.append(items(up))
    rules = [bi(safe(r["en"]), safe(r["hi"])) for r in L.get("upay_rules", [])[:4] if safe(r["en"])]
    if rules:
        blocks.append(para(bi("How to do a remedy:", "उपाय कैसे करें:")))
        blocks.append(items(rules))
    note = bi(L.get("disclaimer", ""), L.get("disclaimer_hi", ""))
    intro = bi("Lal Kitab (1952) reads the chart with Aries always as house 1 and gives simple household remedies.",
               "लाल किताब (1952) कुंडली में मेष को सदा पहला खाना मानकर पढ़ती है और सरल घरेलू उपाय बताती है।")
    return {"key": "lalkitab", "title": bi("Lal Kitab", "लाल किताब"), "intro": intro, "blocks": blocks, "note": note}


def kp(v):
    k = v["kp"]
    prow = [[P(p), S(x["sign"]), P(x["star_lord"]), P(x["sub_lord"])] for p, x in k["planets"].items() if p in NINE]
    crow = []
    for key, x in sorted(k["cusps"].items(), key=lambda kv: int(re.sub(r"\D", "", kv[0]) or 0)):
        n = re.sub(r"\D", "", key)
        crow.append([bi(n), S(x["sign"]), P(x["star_lord"]), P(x["sub_lord"])])
    sig = []
    for h in range(1, 13):
        ps = k["significators_by_house"].get(f"H{h}", [])
        sig.append([house_word(h), join([P(p) for p in ps]) if ps else bi("–")])
    intro = bi("Krishnamurti Paddhati splits each nakshatra into sub-parts; the sub-lord of a house cusp decides whether that house's matters are promised.",
               "कृष्णमूर्ति पद्धति हर नक्षत्र को उप-भागों में बाँटती है; किसी भाव-संधि का उप-स्वामी बताता है कि उस भाव के विषयों का वचन है या नहीं।")
    return {"key": "kp", "title": bi("KP (Krishnamurti Paddhati)", "केपी (कृष्णमूर्ति पद्धति)"), "intro": intro, "blocks": [
        table([bi("Planet", "ग्रह"), bi("Sign", "राशि"), bi("Star lord", "नक्षत्र स्वामी"), bi("Sub lord", "उप स्वामी")], prow),
        table([bi("Cusp", "भाव-संधि"), bi("Sign", "राशि"), bi("Star lord", "नक्षत्र स्वामी"), bi("Sub lord", "उप स्वामी")], crow),
        table([bi("House", "भाव"), bi("Significators", "कारक ग्रह")], sig)],
        "note": bi((k.get("note") or "").strip() or "KP uses Placidus cusps and the KP ayanamsa.", "केपी प्लेसिडस भाव-संधि और केपी अयनांश का उपयोग करती है।")}


def western_timing(w):
    blocks = []
    sp = w.get("secondary_progressions") or {}
    if sp.get("planets"):
        blocks.append(para(bi("Secondary progressions (a day after birth for each year of life):", "द्वितीयक प्रोग्रेशन (जीवन के हर वर्ष के लिए जन्म के बाद का एक दिन):")))
        blocks.append(table([bi("Planet", "ग्रह"), bi("Progressed position", "प्रोग्रेस्ड स्थिति")], [[P(p), pos(t)] for p, t in sp["planets"].items()]))
    sr = w.get("solar_return") or {}
    if sr.get("ascendant"):
        rows = [[bi("Ascendant", "लग्न"), pos(sr["ascendant"])], [bi("Midheaven", "दशम-बिंदु"), pos(sr["midheaven"])]]
        rows += [[P(p), bi(f"{pos(x['pos'])['en']}, house {x['house']}", f"{pos(x['pos'])['hi']}, भाव {x['house']}")]
                 for p, x in sr.get("planets", {}).items() if p in NINE[:7] + ["Uranus", "Neptune", "Pluto"]]
        blocks.append(para(bi(f"Solar return for age {sr['age']} (from {date(sr['return_utc'][:10])['en']}): the chart for the year ahead.",
                              f"आयु {sr['age']} का सोलर रिटर्न ({date(sr['return_utc'][:10])['hi']} से): आगे के वर्ष की कुंडली।")))
        blocks.append(table([bi("Point", "बिंदु"), bi("Position", "स्थिति")], rows))
    h = w.get("hellenistic") or {}
    if h:
        pr = h.get("annual_profection") or {}
        lines = [bi(f"Sect: {h.get('sect', '')}. Lot of Fortune {pos(h.get('lot_of_fortune'))['en']}; Lot of Spirit {pos(h.get('lot_of_spirit'))['en']}.",
                    f"सेक्ट: {'दिन' if 'day' in h.get('sect', '') else 'रात्रि'} कुंडली। भाग्य-लॉट {pos(h.get('lot_of_fortune'))['hi']}; आत्मा-लॉट {pos(h.get('lot_of_spirit'))['hi']}।")]
        if pr:
            lines.append(bi(f"Annual profection at age {pr['age']}: house {pr['profected_house']} ({pr['profected_sign']}), lord of the year {pr['year_lord']}.",
                            f"आयु {pr['age']} का वार्षिक प्रोफ़ेक्शन: भाव {pr['profected_house']} ({HS.SIGN.get(pr['profected_sign'], pr['profected_sign'])}), वर्ष-स्वामी {HS.PLANET.get(pr['year_lord'], pr['year_lord'])}।"))
        for key, en, hi_ in (("zodiacal_releasing_from_spirit", "career and direction", "करियर और दिशा"),
                             ("zodiacal_releasing_from_fortune", "body and circumstances", "शरीर और परिस्थितियाँ")):
            cur = (h.get(key) or {}).get("level1_current")
            if cur:
                lines.append(bi(f"Zodiacal releasing ({en}): {cur['sign']} period ruled by {cur['ruler']}, {span(cur['from'], cur['to'])['en']}.",
                                f"ज़ोडिएकल रिलीज़िंग ({hi_}): {HS.SIGN.get(cur['sign'], cur['sign'])} काल, स्वामी {HS.PLANET.get(cur['ruler'], cur['ruler'])}, {span(cur['from'], cur['to'])['hi']}।"))
        blocks.append(items(lines))
    if not blocks:
        return None
    intro = bi("Western timing techniques for the current period of life.", "जीवन के वर्तमान काल के लिए पश्चिमी समय-निर्धारण पद्धतियाँ।")
    return {"key": "western_timing", "title": bi("Western timing", "पाश्चात्य समय-निर्धारण"), "intro": intro, "blocks": blocks}


def build(c):
    v, w = c.get("vedic"), c.get("western")
    now = c["meta"].get("generated_for_date", "")
    out = []
    for f in ((lambda: panchang(v)), (lambda: ashtakavarga(v)), (lambda: yogini(v, now)), (lambda: jaimini(v)), (lambda: varshaphal(v)),
              (lambda: lalkitab(c)), (lambda: kp(v)), (lambda: western_timing(w) if w else None)):
        try:
            s = f()
        except (KeyError, TypeError, ValueError, IndexError):
            s = None   # a section the engine did not compute for this chart is simply left out
        if s:
            out.append(s)
    vargas = {k: v["divisional_charts"][k] for k in ("D9", "D10") if k in v.get("divisional_charts", {})}
    return {"sections": out, "vargas": vargas}
