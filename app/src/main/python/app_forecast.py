"""app_forecast.py - the app's three-year forecast by life area, in plain English and Hindi.

Input is a chart built with the forecast and events layers (engine_api.forecast does that). Everything dated comes
from the engine's forecast.life_areas and vedic.events; this module only selects, ranks and words it. The method and
the tone rules are the skill's (references/forecast_method.md); the outlook classes and the base-rate wording follow
render_report.forecast_summary and event_meaning.

Wording rules, as everywhere in the app: tendencies, never certainties; no illness, death or divorce is ever named;
health is energy, stress and rest only, with a pointer to a doctor; money is never investment advice.
"""
import re

import hindi_shell as HS

MON_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MON_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def month(iso, hi=False):
    y, m = iso[:4], int(iso[5:7])
    return f"{(MON_HI if hi else MON_EN)[m - 1]} {y}"


def day(iso, hi=False):
    y, m, d = iso[:4], int(iso[5:7]), int(iso[8:10])
    return f"{d} {(MON_HI if hi else MON_EN)[m - 1]} {y}"


def span(a, b, hi=False):
    return month(a, hi) if a[:7] == b[:7] else f"{month(a, hi)} – {month(b, hi)}"


def P(name, hi):
    return HS.PLANET.get(name, name) if hi else name


def S(sign, hi):
    return HS.SIGN.get(sign, sign) if hi else sign


HOUSE = {1: ("self and vitality", "स्वयं और ऊर्जा"), 2: ("family and savings", "परिवार और संचित धन"),
         3: ("effort and siblings", "प्रयास और भाई-बहन"), 4: ("home and mother", "घर और माता"),
         5: ("children, romance and learning", "संतान, प्रेम और विद्या"), 6: ("daily work and routine", "दैनिक कार्य और दिनचर्या"),
         7: ("partner and marriage", "जीवनसाथी और विवाह"), 8: ("change and shared resources", "परिवर्तन और साझा संसाधन"),
         9: ("fortune and father", "भाग्य और पिता"), 10: ("career", "करियर"), 11: ("gains and friends", "लाभ और मित्र"),
         12: ("expenses, rest and travel abroad", "व्यय, विश्राम और विदेश")}
ORD_EN = {1: "1st", 2: "2nd", 3: "3rd"}
ORD_HI = {1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें", 6: "छठे", 7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें",
          11: "ग्यारहवें", 12: "बारहवें"}


def hname(h, hi):
    return f"{ORD_HI[h]} भाव ({HOUSE[h][1]})" if hi else f"{ORD_EN.get(h, f'{h}th')} house ({HOUSE[h][0]})"


TONE = {"+": ("supportive", "अनुकूल"), "-": ("asks for effort", "प्रयास माँगता है"), "~": ("mixed", "मिश्रित"),
        "*": ("brings this area forward", "इस क्षेत्र को सक्रिय करता है")}

AREAS = [
    {"key": "marriage", "src": ["love"], "windows": ["marriage"],
     "title": ("Marriage & partner", "विवाह और जीवनसाथी"),
     "sub": ("Partnership, romance and the timing windows for marriage. If you are married, read it for your partnership.",
             "साझेदारी, प्रेम और विवाह के समय की खिड़कियाँ। विवाहित हों तो इसे अपने दांपत्य के लिए पढ़ें।")},
    {"key": "work", "src": ["career"], "windows": ["career"],
     "title": ("Work & career", "कार्य और करियर"),
     "sub": ("Job, business, status and the people you work with", "नौकरी, व्यवसाय, प्रतिष्ठा और सहकर्मी")},
    {"key": "health", "src": ["health"], "windows": [],
     "title": ("Health & energy", "स्वास्थ्य और ऊर्जा"),
     "sub": ("Energy, stress and rest. Not medical advice: see a doctor for any health concern.",
             "ऊर्जा, तनाव और विश्राम। यह चिकित्सा सलाह नहीं है: स्वास्थ्य संबंधी किसी भी चिंता के लिए डॉक्टर से मिलें।")},
    {"key": "family", "src": ["family", "children"], "windows": ["property", "children"],
     "title": ("Love & family", "प्रेम और परिवार"),
     "sub": ("Home, parents, children and emotional life", "घर, माता-पिता, संतान और भावनात्मक जीवन")},
]
AREA_HOUSES = {"marriage": {7, 5}, "work": {10, 6, 11}, "health": {1, 6, 8}, "family": {4, 2, 5}}

