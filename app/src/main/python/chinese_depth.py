"""chinese_depth.py - BaZi and Zi Wei depth (v22): Na Yin and the twelve growth phases of the Day Master on each
pillar, the common symbolic stars (Nobleman, Academic, Peach Blossom, Travelling Horse, Canopy), BaZi compatibility of
two people, and for Zi Wei Dou Shu the 'three directions and four squares' (三方四正) of the key palaces and this year's
overlay (流年 palace and the year's four transformations).

Symbolic stars use the most widely shared definitions: Nobleman by the Day Master (甲戊庚 丑未, 乙己 子申, 丙丁 亥酉,
辛 午寅, 壬癸 卯巳); Academic by the Day Master; Peach Blossom, Travelling Horse and Canopy from the year and day
branches. Growth phases use the yang/yin cycle (yang stems forward, yin stems backward). Leanings only.
"""
import datetime as dt

import chinese_calendar as CC
import ziwei as ZW
from app_details import bi, table, para, items

STEMS, BRANCHES = CC.STEMS, CC.BRANCHES
NAYIN = ["海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火", "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土", "霹雳火", "松柏木",
         "长流水", "沙中金", "山下火", "平地木", "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金", "桑柘木", "大溪水", "沙中土", "天上火",
         "石榴木", "大海水"]
NAYIN_EN = ["Sea Metal", "Furnace Fire", "Forest Wood", "Roadside Earth", "Sword Metal", "Mountain Fire", "Stream Water", "City-wall Earth",
            "Wax Metal", "Willow Wood", "Spring Water", "Roof Earth", "Thunder Fire", "Pine Wood", "River Water", "Sand Metal", "Foot-of-hill Fire",
            "Plain Wood", "Wall Earth", "Gold-leaf Metal", "Lamp Fire", "Heavenly Water", "Highway Earth", "Jewellery Metal", "Mulberry Wood",
            "Brook Water", "Sand Earth", "Sky Fire", "Pomegranate Wood", "Ocean Water"]
NAYIN_HI = {"Metal": "धातु", "Fire": "अग्नि", "Wood": "काष्ठ", "Earth": "पृथ्वी", "Water": "जल"}
PHASES = [("长生", "Birth", "जन्म"), ("沐浴", "Bath", "स्नान"), ("冠带", "Cap and belt", "मुकुट"), ("临官", "Office", "पद"), ("帝旺", "Peak", "शिखर"),
          ("衰", "Decline", "ढलान"), ("病", "Weakening", "क्षीणता"), ("死", "Rest", "विश्राम"), ("墓", "Store", "भंडार"), ("绝", "Cut-off", "विराम"),
          ("胎", "Conception", "गर्भ"), ("养", "Nurture", "पोषण")]
BIRTH_BRANCH = {0: 11, 1: 6, 2: 2, 3: 9, 4: 2, 5: 9, 6: 5, 7: 0, 8: 8, 9: 3}      # 长生 position of each stem
NOBLE = {0: (1, 7), 4: (1, 7), 6: (1, 7), 1: (0, 8), 5: (0, 8), 2: (11, 9), 3: (11, 9), 7: (6, 2), 8: (3, 5), 9: (3, 5)}
ACADEMIC = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 0, 8: 2, 9: 3}
GROUP = {8: 0, 0: 0, 4: 0, 2: 1, 6: 1, 10: 1, 5: 2, 9: 2, 1: 2, 11: 3, 3: 3, 7: 3}   # 申子辰, 寅午戌, 巳酉丑, 亥卯未
PEACH = [9, 3, 6, 0]
HORSE = [2, 8, 11, 5]
CANOPY = [4, 10, 1, 7]
STAR_TEXT = {"noble": ("Nobleman (天乙贵人)", "कुलीन सहायक (天乙贵人)", "help from influential people", "प्रभावशाली लोगों से सहायता"),
             "academic": ("Academic (文昌)", "विद्या तारा (文昌)", "study and writing", "पढ़ाई और लेखन"),
             "peach": ("Peach Blossom (桃花)", "आड़ू पुष्प (桃花)", "charm and popularity", "आकर्षण और लोकप्रियता"),
             "horse": ("Travelling Horse (驿马)", "यात्रा अश्व (驿马)", "travel and movement", "यात्रा और गतिशीलता"),
             "canopy": ("Canopy (华盖)", "छत्र (华盖)", "spiritual and artistic depth", "आध्यात्मिक और कलात्मक गहराई")}
PILLAR = {"year": ("Year", "वर्ष"), "month": ("Month", "माह"), "day": ("Day", "दिन"), "hour": ("Hour", "घड़ी")}
EL = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
EL_HI = {"Wood": "काष्ठ", "Fire": "अग्नि", "Earth": "पृथ्वी", "Metal": "धातु", "Water": "जल"}
GEN = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CTRL = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
SIX_HARMONY = {frozenset((0, 1)), frozenset((2, 11)), frozenset((3, 10)), frozenset((4, 9)), frozenset((5, 8)), frozenset((6, 7))}


