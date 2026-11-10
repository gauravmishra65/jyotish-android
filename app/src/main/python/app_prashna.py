"""app_prashna.py - question charts (v16): Vedic Prashna and KP number horary, for eight everyday questions.

Prashna: the chart of the moment the question is asked, at the place it is asked (Lahiri, whole-sign houses). Read with
the common Prashna checks: the strength of the Lagna and its lord, the Moon, the house of the question and its lord,
and whether the Lagna lord and the house lord are linked (together, in mutual aspect, exchanging signs, or in a Tajika
Ithasala, an applying aspect).

KP horary: the person gives a number from 1 to 249. Each number is one KP sub of the zodiac (the 243 subs split where
they cross a sign, as K.S. Krishnamurti numbered them). The Ascendant is set to the start of that sub: the cusps are
cast for the moment today when that degree rises at the place, and the planets are taken at the moment of judgement.
The judgement reads the sub-lord of the question's cusp: the houses it signifies through its star lord.

Wording rules: questions are only about positive life matters; results are leanings ("the signs lean favourable"),
never promises, and the person is reminded that effort and circumstances decide.
"""
import datetime as dt
import json
from zoneinfo import ZoneInfo

import swisseph as swe

import chart_engine
import common
import hindi_shell as HS
import tajika
import vedic

SIGNS = common.SIGNS
NAK_SPAN = 360 / 27
ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
SIGN_LORD = vedic.SIGN_LORD
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

# question -> (main house, KP favourable houses, KP opposing houses, English, Hindi)
QUESTIONS = {
    "marriage": (7, {2, 7, 11}, {1, 6, 10}, "Will the marriage or relationship go ahead?", "क्या विवाह या संबंध आगे बढ़ेगा?"),
    "job": (10, {2, 6, 10, 11}, {1, 5, 9}, "Will I get the job or promotion?", "क्या नौकरी या पदोन्नति मिलेगी?"),
    "money": (11, {2, 6, 11}, {5, 8, 12}, "Will the money or gain come?", "क्या धन या लाभ आएगा?"),
    "property": (4, {4, 11, 12}, {3, 5, 10}, "Will the home or property purchase happen?", "क्या घर या संपत्ति की ख़रीद होगी?"),
    "travel": (12, {3, 9, 12}, {2, 4, 11}, "Will the journey or move abroad happen?", "क्या यात्रा या विदेश जाना होगा?"),
    "education": (4, {4, 9, 11}, {3, 8, 12}, "Will the studies or exam go well?", "क्या पढ़ाई या परीक्षा अच्छी जाएगी?"),
    "children": (5, {2, 5, 11}, {1, 4, 10}, "Will we be blessed with a child?", "क्या संतान का सुख मिलेगा?"),
    "lost": (2, {2, 6, 11}, {5, 8, 12}, "Will the lost item be found?", "क्या खोई वस्तु मिलेगी?"),
}
HOUSE_HI = {1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें", 6: "छठे", 7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें", 11: "ग्यारहवें", 12: "बारहवें"}   # oblique: "दूसरे भाव में"
ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def _ord(h):
    return ORD.get(h, f"{h}th")


def P(p):
    return {"en": p, "hi": HS.PLANET.get(p, p)}


def Sg(s):
    return {"en": s, "hi": HS.SIGN.get(s, s)}


def bi(en, hi):
    return {"en": en, "hi": hi}


def _jd_now(when_iso, tz):
    t = dt.datetime.fromisoformat(when_iso)
    if t.tzinfo is None:
        t = t.replace(tzinfo=ZoneInfo(tz))
    u = t.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600), t


