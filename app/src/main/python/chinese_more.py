"""chinese_more.py - Nine Star Ki and the Tong Shu (通书) day officers (v17), plus the bilingual sections the Chinese
screen shows for a person: the lunar birth date, the Zi Wei Dou Shu chart, Nine Star Ki and a date finder.

Nine Star Ki: the year changes at Li Chun (Sun at 315 degrees). Year star = 11 minus the digit root of the year,
reduced to 1-9 (1965 -> 8, 2026 -> 1). The month star starts from 8, 2 or 5 in the Tiger month (Feb) for year stars
1-4-7, 2-5-8 and 3-6-9, and falls by one each solar month.

Tong Shu: the twelve day officers (建除十二神) run from the solar month's branch: officer = (day branch - month
branch) mod 12. Suitability by activity follows the common almanac summary; a day whose branch clashes with the
person's birth-year branch is marked. Leanings only; the screen says to confirm important dates with a practitioner.
"""
import datetime as dt
import json

import swisseph as swe

import chinese as CH
import chinese_calendar as CC
import hindi_shell as HS
import ziwei as ZW
from app_details import bi, table, para, items

STAR = {1: ("1 White Water", "1 श्वेत जल", "adaptable, thoughtful, a quiet strength", "अनुकूल, विचारशील, शांत शक्ति"),
        2: ("2 Black Earth", "2 कृष्ण पृथ्वी", "supportive, patient, caring", "सहायक, धैर्यवान, देखभाल करने वाला"),
        3: ("3 Bright Green Wood", "3 हरित काष्ठ", "energetic, quick to start, outspoken", "ऊर्जावान, तेज़ शुरुआत, स्पष्टवादी"),
        4: ("4 Green Wood", "4 हरा काष्ठ", "gentle, sociable, persuasive", "सौम्य, मिलनसार, प्रभावशाली"),
        5: ("5 Yellow Earth", "5 पीत पृथ्वी", "central, strong-willed, a natural leader", "केंद्रीय, दृढ़ इच्छाशक्ति, स्वाभाविक नेता"),
        6: ("6 White Metal", "6 श्वेत धातु", "responsible, principled, organised", "ज़िम्मेदार, सिद्धांतवादी, व्यवस्थित"),
        7: ("7 Red Metal", "7 लाल धातु", "charming, expressive, enjoys life", "आकर्षक, अभिव्यक्तिपूर्ण, जीवन का आनंद लेने वाला"),
        8: ("8 White Earth", "8 श्वेत पृथ्वी", "steady, determined, a careful builder", "स्थिर, दृढ़, सावधान निर्माता"),
        9: ("9 Purple Fire", "9 बैंगनी अग्नि", "bright, inspiring, seeks recognition", "तेजस्वी, प्रेरक, पहचान चाहने वाला")}
OFFICERS = [("建", "Establish", "स्थापना"), ("除", "Remove", "निवारण"), ("满", "Full", "पूर्ण"), ("平", "Balance", "संतुलन"),
            ("定", "Stable", "स्थिर"), ("执", "Initiate", "आरंभ"), ("破", "Break", "भंग"), ("危", "Risky", "जोखिम"),
            ("成", "Success", "सफलता"), ("收", "Receive", "प्राप्ति"), ("开", "Open", "उद्घाटन"), ("闭", "Close", "बंद")]
GOOD = {"wedding": {"成", "开", "定", "满"}, "moving": {"成", "开", "定", "满", "除"}, "business": {"开", "成", "满", "定", "收"},
        "travel": {"成", "开", "定", "建"}, "contract": {"定", "成", "执", "开"}}
AVOID = {"破", "闭", "危"}
ACTIVITY = {"wedding": ("Wedding", "विवाह"), "moving": ("Moving house", "गृह प्रवेश"), "business": ("Opening a business", "व्यवसाय आरंभ"),
            "travel": ("Starting a journey", "यात्रा आरंभ"), "contract": ("Signing a contract", "अनुबंध पर हस्ताक्षर")}


