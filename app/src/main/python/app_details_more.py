"""app_details_more.py - further Kundali sections built from values the engine already computes: doshas, pratyantar
dashas, Chara and Narayana dashas, arudhas and special lagnas, birth-time sensitivity, bhava chalit, the Avakahada
chakra with the name syllable, and the names and uses of the sixteen divisional charts. App-owned.

Every sentence passes the app's rule against death, illness and divorce (app_details.safe), and doshas are described
as patterns the tradition watches for, never as verdicts.
"""
import datetime as dt

import hindi_shell as HS
import ashtakoota as AK
from app_details import bi, P, S, date, span, table, para, items, safe, SIGNS, NINE

VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

VARGAS = [
    ("D1", "Rashi", "राशि", "the whole life", "संपूर्ण जीवन"),
    ("D2", "Hora", "होरा", "wealth", "धन"),
    ("D3", "Drekkana", "द्रेष्काण", "siblings and courage", "भाई-बहन और साहस"),
    ("D4", "Chaturthamsha", "चतुर्थांश", "home and property", "घर और संपत्ति"),
    ("D7", "Saptamsha", "सप्तमांश", "children", "संतान"),
    ("D9", "Navamsha", "नवमांश", "marriage and inner strength", "विवाह और आंतरिक बल"),
    ("D10", "Dashamsha", "दशमांश", "career", "करियर"),
    ("D12", "Dwadashamsha", "द्वादशांश", "parents", "माता-पिता"),
    ("D16", "Shodashamsha", "षोडशांश", "vehicles and comforts", "वाहन और सुख"),
    ("D20", "Vimshamsha", "विंशांश", "spiritual practice", "आध्यात्मिक साधना"),
    ("D24", "Chaturvimshamsha", "चतुर्विंशांश", "learning", "शिक्षा"),
    ("D27", "Bhamsha", "भांश", "strengths and weaknesses", "बल और दुर्बलताएँ"),
    ("D30", "Trimshamsha", "त्रिंशांश", "challenges and resilience", "चुनौतियाँ और सहनशक्ति"),
    ("D40", "Khavedamsha", "खवेदांश", "maternal lineage", "मातृ वंश"),
    ("D45", "Akshavedamsha", "अक्षवेदांश", "paternal lineage and character", "पितृ वंश और चरित्र"),
    ("D60", "Shashtyamsha", "षष्ट्यंश", "the overall pattern of past karma", "पूर्व कर्म का समग्र स्वरूप"),
]

# Namakshar: the first syllable of a name by the Moon's nakshatra and pada (common North Indian table)
SYLLABLE = [
    ("Chu Che Cho La", "चू चे चो ला"), ("Li Lu Le Lo", "ली लू ले लो"), ("A I U E", "अ इ उ ए"), ("O Va Vi Vu", "ओ वा वी वू"),
    ("Ve Vo Ka Ki", "वे वो का की"), ("Ku Gha Nga Chha", "कू घ ङ छ"), ("Ke Ko Ha Hi", "के को हा ही"), ("Hu He Ho Da", "हू हे हो डा"),
    ("Di Du De Do", "डी डू डे डो"), ("Ma Mi Mu Me", "मा मी मू मे"), ("Mo Ta Ti Tu", "मो टा टी टू"), ("Te To Pa Pi", "टे टो पा पी"),
    ("Pu Sha Na Tha", "पू ष ण ठ"), ("Pe Po Ra Ri", "पे पो रा री"), ("Ru Re Ro Ta", "रू रे रो ता"), ("Ti Tu Te To", "ती तू ते तो"),
    ("Na Ni Nu Ne", "ना नी नू ने"), ("No Ya Yi Yu", "नो या यी यू"), ("Ye Yo Bha Bhi", "ये यो भा भी"), ("Bhu Dha Pha Dha", "भू धा फा ढा"),
    ("Bhe Bho Ja Ji", "भे भो जा जी"), ("Khi Khu Khe Kho", "खी खू खे खो"), ("Ga Gi Gu Ge", "गा गी गू गे"), ("Go Sa Si Su", "गो सा सी सू"),
    ("Se So Da Di", "से सो दा दी"), ("Du Tha Jha Na", "दू थ झ ञ"), ("De Do Cha Chi", "दे दो चा ची"),
]
GANA_HI = {"Deva": "देव", "Manushya": "मनुष्य", "Rakshasa": "राक्षस"}
VARNA_HI = {"Brahmin": "ब्राह्मण", "Kshatriya": "क्षत्रिय", "Vaishya": "वैश्य", "Shudra": "शूद्र"}
YONI_HI = {"Horse": "अश्व", "Elephant": "गज", "Sheep": "मेष", "Serpent": "सर्प", "Dog": "श्वान", "Cat": "मार्जार", "Rat": "मूषक",
           "Cow": "गौ", "Buffalo": "महिष", "Tiger": "व्याघ्र", "Deer": "मृग", "Monkey": "वानर", "Mongoose": "नकुल", "Lion": "सिंह"}