# ------------------------------------------------------------------ KP: the 249 numbers
def kp_numbers():
    """[(number, start_lon, end_lon, sign, star_lord, sub_lord)] for 1..249."""
    out, lon = [], 0.0
    for ni in range(27):
        start_i = ni % 9
        for k in range(9):
            lord, yrs = ORDER[(start_i + k) % 9]
            ln = NAK_SPAN * yrs / 120.0
            a, b = lon, lon + ln
            cut = (int(a // 30) + 1) * 30
            if a + 1e-6 < cut < b - 1e-6:
                out.append((a, cut, ORDER[start_i][0], lord))
                out.append((cut, b, ORDER[start_i][0], lord))
            else:
                out.append((a, b, ORDER[start_i][0], lord))
            lon = b
    return [(i + 1, a, b, SIGNS[int(a // 30) % 12], star, sub) for i, (a, b, star, sub) in enumerate(out)]


def _kp_asc(jd, lat, lon):
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
    return ascmc[0]


def _find_rising(target, jd0, lat, lon):
    """The moment in the 24 hours from jd0 when the KP ascendant reaches target (degrees)."""
    def diff(jd):
        return (_kp_asc(jd, lat, lon) - target + 180) % 360 - 180
    step = 4 / 1440
    prev_j, prev_d = jd0, diff(jd0)
    j = jd0
    while j < jd0 + 1.05:
        j += step
        d = diff(j)
        if prev_d < 0 <= d and abs(d - prev_d) < 30:
            a, b = prev_j, j
            for _ in range(40):
                m = (a + b) / 2
                if diff(m) < 0:
                    a = m
                else:
                    b = m
            return (a + b) / 2
        prev_j, prev_d = j, d
    return jd0


def kp_horary(number, when_iso, lat, lon, tz, question):
    nums = kp_numbers()
    n, a, b, sign, star, sub = nums[max(1, min(249, int(number))) - 1]
    jd, local = _jd_now(when_iso, tz)
    jd_c = _find_rising(a + 1e-4, jd - 0.5, lat, lon)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    cusps, _ = swe.houses_ex(jd_c, lat, lon, b"P", swe.FLG_SIDEREAL)
    cusps = list(cusps)
    fl = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    pos = {}
    for name, pid in vedic.PLANETS7:
        pos[name] = swe.calc_ut(jd, pid, fl)[0][0]
    rahu = swe.calc_ut(jd, swe.MEAN_NODE, fl)[0][0]
    pos["Rahu"], pos["Ketu"] = rahu, (rahu + 180) % 360

    def house_of(l):
        for i in range(12):
            x, y = cusps[i], cusps[(i + 1) % 12]
            if (l - x) % 360 < (y - x) % 360:
                return i + 1
        return 1
    planets = {p: {"lon": l, "sign": SIGNS[int(l // 30)], "house": house_of(l), **vedic.kp_lords(l)} for p, l in pos.items()}
    owns = {p: [h + 1 for h in range(12) if SIGN_LORD[int(cusps[h] // 30)] == p] for p in pos}

    def signifies(p):
        """Houses a planet signifies: through its star lord (occupied and owned), then its own (occupied and owned)."""
        st = planets[p]["star_lord"]
        hs = [planets[st]["house"]] + owns.get(st, []) + [planets[p]["house"]] + owns.get(p, [])
        if p in ("Rahu", "Ketu"):          # nodes also give the results of their sign lord
            sl = SIGN_LORD[int(pos[p] // 30)]
            hs += [planets[sl]["house"]] + owns.get(sl, [])
        seen = []
        for h in hs:
            if h not in seen:
                seen.append(h)
        return seen
    main, fav, opp, q_en, q_hi = QUESTIONS[question]
    csl = vedic.kp_lords(cusps[main - 1])["sub_lord"]
    sig = signifies(csl)
    good = [h for h in sig if h in fav]
    bad = [h for h in sig if h in opp]
    if good and len(good) >= len(bad):
        lean = "favourable"
    elif bad and not good:
        lean = "against"
    else:
        lean = "mixed"
    # ruling planets at the moment of judgement
    vara = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"][local.weekday()]
    asc_now = _kp_asc(jd, lat, lon)
    ml = vedic.kp_lords(pos["Moon"])
    al = vedic.kp_lords(asc_now)
    ruling = []
    for p in (al["sign_lord"], al["star_lord"], ml["sign_lord"], ml["star_lord"], vara):
        if p not in ruling:
            ruling.append(p)
    return {"method": "kp", "number": n, "question": question, "question_text": bi(q_en, q_hi),
            "ascendant": {"sign": sign, "from_deg": round(a % 30, 3), "star_lord": star, "sub_lord": sub},
            "cusps": [{"house": i + 1, "sign": SIGNS[int(c // 30)], "deg": round(c % 30, 2), **vedic.kp_lords(c)} for i, c in enumerate(cusps)],
            "planets": {p: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()} for p, o in planets.items()},
            "main_house": main, "cusp_sub_lord": csl, "signifies": sig, "favourable_houses": sorted(fav), "opposing_houses": sorted(opp),
            "found_favourable": good, "found_opposing": bad, "lean": lean, "ruling_planets": ruling,
            "summary": _kp_words(main, csl, sig, good, bad, lean, ruling, fav, opp)}


def _kp_words(main, csl, sig, good, bad, lean, ruling, fav, opp):
    hs = ", ".join(str(h) for h in sig)
    lean_en = {"favourable": "The signs lean favourable.", "against": "The signs lean against it for now.", "mixed": "The signs are mixed."}[lean]
    lean_hi = {"favourable": "संकेत अनुकूल हैं।", "against": "अभी संकेत इसके विरुद्ध हैं।", "mixed": "संकेत मिश्रित हैं।"}[lean]
    rp = f" {csl} is also a ruling planet now, which KP reads as confirmation." if csl in ruling else ""
    rp_hi = f" {HS.PLANET.get(csl, csl)} अभी शासक ग्रह भी है, जिसे केपी पुष्टि मानता है।" if csl in ruling else ""
    return bi(f"The sub-lord of the {_ord(main)} cusp is {csl}. It signifies houses {hs}; houses {', '.join(map(str, sorted(fav)))} support the matter "
              f"and {', '.join(map(str, sorted(opp)))} work against it. {lean_en}{rp}",
              f"{HOUSE_HI[main]} भाव के कस्प का उप-स्वामी {HS.PLANET.get(csl, csl)} है। यह भाव {hs} का कारक है; भाव {', '.join(map(str, sorted(fav)))} "
              f"इस विषय में सहायक हैं और {', '.join(map(str, sorted(opp)))} विरोधी। {lean_hi}{rp_hi}")


# ------------------------------------------------------------------ Vedic Prashna
def prashna(when_iso, lat, lon, tz, place, question, ayanamsa="lahiri"):
    jd, local = _jd_now(when_iso, tz)
    c = chart_engine.build_chart(_args(local, lat, lon, tz, place, ayanamsa))
    v = c["vedic"]
    pl, houses = v["planets"], v["houses"]
    lag = v["lagna"]["sign"]
    main, *_rest, q_en, q_hi = QUESTIONS[question]
    llord = SIGN_LORD[SIGNS.index(lag)]
    hlord = houses[main - 1]["lord"]
    checks = []

    def add(ok, en, hi):
        checks.append({"ok": ok, "text": bi(en, hi)})
    # 1. Lagna lord
    lp = pl[llord]
    good_h = lp["house"] in (1, 4, 5, 7, 9, 10, 11)
    strong = lp.get("dignity") in ("exalted", "own sign", "moolatrikona")
    add(good_h or strong, f"The Lagna lord {llord} is in the {_ord(lp['house'])} house" + (f", {lp['dignity']}" if lp.get("dignity") not in (None, "", "n/a", "neutral sign") else "") +
        (": the person asking has the strength to act." if good_h or strong else ": the person asking may need help or more time."),
        f"लग्न स्वामी {HS.PLANET.get(llord, llord)} {HOUSE_HI[lp['house']]} भाव में है" + (": प्रश्नकर्ता में आगे बढ़ने का बल है।" if good_h or strong else ": प्रश्नकर्ता को सहायता या समय की ज़रूरत हो सकती है।"))
    # 2. Moon
    mo = pl["Moon"]
    waxing = v["panchang"]["tithi_number_1_30"] <= 15
    moon_ok = mo["house"] not in (6, 8, 12) and mo.get("dignity") != "debilitated"
    add(moon_ok, f"The Moon is in the {_ord(mo['house'])} house, {'waxing' if waxing else 'waning'}" + (": the mind behind the question is steady." if moon_ok else ": worry may be colouring the question."),
        f"चंद्र {HOUSE_HI[mo['house']]} भाव में, {'बढ़ता' if waxing else 'घटता'} है" + (": प्रश्न के पीछे मन स्थिर है।" if moon_ok else ": प्रश्न पर चिंता का असर हो सकता है।"))
    # 3. house of the question and its lord
    hp = pl[hlord]
    lord_ok = hp["house"] not in (6, 8, 12)
    add(lord_ok, f"{hlord}, lord of the {_ord(main)} house (the question), is in the {_ord(hp['house'])} house" + (": well placed." if lord_ok else ": in a hidden house, so expect delays."),
        f"प्रश्न के {HOUSE_HI[main]} भाव का स्वामी {HS.PLANET.get(hlord, hlord)} {HOUSE_HI[hp['house']]} भाव में है" + (": अच्छी स्थिति।" if lord_ok else ": छिपे भाव में, इसलिए देरी संभव।"))
    occ = houses[main - 1]["occupants"]
    ben = [p for p in occ if p in BENEFICS]
    mal = [p for p in occ if p in MALEFICS]
    if occ:
        add(len(ben) >= len(mal), f"In the {_ord(main)} house: {', '.join(occ)}." + (" Benefics there help." if ben else " Malefics there ask for patience."),
            f"{HOUSE_HI[main]} भाव में: {', '.join(HS.PLANET.get(p, p) for p in occ)}।" + (" वहाँ शुभ ग्रह सहायक हैं।" if ben else " वहाँ पाप ग्रह धैर्य माँगते हैं।"))
    # 4. link between the Lagna lord and the house lord
    link = None
    if llord == hlord:
        link = ("the same planet rules both", "एक ही ग्रह दोनों का स्वामी है")
    elif lp["sign"] == hp["sign"]:
        link = ("they are together in one sign", "दोनों एक ही राशि में हैं")
    elif SIGN_LORD[SIGNS.index(lp["sign"])] == hlord and SIGN_LORD[SIGNS.index(hp["sign"])] == llord:
        link = ("they exchange signs", "दोनों राशि परिवर्तन में हैं")
    else:
        asp = vedic.sign_aspects(pl)
        if hlord in asp.get(llord, []) and llord in asp.get(hlord, []):
            link = ("they aspect each other", "दोनों एक-दूसरे को देखते हैं")
    ith = None
    if llord in tajika.DEEPTAMSA and hlord in tajika.DEEPTAMSA and llord != hlord:
        ith = tajika._aspect_by_degree(lp["lon"], hp["lon"], lp.get("daily_motion", 0), hp.get("daily_motion", 0), tajika.DEEPTAMSA[llord], tajika.DEEPTAMSA[hlord])
    if ith and ith["applying"]:
        add(True, f"The Lagna lord and the house lord form an Ithasala (applying aspect, {ith['gap']:.1f}° apart): the matter moves toward completion.",
            f"लग्न स्वामी और भाव स्वामी में इत्थशाल (निकट आता योग, {ith['gap']:.1f}° का अंतर): विषय पूर्णता की ओर बढ़ता है।")
    elif ith:
        add(False, "The Lagna lord and the house lord are separating (Ishrafa): the best moment may have passed; try again with a fresh approach.",
            "लग्न स्वामी और भाव स्वामी दूर जा रहे हैं (इशराफ़): सबसे अच्छा समय निकल गया हो सकता है; नए ढंग से फिर प्रयास करें।")
    if link:
        add(True, f"The Lagna lord and the house lord are linked: {link[0]}.", f"लग्न स्वामी और भाव स्वामी जुड़े हैं: {link[1]}।")
    elif not ith:
        add(False, "The Lagna lord and the house lord are not linked: the matter may need a go-between or more effort.",
            "लग्न स्वामी और भाव स्वामी जुड़े नहीं हैं: विषय में मध्यस्थ या अधिक प्रयास की ज़रूरत हो सकती है।")
    yes = sum(1 for x in checks if x["ok"])
    share = yes / max(1, len(checks))
    lean = "favourable" if share >= 0.67 else "against" if share <= 0.25 else "mixed"
    return {"method": "prashna", "question": question, "question_text": bi(q_en, q_hi), "asked_at": local.strftime("%Y-%m-%d %H:%M"), "place": place,
            "lagna": lag, "lagna_lord": llord, "house": main, "house_lord": hlord, "moon_sign": mo["sign"], "moon_house": mo["house"],
            "planets": {p: {"sign": o["sign"], "house": o["house"], "deg": round(o["deg_in_sign"], 1), "retrograde": o.get("retrograde", False)} for p, o in pl.items()},
            "checks": checks, "favourable": yes, "out_of": len(checks), "lean": lean,
            "summary": bi({"favourable": "Most Prashna checks are favourable.", "mixed": "The Prashna checks are mixed.",
                           "against": "Most Prashna checks ask for patience; the matter may need more time or a new approach."}[lean],
                          {"favourable": "अधिकतर प्रश्न-संकेत अनुकूल हैं।", "mixed": "प्रश्न-संकेत मिश्रित हैं।",
                           "against": "अधिकतर संकेत धैर्य माँगते हैं; विषय को अधिक समय या नए ढंग की ज़रूरत हो सकती है।"}[lean])}


def _args(local, lat, lon, tz, place, ayanamsa):
    import engine_api
    return engine_api._chart_args({"name": "Prashna", "date": local.strftime("%Y-%m-%d"), "time": local.strftime("%H:%M"), "lat": lat, "lon": lon,
                                   "tz": tz, "place": place, "ayanamsa": ayanamsa, "modules": "vedic", "now": local.strftime("%Y-%m-%d")})


NOTE = bi("A question chart shows the tendencies around a matter at the moment it is sincerely asked. Ask once, about one matter, and treat the "
          "answer as guidance: your effort and the circumstances decide the outcome.",
          "प्रश्न कुंडली उस क्षण की प्रवृत्तियाँ दिखाती है जब कोई बात सच्चे मन से पूछी जाए। एक बात के लिए एक बार पूछें और उत्तर को मार्गदर्शन मानें: "
          "परिणाम आपका प्रयास और परिस्थितियाँ तय करती हैं।")


def ask(request_json):
    r = json.loads(request_json)
    q = r.get("question") if r.get("question") in QUESTIONS else "job"
    when = r.get("when") or dt.datetime.now(ZoneInfo(r["tz"])).strftime("%Y-%m-%dT%H:%M:%S")
    if r.get("method") == "kp":
        out = kp_horary(int(r.get("number", 1)), when, float(r["lat"]), float(r["lon"]), r["tz"], q)
    else:
        out = prashna(when, float(r["lat"]), float(r["lon"]), r["tz"], r.get("place", ""), q, r.get("ayanamsa") or "lahiri")
    out["note"] = NOTE
    out["questions"] = {k: bi(v[3], v[4]) for k, v in QUESTIONS.items()}
    return json.dumps(out, ensure_ascii=False)
