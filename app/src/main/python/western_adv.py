"""western_adv.py - v26: the specialist Western and astronomy sections.

Coordinate perspectives (geocentric, topocentric, heliocentric), the hypothetical bodies (the eight Uranian points,
Black Moon Lilith and Transpluto), the 90-degree dial and midpoint trees of cosmobiology, the Huber age point through
the Koch houses, the sky at birth (altitude and azimuth), heliacal risings and settings, and local space with parans.

Everything here is computed from the Swiss Ephemeris; no school-specific interpretation is attached.
"""
import datetime as dt

import swisseph as swe

import hindi_shell as HS
import western_more as WM
from app_details import bi, items, para, table

URANIAN = [("Cupido", swe.CUPIDO, "क्यूपिडो", "family and groups", "परिवार और समूह"),
           ("Hades", swe.HADES, "हेडीज़", "what is old or hidden", "जो पुराना या छिपा है"),
           ("Zeus", swe.ZEUS, "ज़ीउस", "directed energy", "दिशा पाई हुई ऊर्जा"),
           ("Kronos", swe.KRONOS, "क्रोनोस", "authority and high office", "अधिकार और उच्च पद"),
           ("Apollon", swe.APOLLON, "अपोलोन", "expansion and trade", "विस्तार और व्यापार"),
           ("Admetos", swe.ADMETOS, "एडमेटोस", "narrowing and depth", "संकुचन और गहराई"),
           ("Vulkanus", swe.VULKANUS, "वल्कानस", "great force", "महान बल"),
           ("Poseidon", swe.POSEIDON, "पोसाइडन", "ideas and insight", "विचार और अंतर्दृष्टि")]
OTHER_PTS = [("Black Moon Lilith (mean)", swe.MEAN_APOG, "काली चंद्र लिलिथ (माध्य)"),
             ("Black Moon Lilith (true)", swe.OSCU_APOG, "काली चंद्र लिलिथ (वास्तविक)"),
             ("Transpluto (Isis)", swe.ISIS, "ट्रांसप्लूटो (आइसिस)")]
HELIACAL = [("Venus", swe.VENUS, "शुक्र"), ("Mercury", swe.MERCURY, "बुध"), ("Mars", swe.MARS, "मंगल"),
            ("Jupiter", swe.JUPITER, "गुरु"), ("Saturn", swe.SATURN, "शनि")]
ANGLE_EVENT = [("rises", "उदय", swe.CALC_RISE), ("sets", "अस्त", swe.CALC_SET),
               ("culminates", "मध्य आकाश", swe.CALC_MTRANSIT), ("is lowest", "पाताल", swe.CALC_ITRANSIT)]
DIRECTION = [("N", "उत्तर"), ("NE", "ईशान"), ("E", "पूर्व"), ("SE", "आग्नेय"), ("S", "दक्षिण"),
             ("SW", "नैऋत्य"), ("W", "पश्चिम"), ("NW", "वायव्य")]
MONTH_HI = ["जन", "फ़र", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अग", "सित", "अक्टू", "नव", "दिस"]


def _p(name):
    return bi(name, HS.PLANET.get(name) or WM.WB_HI.get(name, name))


def _dt(jd, tz=0.0):
    y, m, d, h = swe.revjul(jd + tz / 24.0)
    return dt.datetime(y, m, d) + dt.timedelta(hours=h)


def _d(t):
    return bi(t.strftime("%d %b %Y"), f"{t.day} {MONTH_HI[t.month - 1]} {t.year}")


def _compass(az):
    return DIRECTION[int((az % 360 + 22.5) // 45) % 8]


# ------------------------------------------------------------------ F021 perspectives
def perspectives(c):
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    swe.set_topo(pl["lon"], pl["lat"], 0)
    rows = []
    for p in WM.TEN:
        b = WM.BODY[p]
        geo = swe.calc_ut(jd, b, swe.FLG_SWIEPH)[0][0]
        topo = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_TOPOCTR)[0][0]
        if p == "Sun":
            helio = bi("–")
        else:
            try:
                helio = WM._s(swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_HELCTR)[0][0])
            except Exception:
                helio = bi("–")
        diff = abs((topo - geo + 180) % 360 - 180) * 60
        rows.append([_p(p), WM._s(geo), WM._s(topo), bi(f"{diff:.1f}'"), helio])
    return {"key": "w_perspectives", "title": bi("Where the planets are seen from", "ग्रह कहाँ से देखे जाएँ"),
            "intro": bi("Geocentric is from the centre of the Earth and is what every other section uses; topocentric is from the birthplace itself; heliocentric is from the Sun.",
                        "भूकेंद्रित स्थिति पृथ्वी के केंद्र से है और बाकी हर खंड यही लेता है; स्थानकेंद्रित जन्मस्थान से है; सूर्यकेंद्रित सूर्य से।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Geocentric", "भूकेंद्रित"), bi("Topocentric", "स्थानकेंद्रित"),
                              bi("Difference", "अंतर"), bi("Heliocentric", "सूर्यकेंद्रित")], rows)],
            "note": bi("Only the Moon shifts much between the first two, because it is near. Heliocentric positions have no Ascendant or houses.",
                       "पहले दो में केवल चंद्र में बड़ा अंतर आता है, क्योंकि वह निकट है। सूर्यकेंद्रित स्थिति में लग्न और भाव नहीं होते।")}