def _root(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def lichun(year):
    return CH.term_jd(year, 315)


def nine_star_year(y):
    s = (11 - _root(y)) % 9
    return s or 9


def nine_star(d, tz_hours=8.0):
    """Year and month stars for a date (Li Chun and the solar-month boundaries in local time)."""
    jd = swe.julday(d.year, d.month, d.day, 12.0 - tz_hours)
    y = d.year if jd >= lichun(d.year) else d.year - 1
    ys = nine_star_year(y)
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    month_i = int(((sun - 315) % 360) // 30)          # 0 = Tiger month (from Li Chun)
    start = {1: 8, 4: 8, 7: 8, 2: 2, 5: 2, 8: 2, 3: 5, 6: 5, 9: 5}[ys]
    ms = (start - month_i - 1) % 9 + 1
    return {"year_for_stars": y, "year_star": ys, "month_star": ms}


def officer(d, tz_hours=8.0):
    jd = swe.julday(d.year, d.month, d.day, 12.0 - tz_hours)
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    month_branch = (2 + int(((sun - 315) % 360) // 30)) % 12
    di = CH.day_index(d)
    return OFFICERS[(di % 12 - month_branch) % 12], di


def find_days(start_iso, days, activity, birth_year_branch, tz_hours=8.0):
    d0 = dt.date.fromisoformat(start_iso)
    out = []
    for i in range(days):
        d = d0 + dt.timedelta(days=i)
        (zh, en, hi), di = officer(d, tz_hours)
        clash = (di % 12 - birth_year_branch) % 12 == 6
        good = zh in GOOD[activity] and not clash
        avoid = zh in AVOID or clash
        out.append({"date": d.isoformat(), "pillar": CC.STEMS[di % 10] + CC.BRANCHES[di % 12], "officer_zh": zh, "officer_en": en,
                    "officer_hi": hi, "clash": clash, "rating": "good" if good else "avoid" if avoid else "neutral"})
    return out


# ------------------------------------------------------------------ sections for the screen
LAST_GRID = []


def _star(n):
    return bi(STAR[n][0], STAR[n][1])


def person_sections(name, date_iso, time_hhmm, gender, tz_hours, today_tz_hours, today_iso, activity="wedding"):
    d = dt.date.fromisoformat(date_iso)
    lunar = CC.to_lunar(d)
    secs = []
    secs.append({"key": "cn_lunar", "title": bi("Chinese birth date", "चीनी जन्म तिथि"),
                 "blocks": [table([bi("Item", "विवरण"), bi("Value", "मान")], [
                     [bi("Lunar date", "चंद्र तिथि"), bi(f"{lunar['zh']} (year {lunar['year']}, month {lunar['month']}{' leap' if lunar['leap'] else ''}, day {lunar['day']})",
                                                         f"{lunar['zh']} (वर्ष {lunar['year']}, माह {lunar['month']}{' अधिक' if lunar['leap'] else ''}, दिन {lunar['day']})")],
                     [bi("Year (from Chinese New Year)", "वर्ष (चीनी नववर्ष से)"), bi(f"{lunar['stem_branch']} {lunar['pinyin']}, {lunar['animal']}",
                                                                                         f"{lunar['stem_branch']} {lunar['pinyin']}, {lunar['animal_hi']}")]])],
                 "note": bi("BaZi counts the year from Li Chun (about 4 February) instead of New Year, so near the turn of the year the two animals can differ.",
                            "बाज़ी वर्ष को नववर्ष की बजाय ली चुन (लगभग 4 फ़रवरी) से गिनता है, इसलिए वर्ष के मोड़ पर दोनों पशु अलग हो सकते हैं।")})
    z = ZW.chart(date_iso, time_hhmm, gender)
    global LAST_GRID
    LAST_GRID = [{"branch": p["branch"], "branch_zh": p["branch_zh"], "stem_zh": p["stem_zh"], "zh": p["zh"], "en": p["en"], "hi": p["hi"],
                  "body": p["is_body"], "life": p["index"] == 0, "decade": p["decade"],
                  "major": [{"zh": x["zh"], "en": x["en"].split(" (")[0], "hi": x["hi"].split(" (")[0], "t": x["transform"]} for x in p["major"]],
                  "minor": [{"zh": x["zh"], "en": x["en"], "hi": x["hi"], "t": x["transform"]} for x in p["minor"]]} for p in z["palaces"]]
    rows = []
    for p in z["palaces"]:
        def stars(lst):
            return ", ".join(s["en"] + (f" ({s['transform']})" if s.get("transform") else "") for s in lst) or "–", \
                   ", ".join(s["hi"] + (f" ({s['transform']})" if s.get("transform") else "") for s in lst) or "–"
        me, mh = stars(p["major"])
        ne, nh = stars(p["minor"])
        rows.append([bi(f"{p['zh']} {p['en']}" + (" · Body" if p["is_body"] else ""), f"{p['zh']} {p['hi']}" + (" · शरीर" if p["is_body"] else "")),
                     bi(p["stem_zh"] + p["branch_zh"]), bi(me, mh), bi(ne, nh), bi(f"{p['decade'][0]}–{p['decade'][1]}")])
    sh = z["sihua"]
    trans = [bi(f"{k}: {ZW.MAJOR.get(v, ZW.MINOR.get(v, (v, v)))[0]} {ZW.TRANSFORM[k][0]}", f"{k}: {ZW.MAJOR.get(v, ZW.MINOR.get(v, (v, v)))[1]} {ZW.TRANSFORM[k][1]}")
             for k, v in sh.items()]
    bn = z["bureau_name"]
    secs.append({"key": "zwds", "title": bi("Zi Wei Dou Shu chart", "ज़ी वेई दो शू कुंडली"),
                 "intro": bi(f"Five-Element bureau {bn[0]} ({bn[1]}). Life master {ZW.MAJOR.get(z['life_master'], ZW.MINOR.get(z['life_master']))[0]}, "
                             f"body master {ZW.MAJOR.get(z['body_master'], ZW.MINOR.get(z['body_master']))[0]}. Birth hour {z['hour_zh']}.",
                             f"पंचतत्व ब्यूरो {bn[0]} ({bn[2]})। जीवन स्वामी {ZW.MAJOR.get(z['life_master'], ZW.MINOR.get(z['life_master']))[1]}, "
                             f"शरीर स्वामी {ZW.MAJOR.get(z['body_master'], ZW.MINOR.get(z['body_master']))[1]}। जन्म घड़ी {z['hour_zh']}।"),
                 "blocks": [table([bi("Palace", "भाव"), bi("Stem-branch", "तना-शाखा"), bi("Main stars", "मुख्य तारे"), bi("Other stars", "अन्य तारे"),
                                   bi("10-year period (age)", "10 वर्ष की अवधि (आयु)")], rows),
                            para(bi("The four transformations of the birth year:", "जन्म वर्ष के चार रूपांतरण:")), items(trans)],
                 "note": bi("Placements follow the Quanshu rules. Star brightness, yearly overlays and readings are not given here; a Zi Wei "
                            "practitioner reads the chart as a whole.",
                            "स्थान 'चुआनशू' नियमों के अनुसार। तारों की चमक, वार्षिक परतें और फलादेश यहाँ नहीं दिए गए; ज़ी वेई के जानकार कुंडली को समग्र रूप से पढ़ते हैं।")})
    birth = nine_star(d, tz_hours)
    now = nine_star(dt.date.fromisoformat(today_iso), today_tz_hours)
    secs.append({"key": "nine_star_ki", "title": bi("Nine Star Ki", "नौ तारा की"),
                 "intro": bi(f"Your year star is {STAR[birth['year_star']][0]}: {STAR[birth['year_star']][2]}.",
                             f"आपका वर्ष तारा {STAR[birth['year_star']][1]} है: {STAR[birth['year_star']][3]}।"),
                 "blocks": [table([bi("Star", "तारा"), bi("Birth", "जन्म"), bi("Now", "अभी")], [
                     [bi("Year star (principal)", "वर्ष तारा (मुख्य)"), _star(birth["year_star"]), _star(now["year_star"])],
                     [bi("Month star (character)", "माह तारा (स्वभाव)"), _star(birth["month_star"]), _star(now["month_star"])]])],
                 "note": bi("The star year starts at Li Chun (about 4 February) and each star month at the solar term.",
                            "तारा वर्ष ली चुन (लगभग 4 फ़रवरी) से और हर तारा माह सौर पद से शुरू होता है।")})
    days = find_days(today_iso, 30, activity, lunar["branch_index"], today_tz_hours)
    good = [x for x in days if x["rating"] == "good"][:10]
    a_en, a_hi = ACTIVITY[activity]
    rows = [[bi(x["date"]), bi(f"{x['pillar']}"), bi(f"{x['officer_zh']} {x['officer_en']}", f"{x['officer_zh']} {x['officer_hi']}")] for x in good]
    secs.append({"key": "tong_shu", "title": bi(f"Tong Shu: good days for {a_en.lower()}", f"टोंग शू: {a_hi} के लिए शुभ दिन"),
                 "intro": bi(f"Days in the next 30 whose day officer suits {a_en.lower()} and which do not clash with your birth-year animal ({lunar['animal']}).",
                             f"अगले 30 दिनों में वे दिन जिनका दिवस-अधिकारी {a_hi} के अनुकूल है और जो आपके जन्म-वर्ष पशु ({lunar['animal_hi']}) से नहीं टकराते।"),
                 "blocks": [table([bi("Date", "तिथि"), bi("Day pillar", "दिवस स्तंभ"), bi("Day officer", "दिवस अधिकारी")], rows) if rows else
                            para(bi("No suitable day in the next 30 days.", "अगले 30 दिनों में कोई उपयुक्त दिन नहीं।"))],
                 "note": bi("From the twelve day officers of the Chinese almanac. For a wedding or a large move, also check the Vedic Muhurta and ask a practitioner.",
                            "चीनी पंचांग के बारह दिवस अधिकारियों से। विवाह या बड़े स्थानांतरण के लिए वैदिक मुहूर्त भी देखें और किसी जानकार से पूछें।")})
    return secs


def _offset(tz, on):
    from zoneinfo import ZoneInfo
    return dt.datetime(on.year, on.month, on.day, 12, tzinfo=ZoneInfo(tz)).utcoffset().total_seconds() / 3600


def sections_json(request_json):
    """{name, date, time, gender, tz, today_tz?, today?, activity?} -> {"sections": [...], "activities": {...}}."""
    r = json.loads(request_json)
    today = r.get("today") or dt.date.today().isoformat()
    secs = person_sections(r.get("name", ""), r["date"], r["time"], r.get("gender", "M"), _offset(r["tz"], dt.date.fromisoformat(r["date"])),
                           _offset(r.get("today_tz") or r["tz"], dt.date.fromisoformat(today)), today, r.get("activity", "wedding"))
    return json.dumps({"sections": secs, "grid": LAST_GRID, "activities": {k: bi(*v) for k, v in ACTIVITY.items()}}, ensure_ascii=False)
