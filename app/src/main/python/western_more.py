"""western_more.py - Western depth (v21): aspect patterns, dispositors and receptions, essential dignities with the
almuten of the Ascendant, the seven Hermetic lots, firdaria, declination parallels, the harmonic-9, draconic and
sidereal (Fagan-Bradley) positions, this year's Aries ingress chart, and astrocartography for 45 world cities.

Conventions (stated in the notes): tropical zodiac; traditional rulers for dispositors and dignities; Dorothean
triplicities by sect; Egyptian terms; Chaldean faces; lots by Paulus with day/night reversal; Bonatti's firdaria with
the nodes at the end; aspect patterns from the natal aspects already found (orbs as computed there).
"""
import datetime as dt
import math

import swisseph as swe

import hindi_shell as HS
from app_details import bi, table, para, items

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SEVEN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
TEN = SEVEN + ["Uranus", "Neptune", "Pluto"]
BODY = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO}
RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
EXALT = {"Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6}
TRIP = {0: ("Sun", "Jupiter", "Saturn"), 1: ("Venus", "Moon", "Mars"), 2: ("Saturn", "Mercury", "Jupiter"), 3: ("Venus", "Mars", "Moon")}
TERMS = [[("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
         [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
         [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
         [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
         [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
         [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
         [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
         [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
         [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
         [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
         [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
         [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)]]
CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
FACE_START = "Mars"
WB_HI = {"Uranus": "यूरेनस", "Neptune": "नेप्च्यून", "Pluto": "प्लूटो", "North Node": "उत्तर नोड", "South Node": "दक्षिण नोड"}
SIGN_HI = HS.SIGN
CITIES = [("Delhi", 28.61, 77.21), ("Mumbai", 19.08, 72.88), ("Kolkata", 22.57, 88.36), ("Chennai", 13.08, 80.27), ("Bengaluru", 12.97, 77.59),
          ("Hyderabad", 17.39, 78.49), ("Lucknow", 26.85, 80.95), ("Varanasi", 25.32, 82.97), ("Kathmandu", 27.72, 85.32), ("Dhaka", 23.81, 90.41),
          ("Karachi", 24.86, 67.01), ("Colombo", 6.93, 79.86), ("Dubai", 25.20, 55.27), ("Riyadh", 24.71, 46.68), ("Singapore", 1.35, 103.82),
          ("Kuala Lumpur", 3.14, 101.69), ("Bangkok", 13.76, 100.50), ("Jakarta", -6.21, 106.85), ("Hong Kong", 22.32, 114.17), ("Shanghai", 31.23, 121.47),
          ("Beijing", 39.90, 116.41), ("Tokyo", 35.68, 139.69), ("Seoul", 37.57, 126.98), ("Sydney", -33.87, 151.21), ("Melbourne", -37.81, 144.96),
          ("Auckland", -36.85, 174.76), ("London", 51.51, -0.13), ("Paris", 48.86, 2.35), ("Berlin", 52.52, 13.40), ("Rome", 41.90, 12.50),
          ("Madrid", 40.42, -3.70), ("Amsterdam", 52.37, 4.90), ("Moscow", 55.76, 37.62), ("Istanbul", 41.01, 28.98), ("Cairo", 30.04, 31.24),
          ("Nairobi", -1.29, 36.82), ("Johannesburg", -26.20, 28.05), ("Lagos", 6.52, 3.38), ("New York", 40.71, -74.01), ("Toronto", 43.65, -79.38),
          ("Chicago", 41.88, -87.63), ("Los Angeles", 34.05, -118.24), ("San Francisco", 37.77, -122.42), ("Mexico City", 19.43, -99.13),
          ("São Paulo", -23.55, -46.63)]
CITY_HI = {"Delhi": "दिल्ली", "Mumbai": "मुंबई", "Kolkata": "कोलकाता", "Chennai": "चेन्नई", "Bengaluru": "बेंगलुरु", "Hyderabad": "हैदराबाद",
           "Lucknow": "लखनऊ", "Varanasi": "वाराणसी", "Kathmandu": "काठमांडू", "Dhaka": "ढाका", "Karachi": "कराची", "Colombo": "कोलंबो", "Dubai": "दुबई",
           "Riyadh": "रियाद", "Singapore": "सिंगापुर", "Kuala Lumpur": "कुआलालंपुर", "Bangkok": "बैंकॉक", "Jakarta": "जकार्ता", "Hong Kong": "हांगकांग",
           "Shanghai": "शंघाई", "Beijing": "बीजिंग", "Tokyo": "टोक्यो", "Seoul": "सियोल", "Sydney": "सिडनी", "Melbourne": "मेलबर्न", "Auckland": "ऑकलैंड",
           "London": "लंदन", "Paris": "पेरिस", "Berlin": "बर्लिन", "Rome": "रोम", "Madrid": "मैड्रिड", "Amsterdam": "एम्स्टर्डम", "Moscow": "मॉस्को",
           "Istanbul": "इस्तांबुल", "Cairo": "काहिरा", "Nairobi": "नैरोबी", "Johannesburg": "जोहान्सबर्ग", "Lagos": "लागोस", "New York": "न्यूयॉर्क",
           "Toronto": "टोरंटो", "Chicago": "शिकागो", "Los Angeles": "लॉस एंजेलिस", "San Francisco": "सैन फ़्रांसिस्को", "Mexico City": "मेक्सिको सिटी",
           "São Paulo": "साओ पाउलो"}
ACG_THEME = {"Sun": ("recognition and confidence", "पहचान और आत्मविश्वास"), "Moon": ("home, comfort and family", "घर, सुख और परिवार"),
             "Venus": ("love, beauty and ease", "प्रेम, सौंदर्य और सहजता"), "Jupiter": ("growth, luck and teachers", "विकास, सौभाग्य और गुरु"),
             "Mars": ("drive and competition", "उत्साह और प्रतिस्पर्धा"), "Saturn": ("hard work and responsibility", "कठोर परिश्रम और ज़िम्मेदारी"),
             "Mercury": ("study, trade and networking", "पढ़ाई, व्यापार और संपर्क")}
ANGLE = {"MC": ("career (MC)", "करियर (MC)"), "IC": ("home (IC)", "घर (IC)"), "ASC": ("self (rising)", "स्वयं (उदय)"), "DSC": ("partners (setting)", "साथी (अस्त)")}


def _p(name):
    return bi(name, HS.PLANET.get(name) or WB_HI.get(name, name))


def _s(lon):
    s = SIGNS[int(lon % 360 // 30)]
    return bi(f"{s} {lon % 30:.1f}°", f"{SIGN_HI.get(s, s)} {lon % 30:.1f}°")


def _positions(jd):
    out = {}
    for n, b in BODY.items():
        xx = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_SPEED)[0]
        eq = swe.calc_ut(jd, b, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
        out[n] = {"lon": xx[0], "speed": xx[3], "ra": eq[0], "dec": eq[1]}
    nn = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)[0][0]
    out["North Node"] = {"lon": nn, "speed": 0, "ra": None, "dec": None}
    return out


# ------------------------------------------------------------------ patterns, dispositors
def patterns(w):
    asp = {}
    for a in w.get("natal_aspects", []):
        if a["a"] in TEN and a["b"] in TEN:
            asp[frozenset((a["a"], a["b"]))] = a["aspect"]

    def has(x, y, kind):
        return asp.get(frozenset((x, y))) == kind
    found = []
    pl = [p for p in TEN if p in w["planets"]]
    import itertools
    for a, b, c in itertools.combinations(pl, 3):
        if has(a, b, "trine") and has(b, c, "trine") and has(a, c, "trine"):
            found.append(("Grand trine", "ग्रैंड ट्राइन", [a, b, c], "an easy flow of talent", "प्रतिभा का सहज प्रवाह"))
        for x, y, z in ((a, b, c), (a, c, b), (b, c, a)):
            if has(x, y, "opposition") and has(x, z, "square") and has(y, z, "square"):
                found.append(("T-square", "टी-स्क्वेयर", [x, y, z], f"tension that drives effort, focused through {z}", f"{HS.PLANET.get(z) or WB_HI.get(z, z)} के माध्यम से प्रयास को प्रेरित करता तनाव"))
            if has(x, y, "sextile") and has(x, z, "quincunx") and has(y, z, "quincunx"):
                found.append(("Yod", "योड", [x, y, z], f"a special task pointed at {z}", f"{HS.PLANET.get(z) or WB_HI.get(z, z)} की ओर एक विशेष उद्देश्य"))
    for combo in itertools.combinations(pl, 4):
        a, b, c, d = combo
        for x, y, u, v in ((a, b, c, d), (a, c, b, d), (a, d, b, c)):
            if has(x, y, "opposition") and has(u, v, "opposition") and all(has(p, q, "square") for p in (x, y) for q in (u, v)):
                found.append(("Grand cross", "ग्रैंड क्रॉस", [x, y, u, v], "strong drive pulled in four directions", "चार दिशाओं में खिंचती प्रबल ऊर्जा"))
    by_sign = {}
    for p in pl:
        by_sign.setdefault(w["planets"][p]["sign"], []).append(p)
    for s, ps in by_sign.items():
        if len(ps) >= 3:
            found.append(("Stellium", "स्टेलियम", ps, f"a strong focus on {s} themes", f"{SIGN_HI.get(s, s)} के विषयों पर गहरा ध्यान"))
    seen, uniq = set(), []
    for f in found:
        k = (f[0], frozenset(f[2]))
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq


def dispositors(w):
    sign = {p: SIGNS.index(w["planets"][p]["sign"]) for p in SEVEN}
    disp = {p: RULER[sign[p]] for p in SEVEN}
    chains = {}
    for p in SEVEN:
        seen, cur = [p], p
        while disp[cur] not in seen:
            seen.append(disp[cur])
            cur = disp[cur]
        chains[p] = seen
    own = [p for p in SEVEN if disp[p] == p]
    final = own[0] if len(own) == 1 and all(chains[p][-1] == own[0] for p in SEVEN) else None
    mutual = sorted({tuple(sorted((a, b))) for a in SEVEN for b in SEVEN if a != b and disp[a] == b and disp[b] == a})
    return disp, chains, final, mutual


# ------------------------------------------------------------------ dignities
def _term(lon):
    s, d = int(lon // 30) % 12, lon % 30
    return next(p for p, end in TERMS[s] if d < end)


def _face(lon):
    i = int(lon % 360 // 10)
    return CHALDEAN[(CHALDEAN.index(FACE_START) + i) % 7]


def dignity(p, lon, day):
    s = int(lon % 360 // 30)
    score, tags = 0, []
    if RULER[s] == p:
        score += 5; tags.append(("domicile", "स्वगृह"))
    if EXALT.get(p) == s:
        score += 4; tags.append(("exaltation", "उच्च"))
    t = TRIP[s % 4]
    if p == (t[0] if day else t[1]):
        score += 3; tags.append(("triplicity", "त्रिकोण स्वामी"))
    if _term(lon) == p:
        score += 2; tags.append(("term", "सीमा"))
    if _face(lon) == p:
        score += 1; tags.append(("face", "मुख"))
    if RULER[(s + 6) % 12] == p:
        score -= 5; tags.append(("detriment", "शत्रु गृह"))
    if EXALT.get(p) is not None and (EXALT[p] + 6) % 12 == s:
        score -= 4; tags.append(("fall", "नीच"))
    if not any(t[0] in ("domicile", "exaltation", "triplicity", "term", "face") for t in tags):
        tags.append(("peregrine", "भ्रमणशील"))
    return score, tags


def almuten(lon, day):
    best = max(SEVEN, key=lambda p: (dignity(p, lon, day)[0], -SEVEN.index(p)))
    return best


# ------------------------------------------------------------------ lots and firdaria
def lots(asc, pos, day):
    def lot(a, b):
        return (asc + a - b) % 360
    sun, moon = pos["Sun"]["lon"], pos["Moon"]["lon"]
    fortune = lot(moon, sun) if day else lot(sun, moon)
    spirit = lot(sun, moon) if day else lot(moon, sun)
    v, me, ma, j, sa = (pos[x]["lon"] for x in ("Venus", "Mercury", "Mars", "Jupiter", "Saturn"))
    return [("Fortune", "भाग्य", fortune, "body and circumstances", "शरीर और परिस्थितियाँ"),
            ("Spirit", "आत्मा", spirit, "mind and purpose", "मन और उद्देश्य"),
            ("Eros", "प्रेम", lot(v, spirit) if day else lot(spirit, v), "desire and love", "इच्छा और प्रेम"),
            ("Necessity", "आवश्यकता", lot(fortune, me) if day else lot(me, fortune), "duties and limits", "कर्तव्य और सीमाएँ"),
            ("Courage", "साहस", lot(fortune, ma) if day else lot(ma, fortune), "boldness", "साहस"),
            ("Victory", "विजय", lot(j, spirit) if day else lot(spirit, j), "success and faith", "सफलता और विश्वास"),
            ("Nemesis", "नेमेसिस", lot(fortune, sa) if day else lot(sa, fortune), "what must be faced", "जिसका सामना करना है")]


DAY_FIRDARIA = [("Sun", 10), ("Venus", 8), ("Mercury", 13), ("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7), ("North Node", 3), ("South Node", 2)]
NIGHT_FIRDARIA = [("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7), ("Sun", 10), ("Venus", 8), ("Mercury", 13), ("North Node", 3), ("South Node", 2)]


def firdaria(birth, day, now):
    seq = DAY_FIRDARIA if day else NIGHT_FIRDARIA
    out, t = [], birth
    total = 0
    while total < 100:
        for lord, yrs in seq:
            e = t + dt.timedelta(days=yrs * 365.2425)
            subs = []
            if lord in SEVEN:
                st = CHALDEAN.index(lord)
                sl = yrs * 365.2425 / 7
                for k in range(7):
                    subs.append((CHALDEAN[(st + k) % 7], t + dt.timedelta(days=sl * k), t + dt.timedelta(days=sl * (k + 1))))
            out.append((lord, t, e, subs))
            t = e
            total += yrs
            if total >= 100:
                break
    cur = next(((l, a, b, s) for l, a, b, s in out if a <= now < b), None)
    return out, cur


# ------------------------------------------------------------------ astrocartography
def acg(jd, pos):
    gst = swe.sidtime(jd) * 15
    out = []
    for name, la, lo in CITIES:
        lst = (gst + lo) % 360
        for p in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
            ra, dec = pos[p]["ra"], pos[p]["dec"]
            ha = (lst - ra + 180) % 360 - 180
            hits = []
            if abs(ha) < 3:
                hits.append("MC")
            if abs(abs(ha) - 180) < 3:
                hits.append("IC")
            x = -math.tan(math.radians(la)) * math.tan(math.radians(dec))
            if -1 < x < 1:
                h0 = math.degrees(math.acos(x))
                if abs(ha + h0) < 3:
                    hits.append("ASC")
                if abs(ha - h0) < 3:
                    hits.append("DSC")
            for h in hits:
                out.append((name, p, h))
    return out


# ------------------------------------------------------------------ sections
def build(c):
    w = c.get("western")
    if not w:
        return []
    jd = c["time_pipeline"]["jd_ut"]
    pos = _positions(jd)
    asc = float(w["ascendant_lon"]) if "ascendant_lon" in w else None
    if asc is None:
        pl = c["meta"]["place"]
        asc = swe.houses_ex(jd, pl["lat"], pl["lon"], b"P")[1][0]
    day = (w.get("hellenistic") or {}).get("sect", "day chart").startswith("day")
    secs = []
    # patterns and dispositors
    pats = patterns(w)
    disp, chains, final, mutual = dispositors(w)
    blocks = []
    if pats:
        blocks.append(table([bi("Pattern", "योग"), bi("Planets", "ग्रह"), bi("What it suggests", "क्या दर्शाता है")],
                            [[bi(a, b), bi(", ".join(ps), ", ".join(HS.PLANET.get(x) or WB_HI.get(x, x) for x in ps)), bi(e, h)] for a, b, ps, e, h in pats]))
    else:
        blocks.append(para(bi("No grand trine, T-square, grand cross, yod or stellium in this chart.", "इस कुंडली में ग्रैंड ट्राइन, टी-स्क्वेयर, ग्रैंड क्रॉस, योड या स्टेलियम नहीं है।")))
    blocks.append(table([bi("Planet", "ग्रह"), bi("Disposed by", "स्वामी"), bi("Chain", "श्रृंखला")],
                        [[_p(p), _p(disp[p]), bi(" → ".join(chains[p]), " → ".join(HS.PLANET.get(x, x) for x in chains[p]))] for p in SEVEN]))
    blocks.append(para(bi(f"Final dispositor: {final}." if final else "No single final dispositor.",
                          f"अंतिम स्वामी: {HS.PLANET.get(final, final)}।" if final else "कोई एक अंतिम स्वामी नहीं।")))
    if mutual:
        blocks.append(para(bi("Mutual reception: " + "; ".join(f"{a} and {b}" for a, b in mutual) + ".",
                              "परस्पर स्वगृह विनिमय: " + "; ".join(f"{HS.PLANET.get(a, a)} और {HS.PLANET.get(b, b)}" for a, b in mutual) + "।")))
    secs.append({"key": "w_patterns", "title": bi("Western: aspect patterns and dispositors", "पाश्चात्य: दृष्टि योग और स्वामित्व"), "blocks": blocks,
                 "note": bi("Traditional rulers; patterns from the natal aspects within their orbs.", "पारंपरिक स्वामी; योग जन्म की दृष्टियों से, उनकी सीमा में।")})
    # dignities
    rows = []
    for p in SEVEN:
        sc, tags = dignity(p, pos[p]["lon"], day)
        rows.append([_p(p), _s(pos[p]["lon"]), bi(", ".join(t[0] for t in tags), ", ".join(t[1] for t in tags)), bi(f"{sc:+d}")])
    alm = almuten(asc, day)
    secs.append({"key": "w_dignities", "title": bi("Western: essential dignities", "पाश्चात्य: आवश्यक गरिमा"),
                 "intro": bi(f"A {'day' if day else 'night'} chart. Almuten of the Ascendant (the strongest planet over it): {alm}.",
                             f"{'दिन' if day else 'रात'} की कुंडली। लग्न का अलमुतेन (उस पर सबसे बली ग्रह): {HS.PLANET.get(alm, alm)}।"),
                 "blocks": [table([bi("Planet", "ग्रह"), bi("Position", "स्थिति"), bi("Dignities", "गरिमा"), bi("Score", "अंक")], rows)],
                 "note": bi("Points: domicile 5, exaltation 4, triplicity 3 (Dorothean, by sect), term 2 (Egyptian), face 1 (Chaldean); detriment −5, fall −4.",
                            "अंक: स्वगृह 5, उच्च 4, त्रिकोण 3 (डोरोथियस, दिन/रात अनुसार), सीमा 2 (मिस्री), मुख 1 (कैल्डियन); शत्रु गृह −5, नीच −4।")})
    # lots and firdaria
    lrows = [[bi(f"Lot of {en}", f"{hi} लॉट"), _s(lon), bi(te, th)] for en, hi, lon, te, th in lots(asc, pos, day)]
    birth = c["time_pipeline"].get("_utc_dt") or dt.datetime.fromisoformat(c["time_pipeline"]["utc"].replace("Z", "")[:19])
    if isinstance(birth, str):
        birth = dt.datetime.fromisoformat(birth[:19])
    birth = birth.replace(tzinfo=None)
    now = dt.datetime.fromisoformat(c["meta"]["generated_for_date"])
    fd, cur = firdaria(birth, day, now)
    fb = [table([bi("Lot", "लॉट"), bi("Position", "स्थिति"), bi("Theme", "विषय")], lrows)]
    if cur:
        lord, a, b, subs = cur
        sub = next(((l, x, y) for l, x, y in subs if x <= now < y), None)
        fb.append(para(bi(f"Firdaria now: the {lord} period ({a.year}–{b.year})" + (f", {sub[0]} sub-period until {sub[2].strftime('%b %Y')}." if sub else "."),
                          f"अभी फ़िरदारिया: {HS.PLANET.get(lord) or WB_HI.get(lord, lord)} अवधि ({a.year}–{b.year})" +
                          (f", {HS.PLANET.get(sub[0], sub[0])} उप-अवधि {sub[2].month}/{sub[2].year} तक।" if sub else "।"))))
        fb.append(table([bi("Firdaria", "फ़िरदारिया"), bi("Years", "वर्ष")],
                        [[_p(l), bi(f"{x.year}–{y.year}")] for l, x, y, _ in fd if y.year >= now.year - 20 and x.year <= now.year + 25]))
    secs.append({"key": "w_lots", "title": bi("Western: lots and firdaria", "पाश्चात्य: लॉट और फ़िरदारिया"), "blocks": fb,
                 "note": bi("Hermetic lots after Paulus, reversed at night; firdaria after Bonatti, nodes at the end.",
                            "पॉलस के अनुसार हर्मेटिक लॉट, रात में उलटे; बोनाटी के अनुसार फ़िरदारिया, नोड अंत में।")})
    # declination, harmonic, draconic, sidereal
    pars = []
    for i, a in enumerate(TEN):
        for b in TEN[i + 1:]:
            da, db = pos[a]["dec"], pos[b]["dec"]
            if abs(da - db) <= 1.0:
                pars.append(bi(f"{a} parallel {b} ({abs(da - db):.1f}°)", f"{HS.PLANET.get(a) or WB_HI.get(a, a)} समांतर {HS.PLANET.get(b) or WB_HI.get(b, b)} ({abs(da - db):.1f}°)"))
            elif abs(da + db) <= 1.0:
                pars.append(bi(f"{a} contraparallel {b} ({abs(da + db):.1f}°)", f"{HS.PLANET.get(a) or WB_HI.get(a, a)} प्रति-समांतर {HS.PLANET.get(b) or WB_HI.get(b, b)} ({abs(da + db):.1f}°)"))
    node = pos["North Node"]["lon"]
    swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
    fbay = swe.get_ayanamsa_ut(jd)
    rows = [[_p(p), bi(f"{pos[p]['dec']:+.1f}°"), _s(pos[p]["lon"] * 9), _s(pos[p]["lon"] - node), _s(pos[p]["lon"] - fbay)] for p in TEN]
    secs.append({"key": "w_derived", "title": bi("Western: declination, harmonic, draconic and sidereal", "पाश्चात्य: क्रांति, हार्मोनिक, ड्रैकोनिक और निरयण"),
                 "blocks": [table([bi("Planet", "ग्रह"), bi("Declination", "क्रांति"), bi("Harmonic 9", "हार्मोनिक 9"), bi("Draconic", "ड्रैकोनिक"),
                                   bi("Sidereal (Fagan-Bradley)", "निरयण (फ़ेगन-ब्रैडली)")], rows),
                            para(bi("Parallels within 1°:", "1° के भीतर समांतर:")), items(pars or [bi("none", "कोई नहीं")])],
                 "note": bi("Harmonic 9 multiplies each longitude by 9; the draconic chart counts from the North Node; Fagan-Bradley is the Western sidereal zodiac.",
                            "हार्मोनिक 9 हर देशांतर को 9 से गुणा करता है; ड्रैकोनिक कुंडली उत्तर नोड से गिनती है; फ़ेगन-ब्रैडली पाश्चात्य निरयण राशिचक्र है।")})
    # Aries ingress (mundane) for the current year at the birthplace
    pl = c["meta"]["place"]
    jd_i = swe.solcross_ut(0.0, swe.julday(now.year, 3, 1, 0.0), swe.FLG_SWIEPH) + 0.0007   # a minute after, so the Sun reads Aries 0°
    pos_i = _positions(jd_i)
    asc_i = swe.houses_ex(jd_i, pl["lat"], pl["lon"], b"P")[1][0]
    ai = int(asc_i // 30)
    y_, m_, d_, h_ = swe.revjul(jd_i)
    rows = [[_p(p), _s(pos_i[p]["lon"]), bi(f"house {(int(pos_i[p]['lon'] // 30) - ai) % 12 + 1}", f"भाव {(int(pos_i[p]['lon'] // 30) - ai) % 12 + 1}")] for p in TEN]
    secs.append({"key": "w_ingress", "title": bi(f"Aries ingress {now.year} (the astrological new year)", f"मेष प्रवेश {now.year} (ज्योतिषीय नववर्ष)"),
                 "intro": bi(f"Cast for the Sun's entry into Aries on {d_} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m_ - 1]} {y_} at {int(h_):02d}:{int(h_ % 1 * 60):02d} UT, at the birthplace. Ascendant {SIGNS[ai]}.",
                             f"सूर्य के मेष प्रवेश ({d_}/{m_}/{y_}, {int(h_):02d}:{int(h_ % 1 * 60):02d} UT) के लिए, जन्मस्थान पर। लग्न {SIGN_HI.get(SIGNS[ai], SIGNS[ai])}।"),
                 "blocks": [table([bi("Planet", "ग्रह"), bi("Position", "स्थिति"), bi("House (whole sign)", "भाव (पूर्ण राशि)")], rows)],
                 "note": bi("Mundane astrologers read the ingress chart for the year of a place; here it is cast for your birthplace.",
                            "मुंडेन ज्योतिषी किसी स्थान के वर्ष के लिए प्रवेश कुंडली पढ़ते हैं; यहाँ यह आपके जन्मस्थान के लिए है।")})
    # astrocartography
    hits = acg(jd, pos)
    good = [h for h in hits if h[1] in ("Sun", "Moon", "Venus", "Jupiter", "Mercury")]
    rows = [[bi(city, CITY_HI.get(city, city)), _p(p), bi(*ANGLE[a]), bi(*ACG_THEME[p])] for city, p, a in good[:25]]
    blk = [table([bi("City", "शहर"), bi("Planet", "ग्रह"), bi("Angle", "कोण"), bi("Theme there", "वहाँ का विषय")], rows)] if rows else \
        [para(bi("None of the 45 listed cities lies within 3° of a Sun, Moon, Mercury, Venus or Jupiter line.", "सूचीबद्ध 45 शहरों में से कोई भी सूर्य, चंद्र, बुध, शुक्र या गुरु रेखा के 3° के भीतर नहीं।"))]
    tough = [h for h in hits if h[1] in ("Mars", "Saturn")]
    if tough:
        blk.append(para(bi("Mars and Saturn lines (more effort there): " + ", ".join(f"{c_} ({p}, {ANGLE[a][0]})" for c_, p, a in tough[:10]) + ".",
                           "मंगल और शनि रेखाएँ (वहाँ अधिक प्रयास): " + ", ".join(f"{CITY_HI.get(c_, c_)} ({HS.PLANET.get(p, p)}, {ANGLE[a][1]})" for c_, p, a in tough[:10]) + "।")))
    secs.append({"key": "w_acg", "title": bi("Western: astrocartography (where your planets are strong)", "पाश्चात्य: एस्ट्रोकार्टोग्राफ़ी (आपके ग्रह कहाँ बली हैं)"),
                 "blocks": blk,
                 "note": bi("A planet on the MC, IC, rising or setting line of a place is emphasised there (within 3° of hour angle). Use it as one factor in choosing where to live or work.",
                            "किसी स्थान की MC, IC, उदय या अस्त रेखा पर ग्रह वहाँ प्रबल होता है (होरा कोण के 3° के भीतर)। रहने या काम करने की जगह चुनते समय इसे एक कारक मानें।")})
    return secs