# ------------------------------------------------------------------ F026 hypothetical points
def hypothetical(c):
    jd = c["time_pipeline"]["jd_ut"]
    rows = []
    for en, b, hi, te, th in URANIAN:
        try:
            lon = swe.calc_ut(jd, b, swe.FLG_SWIEPH)[0][0]
        except Exception:
            continue
        rows.append([bi(en, hi), WM._s(lon), bi(te, th)])
    other = []
    for en, b, hi in OTHER_PTS:
        try:
            other.append([bi(en, hi), WM._s(swe.calc_ut(jd, b, swe.FLG_SWIEPH)[0][0])])
        except Exception:
            pass
    return {"key": "w_hypothetical", "title": bi("Hypothetical points", "कल्पित बिंदु"),
            "blocks": [para(bi("The eight Uranian points of the Hamburg school:", "हैम्बर्ग परंपरा के आठ यूरेनियन बिंदु:")),
                       table([bi("Point", "बिंदु"), bi("At", "स्थान"), bi("Theme", "विषय")], rows),
                       para(bi("Other calculated points:", "अन्य गणित बिंदु:")),
                       table([bi("Point", "बिंदु"), bi("At", "स्थान")], other)],
            "note": bi("These are calculated points, not bodies anyone has seen. They are given because some schools use them; the app's readings do not.",
                       "ये गणना से निकाले गए बिंदु हैं, कोई देखा हुआ पिंड नहीं। कुछ परंपराएँ इन्हें लेती हैं, इसलिए दिए गए हैं; ऐप के फलादेश इन्हें नहीं लेते।")}


# ------------------------------------------------------------------ F039 cosmobiology
def dial90(c, pos, asc, mc):
    pts = {p: pos[p]["lon"] for p in WM.TEN}
    pts["ASC"], pts["MC"] = asc, mc
    hi = lambda n: HS.PLANET.get(n) or WM.WB_HI.get(n) or {"ASC": "लग्न", "MC": "दशम"}[n]     # noqa: E731
    en = lambda n: {"ASC": "Ascendant", "MC": "Midheaven"}.get(n, n)                           # noqa: E731
    rows = sorted(([bi(en(k), hi(k)), bi(f"{v % 90:.2f}°"), bi(f"{v % 45:.2f}°")] for k, v in pts.items()),
                  key=lambda r: float(r[1]["en"][:-1]))
    trees = []
    for focus in ("Sun", "Moon", "ASC", "MC"):
        f = pts[focus]
        names = [k for k in pts if k != focus]
        found = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                d = (pts[b] - pts[a]) % 360
                mid = (pts[a] + (d if d <= 180 else d - 360) / 2) % 360
                orb = abs((mid - f + 45) % 90 - 45)        # the 90-degree dial folds every hard aspect onto one point
                if orb <= 1.5:
                    found.append((orb, f"{en(a)}/{en(b)}", f"{hi(a)}/{hi(b)}"))
        found.sort()
        if found:
            trees.append(bi(f"{en(focus)} = " + ", ".join(f"{t} ({o:.1f}°)" for o, t, _ in found[:6]),
                            f"{hi(focus)} = " + ", ".join(f"{t} ({o:.1f}°)" for o, _, t in found[:6])))
    return {"key": "w_dial", "title": bi("Cosmobiology: the 90-degree dial", "कॉस्मोबायोलॉजी: 90 अंश का डायल"),
            "intro": bi("On the 90-degree dial every conjunction, square and opposition falls on the same point, so only the hard contacts show.",
                        "90 अंश के डायल पर युति, केंद्र और सम्मुख दृष्टि एक ही बिंदु पर आ जाती हैं, इसलिए केवल कठोर संबंध दिखते हैं।"),
            "blocks": [table([bi("Point", "बिंदु"), bi("On the 90° dial", "90° डायल पर"), bi("On the 45° dial", "45° डायल पर")], rows),
                       para(bi("Midpoint trees within 1.5°:", "1.5° के भीतर मध्यबिंदु वृक्ष:")),
                       items(trees or [bi("none", "कोई नहीं")])],
            "note": bi("After Ebertin's method: a planet standing on a midpoint is read as the two together. Orb 1.5° on the dial.",
                       "एबर्टिन की पद्धति के अनुसार: मध्यबिंदु पर खड़ा ग्रह दोनों को साथ लेकर पढ़ा जाता है। डायल पर अंतर 1.5°।")}