NADI_HI = {"Adi": "आदि", "Madhya": "मध्य", "Antya": "अंत्य"}
VASHYA_HI = {"Chatushpad (quadruped)": "चतुष्पद", "Dwipad (human)": "द्विपद (मानव)", "Jalachar (water)": "जलचर",
             "Vanachar (wild)": "वनचर", "Keeta (insect)": "कीट"}
TATVA = [("Fire", "अग्नि"), ("Earth", "पृथ्वी"), ("Air", "वायु"), ("Water", "जल")]


def _sign(s):
    return S(s) if s in SIGNS else bi(s)


def _add_years(iso, years):
    d = dt.date.fromisoformat(iso[:10])
    return (d + dt.timedelta(days=round(years * 365.2425))).isoformat()


def varga_meta():
    return [{"key": k, "name": bi(f"{k} {en}", f"{k} {hi}"), "use": bi(ue, uh)} for k, en, hi, ue, uh in VARGAS]


def avakahada(v):
    moon = v["planets"]["Moon"]
    nak = moon["nakshatra"]
    ni = AK.NAKSHATRAS.index(nak)
    si = moon["sign_index"]
    varna = AK.VARNA_NAME[AK.VARNA[si]]
    vashya = AK.vashya_group(si, moon["lon"])
    gana = AK.GANA[nak]
    yoni = AK.YONI[ni]
    nadi = AK.NADI_PATTERN[ni % 6]
    syl_en, syl_hi = SYLLABLE[ni]
    pada = moon["pada"]
    first_en, first_hi = syl_en.split()[pada - 1], syl_hi.split()[pada - 1]
    tat = TATVA[si % 4]
    rows = [
        [bi("Moon sign (rashi)", "चंद्र राशि"), S(moon["sign"])],
        [bi("Nakshatra and pada", "नक्षत्र और पद"), bi(f"{nak}, pada {pada} (lord {moon['nakshatra_lord']})",
                                                    f"{HS.NAK.get(nak, nak)}, पद {pada} (स्वामी {HS.PLANET.get(moon['nakshatra_lord'], moon['nakshatra_lord'])})")],
        [bi("Name syllable (namakshar)", "नामाक्षर"), bi(f"{first_en} (the four for this nakshatra: {syl_en})", f"{first_hi} (इस नक्षत्र के चार: {syl_hi})")],
        [bi("Varna", "वर्ण"), bi(varna, VARNA_HI[varna])],
        [bi("Vashya", "वश्य"), bi(vashya, VASHYA_HI.get(vashya, vashya))],
        [bi("Yoni", "योनि"), bi(yoni, YONI_HI.get(yoni, yoni))],
        [bi("Gana", "गण"), bi(gana, GANA_HI[gana])],
        [bi("Nadi", "नाड़ी"), bi(nadi, NADI_HI[nadi])],
        [bi("Tatva (element of the Moon sign)", "तत्व (चंद्र राशि का)"), bi(*tat)],
        [bi("Rashi lord", "राशि स्वामी"), P(moon["sign_lord"])],
    ]
    intro = bi("The Avakahada chakra lists the birth Moon's qualities used in naming and in Kundli Milan.",
               "अवकहड़ा चक्र में जन्म चंद्र के वे गुण हैं जो नामकरण और कुंडली मिलान में काम आते हैं।")
    return {"key": "avakahada", "title": bi("Avakahada chakra and name syllable", "अवकहड़ा चक्र और नामाक्षर"), "intro": intro,
            "blocks": [table([bi("Quality", "गुण"), bi("Value", "मान")], rows)]}