SUMMARY = {
    "marriage": {
        "supportive": ("A supportive year for relationships: a good time to meet people, deepen a bond or plan a wedding.",
                       "रिश्तों के लिए अनुकूल वर्ष: लोगों से मिलने, संबंध गहरा करने या विवाह की योजना के लिए अच्छा समय।"),
        "demanding": ("Relationships ask for patience this year: talk things through and avoid rushed decisions.",
                      "इस वर्ष रिश्ते धैर्य माँगते हैं: बातचीत से सुलझाएँ और जल्दबाज़ी के निर्णय न लें।"),
        "mixed": ("Mixed signals for relationships: take important steps in the supportive months.",
                  "रिश्तों के लिए मिले-जुले संकेत: महत्वपूर्ण कदम अनुकूल महीनों में उठाएँ।"),
        "quiet": ("No strong signal for relationships this year; things continue much as they are.",
                  "इस वर्ष रिश्तों के लिए कोई बड़ा संकेत नहीं; स्थिति लगभग वैसी ही रहती है।")},
    "work": {
        "supportive": ("A supportive year for work: a good time to apply, ask for more responsibility or start something new.",
                       "कार्य के लिए अनुकूल वर्ष: आवेदन करने, अधिक ज़िम्मेदारी माँगने या कुछ नया शुरू करने का अच्छा समय।"),
        "demanding": ("Work asks for steady effort this year: keep commitments, build skills and avoid risky jumps.",
                      "इस वर्ष कार्य निरंतर मेहनत माँगता है: वचन निभाएँ, कौशल बढ़ाएँ और जोखिम भरी छलाँग से बचें।"),
        "mixed": ("Ups and downs at work: use the supportive stretches for big moves and the slower ones to consolidate.",
                  "कार्य में उतार-चढ़ाव: बड़े कदम अनुकूल समय में और धीमे समय में स्थिरता पर ध्यान।"),
        "quiet": ("A steady year at work, without a strong push either way.",
                  "कार्य में स्थिर वर्ष, किसी ओर बड़ा धक्का नहीं।")},
    "health": {
        "supportive": ("Good energy this year: a fine time to build healthy routines.",
                       "इस वर्ष अच्छी ऊर्जा: स्वस्थ दिनचर्या बनाने का अच्छा समय।"),
        "demanding": ("Energy may run lower this year: protect sleep, rest and routine, and see a doctor for any health concern.",
                      "इस वर्ष ऊर्जा कुछ कम रह सकती है: नींद, विश्राम और दिनचर्या का ध्यान रखें, और स्वास्थ्य की किसी भी चिंता पर डॉक्टर से मिलें।"),
        "mixed": ("Energy comes and goes: pace yourself in busy stretches and keep a steady routine.",
                  "ऊर्जा घटती-बढ़ती रहती है: व्यस्त समय में अपनी गति संभालें और दिनचर्या नियमित रखें।"),
        "quiet": ("No strong signal for energy this year; keep your usual routine.",
                  "इस वर्ष ऊर्जा के लिए कोई बड़ा संकेत नहीं; अपनी सामान्य दिनचर्या बनाए रखें।")},
    "family": {
        "supportive": ("A warm year for home and family: good for time together, family plans and home matters.",
                       "घर और परिवार के लिए सुखद वर्ष: साथ समय बिताने, पारिवारिक योजनाओं और घर के कामों के लिए अच्छा।"),
        "demanding": ("Home and family ask for more care this year: be patient with responsibilities and keep talking.",
                      "इस वर्ष घर और परिवार अधिक देखभाल माँगते हैं: ज़िम्मेदारियों में धैर्य रखें और बातचीत बनाए रखें।"),
        "mixed": ("Family life has busy and calm stretches: plan important family steps in the supportive months.",
                  "पारिवारिक जीवन में व्यस्त और शांत, दोनों समय: महत्वपूर्ण पारिवारिक कदम अनुकूल महीनों में रखें।"),
        "quiet": ("A quiet year for home and family, without strong signals.",
                  "घर और परिवार के लिए शांत वर्ष, कोई बड़ा संकेत नहीं।")},
}
OUTLOOK = {
    "mostly_supportive": ("Mostly supportive", "अधिकतर अनुकूल"),
    "mostly_demanding": ("Mostly demanding: steady effort needed", "अधिकतर चुनौतीपूर्ण: लगातार प्रयास चाहिए"),
    "ups_and_downs": ("Ups and downs: good and testing years both", "उतार-चढ़ाव: अच्छे और परीक्षा वाले, दोनों तरह के वर्ष"),
    "gently_supportive": ("Gently supportive", "हल्का अनुकूल"),
    "some_pressure": ("Some pressure, no strong support", "कुछ दबाव, बड़ा सहारा नहीं"),
    "steady": ("Steady: no strong signal either way", "स्थिर: किसी ओर बड़ा संकेत नहीं"),
}
WINDOW_NAME = {"marriage": ("marriage", "विवाह"), "career": ("a career step", "करियर में कदम"),
               "property": ("home or property", "घर या संपत्ति"), "children": ("children", "संतान")}
