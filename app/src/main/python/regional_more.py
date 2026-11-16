"""regional_more.py - v28: the regional traditions that can be checked.

Sanmeigaku (Japanese) and Saju (Korean) read the same four pillars the BaZi section already computes, so they are given
as that chart in each tradition's own names and readings rather than as a second calculation. The Thai almanac gives the
Buddhist Era year, the Thai zodiac animal and the day colour. The 13 Moon calendar gives the moon and day of a year that
starts on 26 July, with 25 July as the day out of time.

Left out, and why: Mongolian and Tibetan modules and Qi Men and Da Liu Ren have no reference here to check the
arithmetic against; Mahabote names one of its houses for death; the Dreamspell kin number needs a correlation anchor
this file cannot verify, so only the 13 Moon date is given.
"""
import datetime as dt

import chinese as CH
from app_details import bi, para, table

JP_STEM = ["kinoe", "kinoto", "hinoe", "hinoto", "tsuchinoe", "tsuchinoto", "kanoe", "kanoto", "mizunoe", "mizunoto"]
JP_BRANCH = ["ne", "ushi", "tora", "u", "tatsu", "mi", "uma", "hitsuji", "saru", "tori", "inu", "i"]
KR_STEM = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
KR_BRANCH = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
KR_STEM_ROM = ["gap", "eul", "byeong", "jeong", "mu", "gi", "gyeong", "sin", "im", "gye"]
KR_BRANCH_ROM = ["ja", "chuk", "in", "myo", "jin", "sa", "o", "mi", "sin", "yu", "sul", "hae"]
PILLAR = [("Year", "वर्ष", "年柱", "년주"), ("Month", "माह", "月柱", "월주"), ("Day", "दिन", "日柱", "일주"), ("Hour", "घड़ी", "時柱", "시주")]
THAI_ANIMAL = [("Chuat", "ชวด", "Rat", "चूहा"), ("Chalu", "ฉลู", "Ox", "बैल"), ("Khan", "ขาล", "Tiger", "बाघ"), ("Tho", "เถาะ", "Rabbit", "खरगोश"),
               ("Marong", "มะโรง", "Dragon", "ड्रैगन"), ("Maseng", "มะเส็ง", "Snake", "साँप"), ("Mamia", "มะเมีย", "Horse", "घोड़ा"),
               ("Mamae", "มะแม", "Goat", "बकरी"), ("Wok", "วอก", "Monkey", "बंदर"), ("Raka", "ระกา", "Rooster", "मुर्गा"),
               ("Cho", "จอ", "Dog", "कुत्ता"), ("Kun", "กุน", "Pig", "सूअर")]
THAI_DAY = [("Monday", "सोमवार", "Yellow", "पीला"), ("Tuesday", "मंगलवार", "Pink", "गुलाबी"), ("Wednesday", "बुधवार", "Green", "हरा"),
            ("Thursday", "गुरुवार", "Orange", "नारंगी"), ("Friday", "शुक्रवार", "Blue", "नीला"), ("Saturday", "शनिवार", "Purple", "बैंगनी"),
            ("Sunday", "रविवार", "Red", "लाल")]
MOONS = [("Magnetic Bat", "चुंबकीय चमगादड़"), ("Lunar Scorpion", "चंद्र बिच्छू"), ("Electric Deer", "विद्युत हिरण"),
         ("Self-Existing Owl", "स्वयंभू उल्लू"), ("Overtone Peacock", "अनुनाद मोर"), ("Rhythmic Lizard", "लयबद्ध छिपकली"),
         ("Resonant Monkey", "प्रतिध्वनि वानर"), ("Galactic Hawk", "गैलेक्टिक बाज"), ("Solar Jaguar", "सौर जगुआर"),
         ("Planetary Dog", "ग्रहीय श्वान"), ("Spectral Serpent", "वर्णक्रम सर्प"), ("Crystal Rabbit", "क्रिस्टल खरगोश"),
         ("Cosmic Turtle", "ब्रह्मांडीय कछुआ")]
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _idx(p):
    return CH.STEMS.index(p["stem"]), CH.BRANCHES.index(p["branch"])