def pratyantar(v, now):
    cur = v["dashas"]["vimshottari"]["current"]
    md, ad = cur["mahadasha"]["lord"], cur["antardasha"]
    a, b = dt.date.fromisoformat(ad["start"]), dt.date.fromisoformat(ad["end"])
    total = (b - a).days
    i0 = VIM_ORDER.index(ad["lord"])
    rows, t = [], a
    for k in range(9):
        lord = VIM_ORDER[(i0 + k) % 9]
        e = a + dt.timedelta(days=round(total * (sum(VIM_YEARS[VIM_ORDER[(i0 + j) % 9]] for j in range(k + 1)) / 120)))
        isnow = t.isoformat() <= now < e.isoformat()
        lab = P(lord)
        rows.append([bi(f"{date(t.isoformat())['en']} – {date(e.isoformat())['en']}", f"{date(t.isoformat())['hi']} – {date(e.isoformat())['hi']}"),
                     bi(lab["en"] + (" (current)" if isnow else ""), lab["hi"] + (" (चालू)" if isnow else ""))])
        t = e
    intro = bi(f"The nine sub-sub-periods inside the current {md}–{ad['lord']} period, each in proportion to its lord's Vimshottari years.",
               f"चालू {HS.PLANET.get(md, md)}–{HS.PLANET.get(ad['lord'], ad['lord'])} अवधि के भीतर की नौ प्रत्यंतर दशाएँ, हर एक अपने स्वामी के विंशोत्तरी वर्षों के अनुपात में।")
    return {"key": "pratyantar", "title": bi("Pratyantar dashas (third level)", "प्रत्यंतर दशाएँ (तीसरा स्तर)"), "intro": intro,
            "blocks": [table([bi("Period", "अवधि"), bi("Lord", "स्वामी")], rows)]}


def _rasi_dasha_rows(cycle, start, now, limit=12):
    rows, t = [], start
    for p in cycle[:limit]:
        e = _add_years(t, p["years"])
        isnow = t <= now < e
        s = _sign(p["sign"])
        rows.append([span(t, e), bi(s["en"] + (" (current)" if isnow else ""), s["hi"] + (" (चालू)" if isnow else "")),
                     bi(f"{p['years']} year" + ("" if p["years"] == 1 else "s"), f"{p['years']} वर्ष")])
        t = e
    return rows


def chara(v, now, birth):
    c = v["jaimini"]["chara_dasha_rao"]
    rows = _rasi_dasha_rows(c["first_cycle"], birth, now)
    intro = bi("Jaimini's sign-based dasha as taught by K.N. Rao: each sign runs for a number of years set by where its lord sits.",
               "के.एन. राव द्वारा सिखाई गई जैमिनी की राशि-आधारित दशा: हर राशि उतने वर्ष चलती है जितने उसके स्वामी की स्थिति से तय होते हैं।")
    return {"key": "chara", "title": bi("Chara dasha (Jaimini)", "चर दशा (जैमिनी)"), "intro": intro,
            "blocks": [table([bi("Period", "अवधि"), bi("Sign", "राशि"), bi("Length", "अवधि")], rows)]}


