"""app_predict.py - the Predictions page (v18): today, this week, this month, this year and the next three years, by
life area, for one person, with a star rating, a short reading, the main reason ("why") and lucky pointers.

Method, stated on the page:
* Gochar (transits) from the natal Moon, with the classical favourable houses for each planet, applied to the houses
  that rule each life area, counted from the Lagna and from the Moon. Natural significators (karakas) add half weight.
* The planets that move in each period carry the weight: the Moon for today; the Moon, Sun, Mercury, Venus and Mars for
  the week; the Sun, Mercury, Venus and Mars for the month; Jupiter, Saturn and Rahu for the year.
* The running Vimshottari periods (mahadasha and antardasha, and the pratyantar for the month) add to the areas their
  lords rule or occupy, by how well the lord is placed.
* The year and the three years use the multi-system forecast (app_forecast) where it covers the area.
Ratings are tendencies, 2 to 5 stars; no area is ever rated as a certainty, and wording follows the app's rules.
"""
import datetime as dt
import json

import swisseph as swe

import app_today as AT
import hindi_shell as HS
import vedic

SIGNS = vedic.SIGNS
SIGN_LORD = vedic.SIGN_LORD
FAV = {"Sun": {3, 6, 10, 11}, "Moon": {1, 3, 6, 7, 10, 11}, "Mars": {3, 6, 11}, "Mercury": {2, 4, 6, 8, 10, 11},
       "Jupiter": {2, 5, 7, 9, 11}, "Venus": {1, 2, 3, 4, 5, 8, 9, 11, 12}, "Saturn": {3, 6, 11}, "Rahu": {3, 6, 11}}
BODIES = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
          "Saturn": swe.SATURN, "Rahu": None}
AREAS = [  # key, houses, karakas, English, Hindi
    ("career", {10, 6, 11}, {"Sun", "Saturn"}, "Career and work", "करियर और काम"),
    ("money", {2, 11}, {"Jupiter", "Venus"}, "Money", "धन"),
    ("love", {7, 5}, {"Venus"}, "Love and marriage", "प्रेम और विवाह"),
    ("family", {4, 2}, {"Moon"}, "Family and home", "परिवार और घर"),
    ("energy", {1, 6}, {"Sun", "Mars"}, "Energy and rest", "ऊर्जा और विश्राम"),
    ("learning", {9, 3, 12}, {"Jupiter", "Mercury"}, "Learning and travel", "शिक्षा और यात्रा"),
]
PERIOD_WEIGHTS = {
    "day": {"Moon": 3.0},
    "week": {"Moon": 1.5, "Sun": 0.5, "Mercury": 0.7, "Venus": 0.7, "Mars": 0.7},
    "month": {"Sun": 1.0, "Mercury": 0.8, "Venus": 0.8, "Mars": 1.0, "Moon": 0.3},
    "year": {"Jupiter": 1.5, "Saturn": 1.5, "Rahu": 0.8},
}
GOOD_HOUSES = {1, 2, 4, 5, 7, 9, 10, 11}
ORD_EN = {1: "1st", 2: "2nd", 3: "3rd"}
ORD_HI = {1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें", 6: "छठे", 7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें", 11: "ग्यारहवें", 12: "बारहवें"}
COLOUR = {"Sun": ("orange or gold", "नारंगी या सुनहरा"), "Moon": ("white or silver", "सफ़ेद या चाँदी"), "Mars": ("red", "लाल"),
          "Mercury": ("green", "हरा"), "Jupiter": ("yellow", "पीला"), "Venus": ("white or pink", "सफ़ेद या गुलाबी"), "Saturn": ("blue", "नीला")}
NUMBER = {"Sun": 1, "Moon": 2, "Jupiter": 3, "Rahu": 4, "Mercury": 5, "Venus": 6, "Ketu": 7, "Saturn": 8, "Mars": 9}

