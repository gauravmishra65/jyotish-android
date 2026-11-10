"""ziwei.py - Zi Wei Dou Shu (紫微斗数) natal chart (v17), the common Quanshu (全书) placement rules.

Computed: the twelve palaces with their stems (五虎遁), the Life (命) and Body (身) palaces, the Five-Element bureau
(五行局, from the Na Yin of the Life palace), the fourteen major stars, the six lucky and six unlucky auxiliary stars
plus Lu Cun and Tian Ma, the four transformations (四化) of the birth year, the Life and Body masters, and the ten-year
periods (大限). Not computed: star brightness (schools differ), annual and monthly overlays, interpretation.

Conventions, stated with the result:
* The lunar date comes from chinese_calendar (China Standard Time). The hour is the double hour of the birth's local
  clock time; 23:00-24:00 is the Zi hour of the NEXT lunar day.
* A leap month counts as its own month for days 1-15 and as the following month from day 16.
* Positions are branch indices: Zi 子 = 0 ... Hai 亥 = 11.
"""
import datetime as dt

import chinese_calendar as CC

STEMS, BRANCHES = CC.STEMS, CC.BRANCHES
PALACES = [("命宫", "Life", "जीवन"), ("兄弟", "Siblings", "भाई-बहन"), ("夫妻", "Spouse", "जीवनसाथी"), ("子女", "Children", "संतान"),
           ("财帛", "Wealth", "धन"), ("疾厄", "Energy and rest", "ऊर्जा और विश्राम"), ("迁移", "Travel", "यात्रा"), ("交友", "Friends", "मित्र"),
           ("官禄", "Career", "करियर"), ("田宅", "Property", "संपत्ति"), ("福德", "Inner contentment", "आंतरिक संतोष"), ("父母", "Parents", "माता-पिता")]
MAJOR = {"紫微": ("Zi Wei", "ज़ी वेई"), "天机": ("Tian Ji", "तियान जी"), "太阳": ("Tai Yang (Sun)", "ताई यांग (सूर्य)"), "武曲": ("Wu Qu", "वू चू"),
         "天同": ("Tian Tong", "तियान तोंग"), "廉贞": ("Lian Zhen", "लियान झेन"), "天府": ("Tian Fu", "तियान फू"), "太阴": ("Tai Yin (Moon)", "ताई यिन (चंद्र)"),
         "贪狼": ("Tan Lang", "तान लांग"), "巨门": ("Ju Men", "जू मेन"), "天相": ("Tian Xiang", "तियान श्यांग"), "天梁": ("Tian Liang", "तियान लियांग"),
         "七杀": ("Qi Sha", "ची शा"), "破军": ("Po Jun", "पो जुन")}
MINOR = {"文昌": ("Wen Chang", "वेन चांग"), "文曲": ("Wen Qu", "वेन चू"), "左辅": ("Zuo Fu", "ज़ुओ फू"), "右弼": ("You Bi", "यो बी"),
         "天魁": ("Tian Kui", "तियान कुई"), "天钺": ("Tian Yue", "तियान युए"), "禄存": ("Lu Cun", "लू चुन"), "天马": ("Tian Ma", "तियान मा"),
         "擎羊": ("Qing Yang", "चिंग यांग"), "陀罗": ("Tuo Luo", "तुओ लुओ"), "火星": ("Huo Xing", "हुओ शिंग"), "铃星": ("Ling Xing", "लिंग शिंग"),
         "地空": ("Di Kong", "दी कोंग"), "地劫": ("Di Jie", "दी जिए")}
LUCKY = {"文昌", "文曲", "左辅", "右弼", "天魁", "天钺"}
TRANSFORM = {"禄": ("Lu (abundance)", "लू (समृद्धि)"), "权": ("Quan (authority)", "चुआन (अधिकार)"), "科": ("Ke (recognition)", "के (प्रतिष्ठा)"),
             "忌": ("Ji (obstacle)", "जी (बाधा)")}
SIHUA = {0: ("廉贞", "破军", "武曲", "太阳"), 1: ("天机", "天梁", "紫微", "太阴"), 2: ("天同", "天机", "文昌", "廉贞"), 3: ("太阴", "天同", "天机", "巨门"),
         4: ("贪狼", "太阴", "右弼", "天机"), 5: ("武曲", "贪狼", "天梁", "文曲"), 6: ("太阳", "武曲", "太阴", "天同"), 7: ("巨门", "太阳", "文曲", "文昌"),
         8: ("天梁", "紫微", "左辅", "武曲"), 9: ("破军", "巨门", "太阴", "贪狼")}
NAYIN = "金火木土金火水土金木水土火木水金火木土金火水土金木水土火木水"
BUREAU = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}
BUREAU_NAME = {2: ("水二局", "Water 2", "जल 2"), 3: ("木三局", "Wood 3", "काष्ठ 3"), 4: ("金四局", "Metal 4", "धातु 4"),
               5: ("土五局", "Earth 5", "पृथ्वी 5"), 6: ("火六局", "Fire 6", "अग्नि 6")}