def narayana(v, now, birth):
    n = v["rasi_dashas"]["narayana"]["D-1"]
    rows = _rasi_dasha_rows(n["first_cycle"], birth, now)
    intro = bi(f"Narayana dasha from the Rashi chart, starting from {n['seed']} ({n.get('seed_reason', '')}). It is read for events in the outer world.",
               f"राशि कुंडली से नारायण दशा, {HS.SIGN.get(n['seed'], n['seed'])} से आरंभ। इसे बाहरी जीवन की घटनाओं के लिए पढ़ा जाता है।")
    return {"key": "narayana", "title": bi("Narayana dasha", "नारायण दशा"), "intro": intro,
            "blocks": [table([bi("Period", "अवधि"), bi("Sign", "राशि"), bi("Length", "अवधि")], rows)]}


ARUDHA_USE = {"A1": ("image", "छवि"), "A2": ("wealth as others see it", "दिखने वाला धन"), "A3": ("courage, initiative", "साहस, पहल"),
              "A4": ("home, property", "घर, संपत्ति"), "A5": ("children, creativity", "संतान, रचनात्मकता"), "A6": ("rivals, effort", "प्रतिद्वंद्वी, परिश्रम"),
              "A7": ("partner, business", "साथी, व्यापार"), "A8": ("hidden matters, research", "गुप्त विषय, शोध"), "A9": ("fortune, teachers", "भाग्य, गुरु"),
              "A10": ("work and status", "काम और प्रतिष्ठा"), "A11": ("gains, network", "लाभ, संपर्क"), "A12": ("spending, retreat", "व्यय, एकांत")}


def arudhas(v):
    ar = v["jaimini"]["arudha_padas"]
    rows = []
    for k in [f"A{i}" for i in range(1, 13)]:
        if k in ar:
            u = ARUDHA_USE[k]
            rows.append([bi(k + (" (Arudha Lagna)" if k == "A1" else ""), k + (" (आरूढ़ लग्न)" if k == "A1" else "")), _sign(ar[k]), bi(*u)])
    if ar.get("UL (Upapada Lagna)"):
        rows.append([bi("UL (Upapada)", "उपपद लग्न"), _sign(ar["UL (Upapada Lagna)"]), bi("marriage", "विवाह")])
    blocks = [table([bi("Pada", "पद"), bi("Sign", "राशि"), bi("Shows", "दर्शाता है")], rows)]
    sl = v.get("rasi_dashas", {}).get("special_lagnas")
    if sl:
        names = {"BL": ("Bhava Lagna", "भाव लग्न"), "HL": ("Hora Lagna (wealth)", "होरा लग्न (धन)"),
                 "GL": ("Ghatika Lagna (power, status)", "घटिका लग्न (शक्ति, प्रतिष्ठा)"), "SL": ("Sree Lagna (prosperity)", "श्री लग्न (समृद्धि)")}
        srows = [[bi(*names[k]), bi(f"{sl[k]['sign']} {sl[k]['deg']:.1f}°", f"{HS.SIGN.get(sl[k]['sign'], sl[k]['sign'])} {sl[k]['deg']:.1f}°")]
                 for k in ("BL", "HL", "GL", "SL") if k in sl]
        blocks += [table([bi("Special lagna", "विशेष लग्न"), bi("Position", "स्थिति")], srows),
                   para(bi("Ghatika and Hora Lagna move fast (1.25° and 0.5° per minute of birth time); use them only with a reliable time.",
                           "घटिका और होरा लग्न तेज़ चलते हैं (जन्म समय के हर मिनट में 1.25° और 0.5°); इन्हें केवल विश्वसनीय समय के साथ लें।"))]
    intro = bi("Arudha padas show how each area of life appears to the world; special lagnas are extra reference points from Jaimini and Parashara.",
               "आरूढ़ पद दिखाते हैं कि जीवन का हर क्षेत्र दुनिया को कैसा दिखता है; विशेष लग्न जैमिनी और पाराशर के अतिरिक्त संदर्भ बिंदु हैं।")
    return {"key": "arudhas", "title": bi("Arudha padas and special lagnas", "आरूढ़ पद और विशेष लग्न"), "intro": intro, "blocks": blocks}