# ------------------------------------------------------------------ F040 Huber age point
def huber(c, pos):
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    now = dt.datetime.fromisoformat(c["meta"]["generated_for_date"])
    jd_now = swe.julday(now.year, now.month, now.day, 12.0)
    age = (jd_now - jd) / 365.2422
    try:
        cusps = swe.houses(jd, pl["lat"], pl["lon"], b"K")[0]
    except Exception:
        return None
    house = int(age // 6) % 12
    within = (age % 6) / 6.0
    a, b = cusps[house], cusps[(house + 1) % 12]
    span = (b - a) % 360
    ap = (a + span * within) % 360
    rows = []
    for k in range(12):
        start = k * 6
        rows.append([bi(f"{k + 1}"), bi(f"{start}–{start + 6}"), WM._s(cusps[k]),
                     bi("age point here now", "आयु बिंदु अभी यहाँ") if k == house else bi("")])
    hits = []
    for p in WM.TEN:
        o = abs((pos[p]["lon"] - ap + 180) % 360 - 180)
        if o <= 3.0:
            when = age + (o / 60.0)
            hits.append(bi(f"{p} within {o:.1f}° of the age point", f"{HS.PLANET.get(p, p)} आयु बिंदु से {o:.1f}° के भीतर"))
    return {"key": "w_huber", "title": bi("Huber age point", "हूबर आयु बिंदु"),
            "intro": bi(f"At age {age:.1f} the age point is in Koch house {house + 1}, at {WM._s(ap)['en']}.",
                        f"{age:.1f} वर्ष की आयु में आयु बिंदु कोख भाव {house + 1} में है, {WM._s(ap)['hi']} पर।"),
            "blocks": [table([bi("House", "भाव"), bi("Ages", "आयु"), bi("Cusp", "भाव संधि"), bi("", "")], rows)] +
                      ([para(bi("Near a planet now:", "अभी किसी ग्रह के निकट:")), items(hits)] if hits else []),
            "note": bi("The Huber age point leaves the Ascendant at birth and takes six years to cross each Koch house, seventy-two years for the circle.",
                       "हूबर आयु बिंदु जन्म के समय लग्न से चलता है और हर कोख भाव को पार करने में छह वर्ष, पूरे चक्र में बहत्तर वर्ष लेता है।")}


# ------------------------------------------------------------------ F046 the sky at birth
def sky_view(c):
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    geo = (pl["lon"], pl["lat"], 0)
    rows = []
    up = 0
    for p in WM.TEN:
        eq = swe.calc_ut(jd, WM.BODY[p], swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
        az, alt, _ = swe.azalt(jd, swe.EQU2HOR, geo, 1013.25, 15.0, (eq[0], eq[1], 1.0))
        az = (az + 180) % 360          # the library measures azimuth from the south; the compass is measured from the north
        d = _compass(az)
        if alt > 0:
            up += 1
        rows.append([_p(p), bi(f"{alt:+.1f}°"), bi(f"{az:.0f}°"), bi(*d),
                     bi("above the horizon", "क्षितिज के ऊपर") if alt > 0 else bi("below the horizon", "क्षितिज के नीचे")])
    return {"key": "w_sky", "title": bi("The sky at your birth", "आपके जन्म के समय का आकाश"),
            "intro": bi(f"{up} of the ten planets were above the horizon.", f"दस ग्रहों में से {up} क्षितिज के ऊपर थे।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Height above the horizon", "क्षितिज से ऊँचाई"), bi("Azimuth", "दिगंश"),
                              bi("Direction to look", "किस दिशा में"), bi("", "")], rows)],
            "note": bi("Where each planet stood in the sky over the birthplace, by the compass and by height. Refraction at 15 °C and 1013 hPa.",
                       "जन्मस्थान के आकाश में हर ग्रह कहाँ था, दिशा और ऊँचाई से। अपवर्तन 15 °C और 1013 hPa पर।")}