def sanmeigaku(b):
    rows = []
    for k, (en, hi, jp, _kr) in zip(("year", "month", "day", "hour"), PILLAR):
        p = b["pillars"].get(k)
        if not p:
            continue
        s, br = _idx(p)
        rows.append([bi(f"{en} ({jp})", f"{hi} ({jp})"), bi(p["text"]),
                     bi(f"{JP_STEM[s]}-{JP_BRANCH[br]}", f"{JP_STEM[s]}-{JP_BRANCH[br]}")])
    return {"key": "sanmeigaku", "title": bi("Sanmeigaku (算命学): the same pillars in Japanese", "सानमेइगाकु (算命学): वही स्तंभ जापानी में"),
            "blocks": [table([bi("Pillar", "स्तंभ"), bi("Characters", "अक्षर"), bi("Japanese reading", "जापानी उच्चारण")], rows)],
            "note": bi("Sanmeigaku and Shichuusuimei read the four pillars the BaZi section already computes; only the names and readings differ. "
                       "Their own judgement methods are not applied here.",
                       "सानमेइगाकु और शिचूसुइमेइ उन्हीं चार स्तंभों को पढ़ते हैं जो बाज़ी खंड पहले ही निकालता है; केवल नाम और उच्चारण अलग हैं। "
                       "उनकी अपनी निर्णय पद्धतियाँ यहाँ लागू नहीं की गईं।")}


def saju(b):
    rows = []
    for k, (en, hi, _jp, kr) in zip(("year", "month", "day", "hour"), PILLAR):
        p = b["pillars"].get(k)
        if not p:
            continue
        s, br = _idx(p)
        rows.append([bi(f"{en} ({kr})", f"{hi} ({kr})"), bi(p["text"]),
                     bi(f"{KR_STEM[s]}{KR_BRANCH[br]} ({KR_STEM_ROM[s]}-{KR_BRANCH_ROM[br]})",
                        f"{KR_STEM[s]}{KR_BRANCH[br]} ({KR_STEM_ROM[s]}-{KR_BRANCH_ROM[br]})")])
    return {"key": "saju", "title": bi("Saju (사주): the same pillars in Korean", "साजू (사주): वही स्तंभ कोरियाई में"),
            "blocks": [table([bi("Pillar", "स्तंभ"), bi("Characters", "अक्षर"), bi("Korean reading", "कोरियाई उच्चारण")], rows)],
            "note": bi("Saju Palja reads the same four pillars. The Korean year boundary follows Li Chun as the BaZi section does.",
                       "साजू पालजा उन्हीं चार स्तंभों को पढ़ता है। कोरियाई वर्ष की सीमा भी ली चुन से है, जैसी बाज़ी खंड में।")}


def thai(c):
    d = dt.date.fromisoformat(c["time_pipeline"]["local_civil"][:10])
    be = d.year + 543                                   # the Thai Buddhist Era, counted from 1 January since 1941
    animal = THAI_ANIMAL[(d.year - 4) % 12]
    day = THAI_DAY[d.weekday()]
    rows = [[bi("Buddhist Era year", "बौद्ध संवत् वर्ष"), bi(f"BE {be}", f"बु.सं. {be}")],
            [bi("Thai zodiac animal", "थाई राशि पशु"), bi(f"{animal[1]} {animal[0]} ({animal[2]})", f"{animal[1]} {animal[0]} ({animal[3]})")],
            [bi("Day of birth", "जन्म का वार"), bi(day[0], day[1])],
            [bi("Colour of that day", "उस वार का रंग"), bi(day[2], day[3])]]
    return {"key": "thai", "title": bi("Thai almanac", "थाई पंचांग"),
            "blocks": [table([bi("Item", "विवरण"), bi("Value", "मान")], rows)],
            "note": bi("The Buddhist Era runs 543 years ahead of the common era and has started on 1 January since 1941. "
                       "The day colour is the everyday Thai custom; the animal year follows the Chinese cycle with Thai names.",
                       "बौद्ध संवत् ईस्वी से 543 वर्ष आगे है और 1941 से 1 जनवरी को शुरू होता है। "
                       "वार का रंग थाई लोक-प्रथा है; पशु वर्ष चीनी चक्र के अनुसार है, थाई नामों के साथ।")}