def sensitivity(v):
    s = v["sensitivity"]["lagna_time_window_minutes"]
    lg, nv = s["lagna_sign_changes"], s["navamsa_lagna_changes"]
    lag = v["lagna"]["sign"]
    lines = [
        bi(f"The Lagna stays {lag} if the birth time was up to {lg['earlier']} minutes earlier or {lg['later']} minutes later.",
           f"लग्न {HS.SIGN.get(lag, lag)} ही रहता है यदि जन्म समय {lg['earlier']} मिनट पहले या {lg['later']} मिनट बाद तक का हो।"),
        bi(f"The Navamsa Lagna stays the same within {nv['earlier']} minutes earlier and {nv['later']} minutes later.",
           f"नवमांश लग्न {nv['earlier']} मिनट पहले और {nv['later']} मिनट बाद तक वही रहता है।"),
    ]
    te = v.get("time_error", {})
    unstable = [x["varga"] for x in te.get("varga_lagnas", []) if not x.get("stable", True)]
    if te.get("uncertainty_minutes") is not None:
        u = te["uncertainty_minutes"]
        if unstable:
            lines.append(bi(f"With a ±{u} minute doubt in the time, the lagna of these charts could change: {', '.join(unstable)}. Read them lightly.",
                            f"समय में ±{u} मिनट के संदेह से इन चार्टों का लग्न बदल सकता है: {', '.join(unstable)}। इन्हें सावधानी से पढ़ें।"))
        else:
            lines.append(bi(f"With a ±{u} minute doubt in the time, no divisional chart changes its lagna.",
                            f"समय में ±{u} मिनट के संदेह से किसी वर्ग चार्ट का लग्न नहीं बदलता।"))
    ch = v["sensitivity"].get("ayanamsa", {}).get("placements_that_change", [])
    if ch:
        lines.append(bi(f"With another ayanamsa, {len(ch)} nakshatra or pada placements would change; the sign placements stay as shown." if not any("sign" in str(x.get("changes")) for x in ch)
                        else f"With another ayanamsa, {len(ch)} placements would change.",
                        f"दूसरे अयनांश से {len(ch)} नक्षत्र या पद स्थितियाँ बदलेंगी।"))
    intro = bi("How much the chart depends on the exact birth time. A wide window means the main results are safe even if the time is a little off.",
               "कुंडली सटीक जन्म समय पर कितनी निर्भर है। चौड़ी सीमा का अर्थ है कि समय थोड़ा अलग होने पर भी मुख्य परिणाम सुरक्षित हैं।")
    return {"key": "sensitivity", "title": bi("How sure is the chart? (birth-time check)", "कुंडली कितनी पक्की है? (जन्म-समय जाँच)"), "intro": intro,
            "blocks": [items(lines)]}


def bhava_chalit(v):
    sh = v.get("bhava_chalit_shifts") or {}
    if not sh:
        rows = None
    else:
        rows = [[P(p), bi(f"house {x['rashi_house']}", f"भाव {x['rashi_house']}"), bi(f"house {x['chalit_house']}", f"भाव {x['chalit_house']}")] for p, x in sh.items()]
    intro = bi("Bhava chalit places house cusps at the degree of the Lagna. Planets near a sign's edge can fall in the next house; they are listed here.",
               "भाव चलित में भाव-संधि लग्न के अंश पर होती है। राशि के छोर के पास के ग्रह अगले भाव में जा सकते हैं; वे यहाँ दिए हैं।")
    blocks = [table([bi("Planet", "ग्रह"), bi("Rashi chart", "राशि कुंडली"), bi("Bhava chalit", "भाव चलित")], rows)] if rows else \
        [para(bi("Every planet stays in the same house in the bhava chalit chart.", "भाव चलित में हर ग्रह उसी भाव में रहता है।"))]
    return {"key": "bhava_chalit", "title": bi("Bhava chalit", "भाव चलित"), "intro": intro, "blocks": blocks}