TEXT = {  # area -> level -> (en, hi); level: high (4-5 stars), mid (3), low (2)
    "career": {"high": ("Work moves well: a good time to take on responsibility, ask for what you want and finish pending tasks.",
                        "काम अच्छा चलता है: ज़िम्मेदारी लेने, अपनी बात रखने और रुके काम पूरे करने का अच्छा समय।"),
               "mid": ("A steady time at work. Keep to your routine and build quietly.", "काम में स्थिर समय। अपनी दिनचर्या बनाए रखें और धीरे-धीरे आगे बढ़ें।"),
               "low": ("Work may ask for extra patience. Double-check details and avoid hasty decisions.", "काम में अधिक धैर्य चाहिए। बारीकियाँ दोबारा जाँचें और जल्दबाज़ी के निर्णय से बचें।")},
    "money": {"high": ("Money matters look supportive: gains, savings and good purchases are favoured.", "धन के मामले अनुकूल: लाभ, बचत और अच्छी ख़रीद के लिए अच्छा समय।"),
              "mid": ("Money stays steady. Keep spending in line with plans.", "धन स्थिर रहता है। ख़र्च योजना के अनुसार रखें।"),
              "low": ("Be careful with spending and lending. Postpone large commitments if you can.", "ख़र्च और उधार में सावधानी रखें। हो सके तो बड़े वित्तीय निर्णय टालें।")},
    "love": {"high": ("Warmth in relationships: a good time to spend with your partner or meet someone new.", "रिश्तों में गर्मजोशी: साथी के साथ समय बिताने या नए लोगों से मिलने का अच्छा समय।"),
             "mid": ("Relationships are steady. Small gestures go a long way.", "रिश्ते स्थिर हैं। छोटी-छोटी बातें बड़ा असर करती हैं।"),
             "low": ("Moods can clash. Listen first and choose words gently.", "मनोदशा टकरा सकती है। पहले सुनें और शब्द सोच-समझकर चुनें।")},
    "family": {"high": ("Home and family feel supportive. Good for family plans and time together.", "घर-परिवार सहयोगी है। पारिवारिक योजनाओं और साथ समय बिताने के लिए अच्छा।"),
               "mid": ("Family life is steady. Keep in touch with those close to you.", "पारिवारिक जीवन स्थिर है। अपनों के संपर्क में रहें।"),
               "low": ("Home may need more attention. Patience with elders helps.", "घर को अधिक ध्यान चाहिए। बड़ों के साथ धैर्य रखें।")},
    "energy": {"high": ("Energy is good. Use it for exercise and the tasks you have been putting off.", "ऊर्जा अच्छी है। इसे व्यायाम और टले हुए कामों में लगाएँ।"),
               "mid": ("Energy is even. Keep regular sleep and meals.", "ऊर्जा सामान्य है। नींद और भोजन नियमित रखें।"),
               "low": ("Energy may dip. Rest well, keep the pace gentle and avoid overwork.", "ऊर्जा कम हो सकती है। अच्छा विश्राम करें, गति धीमी रखें और अधिक काम से बचें।")},
    "learning": {"high": ("Good for study, exams, short trips and learning something new.", "पढ़ाई, परीक्षा, छोटी यात्राओं और कुछ नया सीखने के लिए अच्छा।"),
                 "mid": ("Steady progress in study. Plan travel ahead.", "पढ़ाई में स्थिर प्रगति। यात्रा पहले से योजना बनाकर करें।"),
                 "low": ("Concentration may need effort. Avoid last-minute travel changes.", "एकाग्रता में प्रयास लगेगा। यात्रा में अंतिम समय के बदलाव से बचें।")},
}
PERIOD_NAME = {"day": ("Today", "आज"), "week": ("This week", "यह सप्ताह"), "month": ("This month", "यह माह"), "year": ("This year", "यह वर्ष"),
               "three": ("Next 3 years", "अगले 3 वर्ष")}
FC_MAP = {"career": "work", "love": "marriage", "energy": "health", "family": "family"}


def bi(en, hi):
    return {"en": en, "hi": hi}


def _ord_en(h):
    return ORD_EN.get(h, f"{h}th")


def _house(base, s):
    return (s - base) % 12 + 1


