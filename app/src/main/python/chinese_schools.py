"""chinese_schools.py - v27: the judgement layer of BaZi and Zi Wei Dou Shu.

BaZi: the favourable elements (用神) from the Day Master's strength, the chart's structure (格局) from the month
branch, and a search for days whose own pillar suits the chart. Zi Wei: the flying transformations between palaces
(四化飞星), the month-by-month overlay of the current year, and a note on what each main star stands for.

Every rule used is named in the note under its table, because schools word these differently.
"""
import datetime as dt

import chinese as CH
import chinese_calendar as CC
import ziwei as ZW
from app_details import bi, items, para, table

ELS = ["Wood", "Fire", "Earth", "Metal", "Water"]
EL_HI = {"Wood": "काष्ठ", "Fire": "अग्नि", "Earth": "पृथ्वी", "Metal": "धातु", "Water": "जल"}
EL_ZH = {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"}
GEN = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CTRL = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
ROLE = {"resource": ("Resource: what feeds you", "संसाधन: जो आपको पोषण दे"),
        "companion": ("Companion: your own element", "सहचर: आपका अपना तत्व"),
        "output": ("Output: what you express", "उत्पादन: जो आप व्यक्त करें"),
        "wealth": ("Wealth: what you take hold of", "धन: जिस पर आप अधिकार करें"),
        "officer": ("Officer: what disciplines you", "अधिकारी: जो आपको अनुशासित करे")}
STRUCTURE = {"Direct Officer": ("正官格", "rules, office and a careful name", "नियम, पद और सँभला हुआ नाम"),
             "Seven Killings": ("七杀格", "pressure met head-on", "दबाव का सीधा सामना"),
             "Direct Wealth": ("正财格", "steady earning and thrift", "स्थिर आय और मितव्ययिता"),
             "Indirect Wealth": ("偏财格", "wide and moving money", "चलती-फिरती और विस्तृत कमाई"),
             "Direct Resource": ("正印格", "study, shelter and learning", "अध्ययन, आश्रय और सीख"),
             "Indirect Resource": ("偏印格", "unusual learning and a private mind", "असाधारण सीख और एकांत मन"),
             "Eating God": ("食神格", "making, feeding and ease", "रचना, पोषण और सहजता"),
             "Hurting Officer": ("伤官格", "talent that will not be held in", "प्रतिभा जो बँधकर नहीं रहती"),
             "Friend": ("建禄格", "standing on your own feet", "अपने पैरों पर खड़ा होना"),
             "Rob Wealth": ("月劫格", "sharing and rivalry", "साझा और प्रतिद्वंद्विता")}
STAR_NOTE = {"紫微": ("the emperor: standing, dignity, wanting to be in charge", "सम्राट: प्रतिष्ठा, गरिमा, नेतृत्व की चाह"),
             "天机": ("the strategist: thinking, planning, restlessness", "रणनीतिकार: चिंतन, योजना, बेचैनी"),
             "太阳": ("the sun: giving out, fathers, public life", "सूर्य: देना, पिता, सार्वजनिक जीवन"),
             "武曲": ("the general: money, metal, decisive action", "सेनापति: धन, धातु, निर्णायक कर्म"),
             "天同": ("the child: ease, enjoyment, slow starts", "शिशु: सहजता, आनंद, धीमी शुरुआत"),
             "廉贞": ("the officer: discipline, charm, extremes", "अधिकारी: अनुशासन, आकर्षण, अति"),
             "天府": ("the treasury: keeping, caution, comfort", "कोष: संचय, सावधानी, सुख"),
             "太阴": ("the moon: mothers, quiet wealth, feeling", "चंद्र: माता, शांत समृद्धि, भावना"),
             "贪狼": ("the wolf: desire, talent, many interests", "भेड़िया: इच्छा, प्रतिभा, अनेक रुचियाँ"),
             "巨门": ("the gate: speech, doubt, getting to the bottom of things", "द्वार: वाणी, संदेह, तह तक जाना"),
             "天相": ("the minister: service, fairness, helping others decide", "मंत्री: सेवा, निष्पक्षता, दूसरों को निर्णय में सहारा"),
             "天梁": ("the elder: protection, advice, old knowledge", "ज्येष्ठ: संरक्षण, सलाह, पुराना ज्ञान"),
             "七杀": ("the commander: force, change, doing it alone", "सेनानायक: बल, परिवर्तन, अकेले करना"),
             "破军": ("the breaker: clearing away before building", "विध्वंसक: बनाने से पहले हटाना")}
GOD_HI = {"Direct Officer": "正官 प्रत्यक्ष अधिकारी", "Seven Killings": "七杀 सप्त घातक", "Direct Wealth": "正财 प्रत्यक्ष धन",
          "Indirect Wealth": "偏财 अप्रत्यक्ष धन", "Direct Resource": "正印 प्रत्यक्ष संसाधन", "Indirect Resource": "偏印 अप्रत्यक्ष संसाधन",
          "Eating God": "食神 भोजन देव", "Hurting Officer": "伤官 आहत अधिकारी", "Friend": "比肩 सहचर", "Rob Wealth": "劫财 धन हरण"}
ANIMAL_HI = dict(zip(CH.ANIMAL, ["चूहा", "बैल", "बाघ", "खरगोश", "ड्रैगन", "साँप", "घोड़ा", "बकरी", "बंदर", "मुर्गा", "कुत्ता", "सूअर"]))
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _god(name):
    return name.split(" (")[0]


# ------------------------------------------------------------------ F115 favourable elements
def useful_elements(b):
    dm = b["day_master"]
    el = dm["element"]
    h = b["day_master_strength_heuristic"]
    season = h["month_season_status"][:1]
    strong = (season in "旺相" and h["supporters"] >= h["drainers"]) or h["supporters"] >= h["drainers"] * 2
    resource = next(k for k, v in GEN.items() if v == el)
    output = GEN[el]
    wealth = CTRL[el]
    officer = next(k for k, v in CTRL.items() if v == el)
    roles = [("resource", resource), ("companion", el), ("output", output), ("wealth", wealth), ("officer", officer)]
    good = {output, wealth, officer} if strong else {resource, el}
    rows = [[bi(*ROLE[r]), bi(f"{EL_ZH[e]} {e}", f"{EL_ZH[e]} {EL_HI[e]}"),
             bi("favourable", "अनुकूल") if e in good else bi("already enough", "पहले से पर्याप्त")] for r, e in roles]
    lean = ("strong", "बली") if strong else ("not strong", "बली नहीं")
    picks = ", ".join(sorted(good))
    picks_hi = ", ".join(EL_HI[x] for x in sorted(good))
    return {"key": "bazi_useful", "title": bi("BaZi: favourable elements (用神)", "बाज़ी: अनुकूल तत्व (用神)"),
            "intro": bi(f"The Day Master {dm['stem']} ({el}) reads as {lean[0]}, so the chart leans on {picks}.",
                        f"दिवस स्वामी {dm['stem']} ({EL_HI[el]}) {lean[1]} दिखता है, इसलिए कुंडली {picks_hi} पर टिकती है।"),
            "blocks": [table([bi("Role", "भूमिका"), bi("Element", "तत्व"), bi("For this chart", "इस कुंडली के लिए")], rows)],
            "note": bi("The usual balancing rule: a strong Day Master leans on what drains or checks it, a weak one on what feeds and joins it. "
                       "Strength here is the season plus weighted support, which is a screen; a practitioner judges special structures separately.",
                       "सामान्य संतुलन नियम: बली दिवस स्वामी उसे खर्च या नियंत्रित करने वाले पर टिकता है, निर्बल उसे पोषण देने और साथ देने वाले पर। "
                       "यहाँ बल ऋतु और भारित सहारे से निकाला गया है, जो एक छानबीन है; विशेष संरचनाओं का निर्णय जानकार अलग से करते हैं।")}


# ------------------------------------------------------------------ F117 structure
def structure(b):
    P = b["pillars"]
    mb = CH.BRANCHES.index(P["month"]["branch"])
    dm = CH.STEMS.index(P["day"]["stem"])
    hidden = CH.HIDDEN[mb]
    visible = {CH.STEMS.index(P[k]["stem"]) for k in P if P.get(k)}
    pick = next((h for h in hidden if h in visible), hidden[0])
    god = _god(CH.ten_god(dm, pick))
    zh, te, th = STRUCTURE.get(god, ("–", god, god))
    rows = [[bi("Month branch", "माह शाखा"), bi(P["month"]["branch"])],
            [bi("Hidden stems there", "उसमें छिपे तने"), bi(" ".join(CH.STEMS[h] for h in hidden))],
            [bi("The one that leads", "जो अग्रणी है"), bi(CH.STEMS[pick] + (" (also in the open)" if pick in visible else " (hidden only)"),
                                                            CH.STEMS[pick] + (" (खुले में भी)" if pick in visible else " (केवल छिपा)"))],
            [bi("Structure", "संरचना"), bi(f"{zh} {god}", GOD_HI.get(god, zh))]]
    return {"key": "bazi_structure", "title": bi("BaZi: the chart's structure (格局)", "बाज़ी: कुंडली की संरचना (格局)"),
            "intro": bi(f"This reads as {zh}: {te}.", f"यह {zh} के रूप में पढ़ी जाती है: {th}।"),
            "blocks": [table([bi("Step", "चरण"), bi("Value", "मान")], rows)],
            "note": bi("Taken the common way: the month branch's leading hidden stem, preferring one that also stands in the open. "
                       "Special and following structures are not judged here.",
                       "सामान्य विधि से: माह शाखा का अग्रणी छिपा तना, वरीयता उसे जो खुले में भी खड़ा हो। "
                       "विशेष और अनुगामी संरचनाओं का निर्णय यहाँ नहीं किया गया।")}


# ------------------------------------------------------------------ F126 date search
def good_days(b, start_iso, days=60):
    dm = CH.STEMS.index(b["pillars"]["day"]["stem"])
    db = CH.BRANCHES.index(b["pillars"]["day"]["branch"])
    h = b["day_master_strength_heuristic"]
    season = h["month_season_status"][:1]
    strong = (season in "旺相" and h["supporters"] >= h["drainers"]) or h["supporters"] >= h["drainers"] * 2
    want = {"Eating God", "Direct Wealth", "Indirect Wealth", "Direct Officer"} if strong else {"Direct Resource", "Friend", "Indirect Resource"}
    d0 = dt.date.fromisoformat(start_iso)
    rows = []
    for k in range(days):
        d = d0 + dt.timedelta(days=k)
        i = CH.day_index(d)
        s, br = i % 10, i % 12
        if (br - db) % 12 == 6:                      # the day clashes with the chart's own day branch
            continue
        god = _god(CH.ten_god(dm, s))
        if god in want:
            rows.append([bi(d.strftime("%d %b %Y"), f"{d.day} {MONTH_HI[d.month - 1]} {d.year}"),
                         bi(CH.STEMS[s] + CH.BRANCHES[br]), bi(god, GOD_HI.get(god, god)), bi(CH.ANIMAL[br], ANIMAL_HI[CH.ANIMAL[br]])])
        if len(rows) >= 12:
            break
    return {"key": "bazi_days", "title": bi("BaZi: days that suit this chart", "बाज़ी: इस कुंडली के अनुकूल दिन"),
            "intro": bi("Days in the next two months whose own stem brings what this chart leans on, leaving out days that clash with its day branch.",
                        "अगले दो महीनों के वे दिन जिनका तना वही लाता है जिस पर यह कुंडली टिकती है, और जो इसकी दिवस शाखा से नहीं टकराते।"),
            "blocks": [table([bi("Date", "तिथि"), bi("Day pillar", "दिवस स्तंभ"), bi("Brings", "क्या लाता है"), bi("Animal", "पशु")], rows) if rows else
                       para(bi("No day in the next two months fits both tests.", "अगले दो महीनों में कोई दिन दोनों कसौटियों पर खरा नहीं।"))],
            "note": bi("A light filter on the day pillar only. For a wedding or a move, read it beside the Tong Shu day officers and the Vedic Muhurta.",
                       "केवल दिवस स्तंभ पर एक हल्की छलनी। विवाह या स्थानांतरण के लिए इसे टोंग शू के दिवस अधिकारियों और वैदिक मुहूर्त के साथ पढ़ें।")}


# ------------------------------------------------------------------ F132 flying transformations
def flying(z):
    by_branch = {p["branch"]: p for p in z["palaces"]}
    star_at = {}
    for p in z["palaces"]:
        for s in p["major"] + p["minor"]:
            star_at[s["zh"]] = p
    rows = []
    for p in z["palaces"]:
        si = CH.STEMS.index(p["stem_zh"])
        out = []
        for star, mark in zip(ZW.SIHUA[si], "禄权科忌"):
            tgt = star_at.get(star)
            if tgt:
                out.append((mark, star, tgt))
        if not out:
            continue
        rows.append([bi(f"{p['zh']} {p['en']}", f"{p['zh']} {p['hi']}"), bi(p["stem_zh"]),
                     bi(", ".join(f"{m}→{t['en']}" for m, _s, t in out), ", ".join(f"{m}→{t['hi']}" for m, _s, t in out))])
    life = z["palaces"][0]
    si = CH.STEMS.index(life["stem_zh"])
    focus = []
    for star, mark in zip(ZW.SIHUA[si], "禄权科忌"):
        tgt = star_at.get(star)
        if tgt:
            nm = ZW.MAJOR.get(star) or ZW.MINOR.get(star) or (star, star)
            focus.append(bi(f"{mark} {ZW.TRANSFORM[mark][0]}: {nm[0]} lands in {tgt['en']}",
                            f"{mark} {ZW.TRANSFORM[mark][1]}: {nm[1]}, {tgt['hi']} में"))
    return {"key": "zwds_flying", "title": bi("Zi Wei: transformations flying between palaces", "ज़ी वेई: भावों के बीच उड़ते रूपांतरण"),
            "intro": bi("Each palace has its own stem, and that stem sends four transformations out to wherever those stars sit.",
                        "हर भाव का अपना तना है, और वह तना चार रूपांतरण वहाँ भेजता है जहाँ वे तारे बैठे हैं।"),
            "blocks": [para(bi("From the Life palace:", "जीवन भाव से:")), items(focus or [bi("–")]),
                       table([bi("From palace", "किस भाव से"), bi("Its stem", "उसका तना"), bi("Sends to", "कहाँ भेजता है")], rows)],
            "note": bi("The flying-star method of Zi Wei: a palace is linked to the palaces its own transformations reach. 禄 abundance, 权 authority, 科 recognition, 忌 obstacle.",
                       "ज़ी वेई की उड़ते-तारे पद्धति: कोई भाव उन भावों से जुड़ता है जहाँ उसके अपने रूपांतरण पहुँचते हैं। 禄 समृद्धि, 权 अधिकार, 科 प्रतिष्ठा, 忌 बाधा।")}


# ------------------------------------------------------------------ F136 finer overlays
def monthly(z, today_iso):
    today = dt.date.fromisoformat(today_iso)
    ly = CC.to_lunar(today)
    by_branch = {p["branch"]: p for p in z["palaces"]}
    annual = by_branch[ly["branch_index"]]
    rows = []
    for m in range(1, 13):
        b = (annual["branch"] + (m - 1)) % 12
        p = by_branch[b]
        stars = ", ".join(s["en"] for s in p["major"]) or "–"
        stars_hi = ", ".join(s["hi"] for s in p["major"]) or "–"
        rows.append([bi(f"Month {m}", f"माह {m}"), bi(f"{p['zh']} {p['en']}", f"{p['zh']} {p['hi']}"), bi(stars, stars_hi),
                     bi("this lunar month", "यही चंद्र माह") if m == ly["month"] else bi("")])
    return {"key": "zwds_monthly", "title": bi(f"Zi Wei: the months of the year {ly['stem_branch']}", f"ज़ी वेई: {ly['stem_branch']} वर्ष के माह"),
            "blocks": [table([bi("Lunar month", "चंद्र माह"), bi("Palace", "भाव"), bi("Main stars", "मुख्य तारे"), bi("", "")], rows)],
            "note": bi("Counted the common way: the year's palace is the first lunar month, then one palace forward for each month. "
                       "Schools count this differently, so it is given as a layer to look at, not a verdict.",
                       "सामान्य विधि से गिना गया: वर्ष का भाव पहला चंद्र माह है, फिर हर माह एक भाव आगे। "
                       "परंपराएँ इसे अलग-अलग गिनती हैं, इसलिए यह देखने की एक परत है, निर्णय नहीं।")}


# ------------------------------------------------------------------ F140 interpretation notes
def star_notes():
    rows = [[bi(zh), bi(ZW.MAJOR[zh][0], ZW.MAJOR[zh][1]), bi(te, th)] for zh, (te, th) in STAR_NOTE.items()]
    rows += [[bi(zh), bi(en, hi), bi("a helping star", "सहायक तारा") if zh in ZW.LUCKY else bi("a testing star", "परीक्षा लेने वाला तारा")]
             for zh, (en, hi) in ZW.MINOR.items()]
    return {"key": "zwds_notes", "title": bi("Zi Wei: what each star stands for", "ज़ी वेई: हर तारा किसका प्रतीक है"),
            "blocks": [table([bi("Star", "तारा"), bi("Name", "नाम"), bi("Stands for", "किसका प्रतीक")], rows)],
            "note": bi("The themes most schools agree on, as a reading aid. A star is read with its palace, the stars beside it and the transformations reaching it.",
                       "वे विषय जिन पर अधिकतर परंपराएँ सहमत हैं, पढ़ने में सहायता के लिए। तारे को उसके भाव, साथ के तारों और उस तक पहुँचते रूपांतरणों के साथ पढ़ा जाता है।")}


def build(c, today_iso=None):
    out = []
    b = c.get("bazi")
    today = today_iso or c["meta"]["generated_for_date"]

    def add(f, *a):
        try:
            r = f(*a)
        except Exception:
            return
        if r:
            out.append(r)
    if b:
        add(useful_elements, b)
        add(structure, b)
        add(good_days, b, today)
    return out


def ziwei_sections(z, today_iso):
    out = []
    for f, a in ((flying, (z,)), (monthly, (z, today_iso)), (star_notes, ())):
        try:
            out.append(f(*a))
        except Exception:
            pass
    return out