def _idx(stem, branch):
    return next(n for n in range(60) if n % 10 == stem and n % 12 == branch)


def phase(stem, branch):
    start = BIRTH_BRANCH[stem]
    k = (branch - start) % 12 if stem % 2 == 0 else (start - branch) % 12
    return PHASES[k]


def bazi_sections(b):
    P = b["pillars"]
    dm = STEMS.index(P["day"]["stem"])
    rows = []
    for k in ("year", "month", "day", "hour"):
        if k not in P or not P[k]:
            continue
        s, br = STEMS.index(P[k]["stem"]), BRANCHES.index(P[k]["branch"])
        ny = _idx(s, br) // 2
        ph = phase(dm, br)
        el = NAYIN_EN[ny].split()[-1]
        rows.append([bi(*PILLAR[k]), bi(P[k]["text"]), bi(f"{NAYIN[ny]} {NAYIN_EN[ny]}", f"{NAYIN[ny]} ({NAYIN_HI.get(el, el)})"),
                     bi(f"{ph[0]} {ph[1]}", f"{ph[0]} {ph[2]}")])
    yb, db = BRANCHES.index(P["year"]["branch"]), BRANCHES.index(P["day"]["branch"])
    branches = {k: BRANCHES.index(P[k]["branch"]) for k in P if P.get(k)}
    found = []
    targets = {"noble": set(NOBLE[dm]), "academic": {ACADEMIC[dm]},
               "peach": {PEACH[GROUP[yb]], PEACH[GROUP[db]]}, "horse": {HORSE[GROUP[yb]], HORSE[GROUP[db]]},
               "canopy": {CANOPY[GROUP[yb]], CANOPY[GROUP[db]]}}
    for star, tset in targets.items():
        where = [k for k, br in branches.items() if br in tset]
        if where:
            en, hi, te, th = STAR_TEXT[star]
            found.append([bi(en, hi), bi(", ".join(PILLAR[w][0] for w in where), ", ".join(PILLAR[w][1] for w in where)), bi(te, th)])
    secs = [{"key": "bazi_nayin", "title": bi("BaZi: Na Yin and growth phases", "बाज़ी: ना यिन और विकास चरण"),
             "intro": bi(f"Na Yin is the sound-element of each pillar; the growth phase shows how strong the Day Master {P['day']['stem']} feels in each branch.",
                         f"ना यिन हर स्तंभ का ध्वनि-तत्व है; विकास चरण दिखाता है कि दिवस स्वामी {P['day']['stem']} हर शाखा में कितना बली है।"),
             "blocks": [table([bi("Pillar", "स्तंभ"), bi("Stem-branch", "तना-शाखा"), bi("Na Yin", "ना यिन"), bi("Day Master's phase", "दिवस स्वामी का चरण")], rows)]},
            {"key": "bazi_stars", "title": bi("BaZi: symbolic stars", "बाज़ी: प्रतीकात्मक तारे"),
             "blocks": [table([bi("Star", "तारा"), bi("In pillar", "स्तंभ में"), bi("Theme", "विषय")], found) if found else
                        para(bi("None of the five common symbolic stars falls in this chart's pillars.", "पाँच सामान्य प्रतीकात्मक तारों में से कोई भी इन स्तंभों में नहीं।"))],
             "note": bi("Definitions shared by most schools; the Nobleman is counted from the Day Master.", "अधिकतर परंपराओं में मान्य परिभाषाएँ; कुलीन सहायक दिवस स्वामी से गिना जाता है।")}]
    return secs