# ------------------------------------------------------------------ F060 heliacal events
def heliacal(c):
    pl = c["meta"]["place"]
    tz = c["time_pipeline"]["utc_offset_hours"]
    now = dt.datetime.fromisoformat(c["meta"]["generated_for_date"])
    j0 = swe.julday(now.year, now.month, now.day, 0.0)
    geo = (pl["lon"], pl["lat"], 0)
    atm, obs = (0, 0, 0, 0), (0, 0, 0, 0, 0, 0)
    rows = []
    for en, _b, hi in HELIACAL:
        for ev, (ten, thi) in ((swe.HELIACAL_RISING, ("first seen at dawn", "भोर में पहली बार दिखाई")),
                               (swe.HELIACAL_SETTING, ("last seen at dusk", "सांझ में आख़िरी बार दिखाई"))):
            try:
                jd = swe.heliacal_ut(j0, geo, atm, obs, en, ev, swe.FLG_SWIEPH)[0]
            except Exception:
                continue
            if jd:
                rows.append((jd, [bi(en, hi), bi(ten, thi), _d(_dt(jd, tz))]))
    rows.sort(key=lambda x: x[0])
    return {"key": "w_heliacal", "title": bi("Heliacal risings and settings", "उदय और अस्त (हेलियाकल)"),
            "intro": bi("When each planet next comes out of the Sun's light at dawn, or disappears into it at dusk, seen from the birthplace.",
                        "हर ग्रह अगली बार कब भोर में सूर्य के प्रकाश से बाहर आता है, या सांझ में उसमें छिप जाता है, जन्मस्थान से देखने पर।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Event", "घटना"), bi("Date", "तिथि")], [r for _, r in rows])],
            "note": bi("Computed with the Swiss Ephemeris visibility model for an average observer at sea level; haze and city light move these dates.",
                       "स्विस एफेमेरिस के दृश्यता मॉडल से, समुद्र तल पर एक सामान्य दर्शक के लिए; धुंध और शहर की रोशनी इन तिथियों को खिसकाती है।")}


# ------------------------------------------------------------------ F065 local space and parans
def local_space(c):
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    geo = (pl["lon"], pl["lat"], 0)
    rows = []
    for p in WM.TEN:
        eq = swe.calc_ut(jd, WM.BODY[p], swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
        az = (swe.azalt(jd, swe.EQU2HOR, geo, 1013.25, 15.0, (eq[0], eq[1], 1.0))[0] + 180) % 360
        rows.append([_p(p), bi(f"{az:.0f}°"), bi(*_compass(az))])
    # parans: two planets on an angle within 20 minutes of each other on the birth day
    day0 = swe.julday(*swe.revjul(jd)[:3], 0.0)
    events = []
    for p in WM.TEN:
        for ten, thi, flag in ANGLE_EVENT:
            try:
                ok, t = swe.rise_trans(day0, WM.BODY[p], flag | swe.BIT_DISC_CENTER, geo, 1013.25, 15.0)
            except Exception:
                continue
            if ok >= 0 and t and t[0] and t[0] - day0 < 1.0:
                events.append((t[0], p, ten, thi))
    events.sort()
    par = []
    for i, (t1, p1, e1, h1) in enumerate(events):
        for t2, p2, e2, h2 in events[i + 1:]:
            if t2 - t1 > 20 / 1440.0:
                break
            if p1 != p2:
                mins = (t2 - t1) * 1440
                par.append(bi(f"{p1} {e1} as {p2} {e2} ({mins:.0f} min apart)",
                              f"{HS.PLANET.get(p1, p1)} {h1} और {HS.PLANET.get(p2, p2)} {h2} ({mins:.0f} मिनट का अंतर)"))
    return {"key": "w_local_space", "title": bi("Local space and parans", "स्थानिक दिशाएँ और पैरान"),
            "intro": bi("Local space gives each planet a compass direction from the birthplace; a paran is two planets on an angle at the same time.",
                        "स्थानिक दिशा हर ग्रह को जन्मस्थान से एक दिशा देती है; पैरान वह है जब दो ग्रह एक ही समय किसी कोण पर हों।"),
            "blocks": [table([bi("Planet", "ग्रह"), bi("Azimuth", "दिगंश"), bi("Direction", "दिशा")], rows),
                       para(bi("Parans on the birth day (within 20 minutes):", "जन्म के दिन के पैरान (20 मिनट के भीतर):")),
                       items(par[:12] or [bi("none", "कोई नहीं")])],
            "note": bi("Directions are from the birthplace; walking or building along a planet's line is a local-space practice, not a prediction.",
                       "दिशाएँ जन्मस्थान से हैं; किसी ग्रह की दिशा में चलना या निर्माण करना एक स्थानिक-दिशा प्रथा है, भविष्यवाणी नहीं।")}


def build(c):
    out = []
    jd, pl = c["time_pipeline"]["jd_ut"], c["meta"]["place"]
    try:
        pos = WM._positions(jd)
        ascmc = swe.houses(jd, pl["lat"], pl["lon"], b"P")[1]
    except Exception:
        return out

    def add(f, *a):
        try:
            r = f(*a)
        except Exception:
            return
        if r:
            out.append(r)
    add(perspectives, c)
    add(hypothetical, c)
    add(dial90, c, pos, ascmc[0], ascmc[1])
    add(huber, c, pos)
    add(sky_view, c)
    add(local_space, c)
    add(heliacal, c)
    return out