def thirteen_moon(c):
    """The 13 Moon calendar date: a year of 13 moons of 28 days from 26 July, with 25 July as the day out of time."""
    d = dt.date.fromisoformat(c["time_pipeline"]["local_civil"][:10])
    start_year = d.year if (d.month, d.day) >= (7, 26) else d.year - 1
    start = dt.date(start_year, 7, 26)
    n = (d - start).days
    # the 13 Moon year ignores 29 February, so a leap day inside the year is not counted
    leap_day = dt.date(start_year + 1, 2, 29) if _is_leap(start_year + 1) else None
    if leap_day and start < leap_day <= d:
        n -= 1
    if d.month == 7 and d.day == 25:
        return {"key": "thirteen_moon", "title": bi("13 Moon calendar", "13 चंद्र पंचांग"),
                "intro": bi("Born on the Day Out of Time, the day that belongs to no moon.", "समय से बाहर के दिन जन्म, वह दिन जो किसी चंद्र का नहीं है।"),
                "blocks": [para(bi("25 July is the day out of time in this calendar.", "इस पंचांग में 25 जुलाई समय से बाहर का दिन है।"))],
                "note": bi("A modern calendar of thirteen moons of twenty-eight days, not a Maya one; the ancient Maya counts are in the Maya calendar section.",
                           "अट्ठाईस दिन के तेरह चंद्रों वाला एक आधुनिक पंचांग, माया का नहीं; प्राचीन माया गणनाएँ माया पंचांग खंड में हैं।")}
    moon, day = n // 28, n % 28
    moon = min(moon, 12)
    nm = MOONS[moon]
    return {"key": "thirteen_moon", "title": bi("13 Moon calendar", "13 चंद्र पंचांग"),
            "intro": bi(f"Moon {moon + 1} of 13, day {day + 1} of 28: the {nm[0]} moon.",
                        f"13 में से {moon + 1}वाँ चंद्र, 28 में से {day + 1}वाँ दिन: {nm[1]} चंद्र।"),
            "blocks": [table([bi("Item", "विवरण"), bi("Value", "मान")],
                             [[bi("Year began", "वर्ष आरंभ"), bi(f"26 July {start_year}", f"26 जुलाई {start_year}")],
                              [bi("Moon", "चंद्र"), bi(f"{moon + 1} · {nm[0]}", f"{moon + 1} · {nm[1]}")],
                              [bi("Day of the moon", "चंद्र का दिन"), bi(f"{day + 1} of 28", f"28 में से {day + 1}")]])],
            "note": bi("Thirteen moons of twenty-eight days make 364; 25 July is the day out of time and 29 February is not counted. "
                       "A modern calendar, not an ancient Maya one.",
                       "अट्ठाईस दिन के तेरह चंद्र मिलकर 364 होते हैं; 25 जुलाई समय से बाहर का दिन है और 29 फ़रवरी नहीं गिनी जाती। "
                       "यह एक आधुनिक पंचांग है, प्राचीन माया नहीं।")}


def _is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def build(c):
    out = []
    b = c.get("bazi")
    for f, a in (((sanmeigaku, (b,)), (saju, (b,))) if b else ()) + ((thai, (c,)), (thirteen_moon, (c,))):
        try:
            r = f(*a)
        except Exception:
            r = None
        if r:
            out.append(r)
    return out