PY_THEME = {1: ("new beginnings", "नई शुरुआत"), 2: ("partnership and patience", "साझेदारी और धैर्य"),
            3: ("expression and social life", "अभिव्यक्ति और मेल-जोल"), 4: ("building and hard work", "निर्माण और परिश्रम"),
            5: ("change and movement", "परिवर्तन और गतिशीलता"), 6: ("family and responsibility", "परिवार और ज़िम्मेदारी"),
            7: ("reflection and rest", "चिंतन और विश्राम"), 8: ("achievement and money matters", "उपलब्धि और धन"),
            9: ("completion and letting go", "पूर्णता और छोड़ना"), 11: ("inspiration", "प्रेरणा"), 22: ("building something large", "बड़ा निर्माण")}
TEN_GOD_THEME = {"Wealth": ("money", "धन"), "Officer": ("career and authority", "करियर और अधिकार"),
                 "Seven Killings": ("pressure and ambition", "दबाव और महत्वाकांक्षा"),
                 "Eating God": ("creativity and enjoyment", "सृजन और आनंद"), "Hurting Officer": ("self-expression", "आत्म-अभिव्यक्ति"),
                 "Resource": ("learning and support", "विद्या और सहारा"), "Friend": ("peers", "साथी"), "Rob Wealth": ("competition", "प्रतिस्पर्धा")}
PALACE = {"Year": ("elders and wider family", "बड़ों और बड़े परिवार"), "Month": ("career and parents", "करियर और माता-पिता"),
          "Day": ("partner and home life", "जीवनसाथी और गृहस्थ जीवन"), "Hour": ("children and later projects", "संतान और आगे की योजनाओं")}
POINT = {"Ascendant": ("rising point", "लग्न-बिंदु"), "Midheaven": ("career point (Midheaven)", "करियर-बिंदु (दशम)")}
EASY = {"trine", "sextile"}
TENSE = {"square", "opposition"}