def _sign_at(jd, p):
    if p == "Rahu":
        return int((swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360) // 30)
    return int(AT._sid(jd, BODIES[p])[0] // 30)


def _samples(start, period):
    if period == "day":
        return [start]
    if period == "week":
        return [start + dt.timedelta(days=i) for i in range(7)]
    if period == "month":
        return [start + dt.timedelta(days=i) for i in range(0, 30, 3)]
    return [start + dt.timedelta(days=i) for i in range(0, 365, 30)]


def _dasha_now(v, iso):
    for m in v["dashas"]["vimshottari"]["mahadashas"]:
        if m["start"] <= iso < m["end"]:
            for a in m.get("antardashas") or []:
                if a["start"] <= iso < a["end"]:
                    return m["lord"], a["lord"]
            return m["lord"], None
    return None, None


def score(v, period, start):
    msign = SIGNS.index(v["planets"]["Moon"]["sign"])
    lsign = SIGNS.index(v["lagna"]["sign"])
    weights = PERIOD_WEIGHTS[period]
    totals = {a[0]: 0.0 for a in AREAS}
    reasons = {a[0]: [] for a in AREAS}
    dates = _samples(start, period)
    for d in dates:
        jd = swe.julday(d.year, d.month, d.day, 6.5)
        for p, w in weights.items():
            s = _sign_at(jd, p)
            hm, hl = _house(msign, s), _house(lsign, s)
            good = hm in FAV[p]
            for key, houses, karakas, _, _ in AREAS:
                wt = 0.0
                if hl in houses or hm in houses:
                    wt += w
                if p in karakas:
                    wt += w * 0.5
                if wt:
                    val = wt * (1 if good else -1) / len(dates)
                    totals[key] += val
                    reasons[key].append((abs(val), p, hm, good))
    # running dasha lords
    md, ad = _dasha_now(v, start.isoformat())
    for lord, w in ((md, 0.6 if period in ("year", "three") else 0.3), (ad, 0.8 if period in ("month", "year") else 0.4)):
        if not lord or lord not in v["planets"]:
            continue
        pl = v["planets"][lord]
        ruled = {h["house"] for h in v["houses"] if h["lord"] == lord} | {pl["house"]}
        good = pl["house"] in GOOD_HOUSES and pl.get("dignity") != "debilitated"
        for key, houses, _, _, _ in AREAS:
            if ruled & houses:
                totals[key] += w * (1 if good else -1)
                reasons[key].append((w, f"dasha:{lord}", pl["house"], good))
    return totals, reasons, (md, ad)


def stars(t):
    return 5 if t >= 1.2 else 4 if t >= 0.4 else 3 if t > -0.4 else 2


def _why(reason):
    if not reason:
        return bi("Planets are quiet for this area.", "इस क्षेत्र के लिए ग्रह शांत हैं।")
    _, p, h, good = max(reason)
    if p.startswith("dasha:"):
        lord = p.split(":")[1]
        return bi(f"Your running {lord} period, with {lord} in the {_ord_en(h)} house of your chart" + (" (well placed)." if good else " (asks for effort)."),
                  f"आपकी चल रही {HS.PLANET.get(lord, lord)} दशा, {HS.PLANET.get(lord, lord)} आपकी कुंडली के {ORD_HI[h]} भाव में" +
                  (" (अच्छी स्थिति)।" if good else " (प्रयास माँगती है)।"))
    return bi(f"{p} moves through the {_ord_en(h)} house from your Moon" + (", a helpful position." if good else ", which asks for care."),
              f"{HS.PLANET.get(p, p)} आपके चंद्र से {ORD_HI[h]} भाव में है" + (", जो सहायक स्थिति है।" if good else ", जो सावधानी माँगती है।"))


def _level(n):
    return "high" if n >= 4 else "mid" if n == 3 else "low"


def _lucky_day(v, d, tz):
    wd = d.weekday()
    lord = AT.WD_LORD[wd]
    md, ad = _dasha_now(v, d.isoformat())
    friend = ad or md or lord
    c = COLOUR.get(friend, COLOUR[lord])
    return {"colour": bi(c[0], c[1]), "number": NUMBER.get(friend, NUMBER.get(lord, 1)),
            "note": bi(f"Colour and number of {friend}, the lord of your running period.", f"आपकी चल रही दशा के स्वामी {HS.PLANET.get(friend, friend)} का रंग और अंक।")}


def _best_days(v, start, n):
    """The n days in the period with the best Moon gochar for this person."""
    msign = SIGNS.index(v["planets"]["Moon"]["sign"])
    out = []
    for i in range(n):
        d = start + dt.timedelta(days=i)
        jd = swe.julday(d.year, d.month, d.day, 6.5)
        h = _house(msign, _sign_at(jd, "Moon"))
        out.append((1 if h in FAV["Moon"] else 0, -i, d))
    return [x[2] for x in sorted(out, reverse=True) if x[0] > 0][:3]


def predict(c, period, today_iso, place=None, fc=None):
    v = c["vedic"]
    start = dt.date.fromisoformat(today_iso)
    if period == "month":
        start = start.replace(day=1) if start.day < 3 else start
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    p_for = "year" if period == "three" else period
    totals, reasons, (md, ad) = score(v, p_for, start)
    areas = []
    for key, _, _, en, hi in AREAS:
        n = stars(totals[key])
        reading = TEXT[key][_level(n)]
        why = _why(reasons[key])
        if fc and period in ("year", "three") and key in FC_MAP:
            fa = next((a for a in fc["areas"] if a["key"] == FC_MAP[key]), None)
            if fa:
                ys = fa["years"] if period == "three" else fa["years"][:1]
                sup = sum(1 for y in ys if y["lean"] == "supportive")
                dem = sum(1 for y in ys if y["lean"] == "demanding")
                n = max(2, min(5, 3 + sup - dem + (1 if sup > 1 else 0)))
                y0 = ys[0]
                reading = bi(y0["summary"]["en"], y0["summary"]["hi"]) if period == "year" else \
                    bi(" ".join(f"{y['from'][:4]}: {y['summary']['en']}" for y in ys), " ".join(f"{y['from'][:4]}: {y['summary']['hi']}" for y in ys))
                if y0.get("drivers"):
                    dv = y0["drivers"][0]
                    why = bi(dv["en"], dv["hi"])
            else:
                reading = bi(*reading)
        else:
            reading = bi(*reading)
        areas.append({"key": key, "title": bi(en, hi), "stars": n, "reading": reading, "why": why})
    out = {"period": period, "title": bi(*PERIOD_NAME[period]), "from": start.isoformat(), "areas": areas,
           "dasha": {"maha": md, "antar": ad}}
    if period == "day":
        out["lucky"] = _lucky_day(v, start, None)
        if place:
            try:
                day = AT.Day(start, float(place["lat"]), float(place["lon"]), AT.ZoneInfo(place["tz"]))
                pr = AT.periods(day)
                if "abhijit" in pr and not pr["abhijit"].get("wednesday"):
                    out["best_time"] = bi(f"Abhijit muhurta {pr['abhijit']['from']}–{pr['abhijit']['to']}; avoid Rahu Kaal {pr['rahu_kalam']['from']}–{pr['rahu_kalam']['to']}.",
                                          f"अभिजित मुहूर्त {pr['abhijit']['from']}–{pr['abhijit']['to']}; राहु काल {pr['rahu_kalam']['from']}–{pr['rahu_kalam']['to']} से बचें।")
                elif "rahu_kalam" in pr:
                    good = next((x for x in pr["choghadiya_day"] if x["kind"] == "good"), None)
                    out["best_time"] = bi((f"{good['name']['en']} choghadiya {good['from']}–{good['to']}; " if good else "") +
                                          f"avoid Rahu Kaal {pr['rahu_kalam']['from']}–{pr['rahu_kalam']['to']}.",
                                          (f"{good['name']['hi']} चौघड़िया {good['from']}–{good['to']}; " if good else "") +
                                          f"राहु काल {pr['rahu_kalam']['from']}–{pr['rahu_kalam']['to']} से बचें।")
            except Exception:
                pass
    elif period in ("week", "month"):
        days = _best_days(v, start, 7 if period == "week" else 30)
        if days:
            out["best_days"] = bi(", ".join(d.strftime("%a %d %b") for d in days),
                                  ", ".join(f"{AT.WD_HI[d.weekday()]} {d.day}" for d in days))
    elif period == "year" and md:
        out["dasha_note"] = bi(f"You are in the {md} mahadasha" + (f", {ad} antardasha." if ad else "."),
                               f"आप {HS.PLANET.get(md, md)} महादशा" + (f", {HS.PLANET.get(ad, ad)} अंतर्दशा में हैं।" if ad else " में हैं।"))
    out["note"] = bi("Tendencies from the transits and your running periods, not certainties. Your choices and effort shape the outcome.",
                     "गोचर और आपकी चल रही दशाओं से झुकाव, निश्चितता नहीं। परिणाम आपके निर्णय और प्रयास से बनते हैं।")
    return out


def predict_json(request_json):
    """Chart request plus {period: day|week|month|year|three, today_lat?, today_lon?, today_tz?}."""
    import engine_api
    r = json.loads(request_json)
    period = r.get("period", "day")
    fc = None
    if period in ("year", "three"):
        import app_forecast
        rr = dict(r, modules=engine_api.FORECAST_MODULES, horizon_years=3)
        c = engine_api.chart_obj(rr)
        fc = app_forecast.build(c, birth_date=r["date"])
    else:
        c = engine_api.chart_obj(dict(r, modules="vedic"))
    place = {"lat": r["today_lat"], "lon": r["today_lon"], "tz": r["today_tz"]} if r.get("today_lat") is not None else \
        {"lat": r["lat"], "lon": r["lon"], "tz": r["tz"]}
    return json.dumps(predict(c, period, r.get("now") or dt.date.today().isoformat(), place, fc), ensure_ascii=False)