def bazi_match(A, B, na, nb):
    """Compatibility of two BaZi charts from chart_engine match_inputs (bazi_branches, bazi_stems, bazi_dm)."""
    def pil(x):
        st, br = dict(x["bazi_stems"]), dict(x["bazi_branches"])
        return {k.lower(): {"stem": STEMS[st[k]], "branch": BRANCHES[br[k]]} for k in br}
    pa, pb = pil(A), pil(B)
    da, db = A["bazi_dm"], B["bazi_dm"]
    ea, eb = EL[da], EL[db]
    if ea == eb:
        dm = ("same element: an easy understanding", "एक ही तत्व: सहज समझ", 2)
    elif GEN[ea] == eb or GEN[eb] == ea:
        giver = na if GEN[ea] == eb else nb
        dm = (f"one feeds the other ({giver} gives support)", f"एक दूसरे को पोषण देता है ({giver} की ओर से सहारा)", 2)
    else:
        dm = ("one element checks the other: respect each other's pace", "एक तत्व दूसरे को नियंत्रित करता है: एक-दूसरे की गति का सम्मान करें", 1)
    rows = [[bi("Day Masters", "दिवस स्वामी"), bi(f"{pa['day']['stem']} {ea} – {pb['day']['stem']} {eb}", f"{pa['day']['stem']} {EL_HI[ea]} – {pb['day']['stem']} {EL_HI[eb]}"), bi(dm[0], dm[1])]]
    score = dm[2]
    for k, lab in (("day", ("Day branches (the spouse palace)", "दिवस शाखाएँ (जीवनसाथी भाव)")), ("year", ("Year branches (families)", "वर्ष शाखाएँ (परिवार)"))):
        x, y = BRANCHES.index(pa[k]["branch"]), BRANCHES.index(pb[k]["branch"])
        if frozenset((x, y)) in SIX_HARMONY:
            r = ("six harmony (六合): warm and close", "छह सामंजस्य (六合): गर्मजोशी और निकटता", 2)
        elif GROUP[x] == GROUP[y]:
            r = ("same three-harmony group (三合): shared aims", "एक ही त्रि-सामंजस्य समूह (三合): साझा लक्ष्य", 2)
        elif (x - y) % 12 == 6:
            r = ("clash (冲): lively differences that need patience", "टकराव (冲): जीवंत मतभेद जिनमें धैर्य चाहिए", 0)
        else:
            r = ("neutral", "सामान्य", 1)
        score += r[2]
        rows.append([bi(*lab), bi(f"{pa[k]['branch']} – {pb[k]['branch']}"), bi(r[0], r[1])])
    lean = "supportive" if score >= 5 else "workable" if score >= 3 else "needs understanding"
    lean_hi = {"supportive": "अनुकूल", "workable": "निभने योग्य", "needs understanding": "समझ और धैर्य माँगता है"}[lean]
    return {"key": "bazi_match", "title": bi("BaZi compatibility", "बाज़ी अनुकूलता"),
            "intro": bi(f"Overall: {lean} ({score} of 6).", f"कुल मिलाकर: {lean_hi} (6 में से {score})।"),
            "blocks": [table([bi("Compared", "तुलना"), bi("Pair", "जोड़ी"), bi("Reading", "फल")], rows)],
            "note": bi("A light check beside Kundli Milan, not a replacement for it.", "कुंडली मिलान के साथ एक हल्की जाँच, उसका विकल्प नहीं।")}


def ziwei_depth(z, today_iso):
    by_branch = {p["branch"]: p for p in z["palaces"]}

    def stars(p):
        return [s["zh"] for s in p["major"]]
    rows = []
    for idx in (0, 8, 4):        # Life, Career, Wealth
        p = z["palaces"][idx]
        b = p["branch"]
        group = [by_branch[(b + k) % 12] for k in (0, 6, 4, 8)]
        st = [s for g in group for s in stars(g)]
        rows.append([bi(f"{p['zh']} {p['en']}", f"{p['zh']} {p['hi']}"), bi(" ".join(g["zh"] for g in group[1:])),
                     bi(", ".join(ZW.MAJOR[s][0] for s in st) or "–", ", ".join(ZW.MAJOR[s][1] for s in st) or "–")])
    today = dt.date.fromisoformat(today_iso)
    ly = CC.to_lunar(today)
    yb, ys = ly["branch_index"], ly["stem_index"]
    annual = by_branch[yb]
    sihua = dict(zip(ZW.SIHUA[ys], "禄权科忌"))
    where = []
    for p in z["palaces"]:
        for s in p["major"] + p["minor"]:
            if s["zh"] in sihua:
                where.append(bi(f"{sihua[s['zh']]}: {s['en']} in {p['en']}", f"{sihua[s['zh']]}: {s['hi']}, {p['hi']} में"))
    return {"key": "zwds_depth", "title": bi("Zi Wei: key palaces and this year", "ज़ी वेई: मुख्य भाव और यह वर्ष"),
            "intro": bi(f"This lunar year ({ly['stem_branch']}) falls on your {annual['en']} palace ({annual['zh']}), the year's Life palace.",
                        f"यह चंद्र वर्ष ({ly['stem_branch']}) आपके {annual['hi']} भाव ({annual['zh']}) पर पड़ता है, जो वर्ष का जीवन भाव है।"),
            "blocks": [table([bi("Palace", "भाव"), bi("Three directions (三方四正)", "तीन दिशाएँ (三方四正)"), bi("Main stars that support it", "सहायक मुख्य तारे")], rows),
                       para(bi("This year's four transformations land on:", "इस वर्ष के चार रूपांतरण यहाँ पड़ते हैं:")), items(where)],
            "note": bi("A palace is read with its opposite and its two trines. Star brightness is not shown because schools differ.",
                       "हर भाव को उसके सामने और दोनों त्रिकोण भावों के साथ पढ़ा जाता है। तारों की चमक नहीं दिखाई गई क्योंकि परंपराएँ अलग हैं।")}