def event_meaning(rate, hi=False):
    if rate < 0.25:
        return "इस कुंडली में दुर्लभ: सार्थक संकेत।" if hi else "Rare in this chart: a real signal."
    if rate < 0.5:
        return "काफ़ी चयनात्मक: अन्य संकेत साथ हों तो बेहतर।" if hi else "Fairly selective: best with other support."
    if rate < 0.75:
        return "आम: इसे पृष्ठभूमि मानें।" if hi else "Common: treat it as background."
    return "अधिकतर समय सत्य: अकेले यह कम बताता है।" if hi else "True most of the time: on its own it says little."


# ------------------------------------------------------------------ one indicator in plain words
def _houses_list(hs, hi):
    hs = [h for h in hs if h in HOUSE]
    if not hs:
        return ""
    parts = [hname(h, hi) for h in hs]
    return (" और ".join(parts) if hi else " and ".join(parts))


def plain(i, area_houses):
    """(rank, en, hi) for one engine indicator; rank orders drivers (lower first). Unknown text falls back to itself."""
    t, tone = i["text"], i["tone"]
    te, th = TONE[tone]
    fr, to = i["from"], i["to"]
    m = re.match(r"^(\w+)(?:-(\w+))? (mahadasha|antardasha): lord (\w+) in H(\d+), owns ([\d, -]+)", t)
    if m:
        maha, antar, kind, lord, h = m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
        owns = [int(x) for x in re.findall(r"\d+", m.group(6))]
        tied = [x for x in owns if x in area_houses]
        if kind == "mahadasha":
            le, lh = f"{maha} major period (until {month(to)})", f"{P(maha, True)} महादशा ({month(to, True)} तक)"
        else:
            le, lh = f"{maha}–{antar} period ({span(fr, to)})", f"{P(maha, True)}–{P(antar, True)} दशा ({span(fr, to, True)})"
        if tied:
            en = f"{le}: {lord} rules your {_houses_list(tied, False)} and sits in your {hname(h, False)}. {te.capitalize()}."
            hi_ = f"{lh}: {P(lord, True)} आपके {_houses_list(tied, True)} का स्वामी है और {hname(h, True)} में है। {th}।"
        else:
            en = f"{le}: {lord} sits in your {hname(h, False)}. {te.capitalize()}."
            hi_ = f"{lh}: {P(lord, True)} आपके {hname(h, True)} में है। {th}।"
        return (0 if kind == "antardasha" else 2), en, hi_
    m = re.match(r"^Double transit \(Jupiter \+ Saturn\) on H(\d+) from (moon|lagna)", t)
    if m:
        h, ref = int(m.group(1)), m.group(2)
        return (1, f"Jupiter and Saturn together activate your {hname(h, False)}, counted from your "
                   f"{'Moon sign' if ref == 'moon' else 'rising sign'} ({span(fr, to)}): a classic sign that this part of life gets busy.",
                f"गुरु और शनि मिलकर आपके {'चंद्र' if ref == 'moon' else 'लग्न'} से {hname(h, True)} को सक्रिय करते हैं ({span(fr, to, True)}): "
                f"शास्त्रीय संकेत कि जीवन का यह हिस्सा सक्रिय रहेगा।")
    m = re.match(r"^Event window \((\w+)\): .*base rate (\d+)%", t)
    if m:
        k, rate = m.group(1), int(m.group(2)) / 100
        ne, nh = WINDOW_NAME.get(k, (k, k))
        return (-1, f"Timing window for {ne} ({span(fr, to)}): the planetary period and the Jupiter–Saturn transits agree. "
                   f"{event_meaning(rate)}",
                f"{nh} के लिए समय की खिड़की ({span(fr, to, True)}): दशा और गुरु-शनि गोचर एकमत हैं। {event_meaning(rate, True)}")
    m = re.match(r"^(Jupiter|Saturn|Rahu|Ketu) in (\w+) \(H(\d+) from Lagna, H(\d+) from Moon\)(?:, aspecting (.+?))? \(", t)
    if m:
        p, sg, hl, hm = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        asp = [int(x) for x in re.findall(r"H(\d+) from Lagna", m.group(5) or "")]
        asp = [x for x in asp if x in area_houses]
        rank = 3 if p in ("Jupiter", "Saturn") else 5
        on = hl in area_houses
        if on or not asp:
            en = f"{p} moves through {sg}, your {hname(hl, False)} ({span(fr, to)}). {te.capitalize()}."
            hi_ = f"{P(p, True)} {S(sg, True)} राशि में, आपके {hname(hl, True)} से गुज़रता है ({span(fr, to, True)})। {th}।"
        else:
            en = f"{p} in {sg} looks at your {_houses_list(asp, False)} ({span(fr, to)}). {te.capitalize()}."
            hi_ = f"{S(sg, True)} में {P(p, True)} की दृष्टि आपके {_houses_list(asp, True)} पर ({span(fr, to, True)})। {th}।"
        return rank, en, hi_
    if t.startswith("Sade Sati"):
        return (2, f"Saturn's Sade Sati ({t.split(' - ')[-1]}, {span(fr, to)}): a time of responsibility and slower results, not disaster.",
                f"शनि की {HS.SHANI_HI.get(t, 'साढ़े साती').replace('&mdash;', '—')} ({span(fr, to, True)}): ज़िम्मेदारी और धीमे परिणामों का समय, विपत्ति का नहीं।")
    if t.startswith("Kantaka Shani"):
        return (3, f"Saturn passes a demanding point from your Moon ({t}, {span(fr, to)}): extra duties; pace yourself.",
                f"शनि चंद्र से कठिन स्थान पर ({HS.SHANI_HI.get(t, t)}, {span(fr, to, True)}): अतिरिक्त ज़िम्मेदारियाँ; अपनी गति संभालें।")
    if t.startswith("Ashtama Shani"):
        return (3, f"Saturn 8th from your Moon (Ashtama Shani, {span(fr, to)}): keep plans simple and rest well.",
                f"चंद्र से अष्टम शनि ({span(fr, to, True)}): योजनाएँ सरल रखें और पूरा विश्राम लें।")
    m = re.match(r"^Varshaphal age (\d+): Muntha in H(\d+)", t)
    if m:
        a, h = m.group(1), int(m.group(2))
        return (4, f"Your birthday-year chart (age {a}) puts the year's focus on your {hname(h, False)}. {te.capitalize()}.",
                f"आपका वर्षफल (आयु {a}) वर्ष का केंद्र आपके {hname(h, True)} पर रखता है। {th}।")
    m = re.match(r"^(\w+) (conjunction|opposition|square|trine|sextile) natal (\w+) \(([\d\-, ]+)\)", t)
    if m:
        p, asp, pt, dates = m.group(1), m.group(2), m.group(3), m.group(4).split(", ")
        kind = "an easy" if asp in EASY else "a tense" if asp in TENSE else "a strong"
        kh = "सहज" if asp in EASY else "तनावपूर्ण" if asp in TENSE else "प्रबल"
        pe, ph = POINT.get(pt, (f"natal {pt}", f"जन्म-{P(pt, True)}"))
        when_e = day(dates[0]) + (f" (and {len(dates) - 1} more pass{'es' if len(dates) > 2 else ''})" if len(dates) > 1 else "")
        when_h = day(dates[0], True) + (f" (और {len(dates) - 1} बार)" if len(dates) > 1 else "")
        return (6, f"Western: {p} makes {kind} angle to your {pe} on {when_e}. {te.capitalize()}.",
                f"पश्चिमी: {P(p, True)} आपके {ph} से {kh} कोण बनाता है, {when_h}। {th}।")
    m = re.match(r"^Profection to H(\d+)", t)
    if m:
        h = int(m.group(1))
        return (6, f"Western annual profection: this birthday year switches on your {hname(h, False)}.",
                f"पश्चिमी वार्षिक प्रोफ़ेक्शन: यह जन्मदिन-वर्ष आपके {hname(h, True)} को सक्रिय करता है।")
    m = re.match(r"^ZR from (Spirit|Fortune)", t)
    if m:
        what = ("career and direction", "करियर और दिशा") if m.group(1) == "Spirit" else ("body and circumstances", "शरीर और परिस्थितियाँ")
        if "loosing of the bond" in t:
            return (6, f"Western zodiacal releasing: a turning point for {what[0]} ({span(fr, to)}).",
                    f"पश्चिमी ज़ोडिएकल रिलीज़िंग: {what[1]} के लिए मोड़ ({span(fr, to, True)})।")
        return (6, f"Western zodiacal releasing: a peak period for {what[0]} ({span(fr, to)}).",
                f"पश्चिमी ज़ोडिएकल रिलीज़िंग: {what[1]} के लिए शिखर-काल ({span(fr, to, True)})।")
    m = re.match(r"^(\w+) (solar|lunar) eclipse in H(\d+)", t)
    if m:
        h = int(m.group(3))
        return (7, f"A {m.group(2)} eclipse on {day(fr)} highlights your {hname(h, False)} for about six months.",
                f"{day(fr, True)} का {'सूर्य' if m.group(2) == 'solar' else 'चंद्र'} ग्रहण लगभग छह महीने आपके {hname(h, True)} को उभारता है।")
    yr = fr[:4]
    m = re.match(r"^\S+ year stem is (.+)$", t)
    if m:
        g = m.group(1)
        th_ = next((v for k, v in TEN_GOD_THEME.items() if k in g), ("this area", "इस क्षेत्र"))
        return (7, f"Chinese BaZi: the year from Feb {yr} carries a theme of {th_[0]}.",
                f"चीनी बाज़ी: फ़रवरी {yr} से शुरू वर्ष में {th_[1]} का विषय है।")
    m = re.match(r"^\S+ year: (.+?) with (\w+) pillar", t)
    if m:
        rel, pal = m.group(1), PALACE.get(m.group(2), (m.group(2), m.group(2)))
        if "harmony" in rel and "half" not in rel:
            return (7, f"Chinese BaZi: the year from Feb {yr} is in harmony with your {pal[0]}.",
                    f"चीनी बाज़ी: फ़रवरी {yr} से शुरू वर्ष आपके {pal[1]} के साथ मेल में है।")
        return (7, f"Chinese BaZi: the year from Feb {yr} brings friction to your {pal[0]}; read it as change, not loss.",
                f"चीनी बाज़ी: फ़रवरी {yr} से शुरू वर्ष आपके {pal[1]} में घर्षण लाता है; इसे बदलाव समझें, हानि नहीं।")
    if "Peach Blossom" in t:
        return (7, f"Chinese BaZi: the year from Feb {yr} is a Peach Blossom year, a livelier social and romantic life.",
                f"चीनी बाज़ी: फ़रवरी {yr} से शुरू वर्ष पीच ब्लॉसम वर्ष है, सामाजिक और प्रेम-जीवन अधिक सक्रिय।")
    m = re.match(r"^Personal Year (\d+) \((\d+)\)", t)
    if m:
        n, y = int(m.group(1)), m.group(2)
        th2 = PY_THEME.get(n, ("", ""))
        return (8, f"Numerology: {y} is a Personal Year {n}, a year of {th2[0]}.",
                f"अंक ज्योतिष: {y} व्यक्तिगत वर्ष {n} है, {th2[1]} का वर्ष।")
    return 9, t, HS.to_hindi(t)