def doshas(v, now):
    d = v["doshas"]
    rows = []
    m = d["mangal_dosha"]
    h = m["mars_house"]
    pr = m["present_by_reference"]
    refs = [n for n, k in (("Lagna", "from_lagna"), ("Moon", "from_moon"), ("Venus", "from_venus")) if pr.get(k)]
    refs_hi = {"Lagna": "लग्न", "Moon": "चंद्र", "Venus": "शुक्र"}
    rows.append([bi("Mangal (Manglik)", "मंगल दोष (मांगलिक)"),
                 bi(("Present from " + ", ".join(refs)) if refs else "Not present", ("उपस्थित: " + ", ".join(refs_hi[r] for r in refs) + " से") if refs else "उपस्थित नहीं"),
                 bi(f"Mars is in house {h['from_lagna']} from the Lagna, {h['from_moon']} from the Moon, {h['from_venus']} from Venus. Kundli Milan checks the cancellations for a couple.",
                    f"मंगल लग्न से भाव {h['from_lagna']}, चंद्र से {h['from_moon']}, शुक्र से {h['from_venus']} में है। कुंडली मिलान जोड़े के लिए परिहार जाँचता है।")])
    k = d["kaal_sarp"]
    rows.append([bi("Kaal Sarp", "काल सर्प"),
                 bi("Present" if k.get("present") else ("Partial pattern" if k.get("partial") else "Not present"),
                    "उपस्थित" if k.get("present") else ("आंशिक स्वरूप" if k.get("partial") else "उपस्थित नहीं")),
                 bi("All planets between Rahu and Ketu." if k.get("present") else ("Planets outside the Rahu–Ketu axis: " + ", ".join(k.get("planet_outside_axis", [])) + ". A partial pattern is not counted as the dosha." if k.get("partial") else "Planets lie on both sides of the Rahu–Ketu axis."),
                    "सभी ग्रह राहु और केतु के बीच।" if k.get("present") else ("राहु–केतु अक्ष के बाहर के ग्रह: " + ", ".join(HS.PLANET.get(x, x) for x in k.get("planet_outside_axis", [])) + "। आंशिक स्वरूप दोष नहीं गिना जाता।" if k.get("partial") else "ग्रह राहु–केतु अक्ष के दोनों ओर हैं।"))])
    p = d.get("pitra_dosha_indicators", {})
    pi = [n for n, key in (("Sun with Rahu or Ketu", "sun_with_rahu_or_ketu"), ("Rahu or Ketu in the 9th", "rahu_or_ketu_in_9th"), ("Sun in the 9th", "sun_in_9th")) if p.get(key)]
    pi_hi = {"Sun with Rahu or Ketu": "सूर्य राहु या केतु के साथ", "Rahu or Ketu in the 9th": "नवम में राहु या केतु", "Sun in the 9th": "नवम में सूर्य"}
    rows.append([bi("Pitra indicators", "पितृ दोष संकेत"), bi(", ".join(pi) if pi else "None", ", ".join(pi_hi[x] for x in pi) if pi else "कोई नहीं"),
                 bi("Raw indicators from the 9th house and the Sun; they are read with the whole chart.", "नवम भाव और सूर्य से कच्चे संकेत; इन्हें पूरी कुंडली के साथ पढ़ा जाता है।")])
    rows.append([bi("Gandmool (Moon)", "गंडमूल (चंद्र)"), bi("Yes" if d.get("gandmool_nakshatra_moon") else "No", "हाँ" if d.get("gandmool_nakshatra_moon") else "नहीं"),
                 bi("Moon in Ashwini, Ashlesha, Magha, Jyeshtha, Mula or Revati; families often do a shanti puja.", "चंद्र अश्विनी, आश्लेषा, मघा, ज्येष्ठा, मूल या रेवती में; परिवार प्रायः शांति पूजा करते हैं।")])
    rows.append([bi("Guru-Chandal", "गुरु-चांडाल"), bi("Yes" if d.get("guru_chandal") else "No", "हाँ" if d.get("guru_chandal") else "नहीं"),
                 bi("Jupiter with Rahu.", "गुरु राहु के साथ।")])
    rows.append([bi("Shani-Rahu (Shrapit)", "शनि-राहु (श्रापित)"), bi("Yes" if d.get("shani_rahu") else "No", "हाँ" if d.get("shani_rahu") else "नहीं"),
                 bi("Saturn with Rahu.", "शनि राहु के साथ।")])
    ss = v.get("sade_sati", {})
    cur = ss.get("sade_sati_now")
    phase_hi = {"rising": "पहला चरण", "peak": "मध्य चरण", "setting": "अंतिम चरण"}
    if cur:
        txt = bi(f"Running now ({cur})" if isinstance(cur, str) else "Running now", f"अभी चल रही है")
    elif ss.get("ashtama_shani_now"):
        txt = bi("Ashtama Shani now (Saturn 8th from the Moon)", "अभी अष्टम शनि (चंद्र से आठवाँ शनि)")
    elif ss.get("kantaka_shani_now"):
        txt = bi("Kantaka Shani now (Saturn 4th from the Moon)", "अभी कंटक शनि (चंद्र से चौथा शनि)")
    else:
        txt = bi("Not running now", "अभी नहीं चल रही")
    cyc = [c for c in ss.get("cycles_in_window", []) if c.get("end", "") >= now[:10]]
    nxt = cyc[0] if cyc else None
    rows.append([bi("Sade Sati", "साढ़े साती"), txt,
                 bi(f"Saturn is in house {ss.get('saturn_house_from_moon')} from the Moon." + (f" Next or current cycle: {date(nxt['start'])['en']} – {date(nxt['end'])['en']}." if nxt else ""),
                    f"शनि चंद्र से भाव {ss.get('saturn_house_from_moon')} में है।" + (f" अगला या चालू चक्र: {date(nxt['start'])['hi']} – {date(nxt['end'])['hi']}।" if nxt else ""))])
    intro = bi("Doshas are patterns the tradition watches for. Each has cancellations and remedies in the classical texts, and none of them decides a life on its own.",
               "दोष वे स्वरूप हैं जिन पर परंपरा ध्यान देती है। शास्त्रों में हर दोष के परिहार और उपाय हैं, और कोई भी अकेले जीवन तय नहीं करता।")
    rows = [[a, b, bi(safe(c["en"]), safe(c["hi"]))] for a, b, c in rows]
    return {"key": "doshas", "title": bi("Doshas and Sade Sati", "दोष और साढ़े साती"), "intro": intro,
            "blocks": [table([bi("Pattern", "स्वरूप"), bi("In this chart", "इस कुंडली में"), bi("Detail", "विवरण")], rows)]}


def build_more(c):
    v = c["vedic"]
    now = c["meta"].get("generated_for_date", "")
    birth = v["dashas"]["vimshottari"]["mahadashas"][0]["start"]
    out = []
    for f in ((lambda: doshas(v, now)), (lambda: avakahada(v)), (lambda: pratyantar(v, now)), (lambda: sensitivity(v)),
              (lambda: chara(v, now, birth)), (lambda: narayana(v, now, birth)), (lambda: arudhas(v)), (lambda: bhava_chalit(v))):
        try:
            s = f()
        except (KeyError, TypeError, ValueError, IndexError):
            s = None
        if s:
            out.append(s)
    return out