LIFE_MASTER = {0: "贪狼", 1: "巨门", 2: "禄存", 3: "文曲", 4: "廉贞", 5: "武曲", 6: "破军", 7: "武曲", 8: "廉贞", 9: "文曲", 10: "禄存", 11: "巨门"}
BODY_MASTER = {0: "火星", 6: "火星", 1: "天相", 7: "天相", 2: "天梁", 8: "天梁", 3: "天同", 9: "天同", 4: "文昌", 10: "文昌", 5: "天机", 11: "天机"}
KUI_YUE = {0: (1, 7), 4: (1, 7), 6: (1, 7), 1: (0, 8), 5: (0, 8), 2: (11, 9), 3: (11, 9), 7: (6, 2), 8: (3, 5), 9: (3, 5)}
LUCUN = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
TIANMA = {2: 8, 6: 8, 10: 8, 8: 2, 0: 2, 4: 2, 5: 11, 9: 11, 1: 11, 11: 5, 3: 5, 7: 5}
HUO_LING = {2: (1, 3), 6: (1, 3), 10: (1, 3), 8: (2, 10), 0: (2, 10), 4: (2, 10), 5: (3, 10), 9: (3, 10), 1: (3, 10), 11: (9, 10), 3: (9, 10), 7: (9, 10)}


def hour_branch(hhmm):
    h, m = int(hhmm[:2]), int(hhmm[3:5])
    return ((h * 60 + m + 60) // 120) % 12


def _idx60(stem, branch):
    return next(n for n in range(60) if n % 10 == stem and n % 12 == branch)


def ziwei_position(bureau, day):
    x = 0
    while (day + x) % bureau:
        x += 1
    q = (day + x) // bureau
    return (2 + q - 1 + (x if x % 2 == 0 else -x)) % 12


def chart(date_iso, time_hhmm, gender):
    d = dt.date.fromisoformat(date_iso)
    hb = hour_branch(time_hhmm)
    late_zi = int(time_hhmm[:2]) == 23
    lunar = CC.to_lunar(d + dt.timedelta(days=1) if late_zi else d)
    ys, yb = lunar["stem_index"], lunar["branch_index"]
    m = lunar["month"]
    if lunar["leap"] and lunar["day"] > 15:
        m = m % 12 + 1
    day = lunar["day"]
    life = (2 + (m - 1) - hb) % 12
    body = (2 + (m - 1) + hb) % 12
    s_yin = (ys % 5) * 2 + 2
    stem_of = {b: (s_yin + (b - 2) % 12) % 10 for b in range(12)}
    bureau = BUREAU[NAYIN[_idx60(stem_of[life], life) // 2]]
    z = ziwei_position(bureau, day)
    f = (4 - z) % 12
    stars = {b: [] for b in range(12)}
    for name, pos in (("紫微", z), ("天机", z - 1), ("太阳", z - 3), ("武曲", z - 4), ("天同", z - 5), ("廉贞", z - 8),
                      ("天府", f), ("太阴", f + 1), ("贪狼", f + 2), ("巨门", f + 3), ("天相", f + 4), ("天梁", f + 5), ("七杀", f + 6), ("破军", f + 10)):
        stars[pos % 12].append(name)
    minor = {b: [] for b in range(12)}
    kui, yue = KUI_YUE[ys]
    lc = LUCUN[ys]
    huo, ling = HUO_LING[yb]
    for name, pos in (("文昌", 10 - hb), ("文曲", 4 + hb), ("左辅", 4 + (m - 1)), ("右弼", 10 - (m - 1)), ("天魁", kui), ("天钺", yue),
                      ("禄存", lc), ("擎羊", lc + 1), ("陀罗", lc - 1), ("天马", TIANMA[yb]), ("火星", huo + hb), ("铃星", ling + hb),
                      ("地劫", 11 + hb), ("地空", 11 - hb)):
        minor[pos % 12].append(name)
    sihua = dict(zip(SIHUA[ys], "禄权科忌"))
    forward = (ys % 2 == 0) == gender.upper().startswith("M")
    palaces = []
    for i, (zh, en, hi) in enumerate(PALACES):
        b = (life - i) % 12
        k = (b - life) % 12 if forward else (life - b) % 12
        start = bureau + 10 * k
        palaces.append({"index": i, "zh": zh, "en": en, "hi": hi, "branch": b, "branch_zh": BRANCHES[b], "stem_zh": STEMS[stem_of[b]],
                        "is_body": b == body,
                        "major": [{"zh": s, "en": MAJOR[s][0], "hi": MAJOR[s][1], "transform": sihua.get(s)} for s in stars[b]],
                        "minor": [{"zh": s, "en": MINOR[s][0], "hi": MINOR[s][1], "lucky": s in LUCKY, "transform": sihua.get(s)} for s in minor[b]],
                        "decade": [start, start + 9]})
    return {"lunar": lunar, "hour_branch": hb, "hour_zh": BRANCHES[hb] + "时", "late_zi": late_zi, "month_used": m,
            "life_branch": life, "body_branch": body, "bureau": bureau, "bureau_name": BUREAU_NAME[bureau],
            "life_master": LIFE_MASTER[life], "body_master": BODY_MASTER[yb], "sihua": {v: k for k, v in sihua.items()},
            "forward": forward, "palaces": palaces,
            "conventions": "Quanshu placements; lunar date in China Standard Time; 23:00-24:00 counts as the next day's Zi hour; "
                           "a leap month's days 16 onward count as the next month; star brightness not computed (schools differ)."}