# ------------------------------------------------------------------ summarising
_CONV_W = {"strong": 1.5, "moderate": 1.0, "weak": 0.5}


def _score(s):
    return (s["supportive"] - s["demanding"]) * _CONV_W.get(s["convergence"], 1.0)


def _lean(ind):
    """The engine's tag_areas count, redone for a merged list of indicators."""
    systems = {}
    for i in ind:
        systems.setdefault(i["system"], {"+": 0, "-": 0, "~": 0, "*": 0})[i["tone"]] += 1
    plus = sum(1 for c in systems.values() if c["+"] > c["-"])
    minus = sum(1 for c in systems.values() if c["-"] > c["+"])
    act = len(systems)
    lean = "supportive" if plus > minus else "demanding" if minus > plus else "mixed" if act else "quiet"
    conv = "strong" if max(plus, minus) >= 3 else "moderate" if max(plus, minus) == 2 else "weak"
    return lean, conv, plus, minus, act


def outlook(years):
    sup = [y for y in years if y["lean"] == "supportive"]
    dem = [y for y in years if y["lean"] == "demanding"]
    # The skill's five-slice rule (3+ one way, at most 1 the other) scaled to three years: 2+ one way, none the other.
    if len(sup) >= 2 and not dem:
        cls = "mostly_supportive"
    elif len(dem) >= 2 and not sup:
        cls = "mostly_demanding"
    elif sup and dem:
        cls = "ups_and_downs"
    elif sup:
        cls = "gently_supportive"
    elif dem:
        cls = "some_pressure"
    else:
        cls = "steady"
    best = max(years, key=_score) if years else None
    care = min(years, key=_score) if years else None
    return {"class": cls, "en": OUTLOOK[cls][0], "hi": OUTLOOK[cls][1],
            "best": best["id"] if best and _score(best) > 0 else None,
            "care": care["id"] if care and _score(care) < 0 else None}


def _months_runs(months):
    runs, cur = [], None
    for mo in months:
        if cur and _next_month(cur[1]) == mo:
            cur[1] = mo
        else:
            if cur:
                runs.append(cur)
            cur = [mo, mo]
    if cur:
        runs.append(cur)
    return runs


def _next_month(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y + (m == 12)}-{(m % 12) + 1:02d}"


def build(c, max_drivers=5):
    F = c["forecast"]
    ev = (c.get("vedic") or {}).get("events") or {}
    la = F["life_areas"]
    w0, w1 = F["window"]["start"], F["window"]["end"]
    out = {"window": {"from": w0, "to": w1}, "generated_for": c["meta"].get("generated_for_date"),
           "birth_time_confidence": c["meta"].get("birth_time_confidence"), "areas": []}
    conf = c["meta"].get("birth_time_confidence")
    if conf in ("unknown", "approximate"):
        out["reliability"] = {
            "en": ("The birth time is " + conf + ", so everything counted from the rising sign is "
                   + ("not usable" if conf == "unknown" else "less certain") + ". Moon-based periods, BaZi and numerology still hold."),
            "hi": ("जन्म-समय " + ("अज्ञात" if conf == "unknown" else "अनुमानित") + " है, इसलिए लग्न से गिनी गई हर बात "
                   + ("उपयोगी नहीं" if conf == "unknown" else "कम निश्चित") + " है। चंद्र-आधारित दशाएँ, बाज़ी और अंक ज्योतिष फिर भी लागू हैं।")}
    for A in AREAS:
        hs = AREA_HOUSES[A["key"]]
        years = []
        for idx, sl in enumerate(F["slices"]):
            ind, seen = [], set()
            for src in A["src"]:
                for i in la[src]["by_slice"][idx]["indicators"]:
                    if (i["system"], i["text"]) not in seen:
                        seen.add((i["system"], i["text"]))
                        ind.append(i)
            lean, conv, plus, minus, act = _lean(ind)
            drivers = []
            for i in ind:
                rank, en, hi_ = plain(i, hs)
                tr = 0 if i["tone"] in "+-" else 1
                drivers.append({"rank": rank, "_t": tr, "tone": i["tone"], "system": i["system"], "from": i["from"], "to": i["to"],
                                "en": en, "hi": hi_, "technical": i["text"]})
            drivers = [d for d in drivers if d["rank"] >= 0]   # event windows are listed once, above the years
            drivers.sort(key=lambda d: (d["rank"], d["_t"], d["from"]))
            # Lead with variety: at most two items of one kind before the rest.
            first, rest, per = [], [], {}
            for d in drivers:
                per[d["rank"]] = per.get(d["rank"], 0) + 1
                (first if per[d["rank"]] <= 2 else rest).append(d)
            drivers = first + rest
            for d in drivers:
                d.pop("_t")
            se, sh = SUMMARY[A["key"]][lean]
            years.append({"id": sl["id"], "from": sl["from"], "to": sl["to"], "lean": lean, "convergence": conv,
                          "supportive": plus, "demanding": minus, "active": act,
                          "summary": {"en": se, "hi": sh},
                          "drivers": drivers[:max_drivers], "more": drivers[max_drivers:]})
        windows = []
        for k in A["windows"]:
            aw = (ev.get("area_windows") or {}).get(k)
            if not aw:
                continue
            rate = aw["base_rate_ages_18_70"]["dasha+transit"]
            for wd in aw["windows"]:
                a, b = max(wd["from"], w0), min(wd["to"], w1)
                if a > b:
                    continue
                ne, nh = WINDOW_NAME.get(k, (k, k))
                windows.append({"kind": k, "from": a, "to": b, "base_rate": rate, "jaimini": wd.get("with_sign_dasha", False),
                                "en": f"Timing window for {ne}: {span(a, b)}" + (" (a Jaimini period also fits)" if wd.get("with_sign_dasha") else ""),
                                "hi": f"{nh} के लिए समय की खिड़की: {span(a, b, True)}" + (" (जैमिनी दशा भी अनुकूल)" if wd.get("with_sign_dasha") else ""),
                                "meaning": {"en": event_meaning(rate), "hi": event_meaning(rate, True)}})
        if A["key"] == "marriage" and ev.get("marriage_kn_rao"):
            months = [x["month"] for x in ev["marriage_kn_rao"].get("months", []) if x.get("all_steps") and w0[:7] <= x["month"] <= w1[:7]]
            for a, b in _months_runs(months):
                windows.append({"kind": "kn_rao", "from": a + "-01", "to": b + "-28", "base_rate": None, "jaimini": False,
                                "en": f"All of K.N. Rao's marriage transit steps hold: {month(a + '-01')}" + ("" if a == b else f" – {month(b + '-01')}"),
                                "hi": f"के.एन. राव के विवाह-गोचर के सभी चरण पूरे: {month(a + '-01', True)}" + ("" if a == b else f" – {month(b + '-01', True)}"),
                                "meaning": {"en": "The narrowest classical marriage timing in this method.",
                                            "hi": "इस पद्धति में विवाह का सबसे सटीक शास्त्रीय समय।"}})
        windows.sort(key=lambda x: x["from"])
        out["areas"].append({"key": A["key"], "title": {"en": A["title"][0], "hi": A["title"][1]},
                             "subtitle": {"en": A["sub"][0], "hi": A["sub"][1]},
                             "outlook": outlook(years), "years": years, "windows": windows})
    out["method"] = {
        "en": ("Classical Vedic timing (planetary periods, Jupiter and Saturn transits, the birthday-year chart) is checked against "
               "Western transits, Chinese BaZi and numerology. A year is marked strong only when several systems agree. "
               "These are tendencies to plan around, not certainties."),
        "hi": ("शास्त्रीय वैदिक समय-निर्धारण (दशा, गुरु और शनि का गोचर, वर्षफल) को पश्चिमी गोचर, चीनी बाज़ी और अंक ज्योतिष से मिलाया जाता है। "
               "कोई वर्ष तभी प्रबल माना जाता है जब कई पद्धतियाँ सहमत हों। ये योजना के लिए प्रवृत्तियाँ हैं, निश्चितताएँ नहीं।")}
    return out
